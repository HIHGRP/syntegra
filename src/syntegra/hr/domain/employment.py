"""Employment rules: statutory retirement, confirmation and promotion eligibility."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


def add_years(d: dt.date, years: int) -> dt.date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 February
        return d.replace(year=d.year + years, day=28)


def retirement_due(
    date_of_birth: dt.date | None, first_appointment_on: dt.date, retirement_age: int, max_years_service: int
) -> tuple[dt.date, str]:
    """Earlier of the retirement age and the maximum years of service.

    Teachers: 65 years of age or 40 years of service (Harmonised Retirement Age for Teachers in Nigeria Act 2022);
    other public servants: 60 or 35 (Public Service Rules). Values come from the cadre, never from code.
    """
    by_service = add_years(first_appointment_on, max_years_service)
    if date_of_birth is None:
        return by_service, "length_of_service"
    by_age = add_years(date_of_birth, retirement_age)
    return (by_age, "age") if by_age <= by_service else (by_service, "length_of_service")


def confirmation_due(present_appointment_on: dt.date, probation_months: int = 24) -> dt.date:
    m = present_appointment_on.month - 1 + probation_months
    y = present_appointment_on.year + m // 12
    day = min(present_appointment_on.day, 28)
    return dt.date(y, m % 12 + 1, day)


@dataclass(frozen=True)
class PromotionCheck:
    name: str
    passed: bool
    detail: str


def promotion_eligibility(
    *,
    on: dt.date,
    grade_level: int,
    max_grade_level: int,
    last_promotion_on: dt.date | None,
    present_appointment_on: dt.date,
    years_per_promotion: int,
    open_disciplinary: bool,
    confirmed: bool,
    last_rating: str | None,
) -> list[PromotionCheck]:
    since = last_promotion_on or present_appointment_on
    years = (on - since).days / 365.25
    return [
        PromotionCheck(
            "below_cadre_ceiling", grade_level < max_grade_level, f"GL {grade_level} of max {max_grade_level}"
        ),
        PromotionCheck("years_on_grade", years >= years_per_promotion, f"{years:.1f} of {years_per_promotion} years"),
        PromotionCheck("confirmed_in_service", confirmed, "confirmed" if confirmed else "on probation"),
        PromotionCheck(
            "no_open_disciplinary_case", not open_disciplinary, "clear" if not open_disciplinary else "case open"
        ),
        PromotionCheck(
            "appraisal", last_rating not in ("unsatisfactory", "poor"), f"last rating {last_rating or 'not recorded'}"
        ),
    ]
