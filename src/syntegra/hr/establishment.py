"""Establishment, salary structures, cadres, appointments and promotions (FR-HRM-01/02/03/07)."""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any

from django.db import IntegrityError, transaction

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.hr.domain import employment as rules
from syntegra.hr.models import Cadre, EmploymentRecord, Position, PromotionCase, SalaryScalePoint, SalaryStructure
from syntegra.institutions.models import Institution
from syntegra.people.models import Staff, StaffPost

ACTIVE = ("probation", "confirmed", "suspended", "seconded")


# --------------------------------------------------------------------------- structures and cadres
def create_salary_structure(
    scope_node_id: uuid.UUID,
    code: str,
    title: str,
    points: list[tuple[int, int, int, dict[str, Any]]],
    *,
    effective_from: dt.date,
    currency: str = "NGN",
    approval_instrument: str | None = None,
) -> SalaryStructure:
    """``points`` = (grade_level, step, annual_basic_minor, allowances)."""
    with uow.command("registry", "hr:configure", action="publish", record_kind="salary_structure") as cmd:
        version = SalaryStructure.objects.filter(scope_node_id=scope_node_id, code=code).count() + 1
        st = cmd.add(
            SalaryStructure(
                scope_node_id=scope_node_id,
                code=code,
                title=title,
                currency=currency,
                effective_from=effective_from,
                version=version,
                approval_instrument=approval_instrument,
                status="published",
            )
        )
        for gl, step, basic, allowances in points:
            cmd.add(
                SalaryScalePoint(
                    structure_id=st.id,
                    grade_level=gl,
                    step=step,
                    annual_basic_minor=basic,
                    currency=currency,
                    allowances=allowances,
                )
            )
        cmd.record_id = st.id
        return st


def current_structure(code: str) -> SalaryStructure:
    st: SalaryStructure | None = (
        SalaryStructure.objects.filter(code=code, status="published", effective_from__lte=dt.date.today())
        .order_by("-version")
        .first()
    )
    if st is None:
        raise NotFound("salary structure", code)
    return st


def scale_point(structure_id: uuid.UUID, grade_level: int, step: int) -> SalaryScalePoint:
    p: SalaryScalePoint | None = SalaryScalePoint.objects.filter(
        structure_id=structure_id, grade_level=grade_level, step=step
    ).first()
    if p is None:
        raise HardValidation(
            "HR-SCALE-POINT", "Grade level and step not on the salary structure", f"GL {grade_level} step {step}"
        )
    return p


def create_cadre(
    scope_node_id: uuid.UUID,
    code: str,
    title: str,
    *,
    staff_category: str,
    is_teaching: bool,
    salary_structure_code: str,
    entry_grade_level: int,
    max_grade_level: int,
    retirement_age: int,
    max_years_service: int,
    years_per_promotion: int = 3,
) -> Cadre:
    with uow.command("registry", "hr:configure", action="create", record_kind="cadre") as cmd:
        return cmd.add(
            Cadre(
                scope_node_id=scope_node_id,
                code=code,
                title=title,
                staff_category=staff_category,
                is_teaching=is_teaching,
                salary_structure_code=salary_structure_code,
                entry_grade_level=entry_grade_level,
                max_grade_level=max_grade_level,
                years_per_promotion=years_per_promotion,
                retirement_age=retirement_age,
                max_years_service=max_years_service,
                status="active",
            )
        )


def cadre(code: str) -> Cadre:
    c: Cadre | None = Cadre.objects.filter(code=code, status="active").first()
    if c is None:
        raise NotFound("cadre", code)
    return c


# --------------------------------------------------------------------------- establishment
@dataclass
class NewPosition:
    title: str
    cadre_code: str
    employer_scope_id: uuid.UUID
    grade_level_min: int
    grade_level_max: int
    institution_id: uuid.UUID | None = None
    subject_id: uuid.UUID | None = None
    education_levels: list[str] | None = None
    funding: str = "funded"
    budget_line: str | None = None


def create_position(p: NewPosition) -> Position:
    ctx = context.require()
    authz.require("hr:establishment", ctx)
    c = cadre(p.cadre_code)
    if not (c.entry_grade_level <= p.grade_level_min <= p.grade_level_max <= c.max_grade_level):
        raise HardValidation(
            "HR-GRADE-BAND",
            "Grade band outside the cadre",
            f"{c.code} runs GL {c.entry_grade_level}–{c.max_grade_level}.",
        )
    scope = p.employer_scope_id
    prefix = "STATE"
    if p.institution_id:
        inst = Institution.objects.filter(pk=p.institution_id).first()
        if inst is None:
            raise NotFound("institution", p.institution_id)
        scope, prefix = inst.scope_node_id, inst.institution_code.replace("INS-", "")
    with uow.command("registry", None, action="create", record_kind="position") as cmd:
        n = Position.objects.filter(position_code__startswith=f"POS-{prefix}-").count() + 1
        pos = cmd.add(
            Position(
                scope_node_id=scope,
                position_code=f"POS-{prefix}-{n:04d}",
                institution_id=p.institution_id,
                employer_scope_id=p.employer_scope_id,
                title=p.title,
                cadre_id=c.id,
                staff_category=c.staff_category,
                grade_level_min=p.grade_level_min,
                grade_level_max=p.grade_level_max,
                subject_id=p.subject_id,
                education_levels=p.education_levels,
                funding=p.funding,
                budget_line=p.budget_line,
                status="approved",
            )
        )
        cmd.emit(
            "HR.POSITION_CHANGED",
            aggregate_id=pos.id,
            scope_node_id=scope,
            payload={"position_id": pos.id, "status": "approved"},
        )
        return pos


