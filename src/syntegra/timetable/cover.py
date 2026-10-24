"""Staff absence and cover (MFS TIM-03, STF-06; rule G8).

The head records a teacher's absence for one or more school days. Every lesson the teacher is timetabled to teach on
those days is then affected and appears on the cover board for its day. For each affected lesson the board ranks the
staff who could take it: only teachers of the school who are free that period (not teaching, not absent, not already
covering) are offered, ranked qualified first (a verified authorisation for the subject at the class's level), then the
fewest cover lessons this term, then the fewest lessons that day. The head confirms a teacher, or chooses supervised
study with work set, merging the class into another, or cancelling the lesson. Cover is never assigned automatically,
and a cover teacher without the authorisation is recorded as such (``is_qualified``) and shown on the board (G8).
Confirming cover materialises the dated lesson (``lesson_occurrence``) with the teacher who actually takes it.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import IntegrityError, transaction

from syntegra.academic import teaching
from syntegra.academic.models import ClassGroup, Subject
from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.timetable import services as tts
from syntegra.timetable.models import LessonOccurrence, Timetable, TimetableLesson

ABSENCE_TYPES = {
    "sickness": "Sickness",
    "training": "Training or workshop",
    "official_duty": "Official duty (examinations, ministry)",
    "personal": "Personal or family",
    "leave": "Approved leave",
    "other": "Other",
}
ALTERNATIVES = {
    "supervised_study_with_lms_work": "Supervised study with work set",
    "merged_class": "Merge with another class",
    "cancelled_lesson": "Cancel the lesson",
}
MAX_DAYS = 30


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.TIME_ZONE)


def _school(institution_id: uuid.UUID) -> Any:
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _absences_on(institution_id: uuid.UUID, on: dt.date) -> list[Any]:
    from syntegra.people.models import StaffAbsence

    inst = _school(institution_id)
    tz = _tz()
    start = dt.datetime.combine(on, dt.time(0), tzinfo=tz)
    end = start + dt.timedelta(days=1)
    return list(
        StaffAbsence.objects.filter(
            scope_node_id=inst.scope_node_id, starts_at__lt=end, ends_at__gt=start, status__in=("recorded", "approved")
        ).order_by("starts_at")
    )


def record_absence(
    institution_id: uuid.UUID, staff_id: uuid.UUID, first: dt.date, last: dt.date | None, absence_type: str
) -> Any:
    """Record a teacher's absence for whole school days, from ``first`` to ``last``."""
    from syntegra.people.models import StaffAbsence

    ctx = context.require()
    authz.require("cover:manage", ctx)
    inst = _school(institution_id)
    last = last or first
    if absence_type not in ABSENCE_TYPES:
        raise HardValidation("TIM-ABSENCE-TYPE", "Choose the kind of absence", ", ".join(ABSENCE_TYPES.values()))
    if last < first:
        raise HardValidation("TIM-ABSENCE-DATES", "Dates the wrong way round", "The last day is before the first.")
    if (last - first).days >= MAX_DAYS:
        raise HardValidation("TIM-ABSENCE-DATES", "Too long for cover", f"Record at most {MAX_DAYS} days at a time.")
    posts = {p.staff_id: p for p in teaching.staff_of(inst.id, first)}
    if staff_id not in posts:
        raise HardValidation(
            "TIM-ABSENCE-STAFF", "Not a member of staff here", "Choose a teacher posted to the school."
        )
    tz = _tz()
    starts = dt.datetime.combine(first, dt.time(0), tzinfo=tz)
    ends = dt.datetime.combine(last + dt.timedelta(days=1), dt.time(0), tzinfo=tz)
    with uow.command("ops", "cover:manage", action="record_absence", record_kind="staff_absence") as cmd:
        clash = StaffAbsence.objects.using(cmd.alias).filter(
            staff_id=staff_id, starts_at__lt=ends, ends_at__gt=starts, status__in=("recorded", "approved")
        )
        if clash.exists():
            raise ConflictError("TIM-ABSENCE-OVERLAP", "Absence already recorded", "These days overlap an absence.")
        a = cmd.add(
            StaffAbsence(
                scope_node_id=inst.scope_node_id,
                staff_id=staff_id,
                staff_post_id=posts[staff_id].id,
                absence_type=absence_type,
                starts_at=starts,
                ends_at=ends,
                is_planned=first > dt.date.today(),
                approved_by=ctx.actor_id,
                status="recorded",
            )
        )
        cmd.record_id = a.id
        return a


