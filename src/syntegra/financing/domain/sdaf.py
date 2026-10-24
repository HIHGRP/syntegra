"""SDAF census arithmetic (MFS §19.3–19.5) — pure functions."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Iterable
from dataclasses import dataclass

BASIC_LEVELS = {
    "primary_1",
    "primary_2",
    "primary_3",
    "primary_4",
    "primary_5",
    "primary_6",
    "jss_1",
    "jss_2",
    "jss_3",
    "primary",
    "jss",
}


def is_basic_education(level: str, public: bool) -> bool:
    """Public primary and junior secondary: free under the UBE Act 2004 (government pays)."""
    return public and (level.lower() in BASIC_LEVELS or level.lower().startswith(("primary", "jss")))


@dataclass(frozen=True)
class CensusInput:
    learner_id: uuid.UUID
    enrolment_id: uuid.UUID
    verified: bool


@dataclass(frozen=True)
class CensusLine:
    learner_id: uuid.UUID
    enrolment_id: uuid.UUID
    inclusion: str  # billable | exempt | excluded
    reason: str | None
    verified: bool


def classify(
    rows: Iterable[CensusInput], *, billed_elsewhere: set[uuid.UUID], exempt: set[uuid.UUID]
) -> list[CensusLine]:
    seen: set[uuid.UUID] = set()
    out = []
    for r in rows:
        if r.learner_id in seen:
            out.append(CensusLine(r.learner_id, r.enrolment_id, "excluded", "duplicate", r.verified))
            continue
        seen.add(r.learner_id)
        if r.learner_id in billed_elsewhere:
            out.append(CensusLine(r.learner_id, r.enrolment_id, "excluded", "other_institution_holds", r.verified))
        elif r.learner_id in exempt:
            out.append(CensusLine(r.learner_id, r.enrolment_id, "exempt", "exempt", r.verified))
        else:
            out.append(CensusLine(r.learner_id, r.enrolment_id, "billable", None, r.verified))
    return out


def totals(lines: list[CensusLine]) -> dict[str, int]:
    return {
        "enrolled": len({ln.learner_id for ln in lines}),
        "verified": sum(1 for ln in lines if ln.verified),
        "billable": sum(1 for ln in lines if ln.inclusion == "billable"),
        "exempt": sum(1 for ln in lines if ln.inclusion == "exempt"),
        "excluded": sum(1 for ln in lines if ln.inclusion == "excluded"),
    }


def content_hash(pairs: Iterable[tuple[uuid.UUID, str]]) -> bytes:
    h = hashlib.sha256()
    for learner, inclusion in sorted(pairs, key=lambda p: p[0].bytes):
        h.update(learner.bytes + inclusion.encode() + b"\n")
    return h.digest()


def amount(billable: int, waived: int, rate_minor: int) -> int:
    if waived > billable:
        raise ValueError("waived exceeds billable")
    return (billable - waived) * rate_minor
