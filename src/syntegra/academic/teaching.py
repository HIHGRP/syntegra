"""Class subject plan and teacher assignment (MFS ACA-101, FR-ACA-101, FR-CUR-106).

The head (or deputy) sees each class's subjects with the teacher of record, the periods a week and the curriculum
version, and the teaching chain is validated live: a mandatory subject with no teacher of record (G2) or with a
teacher who holds no verified teaching authorisation for the subject and level (G3) is flagged on the row. A teacher
is assigned from the school's own staff; assigning someone without the authorisation needs a written reason, which is
kept on the assignment. Replacing the teacher of record ends the current assignment and starts the new one in a
single change, so a class-subject never has two teachers of record or none in between. An assignment ended today is
no longer current (the hand-over takes effect at once) but still counts for today's lessons already taught.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.academic.models import ClassGroup, ClassSubjectPlan, Subject, TeachingAssignment
from syntegra.academic.services import _assignment_payload
from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.curriculum.domain import coverage

ROLES = {"teacher_of_record": "Teacher of record", "co_teacher": "Co-teacher"}
MIN_REASON = 10


def _class(class_id: uuid.UUID) -> ClassGroup:
    c: ClassGroup | None = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    if c is None:
        raise NotFound("class", class_id)
    return c


def _names(staff_ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    from syntegra.people.models import Staff

    return {s.id: f"{s.given_name} {s.family_name}" for s in Staff.objects.filter(id__in=staff_ids)}


def _authorised(staff_ids: set[uuid.UUID], on: dt.date) -> dict[uuid.UUID, list[tuple[uuid.UUID, list[str]]]]:
    """Verified, unexpired teaching authorisations per teacher: (subject, levels — empty means every level)."""
    from syntegra.people.models import StaffQualification

    out: dict[uuid.UUID, list[tuple[uuid.UUID, list[str]]]] = {s: [] for s in staff_ids}
    for q in StaffQualification.objects.filter(
        staff_id__in=staff_ids, kind="teaching_authorisation", verification="verified"
    ):
        if q.subject_id is None or (q.expires_on and q.expires_on < on):
            continue
        out[q.staff_id].append((q.subject_id, list(q.levels or [])))
    return out


def _covers(auth: list[tuple[uuid.UUID, list[str]]], subject_id: uuid.UUID, level: str) -> bool:
    return any(s == subject_id and (not levels or level in levels) for s, levels in auth)


def staff_of(institution_id: uuid.UUID, on: dt.date | None = None) -> list[Any]:
    """The school's teaching staff: active posts at the institution."""
    from syntegra.people.models import StaffPost

    on = on or dt.date.today()
    return list(
        StaffPost.objects.filter(institution_id=institution_id, valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .order_by("staff_id")
    )


def _active(qs: Any, on: dt.date) -> Any:
    return qs.filter(valid_from__lte=on).exclude(valid_to__lt=on)


def current(qs: Any, on: dt.date) -> Any:
    """Assignments in force now: an assignment ended today (``valid_to`` = today, its last day) no longer counts, so
    a hand-over takes effect at once; for any past day the end date is inclusive (``_active``)."""
    return qs.filter(valid_from__lte=on).exclude(valid_to__lte=on)


def class_plan(class_id: uuid.UUID, on: dt.date | None = None) -> dict[str, Any]:
    """ACA-101 read model: the class's subjects, who teaches each, live G2/G3 validation and the teachers' loads."""
    ctx = context.require()
    authz.require("class:view", ctx)
    on = on or dt.date.today()
    c = _class(class_id)
    from syntegra.academic.models import ClassMembership
    from syntegra.curriculum.models import CurriculumVersion
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=c.institution_id).first()
    plans = list(_active(ClassSubjectPlan.objects.filter(class_group_id=c.id), on))
    subjects = {s.id: s for s in Subject.objects.filter(id__in={p.subject_id for p in plans})}
    assignments = list(current(TeachingAssignment.objects.filter(class_subject_plan_id__in=[p.id for p in plans]), on))
    posts = staff_of(c.institution_id, on)
    staff_ids = {p.staff_id for p in posts} | {a.staff_id for a in assignments}
    names = _names(staff_ids)
    auth = _authorised(staff_ids, on)
    versions = {
        v.id: v
        for v in CurriculumVersion.objects.filter(
            id__in={p.curriculum_version_id for p in plans if p.curriculum_version_id}
        )
    }
    learners = _active(ClassMembership.objects.filter(class_group_id=c.id), on).count()
    rows = []
    for p in sorted(plans, key=lambda p: subjects[p.subject_id].name if p.subject_id in subjects else ""):
        mine = [a for a in assignments if a.class_subject_plan_id == p.id]
        tors = [a for a in mine if a.role == "teacher_of_record"]
        facts = coverage.ClassSubjectFacts(
            plan_id=p.id,
            class_id=c.id,
            subject_id=p.subject_id,
            level=c.education_level,
            learners=learners,
            is_mandatory=p.is_mandatory,
            teachers_of_record=[a.staff_id for a in tors],
            authorised={a.staff_id: _covers(auth.get(a.staff_id, []), p.subject_id, c.education_level) for a in tors},
        )
        breaches = coverage.evaluate(facts)

        def person(a: TeachingAssignment, p: ClassSubjectPlan = p) -> dict[str, Any]:
            return {
                "assignment_id": a.id,
                "staff_id": a.staff_id,
                "name": names.get(a.staff_id, "?"),
                "since": a.valid_from,
                "until": a.valid_to,
                "authorised": _covers(auth.get(a.staff_id, []), p.subject_id, c.education_level),
                "justification": a.justification,
            }

        v = versions.get(p.curriculum_version_id) if p.curriculum_version_id else None
        rows.append(
            {
                "plan_id": p.id,
                "subject": subjects[p.subject_id].name if p.subject_id in subjects else "?",
                "subject_id": p.subject_id,
                "periods": p.periods_per_week,
                "mandatory": p.is_mandatory,
                "curriculum": v.version_label if v else None,
                "teacher": person(tors[0]) if tors else None,
                "co_teachers": [person(a) for a in mine if a.role != "teacher_of_record"],
                "breaches": [{"rule": b.rule.upper(), "severity": b.severity, "detail": b.detail} for b in breaches],
            }
        )
    # each teacher's load across the whole school (teacher-of-record periods a week)
    loads: dict[uuid.UUID, int] = {}
    classes_of: dict[uuid.UUID, set[str]] = {}
    school_plans = {
        p.id: p
        for p in _active(
            ClassSubjectPlan.objects.filter(
                class_group_id__in=ClassGroup.objects.filter(institution_id=c.institution_id, status="active").values(
                    "id"
                )
            ),
            on,
        )
    }
    class_names = dict(ClassGroup.objects.filter(institution_id=c.institution_id).values_list("id", "name"))
    for a in current(
        TeachingAssignment.objects.filter(class_subject_plan_id__in=list(school_plans), role="teacher_of_record"), on
    ):
        p = school_plans[a.class_subject_plan_id]
        loads[a.staff_id] = loads.get(a.staff_id, 0) + int(a.weekly_periods or p.periods_per_week or 0)
        classes_of.setdefault(a.staff_id, set()).add(class_names.get(p.class_group_id, ""))
    all_subjects = dict(
        Subject.objects.filter(id__in={s for v in auth.values() for s, _l in v}).values_list("id", "name")
    )
    teachers = [
        {
            "staff_id": sp.staff_id,
            "name": names.get(sp.staff_id, "?"),
            "job_title": sp.job_title,
            "authorised": sorted({all_subjects.get(s, "?") for s, _l in auth.get(sp.staff_id, [])}),
            "load": loads.get(sp.staff_id, 0),
            "classes": len(classes_of.get(sp.staff_id, ())),
        }
        for sp in posts
    ]
    teachers.sort(key=lambda t: t["name"])
    siblings = list(
        ClassGroup.objects.filter(institution_id=c.institution_id, period_id=c.period_id, status="active")
        .order_by("name")
        .values("id", "name")
    )
    return {
        "class": {"id": c.id, "name": c.name, "level": c.education_level, "learners": learners},
        "institution": inst.name if inst else "",
        "classes": siblings,
        "rows": rows,
        "teachers": teachers,
        "totals": {
            "subjects": len(rows),
            "assigned": sum(1 for r in rows if r["teacher"]),
            "flagged": sum(1 for r in rows if r["breaches"]),
            "periods": sum(r["periods"] or 0 for r in rows),
        },
    }


