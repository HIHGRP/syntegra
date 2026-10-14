"""Learner 360 services (MFS §9, FR-LRN-*): registration with identity matching, GLID, enrolment, transfer.

* Every new learner is matched against the state registry before creation (blocking on phonetic keys,
  date of birth and NIN lookup token). ≥ 0.98 links to the existing learner; 0.80–0.98 needs a recorded
  override reason and opens a steward review; below that a new learner is created.
* A Global Learner ID is allocated from the state's leased national block and never reused.
* One active primary enrolment per learner is enforced by the database (``uq_enrolment_active_primary_key``).
"""

from __future__ import annotations

import datetime as dt
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from django.db import IntegrityError, connections, transaction
from django.db.models import Q, QuerySet

from syntegra.academic.models import Programme
from syntegra.clearance.services import DecisionInput, gate, national_network_active
from syntegra.core import authz, context, crypto, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound, SoftWarning
from syntegra.core.ids import format_glid
from syntegra.core.text import name_phonetic, phonetic_key
from syntegra.families import services as families
from syntegra.families.services import GuardianInput
from syntegra.institutions.models import Institution
from syntegra.learners.domain import matching
from syntegra.learners.models import Enrolment, Learner, LearnerTransfer
from syntegra.mdm.models import ExternalIdentifier, MatchReview

SEXES = {"female", "male"}
# Identifiers captured at registration besides the NIN (post-secondary: JAMB registration and matriculation number)
_IDENTIFIER = re.compile(r"[A-Z0-9][A-Z0-9/-]{2,22}[A-Z0-9]")
REGISTRATION_SCHEMES = ("JAMB-REG", "INST-ID", "WAEC-CAND", "NECO-CAND", "NABTEB-CAND", "PREV-LRN-ID")


@dataclass
class RegisterLearner:
    given: str
    family: str
    date_of_birth: dt.date
    sex: str
    institution_id: uuid.UUID
    education_level: str
    middle: str | None = None
    preferred_name: str | None = None
    dob_precision: str = "day"
    nin: str | None = None
    nationality: str | None = "NG"
    state_of_origin: str | None = None
    home_languages: list[str] = field(default_factory=list)
    start_on: dt.date | None = None
    basis: str = "admission"
    is_minimal_documentation: bool = False
    guardians: list[GuardianInput] = field(default_factory=list)
    programme_id: uuid.UUID | None = None  # post-secondary: the programme admitted to
    cohort_label: str | None = None  # intake cohort, e.g. 2026/2027 entry
    identifiers: dict[str, str] = field(default_factory=dict)  # scheme → value, e.g. JAMB-REG, INST-ID


@dataclass
class Registration:
    learner: Learner
    enrolment: Enrolment | None
    outcome: str  # created | linked
    review_id: uuid.UUID | None = None
    match: dict[str, Any] | None = None
    guardians: list[families.LinkedGuardian] = field(default_factory=list)


# --------------------------------------------------------------------------- visibility (derived scope)
def visible() -> QuerySet[Learner]:
    """Learners visible to the caller: enrolled (now or before) at an institution inside the grant subtree."""
    ctx = context.require()
    qs = Learner.objects.all()
    if ctx.is_system or ctx.scope_ids is None:
        return qs
    enrolled = Enrolment.objects.filter(scope_node_id__in=list(ctx.scope_ids)).values("learner_id")
    return qs.filter(id__in=enrolled)


def get(learner_id: uuid.UUID) -> Learner:
    lrn = visible().filter(pk=learner_id).first()
    if lrn is None:
        raise NotFound("learner", learner_id)
    return lrn


# --------------------------------------------------------------------------- GLID allocation
def allocate_glid(alias: str) -> str:
    """Next GLID from the state's leased blocks (CD-07). Called inside the registry transaction."""
    from syntegra.platform.models import GlidBlock

    ctx = context.require()
    blocks = list(GlidBlock.objects.using("platform").filter(tenant_id=ctx.state_tenant_id).order_by("first_serial"))
    if not blocks:
        raise ConflictError("GLID-NO-BLOCK", "No GLID block leased", "The state has no Global Learner ID block.")
    with connections[alias].cursor() as cur:
        for b in blocks:
            lo, hi = format_glid(b.first_serial)[:13], format_glid(b.last_serial)[:13]
            cur.execute(
                "SELECT global_learner_id FROM learner WHERE tenant_id = %s AND global_learner_id >= %s "
                "AND global_learner_id < %s ORDER BY global_learner_id DESC LIMIT 1 FOR UPDATE",
                [ctx.state_tenant_id.bytes, lo, hi + "~"],  # type: ignore[union-attr]
            )
            r = cur.fetchone()
            nxt = b.first_serial if r is None else int(r[0][4:8] + r[0][9:13]) + 1
            if nxt <= b.last_serial:
                return format_glid(nxt)
    raise ConflictError("GLID-EXHAUSTED", "GLID block exhausted", "Lease a new block from the national allocator.")


