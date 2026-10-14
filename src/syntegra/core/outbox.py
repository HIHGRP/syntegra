"""Transactional outbox and in-process event dispatch (CEDA §9, Book 3 §16).

Events are inserted into the zone's ``outbox_event`` in the same transaction as the change. In production
Debezium's outbox router publishes them to Kafka (``SYNTEGRA_EVENT_DISPATCH = "debezium"``); in development
and tests, ``dispatch_pending`` delivers them to in-process subscribers after commit (``"inline"``).
"""

from __future__ import annotations

import json
import logging
import uuid
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.db import connections, transaction

from syntegra.core import catalog
from syntegra.core.context import Context
from syntegra.core.fields import utcnow
from syntegra.core.ids import uuid7
from syntegra.core.zones import zone_of_alias

log = logging.getLogger(__name__)
Handler = Callable[[dict[str, Any]], None]
_subscribers: dict[str, list[Handler]] = defaultdict(list)


def subscriber(*event_types: str) -> Callable[[Handler], Handler]:
    def deco(fn: Handler) -> Handler:
        for et in event_types:
            catalog.event(et)  # must exist in the CEDA catalogue
            _subscribers[et].append(fn)
        return fn

    return deco


class EventPayloadError(ValueError):
    pass


def validate_payload(event_type: str, payload: dict[str, Any]) -> None:
    spec = catalog.event(event_type).get("payload") or {}
    unknown = set(payload) - set(spec)
    if unknown:
        raise EventPayloadError(f"{event_type}: fields not in the catalogue: {sorted(unknown)}")
    missing = [f for f, t in spec.items() if str(t).endswith("!") and payload.get(f) is None]
    if missing:
        raise EventPayloadError(f"{event_type}: required fields missing: {missing}")


def _jsonable(v: Any) -> Any:
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


def emit(
    alias: str,
    ctx: Context,
    event_type: str,
    *,
    aggregate_kind: str,
    aggregate_id: uuid.UUID,
    payload: dict[str, Any],
    scope_node_id: uuid.UUID | None = None,
) -> uuid.UUID:
    """Insert an event into the outbox of ``alias`` — call inside the command's transaction."""
    validate_payload(event_type, payload)
    spec = catalog.event(event_type)
    zone = zone_of_alias(alias)
    event_id = uuid7()
    now = utcnow().replace(tzinfo=None)
    cols = [
        "id",
        "created_on",
        "event_type",
        "schema_version",
        "aggregate_kind",
        "aggregate_id",
        "scope_node_id_at",
        "actor",
        "correlation_id",
        "payload",
        "created_at",
        "created_by",
    ]
    vals: list[Any] = [
        event_id.bytes,
        now.date(),
        event_type,
        int(spec.get("version", 1)),
        aggregate_kind,
        aggregate_id.bytes,
        scope_node_id.bytes if scope_node_id else None,
        ctx.actor_label()[:120],
        ctx.correlation_id[:64],
        json.dumps(_jsonable(payload)),
        now,
        ctx.actor_id.bytes if ctx.actor_id else None,
    ]
    if zone != "platform":
        tenant = ctx.state_tenant_id if zone == "registry" else ctx.tenant_id
        cols.insert(1, "tenant_id")
        vals.insert(1, tenant.bytes if tenant else None)
    with connections[alias].cursor() as cur:
        cur.execute(f"INSERT INTO outbox_event ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})", vals)
    if getattr(settings, "SYNTEGRA_EVENT_DISPATCH", "inline") == "inline":
        transaction.on_commit(lambda: dispatch_pending(alias), using=alias)
    return event_id


def envelope(row: dict[str, Any], region: str = "ng") -> dict[str, Any]:
    """CloudEvents 1.0 structured envelope (ceda/generated/events/envelope.schema.json)."""
    et = row["event_type"]
    dom, name = et.split(".", 1)
    return {
        "specversion": "1.0",
        "id": str(row["id"]),
        "source": f"/syntegra/{region}/{row['zone']}",
        "type": f"io.syntegra.{dom.lower()}.{name.lower()}.v{row['schema_version']}",
        "time": row["created_at"].isoformat() + "Z",
        "subject": f"{row['aggregate_kind']}/{row['aggregate_id']}",
        "datacontenttype": "application/json",
        "tenantid": str(row["tenant_id"]) if row.get("tenant_id") else None,
        "scopenodeid": str(row["scope_node_id_at"]) if row.get("scope_node_id_at") else None,
        "actor": row["actor"],
        "schemaversion": row["schema_version"],
        "correlationid": row["correlation_id"],
        "classification": catalog.event(et).get("class", "internal"),
        "eventtype": et,
        "data": row["payload"],
    }


def dispatch_pending(alias: str, limit: int = 500) -> int:
    """Deliver unpublished events to in-process subscribers and mark them published."""
    zone = zone_of_alias(alias)
    tenant_col = ", tenant_id" if zone != "platform" else ""
    delivered = 0
    with connections[alias].cursor() as cur:
        cur.execute(
            f"SELECT id, created_on, event_type, schema_version, aggregate_kind, aggregate_id, scope_node_id_at, "
            f"actor, correlation_id, payload, created_at{tenant_col} FROM outbox_event WHERE published_at IS NULL "
            f"ORDER BY created_at, id LIMIT %s",
            [limit],
        )
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
    for row in rows:
        for k in ("id", "aggregate_id", "scope_node_id_at", "tenant_id"):
            if row.get(k):
                row[k] = uuid.UUID(bytes=bytes(row[k]))
        row["payload"] = json.loads(row["payload"])
        row["zone"] = zone
        env = envelope(row)
        for handler in _subscribers.get(row["event_type"], []):
            try:
                handler(env)
            except Exception:  # a failing consumer never blocks the producer; it is retried by its own queue
                log.exception("event handler failed for %s", row["event_type"])
        with connections[alias].cursor() as cur:
            cur.execute(
                "UPDATE outbox_event SET published_at = UTC_TIMESTAMP(6) WHERE id = %s AND created_on = %s",
                [row["id"].bytes, row["created_on"]],
            )
        delivered += 1
    return delivered
