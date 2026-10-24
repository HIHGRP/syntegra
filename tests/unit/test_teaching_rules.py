"""Pure rules of the timetable placement and the scheme-of-work drafting (ACA-101, CUR-09)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any

from syntegra.curriculum.lessons import share, spread
from syntegra.timetable import services as tt


def test_spread_covers_every_week_in_order_and_in_proportion() -> None:
    ids = [uuid.uuid4() for _ in range(5)]
    weeks = spread([(ids[0], 2), (ids[1], 2), (ids[2], 4), (ids[3], 1), (ids[4], 3)], 12)
    assert len(weeks) == 12 and all(weeks)
    flat = [x for w in weeks for x in w]
    assert [x for i, x in enumerate(flat) if i == 0 or flat[i - 1] != x] == ids  # in curriculum order, each once a run
    assert sum(1 for w in weeks if ids[2] in w) > sum(1 for w in weeks if ids[3] in w)  # 4 hours span more weeks
    assert spread([], 3) == [[], [], []] and spread([(ids[0], 1)], 0) == []


def test_spread_puts_many_short_objectives_into_the_same_week() -> None:
    ids = [uuid.uuid4() for _ in range(30)]
    weeks = spread([(i, 1) for i in ids], 10)
    assert len(weeks) == 10 and all(len(w) >= 3 for w in weeks)
    assert sorted({x for w in weeks for x in w}, key=ids.index) == ids


def test_share_splits_a_week_over_its_lessons() -> None:
    assert share(["a", "b"], 5) == [["a"], ["a"], ["a"], ["b"], ["b"]]
    assert share(["a", "b", "c", "d", "e", "f", "g"], 3) == [["a", "b"], ["c", "d"], ["e", "f", "g"]]
    assert share([], 2) == [[], []] and share(["a"], 0) == []


def _need(cls: Any, staff: uuid.UUID, periods: int) -> Any:
    return tt._Need(plan=SimpleNamespace(id=uuid.uuid4()), cls=cls, staff_id=staff, periods=periods)  # type: ignore[arg-type]


def test_placement_never_double_books_and_spreads_a_subject_over_the_week() -> None:
    classes = [SimpleNamespace(id=uuid.uuid4(), name=f"C{i}") for i in range(12)]
    teachers = [uuid.uuid4() for _ in range(11)]  # one teacher per subject for the junior and the senior classes
    rooms = [uuid.uuid4() for _ in range(7)]
    needs = [_need(c, teachers[2 * j + (i < 6)], (5, 5, 3, 3, 3)[j]) for i, c in enumerate(classes) for j in range(5)]
    needs += [_need(classes[0], teachers[10], 3)]
    placed, unmet = tt.place(needs, rooms, {c.id: rooms[i % len(rooms)] for i, c in enumerate(classes)})
    assert not unmet and len(placed) == sum(n.periods for n in needs)
    for key in (
        lambda n, d, p, r: (n.cls.id, d, p),
        lambda n, d, p, r: (n.staff_id, d, p),
        lambda n, d, p, r: (r, d, p),
    ):
        slots = [key(*x) for x in placed]
        assert len(slots) == len(set(slots))  # no class, teacher or room in two places at once
    per_day: dict[tuple[int, int], int] = {}
    for n, d, _p, _r in placed:
        per_day[(id(n), d)] = per_day.get((id(n), d), 0) + 1
    assert max(per_day.values()) == 1  # five periods or fewer: never twice a day


def test_placement_reports_what_cannot_fit() -> None:
    cls = SimpleNamespace(id=uuid.uuid4(), name="C")
    staff = uuid.uuid4()
    room = uuid.uuid4()
    placed, unmet = tt.place([_need(cls, staff, 50)], [room], {cls.id: room})
    assert len(placed) == 5 * len(tt.TEACHING) and unmet == [
        {"class_subject_plan_id": unmet[0]["class_subject_plan_id"], "class": "C", "missing_periods": 5}
    ]
