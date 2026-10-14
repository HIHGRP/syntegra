"""Base class of every generated CEDA model."""

from __future__ import annotations

from typing import Any, ClassVar

from django.db import models

from syntegra.core import context
from syntegra.core.errors import AppendOnlyViolation
from syntegra.core.fields import utcnow


class CedaModel(models.Model):
    """Behaviour shared by all CEDA entities: tenant stamping, actor stamping, optimistic locking, append-only."""

    ceda_entity: ClassVar[str] = ""
    ceda_zones: ClassVar[tuple[str, ...]] = ()
    ceda_domain: ClassVar[str] = ""
    ceda_kind: ClassVar[str] = ""
    ceda_class: ClassVar[str] = "internal"
    ceda_history: ClassVar[str] = "none"
    ceda_scope: ClassVar[str] = "none"
    ceda_append_only: ClassVar[bool] = False
    ceda_partition: ClassVar[dict[str, str] | None] = None
    ceda_retention: ClassVar[str | None] = None
    ceda_fields: ClassVar[dict[str, dict[str, Any]]] = {}

    class Meta:
        abstract = True

    # ------------------------------------------------------------------ persistence
    def save(self, *args: Any, **kwargs: Any) -> None:
        ctx = context.current(required=False)
        adding = self._state.adding
        if not adding and self.ceda_append_only:
            raise AppendOnlyViolation(self.ceda_entity)
        if self.has_column("tenant_id") and getattr(self, "tenant_id", None) is None and ctx is not None:
            using = kwargs.get("using") or self._state.db
            zone = self._zone_for(using, ctx)
            self.tenant_id = ctx.state_tenant_id if zone == "registry" else ctx.tenant_id
        actor = ctx.actor_id if ctx is not None else None
        if adding and self.has_column("created_by") and getattr(self, "created_by", None) is None:
            self.created_by = actor
        if not adding:
            if self.has_column("row_version"):
                self.row_version = (getattr(self, "row_version", 0) or 0) + 1
            if self.has_column("updated_at"):
                self.updated_at = utcnow()
            if self.has_column("updated_by"):
                self.updated_by = actor
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        if self.ceda_append_only:
            raise AppendOnlyViolation(self.ceda_entity)
        return super().delete(*args, **kwargs)

    # ------------------------------------------------------------------ helpers
    @classmethod
    def has_column(cls, name: str) -> bool:
        return name in cls.ceda_fields

    @property
    def etag(self) -> str:
        return f'W/"{getattr(self, "row_version", 0)}"'

    def zone(self) -> str:
        from syntegra.core.zones import zone_of_alias

        return zone_of_alias(self._state.db) if self._state.db else self.ceda_zones[0]

    def _zone_for(self, using: str | None, ctx: context.Context) -> str:
        from syntegra.core.zones import zone_of_alias

        if using:
            return zone_of_alias(using)
        if ctx.zone_override in self.ceda_zones:
            return ctx.zone_override
        return self.ceda_zones[0]
