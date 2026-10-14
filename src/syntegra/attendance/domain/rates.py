"""Attendance arithmetic (Book 3 §7.2).

Codes: P present, L late (present), AA approved activity (present, off-site), A absent unauthorised,
M medical (authorised absence), E excused (authorised absence), NR not required (removed from possible
sessions). Rate = attended ÷ possible; persistent absence < 90 %, severe < 50 % (state policy may tighten).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

CODES = ("P", "L", "A", "M", "E", "AA", "NR")
PRESENT = {"P", "L", "AA"}
AUTHORISED = {"M", "E"}
UNAUTHORISED = {"A"}
NOT_POSSIBLE = {"NR"}


@dataclass(frozen=True)
class Summary:
    possible: int
    attended: int
    authorised_absence: int
    unauthorised_absence: int
    late: int

    @property
    def rate(self) -> float | None:
        return round(self.attended / self.possible, 4) if self.possible else None


def summarise(codes: Iterable[str]) -> Summary:
    c = Counter(codes)
    unknown = set(c) - set(CODES)
    if unknown:
        raise ValueError(f"unknown attendance codes {sorted(unknown)}")
    possible = sum(n for k, n in c.items() if k not in NOT_POSSIBLE)
    return Summary(
        possible=possible,
        attended=sum(c[k] for k in PRESENT),
        authorised_absence=sum(c[k] for k in AUTHORISED),
        unauthorised_absence=sum(c[k] for k in UNAUTHORISED),
        late=c["L"],
    )


def validate_mark(code: str, minutes_late: int | None) -> list[str]:
    errs = []
    if code not in CODES:
        errs.append(f"unknown code {code}")
    if code == "L" and (minutes_late is None or minutes_late <= 0):
        errs.append("late marks need minutes late")
    if code != "L" and minutes_late:
        errs.append("minutes late only apply to code L")
    return errs
