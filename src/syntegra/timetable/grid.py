"""The timetable as a week grid (MFS TIM-02): a class's, a teacher's or a room's week from the published timetable,
with the week's changes — cover (who takes a lesson, or that it is supervised, merged or cancelled) and, for a room,
its bookings. A teacher sees their own week, including the lessons they cover."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings

from syntegra.academic import teaching
from syntegra.academic.models import ClassGroup, Subject
from syntegra.core import authz, context
from syntegra.core.errors import HardValidation, NotFound
from syntegra.timetable import cover, rooms
from syntegra.timetable import services as tts
from syntegra.timetable.models import RoomBooking, TimetableLesson


def week_grid(
    institution_id: uuid.UUID,
    week_of: dt.date,
    *,
    class_id: uuid.UUID | None = None,
    staff_id: uuid.UUID | None = None,
    room_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    from syntegra.institutions.models import Institution
    from syntegra.operations.models import Room

    ctx = context.require()
    authz.require("timetable:view", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    if sum(x is not None for x in (class_id, staff_id, room_id)) != 1:
        raise HardValidation("TIM-VIEW", "Choose a class, a teacher or a room", "")
    tt = tts.current(inst.id)
    monday = tts.monday(week_of)
    day = tts.schedule(tt)
    dates = {d: monday + dt.timedelta(days=d - 1) for d in tts.DAYS}
    classes = {c.id: c for c in ClassGroup.objects.filter(institution_id=inst.id, status="active").order_by("name")}
    posts = teaching.staff_of(inst.id, monday)
    names = teaching._names({p.staff_id for p in posts})
    room_list = rooms._rooms(inst.scope_node_id)
    room_names = {r.id: r.code for r in Room.objects.filter(scope_node_id=inst.scope_node_id, status="active")}
    cells: dict[tuple[str, int], list[dict[str, Any]]] = {}
    title = ""
    if tt is not None:
        all_lessons = list(TimetableLesson.objects.filter(timetable_id=tt.id))
        covers = cover.covers_in_week(tt, monday)
        subjects = dict(Subject.objects.filter(id__in={x.subject_id for x in all_lessons}).values_list("id", "name"))
        for ls in all_lessons:
            on = dates.get(ls.cycle_day)
            if on is None:
                continue
            c = covers.get((ls.id, on))
            mine = (
                (class_id is not None and ls.class_group_id == class_id)
                or (room_id is not None and ls.room_id == room_id)
                or (staff_id is not None and (ls.staff_id == staff_id or (c is not None and c["staff_id"] == staff_id)))
            )
            if not mine:
                continue
            note = None
            if c is not None:
                if c["staff_id"] is not None:
                    note = f"Cover: {names.get(c['staff_id'], '?')}" + ("" if c["qualified"] else " (not authorised)")
                else:
                    note = c["alternative"]
            cells.setdefault((ls.period_code, ls.cycle_day), []).append(
                {
                    "subject": subjects.get(ls.subject_id, "?"),
                    "class": classes[ls.class_group_id].name if ls.class_group_id in classes else "?",
                    "teacher": names.get(ls.staff_id, "?"),
                    "room": room_names.get(ls.room_id, "") if ls.room_id else "",
                    "change": note,
                    "covering": staff_id is not None and ls.staff_id != staff_id,
                    "away": staff_id is not None and ls.staff_id == staff_id and c is not None,
                }
            )
    bookings = []
    if room_id is not None:
        tz = ZoneInfo(settings.TIME_ZONE)
        a = dt.datetime.combine(monday, dt.time(0), tzinfo=tz)
        for b in RoomBooking.objects.filter(
            room_id=room_id, status__in=rooms.LIVE, starts_at__lt=a + dt.timedelta(days=6), ends_at__gt=a
        ).order_by("starts_at"):
            s0, s1 = b.starts_at.astimezone(tz), b.ends_at.astimezone(tz)
            bookings.append({"on": s0.date(), "starts": s0.time(), "ends": s1.time(), "purpose": b.purpose,
                             "status": b.status})  # fmt: skip
            for code, p0, p1, _teach in day:
                if s0.isoweekday() in tts.DAYS and tts._t(p0) < s1.time() and s0.time() < tts._t(p1):
                    cells.setdefault((code, s0.isoweekday()), []).append(
                        {"booking": b.purpose, "status": b.status, "starts": s0.time(), "ends": s1.time()}
                    )
    if class_id is not None:
        title = classes[class_id].name if class_id in classes else "?"
    elif staff_id is not None:
        title = names.get(staff_id, "?")
    elif room_id is not None:
        title = room_names.get(room_id, "?")
    rows = [
        {
            "code": code,
            "starts": p0,
            "ends": p1,
            "teaching": teach,
            "cells": [cells.get((code, d), []) for d in tts.DAYS],
        }
        for code, p0, p1, teach in day
    ]
    return {
        "institution": {"id": inst.id, "name": inst.name},
        "timetable": {"version": tt.version, "published_at": tt.published_at} if tt else None,
        "title": title,
        "view": "class" if class_id else "teacher" if staff_id else "room",
        "picked": class_id or staff_id or room_id,
        "days": [{"name": tts.DAYS[d], "on": dates[d], "today": dates[d] == dt.date.today()} for d in tts.DAYS],
        "week": {"monday": monday, "prev": monday - dt.timedelta(days=7), "next": monday + dt.timedelta(days=7)},
        "rows": rows,
        "bookings": bookings,
        "lessons": sum(len([e for e in v if "subject" in e]) for v in cells.values()),
        "changes": sum(1 for v in cells.values() for e in v if e.get("change")),
        "classes": [{"id": c.id, "name": c.name} for c in classes.values()],
        "teachers": sorted(
            ({"id": p.staff_id, "name": names.get(p.staff_id, "?")} for p in posts), key=lambda x: x["name"]
        ),
        "rooms": [
            {"id": r.id, "name": f"{r.code} — {rooms.BOOKABLE.get(r.room_type, r.room_type)}"} for r in room_list
        ],
    }
