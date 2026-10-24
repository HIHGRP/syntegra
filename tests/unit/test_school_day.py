"""The school day (TIM-01): building a bell schedule from its shape, and reading the shape back."""

from __future__ import annotations

import pytest

from syntegra.core.errors import HardValidation
from syntegra.timetable.services import BELL, describe, school_day


def test_the_standard_day_round_trips() -> None:
    shape = describe(BELL)
    assert shape == {"start": "08:00", "end": "14:15", "period": 35, "before_break": 3, "before_lunch": 3,
                     "after_lunch": 3, "break_minutes": 20, "lunch_minutes": 40, "periods": 9,
                     "teaching_minutes": 315}  # fmt: skip
    keys = ("start", "period", "before_break", "break_minutes", "before_lunch", "lunch_minutes", "after_lunch")
    assert school_day(**{k: shape[k] for k in keys}) == BELL


def test_a_school_day_of_its_own() -> None:
    day = school_day("07:30", 40, 4, 15, 2, 30, 2)
    assert [b[0] for b in day] == ["P1", "P2", "P3", "P4", "BRK", "P5", "P6", "LUN", "P7", "P8"]
    assert day[0] == ("P1", "07:30", "08:10", True) and day[4] == ("BRK", "10:10", "10:25", False)
    assert day[-1] == ("P8", "12:55", "13:35", True)
    # no lunch is kept at the end of a day with nothing after it
    assert [b[0] for b in school_day("08:00", 45, 3, 20, 3, 30, 0)][-1] == "P6"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("05:00", 35, 3, 20, 3, 40, 3), "06:30"),
        (("08:00", 25, 3, 20, 3, 40, 3), "30 to 80"),
        (("08:00", 35, 0, 20, 3, 40, 3), "at least one before the break"),
        (("08:00", 35, 5, 20, 5, 40, 5), "4 to 12"),
        (("08:00", 35, 3, 5, 3, 40, 3), "break of 10 to 60"),
        (("09:30", 80, 4, 30, 4, 60, 4), "after 17:00"),
    ],
)
def test_days_that_do_not_work_are_refused(args: tuple, message: str) -> None:
    with pytest.raises(HardValidation) as exc:
        school_day(*args)
    assert message in str(exc.value.problem())
