"""Security agencies' education and training (CR-004, FR-STI-01..08).

Reads are scoped by the caller's grant: a grant at an agency's node sees that agency's structure, institutions and
courses; a grant at a command sees the institutions under it; a grant at the registry root sees every agency.
Writes — intakes, trainees and outcomes — are recorded at the institution and emit events. Trainee records are
restricted; nothing operational is held (see ``reference``).
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from django.db import IntegrityError, transaction

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.institutions.models import Institution
from syntegra.learners.models import Enrolment, Learner
from syntegra.security_training.models import (
    AgencyRank,
    AgencyUnit,
    SecurityAgency,
    SecurityCourse,
    SecurityCourseIntake,
    SecurityCourseModule,
    SecurityInstitution,
    TraineeRecord,
)


def _rank_agencies(agency_id: uuid.UUID) -> list[uuid.UUID]:
    """Agencies whose ranks apply: the agency's own, or every armed service for tri-service (DHQ) institutions."""
    a = SecurityAgency.objects.get(pk=agency_id)
    if a.code == "DHQ":
        return list(SecurityAgency.objects.filter(category="armed_forces").values_list("id", flat=True))
    return [a.id]


FINAL_OUTCOMES = ("passed", "passed_out", "commissioned", "failed", "relegated", "withdrawn", "discharged")


def _row(obj: Any, *fields: str) -> dict[str, Any]:
    return {f: getattr(obj, f) for f in ("id", *fields)}


def _visible_agencies() -> list[SecurityAgency]:
    """Agencies whose own node is in scope, plus agencies owning a visible institution (command-level grants)."""
    ids = set(SecurityAgency.objects.in_scope().values_list("id", flat=True))
    ids |= set(SecurityInstitution.objects.in_scope().values_list("agency_id", flat=True))
    return list(SecurityAgency.objects.filter(id__in=ids).order_by("category", "name"))


# --------------------------------------------------------------------------- reads
def directory() -> list[dict[str, Any]]:
    """STI-01: every visible agency with its institutions (and how many units its structure has)."""
    authz.require("security_training:view")
    agencies = _visible_agencies()
    profiles = list(SecurityInstitution.objects.in_scope().filter(agency_id__in=[a.id for a in agencies]))
    insts = {i.id: i for i in Institution.objects.filter(id__in=[p.institution_id for p in profiles])}
    units = {u.id: u for u in AgencyUnit.objects.filter(id__in=[p.unit_id for p in profiles])}
    counts: dict[uuid.UUID, int] = {}
    for agency_id in AgencyUnit.objects.filter(agency_id__in=[a.id for a in agencies]).values_list(
        "agency_id", flat=True
    ):
        counts[agency_id] = counts.get(agency_id, 0) + 1
    courses: dict[uuid.UUID, int] = {}
    for iid in SecurityCourse.objects.filter(institution_id__in=list(insts), status="published").values_list(
        "institution_id", flat=True
    ):
        courses[iid] = courses.get(iid, 0) + 1
    out = []
    for a in agencies:
        rows = [
            {
                "institution_id": p.institution_id,
                "name": insts[p.institution_id].name,
                "short_name": insts[p.institution_id].short_name,
                "town": (insts[p.institution_id].address or {}).get("town"),
                "state": (insts[p.institution_id].address or {}).get("state"),
                "institution_type": p.institution_type,
                "unit": units[p.unit_id].name,
                "access_regime": p.access_regime,
                "courses": courses.get(p.institution_id, 0),
                "data_status": p.data_status,
            }
            for p in profiles
            if p.agency_id == a.id and p.institution_id in insts
        ]
        out.append(
            {
                **_row(a, "code", "name", "category", "supervising_ministry", "establishing_law", "data_status"),
                "units": counts.get(a.id, 0),
                "institutions": sorted(rows, key=lambda r: r["name"]),
            }
        )
    return out


