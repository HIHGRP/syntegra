"""Markbook — organised marksheets (MFS ASM-01, FR-ASM-01 – FR-ASM-05).

One sheet per class and subject: every assessment of the class-subject is a column (continuous-assessment tests,
examination, coursework …) with its maximum mark and weight, every learner of the class a row. The sheet works out
each learner's weighted total out of the weights set so far, the WAEC/NECO-style grade, the position in the subject
(equal totals share a position) and, per column, the class average, highest and lowest. The teacher of record adds
assessments and enters marks (0 to the maximum; blank for work not done); the head locks an assessment once the marks
are approved, after which they cannot be changed. The weights of a class-subject's assessments add up to at most 100.
"""

from __future__ import annotations

import datetime as dt
import uuid
from decimal import Decimal
from typing import Any

from syntegra.academic.models import (
    AcademicPeriod,
    ClassGroup,
    ClassMembership,
    ClassSubjectPlan,
    Subject,
    TeachingAssignment,
)
from syntegra.assessment import services
from syntegra.assessment.models import Assessment, AssessmentResult
from syntegra.core import authz, context
from syntegra.core.errors import Forbidden, HardValidation, NotFound

KINDS = {
    "ca_test": "Continuous assessment test",
    "examination": "Examination",
    "coursework": "Coursework",
    "practical": "Practical",
    "homework": "Homework",
    "quiz": "Quiz",
}
REMARK = {"A1": "Excellent", "B2": "Very good", "B3": "Good", "C4": "Credit", "C5": "Credit", "C6": "Credit",
          "D7": "Pass", "E8": "Pass", "F9": "Fail"}  # fmt: skip


def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def positions(totals: dict[Any, float]) -> dict[Any, int]:
    """Competition ranking: equal totals share a position and the next position is skipped (1, 2, 2, 4)."""
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    out: dict[Any, int] = {}
    for i, (key, value) in enumerate(ranked):
        out[key] = out[ranked[i - 1][0]] if i and value == ranked[i - 1][1] else i + 1
    return out


def terms(cls: ClassGroup) -> list[AcademicPeriod]:
    return list(AcademicPeriod.objects.filter(parent_id=cls.period_id, kind="term").order_by("starts_on"))


def current_term(cls: ClassGroup, on: dt.date | None = None) -> AcademicPeriod | None:
    """The term running on the day (the last one started before it, else the first)."""
    on = on or dt.date.today()
    all_ = terms(cls)
    started = [t for t in all_ if t.starts_on <= on]
    return started[-1] if started else (all_[0] if all_ else None)


def _in_term(qs: Any, term: AcademicPeriod | None) -> Any:
    return qs.filter(assessed_on__gte=term.starts_on, assessed_on__lte=term.ends_on) if term is not None else qs