def establishment(institution_id: uuid.UUID) -> dict[str, Any]:
    """Positions with holders, vacancies by subject and over-establishment for one institution (HRM-01)."""
    authz.require("hr:view")
    positions = list(Position.objects.in_scope().filter(institution_id=institution_id).exclude(status="abolished"))
    filled = {
        r.position_id: r
        for r in EmploymentRecord.objects.filter(position_id__in=[p.id for p in positions], status__in=ACTIVE)
    }
    unplaced = (
        StaffPost.objects.filter(institution_id=institution_id, valid_to__isnull=True)
        .exclude(
            id__in=EmploymentRecord.objects.filter(position_id__isnull=False, status__in=ACTIVE).values("staff_post_id")
        )
        .count()
    )
    vac_by_subject: dict[str, int] = {}
    rows = []
    for p in positions:
        holder = filled.get(p.id)
        rows.append(
            {
                "position_id": p.id,
                "position_code": p.position_code,
                "title": p.title,
                "status": p.status,
                "funding": p.funding,
                "subject_id": p.subject_id,
                "holder_staff_id": holder.staff_id if holder else None,
            }
        )
        if holder is None and p.status == "approved" and p.funding != "unfunded":
            key = str(p.subject_id) if p.subject_id else "general"
            vac_by_subject[key] = vac_by_subject.get(key, 0) + 1
    approved = sum(1 for p in positions if p.status == "approved")
    return {
        "institution_id": institution_id,
        "approved": approved,
        "filled": len(filled),
        "vacant": approved - len(filled),
        "fill_rate": round(len(filled) / approved, 4) if approved else None,
        "vacancies_by_subject": vac_by_subject,
        "posts_without_position": unplaced,
        "positions": rows,
    }


# --------------------------------------------------------------------------- appointment
@dataclass
class Appointment:
    staff_id: uuid.UUID
    position_id: uuid.UUID
    appointment_type: str
    first_appointment_on: dt.date
    grade_level: int
    step: int = 1
    present_appointment_on: dt.date | None = None
    contract: str = "permanent"
    appointment_letter_ref: str | None = None
    confirmed_on: dt.date | None = None


def appoint(a: Appointment) -> EmploymentRecord:
    """Fill an approved, vacant position: create the staff post and its employment record (FR-HRM-03)."""
    ctx = context.require()
    authz.require("hr:appoint", ctx)
    pos = Position.objects.filter(pk=a.position_id).first()
    staff = Staff.objects.filter(pk=a.staff_id).first()
    if pos is None or staff is None:
        raise NotFound("position or staff member")
    if pos.status != "approved":
        raise ConflictError("HR-POSITION-STATUS", "Position is not open", f"The position is {pos.status}.")
    if not pos.grade_level_min <= a.grade_level <= pos.grade_level_max:
        raise HardValidation(
            "HR-GRADE-POSITION",
            "Grade outside the position's band",
            f"{pos.position_code} is GL {pos.grade_level_min}–{pos.grade_level_max}.",
        )
    c = Cadre.objects.get(pk=pos.cadre_id)
    st = current_structure(c.salary_structure_code)
    scale_point(st.id, a.grade_level, a.step)
    present = a.present_appointment_on or a.first_appointment_on
    retire_on, basis = rules.retirement_due(
        staff.date_of_birth, a.first_appointment_on, c.retirement_age, c.max_years_service
    )
    if retire_on <= dt.date.today():
        raise HardValidation(
            "HR-PAST-RETIREMENT",
            "Past statutory retirement",
            f"Statutory retirement fell on {retire_on} ({basis.replace('_', ' ')}).",
        )
    inst_id = pos.institution_id
    with uow.command("registry", None, action="appoint", record_kind="employment_record") as cmd:
        post = cmd.add(
            StaffPost(
                scope_node_id=pos.scope_node_id,
                staff_id=staff.id,
                institution_id=inst_id,
                job_title=pos.title,
                staff_category=pos.staff_category,
                grade_step=f"GL{a.grade_level:02d}/{a.step:02d}",
                contract=a.contract,
                fte=1,
                employer_scope_id=pos.employer_scope_id,
                valid_from=present,
            )
        )
        rec = EmploymentRecord(
            scope_node_id=pos.scope_node_id,
            staff_post_id=post.id,
            staff_id=staff.id,
            position_id=pos.id,
            cadre_id=c.id,
            employer_scope_id=pos.employer_scope_id,
            appointment_type=a.appointment_type,
            appointment_letter_ref=a.appointment_letter_ref,
            first_appointment_on=a.first_appointment_on,
            present_appointment_on=present,
            confirmation_due_on=rules.confirmation_due(present),
            confirmed_on=a.confirmed_on,
            salary_structure_id=st.id,
            grade_level=a.grade_level,
            step=a.step,
            retirement_due_on=retire_on,
            retirement_basis=basis,
            status="confirmed" if a.confirmed_on else "probation",
        )
        try:
            with transaction.atomic(using=cmd.alias):
                cmd.add(rec)
        except IntegrityError as exc:
            if "seat_key" in str(exc):
                raise ConflictError(
                    "HR-POSITION-FILLED", "Position already filled", f"{pos.position_code} has an active holder."
                ) from exc
            raise
        if staff.status == "onboarding":
            cmd.update(staff, status="active")
        cmd.record_id = rec.id
        return rec