def agency(agency_id: uuid.UUID) -> dict[str, Any]:
    """The agency's own structure as a tree, its ranks and its institutions."""
    authz.require("security_training:view")
    a = next((x for x in _visible_agencies() if x.id == agency_id), None)
    if a is None:
        raise NotFound("security agency", agency_id)
    units = list(AgencyUnit.objects.filter(agency_id=a.id).order_by("name"))
    children: dict[uuid.UUID | None, list[AgencyUnit]] = {}
    for u in units:
        children.setdefault(u.parent_unit_id, []).append(u)

    def tree(parent: uuid.UUID | None) -> list[dict[str, Any]]:
        return [
            {
                **_row(u, "code", "name", "unit_type", "headquarters_state", "headquarters_town", "data_status"),
                "children": tree(u.id),
            }
            for u in sorted(children.get(parent, []), key=lambda x: (x.unit_type == "state_command", x.name))
        ]

    ranks = [
        _row(r, "code", "title", "abbreviation", "rank_category", "seniority", "data_status")
        for r in AgencyRank.objects.filter(agency_id=a.id).order_by("-seniority")
    ]
    insts = [i for d in directory() if d["id"] == a.id for i in d["institutions"]]
    return {
        **_row(a, "code", "name", "category", "supervising_ministry", "establishing_law", "data_status"),
        "structure": tree(None),
        "ranks": ranks,
        "institutions": insts,
    }


def _profile(institution_id: uuid.UUID) -> SecurityInstitution:
    p: SecurityInstitution | None = SecurityInstitution.objects.in_scope().filter(institution_id=institution_id).first()
    if p is None:
        raise NotFound("training institution", institution_id)
    return p


def institution(institution_id: uuid.UUID) -> dict[str, Any]:
    """STI-02: institution profile and its own course catalogue."""
    authz.require("security_training:view")
    p = _profile(institution_id)
    inst = Institution.objects.get(pk=institution_id)
    a = SecurityAgency.objects.get(pk=p.agency_id)
    unit = AgencyUnit.objects.get(pk=p.unit_id)
    courses = [
        _row(
            c,
            "code",
            "title",
            "category",
            "award",
            "award_title",
            "accrediting_body",
            "duration_weeks",
            "content_held",
            "data_status",
            "status",
            "version",
        )
        for c in SecurityCourse.objects.filter(institution_id=institution_id).order_by("category", "title")
    ]
    return {
        "institution_id": inst.id,
        "name": inst.name,
        "short_name": inst.short_name,
        "institution_code": inst.institution_code,
        "address": inst.address,
        "category": inst.category,
        "agency": _row(a, "code", "name"),
        "unit": _row(unit, "code", "name", "unit_type"),
        **_row(
            p,
            "institution_type",
            "access_regime",
            "accreditation",
            "commandant_title",
            "established_year",
            "data_status",
        ),
        "courses": courses,
    }


def _course(course_id: uuid.UUID) -> SecurityCourse:
    c: SecurityCourse | None = SecurityCourse.objects.in_scope().filter(pk=course_id).first()
    if c is None:
        raise NotFound("training course", course_id)
    return c


def course(course_id: uuid.UUID) -> dict[str, Any]:
    """STI-03: one course's curriculum — modules (syllabus headings) and intakes."""
    authz.require("security_training:view")
    c = _course(course_id)
    inst = Institution.objects.get(pk=c.institution_id)
    ranks: dict[str, str] = {}
    for r in AgencyRank.objects.filter(agency_id__in=_rank_agencies(c.agency_id)).order_by("code"):
        ranks.setdefault(r.code, r.title)
    modules = (
        [
            _row(m, "sequence", "code", "title", "area", "contact_hours", "assessment", "is_mandatory")
            for m in SecurityCourseModule.objects.filter(course_id=c.id).order_by("sequence")
        ]
        if c.content_held
        else []
    )
    intakes = [
        {
            **_row(i, "intake_code", "name", "starts_on", "ends_on", "capacity", "status"),
            "trainees": TraineeRecord.objects.filter(intake_id=i.id).count(),
        }
        for i in SecurityCourseIntake.objects.filter(course_id=c.id).order_by("-starts_on")
    ]
    return {
        **_row(
            c,
            "code",
            "title",
            "category",
            "award",
            "award_title",
            "accrediting_body",
            "duration_weeks",
            "entry_requirements",
            "description",
            "version",
            "content_held",
            "data_status",
            "status",
        ),
        "institution": {"institution_id": inst.id, "name": inst.name},
        "target_ranks": [{"code": r, "title": ranks.get(r, r)} for r in (c.target_ranks or [])],
        "modules": modules,
        "intakes": intakes,
    }


