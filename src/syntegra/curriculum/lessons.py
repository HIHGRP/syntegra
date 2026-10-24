"""Lesson plan and delivery log (MFS CUR-09, FR-CUR-09, FR-CUR-111; coverage rules G5, G6, G10).

Every class lesson is linked to the curriculum. A class-subject carries the curriculum version that applies to it
(``class_subject_plan.curriculum_version_id``, stamped from the school's adoption). For the teacher of record the
scheme of work is drafted from that version: the term's objectives, in curriculum order, are spread over the term's
teaching weeks in proportion to their minimum hours (the last two weeks are kept for revision and examinations).
Within a week the objectives are shared out over the week's timetabled lessons in order, so each dated lesson shows
the objectives it is planned to teach. After the lesson the teacher logs what was actually covered, how many
learners were present and a note — the delivery log is append-only and is the evidence for curriculum compliance.
A lesson is logged once, only by the teacher it is timetabled for, never before it has happened.
"""

from __future__ import annotations

import datetime as dt
import math
import uuid
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import IntegrityError, transaction

from syntegra.academic.models import (
    AcademicPeriod,
    ClassGroup,
    ClassMembership,
    ClassSubjectPlan,
    Subject,
    TeachingAssignment,
)
from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.curriculum.models import (
    Curriculum,
    CurriculumNode,
    CurriculumVersion,
    DeliveryLog,
    SchemeOfWork,
    SchemeWeek,
)
from syntegra.timetable import services as timetable
from syntegra.timetable.models import LessonOccurrence, Timetable, TimetableLesson

RESERVED_WEEKS = 2  # revision and examinations at the end of the term
MAX_NOTE = 1000


# --------------------------------------------------------------------------- who and what
def my_staff_id(ctx: context.Context | None = None) -> uuid.UUID | None:
    """The staff record of the signed-in user, when the account belongs to a member of staff."""
    from syntegra.iam.models import AppUser

    ctx = ctx or context.require()
    u = AppUser.objects.filter(pk=ctx.actor_id).first() if ctx.actor_id else None
    return u.person_id if u is not None and u.person_kind == "staff" else None


def _active(qs: Any, on: dt.date) -> Any:
    return qs.filter(valid_from__lte=on).exclude(valid_to__lt=on)


def choices(on: dt.date | None = None) -> list[dict[str, Any]]:
    """The class-subjects the user can open: a teacher's own; for those who manage classes, every class-subject of the
    schools in their scope that has a teacher of record."""
    ctx = context.require()
    authz.require("class:view", ctx)
    on = on or dt.date.today()
    mine = my_staff_id(ctx)
    from syntegra.academic.teaching import current

    qs = current(TeachingAssignment.objects.in_scope().filter(role="teacher_of_record"), on)
    if not ctx.has("class:manage"):
        if mine is None:
            return []
        qs = qs.filter(staff_id=mine)
    rows = list(qs)
    plans = {p.id: p for p in ClassSubjectPlan.objects.filter(id__in={a.class_subject_plan_id for a in rows})}
    classes = {c.id: c for c in ClassGroup.objects.filter(id__in={p.class_group_id for p in plans.values()})}
    subjects = dict(Subject.objects.filter(id__in={p.subject_id for p in plans.values()}).values_list("id", "name"))
    out = []
    for a in rows:
        p = plans.get(a.class_subject_plan_id)
        c = classes.get(p.class_group_id) if p else None
        if p is None or c is None:
            continue
        out.append(
            {
                "assignment_id": a.id,
                "plan_id": p.id,
                "class_id": c.id,
                "label": f"{c.name} — {subjects.get(p.subject_id, '?')}",
                "class": c.name,
                "mine": a.staff_id == mine,
                "has_curriculum": p.curriculum_version_id is not None,
            }
        )
    out.sort(key=lambda r: (not r["mine"], not r["has_curriculum"], r["label"]))
    return out


