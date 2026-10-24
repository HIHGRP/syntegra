"""Rooms and bookings with booking permissions (MFS TIM-04).

Teachers book the school's specialist and shared rooms — laboratories, workshops, the ICT suite, the library, the hall,
sports areas and free classrooms — for a purpose, a time and a number of people. Every request is checked: the room
is bookable, not assessed unsafe and big enough; the time is in the future, within 07:00–18:00 on a school day or a
Saturday and at most four hours; and the room is free — no timetabled lesson in it and no other booking.

Whether a request is confirmed at once or waits for the head depends on who asks and for what:

| Rule | Outcome |
|---|---|
| The head (or facilities officer) books | Confirmed |
| Hall or sports area | Waits for the head's approval |
| Laboratory, workshop or skills lab, by a teacher of a subject that uses it | Confirmed |
| Laboratory, workshop or skills lab, by any other teacher | Waits for approval |
| Classroom, ICT suite or library | Confirmed |
| Longer than two hours or more than 14 days ahead (any room) | Waits for approval |

The decision and its reason are shown to the teacher. The head approves or declines what waits (the checks run again
on approval); the person who booked, or the head, can cancel a booking that has not started.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.timetable import services as tts
from syntegra.timetable.models import RoomBooking, TimetableLesson

BOOKABLE = {
    "laboratory": "Laboratory",
    "workshop": "Workshop",
    "skills_lab": "Skills lab",
    "ict_suite": "ICT suite",
    "library": "Library",
    "hall": "Hall",
    "sports": "Sports area",
    "classroom": "Classroom",
}
APPROVAL_ALWAYS = {"hall", "sports"}
SPECIALIST = {"laboratory", "workshop", "skills_lab"}
# subjects whose teachers book a specialist room without approval
USES = {
    "laboratory": ("Biology", "Chemistry", "Physics", "Basic Science", "Agricultural Science"),
    "workshop": ("Technical Drawing", "Basic Technology", "Woodwork", "Metalwork"),
    "skills_lab": ("Home Economics", "Food and Nutrition", "Catering"),
}
OPEN, CLOSE = dt.time(7, 0), dt.time(18, 0)
MAX_HOURS, DIRECT_HOURS, DIRECT_DAYS, MAX_DAYS = 4, 2, 14, 60
LIVE = ("requested", "confirmed")


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.TIME_ZONE)


def schools() -> list[Any]:
    """The schools in the user's scope that have rooms."""
    from syntegra.institutions.models import Institution

    ctx = context.require()
    qs = Institution.objects.filter(status="active")
    if ctx.scope_ids is not None:
        qs = qs.filter(scope_node_id__in=list(ctx.scope_ids))
    return list(qs.order_by("name")[:200])


def _rooms(scope_node_id: uuid.UUID) -> list[Any]:
    from syntegra.estate import services as estate
    from syntegra.operations.models import Room

    rooms = list(
        Room.objects.filter(scope_node_id=scope_node_id, status="active", room_type__in=list(BOOKABLE)).order_by(
            "room_type", "code"
        )
    )
    use = estate.room_usability([r.id for r in rooms])
    for r in rooms:
        r.usability = use.get(r.id)
        r.unsafe = use.get(r.id) in estate.UNSAFE_USABILITY
    return rooms


def _subjects_taught(staff_id: uuid.UUID | None, on: dt.date) -> set[str]:
    from syntegra.academic.models import ClassSubjectPlan, Subject, TeachingAssignment
    from syntegra.academic.teaching import current

    if staff_id is None:
        return set()
    plans = current(TeachingAssignment.objects.filter(staff_id=staff_id), on).values_list(
        "class_subject_plan_id", flat=True
    )
    subj = ClassSubjectPlan.objects.filter(id__in=list(plans)).values_list("subject_id", flat=True)
    return set(Subject.objects.filter(id__in=list(subj)).values_list("name", flat=True))


def lesson_clash(room_id: uuid.UUID, institution_id: uuid.UUID, starts: dt.datetime, ends: dt.datetime) -> str | None:
    """The timetabled lesson in the room during the time, if any (weekdays of the published timetable)."""
    tt = tts.current(institution_id)
    if tt is None:
        return None
    tz = _tz()
    a, b = starts.astimezone(tz), ends.astimezone(tz)
    if a.isoweekday() not in tts.DAYS:
        return None
    times = tts.bell(tt)
    for ls in TimetableLesson.objects.filter(timetable_id=tt.id, room_id=room_id, cycle_day=a.isoweekday()):
        p0, p1 = times.get(ls.period_code, (None, None))
        if p0 is None or p1 is None:
            continue
        if p0 < b.time() and a.time() < p1:
            return f"a timetabled lesson ({ls.period_code}, {p0:%H:%M}–{p1:%H:%M})"
    return None