# --------------------------------------------------------------------------- matching
def _candidates(data: RegisterLearner, nin_hmac: bytes | None) -> list[tuple[Learner, matching.Person]]:
    family_key = phonetic_key(data.family)
    q = Q(name_phonetic__endswith=" " + family_key) | Q(date_of_birth=data.date_of_birth)
    ids_by_nin: set[uuid.UUID] = set()
    if nin_hmac:
        ids_by_nin = set(
            ExternalIdentifier.objects.filter(person_kind="learner", scheme="NG-NIN", value_hmac=nin_hmac).values_list(
                "person_id", flat=True
            )
        )
        q |= Q(id__in=ids_by_nin)
    rows = list(Learner.objects.filter(q).exclude(status="merged")[:500])  # blocking group (all state learners)
    nins = {
        e.person_id: bytes(e.value_hmac)
        for e in ExternalIdentifier.objects.filter(
            person_kind="learner", scheme="NG-NIN", person_id__in=[r.id for r in rows]
        )
    }
    return [
        (
            r,
            matching.Person(
                r.legal_given_name,
                r.legal_family_name,
                r.date_of_birth,
                r.sex,
                r.dob_precision,
                nin_hmac=nins.get(r.id),
            ),
        )
        for r in rows
    ]


def match(data: RegisterLearner) -> list[tuple[Learner, matching.MatchResult]]:
    ctx = context.require()
    nin_hmac = crypto.lookup_hmac(data.nin, scheme="NG-NIN", tenant_id=ctx.state_tenant_id) if data.nin else None
    cand = matching.Person(data.given, data.family, data.date_of_birth, data.sex, data.dob_precision, nin_hmac=nin_hmac)
    return matching.best(cand, _candidates(data, nin_hmac))


def _validate(data: RegisterLearner) -> None:
    errs = []
    if data.sex not in SEXES:
        errs.append({"field": "sex", "message": "female or male (as on the identity document)"})
    today = dt.date.today()
    if data.date_of_birth > today:
        errs.append({"field": "date_of_birth", "message": "cannot be in the future"})
    elif (today - data.date_of_birth).days < 365 * 2:
        errs.append({"field": "date_of_birth", "message": "learner must be at least two years old"})
    if data.nin and (not data.nin.isdigit() or len(data.nin) != 11):
        errs.append({"field": "nin", "message": "NIN has 11 digits"})
    if not data.given.strip() or not data.family.strip():
        errs.append({"field": "name", "message": "given and family names are required"})
    if errs:
        raise HardValidation("LRN-VALIDATION", "Some fields need attention", errors=errs)


