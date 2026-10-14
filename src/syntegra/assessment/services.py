"""Assessment and results (MFS §11, FR-ASM-01 – FR-ASM-05).

A teacher (or examinations officer) creates an assessment for a class-subject — a continuous-assessment test, an
examination, coursework — with its maximum mark and weight; marks are entered for the class in one batch (hard
rule: 0 ≤ score ≤ maximum), each mark gets its grade label from the grading scale, and the assessment is locked
after approval (corrections after the lock need the head's approval and are flagged).
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from syntegra.academic.models import ClassGroup, ClassSubjectPlan
from syntegra.assessment.models import Assessment, AssessmentResult
from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.core.fields import utcnow

# WAEC/NECO-style grade bands (percentage), the default where no grading scale is configured
WAEC_BANDS: tuple[tuple[float, str], ...] = (
    (75, "A1"), (70, "B2"), (65, "B3"), (60, "C4"), (55, "C5"), (50, "C6"), (45, "D7"), (40, "E8"), (0, "F9"),
)  # fmt: skip
CREDIT = ("A1", "B2", "B3", "C4", "C5", "C6")


def grade(percent: float) -> str:
    for floor, label in WAEC_BANDS:
        if percent >= floor:
            return label
    return "F9"


def create_assessment(
    plan_id: uuid.UUID,
    title: str,
    kind: str,
    *,
    max_mark: Decimal | int = 100,
    weight: Decimal | int = 100,
    assessed_on: dt.date | None = None,
) -> Assessment:
    plan = ClassSubjectPlan.objects.filter(pk=plan_id).first()
    if plan is None:
        raise NotFound("class subject", plan_id)
    cls = ClassGroup.objects.in_scope().filter(pk=plan.class_group_id).first()
    if cls is None:
        raise NotFound("class", plan.class_group_id)
    if not 0 < Decimal(weight) <= 100 or Decimal(max_mark) <= 0:
        raise HardValidation("ASM-DEFINITION", "Maximum mark and weight", "Weight is 1–100 %; maximum mark > 0.")
    with uow.command("ops", "assessment:manage", action="create", record_kind="assessment") as cmd:
        a = cmd.add(
            Assessment(
                scope_node_id=cls.scope_node_id,
                class_subject_plan_id=plan.id,
                title=title,
                assessment_kind=kind,
                max_mark=Decimal(max_mark),
                weight=Decimal(weight),
                assessed_on=assessed_on or dt.date.today(),
                status="open",
            )
        )
        cmd.emit("ASM.ASSESSMENT_CREATED", aggregate_id=a.id, payload={"assessment_id": str(a.id)})
        return a


def record_results(
    assessment_id: uuid.UUID, marks: Sequence[tuple[uuid.UUID, float | Decimal | None]], *, lock: bool = False
) -> dict[str, Any]:
    """Enter (or update before the lock) the marks of an assessment in one batch. ``None`` records missing work."""
    ctx = context.require()
    with uow.command("ops", "assessment:enter", action="enter_results", record_kind="assessment") as cmd:
        a = cmd.lock(Assessment, assessment_id)
        if a.status == "locked":
            raise ConflictError("ASM-LOCKED", "Results are locked", "Corrections need the head's approval.")
        errors = []
        for lid, score in marks:
            if score is not None and not 0 <= Decimal(str(score)) <= a.max_mark:
                errors.append({"field": str(lid), "message": f"score must be between 0 and {a.max_mark}"})
        if errors:
            raise HardValidation("ASM-MARK-RANGE", "Some marks are out of range", errors=errors)
        existing = {r.learner_id: r for r in AssessmentResult.objects.filter(assessment_id=a.id)}
        new = []
        updated = 0
        for lid, score in marks:
            value = Decimal(str(score)).quantize(Decimal("0.001")) if score is not None else None
            label = grade(float(value / a.max_mark * 100)) if value is not None else None
            r = existing.get(lid)
            if r is None:
                new.append(
                    AssessmentResult(
                        tenant_id=ctx.tenant_id,
                        assessment_id=a.id,
                        learner_id=lid,
                        score=value,
                        grade_label=label,
                        is_missing_work=value is None,
                        entered_by=ctx.actor_id,
                        created_by=ctx.actor_id,
                    )
                )
            elif r.score != value:
                cmd.update(r, score=value, grade_label=label, is_missing_work=value is None)
                updated += 1
        AssessmentResult.unscoped.using(cmd.alias).bulk_create(new, batch_size=2000)
        cmd.note("results", None, {"created": len(new), "updated": updated})
        if lock:
            cmd.update(a, status="locked", locked_at=utcnow())
            cmd.emit("ASM.RESULTS_LOCKED", aggregate_id=a.id, payload={"assessment_id": str(a.id)})
        elif a.status == "open":
            cmd.update(a, status="marking")
        return {"created": len(new), "updated": updated, "locked": lock}


def lock(assessment_id: uuid.UUID) -> Assessment:
    with uow.command("ops", "assessment:approve", action="lock", record_kind="assessment") as cmd:
        a = cmd.lock(Assessment, assessment_id)
        if a.status == "locked":
            return a
        a = cmd.update(a, status="locked", locked_at=utcnow())
        cmd.emit("ASM.RESULTS_LOCKED", aggregate_id=a.id, payload={"assessment_id": str(a.id)})
        return a


def class_results(class_id: uuid.UUID) -> dict[str, Any]:
    """Broadsheet of a class: each learner's weighted total per subject and overall average."""
    authz.require("assessment:view")
    cls = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    if cls is None:
        raise NotFound("class", class_id)
    plans = {p.id: p for p in ClassSubjectPlan.objects.filter(class_group_id=cls.id)}
    assessments = {a.id: a for a in Assessment.objects.filter(class_subject_plan_id__in=list(plans))}
    totals: dict[uuid.UUID, dict[uuid.UUID, float]] = {}
    for r in AssessmentResult.objects.filter(assessment_id__in=list(assessments)).exclude(score=None):
        a = assessments[r.assessment_id]
        part = float(r.score / a.max_mark) * float(a.weight)
        subj = plans[a.class_subject_plan_id].subject_id
        totals.setdefault(r.learner_id, {}).setdefault(subj, 0.0)
        totals[r.learner_id][subj] += part
    rows: list[dict[str, Any]] = [
        {"learner_id": lid, "subjects": subj, "average": round(sum(subj.values()) / len(subj), 2) if subj else None}
        for lid, subj in totals.items()
    ]
    rows.sort(key=lambda x: -float(x["average"] or 0))
    for i, row in enumerate(rows, start=1):
        row["position"] = i
    return {"class_id": cls.id, "name": cls.name, "rows": rows}
