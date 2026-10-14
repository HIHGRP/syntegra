"""Fee-clearance due diligence across the education ecosystem (CR-001, FR-FCL-01..08).

* ``publish`` — a creditor institution's ledger publishes outstanding obligations (summaries backed by invoices).
* ``gate`` — called by admission and transfer: runs the state-wide check, records it, notifies creditors and the
  family, and returns. If obligations are outstanding it requires a recorded human decision; it never refuses,
  never delays the records transfer and never touches attendance (P9). Learners entering public basic education
  are admitted automatically; heads can mark other protected learners.
* ``raise_dispute`` / ``resolve_dispute`` — families and institutions contest claims; the LGA or state decides.

This module never imports the finance ledger (import contract): the only payment-derived data that reaches an
admission decision is the published obligation summary.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import uuid
from dataclasses import dataclass
from typing import Any

from django.db import IntegrityError, transaction

from syntegra.clearance.domain import rules
from syntegra.clearance.models import ClearanceCheck, ClearanceDecision, LearnerObligation, ObligationDispute
from syntegra.core import authz, context, uow
from syntegra.core.canonical_json import canonicalize
from syntegra.core.errors import ConflictError, DomainError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.governance.models import ScopeNode
from syntegra.institutions.models import Institution
from syntegra.learners.models import Learner


class ClearanceDecisionRequired(DomainError):
    """409: obligations are outstanding — repeat the request with a clearance decision (never a refusal)."""

    def __init__(self, check: ClearanceCheck):
        super().__init__(
            "FCL-DECISION-REQUIRED",
            "Outstanding fees or dues at another institution",
            "Record an admission decision: admit, admit with a payment plan, defer pending settlement, or admit "
            "as a protected learner. The learner's records transfer is not affected.",
            409,
            [],
            {
                "clearance_check_id": str(check.id),
                "result": check.result,
                "total_outstanding_minor": check.total_outstanding_minor,
                "currency": check.currency,
                "obligations": check.obligations,
                "pattern_flags": check.pattern_flags or [],
                "allowed_decisions": list(rules.DECISIONS),
            },
        )


class AdmissionDeferred(DomainError):
    def __init__(self, check_id: uuid.UUID):
        super().__init__(
            "FCL-ADMISSION-DEFERRED",
            "Admission deferred pending settlement",
            "The decision was recorded; no enrolment was created.",
            409,
            [],
            {"clearance_check_id": str(check_id)},
        )


@dataclass
class DecisionInput:
    decision: str
    reason: str
    check_id: uuid.UUID | None = None
    protected_reason: str | None = None
    payment_plan_ref: str | None = None


# --------------------------------------------------------------------------- publication (creditor side)
def publish(
    *,
    learner_id: uuid.UUID,
    creditor_institution_id: uuid.UUID,
    kind: str,
    amount_minor: int,
    oldest_due_on: dt.date,
    evidence: list[Any],
    periods: list[str] | None = None,
    payer_kind: str = "guardian",
    source: str = "ledger",
    currency: str = "NGN",
) -> LearnerObligation | None:
    """Create or refresh the open obligation for learner × creditor × kind; amount 0 settles it."""
    ctx = context.require()
    authz.require("clearance:publish", ctx)
    inst = Institution.objects.filter(pk=creditor_institution_id).first()
    if inst is None:
        raise NotFound("institution", creditor_institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    today = dt.date.today()
    with uow.command("registry", None, action="publish", record_kind="learner_obligation") as cmd:
        cur = (
            LearnerObligation.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(
                tenant_id=ctx.state_tenant_id,
                learner_id=learner_id,
                creditor_institution_id=inst.id,
                obligation_kind=kind,
                status__in=rules.OPEN,
            )
            .first()
        )
        if amount_minor <= 0:
            if cur is None:
                cmd.audited = False
                return None
            cmd.update(cur, status="settled", settled_at=utcnow())
            cmd.emit(
                "FCL.OBLIGATION_SETTLED",
                aggregate_id=cur.id,
                scope_node_id=inst.scope_node_id,
                payload={"learner_obligation_id": cur.id, "status": "settled"},
            )
            return cur
        errs = rules.validate_publication(
            kind=kind,
            amount_minor=amount_minor,
            oldest_due_on=oldest_due_on,
            evidence=evidence,
            source=source,
            on=today,
        )
        if errs:
            raise HardValidation(
                "FCL-PUBLICATION",
                "Obligation cannot be published",
                errors=[{"field": None, "message": e} for e in errs],
            )
        ev_hash = hashlib.sha256(canonicalize(evidence)).digest()
        fields = {
            "amount_outstanding_minor": amount_minor,
            "oldest_due_on": oldest_due_on,
            "evidence": evidence,
            "evidence_hash": ev_hash,
            "periods": periods,
            "published_by": ctx.actor_id or uuid.UUID(int=0),
            "published_at": utcnow(),
            "reconfirm_by": today + dt.timedelta(days=rules.RECONFIRM_DAYS),
            "currency": currency,
            "payer_kind": payer_kind,
            "source": source,
        }
        if cur is not None:
            if cur.status == "disputed" and amount_minor > cur.amount_outstanding_minor:
                raise ConflictError(
                    "FCL-DISPUTED",
                    "Obligation under dispute",
                    "A disputed obligation cannot be increased until the dispute is resolved.",
                )
            ob = cmd.update(cur, **fields)
        else:
            ob = cmd.add(
                LearnerObligation(
                    scope_node_id=inst.scope_node_id,
                    learner_id=learner_id,
                    creditor_institution_id=inst.id,
                    creditor_tenant_id=inst.operating_tenant_id,
                    obligation_kind=kind,
                    status="outstanding",
                    **fields,
                )
            )
        cmd.emit(
            "FCL.OBLIGATION_PUBLISHED",
            aggregate_id=ob.id,
            scope_node_id=inst.scope_node_id,
            payload={"learner_obligation_id": ob.id, "creditor_institution_id": inst.id},
        )
        return ob


def set_status(obligation_id: uuid.UUID, status: str, reason: str) -> LearnerObligation:
    """Creditor marks an obligation as on a payment plan, waived, written off or withdrawn."""
    if status not in ("payment_plan", "waived", "written_off", "withdrawn", "settled"):
        raise HardValidation("FCL-STATUS", "Status not allowed", status)
    with uow.command(
        "registry", "clearance:publish", action=status, record_kind="learner_obligation", reason=reason
    ) as cmd:
        ob = cmd.lock(LearnerObligation, obligation_id)
        if ob.status not in rules.OPEN:
            raise ConflictError("FCL-CLOSED", "Obligation is closed", ob.status)
        cmd.update(ob, status=status, settled_at=utcnow() if status != "payment_plan" else None)
        if status != "payment_plan":
            cmd.emit(
                "FCL.OBLIGATION_SETTLED",
                aggregate_id=ob.id,
                scope_node_id=ob.scope_node_id,
                payload={"learner_obligation_id": ob.id, "status": status},
            )
        return ob


def expire_stale(on: dt.date | None = None) -> int:
    """Nightly: obligations the creditor did not reconfirm within 90 days expire (FR-FCL-07)."""
    ctx = context.require()
    on = on or dt.date.today()
    n = 0
    with uow.command("registry", "clearance:administer", action="expire", record_kind="learner_obligation") as cmd:
        for ob in (
            LearnerObligation.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(tenant_id=ctx.state_tenant_id, status__in=("outstanding", "payment_plan"), reconfirm_by__lt=on)
        ):
            cmd.update(ob, status="expired", settled_at=utcnow())
            cmd.emit(
                "FCL.OBLIGATION_SETTLED",
                aggregate_id=ob.id,
                scope_node_id=ob.scope_node_id,
                payload={"learner_obligation_id": ob.id, "status": "expired"},
            )
            n += 1
        if not n:
            cmd.audited = False
    return n


# --------------------------------------------------------------------------- the check (admitting side)
def _snapshot(ob: LearnerObligation, names: dict[uuid.UUID, str]) -> rules.Obligation:
    return rules.Obligation(
        ob.id,
        ob.creditor_institution_id,
        names.get(ob.creditor_institution_id, "?"),
        ob.obligation_kind,
        ob.amount_outstanding_minor,
        ob.currency,
        ob.oldest_due_on,
        ob.status,
    )


def check(
    learner_id: uuid.UUID,
    requesting_institution_id: uuid.UUID,
    *,
    purpose: str,
    education_level: str,
    learner_transfer_id: uuid.UUID | None = None,
    admission_application_id: uuid.UUID | None = None,
    basis: str = "admission_due_diligence",
) -> ClearanceCheck:
    """Run and record a state-wide clearance check (purpose-bound: only for an admission or transfer here)."""
    ctx = context.require()
    authz.require("clearance:check", ctx)
    inst = Institution.objects.filter(pk=requesting_institution_id).first()
    if inst is None or not Learner.objects.filter(pk=learner_id).exists():
        raise NotFound("institution or learner")
    authz.require_scope(inst.scope_node_id, ctx)
    # The register is state-wide by design: every creditor institution, public or private.
    obs = list(
        LearnerObligation.objects.filter(learner_id=learner_id, status__in=rules.OPEN).exclude(
            creditor_institution_id=inst.id
        )
    )
    names = dict(Institution.objects.filter(id__in={o.creditor_institution_id for o in obs}).values_list("id", "name"))
    since = utcnow() - dt.timedelta(days=730)
    prior = (
        ClearanceCheck.objects.filter(learner_id=learner_id, result="outstanding", checked_at__gte=since)
        .exclude(requesting_institution_id=inst.id)
        .values("requesting_institution_id")
        .distinct()
        .count()
    )
    protected = "public_basic_education" if rules.is_public_basic_education(inst.is_public, education_level) else None
    a = rules.assess(
        [_snapshot(o, names) for o in obs],
        protected_reason=protected,
        prior_outstanding_checks=prior,
        creditors_with_open=len({o.creditor_institution_id for o in obs if o.status != "disputed"}),
    )
    with uow.command("registry", None, action="clearance_check", record_kind="clearance_check") as cmd:
        chk = cmd.add(
            ClearanceCheck(
                learner_id=learner_id,
                requesting_institution_id=inst.id,
                purpose=purpose,
                basis=basis,
                admission_application_id=admission_application_id,
                learner_transfer_id=learner_transfer_id,
                requested_by=ctx.actor_id or uuid.UUID(int=0),
                checked_at=utcnow(),
                coverage="state",
                result=a.result,
                obligations=[
                    {
                        "obligation_id": str(o.id),
                        "creditor_institution_id": str(o.creditor_institution_id),
                        "creditor": o.creditor_name,
                        "kind": o.kind,
                        "amount_minor": o.amount_minor,
                        "currency": o.currency,
                        "oldest_due_on": o.oldest_due_on.isoformat(),
                        "status": o.status,
                    }
                    for o in a.obligations
                ],
                total_outstanding_minor=a.total_outstanding_minor,
                currency="NGN",
                pattern_flags=a.pattern_flags or None,
            )
        )
        LearnerObligation.unscoped.using(cmd.alias).filter(id__in=[o.id for o in obs]).update(
            last_checked_at=chk.checked_at
        )
        cmd.record_id = chk.id
        cmd.emit(
            "FCL.CHECK_PERFORMED",
            aggregate_id=chk.id,
            scope_node_id=inst.scope_node_id,
            payload={"clearance_check_id": chk.id, "learner_id": learner_id, "result": a.result},
        )
        if protected:
            _record_decision(
                cmd,
                chk,
                "admit_protected",
                "Public basic education is free under the UBE Act 2004; the obligation stays with the creditor.",
                protected,
                None,
                system=True,
            )
        return chk


def _record_decision(
    cmd: uow.Command,
    chk: ClearanceCheck,
    decision: str,
    reason: str,
    protected_reason: str | None,
    payment_plan_ref: str | None,
    *,
    system: bool = False,
) -> ClearanceDecision:
    try:
        with transaction.atomic(using=cmd.alias):
            d = cmd.add(
                ClearanceDecision(
                    check_id=chk.id,
                    decision=decision,
                    protected_reason=protected_reason,
                    reason=reason,
                    payment_plan_ref=payment_plan_ref,
                    decided_by=uuid.UUID(int=0) if system else cmd.ctx.actor_id,
                    decided_at=utcnow(),
                )
            )
    except IntegrityError as exc:
        raise ConflictError("FCL-DECIDED", "Decision already recorded", "Run a new check.") from exc
    cmd.emit("FCL.DECISION_RECORDED", aggregate_id=d.id, payload={"clearance_decision_id": d.id, "decision": decision})
    return d


def decide(check_id: uuid.UUID, d: DecisionInput) -> ClearanceDecision:
    """Record the human admission decision on a check (permission admission:decide; people only)."""
    ctx = context.require()
    authz.require("admission:decide", ctx)
    if ctx.actor_kind != "user":
        raise Forbidden("Admission decisions are made by people (A1).", code="HUMAN-ONLY")
    errs = rules.decision_errors(
        d.decision, protected_reason=d.protected_reason, payment_plan_ref=d.payment_plan_ref, reason=d.reason
    )
    if errs:
        raise HardValidation(
            "FCL-DECISION", "Decision incomplete", errors=[{"field": None, "message": e} for e in errs]
        )
    with uow.command(
        "registry", None, action="clearance_decision", record_kind="clearance_check", reason=d.reason
    ) as cmd:
        chk = ClearanceCheck.unscoped.using(cmd.alias).filter(tenant_id=ctx.state_tenant_id, pk=check_id).first()
        if chk is None:
            raise NotFound("clearance check", check_id)
        inst = Institution.objects.get(pk=chk.requesting_institution_id)
        authz.require_scope(inst.scope_node_id, ctx)
        cmd.record_id = chk.id
        return _record_decision(cmd, chk, d.decision, d.reason, d.protected_reason, d.payment_plan_ref)


def gate(
    learner_id: uuid.UUID,
    institution_id: uuid.UUID,
    *,
    purpose: str,
    education_level: str,
    decision: DecisionInput | None = None,
) -> ClearanceCheck | None:
    """Pre-admission due diligence used by learner registration and transfer.

    Returns the check when the learner may be enrolled; raises ``ClearanceDecisionRequired`` (409, nothing
    enrolled, check logged) or ``AdmissionDeferred`` (decision recorded, nothing enrolled).
    """
    chk = None
    if decision and decision.check_id:
        chk = ClearanceCheck.objects.filter(
            pk=decision.check_id,
            learner_id=learner_id,
            requesting_institution_id=institution_id,
            checked_at__gte=utcnow() - dt.timedelta(hours=24),
        ).first()
        if chk is None:
            raise HardValidation(
                "FCL-CHECK-STALE", "Clearance check not found or older than 24 hours", "Run a new check."
            )
    if chk is None:
        chk = check(learner_id, institution_id, purpose=purpose, education_level=education_level)
    existing = ClearanceDecision.objects.filter(check_id=chk.id).first()
    if chk.result in ("clear", "disputed_only") or (existing and existing.decision != "defer_pending_settlement"):
        return chk
    if existing is None:
        if decision is None:
            raise ClearanceDecisionRequired(chk)
        existing = decide(chk.id, decision)
    if existing.decision == "defer_pending_settlement":
        raise AdmissionDeferred(chk.id)
    return chk


# --------------------------------------------------------------------------- disputes
def raise_dispute(
    obligation_id: uuid.UUID,
    *,
    party: str,
    grounds: str,
    statement: str,
    evidence_document_ids: list[str] | None = None,
) -> ObligationDispute:
    from syntegra.curriculum.domain.coverage import add_school_days

    ctx = context.require()
    authz.require("clearance:dispute", ctx)
    with uow.command("registry", None, action="dispute", record_kind="learner_obligation") as cmd:
        ob = (
            LearnerObligation.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(tenant_id=ctx.state_tenant_id, pk=obligation_id)
            .first()
        )
        if ob is None or ob.status not in ("outstanding", "payment_plan"):
            raise ConflictError("FCL-NOT-DISPUTABLE", "Only open obligations can be disputed", "")
        inst = Institution.objects.get(pk=ob.creditor_institution_id)
        resolver = ScopeNode.objects.filter(pk=inst.lga_scope_id).first()
        basis = _dispute_basis(ctx, ob, party)
        d = cmd.add(
            ObligationDispute(
                scope_node_id=ob.scope_node_id,
                obligation_id=ob.id,
                raised_by_kind=party,
                raised_by=ctx.actor_id,
                grounds=grounds,
                statement=statement,
                evidence_document_ids=evidence_document_ids or [],
                due_by=add_school_days(dt.date.today(), rules.DISPUTE_SCHOOL_DAYS),
                resolver_scope_id=resolver.id if resolver else inst.scope_node_id,
                currency=ob.currency,
                status="open",
            ),
            cross_scope_basis=basis,
        )
        cmd.update(ob, status="disputed")
        cmd.record_id = ob.id
        cmd.emit(
            "FCL.DISPUTE_RAISED",
            aggregate_id=d.id,
            scope_node_id=ob.scope_node_id,
            payload={"obligation_dispute_id": d.id, "learner_obligation_id": ob.id},
        )
        return d


def _dispute_basis(ctx: context.Context, ob: LearnerObligation, party: str) -> str | None:
    """Who may dispute: the creditor (own scope), or an institution that checked this learner within 30 days.

    Families dispute through the parent portal (guardian identity), which uses the same rule as the admitting
    institution: they are a party to the check. Anyone else is refused.
    """
    if ctx.scope_ids is None or ob.scope_node_id in ctx.scope_ids:
        return None  # in scope (creditor or a higher level): the normal scope check applies
    recent = ClearanceCheck.objects.filter(learner_id=ob.learner_id, checked_at__gte=utcnow() - dt.timedelta(days=30))
    mine = [
        c
        for c in recent
        if Institution.objects.filter(pk=c.requesting_institution_id, scope_node_id__in=list(ctx.scope_ids)).exists()
    ]
    if party in ("admitting_institution", "guardian", "learner") and mine:
        return f"party to clearance check {mine[0].id}"
    raise Forbidden("Only the creditor or an institution that checked this learner may dispute.", code="AUTH-SCOPE")


def resolve_dispute(
    dispute_id: uuid.UUID, resolution: str, *, resolved_amount_minor: int | None = None, reason: str
) -> ObligationDispute:
    ctx = context.require()
    authz.require("clearance:resolve", ctx)
    if ctx.actor_kind != "user":
        raise Forbidden("Disputes are resolved by people.", code="HUMAN-ONLY")
    with uow.command(
        "registry", None, action=f"dispute_{resolution}", record_kind="obligation_dispute", reason=reason
    ) as cmd:
        d = cmd.lock(ObligationDispute, dispute_id)
        if d.status == "closed":
            raise ConflictError("FCL-DISPUTE-CLOSED", "Dispute already resolved", "")
        authz.require_scope(d.resolver_scope_id, ctx)
        ob = cmd.lock(LearnerObligation, d.obligation_id)
        if resolution == "upheld":
            cmd.update(ob, status="withdrawn", settled_at=utcnow())
        elif resolution == "partly_upheld":
            if not resolved_amount_minor or resolved_amount_minor >= ob.amount_outstanding_minor:
                raise HardValidation("FCL-RESOLVED-AMOUNT", "Give the reduced amount", "")
            cmd.update(ob, status="outstanding", amount_outstanding_minor=resolved_amount_minor)
        else:
            cmd.update(ob, status="outstanding")
        cmd.update(
            d,
            resolution=resolution,
            resolved_amount_minor=resolved_amount_minor,
            resolved_by_id=ctx.actor_id,
            resolved_at=utcnow(),
            status="closed",
        )
        cmd.emit(
            "FCL.DISPUTE_RESOLVED",
            aggregate_id=d.id,
            scope_node_id=ob.scope_node_id,
            payload={"obligation_dispute_id": d.id, "resolution": resolution},
        )
        return d


# --------------------------------------------------------------------------- transparency
def checks_about(learner_id: uuid.UUID) -> list[dict[str, Any]]:
    """Every check run about a learner — what the family sees (FR-FCL-08)."""
    authz.require("learner:view")
    from syntegra.learners import services as learners

    learners.get(learner_id)
    names = dict(Institution.objects.values_list("id", "name"))
    out = []
    for c in ClearanceCheck.objects.filter(learner_id=learner_id).order_by("-checked_at"):
        dec = ClearanceDecision.objects.filter(check_id=c.id).first()
        out.append(
            {
                "checked_at": c.checked_at,
                "by_institution": names.get(c.requesting_institution_id),
                "purpose": c.purpose,
                "result": c.result,
                "decision": dec.decision if dec else None,
            }
        )
    return out
