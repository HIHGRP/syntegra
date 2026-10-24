"""Parents' meetings (MFS PTM-101; CR-009 phase 4).

The head sets up a meeting — one or more evenings, the classes it is for, the length of a slot, the gap a parent
needs to walk from one teacher to the next, whether parents may meet in person or by video, and when booking opens
and closes. Every teacher of those classes (form teachers and the teachers of record for each subject) then has a
column of slots.

A parent books a slot with each of their child's teachers they want to see. A booking is refused when the slot is
taken, when the parent already has another meeting that overlaps it, or that ends too close to it to get to the
next teacher (the gap does not apply between two meetings with the same teacher), when the parent already has a
meeting with that teacher about that child, or when booking is closed. Bookings are made one at a time under a lock
on the meeting, so two parents racing for the last slot cannot both get it. The school office can book for a parent
who has no account (and after booking has closed, until the meeting starts).

On the evening each teacher has their list. They record who came and a short note, which stays on the booking.
Video meetings carry no link here: no video provider is connected in this release, and the page says the school
sends the link.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.families import portal
from syntegra.forms.models import MeetingBooking, MeetingEvent

MODES = {"in_person": "In person", "video": "Video call"}
SLOT_MINUTES = (5, 30)
GAP_MINUTES = (0, 15)
MAX_DAYS = 3
LAST_FINISH = dt.time(20, 0)


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.TIME_ZONE)


def _institution(institution_id: uuid.UUID) -> Any:
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _event(event_id: uuid.UUID) -> MeetingEvent:
    ev: MeetingEvent | None = MeetingEvent.objects.in_scope().filter(pk=event_id).first()
    if ev is None:
        raise NotFound("meeting_event", event_id)
    return ev


def _hm(value: str, what: str) -> dt.time:
    try:
        return dt.time.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise HardValidation("PTM-TIME", f"Give the {what} as a time", "For example 16:00.") from exc


def _days(ev: MeetingEvent) -> list[tuple[dt.date, dt.time, dt.time]]:
    return [
        (dt.date.fromisoformat(d["date"]), dt.time.fromisoformat(d["from"]), dt.time.fromisoformat(d["to"]))
        for d in ev.days
    ]


def slot_starts(ev: MeetingEvent) -> list[dt.datetime]:
    tz = _tz()
    out = []
    step = dt.timedelta(minutes=ev.slot_minutes)
    for day, a, b in _days(ev):
        t = dt.datetime.combine(day, a, tzinfo=tz)
        end = dt.datetime.combine(day, b, tzinfo=tz)
        while t + step <= end:
            out.append(t)
            t += step
    return out


def create(
    institution_id: uuid.UUID,
    *,
    title: str,
    class_ids: list[uuid.UUID],
    days: list[tuple[dt.date, str, str]],
    slot_minutes: int,
    gap_minutes: int,
    modes: list[str],
    opens_on: dt.date,
    closes_on: dt.date,
) -> MeetingEvent:
    """Set up a parents' meeting. Booking opens at the start of ``opens_on`` and closes at the end of ``closes_on``,
    which must be before the first evening."""
    from syntegra.academic.models import ClassGroup

    inst = _institution(institution_id)
    title = (title or "").strip()
    if len(title) < 4:
        raise HardValidation("PTM-TITLE", "Give the meeting a title", "For example: SS 2 parents' evening.")
    classes = list(ClassGroup.objects.in_scope().filter(institution_id=inst.id, id__in=class_ids, status="active"))
    if not classes or len(classes) != len(set(class_ids)):
        raise HardValidation("PTM-CLASSES", "Choose the classes", "Tick the classes whose parents are invited.")
    if not days or len(days) > MAX_DAYS:
        raise HardValidation("PTM-DAYS", "Give the evenings", f"One to {MAX_DAYS} evenings.")
    if not (SLOT_MINUTES[0] <= slot_minutes <= SLOT_MINUTES[1]):
        raise HardValidation("PTM-SLOT", "Slot length", f"Between {SLOT_MINUTES[0]} and {SLOT_MINUTES[1]} minutes.")
    if not (GAP_MINUTES[0] <= gap_minutes <= GAP_MINUTES[1]):
        raise HardValidation(
            "PTM-GAP", "Gap between teachers", f"Between {GAP_MINUTES[0]} and {GAP_MINUTES[1]} minutes."
        )
    modes = [m for m in modes if m in MODES]
    if not modes:
        raise HardValidation("PTM-MODES", "How parents meet", "In person, by video, or both.")
    today = dt.date.today()
    rows = []
    for day, a, b in sorted(days):
        start, end = _hm(a, "start"), _hm(b, "finish")
        if day <= today:
            raise HardValidation("PTM-DAYS", "The evening has to be in the future", f"{day:%d %B %Y} has come.")
        if day.weekday() > 5:
            raise HardValidation("PTM-DAYS", "Not on a Sunday", f"{day:%d %B %Y} is a Sunday.")
        if end <= start or end > LAST_FINISH:
            raise HardValidation(
                "PTM-DAYS", "Check the times", f"On {day:%d %B} the finish must be after the start and by 20:00."
            )
        if (dt.datetime.combine(day, end) - dt.datetime.combine(day, start)) < dt.timedelta(minutes=slot_minutes):
            raise HardValidation("PTM-DAYS", "Too short", f"On {day:%d %B} there is not room for one slot.")
        rows.append({"date": day.isoformat(), "from": start.strftime("%H:%M"), "to": end.strftime("%H:%M")})
    if len({r["date"] for r in rows}) != len(rows):
        raise HardValidation("PTM-DAYS", "An evening is listed twice", "Give each date once.")
    first = dt.date.fromisoformat(rows[0]["date"])
    if not (today <= opens_on <= closes_on < first):
        raise HardValidation(
            "PTM-WINDOW",
            "Check when booking opens and closes",
            "Booking opens today or later and closes before the first evening.",
        )
    tz = _tz()
    with uow.command("ops", "meeting:manage", action="create_meeting", record_kind="meeting_event") as cmd:
        return cmd.add(
            MeetingEvent(
                scope_node_id=inst.scope_node_id,
                title=title,
                class_group_ids=[str(c.id) for c in classes],
                days=rows,
                slot_minutes=slot_minutes,
                travel_gap_minutes=gap_minutes,
                modes=modes,
                booking_opens_at=dt.datetime.combine(opens_on, dt.time(0, 0), tzinfo=tz),
                booking_closes_at=dt.datetime.combine(closes_on, dt.time(23, 59), tzinfo=tz),
                status="active",
            )
        )


def _classes(ev: MeetingEvent) -> list[Any]:
    from syntegra.academic.models import ClassGroup

    return list(ClassGroup.objects.filter(id__in=ev.class_group_ids).order_by("name"))


def _teachers(ev: MeetingEvent) -> dict[uuid.UUID, dict[str, Any]]:
    """Every teacher of the meeting's classes, with what they teach each class."""
    from syntegra.academic import teaching
    from syntegra.people.models import Staff

    out: dict[uuid.UUID, dict[str, Any]] = {}
    for cls in _classes(ev):
        for sid, roles in teaching.teachers_of_class(cls.id).items():
            t = out.setdefault(sid, {"staff_id": sid, "classes": {}})
            t["classes"][cls.id] = roles
    for s in Staff.objects.filter(id__in=list(out)):
        out[s.id]["name"] = f"{s.given_name} {s.family_name}"
    return {k: v for k, v in out.items() if "name" in v}


