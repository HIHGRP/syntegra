"""Shared API helpers: command headers, ETags, idempotent replay (Book 3 §26.1)."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from django.db import IntegrityError, connections, transaction
from rest_framework.request import Request
from rest_framework.response import Response

from syntegra.core import context
from syntegra.core.errors import HardValidation
from syntegra.core.ids import uuid7
from syntegra.core.uow import parse_etag
from syntegra.core.zones import current_alias

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
    """Replay the stored response for a repeated ``Idempotency-Key`` from the same principal (24 hours).

    Responses are kept in the registry zone's ``idempotency_key`` table (CEDA, FR-ATT-03/FR-PMT-02), so a
    retry reaching another application node replays the same answer. Reusing a key with a different body
    is refused. Two truly concurrent first attempts are serialised by the unique key: the loser replays.
    """
    key = request.headers.get("Idempotency-Key")
    if not key:
        return fn()
    if len(key) > 128 or not key.isascii():
        raise HardValidation("IDEMPOTENCY-KEY", "Invalid Idempotency-Key", "Use at most 128 ASCII characters.")
    ctx = context.require()
    alias = current_alias("registry")
    principal = (ctx.actor_id or uuid.UUID(int=0)).bytes
    tenant = (ctx.state_tenant_id or uuid.UUID(int=0)).bytes
    body = hashlib.sha256(json.dumps(request.data, sort_keys=True, default=str).encode()).digest()
    hit = _stored(alias, tenant, principal, key)
    if hit is not None:
        return _replay(hit, body)
    resp = fn()
    if resp.status_code >= 500:
        return resp
    stored = {"data": jsonable(resp.data), "headers": {k: v for k, v in resp.items() if k in ("ETag", "Location")}}
    try:
        with transaction.atomic(using=alias), connections[alias].cursor() as cur:
            cur.execute(
                "DELETE FROM idempotency_key WHERE tenant_id = %s AND principal_id = %s AND idem_key = %s "
                "AND expires_at <= UTC_TIMESTAMP(6)",
                [tenant, principal, key],
            )
            cur.execute(
                "INSERT INTO idempotency_key (id, tenant_id, principal_id, idem_key, request_hash, response_status, "
                "response_body, expires_at, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, "
                "UTC_TIMESTAMP(6) + INTERVAL %s SECOND, %s)",
                [
                    uuid7().bytes,
                    tenant,
                    principal,
                    key,
                    body,
                    resp.status_code,
                    json.dumps(stored),
                    IDEMPOTENCY_TTL,
                    principal,
                ],
            )
    except IntegrityError:
        hit = _stored(alias, tenant, principal, key)
        if hit is not None:
            return _replay(hit, body)
    return resp


def _stored(alias: str, tenant: bytes, principal: bytes, key: str) -> tuple[bytes, int, dict[str, Any]] | None:
    with connections[alias].cursor() as cur:
        cur.execute(
            "SELECT request_hash, response_status, response_body FROM idempotency_key WHERE tenant_id = %s "
            "AND principal_id = %s AND idem_key = %s AND expires_at > UTC_TIMESTAMP(6)",
            [tenant, principal, key],
        )
        row = cur.fetchone()
    if row is None:
        return None
    body = row[2] if isinstance(row[2], dict) else json.loads(row[2] or "{}")
    return bytes(row[0]), int(row[1]), body


def _replay(hit: tuple[bytes, int, dict[str, Any]], body: bytes) -> Response:
    if hit[0] != body:
        raise HardValidation(
            "IDEMPOTENCY-MISMATCH",
            "Idempotency key reused",
            "The same Idempotency-Key was used with a different request body.",
        )
    r = Response(hit[2].get("data"), status=hit[1], headers=hit[2].get("headers") or None)
    r["Idempotent-Replayed"] = "true"
    return r


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
