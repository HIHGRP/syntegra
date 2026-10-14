"""Registry-wide jobs (CR-006): bring existing registries up to the current release, and the daily run.

``upgrade`` re-applies the idempotent configuration of every registry (roles and their permissions, policies),
loads the funding programmes into state registries and completes the security-agency curricula. ``daily`` runs,
for every registry: facility rules and escalation, overdue imprest, loan arrears, and the warehouse load.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from syntegra.core import context, uow


def _registries(kinds: tuple[str, ...] = ("state", "sector_registry")) -> list[Any]:
    from syntegra.platform.models import Tenant

    return list(Tenant.objects.using("platform").filter(kind__in=kinds, status="active").order_by("code"))


def upgrade() -> dict[str, dict[str, Any]]:
    from syntegra.funding import services as funding
    from syntegra.governance.models import ScopeNode
    from syntegra.platform.bootstrap import seed_registry_config

    out: dict[str, dict[str, Any]] = {}
    for t in _registries():
        with context.use(context.system(t.id, t.id, correlation_id=f"upgrade-{t.code}")):
            root = (
                ScopeNode.objects.filter(depth=1).order_by("created_at").first()
                or ScopeNode.objects.filter(parent_id__isnull=True).first()
            )
            if root is None:
                continue
            with uow.command("registry", None, action="upgrade", record_kind="tenant") as cmd:
                cmd.record_id = t.id
                seed_registry_config(cmd, root)
            res: dict[str, Any] = {}
            if t.kind == "state":
                res["funding_programmes"] = funding.seed_programmes(root.id)
            if t.code.upper() == "NG-FSE":
                from syntegra.security_training import registry

                res["security"] = registry.seed_reference().__dict__
            out[t.code] = res
    return out


def daily(on: dt.date | None = None, *, warehouse: bool = True) -> dict[str, dict[str, Any]]:
    from syntegra.analytics import warehouse as dw
    from syntegra.estate import services as estate
    from syntegra.finance import budgets
    from syntegra.funding import services as funding

    on = on or dt.date.today()
    out: dict[str, dict[str, Any]] = {}
    for t in _registries():
        with context.use(context.system(t.id, t.id, correlation_id=f"daily-{t.code}-{on:%Y%m%d}")):
            res: dict[str, Any] = {
                "facilities": estate.run_daily(on),
                "imprest_overdue": budgets.flag_overdue_imprest(on),
                "funding": funding.refresh_arrears(on),
            }
            if warehouse:
                res["warehouse"] = dw.load(on)
            out[t.code] = res
    return out