def register(
    data: RegisterLearner, *, override_reason: str | None = None, clearance: DecisionInput | None = None
) -> Registration:
    ctx = context.require()
    authz.require("learner:register", ctx)
    if data.nin:
        data.nin = "".join(data.nin.split())
    _validate(data)
    inst = Institution.objects.filter(pk=data.institution_id).first()
    if inst is None:
        raise NotFound("institution", data.institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    found = match(data)
    top = found[0] if found else None
    start = data.start_on or dt.date.today()
    # FR-LRN-06: a minor needs a guardian with parental responsibility (age of majority from state policy, FR-LRN-05)
    families.check(
        data.guardians,
        date_of_birth=data.date_of_birth,
        on=start,
        scope_node_id=inst.scope_node_id,
        learner_id=top[0].id if top and top[1].band == "auto_link" else None,
        learner_nin=data.nin,
    )
    _check_programme_and_identifiers(data, inst, top[0].id if top and top[1].band == "auto_link" else None)
    if top and top[1].band == "review" and not override_reason:
        err = SoftWarning(
            "LRN-PROBABLE-MATCH",
            "This learner may already be registered",
            "Check the candidates; continue only if this is a different child.",
        )
        err.extra["candidates"] = [
            {
                "learner_id": str(lr.id),
                "global_learner_id": lr.global_learner_id,
                "score": r.score,
                "evidence": r.evidence,
            }
            for lr, r in found[:3]
        ]
        raise err
    linked = bool(top and top[1].band == "auto_link")
    if top and linked and (_left_elsewhere(top[0].id, inst.id) or top[0].status == "registered"):
        # re-admission of a known learner who was enrolled elsewhere (or whose admission is awaiting a clearance
        # decision): fee-clearance due diligence (CR-001), including every other state on the network (CR-002)
        gate(top[0].id, inst.id, purpose="admission", education_level=data.education_level, decision=clearance)
    # New to this state while other states are on the national clearance network: the learner record is created
    # first, the other states are asked, then the enrolment follows the clearance outcome (CR-002, FR-FCL-13).
    cross_state = not linked and national_network_active()
    with uow.command("registry", None, action="register", record_kind="learner", reason=override_reason) as cmd:
        if top and top[1].band == "auto_link":
            learner = top[0]
            review = cmd.add(
                MatchReview(
                    entity_kind="learner",
                    candidate_id=learner.id,
                    existing_id=learner.id,
                    score=top[1].score,
                    evidence={"fields": top[1].evidence, "model": matching.MODEL_VERSION, "auto_linked": True},
                    source="registration",
                    decision="same",
                    decision_reason="auto-linked at ≥ 0.98",
                    status="resolved",
                )
            )
            cmd.record_id = learner.id
            linked_guardians = families.link(cmd, learner.id, data.guardians, valid_from=start)
            _add_identifiers(cmd, learner.id, data.identifiers)
            enr = _enrol(
                cmd,
                learner,
                inst,
                data.education_level,
                data.start_on,
                data.basis,
                data.programme_id,
                data.cohort_label,
            )
            return Registration(learner, enr, "linked", review.id, {"score": top[1].score}, linked_guardians)
        learner = Learner(
            global_learner_id=allocate_glid(cmd.alias),
            legal_given_name=data.given.strip(),
            legal_middle_names=data.middle,
            legal_family_name=data.family.strip(),
            preferred_name=data.preferred_name,
            name_phonetic=name_phonetic(data.given, data.family),
            date_of_birth=data.date_of_birth,
            dob_precision=data.dob_precision,
            sex=data.sex,
            nationality=data.nationality,
            state_of_origin=data.state_of_origin,
            home_languages=data.home_languages or None,
            is_minimal_documentation=data.is_minimal_documentation,
            identity_verified_level="unverified",
            status="registered",
        )
        cmd.add(learner)
        cmd.record_id = learner.id
        if data.nin:
            cmd.add(
                ExternalIdentifier(
                    person_kind="learner",
                    person_id=learner.id,
                    scheme="NG-NIN",
                    value_hmac=crypto.lookup_hmac(data.nin, scheme="NG-NIN", tenant_id=ctx.state_tenant_id),
                    value_national_hmac=crypto.national_lookup_hmac(data.nin, scheme="NG-NIN"),
                    value_enc=crypto.encrypt(data.nin, purpose="id:NG-NIN", tenant_id=ctx.state_tenant_id),
                    value_last4=crypto.last4(data.nin),
                    status="unverified",
                )
            )
        review_id = None
        if top and top[1].band == "review":
            review_id = cmd.add(
                MatchReview(
                    entity_kind="learner",
                    candidate_id=learner.id,
                    existing_id=top[0].id,
                    score=top[1].score,
                    evidence={"fields": top[1].evidence, "model": matching.MODEL_VERSION, "override": override_reason},
                    source="registration",
                    status="open",
                )
            ).id
        cmd.emit(
            "LRN.CREATED",
            aggregate_id=learner.id,
            scope_node_id=inst.scope_node_id,
            payload={"learner_id": learner.id, "global_learner_id": learner.global_learner_id},
        )
        reg = Registration(
            learner,
            None,
            "created",
            review_id,
            {"score": top[1].score} if top else None,
            families.link(cmd, learner.id, data.guardians, valid_from=start),
        )
        _add_identifiers(cmd, learner.id, data.identifiers)
        if not cross_state:
            reg.enrolment = _enrol(
                cmd,
                learner,
                inst,
                data.education_level,
                data.start_on,
                data.basis,
                data.programme_id,
                data.cohort_label,
            )
            return reg
    gate(learner.id, inst.id, purpose="admission", education_level=data.education_level, decision=clearance)
    with uow.command("registry", None, action="enrol", record_kind="enrolment") as cmd:
        reg.enrolment = _enrol(
            cmd, learner, inst, data.education_level, data.start_on, data.basis, data.programme_id, data.cohort_label
        )
    return reg


# --------------------------------------------------------------------------- programme and identifiers
def _normalise_identifier(value: str) -> str:
    return "".join(value.split()).upper()


def _check_programme_and_identifiers(
    data: RegisterLearner, inst: Institution, linked_learner_id: uuid.UUID | None
) -> None:
    """Programme must belong to the admitting institution; an identifier can never belong to two learners."""
    ctx = context.require()
    errs: list[dict[str, Any]] = []
    if data.programme_id is not None:
        prog = Programme.objects.filter(pk=data.programme_id).first()
        if prog is None or prog.institution_id != inst.id:
            errs.append({"field": "programme_id", "message": "choose a programme of the admitting institution"})
        elif prog.status not in ("approved", "published"):
            errs.append({"field": "programme_id", "message": "the programme is not open for admission"})
    for scheme, raw in data.identifiers.items():
        f = f"identifiers[{scheme}]"
        value = _normalise_identifier(raw or "")
        if scheme not in REGISTRATION_SCHEMES:
            errs.append({"field": f, "message": "this identifier cannot be captured at registration"})
            continue
        if not value:
            continue
        if not _IDENTIFIER.fullmatch(value):
            errs.append({"field": f, "message": "letters, digits, / and - only (4–24 characters)"})
            continue
        token = crypto.lookup_hmac(value, scheme=scheme, tenant_id=ctx.state_tenant_id)
        holder = (
            ExternalIdentifier.objects.filter(person_kind="learner", scheme=scheme, value_hmac=token)
            .exclude(person_id=linked_learner_id)
            .values_list("person_id", flat=True)
            .first()
        )
        if holder is not None:
            other = Learner.objects.filter(pk=holder).values_list("global_learner_id", flat=True).first()
            errs.append({"field": f, "message": f"already recorded for another learner ({other or 'unknown'})"})
    if errs:
        raise HardValidation("LRN-VALIDATION", "Some fields need attention", errors=errs)


def _add_identifiers(cmd: uow.Command, learner_id: uuid.UUID, identifiers: dict[str, str]) -> None:
    tenant = cmd.ctx.state_tenant_id
    for scheme, raw in identifiers.items():
        value = _normalise_identifier(raw or "")
        if (
            not value
            or ExternalIdentifier.objects.filter(person_kind="learner", person_id=learner_id, scheme=scheme).exists()
        ):
            continue
        cmd.add(
            ExternalIdentifier(
                person_kind="learner",
                person_id=learner_id,
                scheme=scheme,
                value_hmac=crypto.lookup_hmac(value, scheme=scheme, tenant_id=tenant),
                value_enc=crypto.encrypt(value, purpose=f"id:{scheme}", tenant_id=tenant),
                value_last4=crypto.last4(value),
                status="unverified",
            )
        )


def identifiers_of(learner_id: uuid.UUID) -> list[dict[str, Any]]:
    """Identifiers on record, masked (last four characters only)."""
    get(learner_id)
    return [
        {"scheme": e.scheme, "last4": e.value_last4, "status": e.status}
        for e in ExternalIdentifier.objects.filter(person_kind="learner", person_id=learner_id).order_by("scheme")
    ]


# --------------------------------------------------------------------------- enrolment
def _enrol(
    cmd: uow.Command,
    learner: Learner,
    inst: Institution,
    level: str,
    start_on: dt.date | None,
    basis: str,
    programme_id: uuid.UUID | None = None,
    cohort_label: str | None = None,
) -> Enrolment:
    enr = Enrolment(
        scope_node_id=inst.scope_node_id,
        learner_id=learner.id,
        institution_id=inst.id,
        operating_tenant_id=inst.operating_tenant_id,
        education_level=level,
        programme_id=programme_id,
        cohort_label=cohort_label or None,
        is_primary=True,
        basis=basis,
        start_on=start_on or dt.date.today(),
        status="active",
    )
    try:
        with transaction.atomic(using=cmd.alias):  # savepoint: keep the command usable after a conflict
            cmd.add(enr)
    except IntegrityError as exc:
        if "active_primary_key" in str(exc):
            raise ConflictError(
                "ENR-ACTIVE-PRIMARY",
                "Learner already enrolled",
                f"{learner.global_learner_id} has an active enrolment elsewhere; request a transfer instead.",
            ) from exc
        raise
    if learner.status == "registered":
        cmd.update(learner, status="active")
    cmd.emit(
        "ENR.STARTED",
        aggregate_id=enr.id,
        aggregate_kind="enrolment",
        scope_node_id=inst.scope_node_id,
        payload={"enrolment_id": enr.id, "learner_id": learner.id, "institution_id": inst.id},
    )
    return enr


def transfer(
    learner_id: uuid.UUID,
    to_institution_id: uuid.UUID,
    *,
    effective_on: dt.date | None = None,
    education_level: str | None = None,
    clearance: DecisionInput | None = None,
) -> LearnerTransfer:
    """Move a learner's active primary enrolment to another institution in the state (FR-LRN-07).

    The receiving institution's fee-clearance check runs first (CR-001). It never blocks the records
    transfer or the learner's attendance at the current school (P9); outstanding obligations need a recorded
    human admission decision before the new enrolment is created.
    """
    ctx = context.require()
    authz.require("enrolment:transfer", ctx)
    effective_on = effective_on or dt.date.today()
    to_inst = Institution.objects.filter(pk=to_institution_id, status="active").first()
    if to_inst is None:
        raise NotFound("institution", to_institution_id)
    authz.require_scope(to_inst.scope_node_id, ctx)  # the receiving institution requests the transfer
    level = education_level or (
        Enrolment.objects.filter(learner_id=learner_id, status="active", is_primary=True)
        .values_list("education_level", flat=True)
        .first()
        or ""
    )
    gate(learner_id, to_inst.id, purpose="transfer", education_level=level, decision=clearance)
    with uow.command("registry", None, action="transfer", record_kind="learner_transfer") as cmd:
        learner = cmd.lock(Learner, learner_id)
        cur = (
            Enrolment.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(tenant_id=ctx.state_tenant_id, learner_id=learner.id, status="active", is_primary=True)
            .first()
        )
        if cur is None:
            raise ConflictError("ENR-NONE", "No active enrolment", "The learner has no active primary enrolment.")
        if cur.institution_id == to_inst.id:
            raise HardValidation("ENR-SAME", "Same institution", "The learner is already enrolled here.")
        cmd.update(
            cur,
            status="transferred",
            end_on=effective_on,
            leaving_reason="transferred",
            destination={"institution_id": str(to_inst.id)},
        )
        cmd.emit(
            "ENR.ENDED",
            aggregate_id=cur.id,
            aggregate_kind="enrolment",
            scope_node_id=cur.scope_node_id,
            payload={"enrolment_id": cur.id, "status": "transferred"},
        )
        new = _enrol(cmd, learner, to_inst, education_level or cur.education_level, effective_on, "transfer")
        t = LearnerTransfer(
            scope_node_id=to_inst.scope_node_id,
            learner_id=learner.id,
            from_enrolment_id=cur.id,
            to_institution_id=to_inst.id,
            to_enrolment_id=new.id,
            requested_by_id=ctx.actor_id,
            effective_on=effective_on,
            dsl_handover_due_on=effective_on + dt.timedelta(days=5),
            status="completed",
        )
        cmd.add(t)
        cmd.record_id = t.id
        cmd.emit(
            "LRN.TRANSFERRED",
            aggregate_id=t.id,
            scope_node_id=to_inst.scope_node_id,
            payload={"learner_id": learner.id, "learner_transfer_id": t.id, "to_institution_id": to_inst.id},
        )
        return t


def _left_elsewhere(learner_id: uuid.UUID, institution_id: uuid.UUID) -> bool:
    """Previously enrolled at another institution and not actively enrolled anywhere now."""
    enrs = Enrolment.objects.filter(learner_id=learner_id)
    return (
        enrs.exclude(institution_id=institution_id).exists()
        and not enrs.filter(status="active", is_primary=True).exists()
    )


def enrolments(learner_id: uuid.UUID) -> list[Enrolment]:
    get(learner_id)
    return list(Enrolment.objects.filter(learner_id=learner_id).order_by("-start_on"))


def reveal_nin(learner_id: uuid.UUID) -> str | None:
    """Reveal the NIN — restricted: requires permission, a purpose, and is audited."""
    ctx = context.require()
    authz.require("learner.nin:reveal", ctx)
    authz.require_purpose("restricted", ctx)
    learner = get(learner_id)
    e = ExternalIdentifier.objects.filter(person_kind="learner", person_id=learner.id, scheme="NG-NIN").first()
    if e is None:
        return None
    with uow.command("registry", None, action="reveal", record_kind="learner") as cmd:
        cmd.record_id = learner.id
        cmd.note("nin", None, {"revealed": True})
    return crypto.decrypt(bytes(e.value_enc), purpose="id:NG-NIN", tenant_id=ctx.state_tenant_id)
