"""Coverage engine service (FR-CUR-106/107): evaluate G2 and G3, open, update and close gap records.

Gaps are deduplicated by the database (``uq_coverage_gap_open_key``: one open gap per rule per target).
Every state change is appended to ``gap_event`` and published (CUR.GAP_OPENED / CUR.GAP_CLOSED).
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.academic.models import ClassGroup, ClassMembership, ClassSubjectPlan, TeachingAssignment
from syntegra.core import authz, context, policy, uow
from syntegra.core.errors import ConflictError, NotFound
from syntegra.core.fields import utcnow
from syntegra.curriculum.domain import coverage
from syntegra.curriculum.models import CoverageGap, GapEvent
from syntegra.institutions.models import Institution
from syntegra.people import services as people


def _facts(plan: ClassSubjectPlan, cls: ClassGroup, on: dt.date) -> coverage.ClassSubjectFacts:
    tors = list(
        TeachingAssignment.objects.filter(class_subject_plan_id=plan.id, role="teacher_of_record", valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .values_list("staff_id", flat=True)
    )
    learners = (
        ClassMembership.objects.filter(class_group_id=cls.id, valid_from__lte=on).exclude(valid_to__lt=on).count()
    )
    return coverage.ClassSubjectFacts(
        plan_id=plan.id,
        class_id=cls.id,
        subject_id=plan.subject_id,
        level=cls.education_level,
        learners=learners,
        is_mandatory=plan.is_mandatory,
        teachers_of_record=tors,
        authorised={s: people.is_authorised(s, plan.subject_id, cls.education_level, on) for s in tors},
    )


def evaluate_institution(institution_id: uuid.UUID, on: dt.date | None = None) -> dict[str, Any]:
    """Run G2/G3 for every class-subject of the institution; returns counts of opened/updated/closed gaps."""
    ctx = context.require()
    authz.require("coverage:evaluate", ctx)
    on = on or dt.date.today()
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    rules = {r: policy.effective_rule(r.upper(), inst.scope_node_id) for r in ("g2", "g3")}
    breaches: dict[tuple[str, uuid.UUID], tuple[coverage.Breach, int]] = {}
    for cls in ClassGroup.objects.filter(institution_id=inst.id, status="active"):
        for plan in ClassSubjectPlan.objects.filter(class_group_id=cls.id, valid_from__lte=on).exclude(valid_to__lt=on):
            facts = _facts(plan, cls, on)
            for b in coverage.evaluate(facts):
                if rules.get(b.rule) is None:
                    continue  # rule not in force for this scope
                breaches[(b.rule, plan.id)] = (b, facts.learners)
    opened = updated = closed = 0
    with uow.command("ops", None, action="evaluate_coverage", record_kind="institution") as cmd:
        cmd.record_id = inst.id
        open_gaps = {
            (g.rule, g.class_subject_plan_id): g
            for g in CoverageGap.unscoped.using(cmd.alias).filter(
                tenant_id=ctx.tenant_id,
                institution_id=inst.id,
                rule__in=("g2", "g3"),
                status__in=("open", "in_progress", "escalated"),
            )
        }
        for key, (b, learners) in breaches.items():
            gap = open_gaps.get(key)
            rule = rules[b.rule]
            params = rule.parameters if rule else {}
            if gap is None:
                due = coverage.add_school_days(on, int(params.get("due_school_days", coverage.DUE_SCHOOL_DAYS[b.rule])))
                gap = cmd.add(
                    CoverageGap(
                        scope_node_id=inst.scope_node_id,
                        rule=b.rule,
                        severity=params.get("severity", b.severity),
                        institution_id=inst.id,
                        class_subject_plan_id=b.plan_id,
                        learners_affected=learners,
                        owner_role=params.get("owner_role", coverage.OWNER[b.rule]),
                        due_on=due,
                        opened_at=utcnow(),
                        suggested_fixes=_fixes(b),
                        status="open",
                    )
                )
                cmd.add(
                    GapEvent(
                        gap_id=gap.id,
                        event_kind="opened",
                        actor=ctx.actor_id,
                        detail={"detail": b.detail, "staff_id": str(b.staff_id) if b.staff_id else None},
                        occurred_at=utcnow(),
                    )
                )
                cmd.emit(
                    "CUR.GAP_OPENED",
                    aggregate_id=gap.id,
                    scope_node_id=inst.scope_node_id,
                    payload={
                        "coverage_gap_id": gap.id,
                        "institution_id": inst.id,
                        "rule": b.rule,
                        "severity": gap.severity,
                    },
                )
                opened += 1
            elif gap.learners_affected != learners:
                cmd.update(gap, learners_affected=learners)
                cmd.add(
                    GapEvent(
                        gap_id=gap.id,
                        event_kind="updated",
                        actor=ctx.actor_id,
                        detail={"learners_affected": learners},
                        occurred_at=utcnow(),
                    )
                )
                updated += 1
        for key, gap in open_gaps.items():
            if key not in breaches:
                _close(cmd, gap, "invariant satisfied")
                closed += 1
    return {"institution_id": inst.id, "opened": opened, "updated": updated, "closed": closed, "open": len(breaches)}


def _fixes(b: coverage.Breach) -> list[dict[str, str]]:
    if b.rule == "g2":
        return [
            {"fix": "assign_qualified_teacher_with_spare_load"},
            {"fix": "request_lga_deployment"},
            {"fix": "remote_teacher_via_lms_live_class"},
        ]
    return [
        {"fix": "reassign"},
        {"fix": "enrol_teacher_in_cpd_authorisation_route"},
        {"fix": "time_boxed_supervised_exception"},
    ]


def _close(cmd: uow.Command, gap: CoverageGap, reason: str) -> None:
    ctx = cmd.ctx
    cmd.update(gap, status="closed", closed_at=utcnow(), closed_by=ctx.actor_id)
    cmd.add(
        GapEvent(
            gap_id=gap.id, event_kind="closed", actor=ctx.actor_id, detail={"reason": reason}, occurred_at=utcnow()
        )
    )
    cmd.emit(
        "CUR.GAP_CLOSED", aggregate_id=gap.id, scope_node_id=gap.scope_node_id, payload={"coverage_gap_id": gap.id}
    )


def accept(gap_id: uuid.UUID, reason: str) -> CoverageGap:
    """Head accepts a gap (e.g. leaver handover in progress) — recorded, still visible to the LGA."""
    with uow.command("ops", "coverage:manage", action="accept", record_kind="coverage_gap", reason=reason) as cmd:
        gap = cmd.lock(CoverageGap, gap_id)
        if gap.status not in ("open", "in_progress", "escalated"):
            raise ConflictError("GAP-CLOSED", "Gap is not open", f"The gap is {gap.status}.")
        cmd.update(gap, status="accepted", accepted_by_head=True)
        cmd.add(
            GapEvent(
                gap_id=gap.id,
                event_kind="accepted",
                actor=cmd.ctx.actor_id,
                detail={"reason": reason},
                occurred_at=utcnow(),
            )
        )
        return gap


def escalate_overdue(on: dt.date | None = None) -> int:
    """Escalate open gaps past their due date one level up the hierarchy (LGA, then state)."""
    from syntegra.core.authz import ancestors

    ctx = context.require()
    on = on or dt.date.today()
    n = 0
    with uow.command("ops", "coverage:evaluate", action="escalate", record_kind="coverage_gap") as cmd:
        for gap in (
            CoverageGap.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(tenant_id=ctx.tenant_id, status__in=("open", "in_progress", "escalated"), due_on__lt=on)
        ):
            path = ancestors(ctx.state_tenant_id, gap.scope_node_id)  # type: ignore[arg-type]
            level = gap.escalation_level + 1
            if level >= len(path):
                continue
            cmd.update(
                gap,
                status="escalated",
                escalation_level=level,
                escalated_to_scope_id=path[level],
                due_on=coverage.add_school_days(on, 7 if level == 1 else 10),
            )
            cmd.add(
                GapEvent(
                    gap_id=gap.id,
                    event_kind="escalated",
                    actor=ctx.actor_id,
                    detail={"to_scope_id": str(path[level]), "level": level},
                    occurred_at=utcnow(),
                )
            )
            cmd.emit(
                "CUR.GAP_ESCALATED",
                aggregate_id=gap.id,
                scope_node_id=gap.scope_node_id,
                payload=_escalated_payload(gap),
            )
            n += 1
    return n


def _escalated_payload(gap: CoverageGap) -> dict[str, Any]:
    from syntegra.core import catalog

    spec = catalog.event("CUR.GAP_ESCALATED").get("payload") or {}
    full = {
        "coverage_gap_id": gap.id,
        "escalation_level": gap.escalation_level,
        "escalated_to_scope_id": gap.escalated_to_scope_id,
        "to_scope_id": gap.escalated_to_scope_id,
    }
    return {k: v for k, v in full.items() if k in spec}


def open_gaps(institution_id: uuid.UUID | None = None) -> list[CoverageGap]:
    authz.require("coverage:view")
    qs = CoverageGap.objects.in_scope().filter(status__in=("open", "in_progress", "escalated"))
    if institution_id:
        qs = qs.filter(institution_id=institution_id)
    return list(qs.order_by("due_on"))
