"""Probabilistic identity matching for learners (MFS §13.5, Book 3 §12.1).

A Fellegi–Sunter-style model: each compared attribute contributes a log-likelihood weight (agreement
raises the odds that two records are the same child, disagreement lowers them); the sum plus a prior
for a random pair within a blocking group is mapped to a probability with the logistic function.

Bands (state policy may tighten): ≥ 0.98 auto-link (still logged); 0.80–0.98 human review;
< 0.80 distinct. Evidence is kept so a steward sees *why* two records were proposed.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field
from typing import Any

from syntegra.core.text import canonical_given, jaro_winkler, normalise_name

AUTO_LINK = 0.98
REVIEW = 0.80
PRIOR = -6.0
MODEL_VERSION = "fs-ng-1.0"


@dataclass(frozen=True)
class Person:
    given: str
    family: str
    date_of_birth: dt.date
    sex: str
    dob_precision: str = "day"
    nin: str | None = None  # plaintext only at the point of capture; stored records compare by HMAC
    nin_hmac: bytes | None = None


@dataclass
class MatchResult:
    score: float
    band: str
    weight: float
    evidence: list[dict[str, Any]] = field(default_factory=list)


def _name_weight(a: str, b: str, *, given: bool) -> tuple[float, float]:
    if given:
        sim = max(
            jaro_winkler(canonical_given(a), canonical_given(b)), jaro_winkler(normalise_name(a), normalise_name(b))
        )
    else:
        sim = jaro_winkler(normalise_name(a), normalise_name(b))
    hi, mid = (4.0, 1.5) if given else (4.5, 2.0)
    if sim >= 0.97:
        return hi, sim
    if sim >= 0.88:
        return mid, sim
    return -3.0, sim


def _dob_weight(a: Person, b: Person) -> tuple[float, str]:
    da, db = a.date_of_birth, b.date_of_birth
    if "year" in (a.dob_precision, b.dob_precision):
        return (1.0, "same year (low precision)") if da.year == db.year else (-4.0, "different year")
    if da == db:
        return 5.0, "exact"
    if da.year == db.year and da.month == db.day and da.day == db.month:
        return 0.5, "day/month transposed"
    if abs((da - db).days) <= 31 and "month" in (a.dob_precision, b.dob_precision):
        return 1.5, "same month (low precision)"
    return -5.0, "different"


def compare(a: Person, b: Person) -> MatchResult:
    ev: list[dict[str, Any]] = []
    w = 0.0
    if a.nin_hmac and b.nin_hmac:
        if a.nin_hmac == b.nin_hmac:
            w += 12.0
            ev.append({"field": "nin", "result": "agree", "weight": 12.0})
        else:
            w -= 10.0
            ev.append({"field": "nin", "result": "disagree", "weight": -10.0})
    gw, gs = _name_weight(a.given, b.given, given=True)
    fw, fs = _name_weight(a.family, b.family, given=False)
    dw, dr = _dob_weight(a, b)
    sw = 0.5 if a.sex == b.sex else -4.0
    w += gw + fw + dw + sw
    ev += [
        {"field": "given_name", "similarity": round(gs, 3), "weight": gw},
        {"field": "family_name", "similarity": round(fs, 3), "weight": fw},
        {"field": "date_of_birth", "result": dr, "weight": dw},
        {"field": "sex", "result": "agree" if sw > 0 else "disagree", "weight": sw},
    ]
    score = 1.0 / (1.0 + math.exp(-(w + PRIOR)))
    band = "auto_link" if score >= AUTO_LINK else "review" if score >= REVIEW else "distinct"
    return MatchResult(round(score, 6), band, round(w, 2), ev)


def best(candidate: Person, existing: list[tuple[Any, Person]]) -> list[tuple[Any, MatchResult]]:
    """Score ``candidate`` against existing records, best first, dropping distinct pairs."""
    scored = [(key, compare(candidate, p)) for key, p in existing]
    return sorted([s for s in scored if s[1].band != "distinct"], key=lambda s: -s[1].score)
