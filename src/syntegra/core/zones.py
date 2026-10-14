"""Data zones → database aliases (CEDA §6).

Two tenancy modes (``SYNTEGRA_TENANCY`` setting):

* ``single`` — development, test and single-state pilots: one alias per zone (``platform``, ``registry``,
  ``ops``, ``vault``, ``records``, ``dw``).
* ``schema`` — production: one schema per tenant per zone (``syn_ops_{tenant}``…). Aliases are registered
  on demand from the ``SYNTEGRA_DB_TEMPLATE`` connection settings, named ``<zone>__<schema>``.
"""

from __future__ import annotations

import copy
import threading
from typing import Any

from django.conf import settings
from django.db import connections

ZONES = ("platform", "registry", "ops", "vault", "records", "dw")
_lock = threading.Lock()


def tenancy_mode() -> str:
    return str(getattr(settings, "SYNTEGRA_TENANCY", "single"))


def zone_of_alias(alias: str) -> str:
    base = alias.split("__", 1)[0]
    if base in ZONES:
        return base
    if base == "default":
        return "platform"
    raise ValueError(f"alias {alias!r} is not a CEDA zone alias")


def is_zone_alias(alias: str) -> bool:
    return alias.split("__", 1)[0] in ZONES


def schema_name(zone: str, tenant_code: str | None) -> str:
    pattern = settings.SYNTEGRA_SCHEMA_PATTERNS[zone]
    return str(pattern).format(state=tenant_code, tenant=tenant_code)


def alias_for(zone: str, tenant_code: str | None = None) -> str:
    """Database alias holding ``zone`` for a tenant (state code for registry/dw)."""
    if zone not in ZONES:
        raise ValueError(zone)
    if tenancy_mode() == "single" or zone == "platform":
        return zone
    if not tenant_code:
        raise ValueError(f"tenant code required for zone {zone} in schema tenancy")
    schema = schema_name(zone, tenant_code)
    alias = f"{zone}__{schema}"
    if alias not in connections.settings:
        with _lock:
            if alias not in connections.settings:
                cfg: dict[str, Any] = copy.deepcopy(settings.SYNTEGRA_DB_TEMPLATE)
                cfg["NAME"] = schema
                if zone == "dw":
                    cfg.update(getattr(settings, "SYNTEGRA_DW_OVERRIDES", {}))
                configured = connections.configure_settings({"default": {}, alias: cfg})
                connections.settings[alias] = configured[alias]
    return alias


def current_alias(zone: str) -> str:
    """Alias for ``zone`` under the current context's tenant."""
    from syntegra.core import context

    ctx = context.current(required=False)
    code = None
    if ctx is not None and tenancy_mode() != "single":
        from syntegra.core.tenancy import tenant_code_for

        code = tenant_code_for(ctx.state_tenant_id if zone in ("registry", "dw") else ctx.tenant_id)
    return alias_for(zone, code)
