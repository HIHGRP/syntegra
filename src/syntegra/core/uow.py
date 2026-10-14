"""Unit of work — the command pipeline every state change goes through (MFS §16.3, Book 3 §13–16).

    with uow.command("ops", "attendance:mark", action="submit", record_kind="attendance_register") as cmd:
        reg = cmd.lock(AttendanceRegister, register_id, expected_version=if_match)
        cmd.update(reg, status="submitted")
        cmd.emit("ATT.RegisterSubmitted", aggregate_id=reg.id, payload={...})

The pipeline: permission check → one database transaction on the zone alias → optimistic concurrency
(If-Match ↔ ``row_version``) → change capture → events into the outbox → exactly one hash-chained audit
event for the command, all committed atomically.
"""

from __future__ import annotations

import contextlib
import uuid
from collections.abc import Iterator
from typing import Any, TypeVar

from django.db import models, transaction

from syntegra.core import audit, authz, context, outbox
from syntegra.core.context import Context
from syntegra.core.errors import NotFound, PreconditionFailed
from syntegra.core.zones import current_alias

M = TypeVar("M", bound=models.Model)
SKIP_AUDIT_FIELDS = {"created_at", "updated_at", "created_by", "updated_by", "row_version"}


def parse_etag(value: str | None) -> int | None:
    """``W/"7"`` or ``"7"`` → 7."""
    if not value:
        return None
    v = value.strip()
    if v.startswith("W/"):
        v = v[2:]
    try:
        return int(v.strip('"'))
    except ValueError as exc:
        raise PreconditionFailed("Malformed If-Match header.") from exc


class Command:
    def __init__(self, ctx: Context, alias: str, action: str, record_kind: str, reason: str | None) -> None:
        self.ctx = ctx
        self.alias = alias
        self.action = action
        self.record_kind = record_kind
        self.record_id: uuid.UUID | None = None
        self.reason = reason
        self.approval_ref: uuid.UUID | None = None
        self.changes: list[dict[str, Any]] = []
        self.events: list[uuid.UUID] = []
        self.audited = True

    # -------------------------------------------------------------- reads under lock
    def lock(self, model: type[M], pk: Any, *, expected_version: int | None = None, **filters: Any) -> M:
        mgr = model._base_manager.using(self.alias)  # tenant filter applied explicitly below
        qs = mgr.select_for_update().filter(pk=pk, **filters)
        qs = _tenant_filter(model, qs, self.ctx, self.alias)
        obj = qs.first()
        if obj is None:
            raise NotFound(getattr(model, "ceda_entity", model.__name__), pk)
        if "scope_node_id" in getattr(model, "ceda_fields", {}):
            authz.require_scope(getattr(obj, "scope_node_id", None), self.ctx)
        if expected_version is not None and getattr(obj, "row_version", None) != expected_version:
            raise PreconditionFailed()
        return obj

    # -------------------------------------------------------------- writes
    def add(self, obj: M) -> M:
        if "scope_node_id" in getattr(obj, "ceda_fields", {}) and getattr(obj, "scope_node_id", None) is not None:
            authz.require_scope(obj.scope_node_id, self.ctx)  # type: ignore[attr-defined]
        obj.save(using=self.alias)
        self._capture(obj, None)
        if self.record_id is None:
            self.record_id = _pk_uuid(obj)
        return obj

    def update(self, obj: M, **changes: Any) -> M:
        before = {k: getattr(obj, _attname(obj, k)) for k in changes}
        for k, v in changes.items():
            setattr(obj, k, v)
        obj.save(using=self.alias)
        self._capture(obj, before)
        if self.record_id is None:
            self.record_id = _pk_uuid(obj)
        return obj

    def emit(self, event_type: str, *, aggregate_id: uuid.UUID, payload: dict[str, Any],
             aggregate_kind: str | None = None, scope_node_id: uuid.UUID | None = None) -> uuid.UUID:
        eid = outbox.emit(self.alias, self.ctx, event_type, aggregate_kind=aggregate_kind or self.record_kind,
                          aggregate_id=aggregate_id, payload=payload, scope_node_id=scope_node_id or self.ctx.scope_node_id)
        self.events.append(eid)
        return eid

    def note(self, field: str, old: Any = None, new: Any = None) -> None:
        self.changes.append({"field": field, "old": old, "new": new})

    def _capture(self, obj: models.Model, before: dict[str, Any] | None) -> None:
        model = type(obj)
        prefix = "" if self.record_kind == getattr(model, "ceda_entity", "") else f"{getattr(model, 'ceda_entity', '')}."
        if before is None:
            for f in model._meta.concrete_fields:
                if f.column in SKIP_AUDIT_FIELDS or getattr(f, "generated", False):
                    continue
                val = getattr(obj, f.attname)
                if val is None:
                    continue
                self.changes.append({"field": prefix + f.column, "new": audit.redact_value(model, f.column, val)})
        else:
            for k, old in before.items():
                col = _column(obj, k)
                new = getattr(obj, _attname(obj, k))
                if old != new:
                    self.changes.append({"field": prefix + col, "old": audit.redact_value(model, col, old),
                                         "new": audit.redact_value(model, col, new)})


def _attname(obj: models.Model, name: str) -> str:
    try:
        return obj._meta.get_field(name).attname
    except Exception:  # noqa: BLE001
        return name


def _column(obj: models.Model, name: str) -> str:
    try:
        return str(obj._meta.get_field(name).column)
    except Exception:  # noqa: BLE001
        return name


def _pk_uuid(obj: models.Model) -> uuid.UUID | None:
    v = getattr(obj, "id", None)
    return v if isinstance(v, uuid.UUID) else None


def _tenant_filter(model: type[models.Model], qs: Any, ctx: Context, alias: str) -> Any:
    if "tenant_id" not in getattr(model, "ceda_fields", {}):
        return qs
    from syntegra.core.zones import zone_of_alias

    zone = zone_of_alias(alias)
    return qs.filter(tenant_id=ctx.state_tenant_id if zone == "registry" else ctx.tenant_id)


@contextlib.contextmanager
def command(zone: str, permission: str | None, *, action: str, record_kind: str, reason: str | None = None,
            ctx: Context | None = None) -> Iterator[Command]:
    """Run a command: authorise, open the zone transaction, yield the Command, then audit and commit."""
    ctx = ctx or context.require()
    if permission:
        authz.require(permission, ctx)
    alias = current_alias(zone)
    with context.use(ctx), transaction.atomic(using=alias):
        cmd = Command(ctx, alias, action, record_kind, reason)
        yield cmd
        if cmd.audited:
            audit.write_event(alias, ctx, action=action, record_kind=record_kind, record_id=cmd.record_id,
                              field_changes=cmd.changes, reason=reason, approval_ref=cmd.approval_ref)