def _plan(class_id: uuid.UUID, subject_id: uuid.UUID) -> tuple[ClassGroup, ClassSubjectPlan, Subject]:
    cls: ClassGroup | None = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    if cls is None:
        raise NotFound("class", class_id)
    today = dt.date.today()
    plan = (
        ClassSubjectPlan.objects.filter(class_group_id=cls.id, subject_id=subject_id, valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .first()
    )
    subject = Subject.objects.filter(pk=subject_id).first()
    if plan is None or subject is None:
        raise NotFound("class subject", subject_id)
    return cls, plan, subject


def _members(cls: ClassGroup) -> list[Any]:
    from syntegra.learners.models import Learner

    today = dt.date.today()
    ids = list(
        ClassMembership.objects.filter(class_group_id=cls.id, valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .values_list("learner_id", flat=True)
    )
    return sorted(Learner.objects.filter(id__in=ids), key=lambda x: (x.legal_family_name, x.legal_given_name))


def may_enter(plan: ClassSubjectPlan, ctx: context.Context | None = None) -> bool:
    """The class-subject's current teacher (of record or co-teacher), or someone who manages classes."""
    from syntegra.curriculum.lessons import my_staff_id

    ctx = ctx or context.require()
    if not ctx.has("assessment:enter"):
        return False
    if ctx.has("class:manage"):
        return True
    mine = my_staff_id(ctx)
    today = dt.date.today()
    return (
        mine is not None
        and TeachingAssignment.objects.filter(class_subject_plan_id=plan.id, staff_id=mine, valid_from__lte=today)
        .exclude(valid_to__lte=today)
        .exists()
    )


def sheet(class_id: uuid.UUID, subject_id: uuid.UUID, term_id: uuid.UUID | None = None) -> dict[str, Any]:
    """The marksheet of one class and subject for a term (the current one unless another is asked for)."""
    ctx = context.require()
    authz.require("assessment:view", ctx)
    cls, plan, subject = _plan(class_id, subject_id)
    all_terms = terms(cls)
    term = next((t for t in all_terms if t.id == term_id), None) or current_term(cls)
    learners = _members(cls)
    columns = list(
        _in_term(Assessment.objects.filter(class_subject_plan_id=plan.id), term).order_by("assessed_on", "created_at")
    )
    results = {
        (r.assessment_id, r.learner_id): r
        for r in AssessmentResult.objects.filter(assessment_id__in=[a.id for a in columns])
    }
    weight = sum((a.weight for a in columns), Decimal(0))
    rows = []
    totals: dict[uuid.UUID, float] = {}
    for lr in learners:
        cells = []
        total = 0.0
        for a in columns:
            r = results.get((a.id, lr.id))
            score = r.score if r is not None else None
            cells.append({"assessment_id": a.id, "score": score, "missing": bool(r and r.is_missing_work)})
            if score is not None:
                total += float(score / a.max_mark * a.weight)
        if any(c["score"] is not None for c in cells):
            totals[lr.id] = round(total, 1)
        rows.append({"learner_id": lr.id, "name": f"{lr.legal_family_name}, {lr.legal_given_name}", "cells": cells})
    pos = positions(totals)
    out_of = float(weight) or 100.0
    for row in rows:
        t = totals.get(row["learner_id"])
        row["total"] = t
        row["percent"] = round(t / out_of * 100, 1) if t is not None else None
        row["grade"] = services.grade(row["percent"]) if row["percent"] is not None else None
        row["remark"] = REMARK.get(row["grade"] or "", "")
        row["position"] = ordinal(pos[row["learner_id"]]) if row["learner_id"] in pos else None

    def stats(values: list[float]) -> dict[str, float | None]:
        return {
            "average": round(sum(values) / len(values), 1) if values else None,
            "highest": max(values) if values else None,
            "lowest": min(values) if values else None,
        }

    cols = []
    for i, a in enumerate(columns):
        scores = [float(r["cells"][i]["score"]) for r in rows if r["cells"][i]["score"] is not None]
        cols.append(
            {
                "id": a.id,
                "title": a.title,
                "kind": KINDS.get(a.assessment_kind, a.assessment_kind.replace("_", " ").capitalize()),
                "max_mark": a.max_mark,
                "weight": a.weight,
                "on": a.assessed_on,
                "locked": a.status == "locked",
                "entered": len(scores),
                **stats(scores),
            }
        )
    can = may_enter(plan, ctx)
    return {
        "class": {"id": cls.id, "name": cls.name, "level": cls.education_level},
        "subject": {"id": subject.id, "name": subject.name},
        "plan_id": plan.id,
        "term": {"id": term.id, "name": term.name, "starts_on": term.starts_on, "ends_on": term.ends_on}
        if term
        else None,
        "terms": [{"id": t.id, "name": t.name} for t in all_terms],
        "columns": cols,
        "rows": rows,
        "weight": weight,
        "weight_left": Decimal(100) - weight,
        "totals": stats(list(totals.values())),
        "can_enter": can,
        "can_lock": ctx.has("assessment:approve"),
        "kinds": KINDS,
        "subjects": [
            {"id": s.id, "name": s.name}
            for s in Subject.objects.filter(
                id__in=list(ClassSubjectPlan.objects.filter(class_group_id=cls.id).values_list("subject_id", flat=True))
            ).order_by("name")
        ],
    }


def add_assessment(
    class_id: uuid.UUID,
    subject_id: uuid.UUID,
    title: str,
    kind: str,
    max_mark: Decimal,
    weight: Decimal,
    assessed_on: dt.date | None,
) -> Assessment:
    cls, plan, _subject = _plan(class_id, subject_id)
    if not may_enter(plan):
        raise Forbidden("Only the teacher of this class-subject can add assessments to its marksheet.")
    if kind not in KINDS:
        raise HardValidation("ASM-KIND", "Choose the kind of assessment", ", ".join(KINDS.values()))
    if len((title or "").strip()) < 3:
        raise HardValidation("ASM-TITLE", "Give the assessment a title", "e.g. Second continuous assessment test")
    on = assessed_on or dt.date.today()
    all_terms = terms(cls)
    term = next((t for t in all_terms if t.starts_on <= on <= t.ends_on), None)
    if all_terms and term is None:
        raise HardValidation("ASM-DATE", "The date is outside the school terms", "Choose a date within a term.")
    used = sum((a.weight for a in _in_term(Assessment.objects.filter(class_subject_plan_id=plan.id), term)), Decimal(0))
    if used + Decimal(weight) > 100:
        raise HardValidation(
            "ASM-WEIGHT",
            "The weights would add up to more than 100",
            f"{100 - used} is left for this class-subject in {term.name if term else 'the term'}.",
        )
    return services.create_assessment(plan.id, title.strip(), kind, max_mark=max_mark, weight=weight, assessed_on=on)


def save_marks(assessment_id: uuid.UUID, marks: dict[uuid.UUID, str], *, lock: bool = False) -> dict[str, Any]:
    """Save the marks typed into one column. A blank box records work not done; only the class's learners count."""
    a: Assessment | None = Assessment.objects.filter(pk=assessment_id).first()
    if a is None or a.class_subject_plan_id is None:
        raise NotFound("assessment", assessment_id)
    plan = ClassSubjectPlan.objects.get(pk=a.class_subject_plan_id)
    cls = ClassGroup.objects.in_scope().filter(pk=plan.class_group_id).first()
    if cls is None:
        raise NotFound("class", plan.class_group_id)
    if not may_enter(plan):
        raise Forbidden("Only the teacher of this class-subject can enter its marks.")
    members = {lr.id for lr in _members(cls)}
    batch: list[tuple[uuid.UUID, float | Decimal | None]] = []
    errors = []
    for lid, raw in marks.items():
        if lid not in members:
            continue
        text = (raw or "").strip()
        if not text:
            batch.append((lid, None))
            continue
        try:
            batch.append((lid, Decimal(text)))
        except ArithmeticError:
            errors.append({"field": str(lid), "message": "not a number"})
    if errors:
        raise HardValidation("ASM-MARK", "Some marks are not numbers", errors=errors)
    if lock and not context.require().has("assessment:approve"):
        raise Forbidden("Only the head can lock marks.")
    return services.record_results(a.id, batch, lock=lock)


def lock(assessment_id: uuid.UUID) -> Assessment:
    return services.lock(assessment_id)