def _bookings(ev: MeetingEvent) -> list[MeetingBooking]:
    return list(MeetingBooking.objects.filter(meeting_event_id=ev.id, status="confirmed").order_by("starts_at"))


def _is_open(ev: MeetingEvent, now: dt.datetime) -> bool:
    return ev.status == "active" and ev.booking_opens_at <= now <= ev.booking_closes_at


def events(institution_id: uuid.UUID) -> list[dict[str, Any]]:
    inst = _institution(institution_id)
    now = dt.datetime.now(_tz())
    rows = []
    for ev in MeetingEvent.objects.in_scope().filter(scope_node_id=inst.scope_node_id).order_by("-created_at"):
        n = MeetingBooking.objects.filter(meeting_event_id=ev.id, status="confirmed").count()
        days = _days(ev)
        rows.append(
            {
                "id": ev.id,
                "title": ev.title,
                "days": days,
                "classes": [c.name for c in _classes(ev)],
                "bookings": n,
                "open": _is_open(ev, now),
                "past": days[-1][0] < now.date(),
                "opens": ev.booking_opens_at,
                "closes": ev.booking_closes_at,
                "status": ev.status,
            }
        )
    return rows


def board(event_id: uuid.UUID) -> dict[str, Any]:
    """The head's view: each teacher's column of slots with who is booked."""
    from syntegra.learners.models import Learner

    authz.require("meeting:manage")
    ev = _event(event_id)
    teachers = _teachers(ev)
    books = _bookings(ev)
    learners = {lr.id: f"{lr.legal_given_name} {lr.legal_family_name}"
                for lr in Learner.objects.filter(id__in={b.learner_id for b in books})}  # fmt: skip
    by = {(b.staff_id, b.starts_at): b for b in books}
    slots = slot_starts(ev)
    columns = []
    for t in sorted(teachers.values(), key=lambda x: x["name"]):
        booked = [by.get((t["staff_id"], s)) for s in slots]
        columns.append(
            {
                "name": t["name"],
                "teaches": sorted({r for rs in t["classes"].values() for r in rs}),
                "booked": sum(1 for b in booked if b),
                "cells": [
                    {"at": s, "learner": learners.get(b.learner_id) if b else None, "mode": b.mode if b else None}
                    for s, b in zip(slots, booked, strict=True)
                ],
            }
        )
    return {"event": _event_row(ev), "slots": slots, "columns": columns, "bookings": len(books)}


