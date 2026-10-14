"""Duplicate-institution detection at registration (FR-INS-02): name similarity within the LGA and distance.

* same government registration number → hard stop;
* name similarity ≥ 0.92 within the LGA, or ≥ 0.75 within 500 m → probable duplicate (soft warning,
  continue only with a recorded reason);
* any institution within 50 m → soft warning (shared compound — common for public primary/JSS pairs).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from syntegra.core.text import jaro_winkler, normalise_name

STOP = {"school", "schools", "the", "of", "and", "college", "academy", "nursery", "primary", "secondary",
        "community", "comprehensive", "model", "international", "ltd", "limited", "group"}


def name_key(name: str) -> str:
    return " ".join(w for w in normalise_name(name).split() if w not in STOP) or normalise_name(name)


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distance in metres between (lon, lat) points."""
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_008.8 * math.asin(math.sqrt(h))


@dataclass(frozen=True)
class Candidate:
    key: Any
    name: str
    gov_reg_no: str | None
    location: tuple[float, float] | None
    category: str


@dataclass(frozen=True)
class Finding:
    key: Any
    level: str  # hard | soft
    reason: str
    similarity: float
    distance_m: float | None


def check(name: str, gov_reg_no: str | None, location: tuple[float, float] | None, category: str,
          existing: list[Candidate]) -> list[Finding]:
    out: list[Finding] = []
    nk = name_key(name)
    for c in existing:
        sim = jaro_winkler(nk, name_key(c.name))
        dist = haversine_m(location, c.location) if location and c.location else None
        if gov_reg_no and c.gov_reg_no and gov_reg_no.strip().upper() == c.gov_reg_no.strip().upper():
            out.append(Finding(c.key, "hard", "same government registration number", sim, dist))
        elif sim >= 0.92 and c.category == category:
            out.append(Finding(c.key, "soft", "very similar name in the same LGA", sim, dist))
        elif dist is not None and dist <= 500 and sim >= 0.75:
            out.append(Finding(c.key, "soft", "similar name within 500 m", sim, dist))
        elif dist is not None and dist <= 50:
            out.append(Finding(c.key, "soft", "another institution within 50 m", sim, dist))
    return sorted(out, key=lambda f: (f.level != "hard", -f.similarity))
