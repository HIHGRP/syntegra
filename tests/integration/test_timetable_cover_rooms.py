"""The school's timetable (TIM-02), its own school day and the builder (TIM-01), staff cover (TIM-03) and room booking
with booking permissions (TIM-04), end to end on the Abia demonstration school."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

import pytest

from tests.conftest import system_ctx
from tests.integration.test_cr006_web import _ok, _sign_in

pytestmark = pytest.mark.django_db(databases="__all__")


def _next_monday() -> dt.date:
    today = dt.date.today()
    return today + dt.timedelta(days=7 - today.weekday())


def test_school_day_timetable_cover_and_rooms(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions.models import Institution
    from syntegra.operations.models import Room
    from syntegra.people.models import CoverAssignment, StaffPost
    from syntegra.platform.demo import abia
    from syntegra.timetable import services as tts
    from syntegra.timetable.models import LessonOccurrence, PeriodStructure, RoomBooking, Timetable, TimetableLesson

    abia.run(
        abia.Scale(schools_per_lga=1, pupils=120, lgas=1, absu_students=3, asceta_students=3, absu_staff=2,
                   asceta_staff=2, days=1),
        log=lambda _m: None,
    )  # fmt: skip
    with context.use(system_ctx()):
        school = Institution.objects.get(name="Government Secondary School, Eziama")
        head = AppUser.objects.get(
            id__in=RoleGrant.objects.filter(scope_id=school.scope_node_id).values("user_id"),
            username__startswith="head.",
        )
        posts = {p.job_title: p for p in StaffPost.objects.filter(institution_id=school.id, valid_to__isnull=True)}
        rooms = {r.code: r for r in Room.objects.filter(scope_node_id=school.scope_node_id)}
        assert {"LAB1", "ICT1", "LIB", "HALL"} <= set(rooms)
    code = school.institution_code.lower()
    teacher = f"teacher.{code}@abia.demo"
    maths = posts["Teacher, Mathematics"].staff_id

    # TIM-02: the teacher opens on their own week; the head on a class, and can pick a room
    _sign_in(client, teacher)
    page = _ok(client.get("/timetable"))
    assert "Timetable — " in page and "Mathematics" in page and "Break" in page and "Lunch" in page
    assert client.get(f"/cover?school={school.id}").status_code == 403  # the cover board is the head's
    _sign_in(client, head.username)
    page = _ok(client.get(f"/timetable?school={school.id}"))
    assert "Timetable — JSS 1A" in page
    assert "Timetable — LAB1" in _ok(client.get(f"/timetable?school={school.id}&room={rooms['LAB1'].id}"))

    # TIM-01: the school day; a day that ends after 17:00 is refused; a new day rebuilds and publishes
    builder = f"/timetable/builder?school={school.id}"
    page = _ok(client.get(builder))
    assert "9 teaching periods of 35 minutes, 08:00–14:15" in page and "Periods each class needs" in page
    day = {"start": "07:45", "period": "40", "before_break": "3", "break_minutes": "20", "before_lunch": "3",
           "lunch_minutes": "30", "after_lunch": "3"}  # fmt: skip
    r = client.post(builder, {**day, "period": "70", "after_lunch": "4"})
    assert r.status_code == 422 and "after 17:00" in r.content.decode()
    page = _ok(client.post(builder, day))
    assert re.search(r"Version \d+ built and published", page), page[-3000:]
    with context.use(system_ctx()):
        tt = tts.current(school.id)
        assert tt is not None and tt.version >= 2
        first = PeriodStructure.objects.filter(timetable_id=tt.id, cycle_day=1).order_by("starts_at").first()
        assert first is not None and first.starts_at == dt.time(7, 45) and first.ends_at == dt.time(8, 25)
        lessons = list(TimetableLesson.objects.filter(timetable_id=tt.id))
        assert {x.duration_minutes for x in lessons} == {40}
        assert tts.period_minutes(school.id) == 40 and tts.describe(tts.schedule(tt))["end"] == "14:35"
        assert Timetable.objects.filter(institution_id=school.id, status="superseded").exists()
    assert "9 teaching periods of 40 minutes, 07:45–14:35" in _ok(client.get(builder))
    _sign_in(client, teacher)
    assert client.post(builder, day).status_code == 403

    # TIM-03: the Mathematics teacher is absent next Monday; each of their lessons that day needs cover
    _sign_in(client, head.username)
    monday = _next_monday()
    board = f"/cover?school={school.id}&on={monday}"
    page = _ok(client.post(board, {"action": "absence", "staff_id": str(maths), "absence_type": "training",
                                   "first": str(monday), "on": str(monday)}))  # fmt: skip
    assert "Absence recorded" in page and "Training or workshop" in page
    affected = [x for x in lessons if x.staff_id == maths and x.cycle_day == 1]
    assert affected and f'<span class="v">{len(affected)}</span><span class="k">lessons affected' in page
    r = client.post(board, {"action": "absence", "staff_id": str(maths), "absence_type": "sickness",
                            "first": str(monday), "on": str(monday)})  # fmt: skip
    assert r.status_code == 422 and "already recorded" in r.content.decode()
    first_lesson = affected[0]
    choices = re.findall(rf'name="lesson_id" value="{first_lesson.id}">.*?</form>', page, re.S)
    assert choices
    free = re.findall(r'value="staff:([0-9a-f-]{36})"', choices[0])
    assert free and str(maths) not in free
    busy = next(x.staff_id for x in lessons if x.cycle_day == 1 and x.period_code == first_lesson.period_code
                and x.staff_id != maths)  # fmt: skip
    r = client.post(board, {"action": "assign", "lesson_id": str(first_lesson.id), "choice": f"staff:{busy}",
                            "on": str(monday)})  # fmt: skip
    assert r.status_code == 422 and "not free" in r.content.decode()
    page = _ok(client.post(board, {"action": "assign", "lesson_id": str(first_lesson.id), "choice": f"staff:{free[0]}",
                                   "on": str(monday)}))  # fmt: skip
    assert "Cover arranged." in page
    r = client.post(board, {"action": "assign", "lesson_id": str(first_lesson.id), "choice": f"staff:{free[0]}",
                            "on": str(monday)})  # fmt: skip
    assert r.status_code == 422 and "already arranged" in r.content.decode()
    if len(affected) > 1:
        page = _ok(client.post(board, {"action": "assign", "lesson_id": str(affected[1].id),
                                       "choice": "alt:supervised_study_with_lms_work", "on": str(monday)}))  # fmt: skip
        assert "Supervised study with work set" in page
    with context.use(system_ctx()):
        o = LessonOccurrence.objects.get(timetable_lesson_id=first_lesson.id, occurs_on=monday)
        c = CoverAssignment.objects.get(lesson_occurrence_id=o.id, status="confirmed")
        assert str(o.staff_id) == free[0] and o.status == "covered" and str(c.cover_staff_id) == free[0]
        assert c.rank_evidence["rank"] == 1 and c.confirmed_by == head.id
    # the week shows the change: on the absent teacher's week and on the covering teacher's
    week = f"/timetable?school={school.id}&week={monday}"
    assert "Cover: " in _ok(client.get(f"{week}&teacher={maths}"))
    assert "You cover" in _ok(client.get(f"{week}&teacher={free[0]}"))
    # cancelling puts the lesson back on the board as a gap
    page = _ok(client.post(board, {"action": "cancel", "cover_id": str(c.id), "on": str(monday)}))
    assert "Cover cancelled" in page
    with context.use(system_ctx()):
        o.refresh_from_db()
        assert o.status == "scheduled" and o.staff_id == maths

    # TIM-04: booking rules for the teacher
    _sign_in(client, teacher)
    book = f"/rooms/bookings?school={school.id}"
    base = {"action": "book", "on": str(monday), "starts": "15:00", "ends": "16:00", "people": "30"}
    page = _ok(client.post(book, {**base, "room_id": str(rooms["ICT1"].id), "purpose": "SS 2 spreadsheet lesson"}))
    assert "Booked." in page and "the ict suite is free" in page
    r = client.post(book, {**base, "room_id": str(rooms["ICT1"].id), "starts": "15:30", "ends": "16:30",
                           "purpose": "Coding club"})  # fmt: skip
    assert r.status_code == 422 and "already booked" in r.content.decode()
    r = client.post(book, {**base, "room_id": str(rooms["ICT1"].id), "people": "31", "starts": "16:00",
                           "ends": "17:00", "purpose": "Coding club"})  # fmt: skip
    assert r.status_code == 422 and "holds 30" in r.content.decode()
    page = _ok(client.post(book, {**base, "room_id": str(rooms["LAB1"].id), "purpose": "Mathematics measurement"}))
    assert "Request sent." in page and "you teach no subject that uses the laboratory" in page
    page = _ok(client.post(book, {**base, "room_id": str(rooms["HALL"].id), "people": "300",
                                  "purpose": "Mathematics quiz finals"}))  # fmt: skip
    assert "Request sent." in page and "booked only with approval" in page
    r = client.post(book, {**base, "on": str(dt.date.today() - dt.timedelta(days=1)), "room_id": str(rooms["LIB"].id),
                           "purpose": "Reading hour"})  # fmt: skip
    assert r.status_code == 422 and "has passed" in r.content.decode()
    taught = next(x for x in lessons if x.cycle_day == 1 and x.room_id is not None)
    with context.use(system_ctx()):
        a, b = tts.bell(tt)[taught.period_code]
    r = client.post(book, {**base, "room_id": str(taught.room_id), "starts": a.strftime("%H:%M"),
                           "ends": b.strftime("%H:%M"), "purpose": "Extra lesson"})  # fmt: skip
    assert r.status_code == 422 and "timetabled lesson" in r.content.decode()
    assert (
        client.post(book, {"action": "approve", "booking_id": "00000000-0000-7000-8000-000000000001"}).status_code
        == 403
    )

    # the head approves the laboratory and declines the hall; the teacher cancels their ICT booking
    _sign_in(client, head.username)
    page = _ok(client.get(book))
    assert "Waiting for your approval" in page
    with context.use(system_ctx()):
        lab = RoomBooking.objects.get(room_id=rooms["LAB1"].id, status="requested")
        hall = RoomBooking.objects.get(room_id=rooms["HALL"].id, status="requested")
        ict = RoomBooking.objects.get(room_id=rooms["ICT1"].id, status="confirmed")
    assert "Booking approved." in _ok(client.post(book, {"action": "approve", "booking_id": str(lab.id)}))
    assert "Booking declined." in _ok(client.post(book, {"action": "decline", "booking_id": str(hall.id)}))
    r = client.post(book, {"action": "approve", "booking_id": str(hall.id)})
    assert r.status_code == 422 and "Already decided" in r.content.decode()
    _sign_in(client, teacher)
    assert "Booking cancelled." in _ok(client.post(book, {"action": "cancel", "booking_id": str(ict.id)}))
    with context.use(system_ctx()):
        assert {x.room_id: x.status for x in RoomBooking.objects.filter(id__in=[lab.id, hall.id, ict.id])} == {
            rooms["LAB1"].id: "confirmed",
            rooms["HALL"].id: "declined",
            rooms["ICT1"].id: "cancelled",
        }
    # the room's week shows the confirmed laboratory booking
    assert "Mathematics measurement" in _ok(
        client.get(f"/timetable?school={school.id}&room={rooms['LAB1'].id}&week={monday}")
    )
