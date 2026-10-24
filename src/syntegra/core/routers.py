"""Database router: CEDA zone of the model + tenant of the context → alias."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ImproperlyConfigured

from syntegra.core import context
from syntegra.core.zones import current_alias, is_zone_alias, zone_of_alias


class ZoneRouter:
    def _route(self, model: type, hints: dict[str, Any]) -> str | None:
        zones: tuple[str, ...] | None = getattr(model, "ceda_zones", None)
        if not zones:
            return "default"
        instance = hints.get("instance")
        if instance is not None and getattr(instance, "_state", None) is not None and instance._state.db:
            return str(instance._state.db)
        if len(zones) == 1:
            return current_alias(zones[0])
        ctx = context.current(required=False)
        if ctx is not None and ctx.zone_override in zones:
            return current_alias(ctx.zone_override)
        raise ImproperlyConfigured(
            f"{model.__name__} is replicated in zones {zones}: use .using(alias) or a context zone_override"
        )

    def db_for_read(self, model: type, **hints: Any) -> str | None:
        return self._route(model, hints)

    def db_for_write(self, model: type, **hints: Any) -> str | None:
        return self._route(model, hints)

    def allow_relation(self, obj1: Any, obj2: Any, **hints: Any) -> bool | None:
        return bool(obj1._state.db == obj2._state.db) if obj1._state.db and obj2._state.db else None

    def allow_migrate(self, db: str, app_label: str, model_name: str | None = None, **hints: Any) -> bool:
        if app_label == "schema":
            return is_zone_alias(db)
        if is_zone_alias(db):
            return False  # zone schemas contain only CEDA tables
        return db == "default"


__all__ = ["ZoneRouter", "zone_of_alias"]
