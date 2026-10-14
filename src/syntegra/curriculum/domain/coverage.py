"""Coverage invariants (MFS §5.3–5.4). Pure evaluation of class-subject facts into gap decisions.

The engine is given facts about each class-subject (teachers of record, their authorisation, load) and
returns the set of breached rules. Persisting, deduplicating (one open gap per rule per target), owning,
escalating and closing gaps is the service's job.
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field

SEVERITY = {"g1": "critical", "g2": "critical", "g3": "high", "g4": "high", "g5": "moderate", "g6": "moderate",
            "g7": "moderate", "g8": "high", "g9": "critical", "g11": "moderate", "g12": "critical"}
OWNER = {"g1": "HT", "g2": "HT", "g3": "HT", "g11": "HT"}
DUE_SCHOOL_DAYS = {"g1": 5, "g2": 3, "g3": 10, "g11": 10}


@dataclass(frozen=True)
class ClassSubjectFacts:
    plan_id: uuid.UUID
    class_id: uuid.UUID
    subject_id: uuid.UUID
    level: str
    learners: int
    is_mandatory: bool
    teachers_of_record: list[uuid.UUID] = field(default_factory=list)  # staff ids
    authorised: dict[uuid.UUID, bool] = field(default_factory=dict)  # staff id → authorised for subject × level


@dataclass(frozen=True)
class Breach:
    rule: str
    plan_id: uuid.UUID
    severity: str
    detail: str
    staff_id: uuid.UUID | None = None


def evaluate(facts: ClassSubjectFacts) -> list[Breach]:
    out: list[Breach] = []
    if not facts.is_mandatory and not facts.teachers_of_record:
        return out
    if len(facts.teachers_of_record) != 1:
        n = len(facts.teachers_of_record)
        out.append(Breach("g2", facts.plan_id, SEVERITY["g2"],
                          "no teacher of record" if n == 0 else f"{n} teachers of record"))
    for staff in facts.teachers_of_record:
        if not facts.authorised.get(staff, False):
            out.append(Breach("g3", facts.plan_id, SEVERITY["g3"],
                              "teacher of record lacks a valid authorisation for the subject and level", staff))
    return out


def add_school_days(start: dt.date, days: int, closures: set[dt.date] | None = None) -> dt.date:
    """Due date in school days (Mon–Fri, skipping closures)."""
    d, left = start, days
    closures = closures or set()
    while left > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and d not in closures:
            left -= 1
    return d
