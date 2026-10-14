"""Programme eligibility rules (FR-FND-02) — pure. Rules inform the reviewer; they never decide.

A programme's ``eligibility`` is a mapping of rule → parameter. Facts describe the applicant and its institution.
Every rule present is evaluated and reported, so the reviewer sees why an applicant is or is not eligible.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TERTIARY = (
    "ND",
    "HND",
    "NCE",
    "UG100",
    "UG200",
    "UG300",
    "UG400",
    "UG500",
    "UG600",
    "UG700",
    "PG",
    "NURSING",
    "HEALTH_TECH",
)


@dataclass(frozen=True)
class Result:
    rule: str
    passed: bool
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {"rule": self.rule, "passed": self.passed, "detail": self.detail}


def _level_ok(levels: list[str], level: str | None) -> bool:
    if not level:
        return False
    allowed = {x.upper() for x in levels}
    if "TERTIARY" in allowed:
        allowed |= set(TERTIARY)
    return level.upper() in allowed


def evaluate(rules: dict[str, Any] | None, facts: dict[str, Any]) -> list[Result]:
    out: list[Result] = []
    for rule, param in (rules or {}).items():
        if rule == "ownership":
            v = facts.get("ownership")
            out.append(Result(rule, v in param, f"institution ownership is {v}; programme covers {', '.join(param)}"))
        elif rule == "categories":
            v = facts.get("category")
            out.append(Result(rule, v in param, f"institution category is {v}"))
        elif rule == "education_levels":
            v = facts.get("education_level")
            out.append(Result(rule, _level_ok(list(param), v), f"current level is {v or 'not enrolled'}"))
        elif rule == "actively_enrolled":
            v = bool(facts.get("actively_enrolled"))
            out.append(Result(rule, v or not param, "has an active enrolment" if v else "no active enrolment"))
        elif rule == "min_service_years":
            v = facts.get("service_years")
            ok = v is not None and v >= param
            out.append(Result(rule, ok, f"{v if v is not None else 'unknown'} years of service; {param} required"))
        elif rule == "confirmed_appointment":
            v = facts.get("appointment_status")
            out.append(Result(rule, v == "confirmed" or not param, f"appointment is {v or 'unknown'}"))
        elif rule == "max_amount_minor":
            v = facts.get("amount_minor", 0)
            out.append(Result(rule, v <= param, f"requested ₦{v / 100:,.2f}; ceiling ₦{param / 100:,.2f}"))
        elif rule == "max_household_income_minor":
            v = facts.get("household_income_minor")
            ok = v is not None and v <= param
            out.append(
                Result(
                    rule,
                    ok,
                    "declared household income within the ceiling"
                    if ok
                    else "income above the ceiling or not declared",
                )
            )
        elif rule == "matching_contribution_pct":
            v = facts.get("matching_contribution_pct")
            ok = v is not None and v >= param
            out.append(
                Result(rule, ok, f"counterpart contribution {v if v is not None else 'not stated'}%; {param}% required")
            )
        else:
            out.append(Result(rule, False, "rule not recognised — review manually"))
    return out


def eligible(results: list[Result]) -> bool:
    return all(r.passed for r in results)
