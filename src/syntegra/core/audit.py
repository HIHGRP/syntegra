"""Tamper-evident audit trail (Book 3 §15, CEDA §8.2, CD-12, CD-16).

One audit event per command, written in the same transaction and zone as the change. Each zone keeps
hash chains per tenant split into lanes: ``hash = SHA-256(prev_hash ‖ JCS(event))``. Special-category and
secret values never enter the audit log in clear — they are replaced by their SHA-256.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import uuid
from typing import Any

from django.conf import settings
from django.db import connections

from syntegra.core.canonical_json import canonicalize
from syntegra.core.context import Context
from syntegra.core.fields import utcnow
from syntegra.core.ids import uuid7
from syntegra.core.zones import zone_of_alias

PLATFORM_CHAIN = uuid.UUID("00000000-0000-7000-8000-00000000c0de")
GENESIS = b"\x00" * 32


def chain_tenant(zone: str, ctx: Context) -> uuid.UUID:
    if zone == "platform":
        return PLATFORM_CHAIN
    tenant = ctx.state_tenant_id if zone == "registry" else ctx.tenant_id
    if tenant is None:
        raise ValueError(f"audit in zone {zone} requires a tenant")
    return tenant


def lane_for(key: uuid.UUID | None) -> int:
    lanes = int(getattr(settings, "SYNTEGRA_AUDIT_LANES", 16))
    seed = key.bytes if key else uuid7().bytes
    return int.from_bytes(hashlib.sha256(seed).digest()[:2], "big") % lanes


def chain_id_for(tenant: uuid.UUID, zone: str, lane: int) -> uuid.UUID:
    return uuid.uuid5(tenant, f"{zone}:lane-{lane}")


def redact_value(model: Any, field: str, value: Any) -> Any:
    info = getattr(model, "ceda_fields", {}).get(field, {})
    sensitive = (
        info.get("class") in ("restricted", "special")
        or info.get("type") in ("sealed", "secret")
        or "secret_of" in info
    )
    if value is None:
        return None
    if sensitive:
        raw = value if isinstance(value, (bytes, bytearray)) else str(value).encode()
        return {"sha256": hashlib.sha256(bytes(raw)).hexdigest()}
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"sha256": hashlib.sha256(bytes(value)).hexdigest()}
    if isinstance(value, (uuid.UUID, dt.date, dt.datetime)):
        return str(value)
    if isinstance(value, (int, str, bool, list, dict)) or value is None:
        return value
    return str(value)


def write_event(
    alias: str,
    ctx: Context,
    *,
    action: str,
    record_kind: str,
    record_id: uuid.UUID | None,
    field_changes: list[dict[str, Any]] | None = None,
    reason: str | None = None,
    approval_ref: uuid.UUID | None = None,
) -> dict[str, Any]:
    """Append one audit event to the chain. Must run inside ``transaction.atomic(using=alias)``."""
    zone = zone_of_alias(alias)
    tenant = chain_tenant(zone, ctx)
    lane = lane_for(record_id)
    chain_id = chain_id_for(tenant, zone, lane)
    conn = connections[alias]
    with conn.cursor() as cur:
        has_tenant = zone != "platform"
        if has_tenant:
            cur.execute(
                "INSERT IGNORE INTO audit_chain_head (chain_id, tenant_id, lane, last_seq, last_hash, created_at) "
                "VALUES (%s, %s, %s, 0, %s, UTC_TIMESTAMP(6))",
                [chain_id.bytes, tenant.bytes, lane, GENESIS],
            )
        else:
            cur.execute(
                "INSERT IGNORE INTO audit_chain_head (chain_id, lane, last_seq, last_hash, created_at) "
                "VALUES (%s, %s, 0, %s, UTC_TIMESTAMP(6))",
                [chain_id.bytes, lane, GENESIS],
            )
        cur.execute("SELECT last_seq, last_hash FROM audit_chain_head WHERE chain_id = %s FOR UPDATE", [chain_id.bytes])
        last_seq, prev_hash = cur.fetchone()
        seq = int(last_seq) + 1
        occurred_at = utcnow().replace(tzinfo=None)
        event_id = uuid7()
        event = {
            "chain_id": str(chain_id),
            "chain_seq": seq,
            "occurred_at": occurred_at.isoformat(timespec="microseconds"),
            "event_id": str(event_id),
            "actor_kind": ctx.actor_kind
            if ctx.actor_kind in ("user", "agent", "api_client", "system", "platform_operator")
            else "system",
            "actor_id": str(ctx.actor_id) if ctx.actor_id else None,
            "on_behalf_of_user_id": str(ctx.on_behalf_of) if ctx.on_behalf_of else None,
            "action": action,
            "record_kind": record_kind,
            "record_id": str(record_id) if record_id else None,
            "field_changes": field_changes or [],
            "reason": reason,
            "purpose_code": ctx.purpose,
        }
        digest = hashlib.sha256(bytes(prev_hash) + canonicalize(event)).digest()
        cols = [
            "chain_id",
            "chain_seq",
            "occurred_at",
            "event_id",
            "actor_kind",
            "actor_id",
            "on_behalf_of_user_id",
            "actor_grant_id",
            "scope_node_id_at",
            "action",
            "record_kind",
            "record_id",
            "field_changes",
            "reason",
            "purpose_code",
            "approval_ref",
            "correlation_id",
            "ip",
            "user_agent",
            "prev_hash",
            "hash",
            "created_at",
        ]
        import json

        vals: list[Any] = [
            chain_id.bytes,
            seq,
            occurred_at,
            event_id.bytes,
            event["actor_kind"],
            ctx.actor_id.bytes if ctx.actor_id else None,
            ctx.on_behalf_of.bytes if ctx.on_behalf_of else None,
            ctx.grant_id.bytes if ctx.grant_id else None,
            ctx.scope_node_id.bytes if ctx.scope_node_id else None,
            action,
            record_kind,
            record_id.bytes if record_id else None,
            json.dumps(field_changes or []),
            reason,
            ctx.purpose,
            approval_ref.bytes if approval_ref else None,
            ctx.correlation_id[:64],
            _packed_ip(ctx.ip),
            (ctx.user_agent or "")[:400] or None,
            bytes(prev_hash),
            digest,
            occurred_at,
        ]
        if has_tenant:
            cols.insert(0, "tenant_id")
            vals.insert(0, tenant.bytes)
        cur.execute(f"INSERT INTO audit_event ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})", vals)
        cur.execute(
            "UPDATE audit_chain_head SET last_seq = %s, last_hash = %s WHERE chain_id = %s",
            [seq, digest, chain_id.bytes],
        )
    return {"chain_id": chain_id, "chain_seq": seq, "hash": digest}


def verify_chain(alias: str, chain_id: uuid.UUID) -> tuple[bool, int]:
    """Recompute a chain; returns (ok, events checked). Run nightly; anchors go to WORM storage."""
    import json

    prev = GENESIS
    n = 0
    with connections[alias].cursor() as cur:
        cur.execute(
            "SELECT chain_seq, occurred_at, event_id, actor_kind, actor_id, on_behalf_of_user_id, action, record_kind, "
            "record_id, field_changes, reason, purpose_code, prev_hash, hash FROM audit_event WHERE chain_id = %s "
            "ORDER BY chain_seq",
            [chain_id.bytes],
        )
        for row in cur.fetchall():
            seq, occ, eid, akind, aid, obo, action, rkind, rid, changes, reason, purpose, ph, h = row
            u = lambda b: str(uuid.UUID(bytes=bytes(b))) if b else None  # noqa: E731
            event = {
                "chain_id": str(chain_id),
                "chain_seq": int(seq),
                "occurred_at": occ.isoformat(timespec="microseconds"),
                "event_id": u(eid),
                "actor_kind": akind,
                "actor_id": u(aid),
                "on_behalf_of_user_id": u(obo),
                "action": action,
                "record_kind": rkind,
                "record_id": u(rid),
                "field_changes": json.loads(changes) if changes else [],
                "reason": reason,
                "purpose_code": purpose,
            }
            if bytes(ph) != prev or hashlib.sha256(prev + canonicalize(event)).digest() != bytes(h):
                return False, n
            prev = bytes(h)
            n += 1
    return True, n


def _packed_ip(ip: str | None) -> bytes | None:
    if not ip:
        return None
    import ipaddress

    try:
        return ipaddress.ip_address(ip).packed
    except ValueError:
        return None
