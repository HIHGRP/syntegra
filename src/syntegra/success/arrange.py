"""Classroom seating: room layouts and arrangement strategies (FR-BEH-101, FR-BEH-110). Pure functions, no framework.

Layouts describe where the desks are: ``pairs`` — two-seater desks in rows, three across with aisles between (the
usual Nigerian secondary classroom); ``rows`` — single desks in rows; ``groups`` — tables of six. Seats are labelled by
row from the front and seat from the left (``R1-S3``). Two seats are *neighbours* when they share a desk or table, or
sit directly one behind the other.

Strategies (``seating_strategy``): ``alphabetical`` by family name; ``ability`` — those needing most support (lowest
working average) at the front; ``mixed_ability`` — each desk pairs a stronger with a weaker learner; ``random`` —
reproducible from its seed; ``separate_negative_influences`` — starts from mixed ability, then moves learners apart
where the evidence (20 or more shared events, more negative behaviour when adjacent than apart) says they distract
each other; ``manual`` — the teacher's own arrangement. Learners with an authorised seating or large-print adjustment
always sit in the front row.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

STYLES = ("pairs", "rows", "groups")
STRATEGIES = ("alphabetical", "ability", "mixed_ability", "random", "separate_negative_influences", "manual")
MIN_EVENTS = 20


@dataclass(frozen=True)
class Seat:
    label: str
    row: int  # 0 = front
    col: int  # seat across the room, 0 = leftmost as the class faces the board
    unit: int  # desk or table number: seats of one unit sit together


@dataclass(frozen=True)
class Learner:
    key: str
    family: str
    given: str
    average: float | None = None  # working average, 0–100
    front: bool = False  # authorised adjustment (seating, large print): always in the front row


def layout(capacity: int, style: str) -> list[Seat]:
    if style not in STYLES:
        raise ValueError(f"style must be one of {STYLES}")
    capacity = max(1, capacity)
    per_unit, across = {"pairs": (2, 6), "rows": (1, 6), "groups": (6, 6)}[style]
    rows = math.ceil(capacity / across)
    seats: list[Seat] = []
    for r in range(rows):
        for c in range(across):
            if len(seats) >= capacity:
                break
            # tables of six: two rows of three facing each other; otherwise desks of ``per_unit`` along the row
            unit = (r // 2) * 2 + c // 3 if style == "groups" else (r * across + c) // per_unit
            seats.append(Seat(f"R{r + 1}-S{c + 1}", r, c, unit))
    return seats


def neighbours(seats: Sequence[Seat]) -> dict[str, set[str]]:
    by_pos = {(s.row, s.col): s for s in seats}
    out: dict[str, set[str]] = {s.label: set() for s in seats}
    for s in seats:
        for other in seats:
            if other.label != s.label and other.unit == s.unit:
                out[s.label].add(other.label)
        behind = by_pos.get((s.row + 1, s.col))
        if behind is not None:
            out[s.label].add(behind.label)
            out[behind.label].add(s.label)
    return out


def _order(learners: Sequence[Learner], strategy: str, seed: int) -> list[Learner]:
    alpha = sorted(learners, key=lambda x: (x.family.lower(), x.given.lower(), x.key))
    known = sorted((x for x in alpha if x.average is not None), key=lambda x: x.average or 0)
    unknown = [x for x in alpha if x.average is None]
    if strategy == "alphabetical":
        return alpha
    if strategy == "random":
        out = list(alpha)
        random.Random(seed).shuffle(out)  # noqa: S311 — seating, not security
        return out
    if strategy == "ability":
        return known + unknown  # weakest at the front
    # mixed ability (and the start for separating influences): strongest with weakest, desk by desk
    out = []
    lo, hi = 0, len(known) - 1
    while lo <= hi:
        out.append(known[lo])
        if hi != lo:
            out.append(known[hi])
        lo, hi = lo + 1, hi - 1
    return out + unknown


def arrange(
    learners: Sequence[Learner],
    seats: Sequence[Seat],
    strategy: str,
    *,
    seed: int = 1,
    avoid: Sequence[tuple[str, str]] = (),
) -> dict[str, str]:
    """learner key → seat label. ``avoid`` lists pairs of learner keys who should not be neighbours."""
    if strategy not in STRATEGIES or strategy == "manual":
        raise ValueError("choose a strategy to generate an arrangement")
    if len(learners) > len(seats):
        raise ValueError(f"{len(learners)} learners but {len(seats)} seats")
    fronts = sorted((x for x in learners if x.front), key=lambda x: (x.family.lower(), x.given.lower()))
    order = fronts + _order([x for x in learners if not x.front], strategy, seed)
    plan = {x.key: s.label for x, s in zip(order, seats, strict=False)}
    if strategy == "separate_negative_influences" and avoid:
        plan = separate(plan, seats, avoid, keep={x.key for x in fronts})
    return plan


def conflicts(plan: dict[str, str], seats: Sequence[Seat], avoid: Sequence[tuple[str, str]]) -> list[tuple[str, str]]:
    near = neighbours(seats)
    return [(a, b) for a, b in avoid if a in plan and b in plan and plan[b] in near[plan[a]]]


def separate(
    plan: dict[str, str],
    seats: Sequence[Seat],
    avoid: Sequence[tuple[str, str]],
    *,
    keep: set[str] | frozenset[str] = frozenset(),
) -> dict[str, str]:
    """Swap learners (or move them to free seats) until no avoided pair are neighbours, where that is possible.
    Learners in ``keep`` (front-row adjustments) are never moved."""
    plan = dict(plan)
    labels = [s.label for s in seats]
    for _ in range(len(avoid) * len(labels)):
        bad = conflicts(plan, seats, avoid)
        if not bad:
            break
        a, b = bad[0]
        mover = a if b in keep else b
        if mover in keep:
            break
        best: tuple[int, str] | None = None
        taken = {v: k for k, v in plan.items()}
        for label in labels:
            if label == plan[mover]:
                continue
            other = taken.get(label)
            if other in keep:
                continue
            trial = dict(plan)
            trial[mover] = label
            if other is not None:
                trial[other] = plan[mover]
            score = len(conflicts(trial, seats, avoid))
            if best is None or score < best[0]:
                best = (score, label)
        if best is None:
            break
        other = taken.get(best[1])
        if other is not None:
            plan[other] = plan[mover]
        plan[mover] = best[1]
    return plan


def influence_pairs(rows: Sequence[tuple[str, str, int, int, int]]) -> list[tuple[str, str]]:
    """(a, b, shared_events, negative_adjacent, negative_apart) → pairs to keep apart: enough evidence, and more
    negative behaviour when sitting together than apart."""
    return [(a, b) for a, b, shared, neg_adj, neg_apart in rows if shared >= MIN_EVENTS and neg_adj > neg_apart]


def rag(average: float | None) -> str | None:
    if average is None:
        return None
    return "green" if average >= 70 else "amber" if average >= 50 else "red"