def intake(intake_id: uuid.UUID) -> dict[str, Any]:
    """STI-04: trainees of an intake (restricted)."""
    authz.require("security_training:view")
    i = SecurityCourseIntake.objects.in_scope().filter(pk=intake_id).first()
    if i is None:
        raise NotFound("course intake", intake_id)
    records = list(TraineeRecord.objects.filter(intake_id=i.id))
    learners = {lr.id: lr for lr in Learner.objects.filter(id__in=[r.learner_id for r in records])}
    ranks = {
        r.id: r.title
        for r in AgencyRank.objects.filter(id__in=[r.rank_at_entry_id for r in records if r.rank_at_entry_id])
    }
    rows = []
    for r in records:
        lr = learners.get(r.learner_id)
        rows.append(
            {
                **_row(r, "outcome", "result", "outcome_on"),
                "learner_id": r.learner_id,
                "name": f"{lr.legal_given_name} {lr.legal_family_name}" if lr else "?",
                "global_learner_id": lr.global_learner_id if lr else None,
                "rank_at_entry": ranks.get(r.rank_at_entry_id) if r.rank_at_entry_id else None,
            }
        )
    return {
        **_row(i, "intake_code", "name", "starts_on", "ends_on", "capacity", "status"),
        "course": course(i.course_id),
        "trainees": sorted(rows, key=lambda x: x["name"]),
    }


# --------------------------------------------------------------------------- writes
def create_intake(
    course_id: uuid.UUID,
    *,
    intake_code: str,
    name: str,
    starts_on: dt.date,
    ends_on: dt.date | None = None,
    capacity: int | None = None,
) -> SecurityCourseIntake:
    c = _course(course_id)
    if ends_on and ends_on < starts_on:
        raise HardValidation("STI-INTAKE-DATES", "The intake ends before it starts", "")
    with uow.command(
        "registry", "security_training:intake", action="create", record_kind="security_course_intake"
    ) as cmd:
        try:
            with transaction.atomic(using=cmd.alias):
                return cmd.add(
                    SecurityCourseIntake(
                        scope_node_id=c.scope_node_id,
                        course_id=c.id,
                        intake_code=intake_code.upper(),
                        name=name,
                        starts_on=starts_on,
                        ends_on=ends_on,
                        capacity=capacity,
                        status="planned" if starts_on > dt.date.today() else "in_progress",
                    )
                )
        except IntegrityError as exc:
            raise ConflictError("STI-INTAKE-EXISTS", "Intake code already used for this course", intake_code) from exc