def _occurrences(lessons: list[uuid.UUID], on: dt.date) -> dict[uuid.UUID, LessonOccurrence]:
    return {
        o.timetable_lesson_id: o for o in LessonOccurrence.objects.filter(timetable_lesson_id__in=lessons, occurs_on=on)
    }


def _covers_on(tt: Timetable, on: dt.date) -> list[Any]:
    from syntegra.people.models import CoverAssignment

    occ = LessonOccurrence.objects.filter(
        timetable_lesson_id__in=TimetableLesson.objects.filter(timetable_id=tt.id).values("id"), occurs_on=on
    )
    return list(CoverAssignment.objects.filter(lesson_occurrence_id__in=list(occ.values_list("id", flat=True))))


def cover_load(institution_id: uuid.UUID, since: dt.date) -> dict[uuid.UUID, int]:
    """Cover lessons taken by each teacher since a date (fairness)."""
    from syntegra.people.models import CoverAssignment

    inst = _school(institution_id)
    tz = _tz()
    out: dict[uuid.UUID, int] = {}
    for sid in CoverAssignment.objects.filter(
        scope_node_id=inst.scope_node_id,
        status="confirmed",
        cover_staff_id__isnull=False,
        created_at__gte=dt.datetime.combine(since, dt.time(0), tzinfo=tz),
    ).values_list("cover_staff_id", flat=True):
        out[sid] = out.get(sid, 0) + 1
    return out


def _term_start(institution_id: uuid.UUID, on: dt.date) -> dt.date:
    from syntegra.academic.models import AcademicPeriod

    t = AcademicPeriod.objects.filter(kind="term", starts_on__lte=on, ends_on__gte=on).order_by("-starts_on").first()
    return t.starts_on if t else on - dt.timedelta(days=90)


def board(institution_id: uuid.UUID, on: dt.date) -> dict[str, Any]:
    """The cover board for a school day: absences, affected lessons with their cover and the ranked candidates."""
    ctx = context.require()
    authz.require("cover:view", ctx)
    inst = _school(institution_id)
    tt = tts.current(inst.id)
    weekday = on.isoweekday()
    absences = _absences_on(inst.id, on)
    posts = teaching.staff_of(inst.id, on)
    staff_ids = {p.staff_id for p in posts}
    names = teaching._names(staff_ids | {a.staff_id for a in absences})
    staff_list = sorted(({"id": s, "name": names.get(s, "?")} for s in staff_ids), key=lambda x: x["name"])
    if tt is None or weekday not in tts.DAYS:
        return {"institution": inst.name, "on": on, "absences": [], "rows": [], "gaps": 0, "covered": 0, "load": [],
                "timetable": tt is not None, "weekday": weekday in tts.DAYS, "types": ABSENCE_TYPES,
                "alternatives": ALTERNATIVES, "staff": staff_list, "can_manage": ctx.has("cover:manage")}  # fmt: skip
    day_lessons = list(TimetableLesson.objects.filter(timetable_id=tt.id, cycle_day=weekday))
    absent = {a.staff_id: a for a in absences}
    times = tts.bell(tt)
    order = {b[0]: i for i, b in enumerate(tts.schedule(tt))}
    affected = sorted((ls for ls in day_lessons if ls.staff_id in absent), key=lambda x: order.get(x.period_code, 99))
    occ = _occurrences([ls.id for ls in affected], on)
    covers = {c.lesson_occurrence_id: c for c in _covers_on(tt, on) if c.status in ("confirmed", "booked")}
    period_of = {o.id: ls.period_code for ls in affected if (o := occ.get(ls.id)) is not None}
    covering = {(c.cover_staff_id, period_of.get(c.lesson_occurrence_id)) for c in covers.values() if c.cover_staff_id}
    teaching_now = {(ls.staff_id, ls.period_code) for ls in day_lessons}
    lessons_today: dict[uuid.UUID, int] = {}
    for ls in day_lessons:
        lessons_today[ls.staff_id] = lessons_today.get(ls.staff_id, 0) + 1
    load = cover_load(inst.id, _term_start(inst.id, on))
    auth = teaching._authorised(staff_ids, on)
    classes = {c.id: c for c in ClassGroup.objects.filter(id__in={ls.class_group_id for ls in affected})}
    subjects = dict(Subject.objects.filter(id__in={ls.subject_id for ls in affected}).values_list("id", "name"))
    rooms = _room_names({ls.room_id for ls in affected if ls.room_id})
    rows = []
    for ls in affected:
        cls = classes[ls.class_group_id]
        o = occ.get(ls.id)
        cover = covers.get(o.id) if o is not None else None
        cands = []
        for sid in staff_ids:
            if sid in absent or (sid, ls.period_code) in teaching_now or (sid, ls.period_code) in covering:
                continue
            qualified = teaching._covers(auth.get(sid, []), ls.subject_id, cls.education_level)
            cands.append(
                {
                    "staff_id": sid,
                    "name": names.get(sid, "?"),
                    "qualified": qualified,
                    "cover_load": load.get(sid, 0),
                    "lessons_today": lessons_today.get(sid, 0),
                }
            )
        cands.sort(key=lambda c: (not c["qualified"], c["cover_load"], c["lessons_today"], c["name"]))
        a, b = times.get(ls.period_code, (dt.time(0), dt.time(0)))
        rows.append(
            {
                "lesson_id": ls.id,
                "absence_id": absent[ls.staff_id].id,
                "period": ls.period_code,
                "starts": a,
                "ends": b,
                "class": cls.name,
                "subject": subjects.get(ls.subject_id, "?"),
                "room": rooms.get(ls.room_id, "—") if ls.room_id else "—",
                "teacher": names.get(ls.staff_id, "?"),
                "cover": {
                    "id": cover.id,
                    "staff": names.get(cover.cover_staff_id, "?") if cover.cover_staff_id else None,
                    "qualified": cover.is_qualified,
                    "alternative": ALTERNATIVES.get(cover.alternative or "", None),
                }
                if cover
                else None,
                "candidates": cands,
            }
        )
    gaps = sum(1 for r in rows if r["cover"] is None)
    return {
        "institution": inst.name,
        "on": on,
        "timetable": True,
        "weekday": True,
        "absences": [
            {
                "id": a.id,
                "staff": names.get(a.staff_id, "?"),
                "type": ABSENCE_TYPES.get(a.absence_type, a.absence_type),
                "first": a.starts_at.astimezone(_tz()).date(),
                "last": (a.ends_at.astimezone(_tz()) - dt.timedelta(seconds=1)).date(),
                "lessons": sum(1 for ls in affected if ls.staff_id == a.staff_id),
            }
            for a in absences
        ],
        "rows": rows,
        "gaps": gaps,
        "covered": len(rows) - gaps,
        "load": sorted(
            ({"name": names.get(s, "?"), "covers": load.get(s, 0)} for s in staff_ids),
            key=lambda x: (-int(x["covers"]), str(x["name"])),
        ),
        "staff": staff_list,
        "types": ABSENCE_TYPES,
        "alternatives": ALTERNATIVES,
        "can_manage": ctx.has("cover:manage"),
    }


