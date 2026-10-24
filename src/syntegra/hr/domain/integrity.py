"""Payroll integrity detection (ghost workers, double employment, pay after exit) — pure rules over facts."""

from __future__ import annotations

import datetime as dt
import uuid
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Finding:
    staff_id: uuid.UUID
    kind: str
    evidence: dict[str, Any] = field(default_factory=dict)
    employer_scope_id: uuid.UUID | None = None


def shared_tokens(rows: Iterable[tuple[uuid.UUID, bytes]], kind: str) -> list[Finding]:
    """Same lookup token (bank account or BVN) held by different staff members."""
    by_token: dict[bytes, set[uuid.UUID]] = defaultdict(set)
    for staff_id, token in rows:
        by_token[bytes(token)].add(staff_id)
    out = []
    for token, holders in by_token.items():
        if len(holders) > 1:
            for s in sorted(holders):
                shared = sorted(str(x) for x in holders - {s})
                out.append(Finding(s, kind, {"shared_with": shared, "token": token.hex()[:12]}))
    return out


def concurrent_posts(rows: Iterable[tuple[uuid.UUID, uuid.UUID, uuid.UUID]]) -> list[Finding]:
    """More than one active employment with *different* employers (staff_id, employer_scope_id, record id)."""
    by_staff: dict[uuid.UUID, dict[uuid.UUID, uuid.UUID]] = defaultdict(dict)
    for staff, employer, record in rows:
        by_staff[staff][employer] = record
    return [
        Finding(
            s,
            "concurrent_public_posts",
            {"employers": sorted(str(e) for e in emps), "records": sorted(str(r) for r in emps.values())},
        )
        for s, emps in by_staff.items()
        if len(emps) > 1
    ]


def past_retirement(rows: Iterable[tuple[uuid.UUID, dt.date | None, uuid.UUID]], on: dt.date) -> list[Finding]:
    return [
        Finding(s, "past_retirement_date", {"retirement_due_on": d.isoformat()}, emp)
        for s, d, emp in rows
        if d is not None and d < on
    ]


def no_recent_attendance(
    active: Iterable[tuple[uuid.UUID, uuid.UUID]], seen: set[uuid.UUID], on: dt.date, days: int = 30
) -> list[Finding]:
    return [
        Finding(s, "no_attendance_30_days", {"window_days": days, "until": on.isoformat()}, emp)
        for s, emp in active
        if s not in seen
    ]
