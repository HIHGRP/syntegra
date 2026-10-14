"""Leave arithmetic: working days, entitlement selection, balances."""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal


def working_days(start: dt.date, end: dt.date, holidays: Iterable[dt.date] = ()) -> int:
    hol = set(holidays)
    n, d = 0, start
    while d <= end:
        if d.weekday() < 5 and d not in hol:
            n += 1
        d += dt.timedelta(days=1)
    return n


def leave_days(start: dt.date, end: dt.date, basis: str, holidays: Iterable[dt.date] = ()) -> Decimal:
    if end < start:
        raise ValueError("leave ends before it starts")
    if basis == "calendar_days":
        return Decimal((end - start).days + 1)
    return Decimal(working_days(start, end, holidays))


@dataclass(frozen=True)
class Policy:
    code: str
    leave_type: str
    cadre_code: str | None
    grade_level_min: int
    grade_level_max: int
    days_per_year: Decimal
    day_basis: str
    carry_over_max: Decimal


def select_policy(policies: Iterable[Policy], leave_type: str, cadre_code: str, grade_level: int) -> Policy | None:
    """Most specific policy for the leave type: a cadre-specific rule beats a general one."""
    fits = [
        p
        for p in policies
        if p.leave_type == leave_type
        and p.grade_level_min <= grade_level <= p.grade_level_max
        and p.cadre_code in (None, cadre_code)
    ]
    fits.sort(key=lambda p: (p.cadre_code is None, p.grade_level_max - p.grade_level_min))
    return fits[0] if fits else None


def available(entitled: Decimal, carried_over: Decimal, taken: Decimal, pending: Decimal) -> Decimal:
    return entitled + carried_over - taken - pending
