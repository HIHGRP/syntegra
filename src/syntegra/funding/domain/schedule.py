"""Repayment schedules (FR-FND-03) — pure functions on integer minor units.

Bases:
* ``annuity`` and ``payroll_deduction`` — equal monthly payments (the last absorbs rounding);
* ``fixed_instalment`` — equal principal each month plus interest on the declining balance;
* ``bullet`` — interest monthly, principal at the end;
* ``income_contingent`` and ``none`` — no fixed schedule (student loans repaid as a share of earnings once the
  borrower is employed; grants, scholarships and bursaries are not repaid).

The moratorium is interest-free unless ``capitalise`` is set, in which case interest accrues and is added to the
principal before the first instalment.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

NO_SCHEDULE = ("income_contingent", "none")


@dataclass(frozen=True)
class Instalment:
    sequence: int
    due_on: dt.date
    principal: int
    interest: int

    @property
    def total(self) -> int:
        return self.principal + self.interest


def add_months(d: dt.date, months: int) -> dt.date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    last = [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return dt.date(year, month, min(d.day, last[month - 1]))


def _round(x: Decimal) -> int:
    return int(x.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def build(
    principal: int,
    annual_rate_pct: Decimal | float | int,
    tenor_months: int | None,
    basis: str,
    first_due: dt.date,
    *,
    moratorium_months: int = 0,
    capitalise: bool = False,
) -> list[Instalment]:
    if basis in NO_SCHEDULE or principal <= 0:
        return []
    if not tenor_months or tenor_months <= 0:
        raise ValueError("a repayable facility needs a tenor in months")
    r = Decimal(str(annual_rate_pct)) / Decimal(1200)
    p = Decimal(principal)
    if capitalise and moratorium_months and r:
        p = p * (1 + r) ** moratorium_months
    n = tenor_months
    out: list[Instalment] = []
    balance = p
    if basis in ("annuity", "payroll_deduction"):
        payment = p / n if r == 0 else p * r / (1 - (1 + r) ** -n)
        for k in range(1, n + 1):
            interest = balance * r
            princ = balance if k == n else payment - interest
            out.append(Instalment(k, add_months(first_due, k - 1), _round(princ), _round(interest)))
            balance -= princ
    elif basis == "fixed_instalment":
        each = p / n
        for k in range(1, n + 1):
            interest = balance * r
            princ = balance if k == n else each
            out.append(Instalment(k, add_months(first_due, k - 1), _round(princ), _round(interest)))
            balance -= princ
    elif basis == "bullet":
        for k in range(1, n + 1):
            out.append(Instalment(k, add_months(first_due, k - 1), _round(p) if k == n else 0, _round(p * r)))
    else:
        raise ValueError(f"unknown repayment basis {basis!r}")
    # rounding: principal instalments sum exactly to the (capitalised) principal
    drift = _round(p) - sum(i.principal for i in out)
    if drift:
        last = out[-1]
        out[-1] = Instalment(last.sequence, last.due_on, last.principal + drift, last.interest)
    return out


def allocate(amount: int, due: list[tuple[int, int, int]]) -> tuple[dict[int, int], int]:
    """Allocate a repayment to instalments oldest first. ``due`` is (sequence, total due, already paid) in due-date
    order. Returns ({sequence: amount}, unallocated remainder)."""
    out: dict[int, int] = {}
    left = amount
    for seq, total, paid in due:
        if left <= 0:
            break
        take = min(left, total - paid)
        if take > 0:
            out[seq] = take
            left -= take
    return out, left


def principal_paid(paid: int, interest: int, principal: int) -> int:
    """Interest is settled first within an instalment, then principal."""
    return max(0, min(principal, paid - interest))


def affordable(gross: int, other_deductions: int, floor_fraction: Decimal | float = Decimal(1) / 3) -> int:
    """The largest monthly deduction that keeps net pay at or above ``floor_fraction`` of gross (FR-FND-06)."""
    floor = _round(Decimal(gross) * Decimal(str(floor_fraction)))
    return max(0, gross - other_deductions - floor)
