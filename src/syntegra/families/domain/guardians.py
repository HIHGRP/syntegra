"""Guardians at registration (FR-LRN-05, FR-LRN-06, FR-FAM-01, FR-FAM-02) — pure functions.

* A learner under the age of majority needs at least one guardian with parental responsibility. The age is a
  jurisdiction policy (``LRN-AGE-OF-MAJORITY``), never a constant in code; ``DEFAULT_MAJORITY`` applies only when a
  state has not published the rule.
* Guardians are person masters: before one is created the registry is searched by NIN, phone and e-mail, and a
  phone or e-mail is only accepted as the same person when the names agree too (families share phones).
* A guardian is never the learner: the minor's and the guardian's identities stay distinct.
"""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

DEFAULT_MAJORITY = 18  # Child's Rights Act 2003 — used only when the state has not published LRN-AGE-OF-MAJORITY
RESPONSIBLE_BY_DEFAULT = ("mother", "father", "legal_guardian", "foster_carer", "social_worker", "step_parent")
RELATIONSHIPS = (
    "mother", "father", "step_parent", "grandparent", "aunt_uncle", "sibling", "legal_guardian", "foster_carer",
    "social_worker", "sponsor", "other",
)  # fmt: skip
MAX_GUARDIANS = 6
NAME_AGREEMENT = 0.88
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class GuardianInput:
    given: str
    family: str
    relationship: str
    has_parental_responsibility: bool = True
    phone: str | None = None
    email: str | None = None
    nin: str | None = None
    title: str | None = None
    lives_with: bool = True
    is_authorised_collector: bool = True
    is_payer: bool = False
    preferred_language: str | None = None
    preferred_channel: str | None = None


class NameScorer(Protocol):
    def __call__(self, a: str, b: str) -> float: ...


def age_on(date_of_birth: dt.date, on: dt.date) -> int:
    return on.year - date_of_birth.year - ((on.month, on.day) < (date_of_birth.month, date_of_birth.day))


def is_minor(date_of_birth: dt.date, on: dt.date, majority: int) -> bool:
    return age_on(date_of_birth, on) < majority


def normalise_phone(raw: str | None, country_code: str = "234") -> str | None:
    """E.164: ``0803 123 4567`` / ``234803…`` / ``+234 803…`` → ``+2348031234567``; ``None`` if not a phone number."""
    if not raw or not raw.strip():
        return None
    digits = re.sub(r"\D", "", raw)
    if raw.strip().startswith("+") or digits.startswith(country_code):
        e164 = "+" + digits
    elif digits.startswith("0"):
        e164 = "+" + country_code + digits[1:]
    else:
        e164 = "+" + country_code + digits
    return e164 if 11 <= len(e164) <= 16 else None


def normalise_email(raw: str | None) -> str | None:
    e = (raw or "").strip().lower()
    return e or None


def errors_for(
    guardians: Sequence[GuardianInput],
    *,
    minor: bool,
    majority: int,
    existing_with_responsibility: int,
    learner_nin: str | None,
) -> list[dict[str, str | None]]:
    """Validation of the guardians given at registration (field names are ``guardians[i].<field>``)."""
    errs: list[dict[str, str | None]] = []
    if len(guardians) > MAX_GUARDIANS:
        errs.append({"field": "guardians", "message": f"at most {MAX_GUARDIANS} guardians at registration"})
    for i, g in enumerate(guardians):
        f = f"guardians[{i}]"
        if not g.given.strip() or not g.family.strip():
            errs.append({"field": f"{f}.name", "message": "given and family names are required"})
        if g.relationship not in RELATIONSHIPS:
            errs.append({"field": f"{f}.relationship", "message": "choose the relationship to the learner"})
        if g.phone and normalise_phone(g.phone) is None:
            errs.append({"field": f"{f}.phone", "message": "enter a valid phone number"})
        if g.email and not _EMAIL.match(g.email.strip()):
            errs.append({"field": f"{f}.email", "message": "enter a valid e-mail address"})
        if not (g.phone or g.email):
            errs.append(
                {"field": f"{f}.phone", "message": "give a phone number or e-mail so the school can reach them"}
            )
        if g.nin:
            nin = "".join(g.nin.split())
            if not nin.isdigit() or len(nin) != 11:
                errs.append({"field": f"{f}.nin", "message": "NIN has 11 digits"})
            elif learner_nin and nin == "".join(learner_nin.split()):
                errs.append({"field": f"{f}.nin", "message": "a guardian cannot have the learner's NIN"})
    if minor and existing_with_responsibility == 0 and not any(g.has_parental_responsibility for g in guardians):
        errs.append(
            {
                "field": "guardians",
                "message": f"learners under {majority} need at least one guardian with parental responsibility "
                "(a social worker or foster carer where the child is in care)",
            }
        )
    return errs


def same_person(
    given: GuardianInput,
    candidate_given: str,
    candidate_family: str,
    *,
    nin_matches: bool,
    phone_matches: bool,
    email_matches: bool,
    name_score: NameScorer,
) -> bool:
    """FR-FAM-01: NIN alone identifies; phone or e-mail only together with agreeing names."""
    if nin_matches:
        return True
    if not (phone_matches or email_matches):
        return False
    return (
        name_score(given.family, candidate_family) >= NAME_AGREEMENT
        and name_score(given.given, candidate_given) >= NAME_AGREEMENT
    )