def _room_names(ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    from syntegra.operations.models import Room

    return {r.id: (r.name or r.code) for r in Room.objects.filter(id__in=ids)}


def assign(
    lesson_id: uuid.UUID, on: dt.date, *, cover_staff_id: uuid.UUID | None = None, alternative: str | None = None
) -> Any:
    """Confirm cover for one affected lesson: a free teacher, or an alternative (supervised study, merge, cancel)."""
    from syntegra.people.models import CoverAssignment

    ctx = context.require()
    authz.require("cover:manage", ctx)
    lesson = TimetableLesson.objects.filter(pk=lesson_id).first()
    tt = Timetable.objects.filter(pk=lesson.timetable_id).first() if lesson else None
    if lesson is None or tt is None or tt.status != "published":
        raise NotFound("lesson", lesson_id)
    if (cover_staff_id is None) == (alternative is None):
        raise HardValidation("TIM-COVER-CHOICE", "Choose a teacher or an alternative", "One or the other.")
    if alternative is not None and alternative not in ALTERNATIVES:
        raise HardValidation("TIM-COVER-CHOICE", "Unknown alternative", ", ".join(ALTERNATIVES.values()))
    d = board(tt.institution_id, on)
    row = next((r for r in d["rows"] if r["lesson_id"] == lesson.id), None)
    if row is None:
        raise HardValidation("TIM-COVER-NOT-AFFECTED", "This lesson needs no cover", "Its teacher is not absent then.")
    if row["cover"] is not None:
        raise ConflictError("TIM-COVER-EXISTS", "Cover is already arranged", "Cancel it first to change it.")
    cand = None
    if cover_staff_id is not None:
        cand = next((c for c in row["candidates"] if c["staff_id"] == cover_staff_id), None)
        if cand is None:
            raise HardValidation(
                "TIM-COVER-NOT-FREE", "That teacher is not free", "They are teaching, absent or covering that period."
            )
    a, b = tts.bell(tt)[lesson.period_code]
    tz = _tz()
    with uow.command("ops", "cover:manage", action="assign_cover", record_kind="cover_assignment") as cmd:
        o = (
            LessonOccurrence.objects.using(cmd.alias)
            .select_for_update()
            .filter(timetable_lesson_id=lesson.id, occurs_on=on)
            .first()
        )
        status = "covered" if cover_staff_id else "cancelled"
        staff = cover_staff_id or lesson.staff_id
        if o is None:
            try:
                with transaction.atomic(using=cmd.alias):
                    o = cmd.add(
                        LessonOccurrence(
                            scope_node_id=tt.scope_node_id,
                            timetable_lesson_id=lesson.id,
                            occurs_on=on,
                            starts_at=dt.datetime.combine(on, a, tzinfo=tz),
                            ends_at=dt.datetime.combine(on, b, tzinfo=tz),
                            staff_id=staff,
                            room_id=lesson.room_id,
                            status=status,
                        )
                    )
            except IntegrityError as exc:
                raise ConflictError("TIM-COVER-RACE", "Changed a moment ago", "Reload the page.") from exc
        else:
            if o.status == "taught":
                raise ConflictError("TIM-COVER-TAUGHT", "The lesson was already taught", "")
            if (
                CoverAssignment.objects.using(cmd.alias)
                .filter(lesson_occurrence_id=o.id, status__in=("confirmed", "booked"))
                .exists()
            ):
                raise ConflictError("TIM-COVER-EXISTS", "Cover is already arranged", "Cancel it first to change it.")
            cmd.update(o, staff_id=staff, status=status)
        c = cmd.add(
            CoverAssignment(
                scope_node_id=tt.scope_node_id,
                absence_id=row["absence_id"],
                lesson_occurrence_id=o.id,
                cover_staff_id=cover_staff_id,
                is_qualified=bool(cand and cand["qualified"]),
                rank_evidence={
                    "rank": (row["candidates"].index(cand) + 1) if cand else None,
                    "of": len(row["candidates"]),
                    "qualified": bool(cand and cand["qualified"]),
                    "cover_load": cand["cover_load"] if cand else None,
                    "lessons_today": cand["lessons_today"] if cand else None,
                },
                alternative=alternative,
                proposed_by=ctx.actor_id,
                confirmed_by=ctx.actor_id,
                status="confirmed",
            )
        )
        cmd.record_id = c.id
        return c


def cancel(cover_id: uuid.UUID) -> Any:
    """Undo a cover arrangement: the lesson goes back to its own teacher (and back on the board as a gap)."""
    from syntegra.people.models import CoverAssignment

    authz.require("cover:manage")
    with uow.command("ops", "cover:manage", action="cancel_cover", record_kind="cover_assignment") as cmd:
        c = cmd.lock(CoverAssignment, cover_id)
        if c.status not in ("confirmed", "booked"):
            raise ConflictError("TIM-COVER-GONE", "Cover already cancelled", "")
        o = cmd.lock(LessonOccurrence, c.lesson_occurrence_id)
        if o.occurs_on < dt.date.today():
            raise ConflictError("TIM-COVER-PAST", "The lesson has taken place", "Past cover is kept as it was.")
        lesson = TimetableLesson.objects.get(pk=o.timetable_lesson_id)
        cmd.update(c, status="declined")
        cmd.update(o, staff_id=lesson.staff_id, status="scheduled")
        return c


def covers_in_week(tt: Timetable, monday: dt.date) -> dict[tuple[uuid.UUID, dt.date], dict[str, Any]]:
    """Confirmed cover for the week, by (timetable lesson, date): who takes it, or the alternative."""
    from syntegra.people.models import CoverAssignment

    occ = {
        o.id: o
        for o in LessonOccurrence.objects.filter(
            timetable_lesson_id__in=TimetableLesson.objects.filter(timetable_id=tt.id).values("id"),
            occurs_on__gte=monday,
            occurs_on__lte=monday + dt.timedelta(days=4),
        )
    }
    out = {}
    for c in CoverAssignment.objects.filter(lesson_occurrence_id__in=list(occ), status="confirmed"):
        o = occ[c.lesson_occurrence_id]
        out[(o.timetable_lesson_id, o.occurs_on)] = {
            "staff_id": c.cover_staff_id,
            "alternative": ALTERNATIVES.get(c.alternative or "", None),
            "qualified": c.is_qualified,
        }
    return out