def active_record(staff_id: uuid.UUID) -> EmploymentRecord:
    r: EmploymentRecord | None = (
        EmploymentRecord.objects.filter(staff_id=staff_id, status__in=ACTIVE)
        .order_by("-present_appointment_on")
        .first()
    )
    if r is None:
        raise NotFound("active employment record", staff_id)
    return r


# --------------------------------------------------------------------------- promotion
def open_promotion(
    staff_id: uuid.UUID, exercise_label: str, *, exam_score: float | None = None, last_rating: str | None = None
) -> PromotionCase:
    from syntegra.hr.models import EmployeeRelationsCase

    authz.require("hr:promote")
    rec = active_record(staff_id)
    c = Cadre.objects.get(pk=rec.cadre_id)
    open_case = EmployeeRelationsCase.objects.filter(
        staff_id=staff_id, case_kind__in=("query", "disciplinary"), status__in=("open", "in_progress", "on_hold")
    ).exists()
    checks = rules.promotion_eligibility(
        on=dt.date.today(),
        grade_level=rec.grade_level,
        max_grade_level=c.max_grade_level,
        last_promotion_on=rec.last_promotion_on,
        present_appointment_on=rec.present_appointment_on,
        years_per_promotion=c.years_per_promotion,
        open_disciplinary=open_case,
        confirmed=rec.status == "confirmed",
        last_rating=last_rating,
    )
    with uow.command("registry", None, action="open", record_kind="promotion_case") as cmd:
        return cmd.add(
            PromotionCase(
                scope_node_id=rec.scope_node_id,
                staff_id=staff_id,
                employment_record_id=rec.id,
                exercise_label=exercise_label,
                from_grade_level=rec.grade_level,
                from_step=rec.step,
                to_grade_level=min(rec.grade_level + 1, c.max_grade_level)
                if rec.grade_level < c.max_grade_level
                else rec.grade_level,
                to_step=1 if rec.grade_level < c.max_grade_level else rec.step + 1,
                eligibility=[{"check": x.name, "passed": x.passed, "detail": x.detail} for x in checks],
                exam_score=exam_score,
                status="submitted",
            )
        )


def decide_promotion(
    case_id: uuid.UUID, decision: str, *, effective_on: dt.date | None = None, reason: str | None = None
) -> PromotionCase:
    """Board decision — human only. Approval moves the employment record to the new grade and step."""
    ctx = context.require()
    authz.require("hr:promote", ctx)
    if ctx.actor_kind != "user":
        raise Forbidden("Promotion decisions are made by people.", code="HUMAN-ONLY")
    with uow.command(
        "registry", None, action=f"promotion_{decision}", record_kind="promotion_case", reason=reason
    ) as cmd:
        case = cmd.lock(PromotionCase, case_id)
        if case.status != "submitted":
            raise ConflictError("HR-PROMOTION-DECIDED", "Already decided", f"The case is {case.status}.")
        if decision == "approved" and not all(x["passed"] for x in case.eligibility) and not reason:
            raise HardValidation(
                "HR-PROMOTION-INELIGIBLE",
                "Eligibility checks failed",
                "Approving an ineligible case needs a recorded reason.",
            )
        cmd.update(
            case,
            board_decision=decision,
            decided_by_id=ctx.actor_id,
            effective_on=effective_on or dt.date.today(),
            status="approved" if decision == "approved" else "rejected",
        )
        if decision == "approved":
            rec = cmd.lock(EmploymentRecord, case.employment_record_id)
            scale_point(rec.salary_structure_id, case.to_grade_level, case.to_step)
            cmd.update(rec, grade_level=case.to_grade_level, step=case.to_step, last_promotion_on=case.effective_on)
            post = cmd.lock(StaffPost, rec.staff_post_id)
            cmd.update(post, grade_step=f"GL{case.to_grade_level:02d}/{case.to_step:02d}")
        cmd.emit(
            "HR.PROMOTION_DECIDED",
            aggregate_id=case.id,
            payload={"promotion_case_id": case.id, "board_decision": decision},
        )
        return case
