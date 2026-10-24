"""Certificates (MFS §15, FR-CER-*): signed issue, public verification, four-eyes reissue with supersession.

* The signed payload is minimal-disclosure JSON canonicalised with RFC 8785 (JCS) and signed with ES256 by
  the state's certificate key (HSM in production; ``LocalKeyProvider`` in development). The payload hash is
  unique, the number is ``<CC>-<AUTH>-<YEAR>-<SEQ><check>`` and never reused (CD-08).
* One valid certificate per learner × qualification × award date (``uq_certificate_award_key``).
* Verification is public, rate-limited and logged without storing the client IP (keyed hash only).
* A reissue needs a reviewer and a different approver; the original is superseded at the same instant the
  replacement is issued.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import uuid
from dataclasses import dataclass
from typing import Any

from django.db import IntegrityError, transaction

from syntegra.certificates.domain import payload as payload_rules
from syntegra.certificates.models import (
    Certificate,
    CertificateEvent,
    CertificateTemplate,
    ReissueCase,
    Signatory,
    SigningKey,
    Verification,
)
from syntegra.core import authz, context, crypto, uow, workflow
from syntegra.core.canonical_json import canonicalize
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.ids import certificate_number_valid, format_certificate_number, short_code
from syntegra.institutions.models import Institution
from syntegra.learners.models import Learner


# --------------------------------------------------------------------------- set-up
def ensure_signing_key(scope_node_id: uuid.UUID, kid: str) -> SigningKey:
    key: SigningKey | None = SigningKey.objects.filter(kid=kid).first()
    if key:
        return key
    with uow.command("registry", "certificate:manage", action="activate_key", record_kind="signing_key") as cmd:
        return cmd.add(
            SigningKey(
                scope_node_id=scope_node_id,
                kid=kid,
                algorithm="ES256",
                public_jwk=crypto.provider().public_jwk(kid),
                hsm_key_ref=f"local:{kid}",
                activated_at=utcnow(),
                status="active",
            )
        )


def create_template(
    scope_node_id: uuid.UUID, code: str, kind: str = "certificate", qualification_id: uuid.UUID | None = None
) -> CertificateTemplate:
    with uow.command("registry", "certificate:manage", action="create", record_kind="certificate_template") as cmd:
        return cmd.add(
            CertificateTemplate(
                scope_node_id=scope_node_id,
                code=code,
                credential_kind=kind,
                qualification_id=qualification_id,
                layout={"size": "A4", "qr": "bottom-right"},
                version=1,
                status="published",
            )
        )


def add_signatory(
    scope_node_id: uuid.UUID, user_id: uuid.UUID, title: str, valid_from: dt.date | None = None
) -> Signatory:
    with uow.command("registry", "certificate:manage", action="create", record_kind="signatory") as cmd:
        return cmd.add(
            Signatory(
                scope_node_id=scope_node_id,
                user_id=user_id,
                title_on_award=title,
                valid_from=valid_from or dt.date.today(),
            )
        )


# --------------------------------------------------------------------------- issue
@dataclass
class IssueRequest:
    learner_id: uuid.UUID
    institution_id: uuid.UUID
    template_id: uuid.UUID
    signatory_id: uuid.UUID
    award_date: dt.date
    award_title: str
    award_class: str | None = None
    qualification_id: uuid.UUID | None = None
    kid: str | None = None
    authority: str = "ABMOE"


def _next_number(alias: str, authority: str, year: int) -> str:
    prefix = f"NG-{authority}-{year}-"
    last = (
        Certificate.unscoped.using(alias)
        .filter(certificate_number__startswith=prefix)
        .order_by("-certificate_number")
        .values_list("certificate_number", flat=True)
        .first()
    )
    seq = int(last[len(prefix) : -2]) + 1 if last else 1
    return format_certificate_number("NG", authority, year, seq)


def _sign_and_add(
    cmd: uow.Command,
    req: IssueRequest,
    learner: Learner,
    inst: Institution,
    template: CertificateTemplate,
    *,
    supersedes: Certificate | None = None,
) -> Certificate:
    key = (
        SigningKey.objects.filter(status="active", **({"kid": req.kid} if req.kid else {}))
        .order_by("-activated_at")
        .first()
    )
    if key is None:
        raise ConflictError("CER-NO-KEY", "No active signing key", "Activate the state certificate key first.")
    now = utcnow()
    holder = payload_rules.holder_name(learner.legal_given_name, learner.legal_middle_names, learner.legal_family_name)
    base = _next_number(cmd.alias, req.authority, req.award_date.year)
    base_seq = int(base.rsplit("-", 1)[1][:-2])
    for attempt in range(3):
        number = format_certificate_number("NG", req.authority, req.award_date.year, base_seq + attempt)
        payload = payload_rules.build(
            payload_rules.Award(
                number=number,
                kind=template.credential_kind,
                holder=holder,
                glid=learner.global_learner_id,
                institution_code=inst.institution_code,
                institution_name=inst.name,
                title=req.award_title,
                award_class=req.award_class,
                award_date=req.award_date,
                authority=req.authority,
                kid=key.kid,
                issued_at=now,
            )
        )
        canonical = canonicalize(payload)
        cert = Certificate(
            scope_node_id=inst.scope_node_id,
            certificate_number=number,
            verification_code=short_code(),
            credential_kind=template.credential_kind,
            learner_id=learner.id,
            institution_id=inst.id,
            qualification_id=req.qualification_id,
            award_date=req.award_date,
            award_class=req.award_class,
            holder_name_on_award=holder,
            template_id=template.id,
            signatory_id=req.signatory_id,
            payload=payload,
            payload_hash=hashlib.sha256(canonical).digest(),
            signature=crypto.sign_es256(key.kid, canonical),
            signing_key_id=key.id,
            supersedes_id=supersedes.id if supersedes else None,
            status="valid",
            status_changed_at=now,
            vc_document={
                "@context": ["https://www.w3.org/ns/credentials/v2"],
                "type": ["VerifiableCredential"],
                "credentialSubject": {"id": f"urn:glid:{learner.global_learner_id}", "award": req.award_title},
            },
        )
        try:
            with transaction.atomic(using=cmd.alias):
                cmd.add(cert)
            return cert
        except IntegrityError as exc:
            msg = str(exc)
            if "award_key" in msg:
                raise ConflictError(
                    "CER-ALREADY-ISSUED",
                    "Certificate already issued",
                    "A valid certificate exists for this learner and award; request a reissue.",
                ) from exc
            if ("certificate_number" in msg or "verification_code" in msg) and attempt < 2:
                continue
            raise
    raise ConflictError("CER-NUMBER", "Could not allocate a certificate number", "Retry the request.")


def issue(req: IssueRequest) -> Certificate:
    ctx = context.require()
    authz.require("certificate:issue", ctx)
    learner = Learner.objects.filter(pk=req.learner_id).first()
    inst = Institution.objects.filter(pk=req.institution_id).first()
    template = CertificateTemplate.objects.filter(pk=req.template_id, status="published").first()
    if learner is None or inst is None or template is None:
        raise NotFound("learner, institution or template")
    authz.require_scope(inst.scope_node_id, ctx)
    if learner.status in ("merged", "deceased"):
        raise HardValidation("CER-LEARNER", "Learner cannot receive awards", f"Learner is {learner.status}.")
    sig = Signatory.objects.filter(pk=req.signatory_id).first()
    if sig is None or sig.valid_from > req.award_date or (sig.valid_to and sig.valid_to < req.award_date):
        raise HardValidation("CER-SIGNATORY", "Signatory not valid on the award date", "")
    with uow.command("registry", None, action="issue", record_kind="certificate") as cmd:
        if (
            req.qualification_id is None
            and Certificate.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(
                tenant_id=ctx.state_tenant_id,
                learner_id=learner.id,
                award_date=req.award_date,
                credential_kind=template.credential_kind,
                status__in=("valid", "suspended"),
                payload__award__title=req.award_title,
            )
            .exists()
        ):
            # uq_certificate_award_key covers awards with a qualification; titled awards are checked here
            raise ConflictError(
                "CER-ALREADY-ISSUED",
                "Certificate already issued",
                "A valid certificate exists for this learner and award; request a reissue.",
            )
        cert = _sign_and_add(cmd, req, learner, inst, template)
        cmd.record_id = cert.id
        cmd.add(
            CertificateEvent(
                certificate_id=cert.id,
                event_kind="issued",
                reason="issued",
                actor_user_id=ctx.actor_id,
                occurred_at=cert.status_changed_at,
            )
        )
        cmd.emit(
            "CERT.ISSUED",
            aggregate_id=cert.id,
            scope_node_id=inst.scope_node_id,
            payload={"certificate_id": cert.id, "institution_id": inst.id, "learner_id": learner.id},
        )
        return cert


# --------------------------------------------------------------------------- verification (public)
def verify(query: str, *, channel: str = "web_number") -> dict[str, Any]:
    """Public verification by certificate number or verification code. Logged; never reveals more than the award."""
    ctx = context.require()
    q = query.strip().upper()
    cert = None
    if certificate_number_valid(q):
        cert = Certificate.objects.filter(certificate_number=q).first()
    elif len(q) == 9 and q[4] == "-":
        cert = Certificate.objects.filter(verification_code=q).first()
    result = cert.status if cert else "not_found"
    sig_ok = None
    if cert is not None:
        key = SigningKey.objects.get(pk=cert.signing_key_id)
        canonical = canonicalize(cert.payload)
        sig_ok = hashlib.sha256(canonical).digest() == bytes(cert.payload_hash) and crypto.verify_es256(
            key.public_jwk, canonical, bytes(cert.signature)
        )
        if not sig_ok:
            result = "not_found"  # tampered record: never confirm it
    ip_hash = hmac.new(
        crypto.provider().hmac_key("verify-ip", ctx.state_tenant_id), (ctx.ip or "").encode(), hashlib.sha256
    ).digest()
    with uow.command("registry", None, action="verify", record_kind="verification") as cmd:
        cmd.audited = False  # the verification log is itself the record (append-only)
        v = cmd.add(
            Verification(
                certificate_id=cert.id if cert else None,
                queried_number=q[:40],
                channel=channel,
                result=result,
                ip_hash=ip_hash,
                verified_at=utcnow(),
            )
        )
        cmd.emit(
            "CERT.VERIFIED" if cert else "CERT.VERIFY_FAILED",
            aggregate_id=v.id,
            aggregate_kind="verification",
            payload=_verified_payload(v, result),
        )
    out: dict[str, Any] = {"result": result, "checked_at": v.verified_at}
    if cert is not None and result != "not_found":
        p = cert.payload
        out.update(
            {
                "certificate_number": cert.certificate_number,
                "holder": p["holder"],
                "award": p["award"],
                "institution": p["institution"],
                "issuer": p["issuer"],
                "signature_valid": sig_ok,
                "status_changed_at": cert.status_changed_at,
            }
        )
        if cert.superseded_by_id:
            out["superseded_by"] = Certificate.objects.get(pk=cert.superseded_by_id).certificate_number
    return out


def _verified_payload(v: Verification, result: str) -> dict[str, Any]:
    from syntegra.core import catalog

    et = "CERT.VERIFIED" if v.certificate_id else "CERT.VERIFY_FAILED"
    spec = catalog.event(et).get("payload") or {}
    full = {"verification_id": v.id, "result": result, "queried_number": v.queried_number, "channel": v.channel}
    return {k: val for k, val in full.items() if k in spec}


def jwks() -> dict[str, Any]:
    keys = []
    for k in SigningKey.objects.filter(status__in=("active", "retired")):
        keys.append({**k.public_jwk, "kid": k.kid, "use": "sig", "alg": k.algorithm, "status": k.status})
    return {"keys": keys}


# --------------------------------------------------------------------------- reissue (four eyes)
def request_reissue(
    certificate_id: uuid.UUID,
    reason: str,
    *,
    applicant_name: str,
    applicant_phone: str,
    evidence_document_ids: list[str] | None = None,
) -> ReissueCase:
    ctx = context.require()
    authz.require("certificate:reissue", ctx)
    with uow.command("registry", None, action="request_reissue", record_kind="reissue_case") as cmd:
        cert = cmd.lock(Certificate, certificate_id)
        if cert.status not in ("valid", "suspended"):
            raise ConflictError("CER-STATUS", "Certificate cannot be reissued", f"It is {cert.status}.")
        case = cmd.add(
            ReissueCase(
                scope_node_id=cert.scope_node_id,
                case_number=f"RIC-{utcnow():%Y}-{short_code().replace('-', '')}",
                certificate_id=cert.id,
                applicant_user_id=None,
                applicant_name=applicant_name,
                applicant_phone=applicant_phone,
                reason=reason,
                evidence_document_ids=evidence_document_ids or [],
                amount_due_minor=0,
                currency="NGN",
                reviewer_id=ctx.actor_id,
                status="in_review",
            )
        )
        cmd.record_id = case.id
        workflow.start(
            "registry",
            "certificate_reissue",
            subject_kind="reissue_case",
            subject_id=case.id,
            scope_node_id=cert.scope_node_id,
            variables={"requested_by": str(ctx.actor_id)},
            cmd=cmd,
        )
        cmd.emit(
            "CER.REISSUE_REQUESTED",
            aggregate_id=case.id,
            aggregate_kind="reissue_case",
            scope_node_id=cert.scope_node_id,
            payload=_filter(
                "CER.REISSUE_REQUESTED", {"reissue_case_id": case.id, "certificate_id": cert.id, "reason": reason}
            ),
        )
        return case


def decide_reissue(case_id: uuid.UUID, approve: bool, *, note: str | None = None) -> ReissueCase:
    """Second person approves or rejects; approval issues the replacement and supersedes the original."""
    from syntegra.governance.models import WorkflowInstance

    ctx = context.require()
    authz.require("certificate:approve", ctx)
    case = ReissueCase.objects.filter(pk=case_id).first()
    if case is None:
        raise NotFound("reissue case", case_id)
    if case.reviewer_id == ctx.actor_id:
        raise Forbidden("The reviewer cannot also approve (four eyes).", code="CER-FOUR-EYES")
    inst = WorkflowInstance.unscoped.using("registry").filter(subject_kind="reissue_case", subject_id=case.id).first()
    if inst is None:
        raise NotFound("workflow", case_id)
    with uow.command(
        "registry",
        None,
        action="approve_reissue" if approve else "reject_reissue",
        record_kind="reissue_case",
        reason=note,
    ) as cmd:
        case = cmd.lock(ReissueCase, case_id)
        # nested command (savepoint): the workflow step and the reissue commit or fail together
        workflow.fire(
            "registry",
            inst.id,
            "approve" if approve else "reject",
            reason=note,
            variables={"approver": str(ctx.actor_id)},
        )
        if not approve:
            cmd.update(case, status="rejected", second_approver_id=ctx.actor_id)
            cmd.emit(
                "CER.REISSUE_DECIDED",
                aggregate_id=case.id,
                aggregate_kind="reissue_case",
                payload={"reissue_case_id": case.id, "status": "rejected"},
            )
            return case
        old = cmd.lock(Certificate, case.certificate_id)
        now = utcnow()
        cmd.update(old, status="superseded", status_changed_at=now)
        learner = Learner.objects.get(pk=old.learner_id)
        inst_ = Institution.objects.get(pk=old.institution_id)
        template = CertificateTemplate.objects.get(pk=old.template_id)
        req = IssueRequest(
            learner_id=learner.id,
            institution_id=inst_.id,
            template_id=template.id,
            signatory_id=old.signatory_id,
            award_date=old.award_date,
            award_title=old.payload["award"]["title"],
            award_class=old.award_class,
            qualification_id=old.qualification_id,
            kid=None,
            authority=old.certificate_number.split("-")[1],
        )
        new = _sign_and_add(cmd, req, learner, inst_, template, supersedes=old)
        cmd.update(old, superseded_by_id=new.id)
        cmd.update(case, status="issued", second_approver_id=ctx.actor_id, new_certificate_id=new.id)
        for c, kind in ((new, "reissued"), (old, "superseded")):
            cmd.add(
                CertificateEvent(
                    certificate_id=c.id,
                    event_kind=kind,
                    reason=case.reason,
                    actor_user_id=case.reviewer_id,
                    approver_user_id=ctx.actor_id,
                    workflow_instance_id=inst.id,
                    occurred_at=now,
                )
            )
        cmd.emit(
            "CER.REISSUE_DECIDED",
            aggregate_id=case.id,
            aggregate_kind="reissue_case",
            payload={"reissue_case_id": case.id, "status": "issued"},
        )
        cmd.emit(
            "CERT.REISSUED",
            aggregate_id=new.id,
            aggregate_kind="certificate",
            scope_node_id=old.scope_node_id,
            payload={"certificate_id": new.id, "supersedes_id": old.id},
        )
        return case


def _filter(event: str, full: dict[str, Any]) -> dict[str, Any]:
    from syntegra.core import catalog

    spec = catalog.event(event).get("payload") or {}
    return {k: v for k, v in full.items() if k in spec}
