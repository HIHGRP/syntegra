"""Access levels (CR-007, FR-ADM-201): five named levels over the data classifications (MFS §2.2).

A role's ``clearance`` is its access level; a grant's ``clearance_cap`` can lower it for one user. The effective level
of the active grant decides which pages, menu items, fields and documents the user can see: anything classified above
it is withheld (pages refuse, menus hide, ``authz.visible_fields`` trims fields, document queries filter).
"""

from __future__ import annotations

from dataclasses import dataclass

from syntegra.core.context import CLASS_ORDER, class_rank


@dataclass(frozen=True)
class Level:
    number: int
    classification: str
    name: str
    sees: str

    @property
    def label(self) -> str:
        return f"Level {self.number} · {self.name}"


LEVELS: tuple[Level, ...] = (
    Level(
        1,
        "public",
        "Public",
        "Published information anyone may see: certificate checks, regulators, public directories.",
    ),
    Level(
        2,
        "internal",
        "Internal",
        "Working information for staff: registers, timetables, aggregates, facilities, budgets at summary level.",
    ),
    Level(
        3,
        "confidential",
        "Confidential",
        "Personal records of learners, families and staff: names, results, attendance, contact details, documents.",
    ),
    Level(
        4,
        "restricted",
        "Restricted",
        "Sensitive records: HR and payroll, investigations, special needs, discipline, loans — a declared purpose is"
        " required and every access is audited.",
    ),
    Level(
        5,
        "special",
        "Special",
        "Special-category data: safeguarding and health — named, cleared users only, never indexed or exported.",
    ),
)
BY_CLASS = {lv.classification: lv for lv in LEVELS}
assert tuple(lv.classification for lv in LEVELS) == CLASS_ORDER


def level(classification: str | None) -> Level:
    """The level of a classification; unknown or missing classifications count as Internal (level 2)."""
    c = (classification or "internal").strip().lower()
    return BY_CLASS.get(c, BY_CLASS["internal"])


def covers(clearance: str | None, classification: str | None) -> bool:
    return class_rank(clearance) >= class_rank(level(classification).classification)


def lower_or_equal(clearance: str | None) -> list[Level]:
    """Levels at or below a clearance — the caps an administrator at that level may set."""
    return [lv for lv in LEVELS if lv.number <= level(clearance).number]