def _term(cls: ClassGroup, on: dt.date) -> AcademicPeriod:
    terms = list(AcademicPeriod.objects.filter(kind="term", parent_id=cls.period_id).order_by("starts_on"))
    if not terms:
        terms = list(
            AcademicPeriod.objects.filter(kind="term", starts_on__lte=on, ends_on__gte=on).order_by("starts_on")
        )
    if not terms:
        raise HardValidation("CUR-NO-TERM", "No term is set up for this class", "Set up the academic calendar first.")
    term: AcademicPeriod = next(
        (t for t in terms if t.starts_on <= on <= t.ends_on), next((t for t in terms if t.starts_on > on), terms[-1])
    )
    return term


def _term_no(term: AcademicPeriod) -> int:
    siblings = list(
        AcademicPeriod.objects.filter(kind="term", parent_id=term.parent_id)
        .order_by("starts_on")
        .values_list("id", flat=True)
    )
    return siblings.index(term.id) + 1 if term.id in siblings else 1


def term_weeks(term: AcademicPeriod) -> list[dt.date]:
    """Mondays of the term's weeks."""
    out, d = [], timetable.monday(term.starts_on)
    while d <= term.ends_on:
        out.append(d)
        d += dt.timedelta(days=7)
    return out


# --------------------------------------------------------------------------- scheme of work (G5, G10)
def spread(objectives: list[tuple[uuid.UUID, float]], weeks: int) -> list[list[uuid.UUID]]:
    """Spread the objectives (in order, each with its minimum hours) over ``weeks`` teaching weeks in proportion to
    their hours. Every week gets at least one objective; an objective longer than a week runs on into the next."""
    if weeks <= 0 or not objectives:
        return [[] for _ in range(max(weeks, 0))]
    total = sum(max(h, 0.1) for _id, h in objectives)
    out: list[list[uuid.UUID]] = [[] for _ in range(weeks)]
    cum = 0.0
    for node_id, h in objectives:
        start = cum / total * weeks
        cum += max(h, 0.1)
        end = cum / total * weeks
        first = min(math.floor(start + 1e-9), weeks - 1)
        last = max(first, min(math.ceil(end - 1e-9) - 1, weeks - 1))
        for w in range(first, last + 1):
            out[w].append(node_id)
    for w in range(weeks):  # a week left empty by rounding continues the previous week's last objective
        if not out[w] and w > 0 and out[w - 1]:
            out[w] = [out[w - 1][-1]]
    return out