def _event_row(ev: MeetingEvent) -> dict[str, Any]:
    now = dt.datetime.now(_tz())
    return {
        "id": ev.id,
        "title": ev.title,
        "days": _days(ev),
        "slot_minutes": ev.slot_minutes,
        "gap": ev.travel_gap_minutes,
        "modes": [(m, MODES[m]) for m in ev.modes if m in MODES],
        "opens": ev.booking_opens_at,
        "closes": ev.booking_closes_at,
        "open": _is_open(ev, now),
        "classes": [c.name for c in _classes(ev)],
    }


# --------------------------------------------------------------------------- parents
def _guardian_bookings(ev: MeetingEvent, guardian_id: uuid.UUID) -> list[MeetingBooking]:
    return [b for b in _bookings(ev) if b.guardian_id == guardian_id]


def for_parent(event_id: uuid.UUID) -> dict[str, Any]:
    """What a parent sees: for each child invited, their teachers with the free slots, and the parent's bookings."""
    g = portal.guardian()
    if g is None:
        raise Forbidden("This page is for parents booking their meetings.", code="FAM-OWN")
    ev = _event(event_id)
    teachers = _teachers(ev)
    books = _bookings(ev)
    mine = [b for b in books if b.guardian_id == g.id]
    taken = {(b.staff_id, b.starts_at) for b in books}
    slots = slot_starts(ev)
    kids = [c for c in portal.children() if str(c["class_id"]) in ev.class_group_ids]
    out_children = []
    for c in kids:
        rows = []
        for t in sorted(teachers.values(), key=lambda x: x["name"]):
            roles = t["classes"].get(c["class_id"])
            if not roles:
                continue
            booked = next((b for b in mine if b.staff_id == t["staff_id"] and b.learner_id == c["id"]), None)
            free = [s for s in slots if (t["staff_id"], s) not in taken and not _clashes(ev, mine, t["staff_id"], s)]
            rows.append({"staff_id": t["staff_id"], "name": t["name"], "roles": roles, "booking": booked,
                         "free": free})  # fmt: skip
        out_children.append({**c, "teachers": rows})
    names = {t["staff_id"]: t["name"] for t in teachers.values()}
    kid_names = {c["id"]: c["given"] for c in kids}
    return {
        "event": _event_row(ev),
        "children": out_children,
        "mine": [
            {
                "id": b.id,
                "at": b.starts_at,
                "teacher": names.get(b.staff_id, "Teacher"),
                "child": kid_names.get(b.learner_id, ""),
                "mode": MODES.get(b.mode, b.mode),
                "interpreter": b.interpreter_language,
            }
            for b in mine
        ],
    }


