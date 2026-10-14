"""Shared API helpers: command headers, ETags, idempotent replay (Book 3 §26.1)."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.response import Response

from syntegra.core import context
from syntegra.core.errors import HardValidation
from syntegra.core.uow import parse_etag

IDEMPOTENCY_TTL = 24 * 3600


@dataclass(frozen=True)
class CommandMeta:
    if_match: int | None
    override_reason: str | None
    idempotency_key: str | None


def meta(request: Request) -> CommandMeta:
    reason = request.headers.get("X-Syntegra-Override-Reason")
    if reason is not None and len(reason.strip()) < 10:
        raise HardValidation("OVERRIDE-REASON", "Reason too short", "Give at least 10 characters.")
    return CommandMeta(
        if_match=parse_etag(request.headers.get("If-Match")),
        override_reason=reason.strip() if reason else None,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )


def idempotent(request: Request, fn: Callable[[], Response]) -> Response:
    """Replay the stored response for a repeated ``Idempotency-Key`` from the same actor and body."""
    key = request.headers.get("Idempotency-Key")
    if not key:
        return fn()
    ctx = context.require()
    body = hashlib.sha256(json.dumps(request.data, sort_keys=True, default=str).encode()).hexdigest()
    ck = f"syn:idem:{ctx.tenant_id}:{ctx.actor_id}:{key}"
    hit = cache.get(ck)
    if hit is not None:
        if hit["body"] != body:
            raise HardValidation("IDEMPOTENCY-MISMATCH", "Idempotency key reused",
                                 "The same Idempotency-Key was used with a different request body.")
        r = Response(hit["data"], status=hit["status"], headers=hit.get("headers"))
        r["Idempotent-Replayed"] = "true"
        return r
    resp = fn()
    if resp.status_code < 500:
        cache.set(ck, {"body": body, "data": resp.data, "status": resp.status_code,
                       "headers": {k: v for k, v in resp.items() if k in ("ETag", "Location")}}, IDEMPOTENCY_TTL)
    return resp


def with_etag(resp: Response, obj: Any) -> Response:
    if hasattr(obj, "row_version"):
        resp["ETag"] = f'W/"{obj.row_version}"'
    return resp


def jsonable(v: Any) -> Any:
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, (bytes, bytearray, memoryview)):
        return None
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if isinstance(v, dict):
        return {k: jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if v.__class__.__name__ == "Decimal":
        return str(v)
    return v


def row(obj: Any, fields: list[str] | None = None) -> dict[str, Any]:
    """Serialise a CEDA model instance by column, trimmed to the caller's clearance."""
    from syntegra.core import authz

    allowed = authz.visible_fields(type(obj))
    names = [f for f in (fields or allowed) if f in allowed]
    out: dict[str, Any] = {}
    for f in obj._meta.concrete_fields:
        if f.column in names:
            out[f.column] = jsonable(getattr(obj, f.attname))
    return out
