"""Examination seating rules (assessment.seating): layouts, class mixing, capacity and invigilators."""

from __future__ import annotations

import pytest

from syntegra.assessment import seating as st


def _cands(spec: dict[str, int]) -> list[st.Candidate]:
    out = []
    for group, n in spec.items():
        out += [st.Candidate(f"{group}{i}", f"{group}/{i:03d}", f"Pupil {group}{i}", group) for i in range(n)]
    return out


def test_alternate_spacing_uses_a_chequerboard_of_desks() -> None:
    lay = st.layout(45, "alternate")
    assert (lay.rows, lay.cols) == (8, 6) and len(lay.desks) == 22
    assert all((r + c) % 2 == 0 for r, c in lay.desks)  # no one directly beside or behind another
    assert len(st.layout(45, "every_desk").desks) == 45
    assert st.desk_label("A1", 1, 2) == "A1-B3"


def test_classes_are_mixed_and_halls_filled_in_order() -> None:
    halls = [st.Hall("h1", "A1", "Classroom A1", 45), st.Hall("h2", "A2", "Classroom A2", 45)]
    placed = st.allocate(_cands({"SS 3A": 21, "SS 3B": 20}), halls, "every_desk")
    assert len(placed) == 1 and len(placed[0].seats) == 41  # one hall is enough
    assert st.neighbours(placed[0].seats) < 10  # mostly different classes side by side and front to back
    three = [*halls, st.Hall("h3", "A3", "Classroom A3", 45)]
    seats = st.allocate(_cands({"SS 3A": 30, "SS 3B": 30}), three, "alternate")
    assert [len(p.seats) for p in seats] == [22, 22, 16]


def test_not_enough_seats_and_front_seat_arrangement() -> None:
    hall = [st.Hall("h1", "A1", "A1", 10)]
    with pytest.raises(st.NotEnoughSeats) as exc:
        st.allocate(_cands({"X": 6}), hall, "alternate")
    assert (exc.value.needed, exc.value.available) == (6, 5)
    front = st.Candidate("f", "X/999", "Front Seat", "X", front=True)
    placed = st.allocate([*_cands({"X": 3}), front], hall, "every_desk")
    assert placed[0].seats[(0, 0)].key == "f"


def test_invigilators_one_per_hall_and_one_per_further_thirty() -> None:
    assert [st.invigilators_needed(n) for n in (0, 1, 30, 31, 61)] == [0, 1, 1, 2, 3]
    halls = [st.Hall(f"h{i}", f"A{i}", f"A{i}", 45) for i in range(1, 4)]
    placed = st.allocate(_cands({"A": 40, "B": 40}), halls, "every_desk")
    with pytest.raises(ValueError, match="needed"):
        st.share_invigilators(placed, ["t1"])
    shares = st.share_invigilators(placed, ["t1", "t2", "t3", "t4"])
    assert all(shares) and sum(len(s) for s in shares) == 4