def share(node_ids: list[Any], lessons: int) -> list[list[Any]]:
    """Share a week's objectives over its lessons in order: several objectives per lesson when there are more
    objectives than lessons, otherwise one objective over consecutive lessons."""
    if lessons <= 0:
        return []
    if not node_ids:
        return [[] for _ in range(lessons)]
    k = len(node_ids)
    if k <= lessons:
        return [[node_ids[j * k // lessons]] for j in range(lessons)]
    return [node_ids[j * k // lessons : (j + 1) * k // lessons] for j in range(lessons)]


def _objectives(version_id: uuid.UUID, term_no: int) -> list[CurriculumNode]:
    nodes = CurriculumNode.objects.filter(version_id=version_id, kind="objective").order_by("sort_key", "node_code")
    return [n for n in nodes if n.term_hint in (None, term_no)]


def draft_scheme(assignment_id: uuid.UUID, on: dt.date | None = None) -> SchemeOfWork:
    """Draft (or redraft) the scheme of work of a teaching assignment from its class-subject's curriculum version."""
    ctx = context.require()
    authz.require("lesson:plan", ctx)
    on = on or dt.date.today()
    with uow.command("ops", "lesson:plan", action="draft_scheme", record_kind="scheme_of_work") as cmd:
        ta = cmd.lock(TeachingAssignment, assignment_id)
        if ta.staff_id != my_staff_id(ctx) and not ctx.has("class:manage"):
            raise Forbidden("Only the teacher of this class-subject or the head can draft its scheme of work.")
        if ta.class_subject_plan_id is None:
            raise HardValidation("CUR-NO-PLAN", "Not a class-subject assignment", "")
        plan = ClassSubjectPlan.objects.get(pk=ta.class_subject_plan_id)
        if plan.curriculum_version_id is None:
            raise HardValidation(
                "CUR-NO-VERSION",
                "No curriculum applies to this class-subject",
                "The curriculum version is set when the school adopts the curriculum for this level.",
            )
        cls = ClassGroup.objects.get(pk=plan.class_group_id)
        term = _term(cls, on)
        weeks = term_weeks(term)
        teaching = weeks[:-RESERVED_WEEKS] if len(weeks) > RESERVED_WEEKS + 2 else weeks
        objs = _objectives(plan.curriculum_version_id, _term_no(term))
        if not objs:
            raise HardValidation("CUR-NO-OBJECTIVES", "The curriculum has no objectives for this term", "")
        per_week = spread([(n.id, float(n.min_hours or 1)) for n in objs], len(teaching))
        prior = list(
            SchemeOfWork.objects.using(cmd.alias)
            .filter(teaching_assignment_id=ta.id)
            .exclude(status__in=("superseded", "retired", "withdrawn"))
        )
        for old in prior:
            cmd.update(old, status="superseded")
        latest = (
            SchemeOfWork.objects.using(cmd.alias).filter(class_subject_plan_id=plan.id).order_by("-version").first()
        )
        scheme = cmd.add(
            SchemeOfWork(
                class_subject_plan_id=plan.id,
                teaching_assignment_id=ta.id,
                curriculum_version_id=plan.curriculum_version_id,
                version=(latest.version + 1) if latest else 1,
                is_auto_drafted=True,
                status="published",
            )
        )
        minutes = int(plan.periods_per_week or 0) * timetable.period_minutes(cls.institution_id)
        for i, monday in enumerate(teaching):
            cmd.add(
                SchemeWeek(
                    scheme_id=scheme.id,
                    week_no=i + 1,
                    week_starts_on=monday,
                    node_ids=[str(x) for x in per_week[i]],
                    planned_minutes=minutes,
                )
            )
        cmd.record_id = scheme.id
        return scheme


def _scheme(assignment_id: uuid.UUID) -> SchemeOfWork | None:
    """The assignment's scheme of work; after a hand-over the new teacher works from the class-subject's latest one."""
    s: SchemeOfWork | None = (
        SchemeOfWork.objects.filter(teaching_assignment_id=assignment_id, status="published")
        .order_by("-version")
        .first()
    )
    if s is None:
        ta = TeachingAssignment.objects.filter(pk=assignment_id).first()
        if ta is not None and ta.class_subject_plan_id is not None:
            s = (
                SchemeOfWork.objects.filter(class_subject_plan_id=ta.class_subject_plan_id, status="published")
                .order_by("-version")
                .first()
            )
    return s


def _week_nodes(scheme: SchemeOfWork | None, monday: dt.date) -> list[str]:
    if scheme is None:
        return []
    w = SchemeWeek.objects.filter(scheme_id=scheme.id, week_starts_on=monday).first()
    return list(w.node_ids or []) if w else []


def _planned(scheme: SchemeOfWork | None, lessons: list[dict[str, Any]]) -> dict[uuid.UUID, list[str]]:
    """Planned objectives for each dated lesson (lessons of one class-subject, one week, in timetable order)."""
    if not lessons:
        return {}
    nodes = _week_nodes(scheme, timetable.monday(lessons[0]["on"]))
    return {ls["lesson_id"]: part for ls, part in zip(lessons, share(nodes, len(lessons)), strict=True)}


# --------------------------------------------------------------------------- read model (CUR-09)
def plan_view(assignment_id: uuid.UUID, week_of: dt.date | None = None) -> dict[str, Any]:
    """The class-subject's curriculum, scheme of work and the week's lessons, each with its planned objectives and
    what was delivered."""
    ctx = context.require()
    authz.require("class:view", ctx)
    today = dt.date.today()
    ta: TeachingAssignment | None = TeachingAssignment.objects.in_scope().filter(pk=assignment_id).first()
    if ta is None or ta.class_subject_plan_id is None:
        raise NotFound("teaching assignment", assignment_id)
    mine = my_staff_id(ctx)
    if ta.staff_id != mine and not ctx.has("class:manage"):
        raise Forbidden("This is another teacher's lesson plan.")
    plan = ClassSubjectPlan.objects.get(pk=ta.class_subject_plan_id)
    cls = ClassGroup.objects.get(pk=plan.class_group_id)
    subject = Subject.objects.filter(pk=plan.subject_id).first()
    from syntegra.people.models import Staff

    teacher = Staff.objects.filter(pk=ta.staff_id).first()
    term = _term(cls, week_of or today)
    weeks = term_weeks(term)
    monday = timetable.monday(week_of or today)
    if monday < weeks[0]:
        monday = weeks[0]
    if monday > weeks[-1]:
        monday = weeks[-1]
    version = (
        CurriculumVersion.objects.filter(pk=plan.curriculum_version_id).first() if plan.curriculum_version_id else None
    )
    curriculum = Curriculum.objects.filter(pk=version.curriculum_id).first() if version else None
    nodes = {n.id: n for n in CurriculumNode.objects.filter(version_id=version.id)} if version else {}

    def node(nid: Any) -> dict[str, Any]:
        n = nodes.get(uuid.UUID(str(nid)))
        parent = nodes.get(n.parent_id) if n and n.parent_id else None
        return {
            "id": str(nid),
            "code": n.node_code if n else "?",
            "statement": n.statement if n else "(not in this curriculum version)",
            "topic": parent.statement if parent else "",
        }

    scheme = _scheme(ta.id)
    logs = list(
        DeliveryLog.objects.filter(
            teaching_assignment_id__in=TeachingAssignment.objects.filter(class_subject_plan_id=plan.id).values("id")
        ).order_by("delivered_on")
    )
    delivered = {str(x) for lg in logs for x in (lg.node_ids or [])}
    lessons = timetable.week(cls.institution_id, monday, class_subject_plan_id=plan.id)
    planned = _planned(scheme, lessons)
    occ = {
        (o.timetable_lesson_id, o.occurs_on): o
        for o in LessonOccurrence.objects.filter(
            timetable_lesson_id__in=[ls["lesson_id"] for ls in lessons], occurs_on__in=[ls["on"] for ls in lessons]
        )
    }
    log_of = {lg.lesson_occurrence_id: lg for lg in logs}
    from syntegra.operations.models import Room

    rooms = dict(
        Room.objects.filter(id__in={ls["room_id"] for ls in lessons if ls["room_id"]}).values_list("id", "code")
    )
    roll = _active(ClassMembership.objects.filter(class_group_id=cls.id), today).count()
    scheme_rows = []
    planned_to_date: set[str] = set()
    planned_before: set[str] = set()  # weeks already over: anything not delivered from them is behind
    if scheme is not None:
        for w in SchemeWeek.objects.filter(scheme_id=scheme.id).order_by("week_no"):
            ids = [str(x) for x in (w.node_ids or [])]
            if w.week_starts_on <= monday:
                planned_to_date |= set(ids)
            if w.week_starts_on < monday:
                planned_before |= set(ids)
            scheme_rows.append(
                {
                    "week_no": w.week_no,
                    "starts": w.week_starts_on,
                    "current": w.week_starts_on == monday,
                    "objectives": [{**node(x), "delivered": x in delivered} for x in ids],
                }
            )
    behind = sorted((node(x) for x in planned_before - delivered), key=lambda r: (r["code"], r["statement"]))
    this_week = _week_nodes(scheme, monday)

    def options(planned_ids: list[str]) -> list[dict[str, Any]]:
        """What the log form offers: the lesson's planned objectives (ticked), then the rest of the week's and the
        objectives the class is behind on."""
        seen: dict[str, dict[str, Any]] = {}
        for x in planned_ids:
            seen[str(x)] = {**node(x), "planned": True}
        for x in [*this_week, *(b["id"] for b in behind)]:
            seen.setdefault(str(x), {**node(x), "planned": False})
        return list(seen.values())

    week_rows = []
    for ls in lessons:
        o = occ.get((ls["lesson_id"], ls["on"]))
        lg = log_of.get(o.id) if o else None
        week_rows.append(
            {
                **ls,
                "room": rooms.get(ls["room_id"], ""),
                "planned": [node(x) for x in planned.get(ls["lesson_id"], [])],
                "log": (
                    {
                        "objectives": [node(x) for x in lg.node_ids or []],
                        "minutes": lg.delivered_minutes,
                        "present": lg.learners_present,
                        "note": lg.note,
                        "as_planned": lg.is_as_planned,
                    }
                    if lg
                    else None
                ),
                "options": options(planned.get(ls["lesson_id"], [])),
                "can_log": lg is None and version is not None and ls["on"] <= today and ls["staff_id"] == mine,
                "future": ls["on"] > today,
            }
        )
    objectives_total = len(_objectives(version.id, _term_no(term))) if version else 0
    prev_week = monday - dt.timedelta(days=7)
    next_week = monday + dt.timedelta(days=7)
    return {
        "assignment_id": ta.id,
        "class": {"id": cls.id, "name": cls.name, "level": cls.education_level, "learners": roll},
        "subject": subject.name if subject else "?",
        "subject_id": plan.subject_id,
        "teacher": f"{teacher.given_name} {teacher.family_name}" if teacher else "?",
        "mine": ta.staff_id == mine,
        "curriculum": (
            {
                "title": curriculum.title if curriculum else "",
                "authority": curriculum.authority if curriculum else "",
                "version": version.version_label,
                "objectives": objectives_total,
            }
            if version
            else None
        ),
        "term": {"name": term.name, "starts": term.starts_on, "ends": term.ends_on},
        "week": {
            "monday": monday,
            "friday": monday + dt.timedelta(days=4),
            "no": weeks.index(monday) + 1 if monday in weeks else None,
            "of": len(weeks),
            "prev": prev_week if prev_week >= weeks[0] else None,
            "next": next_week if next_week <= weeks[-1] else None,
        },
        "scheme": {"version": scheme.version, "weeks": scheme_rows} if scheme else None,
        "lessons": week_rows,
        "progress": {
            "planned_to_date": len(planned_to_date),
            "delivered": len(delivered & {str(n) for n in nodes}),
            "behind": behind,
            "logged_lessons": len(logs),
        },
        "can_draft": scheme is None and version is not None and (ta.staff_id == mine or ctx.has("class:manage")),
    }


# --------------------------------------------------------------------------- delivery log (G6)
def log_delivery(
    lesson_id: uuid.UUID,
    occurs_on: dt.date,
    node_ids: list[str],
    *,
    learners_present: int | None = None,
    minutes: int | None = None,
    note: str | None = None,
) -> DeliveryLog:
    """Record what a timetabled lesson actually covered. Only the lesson's teacher, only once, never in advance."""
    ctx = context.require()
    authz.require("lesson:deliver", ctx)
    today = dt.date.today()
    lesson: TimetableLesson | None = TimetableLesson.objects.filter(pk=lesson_id).first()
    if lesson is None:
        raise NotFound("lesson", lesson_id)
    tt = Timetable.objects.filter(pk=lesson.timetable_id).first()
    if tt is None or tt.status != "published":
        raise HardValidation("CUR-TIMETABLE", "This lesson is not on the published timetable", "")
    authz.require_scope(tt.scope_node_id, ctx)
    if lesson.staff_id != my_staff_id(ctx):
        raise Forbidden("Only the teacher this lesson is timetabled for can log it.")
    if occurs_on.isoweekday() != lesson.cycle_day:
        raise HardValidation(
            "CUR-DAY", "The lesson is not on that day", f"It is on {timetable.DAYS.get(lesson.cycle_day, '?')}s."
        )
    if occurs_on > today:
        raise HardValidation("CUR-FUTURE", "A lesson can be logged only once it has taken place", str(occurs_on))
    plan = ClassSubjectPlan.objects.get(pk=lesson.class_subject_plan_id)
    cls = ClassGroup.objects.get(pk=plan.class_group_id)
    term = _term(cls, occurs_on)
    if not term.starts_on <= occurs_on <= term.ends_on:
        raise HardValidation(
            "CUR-TERM", "That date is outside the term", f"{term.name}: {term.starts_on}–{term.ends_on}"
        )
    if plan.curriculum_version_id is None:
        raise HardValidation("CUR-NO-VERSION", "No curriculum applies to this class-subject", "")
    valid = {
        str(n)
        for n in CurriculumNode.objects.filter(
            version_id=plan.curriculum_version_id, kind__in=("objective", "topic")
        ).values_list("id", flat=True)
    }
    chosen = list(dict.fromkeys(str(x) for x in node_ids if str(x)))
    if not chosen:
        raise HardValidation("CUR-OBJECTIVES", "Tick the objectives the lesson covered", "")
    if not set(chosen) <= valid:
        raise HardValidation("CUR-OBJECTIVES", "An objective is not in this class-subject's curriculum", "")
    roll = _active(ClassMembership.objects.filter(class_group_id=cls.id), occurs_on).count()
    if learners_present is not None and not 0 <= learners_present <= roll:
        raise HardValidation("CUR-PRESENT", "Learners present must be between 0 and the class roll", f"Roll: {roll}")
    if minutes is not None and not 1 <= minutes <= 4 * lesson.duration_minutes:
        raise HardValidation(
            "CUR-MINUTES", "Minutes taught look wrong", f"The lesson is {lesson.duration_minutes} minutes."
        )
    note = (note or "").strip()[:MAX_NOTE] or None
    ta = (
        _active(TeachingAssignment.objects.filter(class_subject_plan_id=plan.id, staff_id=lesson.staff_id), occurs_on)
        .order_by("-valid_from")
        .first()
    )
    if ta is None:
        raise HardValidation("CUR-NO-ASSIGNMENT", "You were not assigned to this class-subject on that day", "")
    week = timetable.week(cls.institution_id, occurs_on, class_subject_plan_id=plan.id)
    planned = _planned(_scheme(ta.id), week).get(lesson.id, [])
    tz = ZoneInfo(settings.TIME_ZONE)
    a, b = timetable.bell(tt)[lesson.period_code]
    with uow.command("ops", "lesson:deliver", action="log_delivery", record_kind="delivery_log") as cmd:
        o = (
            LessonOccurrence.objects.using(cmd.alias)
            .select_for_update()
            .filter(timetable_lesson_id=lesson.id, occurs_on=occurs_on)
            .first()
        )
        if o is None:
            try:
                with transaction.atomic(using=cmd.alias):
                    o = cmd.add(
                        LessonOccurrence(
                            scope_node_id=tt.scope_node_id,
                            timetable_lesson_id=lesson.id,
                            occurs_on=occurs_on,
                            starts_at=dt.datetime.combine(occurs_on, a, tzinfo=tz),
                            ends_at=dt.datetime.combine(occurs_on, b, tzinfo=tz),
                            staff_id=lesson.staff_id,
                            room_id=lesson.room_id,
                            status="taught",
                        )
                    )
            except IntegrityError as exc:
                raise ConflictError("CUR-LOGGED", "This lesson was logged a moment ago", "Reload the page.") from exc
        elif DeliveryLog.objects.using(cmd.alias).filter(lesson_occurrence_id=o.id).exists():
            raise ConflictError("CUR-LOGGED", "This lesson is already logged", "A delivery log cannot be changed.")
        elif o.status in ("covered", "cancelled"):
            raise ConflictError(
                "CUR-COVERED", f"This lesson was {o.status}", "A lesson taken by cover or cancelled is not logged here."
            )
        else:
            cmd.update(o, status="taught")
        lg = cmd.add(
            DeliveryLog(
                scope_node_id=tt.scope_node_id,
                lesson_occurrence_id=o.id,
                teaching_assignment_id=ta.id,
                staff_id=lesson.staff_id,
                node_ids=chosen,
                delivered_minutes=minutes or lesson.duration_minutes,
                is_as_planned=set(planned) <= set(chosen),
                source="class_page",
                learners_present=learners_present,
                note=note,
                delivered_on=occurs_on,
            )
        )
        cmd.record_id = lg.id
        cmd.emit(
            "CUR.LESSON_DELIVERED",
            aggregate_id=lg.id,
            aggregate_kind="delivery_log",
            scope_node_id=tt.scope_node_id,
            payload={"delivery_log_id": lg.id, "teaching_assignment_id": ta.id},
        )
        return lg
