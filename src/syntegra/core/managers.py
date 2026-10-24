"""Tenant-scoped managers (MFS §16.3 layer 2): no query on tenant data runs without a tenant context."""

from __future__ import annotations

from typing import Any

from django.db import models

from syntegra.core import context


class TenantScopedQuerySet(models.QuerySet):  # type: ignore[type-arg]
    def in_scope(self) -> TenantScopedQuerySet:
        """Further restrict owned-scope entities to the caller's grant subtree (scope_closure)."""
        ctx = context.require()
        model = self.model
        if ctx.scope_ids is None or "scope_node_id" not in getattr(model, "ceda_fields", {}):
            return self
        return self.filter(scope_node_id__in=list(ctx.scope_ids))


class TenantScopedManager(models.Manager):  # type: ignore[type-arg]
    """Default manager of every tenant-zone model.

    Filters on ``tenant_id`` from the current context — the state tenant for registry entities, the
    operating tenant for ops/vault/records entities. Raises ``ContextMissing`` without a context.
    Use ``Model.unscoped`` only in reviewed system code (migrations, CDC, integrity jobs).
    """

    def get_queryset(self) -> TenantScopedQuerySet:
        ctx = context.require()
        zones: tuple[str, ...] = getattr(self.model, "ceda_zones", ())
        zone = ctx.zone_override if ctx.zone_override in zones else (zones[0] if zones else None)
        tenant = ctx.state_tenant_id if zone == "registry" else ctx.tenant_id
        if tenant is None:
            raise context.ContextMissing(f"context has no tenant for zone {zone}")
        return TenantScopedQuerySet(self.model, using=self._db).filter(tenant_id=tenant)

    def in_scope(self) -> Any:
        return self.get_queryset().in_scope()