def _clashes(ev: MeetingEvent, mine: list[MeetingBooking], staff_id: uuid.UUID, at: dt.datetime) -> str | None:
    """Why the parent cannot take this slot given their other bookings, or None."""
    slot = dt.timedelta(minutes=ev.slot_minutes)
    gap = dt.timedelta(minutes=ev.travel_gap_minutes)
    for b in mine:
        if b.starts_at == at:
            return f"you already have a meeting at {at:%H:%M}"
        if b.staff_id == staff_id:
            continue
        if at < b.starts_at + slot + gap and b.starts_at < at + slot + gap:
            return f"it leaves no time to get from your {b.starts_at:%H:%M} meeting (allow {ev.travel_gap_minutes} min)"
    return None


def book(
    event_id: uuid.UUID,
    learner_id: uuid.UUID,
    staff_id: uuid.UUID,
    starts_at: dt.datetime,
    mode: str = "in_person",
    interpreter_language: str | None = None,
    guardian_id: uuid.UUID | None = None,
) -> MeetingBooking:
    """Book a slot: a parent for their own child, or the school office (``meeting:manage``) for a parent."""
    from syntegra.academic.models import ClassMembership

    ctx = context.require()
    g = portal.guardian()
    office = g is None
    if office:
        authz.require("meeting:manage", ctx)
        if guardian_id is None:
            raise HardValidation("PTM-PARENT", "Choose the parent", "Pick the parent the meeting is for.")
        if not any(p["guardian_id"] == guardian_id for p in portal.parents_of([learner_id]).get(learner_id, [])):
            raise HardValidation("PTM-PARENT", "Not this learner's parent", "Choose one of the learner's parents.")
    else:
        authz.require("meeting:book", ctx)
        portal.require_child(learner_id)
        guardian_id = g.id  # type: ignore[union-attr]
    if mode not in MODES:
        raise HardValidation("PTM-MODE", "Choose how you will meet", "In person or by video.")
    lang = (interpreter_language or "").strip() or None
    tz = _tz()
    at = starts_at.astimezone(tz)
    with uow.command("ops", None, action="book_meeting", record_kind="meeting_booking") as cmd:
        ev = cmd.lock(MeetingEvent, event_id)
        now = dt.datetime.now(tz)
        first = slot_starts(ev)[0] if slot_starts(ev) else now
        if ev.status != "active":
            raise ConflictError("PTM-CLOSED", "This meeting is not taking bookings", "Ask the school office.")
        if not office and not _is_open(ev, now):
            when = "has not opened yet" if now < ev.booking_opens_at else "has closed"
            raise ConflictError("PTM-CLOSED", f"Booking {when}", "Ask the school office to book for you.")
        if office and now >= first:
            raise ConflictError("PTM-CLOSED", "The meeting has started", "Bookings are made before the first slot.")
        if mode not in ev.modes:
            raise HardValidation("PTM-MODE", f"{MODES[mode]} is not offered", "Choose another way to meet.")
        cls = (
            ClassMembership.objects.filter(learner_id=learner_id, is_arm=True, valid_to__isnull=True)
            .values_list("class_group_id", flat=True)
            .first()
        )
        if cls is None or str(cls) not in ev.class_group_ids:
            raise HardValidation("PTM-CLASS", "This meeting is not for the learner's class", "Choose another meeting.")
        teacher = _teachers(ev).get(staff_id)
        if teacher is None or cls not in teacher["classes"]:
            raise HardValidation("PTM-TEACHER", "Not one of the learner's teachers", "Choose a teacher from the list.")
        if at not in slot_starts(ev):
            raise HardValidation("PTM-SLOT", "Choose a slot from the list", "That time is not one of the slots.")
        books = _bookings(ev)
        if any(b.staff_id == staff_id and b.starts_at == at for b in books):
            raise ConflictError("PTM-TAKEN", "That slot has just been taken", "Choose another time.")
        mine = [b for b in books if b.guardian_id == guardian_id]
        if any(b.staff_id == staff_id and b.learner_id == learner_id for b in mine):
            raise ConflictError(
                "PTM-TWICE", f"You already have a meeting with {teacher['name']}", "Cancel it first to change the time."
            )
        why = _clashes(ev, mine, staff_id, at)
        if why:
            raise ConflictError("PTM-CLASH", "That time does not work", f"The slot is free, but {why}.")
        return cmd.add(
            MeetingBooking(
                meeting_event_id=ev.id,
                staff_id=staff_id,
                guardian_id=guardian_id,
                learner_id=learner_id,
                starts_at=at,
                mode=mode,
                interpreter_language=lang,
                recording_consent_all=False,
                status="confirmed",
            )
        )


