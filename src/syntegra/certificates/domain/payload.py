"""Signed certificate payload (MFS §15.4): minimal disclosure, canonicalised with RFC 8785 before signing."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

PAYLOAD_VERSION = 1


@dataclass(frozen=True)
class Award:
    number: str
    kind: str
    holder: str
    glid: str
    institution_code: str
    institution_name: str
    title: str
    award_class: str | None
    award_date: dt.date
    authority: str
    kid: str
    issued_at: dt.datetime


def build(a: Award) -> dict[str, Any]:
    """Only what a verifier needs to match the paper: no date of birth, no identifiers beyond the GLID."""
    return {
        "v": PAYLOAD_VERSION,
        "number": a.number,
        "kind": a.kind,
        "holder": a.holder,
        "glid": a.glid,
        "institution": {"code": a.institution_code, "name": a.institution_name},
        "award": {"title": a.title, "class": a.award_class, "date": a.award_date.isoformat()},
        "issuer": {"authority": a.authority, "kid": a.kid},
        "issued_at": a.issued_at.replace(microsecond=0).isoformat(),
    }


def holder_name(given: str, middle: str | None, family: str) -> str:
    return " ".join(x for x in (given, middle, family) if x)
