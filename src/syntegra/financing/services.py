"""State Digital Access Fee financing (MFS §19, FR-SDAF-*): census, once-per-period billing, demands.

* The census counts learners actively enrolled on the census date; each is billable, exempt (approved
  exemption) or excluded (with reason). A head confirms; the frozen count carries a content hash.
* A learner is billed at most once per billing period across all institutions and channels
  (``uq_billing_period_billed_…``): a learner already billed elsewhere is excluded with
  ``other_institution_holds``.
* Payer rules: public basic education (primary and junior secondary) is always paid by government — the
  UBE Act — enforced in the payer rule and in the demand (``ck_sdaf_demand__ube_act``).
* Demand amount = (billable − waived) × rate in minor units (kobo).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import uuid
from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Q

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.ids import short_code
from syntegra.financing.domain import sdaf
from syntegra.financing.models import (
    BillingPeriod,
    BillingPeriodBilled,
    CensusLearner,
    CensusSnapshot,
    SdafDemand,
    SdafExemption,
    SdafPayerRule,
    SdafRate,
    SdafRateCard,
)
from syntegra.institutions.models import Institution
from syntegra.learners.models import Enrolment, Learner


def publish_rate_card(
    scope_node_id: uuid.UUID,
    rates: list[tuple[str, str, int]],
    *,
    effective_from: dt.date,
    proposed_by: uuid.UUID,
    approval_instrument: str,
) -> SdafRateCard:
    """Publish a rate card: ``rates`` = (institution_type, education_level, amount_minor per term)."""
    ctx = context.require()
    if proposed_by == ctx.actor_id:
        raise HardValidation("SDAF-FOUR-EYES", "Approver must differ from proposer", "")
    with uow.command("registry", "financing:approve", action="publish", record_kind="sdaf_rate_card") as cmd:
        version = (SdafRateCard.objects.filter(scope_node_id=scope_node_id).count()) + 1
        card = cmd.add(
            SdafRateCard(
                scope_node_id=scope_node_id,
                version=version,
                proposed_by_id=proposed_by,
                approved_by_id=ctx.actor_id,
                approval_instrument=approval_instrument,
                effective_from=effective_from,
                published_at=utcnow(),
                status="published",
            )
        )
        for itype, level, amount in rates:
            cmd.add(
                SdafRate(
                    rate_card_id=card.id,
                    institution_type=itype,
                    education_level=level,
                    charge_period="per_term",
                    amount_minor=amount,
                    currency="NGN",
                )
            )
        return card


def set_payer_rule(
    scope_node_id: uuid.UUID, institution_type: str, education_level: str, payer: str, *, public: bool
) -> SdafPayerRule:
    basic = sdaf.is_basic_education(education_level, public)
    if basic and payer != "government":
        raise HardValidation(
            "SDAF-UBE",
            "Basic education is free",
            "Public primary and junior secondary are paid by government (UBE Act 2004).",
        )
    with uow.command("registry", "financing:manage", action="publish", record_kind="sdaf_payer_rule") as cmd:
        v = (
            SdafPayerRule.objects.filter(
                scope_node_id=scope_node_id, institution_type=institution_type, education_level=education_level
            ).count()
            + 1
        )
        return cmd.add(
            SdafPayerRule(
                scope_node_id=scope_node_id,
                institution_type=institution_type,
                education_level=education_level,
                is_basic_education=basic,
                payer=payer,
                version=v,
                status="published",
            )
        )


def open_period(
    scope_node_id: uuid.UUID,
    academic_period_id: uuid.UUID,
    label: str,
    census_on: dt.date,
    institution_types: list[str],
) -> BillingPeriod:
    with uow.command("registry", "financing:manage", action="open", record_kind="billing_period") as cmd:
        return cmd.add(
            BillingPeriod(
                scope_node_id=scope_node_id,
                academic_period_id=academic_period_id,
                institution_types=institution_types,
                label=label,
                census_on=census_on,
                confirmation_closes_on=census_on + dt.timedelta(days=7),
                collection_window_ends_on=census_on + dt.timedelta(days=42),
                remittance_due_on=census_on + dt.timedelta(days=56),
                status="census_open",
            )
        )


def take_census(institution_id: uuid.UUID, billing_period_id: uuid.UUID) -> CensusSnapshot:
    ctx = context.require()
    authz.require("census:take", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    period = BillingPeriod.objects.filter(pk=billing_period_id).first()
    if inst is None or period is None:
        raise NotFound("institution or billing period")
    authz.require_scope(inst.scope_node_id, ctx)
    on = period.census_on
    enrolments = list(
        Enrolment.objects.filter(institution_id=inst.id, is_primary=True, start_on__lte=on)
        .filter(Q(end_on__isnull=True) | Q(end_on__gte=on))
        .exclude(status__in=("pending", "withdrawn"))
    )
    learners = {lr.id: lr for lr in Learner.objects.filter(id__in=[e.learner_id for e in enrolments])}
    billed_elsewhere = set(
        BillingPeriodBilled.objects.filter(billing_period_id=period.id)
        .exclude(institution_id=inst.id)
        .values_list("learner_id", flat=True)
    )
    exempt = set(
        SdafExemption.objects.filter(billing_period_id=period.id, status__in=("approved", "fulfilled")).values_list(
            "learner_id", flat=True
        )
    )
    lines = sdaf.classify(
        [
            sdaf.CensusInput(e.learner_id, e.id, learners[e.learner_id].identity_verified_level != "unverified")
            for e in enrolments
        ],
        billed_elsewhere=billed_elsewhere,
        exempt=exempt,
    )
    totals = sdaf.totals(lines)
    with uow.command("registry", None, action="take_census", record_kind="census_snapshot") as cmd:
        prev = (
            CensusSnapshot.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(tenant_id=ctx.state_tenant_id, institution_id=inst.id, billing_period_id=period.id)
            .order_by("-version")
        )
        prev_list = list(prev)
        if prev_list and prev_list[0].status == "frozen":
            raise ConflictError("SDAF-FROZEN", "Census already frozen", "Challenge the frozen count instead.")
        for p in prev_list:
            if p.status != "superseded":
                cmd.update(p, status="superseded")
        snap = cmd.add(
            CensusSnapshot(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                billing_period_id=period.id,
                version=(prev_list[0].version + 1) if prev_list else 1,
                enrolled=totals["enrolled"],
                verified=totals["verified"],
                excluded=totals["excluded"],
                exempted=totals["exempt"],
                billable=totals["billable"],
                open_flags=0,
                status="awaiting_confirmation",
            )
        )
        CensusLearner.unscoped.using(cmd.alias).bulk_create(
            [
                CensusLearner(
                    tenant_id=ctx.state_tenant_id,
                    snapshot_id=snap.id,
                    learner_id=ln.learner_id,
                    enrolment_id=ln.enrolment_id,
                    inclusion=ln.inclusion,
                    reason=ln.reason,
                )
                for ln in lines
            ]
        )
        cmd.note("census", None, totals)
        return snap


def confirm_and_freeze(snapshot_id: uuid.UUID) -> CensusSnapshot:
    """Head confirms the count; the snapshot is frozen and every billable learner is marked billed."""
    ctx = context.require()
    with uow.command("registry", "census:confirm", action="freeze", record_kind="census_snapshot") as cmd:
        snap = cmd.lock(CensusSnapshot, snapshot_id)
        if snap.status != "awaiting_confirmation":
            raise ConflictError("SDAF-STATE", "Census not awaiting confirmation", f"It is {snap.status}.")
        rows = list(CensusLearner.unscoped.using(cmd.alias).filter(tenant_id=ctx.state_tenant_id, snapshot_id=snap.id))
        digest = sdaf.content_hash([(r.learner_id, r.inclusion) for r in rows])
        try:
            with transaction.atomic(using=cmd.alias):
                BillingPeriodBilled.unscoped.using(cmd.alias).bulk_create(
                    [
                        BillingPeriodBilled(
                            tenant_id=ctx.state_tenant_id,
                            billing_period_id=snap.billing_period_id,
                            learner_id=r.learner_id,
                            channel="sdaf",
                            institution_id=snap.institution_id,
                            snapshot_id=snap.id,
                        )
                        for r in rows
                        if r.inclusion == "billable"
                    ]
                )
        except IntegrityError as exc:
            raise ConflictError(
                "SDAF-ALREADY-BILLED",
                "Learner already billed this period",
                "Another institution froze a census including the same learner; retake the census.",
            ) from exc
        now = utcnow()
        cmd.update(
            snap, status="frozen", confirmed_by_id=ctx.actor_id, confirmed_at=now, frozen_at=now, content_hash=digest
        )
        return snap


def issue_demand(snapshot_id: uuid.UUID) -> list[SdafDemand]:
    ctx = context.require()
    authz.require("financing:demand", ctx)
    snap = CensusSnapshot.objects.filter(pk=snapshot_id, status="frozen").first()
    if snap is None:
        raise ConflictError("SDAF-NOT-FROZEN", "Census not frozen", "Freeze the census before issuing a demand.")
    inst = Institution.objects.get(pk=snap.institution_id)
    if SdafDemand.objects.filter(snapshot_id=snap.id).exclude(status="cancelled").exists():
        raise ConflictError("SDAF-DEMAND-EXISTS", "Demand already issued", "")
    levels = list(
        Enrolment.objects.filter(
            id__in=CensusLearner.objects.filter(snapshot_id=snap.id, inclusion="billable").values("enrolment_id")
        ).values_list("education_level", "learner_id")
    )
    by_level: dict[str, list[uuid.UUID]] = {}
    for level, learner in levels:
        by_level.setdefault(level, []).append(learner)
    out: list[SdafDemand] = []
    with uow.command("registry", None, action="issue_demand", record_kind="census_snapshot") as cmd:
        cmd.record_id = snap.id
        for level, learners in sorted(by_level.items()):
            rate = _rate(inst.category, level)
            rule = _payer(inst, level)
            basic = sdaf.is_basic_education(level, inst.is_public)
            payer = "government" if basic else rule
            per_learner = payer == "parent_or_student"
            targets: list[uuid.UUID | None] = list(learners) if per_learner else [None]
            for learner_id in targets:
                count = 1 if per_learner else len(learners)
                d = cmd.add(
                    SdafDemand(
                        scope_node_id=inst.scope_node_id,
                        demand_number=f"SDAF-{short_code().replace('-', '')}",
                        institution_id=inst.id,
                        billing_period_id=snap.billing_period_id,
                        snapshot_id=snap.id,
                        payer_kind=payer,
                        payer_ref=None,
                        learner_id=learner_id,
                        billable_count=count,
                        waived_count=0,
                        rate_id=rate.id,
                        amount_minor=sdaf.amount(count, 0, rate.amount_minor),
                        currency=rate.currency,
                        revenue_code="12040001",
                        payment_reference=f"RRR{uuid.uuid4().int % 10**12:012d}",
                        issued_at=utcnow(),
                        is_basic_education=basic,
                        status="issued",
                    )
                )
                out.append(d)
        return out


def _rate(institution_type: str, level: str) -> SdafRate:
    card = (
        SdafRateCard.objects.filter(status="published", effective_from__lte=dt.date.today())
        .order_by("-version")
        .first()
    )
    if card is None:
        raise ConflictError("SDAF-NO-RATE", "No published rate card", "")
    rate: SdafRate | None = SdafRate.objects.filter(
        rate_card_id=card.id, institution_type=institution_type, education_level=level
    ).first()
    if rate is None:
        raise ConflictError(
            "SDAF-NO-RATE", "No rate for this institution type and level", f"{institution_type} / {level}"
        )
    return rate


def _payer(inst: Institution, level: str) -> str:
    rule = (
        SdafPayerRule.objects.filter(institution_type=inst.category, education_level=level, status="published")
        .order_by("-version")
        .first()
    )
    return rule.payer if rule else ("government" if inst.is_public else "parent_or_student")


def demand_summary(billing_period_id: uuid.UUID) -> dict[str, Any]:
    authz.require("financing:view")
    rows = SdafDemand.objects.in_scope().filter(billing_period_id=billing_period_id).exclude(status="cancelled")
    total = sum(d.amount_minor for d in rows)
    return {
        "billing_period_id": billing_period_id,
        "demands": rows.count(),
        "amount_minor": total,
        "content_hash": hashlib.sha256(str(total).encode()).hexdigest()[:16],
    }