def cancel(booking_id: uuid.UUID) -> None:
    b = MeetingBooking.objects.filter(pk=booking_id, status="confirmed").first()
    if b is None:
        raise NotFound("meeting_booking", booking_id)
    ev = _event(b.meeting_event_id)
    g = portal.guardian()
    if g is not None:
        if b.guardian_id != g.id:
            raise NotFound("meeting_booking", booking_id)
    else:
        authz.require("meeting:manage")
    if b.starts_at <= dt.datetime.now(_tz()):
        raise ConflictError("PTM-PAST", "The meeting time has passed", "It can no longer be cancelled.")
    with uow.command("ops", None, action="cancel_meeting", record_kind="meeting_booking") as cmd:
        cmd.lock(MeetingEvent, ev.id)
        cmd.update(b, status="cancelled")


# --------------------------------------------------------------------------- teachers
def _my_staff_id() -> uuid.UUID | None:
    from syntegra.iam.models import AppUser

    ctx = context.require()
    u = AppUser.objects.filter(pk=ctx.actor_id).first()
    return u.person_id if u is not None and u.person_kind == "staff" else None


def my_list(event_id: uuid.UUID) -> dict[str, Any]:
    """A teacher's appointments for the meeting, in time order, with the parent and the child."""
    from syntegra.families.models import Guardian
    from syntegra.learners.models import Learner

    authz.require("meeting:attend")
    ev = _event(event_id)
    me = _my_staff_id()
    books = list(
        MeetingBooking.objects.filter(meeting_event_id=ev.id, staff_id=me)
        .exclude(status__in=("cancelled", "declined"))
        .order_by("starts_at")
    )
    learners = {lr.id: lr for lr in Learner.objects.filter(id__in={b.learner_id for b in books})}
    parents = {g.id: portal.guardian_name(g) for g in Guardian.objects.filter(id__in={b.guardian_id for b in books})}
    return {
        "event": _event_row(ev),
        "is_teacher": me in _teachers(ev),
        "appointments": [
            {
                "id": b.id,
                "at": b.starts_at,
                "parent": parents.get(b.guardian_id, "Parent"),
                "learner": (
                    f"{learners[b.learner_id].legal_given_name} {learners[b.learner_id].legal_family_name}"
                    if b.learner_id in learners
                    else "Learner"
                ),
                "learner_id": b.learner_id,
                "mode": MODES.get(b.mode, b.mode),
                "interpreter": b.interpreter_language,
                "attended": b.attended,
                "note": b.note,
                "status": b.status,
            }
            for b in books
        ],
    }


def record(booking_id: uuid.UUID, attended: bool, note: str | None) -> MeetingBooking:
    """The teacher records whether the parent came and a short note."""
    authz.require("meeting:attend")
    b = MeetingBooking.objects.filter(pk=booking_id).exclude(status__in=("cancelled", "declined")).first()
    if b is None:
        raise NotFound("meeting_booking", booking_id)
    _event(b.meeting_event_id)
    if b.staff_id != _my_staff_id():
        raise Forbidden("Only the teacher the parent met records the meeting.", code="PTM-OWN")
    if b.starts_at > dt.datetime.now(_tz()):
        raise ConflictError("PTM-EARLY", "The meeting has not happened yet", "Record it after the slot.")
    text = (note or "").strip() or None
    if text and len(text) > 1000:
        raise HardValidation("PTM-NOTE", "The note is too long", "Keep it to 1,000 characters.")
    with uow.command("ops", "meeting:attend", action="record_meeting", record_kind="meeting_booking") as cmd:
        done: MeetingBooking = cmd.update(b, attended=attended, note=text, status="completed")
        return done
