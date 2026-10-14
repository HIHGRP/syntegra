"""Tenant resolution (MFS §16.3 layer 1, CEDA §6.3).

A request's tenant is resolved from its host name through ``tenant_domain`` — it is never chosen from a list.
The registry zone is keyed by the *state* tenant: a state tenant is its own state tenant; a private provider
or institution tenant uses its nearest ``state`` ancestor.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache

from syntegra.core.errors import NotFound

# Fixed id of the first state tenant: the CEDA registry seed (15_registry_seed_code_lists.sql) is keyed to it.
SEED_STATE_TENANT = uuid.UUID("00000000-0000-7000-8000-000000000001")


@dataclass(frozen=True)
class TenantInfo:
    id: uuid.UUID
    code: str
    kind: str
    name: str
    state_tenant_id: uuid.UUID
    state_code: str | None
    status: str


def _load(tenant_id: uuid.UUID) -> TenantInfo:
    from syntegra.platform.models import Tenant

    t = Tenant.objects.using("platform").filter(pk=tenant_id).first()
    if t is None:
        raise NotFound("tenant", str(tenant_id))
    node, state = t, None
    for _ in range(8):  # global → country → state → provider → institution → department
        if node.kind == "state":
            state = node
            break
        if node.parent_id is None:
            break
        node = Tenant.objects.using("platform").get(pk=node.parent_id)
    return TenantInfo(
        id=t.id, code=t.code, kind=t.kind, name=t.name, state_tenant_id=(state or t).id,
        state_code=t.state_code, status=t.status,
    )


@lru_cache(maxsize=4096)
def tenant_info(tenant_id: uuid.UUID) -> TenantInfo:
    return _load(tenant_id)


def tenant_code_for(tenant_id: uuid.UUID | None) -> str | None:
    if tenant_id is None:
        return None
    return tenant_info(tenant_id).code


def resolve_host(host: str) -> TenantInfo | None:
    """Host name → tenant through ``tenant_domain``; dev/test fall back to ``SYNTEGRA_DEFAULT_TENANT_CODE``."""
    from syntegra.platform.models import Tenant, TenantDomain

    hostname = host.split(":", 1)[0].lower()
    key = f"syn:host:{hostname}"
    tid = cache.get(key)
    if tid is None:
        dom = TenantDomain.objects.using("platform").filter(hostname=hostname, status="active").first()
        if dom is not None:
            tid = dom.tenant_id
        else:
            code = getattr(settings, "SYNTEGRA_DEFAULT_TENANT_CODE", None)
            fallback = Tenant.objects.using("platform").filter(code=code).first() if code else None
            if fallback is None:
                return None
            tid = fallback.id
        cache.set(key, tid, 300)
    return tenant_info(tid)


def by_code(code: str) -> TenantInfo:
    from syntegra.platform.models import Tenant

    t = Tenant.objects.using("platform").filter(code=code).first()
    if t is None:
        raise NotFound("tenant", code)
    return tenant_info(t.id)


def clear_caches() -> None:
    tenant_info.cache_clear()
    cache.clear()
