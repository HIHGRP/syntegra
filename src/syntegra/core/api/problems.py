"""RFC 9457 problem+json for every API error (Book 3 §26.1)."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, OperationalError
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler

from syntegra.core.errors import PROBLEM_BASE, DomainError

PROBLEM_TYPE = "application/problem+json"


def _resp(body: dict[str, Any], status: int, headers: dict[str, str] | None = None) -> Response:
    r = Response(body, status=status, headers=headers, content_type=PROBLEM_TYPE)
    return r


def exception_handler(exc: Exception, ctx: dict[str, Any]) -> Response | None:
    from syntegra.core import context

    c = context.current(required=False)
    corr = {"correlation_id": c.correlation_id} if c else {}
    if isinstance(exc, DomainError):
        return _resp({**exc.problem(), **corr}, exc.status)
    if isinstance(exc, DjangoValidationError):  # e.g. a malformed id reaching a model filter: the client's input
        return _resp({"type": PROBLEM_BASE + "VALIDATION", "title": "Invalid input", "status": 422,
                      "detail": "; ".join(exc.messages), **corr}, 422)  # fmt: skip
    if isinstance(exc, ObjectDoesNotExist):
        return _resp({"type": PROBLEM_BASE + "NOT-FOUND", "title": "Not found", "status": 404, **corr}, 404)
    if isinstance(exc, IntegrityError):
        msg = (*exc.args, "", "")[1]
        return _resp(
            {
                "type": PROBLEM_BASE + "INTEGRITY",
                "title": "The change conflicts with existing data",
                "status": 409,
                "detail": _integrity_detail(str(msg)),
                **corr,
            },
            409,
        )
    if isinstance(exc, OperationalError) and exc.args and exc.args[0] == 1644:  # SIGNAL from CEDA triggers
        return _resp(
            {
                "type": PROBLEM_BASE + "APPEND-ONLY",
                "title": "Record cannot be changed",
                "status": 409,
                "detail": str(exc.args[1]),
                **corr,
            },
            409,
        )
    resp = drf_handler(exc, ctx)
    if resp is None:
        return None
    status = resp.status_code
    if isinstance(exc, exceptions.ValidationError):
        errors = _flatten(resp.data)
        return _resp(
            {
                "type": PROBLEM_BASE + "VALIDATION",
                "title": "Some fields need attention",
                "status": 422,
                "errors": errors,
                **corr,
            },
            422,
        )
    detail = resp.data.get("detail") if isinstance(resp.data, dict) else resp.data
    code = {401: "AUTH-401", 403: "AUTH-403", 404: "NOT-FOUND", 405: "METHOD", 429: "RATE-LIMIT"}.get(status, "ERROR")
    headers = {k: v for k, v in resp.items() if k in ("WWW-Authenticate", "Retry-After", "Allow")}
    return _resp({"type": PROBLEM_BASE + code, "title": str(detail), "status": status, **corr}, status, headers)


def _flatten(data: Any, prefix: str = "") -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if isinstance(data, dict):
        for k, v in data.items():
            out.extend(_flatten(v, f"{prefix}{k}." if k != "non_field_errors" else prefix))
    elif isinstance(data, list):
        for v in data:
            out.extend(_flatten(v, prefix))
    else:
        out.append({"field": prefix.rstrip(".") or None, "message": str(data)})  # type: ignore[dict-item]
    return out


def _integrity_detail(msg: str) -> str:
    if "Duplicate entry" in msg:
        key = msg.rsplit("for key", 1)[-1].strip(" '")
        return f"A record with the same identifying values already exists ({key.split('.')[-1]})."
    if "foreign key constraint" in msg:
        return "A referenced record does not exist in this tenant."
    if "Check constraint" in msg:
        return "A business rule on the record was violated: " + msg.split("'")[1] if "'" in msg else msg
    return "The change conflicts with existing data."
