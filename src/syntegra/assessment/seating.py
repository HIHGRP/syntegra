"""Examination seating: desk layouts and seat allocation (FR-EXM-03, FR-EXM-101). Pure functions, no framework.

A hall's desks are laid out in rows (A, B, C … from the front) and columns (1, 2, 3 … from the left). With
``spacing="alternate"`` only every other desk is used, chequerboard fashion, so no candidate sits directly beside
another; ``"every_desk"`` uses them all. Candidates are interleaved class by class so that neighbours come from
different classes, and both a row-by-row and a snaking fill are tried, keeping whichever leaves fewer neighbours from
the same class. Candidates with an access arrangement for a front seat go first, on row A of the first hall.
Every hall gets at least one invigilator, and one more for every further 30 candidates.
"""

from __future__ import annotations

import math
import string
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field

SPACING = ("alternate", "every_desk")
CANDIDATES_PER_INVIGILATOR = 30


@dataclass(frozen=True)
class Candidate:
    key: str  # entry id
    number: str  # candidate number
    name: str
    group: str  # class, e.g. "SS 3A"
    front: bool = False  # access arrangement: front seat


@dataclass(frozen=True)
class Hall:
    key: str  # room id
    code: str
    name: str
    capacity: int


@dataclass(frozen=True)
class Layout:
    rows: int
    cols: int
    desks: tuple[tuple[int, int], ...]  # usable (row, col), front to back


@dataclass
class Placed:
    hall: Hall
    layout: Layout
    seats: dict[tuple[int, int], Candidate] = field(default_factory=dict)

    def label(self, rc: tuple[int, int]) -> str:
        return desk_label(self.hall.code, *rc)


class NotEnoughSeats(ValueError):
    def __init__(self, needed: int, available: int) -> None:
        super().__init__(f"{needed} candidates but {available} seats")
        self.needed, self.available = needed, available


def desk_label(hall_code: str, row: int, col: int) -> str:
    """``A1-B3``: hall A1, row B (second from the front), desk 3 from the left."""
    letters = string.ascii_uppercase
    r = letters[row] if row < 26 else letters[row // 26 - 1] + letters[row % 26]
    return f"{hall_code}-{r}{col + 1}"


def layout(capacity: int, spacing: str) -> Layout:
    """Rows of desks for a hall's capacity (pairs of seats across, as in a classroom), with the desks to use."""
    if spacing not in SPACING:
        raise ValueError(f"spacing must be one of {SPACING}")
    capacity = max(1, capacity)
    cols = 6 if capacity >= 30 else 4 if capacity >= 12 else max(1, min(capacity, 3))
    rows = math.ceil(capacity / cols)
    desks = [(r, c) for r in range(rows) for c in range(cols) if r * cols + c < capacity]
    if spacing == "alternate":
        desks = [(r, c) for r, c in desks if (r + c) % 2 == 0]
    return Layout(rows, cols, tuple(desks))


def interleave(candidates: Sequence[Candidate]) -> list[Candidate]:
    """Front-seat candidates first, then one from each class in turn (classes in name order, numbers in order)."""
    front = sorted((c for c in candidates if c.front), key=lambda c: c.number)
    by_group: dict[str, list[Candidate]] = defaultdict(list)
    for c in sorted((c for c in candidates if not c.front), key=lambda c: (c.group, c.number)):
        by_group[c.group].append(c)
    queues = [by_group[g] for g in sorted(by_group)]
    out = list(front)
    while any(queues):
        for q in queues:
            if q:
                out.append(q.pop(0))
    return out


def _orders(lay: Layout) -> list[list[tuple[int, int]]]:
    rows: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for d in lay.desks:
        rows[d[0]].append(d)
    row_major = [d for r in sorted(rows) for d in sorted(rows[r])]
    snake = [d for r in sorted(rows) for d in (sorted(rows[r]) if r % 2 == 0 else sorted(rows[r], reverse=True))]
    return [row_major, snake]


def neighbours(seats: dict[tuple[int, int], Candidate]) -> int:
    """Pairs of candidates from the same class sitting side by side or one behind the other."""
    n = 0
    for (r, c), cand in seats.items():
        for rc in ((r, c + 1), (r + 1, c)):
            other = seats.get(rc)
            if other is not None and other.group == cand.group:
                n += 1
    return n


def invigilators_needed(candidates: int) -> int:
    return 0 if candidates == 0 else 1 + (candidates - 1) // CANDIDATES_PER_INVIGILATOR


def allocate(candidates: Sequence[Candidate], halls: Sequence[Hall], spacing: str) -> list[Placed]:
    """Seat every candidate, filling halls in the order given; halls left empty are not returned."""
    layouts = [(h, layout(h.capacity, spacing)) for h in halls]
    available = sum(len(lay.desks) for _h, lay in layouts)
    if len(candidates) > available:
        raise NotEnoughSeats(len(candidates), available)
    queue = interleave(candidates)
    placed: list[Placed] = []
    for hall, lay in layouts:
        if not queue:
            break
        take, queue = queue[: len(lay.desks)], queue[len(lay.desks) :]
        best: dict[tuple[int, int], Candidate] | None = None
        for order in _orders(lay):
            seats = dict(zip(order, take, strict=False))
            if best is None or neighbours(seats) < neighbours(best):
                best = seats
        placed.append(Placed(hall, lay, best or {}))
    return placed


def share_invigilators(placed: Sequence[Placed], staff: Sequence[str]) -> list[list[str]]:
    """Invigilators per hall: each hall's minimum first, then any extra staff to the fullest halls."""
    need = [invigilators_needed(len(p.seats)) for p in placed]
    if len(staff) < sum(need):
        raise ValueError(f"{sum(need)} invigilators needed, {len(staff)} chosen")
    out: list[list[str]] = [[] for _ in placed]
    pool = list(staff)
    for i, n in enumerate(need):
        out[i], pool = pool[:n], pool[n:]
    order = sorted(range(len(placed)), key=lambda i: -len(placed[i].seats))
    for k, s in enumerate(pool):
        out[order[k % len(order)]].append(s)
    return out