def decide(room: Any, staff_id: uuid.UUID | None, starts: dt.datetime, ends: dt.datetime) -> tuple[str, str]:
    """Confirmed at once, or waiting for approval — with the reason."""
    ctx = context.require()
    kind = BOOKABLE.get(room.room_type, room.room_type)
    if ctx.has("room:approve"):
        return "confirmed", "Confirmed: you manage room bookings."
    if room.room_type in APPROVAL_ALWAYS:
        return "requested", f"Waits for the head's approval: the {kind.lower()} is booked only with approval."
    if ends - starts > dt.timedelta(hours=DIRECT_HOURS):
        return "requested", f"Waits for the head's approval: longer than {DIRECT_HOURS} hours."
    if starts.date() - dt.date.today() > dt.timedelta(days=DIRECT_DAYS):
        return "requested", f"Waits for the head's approval: more than {DIRECT_DAYS} days ahead."
    if room.room_type in SPECIALIST:
        mine = sorted(_subjects_taught(staff_id, starts.date()) & set(USES.get(room.room_type, ())))
        if not mine:
            return "requested", f"Waits for the head's approval: you teach no subject that uses the {kind.lower()}."
        return "confirmed", f"Confirmed: you teach {', '.join(mine)}, which uses the {kind.lower()}."
    return "confirmed", f"Confirmed: the {kind.lower()} is free."


def _check(room: Any, institution_id: uuid.UUID, starts: dt.datetime, ends: dt.datetime, people: int, *,
           ignore: uuid.UUID | None = None, alias: str | None = None) -> None:  # fmt: skip
    if room.room_type not in BOOKABLE:
        raise HardValidation("ROOM-TYPE", "This room cannot be booked", "Choose a teaching or shared room.")
    if room.unsafe:
        raise HardValidation("ROOM-UNSAFE", "This room is assessed unsafe", "It cannot be booked until repaired.")
    if people < 1 or people > room.capacity:
        raise HardValidation("ROOM-CAPACITY", "Too many people", f"{room.code} holds {room.capacity}.")
    tz = _tz()
    a, b = starts.astimezone(tz), ends.astimezone(tz)
    now = dt.datetime.now(tz)
    if a <= now:
        raise HardValidation("ROOM-TIME", "The time has passed", "Book a time in the future.")
    if b <= a or a.date() != b.date() or b - a > dt.timedelta(hours=MAX_HOURS) or b - a < dt.timedelta(minutes=15):
        raise HardValidation("ROOM-TIME", "Check the times", f"15 minutes to {MAX_HOURS} hours on one day.")
    if a.time() < OPEN or b.time() > CLOSE or a.isoweekday() == 7:
        raise HardValidation("ROOM-TIME", "Outside booking hours", "Monday to Saturday, 07:00 to 18:00.")
    if (a.date() - now.date()).days > MAX_DAYS:
        raise HardValidation("ROOM-TIME", "Too far ahead", f"Book at most {MAX_DAYS} days ahead.")
    lesson = lesson_clash(room.id, institution_id, a, b)
    if lesson:
        raise ConflictError("ROOM-CLASH", "The room is in use", f"{room.code} has {lesson} then.")
    qs = RoomBooking.objects.using(alias) if alias else RoomBooking.objects
    other = (
        qs.filter(room_id=room.id, status__in=LIVE, starts_at__lt=b, ends_at__gt=a).exclude(pk=ignore).first()
        if ignore
        else qs.filter(room_id=room.id, status__in=LIVE, starts_at__lt=b, ends_at__gt=a).first()
    )
    if other is not None:
        o0, o1 = other.starts_at.astimezone(tz), other.ends_at.astimezone(tz)
        raise ConflictError(
            "ROOM-CLASH",
            "The room is already booked",
            f"{room.code} is booked {o0:%H:%M}–{o1:%H:%M} ({other.purpose}).",
        )


def _room(room_id: uuid.UUID) -> tuple[Any, Any]:
    from syntegra.institutions.models import Institution
    from syntegra.operations.models import Room

    r = Room.objects.filter(pk=room_id).first()
    if r is None:
        raise NotFound("room", room_id)
    authz.require_scope(r.scope_node_id)
    inst = Institution.objects.filter(scope_node_id=r.scope_node_id).first()
    if inst is None:
        raise NotFound("school of room", room_id)
    room = next((x for x in _rooms(r.scope_node_id) if x.id == r.id), None)
    if room is None:
        raise HardValidation("ROOM-TYPE", "This room cannot be booked", "Choose a teaching or shared room.")
    return room, inst


def book(room_id: uuid.UUID, on: dt.date, start: dt.time, end: dt.time, purpose: str, people: int) -> dict[str, Any]:
    """Ask for a room; confirmed at once or left waiting for approval by the booking rules."""
    from syntegra.curriculum.lessons import my_staff_id

    ctx = context.require()
    authz.require("room:book", ctx)
    purpose = " ".join((purpose or "").split())
    if len(purpose) < 5:
        raise HardValidation("ROOM-PURPOSE", "Say what the room is for", "e.g. SS 2 Chemistry titration practical")
    room, inst = _room(room_id)
    tz = _tz()
    starts, ends = dt.datetime.combine(on, start, tzinfo=tz), dt.datetime.combine(on, end, tzinfo=tz)
    status, reason = decide(room, my_staff_id(ctx), starts, ends)
    with uow.command("ops", "room:book", action="book_room", record_kind="room_booking") as cmd:
        _check(room, inst.id, starts, ends, people, alias=cmd.alias)
        b = cmd.add(
            RoomBooking(
                scope_node_id=room.scope_node_id,
                room_id=room.id,
                booked_by=ctx.actor_id,
                purpose=f"{purpose[:270]} — {people} people",
                starts_at=starts,
                ends_at=ends,
                approved_by=ctx.actor_id if status == "confirmed" else None,
                status=status,
            )
        )
        cmd.record_id = b.id
        return {"booking": b, "status": status, "reason": reason}


