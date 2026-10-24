"""Proactive facility rules (FR-EST-04) — pure.

Given what is known about one facility (its latest assessments, planned maintenance and, for equipment, service
and safety dates), propose the actions the head of institution should take, each with a priority, an owner and a
due date. The platform proposes and escalates; the head decides.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

GRADES = {"good": 0, "fair": 1, "poor": 2, "unsafe": 3}
UNSAFE = ("unsafe_restricted", "unusable", "condemned")
USABLE = ("fully_usable", "usable_minor_repairs", "usable_major_repairs")
REASSESS_DAYS = {"site": 365, "building": 365, "room": 365, "asset": 365}
# days to act, by priority; and days after the due date before each escalation step (LGA, then ministry)
DUE_DAYS = {"critical": 2, "high": 7, "moderate": 30, "info": 60}
ESCALATE_AFTER = {"critical": 2, "high": 7, "moderate": 14, "info": 30}


@dataclass(frozen=True)
class Assessment:
    assessed_on: dt.date
    condition_grade: str
    usability: str
    in_use: bool
    next_due_on: dt.date | None = None


@dataclass(frozen=True)
class Schedule:
    id: str
    task: str
    next_due_on: dt.date


@dataclass
class Facility:
    kind: str  # site, building, room, asset
    id: str
    name: str
    assessments: list[Assessment] = field(default_factory=list)  # newest first
    schedules: list[Schedule] = field(default_factory=list)
    safety_check_due_on: dt.date | None = None
    predicted_failure_on: dt.date | None = None
    in_service: bool = True  # equipment in use
    encroachment: str | None = None
    title_document: str | None = None
    government_owned: bool = True


@dataclass(frozen=True)
class Proposal:
    rule: str
    subject_kind: str
    subject_id: str
    key: str  # one open action per key
    title: str
    detail: str
    priority: str
    due_on: dt.date
    owner_role: str = "HEAD"


def _p(
    f: Facility,
    rule: str,
    title: str,
    detail: str,
    priority: str,
    on: dt.date,
    *,
    due: dt.date | None = None,
    suffix: str = "",
) -> Proposal:
    return Proposal(
        rule,
        f.kind,
        f.id,
        f"{rule}:{f.id}{suffix}",
        title,
        detail,
        priority,
        due or on + dt.timedelta(DUE_DAYS[priority]),
    )


def evaluate(f: Facility, on: dt.date) -> list[Proposal]:
    out: list[Proposal] = []
    latest = f.assessments[0] if f.assessments else None
    if latest is None:
        if f.kind in ("site", "building", "room"):
            out.append(
                _p(
                    f,
                    "never_assessed",
                    f"Assess {f.name}",
                    "No condition and usability assessment is on record.",
                    "moderate",
                    on,
                )
            )
    else:
        if latest.usability in UNSAFE and latest.in_use:
            out.append(
                _p(
                    f,
                    "unsafe_in_use",
                    f"Stop using {f.name} until it is made safe",
                    f"Assessed {latest.usability.replace('_', ' ')} on {latest.assessed_on:%d %b %Y} "
                    "and recorded in use. "
                    "Move learners and staff, restrict access, and raise a work order.",
                    "critical",
                    on,
                )
            )
        due = latest.next_due_on or latest.assessed_on + dt.timedelta(REASSESS_DAYS[f.kind])
        if due < on:
            out.append(
                _p(
                    f,
                    "assessment_overdue",
                    f"Reassess {f.name}",
                    f"The assessment was due on {due:%d %b %Y}.",
                    "moderate",
                    on,
                )
            )
        if len(f.assessments) > 1:
            before = f.assessments[1]
            drop = GRADES.get(latest.condition_grade, 0) - GRADES.get(before.condition_grade, 0)
            if drop >= 2 or (drop >= 1 and latest.condition_grade == "unsafe"):
                out.append(
                    _p(
                        f,
                        "condition_deteriorated",
                        f"Condition of {f.name} is deteriorating",
                        f"{before.condition_grade} on {before.assessed_on:%d %b %Y} → {latest.condition_grade} on "
                        f"{latest.assessed_on:%d %b %Y}. Plan repairs before it becomes unsafe.",
                        "high",
                        on,
                        suffix=f":{latest.assessed_on:%Y%m%d}",
                    )
                )
    for s in f.schedules:
        if s.next_due_on < on:
            out.append(
                _p(
                    f,
                    "maintenance_overdue",
                    f"Overdue: {s.task}",
                    f"{s.task} for {f.name} was due on {s.next_due_on:%d %b %Y}.",
                    "high",
                    on,
                    suffix=f":{s.id}",
                )
            )
        elif s.next_due_on <= on + dt.timedelta(14):
            out.append(
                _p(
                    f,
                    "maintenance_due",
                    f"Due soon: {s.task}",
                    f"{s.task} for {f.name} is due on {s.next_due_on:%d %b %Y}.",
                    "info",
                    on,
                    due=s.next_due_on,
                    suffix=f":{s.id}",
                )
            )
    if f.kind == "asset" and f.in_service:
        if f.safety_check_due_on and f.safety_check_due_on < on:
            out.append(
                _p(
                    f,
                    "safety_check_overdue",
                    f"Safety check overdue: {f.name}",
                    f"The safety check was due on {f.safety_check_due_on:%d %b %Y}; do not allocate it until checked.",
                    "high",
                    on,
                )
            )
        if f.predicted_failure_on and on <= f.predicted_failure_on <= on + dt.timedelta(30):
            out.append(
                _p(
                    f,
                    "predicted_failure",
                    f"Likely to fail soon: {f.name}",
                    f"Predicted to fail around {f.predicted_failure_on:%d %b %Y}; service or replace it first.",
                    "moderate",
                    on,
                    due=f.predicted_failure_on,
                )
            )
    if f.kind == "site":
        if f.encroachment in ("suspected", "confirmed", "in_dispute"):
            out.append(
                _p(
                    f,
                    "encroachment",
                    f"Encroachment on {f.name}",
                    f"Encroachment {f.encroachment.replace('_', ' ')}: notify the ministry and the land registry.",
                    "high",
                    on,
                )
            )
        if f.government_owned and f.title_document in (None, "none_or_unknown", "survey_plan_only"):
            out.append(
                _p(
                    f,
                    "no_title",
                    f"Secure title to {f.name}",
                    "The site has no certificate of occupancy, gazette or deed on record.",
                    "moderate",
                    on,
                )
            )
    return out


def escalation(priority: str, due_on: dt.date, level: int, on: dt.date) -> int:
    """The escalation level an open action should be at: 1 (LGA) once it passes its due date by the priority's
    grace period, 2 (ministry) after twice that."""
    late = (on - due_on).days
    step = ESCALATE_AFTER[priority]
    target = 0 if late <= 0 else 1 if late <= 2 * step else 2
    return max(level, target)


def infrastructure_index(
    classrooms: int,
    usable: int,
    institutions: int,
    with_water: int,
    with_power: int,
    unsafe_in_use: int,
    actions_due: int,
    actions_overdue: int,
) -> float | None:
    """0–100: usable classrooms (40), water and power (20), safety — no unsafe facility in use (20), maintenance and
    actions on time (20)."""
    if not institutions:
        return None
    a = 40 * (usable / classrooms if classrooms else 0)
    b = 10 * with_water / institutions + 10 * with_power / institutions
    c = 20 * max(0.0, 1 - unsafe_in_use / institutions)
    d = 20 * (1 - actions_overdue / actions_due) if actions_due else 20
    return round(a + b + c + d, 2)
