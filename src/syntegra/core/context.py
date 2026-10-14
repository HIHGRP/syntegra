"""Request/command context — who is acting, for which tenant, at which scope, with which clearance and purpose.

Every query on tenant data and every command runs inside a context (MFS §16.3 layer 2). The context is
carried in a ``contextvars.ContextVar`` so it follows the request through sync code, Celery tasks and
async views alike.
"""

from __future__ import annotations

import contextlib
import uuid
from collections.abc import Iterator
from contextvars import ContextVar
from dataclasses import dataclass, field, replace

CLASS_ORDER = ("public", "internal", "confidential", "restricted", "special")


def class_rank(c: str | None) -> int:
    return CLASS_ORDER.index(c) if c in CLASS_ORDER else 0


@dataclass(frozen=True)
class Context:
    """Immutable execution context."""

    tenant_id: uuid.UUID | None  # operating tenant (ops / vault / records zones)
    state_tenant_id: uuid.UUID | None  # state tenant (registry zone)
    actor_kind: str = "system"  # user | agent | api_client | system | public | platform_operator
    actor_id: uuid.UUID | None = None
    on_behalf_of: uuid.UUID | None = None  # owner of an agent's grant ("Agent X acting for Owner Y")
    grant_id: uuid.UUID | None = None
    role_code: str | None = None
    scope_node_id: uuid.UUID | None = None  # root of the grant's subtree
    clearance: str = "internal"
    permissions: frozenset[str] = field(default_factory=frozenset)
    purpose: str | None = None
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    scope_ids: frozenset[uuid.UUID] | None = None  # resolved subtree; None = whole tenant
    ip: str | None = None
    user_agent: str | None = None
    zone_override: str | None = None  # for replicated models

    @property
    def is_system(self) -> bool:
        return self.actor_kind == "system"

    def has(self, permission: str) -> bool:
        if self.is_system or "*" in self.permissions:
            return True
        resource = permission.split(":", 1)[0]
        return permission in self.permissions or f"{resource}:*" in self.permissions

    def cleared_for(self, classification: str | None) -> bool:
        return self.is_system or class_rank(self.clearance) >= class_rank(classification)

    def actor_label(self) -> str:
        if self.actor_kind == "agent" and self.on_behalf_of:
            return f"agent:{self.actor_id} for owner:{self.on_behalf_of}"
        return f"{self.actor_kind}:{self.actor_id or '-'}"

    def with_(self, **changes: object) -> Context:
        return replace(self, **changes)  # type: ignore[arg-type]


_current: ContextVar[Context | None] = ContextVar("syntegra_context", default=None)


class ContextMissing(RuntimeError):
    """Raised when tenant data is touched without a context (MFS §16.3 layer 2)."""


def current(required: bool = True) -> Context | None:
    ctx = _current.get()
    if ctx is None and required:
        raise ContextMissing("no execution context: tenant data may not be queried without tenant and scope")
    return ctx


def require() -> Context:
    ctx = current(required=True)
    assert ctx is not None
    return ctx


@contextlib.contextmanager
def use(ctx: Context) -> Iterator[Context]:
    token = _current.set(ctx)
    try:
        yield ctx
    finally:
        _current.reset(token)


def system(tenant_id: uuid.UUID | None, state_tenant_id: uuid.UUID | None = None, **kw: object) -> Context:
    """Context for platform jobs (nightly engines, CDC loaders, migrations). Audited as ``system:<job>``."""
    return Context(
        tenant_id=tenant_id,
        state_tenant_id=state_tenant_id or tenant_id,
        actor_kind="system",
        clearance="special",
        permissions=frozenset({"*"}),
        **kw,  # type: ignore[arg-type]
    )
