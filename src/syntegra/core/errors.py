"""Domain errors rendered as RFC 9457 problem+json (Book 3 §26.1).

Validation levels (Book 3 §13.1): hard → 422; soft warning → 409 with ``override_allowed`` (the client
repeats the call with ``X-Syntegra-Override-Reason``); anomaly → 202 queued for human review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PROBLEM_BASE = "https://errors.syntegra.io/"


@dataclass
class DomainError(Exception):
    code: str
    title: str
    detail: str = ""
    status: int = 422
    errors: list[dict[str, Any]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.title} — {self.detail}"

    def problem(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "type": PROBLEM_BASE + self.code,
            "title": self.title,
            "status": self.status,
            "code": self.code,
            "detail": self.detail,
        }
        if self.errors:
            body["errors"] = self.errors
        body.update(self.extra)
        return body


class HardValidation(DomainError):
    def __init__(self, code: str, title: str, detail: str = "", errors: list[dict[str, Any]] | None = None):
        super().__init__(code, title, detail, 422, errors or [])


class SoftWarning(DomainError):
    """Unusual but potentially legitimate: continue with an audited reason."""

    def __init__(self, code: str, title: str, detail: str = ""):
        super().__init__(code, title, detail, 409, [], {"override_allowed": True})


class NotFound(DomainError):
    def __init__(self, what: str, ident: object = ""):
        super().__init__("NOT-FOUND", f"{what} not found", str(ident), 404)


class Forbidden(DomainError):
    def __init__(self, detail: str = "You do not have permission for this action.", code: str = "AUTH-403"):
        super().__init__(code, "Forbidden", detail, 403)


class PurposeRequired(DomainError):
    def __init__(self, classification: str):
        super().__init__(
            "PURPOSE-REQUIRED",
            "A purpose is required",
            f"Access to {classification} data requires the X-Syntegra-Purpose header.",
            428,
        )


class ConflictError(DomainError):
    def __init__(self, code: str, title: str, detail: str = ""):
        super().__init__(code, title, detail, 409)


class PreconditionFailed(DomainError):
    def __init__(self, detail: str = "The record changed since you read it."):
        super().__init__("PRECONDITION-FAILED", "Precondition failed", detail, 412)


class AppendOnlyViolation(DomainError):
    def __init__(self, entity: str):
        super().__init__("APPEND-ONLY", "Record cannot be changed", f"{entity} is append-only; record a correction.", 409)