def assign(
    plan_id: uuid.UUID,
    staff_id: uuid.UUID,
    *,
    role: str = "teacher_of_record",
    replace: bool = False,
    justification: str | None = None,
) -> TeachingAssignment:
    """Assign a teacher of the school to a class-subject. A teacher of record who is already in place is ended in the
    same change only when ``replace`` is asked for; a teacher without a verified authorisation for the subject and
    level needs a reason (G3), which is kept on the assignment and stays visible on the plan."""
    if role not in ROLES:
        raise HardValidation("ACA-ROLE", "Choose the teaching role", ", ".join(ROLES.values()))
    reason = (justification or "").strip()
    on = dt.date.today()
    with uow.command("ops", "class:manage", action="assign", record_kind="teaching_assignment") as cmd:
        plan = cmd.lock(ClassSubjectPlan, plan_id)
        cls = ClassGroup.objects.in_scope().filter(pk=plan.class_group_id).first()
        if cls is None:
            raise NotFound("class", plan.class_group_id)
        authz.require_scope(cls.scope_node_id, cmd.ctx)
        post = next((p for p in staff_of(cls.institution_id, on) if p.staff_id == staff_id), None)
        if post is None:
            raise HardValidation(
                "ACA-NOT-STAFF", "Choose a teacher of this school", "Only staff posted to the school can be assigned."
            )
        now = list(current(TeachingAssignment.objects.using(cmd.alias).filter(class_subject_plan_id=plan.id), on))
        if any(a.staff_id == staff_id for a in now):
            raise ConflictError("ACA-ALREADY", "Already teaching this class-subject", "Choose another teacher.")
        authorised = _covers(_authorised({staff_id}, on)[staff_id], plan.subject_id, cls.education_level)
        if not authorised and len(reason) < MIN_REASON:
            raise HardValidation(
                "ACA-NOT-AUTHORISED",
                "This teacher has no authorisation for the subject at this level",
                f"Give a reason of at least {MIN_REASON} characters (e.g. the CPD route or a supervised exception); "
                "the class-subject stays flagged (G3) until an authorisation is verified.",
            )
        if role == "teacher_of_record":
            for a in now:
                if a.role != "teacher_of_record":
                    continue
                if not replace:
                    raise ConflictError(
                        "G2-TWO-TEACHERS",
                        "Class-subject already has a teacher of record",
                        "Choose 'replace' to hand the class over, or add this teacher as a co-teacher.",
                    )
                ended = cmd.lock(TeachingAssignment, a.id)
                cmd.update(ended, valid_to=on)
                cmd.emit(
                    "CUR.ASSIGNMENT_CHANGED",
                    aggregate_id=ended.id,
                    aggregate_kind="teaching_assignment",
                    scope_node_id=cls.scope_node_id,
                    payload=_assignment_payload(ended, cls),
                )
        ta = cmd.add(
            TeachingAssignment(
                scope_node_id=cls.scope_node_id,
                class_subject_plan_id=plan.id,
                staff_id=staff_id,
                staff_post_id=post.id,
                role=role,
                justification=reason or None,
                valid_from=on,
            )
        )
        cmd.record_id = ta.id
        cmd.emit(
            "CUR.ASSIGNMENT_CHANGED",
            aggregate_id=ta.id,
            aggregate_kind="teaching_assignment",
            scope_node_id=cls.scope_node_id,
            payload=_assignment_payload(ta, cls),
        )
        return ta


def end(assignment_id: uuid.UUID) -> TeachingAssignment:
    """End an assignment now (today is its last day). The class-subject is then flagged (G2) until someone else is
    assigned."""
    on = dt.date.today()
    with uow.command("ops", "class:manage", action="end", record_kind="teaching_assignment") as cmd:
        ta = cmd.lock(TeachingAssignment, assignment_id)
        if ta.valid_to is not None and ta.valid_to <= on:
            raise ConflictError("ACA-ENDED", "This assignment has already ended", str(ta.valid_to))
        cls = ClassGroup.objects.get(pk=ClassSubjectPlan.objects.get(pk=ta.class_subject_plan_id).class_group_id)
        cmd.update(ta, valid_to=on)
        cmd.emit(
            "CUR.ASSIGNMENT_CHANGED",
            aggregate_id=ta.id,
            aggregate_kind="teaching_assignment",
            scope_node_id=cls.scope_node_id,
            payload=_assignment_payload(ta, cls),
        )
        return ta
