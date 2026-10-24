"""Timetable (MFS TIM, FR-TIM-101): the bell schedule and a weekly timetable built from the class subject plans.

``build`` places each class-subject's periods a week with its teacher of record, never putting a class, a teacher or a
room in two places at once and spreading a subject over the week (at most one lesson a day while there are days
left). Each lesson is taught in the class's home room when it is free, otherwise in another classroom of the school
that is not assessed unsafe. A class-subject that cannot be placed in full is listed as unmet and the timetable stays a
draft — publication is blocked while mandatory periods are missing (``unmet_requirements``). Publishing supersedes the
previous version. ``week`` gives the dated lessons of a class or a teacher for one week.

The school day is the school's own (TIM-01): when it starts, how long a period is, how many periods come before the
break, between the break and lunch and after lunch, and how long the break and lunch are. It is kept with each
timetable (``period_structure``); a new build keeps the day of the school's latest timetable unless a new one is given.
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any

from syntegra.academic.models import ClassGroup, ClassSubjectPlan, TeachingAssignment
from syntegra.core import authz, context, uow
from syntegra.core.errors import HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.timetable.models import PeriodStructure, Timetable, TimetableLesson

STRUCTURE = "DAY"
# (code, starts, ends, teaching) — a 35-minute period day with a short break and lunch
BELL: tuple[tuple[str, str, str, bool], ...] = (
    ("P1", "08:00", "08:35", True),
    ("P2", "08:35", "09:10", True),
    ("P3", "09:10", "09:45", True),
    ("BRK", "09:45", "10:05", False),
    ("P4", "10:05", "10:40", True),
    ("P5", "10:40", "11:15", True),
    ("P6", "11:15", "11:50", True),
    ("LUN", "11:50", "12:30", False),
    ("P7", "12:30", "13:05", True),
    ("P8", "13:05", "13:40", True),
    ("P9", "13:40", "14:15", True),
)
DAYS = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
TEACHING = [b[0] for b in BELL if b[3]]
Day = tuple[tuple[str, str, str, bool], ...]
LATEST_END = dt.time(17, 0)


def _t(s: str) -> dt.time:
    h, m = s.split(":")
    return dt.time(int(h), int(m))


def _hm(minutes_: int) -> str:
    return f"{minutes_ // 60:02d}:{minutes_ % 60:02d}"


def _mins(t: dt.time | str) -> int:
    t = _t(t) if isinstance(t, str) else t
    return t.hour * 60 + t.minute


def school_day(
    start: str = "08:00",
    period: int = 35,
    before_break: int = 3,
    break_minutes: int = 20,
    before_lunch: int = 3,
    lunch_minutes: int = 40,
    after_lunch: int = 3,
) -> Day:
    """A school day from its shape: periods P1, P2 … with a break and a lunch between them."""
    errors = []
    try:
        begin = _mins(start)
    except ValueError:
        begin = -1
    if not _mins("06:30") <= begin <= _mins("10:00"):
        errors.append({"field": "start", "message": "the day starts between 06:30 and 10:00"})
    if not 30 <= period <= 80:
        errors.append({"field": "period", "message": "a period is 30 to 80 minutes"})
    total = before_break + before_lunch + after_lunch
    if before_break < 1 or min(before_lunch, after_lunch) < 0 or not 4 <= total <= 12:
        errors.append({"field": "periods", "message": "4 to 12 teaching periods, at least one before the break"})
    if not 10 <= break_minutes <= 60 or not 20 <= lunch_minutes <= 90:
        errors.append({"field": "breaks", "message": "a break of 10 to 60 minutes and a lunch of 20 to 90 minutes"})
    if errors:
        raise HardValidation("TIM-DAY", "The school day is not valid", errors[0]["message"].capitalize() + ".", errors)
    out: list[tuple[str, str, str, bool]] = []
    now, n = begin, 0
    for count, pause, code in (
        (before_break, break_minutes, "BRK"),
        (before_lunch, lunch_minutes, "LUN"),
        (after_lunch, 0, ""),
    ):
        for _ in range(count):
            n += 1
            out.append((f"P{n}", _hm(now), _hm(now + period), True))
            now += period
        if pause and n < total:
            out.append((code, _hm(now), _hm(now + pause), False))
            now += pause
    if now > _mins(LATEST_END):
        raise HardValidation("TIM-DAY", "The school day is too long", f"It would end at {_hm(now)}, after 17:00.")
    return tuple(out)


def describe(day: Day) -> dict[str, Any]:
    """The shape of a school day, to fill the builder's form, with its end and teaching time."""
    teach = [b for b in day if b[3]]
    pauses = [b for b in day if not b[3]]
    counts, run = [], 0
    for b in day:
        if b[3]:
            run += 1
        else:
            counts.append(run)
            run = 0
    counts.append(run)
    counts += [0] * (3 - len(counts))
    brk = next((b for b in pauses if b[0] == "BRK"), None)
    lun = next((b for b in pauses if b[0] == "LUN"), None)
    return {
        "start": day[0][1],
        "end": day[-1][2],
        "period": _mins(teach[0][2]) - _mins(teach[0][1]) if teach else 0,
        "before_break": counts[0],
        "before_lunch": counts[1],
        "after_lunch": counts[2],
        "break_minutes": _mins(brk[2]) - _mins(brk[1]) if brk else 20,
        "lunch_minutes": _mins(lun[2]) - _mins(lun[1]) if lun else 40,
        "periods": len(teach),
        "teaching_minutes": sum(_mins(b[2]) - _mins(b[1]) for b in teach),
    }


