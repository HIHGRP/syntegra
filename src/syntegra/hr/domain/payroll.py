"""Payroll arithmetic for Nigerian employers, in kobo (integers only).

Statutory parameters are *data* (versioned ``payroll_tax_table`` rows); the defaults below exist so a new
tenant computes correctly on day one and are the values in force for 2026:

* PAYE — Nigeria Tax Act 2025 (effective 1 January 2026) annual bands: first ₦800,000 at 0%, next ₦2.2m at 15%,
  next ₦9m at 18%, next ₦13m at 21%, next ₦25m at 23%, above ₦50m at 25%; the consolidated relief allowance is
  abolished; pension, NHF and NHIS contributions are deductible, and rent relief is 20% of rent paid up to ₦500,000.
* Pension — Pension Reform Act 2014: employee 8%, employer 10% of monthly emoluments (basic + housing + transport).
* NHF — 2.5% of basic salary.

The tables must be confirmed by the employer's payroll and tax advisers before go-live; changing a rate is a new
table version, never a code change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

KOBO = 100
DEFAULT_PAYE_BANDS: list[dict[str, Any]] = [
    {"upto": 800_000 * KOBO, "rate_bp": 0},
    {"upto": 3_000_000 * KOBO, "rate_bp": 1500},
    {"upto": 12_000_000 * KOBO, "rate_bp": 1800},
    {"upto": 25_000_000 * KOBO, "rate_bp": 2100},
    {"upto": 50_000_000 * KOBO, "rate_bp": 2300},
    {"upto": None, "rate_bp": 2500},
]
DEFAULT_PENSION: dict[str, Any] = {"employee_bp": 800, "employer_bp": 1000, "base": ["BASIC", "HOUSING", "TRANSPORT"]}
DEFAULT_NHF: dict[str, Any] = {"employee_bp": 250, "base": ["BASIC"]}
RENT_RELIEF_BP, RENT_RELIEF_CAP = 2000, 500_000 * KOBO


def pct(amount: int, bp: int) -> int:
    """``amount × bp / 10 000`` rounded half up, in kobo."""
    return (amount * bp + 5000) // 10000


def annual_paye(taxable_annual: int, bands: list[dict[str, Any]] | None = None) -> int:
    bands = bands or DEFAULT_PAYE_BANDS
    tax, lower = 0, 0
    for b in bands:
        upper = b["upto"]
        if taxable_annual <= lower:
            break
        slice_top = taxable_annual if upper is None else min(taxable_annual, int(upper))
        tax += pct(slice_top - lower, int(b["rate_bp"]))
        if upper is None:
            break
        lower = int(upper)
    return tax


@dataclass
class Element:
    code: str
    kind: (
        str  # earning | allowance | statutory_deduction | voluntary_deduction | loan_repayment | employer_contribution
    )
    amount: int
    taxable: bool = True
    pensionable: bool = False


@dataclass
class Payslip:
    gross: int
    deductions: int
    net: int
    employer_cost: int
    lines: list[dict[str, Any]] = field(default_factory=list)


def compute_month(
    basic_annual: int,
    allowances_monthly: dict[str, int],
    *,
    other_elements: tuple[Element, ...] = (),
    paye_bands: list[dict[str, Any]] | None = None,
    pension: dict[str, Any] | None = None,
    nhf: dict[str, Any] | None = None,
    annual_rent: int = 0,
    versions: dict[str, int] | None = None,
) -> Payslip:
    pension = pension or DEFAULT_PENSION
    nhf = nhf or DEFAULT_NHF
    basic = (basic_annual + 6) // 12
    earnings: dict[str, int] = {"BASIC": basic, **allowances_monthly}
    lines: list[dict[str, Any]] = [{"code": k, "kind": "earning", "amount": v} for k, v in earnings.items()]
    voluntary = 0
    for e in other_elements:
        if e.kind in ("earning", "allowance"):
            earnings[e.code] = earnings.get(e.code, 0) + e.amount
            lines.append({"code": e.code, "kind": e.kind, "amount": e.amount})
        elif e.kind in ("voluntary_deduction", "loan_repayment"):
            voluntary += e.amount
            lines.append({"code": e.code, "kind": e.kind, "amount": -e.amount})
    gross = sum(earnings.values())
    pensionable = sum(earnings.get(c, 0) for c in pension["base"])
    pension_ee = pct(pensionable, int(pension["employee_bp"]))
    pension_er = pct(pensionable, int(pension["employer_bp"]))
    nhf_ee = pct(sum(earnings.get(c, 0) for c in nhf["base"]), int(nhf["employee_bp"]))
    rent_relief = min(pct(annual_rent, RENT_RELIEF_BP), RENT_RELIEF_CAP)
    taxable_annual = max(0, gross * 12 - (pension_ee + nhf_ee) * 12 - rent_relief)
    paye = (annual_paye(taxable_annual, paye_bands) + 6) // 12
    lines += [
        {"code": "PENSION_EE", "kind": "statutory_deduction", "amount": -pension_ee},
        {"code": "NHF", "kind": "statutory_deduction", "amount": -nhf_ee},
        {"code": "PAYE", "kind": "statutory_deduction", "amount": -paye, "taxable_annual": taxable_annual},
        {"code": "PENSION_ER", "kind": "employer_contribution", "amount": pension_er},
    ]
    if versions:
        lines.append({"code": "_TABLES", "kind": "meta", "versions": versions})
    deductions = pension_ee + nhf_ee + paye + voluntary
    return Payslip(gross, deductions, gross - deductions, gross + pension_er, lines)
