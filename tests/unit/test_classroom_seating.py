"""Classroom seating rules (success.arrange): layouts, strategies, front-row adjustments, keeping pairs apart."""

from __future__ import annotations

import pytest

from syntegra.success import arrange as ar


def _class(n: int) -> list[ar.Learner]:
    return [ar.Learner(f"k{i:02d}", f"Family{i:02d}", f"Given{i:02d}", float(40 + i)) for i in range(n)]


def test_pairs_layout_has_two_seater_desks_six_across() -> None:
    seats = ar.layout(45, "pairs")
    assert len(seats) == 45 and seats[0].label == "R1-S1" and seats[-1].label == "R8-S3"
    near = ar.neighbours(seats)
    assert near["R1-S1"] == {"R1-S2", "R2-S1"}  # desk-mate and the seat behind
    assert "R1-S3" not in near["R1-S2"]  # an aisle between desks
    groups = ar.layout(36, "groups")
    assert len({s.unit for s in groups}) == 6  # six tables of six


def test_strategies() -> None:
    seats = ar.layout(45, "pairs")
    learners = _class(10)
    alpha = ar.arrange(learners, seats, "alphabetical")
    assert alpha["k00"] == "R1-S1" and alpha["k01"] == "R1-S2"
    ability = ar.arrange(learners, seats, "ability")
    assert ability["k00"] == "R1-S1"  # lowest average at the front
    mixed = ar.arrange(learners, seats, "mixed_ability")
    assert {mixed["k00"], mixed["k09"]} == {"R1-S1", "R1-S2"}  # weakest with strongest at the first desk
    assert ar.arrange(learners, seats, "random", seed=7) == ar.arrange(learners, seats, "random", seed=7)
    with pytest.raises(ValueError, match="seats"):
        ar.arrange(_class(50), seats, "alphabetical")


def test_front_row_adjustment_and_negative_influences() -> None:
    seats = ar.layout(45, "pairs")
    learners = [*_class(12), ar.Learner("glasses", "Zuma", "Ada", 80.0, front=True)]
    avoid = ar.influence_pairs([("k01", "k11", 31, 9, 2), ("k02", "k10", 25, 7, 1), ("k03", "k04", 12, 9, 0)])
    assert ("k03", "k04") not in avoid  # fewer than 20 shared events: not enough evidence
    plan = ar.arrange(learners, seats, "separate_negative_influences", avoid=avoid)
    assert plan["glasses"].startswith("R1-")
    assert ar.conflicts(plan, seats, avoid) == []
    assert ar.conflicts(ar.arrange(learners, seats, "mixed_ability"), seats, avoid)  # mixed ability alone pairs them
    assert ar.rag(72) == "green" and ar.rag(55) == "amber" and ar.rag(31) == "red" and ar.rag(None) is None