def schedule(tt: Timetable | None) -> Day:
    """The school day a timetable was built with (the standard day for a timetable without one)."""
    if tt is None:
        return BELL
    rows = list(PeriodStructure.objects.filter(timetable_id=tt.id, cycle_day=1).order_by("starts_at"))
    if not rows:
        return BELL
    return tuple(
        (r.period_code, r.starts_at.strftime("%H:%M"), r.ends_at.strftime("%H:%M"), r.is_teaching) for r in rows
    )


def latest(institution_id: uuid.UUID) -> Timetable | None:
    tt: Timetable | None = Timetable.objects.filter(institution_id=institution_id).order_by("-version").first()
    return tt


def school_schedule(institution_id: uuid.UUID) -> Day:
    """The school's day: that of its timetable in force, else of its latest timetable, else the standard day."""
    return schedule(current(institution_id) or latest(institution_id))


def bell(tt: Timetable | None = None) -> dict[str, tuple[dt.time, dt.time]]:
    return {code: (_t(a), _t(b)) for code, a, b, _teach in schedule(tt)}


def minutes(period_code: str, tt: Timetable | None = None) -> int:
    a, b = bell(tt)[period_code]
    return _mins(b) - _mins(a)


def period_minutes(institution_id: uuid.UUID) -> int:
    """Length of the school's teaching period."""
    first = next(b for b in school_schedule(institution_id) if b[3])
    return _mins(first[2]) - _mins(first[1])


@dataclass
class _Need:
    plan: ClassSubjectPlan
    cls: ClassGroup
    staff_id: uuid.UUID
    periods: int


def _usable_rooms(scope_node_id: uuid.UUID) -> list[Any]:
    from syntegra.estate import services as estate
    from syntegra.operations.models import Room

    rooms = list(
        Room.objects.filter(scope_node_id=scope_node_id, status="active", room_type="classroom").order_by("code")
    )
    use = estate.room_usability([r.id for r in rooms])
    return [r for r in rooms if use.get(r.id) not in estate.UNSAFE_USABILITY]


def place(
    needs: list[_Need],
    rooms: list[uuid.UUID],
    home: dict[uuid.UUID, uuid.UUID | None],
    teaching: list[str] | None = None,
) -> tuple[list[tuple[_Need, int, str, uuid.UUID]], list[dict[str, Any]]]:
    """Greedy placement: the most constrained class-subjects first, each lesson on the day the class-subject has had
    fewest lessons, in the earliest period free for the class, the teacher and a room. Returns the placed lessons
    (need, day, period, room) and the unmet requirements."""
    busy_class: set[tuple[uuid.UUID, int, str]] = set()
    busy_staff: set[tuple[uuid.UUID, int, str]] = set()
    busy_room: set[tuple[uuid.UUID, int, str]] = set()
    load: dict[uuid.UUID, int] = {}
    for n in needs:
        load[n.staff_id] = load.get(n.staff_id, 0) + n.periods
    order = sorted(needs, key=lambda n: (-load[n.staff_id], -n.periods, n.cls.name, str(n.plan.id)))
    codes = teaching or TEACHING
    placed: list[tuple[_Need, int, str, uuid.UUID]] = []
    unmet: list[dict[str, Any]] = []
    for k, n in enumerate(order):
        per_day = dict.fromkeys(DAYS, 0)
        missing = 0
        for _ in range(n.periods):
            spot = None
            for day in sorted(DAYS, key=lambda d: (per_day[d], (d + k) % len(DAYS))):
                # rotate the starting period so one subject is not always first thing in the morning
                start = (k + day) % len(codes)
                for code in codes[start:] + codes[:start]:
                    if (n.cls.id, day, code) in busy_class or (n.staff_id, day, code) in busy_staff:
                        continue
                    pref = home.get(n.cls.id)
                    choices = ([pref] if pref in rooms else []) + [r for r in rooms if r != pref]
                    room = next((r for r in choices if (r, day, code) not in busy_room), None)
                    if room is not None:
                        spot = (day, code, room)
                        break
                if spot:
                    break
            if spot is None:
                missing += 1
                continue
            day, code, room = spot
            busy_class.add((n.cls.id, day, code))
            busy_staff.add((n.staff_id, day, code))
            busy_room.add((room, day, code))
            per_day[day] += 1
            placed.append((n, day, code, room))
        if missing:
            unmet.append({"class_subject_plan_id": str(n.plan.id), "class": n.cls.name, "missing_periods": missing})
    return placed, unmet