def add_trainee(intake_id: uuid.UUID, learner_id: uuid.UUID, *, rank_code: str | None = None) -> TraineeRecord:
    """Put a learner on an intake. The learner must be enrolled at the institution (single registration path)."""
    i = SecurityCourseIntake.objects.in_scope().filter(pk=intake_id).first()
    if i is None:
        raise NotFound("course intake", intake_id)
    c = SecurityCourse.objects.get(pk=i.course_id)
    enr = Enrolment.objects.filter(learner_id=learner_id, institution_id=c.institution_id, status="active").first()
    if enr is None:
        raise HardValidation("STI-NOT-ENROLLED", "Register the trainee at the institution first", "")
    rank = None
    if rank_code:
        rank = AgencyRank.objects.filter(agency_id__in=_rank_agencies(c.agency_id), code=rank_code.upper()).first()
        if rank is None:
            raise HardValidation("STI-RANK", "Unknown rank for this agency", rank_code)
    if i.capacity and TraineeRecord.objects.filter(intake_id=i.id).count() >= i.capacity:
        raise ConflictError("STI-INTAKE-FULL", "The intake is full", f"Capacity {i.capacity}.")
    with uow.command("registry", "security_training:record", action="add", record_kind="trainee_record") as cmd:
        try:
            with transaction.atomic(using=cmd.alias):
                return cmd.add(
                    TraineeRecord(
                        scope_node_id=i.scope_node_id,
                        learner_id=learner_id,
                        intake_id=i.id,
                        enrolment_id=enr.id,
                        rank_at_entry_id=rank.id if rank else None,
                        outcome="in_training",
                    )
                )
        except IntegrityError as exc:
            raise ConflictError("STI-TRAINEE-EXISTS", "Already on this intake", "") from exc


def record_outcome(
    record_id: uuid.UUID,
    outcome: str,
    *,
    result: str | None = None,
    reason: str | None = None,
    on: dt.date | None = None,
) -> TraineeRecord:
    """Record a final outcome — passed out, commissioned, failed, relegated, withdrawn — by a person."""
    ctx = context.require()
    if outcome not in FINAL_OUTCOMES:
        raise HardValidation("STI-OUTCOME", "Choose a final outcome", ", ".join(FINAL_OUTCOMES))
    if outcome in ("failed", "relegated", "withdrawn", "discharged") and len((reason or "").strip()) < 10:
        raise HardValidation("STI-OUTCOME-REASON", "Give the reason (at least 10 characters)", "")
    with uow.command(
        "registry", "security_training:record", action=outcome, record_kind="trainee_record", reason=reason
    ) as cmd:
        r = cmd.lock(TraineeRecord, record_id)
        if r.outcome in FINAL_OUTCOMES:
            raise ConflictError("STI-OUTCOME-RECORDED", "An outcome is already recorded", r.outcome)
        cmd.update(
            r,
            outcome=outcome,
            result=result,
            outcome_reason=reason,
            outcome_on=on or dt.date.today(),
            recorded_by_id=ctx.actor_id if ctx.actor_kind == "user" else None,
        )
        cmd.emit(
            "STI.TRAINEE_OUTCOME_RECORDED",
            aggregate_id=r.id,
            scope_node_id=r.scope_node_id,
            payload={"trainee_record_id": r.id, "outcome": outcome},
        )
        if outcome in ("passed_out", "commissioned", "withdrawn", "discharged", "failed"):
            enr = Enrolment.unscoped.using(cmd.alias).filter(pk=r.enrolment_id, status="active").first()
            if enr is not None:  # the course is over: close the institution enrolment
                cmd.update(
                    enr,
                    status="completed" if outcome in ("passed_out", "commissioned") else "withdrawn",
                    end_on=on or dt.date.today(),
                )
        return r


def learner_courses(learner_id: uuid.UUID) -> list[dict[str, Any]]:
    """Security courses on a learner's lifelong record (Learner 360)."""
    rows = []
    for r in TraineeRecord.objects.in_scope().filter(learner_id=learner_id):
        i = SecurityCourseIntake.objects.get(pk=r.intake_id)
        c = SecurityCourse.objects.get(pk=i.course_id)
        rows.append(
            {
                "course": c.title,
                "intake": i.name,
                "outcome": r.outcome,
                "result": r.result,
                "outcome_on": r.outcome_on,
                "starts_on": i.starts_on,
            }
        )
    return sorted(rows, key=lambda x: x["starts_on"], reverse=True)


__all__ = [
    "FINAL_OUTCOMES",
    "add_trainee",
    "agency",
    "course",
    "create_intake",
    "directory",
    "institution",
    "intake",
    "learner_courses",
    "record_outcome",
]
