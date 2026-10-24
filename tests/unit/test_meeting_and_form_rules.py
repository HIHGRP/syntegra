"""Parents' meeting slots and clash rules (PTM-101), and checking answers to a school's form (FRM-102)."""

from __future__ import annotations

import datetime as dt
import uuid
from zoneinfo import ZoneInfo

import pytest

from syntegra.core.errors import HardValidation
from syntegra.forms.builder import check
from syntegra.forms.meetings import _clashes, slot_starts
from syntegra.forms.models import FormDefinition, MeetingBooking, MeetingEvent

TZ = ZoneInfo("Africa/Lagos")
DAY = dt.date(2026, 11, 4)


def _event(gap: int = 5) -> MeetingEvent:
    window = {"date": DAY.isoformat(), "from": "16:00", "to": "17:00"}
    return MeetingEvent(title="SS 2", class_group_ids=[], days=[window], slot_minutes=10, travel_gap_minutes=gap,
                        modes=["in_person"])  # fmt: skip


def _at(h: int, m: int) -> dt.datetime:
    return dt.datetime.combine(DAY, dt.time(h, m), tzinfo=TZ)


def test_slots_fill_the_window_and_stop_before_the_end() -> None:
    starts = slot_starts(_event())
    assert [s.strftime("%H:%M") for s in starts] == ["16:00", "16:10", "16:20", "16:30", "16:40", "16:50"]
    ev = _event()
    ev.days = [{"date": DAY.isoformat(), "from": "16:00", "to": "16:25"}]
    assert len(slot_starts(ev)) == 2  # a part-slot at the end is not offered


def test_a_parent_needs_time_to_walk_between_teachers() -> None:
    ev, a, b = _event(gap=5), uuid.uuid4(), uuid.uuid4()
    mine = [MeetingBooking(staff_id=a, starts_at=_at(16, 10))]
    assert _clashes(ev, mine, b, _at(16, 10)) is not None  # the same time
    assert "no time to get from" in (_clashes(ev, mine, b, _at(16, 20)) or "")  # back to back, another teacher
    assert _clashes(ev, mine, a, _at(16, 20)) is None  # back to back with the same teacher is fine
    assert _clashes(ev, mine, b, _at(16, 30)) is None  # a slot in between is time enough
    assert _clashes(_event(gap=0), mine, b, _at(16, 20)) is None  # no gap asked for


def _form() -> FormDefinition:
    return FormDefinition(
        title="Medical",
        field_schema={"fields": [
            {"key": "q1", "label": "Condition?", "kind": "yes_no", "required": True, "options": [], "show_if": None},
            {"key": "q2", "label": "Details", "kind": "long_text", "required": True, "options": [],
             "show_if": {"key": "q1", "equals": "yes"}},
            {"key": "q3", "label": "Weight (kg)", "kind": "number", "required": False, "options": [], "show_if": None},
            {"key": "q4", "label": "House", "kind": "choice", "required": False, "options": ["Blue", "Red"],
             "show_if": None},
            {"key": "q5", "label": "Signed", "kind": "signature", "required": True, "options": [], "show_if": None},
        ]},
        version=1,
    )  # fmt: skip


def test_answers_are_kept_only_for_questions_that_were_shown() -> None:
    f = _form()
    assert check(f, {"q1": "no", "q2": "left over from an earlier choice", "q5": "Ada Okafor"}) == {
        "q1": "no",
        "q5": "Ada Okafor",
    }
    got = check(f, {"q1": "yes", "q2": "Asthma; inhaler in the bag", "q3": "1,045.5", "q4": "Red", "q5": "Ada Okafor"})
    assert got["q2"] == "Asthma; inhaler in the bag" and got["q3"] == "1045.5" and got["q4"] == "Red"


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ({"q5": "Ada Okafor"}, "“Condition?” needs an answer"),
        ({"q1": "yes", "q5": "Ada Okafor"}, "“Details” needs an answer"),
        ({"q1": "maybe", "q5": "Ada Okafor"}, "answer yes or no"),
        ({"q1": "no", "q3": "heavy", "q5": "Ada Okafor"}, "must be a number"),
        ({"q1": "no", "q4": "Green", "q5": "Ada Okafor"}, "choose from the list"),
        ({"q1": "no", "q5": "Ada"}, "type your full name"),
    ],
)
def test_answers_are_checked(raw: dict[str, str], message: str) -> None:
    with pytest.raises(HardValidation) as exc:
        check(_form(), raw)
    assert message in (exc.value.detail or "")