def build(institution_id: uuid.UUID, period_id: uuid.UUID, day: Day | None = None) -> Timetable:
    """Build and, when every mandatory period is placed, publish the school's timetable for the period, on the given
    school day or the day of the school's latest timetable."""
    from syntegra.institutions.models import Institution

    ctx = context.require()
    authz.require("timetable:manage", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    today = dt.date.today()
    classes = {
        c.id: c
        for c in ClassGroup.objects.filter(institution_id=inst.id, period_id=period_id, status="active").order_by(
            "name"
        )
    }
    plans = list(
        ClassSubjectPlan.objects.filter(class_group_id__in=list(classes), valid_from__lte=today).exclude(
            valid_to__lt=today
        )
    )
    tor = {
        a.class_subject_plan_id: a.staff_id
        for a in TeachingAssignment.objects.filter(
            class_subject_plan_id__in=[p.id for p in plans], role="teacher_of_record", valid_from__lte=today
        ).exclude(valid_to__lte=today)
    }
    needs, unmet = [], []
    for p in plans:
        if p.id not in tor:
            if p.is_mandatory:
                unmet.append(
                    {
                        "class_subject_plan_id": str(p.id),
                        "class": classes[p.class_group_id].name,
                        "missing_periods": p.periods_per_week or 0,
                        "reason": "no teacher of record",
                    }
                )
            continue
        needs.append(_Need(p, classes[p.class_group_id], tor[p.id], int(p.periods_per_week or 0)))
    rooms = [r.id for r in _usable_rooms(inst.scope_node_id)]
    if not rooms:
        raise HardValidation("TIM-NO-ROOMS", "No usable classroom", "Every classroom is missing or assessed unsafe.")
    day = day or school_schedule(inst.id)
    length = {code: _mins(b) - _mins(a) for code, a, b, _teach in day}
    placed, short = place(needs, rooms, {c.id: c.room_id for c in classes.values()}, [b[0] for b in day if b[3]])
    unmet += short
    with uow.command("ops", "timetable:manage", action="build", record_kind="timetable") as cmd:
        prior = list(
            Timetable.objects.using(cmd.alias).filter(institution_id=inst.id, period_id=period_id).order_by("-version")
        )
        tt = cmd.add(
            Timetable(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                period_id=period_id,
                version=(prior[0].version + 1) if prior else 1,
                cycle_weeks=1,
                sessions_per_day=1,
                solver_run={
                    "method": "greedy, most constrained first",
                    "constraints": ["class", "teacher", "room", "spread over the week"],
                    "lessons_placed": len(placed),
                },
                unmet_requirements=unmet or None,
                published_at=None if unmet else utcnow(),
                status="draft" if unmet else "published",
            )
        )
        for weekday in DAYS:
            for code, a, b, teach in day:
                cmd.add(
                    PeriodStructure(
                        timetable_id=tt.id,
                        structure_code=STRUCTURE,
                        cycle_day=weekday,
                        period_code=code,
                        starts_at=_t(a),
                        ends_at=_t(b),
                        is_teaching=teach,
                    )
                )
        for n, weekday, code, room in placed:
            TimetableLesson(
                timetable_id=tt.id,
                class_group_id=n.cls.id,
                class_subject_plan_id=n.plan.id,
                subject_id=n.plan.subject_id,
                staff_id=n.staff_id,
                room_id=room,
                cycle_day=weekday,
                period_code=code,
                duration_minutes=length[code],
                lesson_kind="lesson",
            ).save(using=cmd.alias)  # recorded in bulk: the audit event notes the count
        cmd.note("lessons", None, len(placed))
        if not unmet:
            for old in prior:
                if old.status == "published":
                    cmd.update(old, status="superseded")
        return tt


def current(institution_id: uuid.UUID) -> Timetable | None:
    """The school's published timetable in force."""
    tt: Timetable | None = (
        Timetable.objects.filter(institution_id=institution_id, status="published").order_by("-version").first()
    )
    return tt


def monday(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def week(
    institution_id: uuid.UUID,
    week_of: dt.date,
    *,
    class_subject_plan_id: uuid.UUID | None = None,
    staff_id: uuid.UUID | None = None,
) -> list[dict[str, Any]]:
    """The dated lessons of one week (Monday to Friday) from the published timetable, filtered to a class-subject or
    a teacher."""
    tt = current(institution_id)
    if tt is None:
        return []
    qs = TimetableLesson.objects.filter(timetable_id=tt.id)
    if class_subject_plan_id:
        qs = qs.filter(class_subject_plan_id=class_subject_plan_id)
    if staff_id:
        qs = qs.filter(staff_id=staff_id)
    times = bell(tt)
    start = monday(week_of)
    order = {c: i for i, c in enumerate(b[0] for b in schedule(tt))}
    out = []
    for ls in sorted(qs, key=lambda x: (x.cycle_day, order.get(x.period_code, 99))):
        on = start + dt.timedelta(days=ls.cycle_day - 1)
        a, b = times.get(ls.period_code, (dt.time(0), dt.time(0)))
        out.append(
            {
                "lesson_id": ls.id,
                "plan_id": ls.class_subject_plan_id,
                "class_id": ls.class_group_id,
                "staff_id": ls.staff_id,
                "room_id": ls.room_id,
                "day": DAYS.get(ls.cycle_day, str(ls.cycle_day)),
                "on": on,
                "period": ls.period_code,
                "starts": a,
                "ends": b,
                "minutes": ls.duration_minutes,
            }
        )
    return out


def _session_of(institution_id: uuid.UUID) -> uuid.UUID | None:
    """The session the school's active classes belong to."""
    counts: dict[uuid.UUID, int] = {}
    for pid in ClassGroup.objects.filter(institution_id=institution_id, status="active").values_list(
        "period_id", flat=True
    ):
        counts[pid] = counts.get(pid, 0) + 1
    return max(counts, key=lambda k: counts[k]) if counts else None


def builder(institution_id: uuid.UUID) -> dict[str, Any]:
    """TIM-01: the school's day, how many periods its classes need against the week's teaching periods, and the
    timetable versions."""
    from syntegra.institutions.models import Institution

    ctx = context.require()
    authz.require("timetable:view", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    today = dt.date.today()
    day = school_schedule(inst.id)
    shape = describe(day)
    classes = {c.id: c for c in ClassGroup.objects.filter(institution_id=inst.id, status="active").order_by("name")}
    need: dict[uuid.UUID, int] = dict.fromkeys(classes, 0)
    for p in ClassSubjectPlan.objects.filter(class_group_id__in=list(classes), valid_from__lte=today).exclude(
        valid_to__lt=today
    ):
        need[p.class_group_id] += int(p.periods_per_week or 0)
    slots = shape["periods"] * len(DAYS)
    versions = list(Timetable.objects.filter(institution_id=inst.id).order_by("-version")[:8])
    lessons = {v.id: n for v, n in ((v, TimetableLesson.objects.filter(timetable_id=v.id).count()) for v in versions)}
    return {
        "institution": {"id": inst.id, "name": inst.name},
        "day": [{"code": c, "starts": a, "ends": b, "teaching": t} for c, a, b, t in day],
        "shape": shape,
        "slots": slots,
        "classes": [{"name": c.name, "periods": need[c.id], "fits": need[c.id] <= slots} for c in classes.values()],
        "most": max(need.values()) if need else 0,
        "versions": [
            {
                "version": v.version,
                "status": v.status,
                "published_at": v.published_at,
                "created_at": v.created_at,
                "lessons": lessons[v.id],
                "unmet": v.unmet_requirements or [],
                "day": describe(schedule(v)),
            }
            for v in versions
        ],
        "can_build": ctx.has("timetable:manage"),
    }


def rebuild(institution_id: uuid.UUID, day: Day) -> Timetable:
    """Build a new version of the school's timetable on the given school day."""
    period_id = _session_of(institution_id)
    if period_id is None:
        raise HardValidation("TIM-NO-CLASSES", "The school has no active classes", "")
    return build(institution_id, period_id, day)