def decide_request(booking_id: uuid.UUID, approve: bool) -> RoomBooking:
    """The head approves (the checks run again) or declines a booking that waits."""
    ctx = context.require()
    authz.require("room:approve", ctx)
    with uow.command("ops", "room:approve", action="decide_booking", record_kind="room_booking") as cmd:
        b = cmd.lock(RoomBooking, booking_id)
        if b.status != "requested":
            raise ConflictError("ROOM-DECIDED", "Already decided", f"The booking is {b.status}.")
        if approve:
            room, inst = _room(b.room_id)
            _check(room, inst.id, b.starts_at, b.ends_at, 1, ignore=b.id, alias=cmd.alias)  # numbers checked on request
        return cmd.update(b, status="confirmed" if approve else "declined", approved_by=ctx.actor_id)


def cancel(booking_id: uuid.UUID) -> RoomBooking:
    ctx = context.require()
    with uow.command("ops", "room:book", action="cancel_booking", record_kind="room_booking") as cmd:
        b = cmd.lock(RoomBooking, booking_id)
        if b.booked_by != ctx.actor_id and not ctx.has("room:approve"):
            raise Forbidden("Only the person who booked, or the head, can cancel a booking.")
        if b.status not in LIVE:
            raise ConflictError("ROOM-GONE", "Not a live booking", f"The booking is {b.status}.")
        if b.starts_at <= dt.datetime.now(_tz()):
            raise ConflictError("ROOM-STARTED", "The booking has started", "Past bookings are kept as they were.")
        return cmd.update(b, status="cancelled")


def overview(institution_id: uuid.UUID, on: dt.date) -> dict[str, Any]:
    """The school's bookable rooms, the week's bookings and the requests waiting for approval."""
    from syntegra.iam.models import AppUser
    from syntegra.institutions.models import Institution

    ctx = context.require()
    authz.require("room:book", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    rooms = _rooms(inst.scope_node_id)
    tz = _tz()
    monday = tts.monday(on)
    a = dt.datetime.combine(monday, dt.time(0), tzinfo=tz)
    b = a + dt.timedelta(days=7)
    bookings = list(
        RoomBooking.objects.filter(room_id__in=[r.id for r in rooms], starts_at__lt=b, ends_at__gt=a)
        .exclude(status="cancelled")
        .order_by("starts_at")
    )
    now = dt.datetime.now(tz)
    waiting = list(
        RoomBooking.objects.filter(room_id__in=[r.id for r in rooms], status="requested", ends_at__gt=now).order_by(
            "starts_at"
        )
    )
    users = dict(
        AppUser.objects.filter(id__in={x.booked_by for x in bookings + waiting}).values_list("id", "display_name")
    )
    by_room = {r.id: r for r in rooms}

    def row(x: RoomBooking) -> dict[str, Any]:
        r = by_room.get(x.room_id)
        s0, s1 = x.starts_at.astimezone(tz), x.ends_at.astimezone(tz)
        return {
            "id": x.id,
            "room": f"{r.code} {r.name or ''}".strip() if r else "?",
            "kind": BOOKABLE.get(r.room_type, "") if r else "",
            "on": s0.date(),
            "starts": s0.time(),
            "ends": s1.time(),
            "purpose": x.purpose,
            "by": users.get(x.booked_by, "?"),
            "mine": x.booked_by == ctx.actor_id,
            "status": x.status,
            "can_cancel": x.status in LIVE and s0 > now and (x.booked_by == ctx.actor_id or ctx.has("room:approve")),
        }

    return {
        "institution": {"id": inst.id, "name": inst.name},
        "week": {"monday": monday, "saturday": monday + dt.timedelta(days=5)},
        "rooms": [
            {
                "id": r.id,
                "code": r.code,
                "name": r.name,
                "kind": BOOKABLE.get(r.room_type, r.room_type),
                "type": r.room_type,
                "capacity": r.capacity,
                "unsafe": r.unsafe,
                "rule": "approval"
                if r.room_type in APPROVAL_ALWAYS
                else "subject"
                if r.room_type in SPECIALIST
                else "direct",
                "uses": ", ".join(USES.get(r.room_type, ())),
            }
            for r in rooms
        ],
        "bookings": [row(x) for x in bookings],
        "waiting": [row(x) for x in waiting],
        "can_approve": ctx.has("room:approve"),
    }
