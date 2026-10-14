"""Authorisation (MFS §5, Book 3 §14): role grant → permissions, scope subtree, clearance and purpose.

* **Permission** — ``resource:action`` strings from ``role_permission`` (``*`` and ``resource:*`` wildcards).
* **Scope** — a grant applies to the subtree of its scope node, resolved through ``scope_closure``.
* **Clearance** — the lower of the role's clearance and the grant's ``clearance_cap``; fields above it are
  trimmed from responses (see ``visible_fields``).
* **Purpose** — restricted and special reads require a declared purpose (``X-Syntegra-Purpose``) from
  ``purpose_code`` permitted for the role; the purpose is written to the audit event.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.core import context
from syntegra.core.context import Context, class_rank
from syntegra.core.errors import Forbidden, PurposeRequired


def subtree(state_tenant_id: uuid.UUID, scope_node_id: uuid.UUID) -> frozenset[uuid.UUID]:
    from syntegra.governance.models import ScopeClosure

    ids = ScopeClosure.unscoped.using(_registry()).filter(
        tenant_id=state_tenant_id, ancestor_id=scope_node_id
    ).values_list("descendant_id", flat=True)
    return frozenset(ids) | {scope_node_id}


def ancestors(state_tenant_id: uuid.UUID, scope_node_id: uuid.UUID) -> list[uuid.UUID]:
    """Ancestors of a node, nearest first (depth ascending, self included)."""
    from syntegra.governance.models import ScopeClosure

    rows = ScopeClosure.unscoped.using(_registry()).filter(
        tenant_id=state_tenant_id, descendant_id=scope_node_id
    ).order_by("depth").values_list("ancestor_id", flat=True)
    out = list(rows)
    return out or [scope_node_id]


def _registry() -> str:
    from syntegra.core.zones import current_alias

    return current_alias("registry")


def grant_context(base: Context, grant_id: uuid.UUID, *, today: dt.date | None = None) -> Context:
    """Expand a role grant into permissions, clearance and resolved scope."""
    from syntegra.iam.models import Role, RoleGrant, RolePermission

    alias = _registry()
    today = today or dt.date.today()
    g = RoleGrant.unscoped.using(alias).filter(pk=grant_id, tenant_id=base.state_tenant_id).first()
    if g is None or g.status != "active" or g.valid_from > today or (g.valid_to and g.valid_to < today):
        raise Forbidden("The role grant is not active.", code="AUTH-GRANT-INACTIVE")
    role = Role.unscoped.using(alias).get(pk=g.role_id)
    perms = frozenset(RolePermission.unscoped.using(alias).filter(role_id=role.id).values_list("permission", flat=True))
    clearance = role.clearance
    if g.clearance_cap and class_rank(g.clearance_cap) < class_rank(clearance):
        clearance = g.clearance_cap
    assert base.state_tenant_id is not None
    return base.with_(
        grant_id=g.id,
        role_code=role.code,
        scope_node_id=g.scope_id,
        clearance=clearance,
        permissions=perms,
        scope_ids=subtree(base.state_tenant_id, g.scope_id),
    )


def require(permission: str, ctx: Context | None = None) -> Context:
    ctx = ctx or context.require()
    if not ctx.has(permission):
        raise Forbidden(f"Missing permission {permission}.", code="AUTH-PERMISSION")
    return ctx


def require_scope(scope_node_id: uuid.UUID | None, ctx: Context | None = None) -> None:
    """The target record's scope must lie in the caller's subtree."""
    ctx = ctx or context.require()
    if ctx.is_system or ctx.scope_ids is None:
        return
    if scope_node_id is None or scope_node_id not in ctx.scope_ids:
        raise Forbidden("The record is outside your scope.", code="AUTH-SCOPE")


def require_purpose(classification: str, ctx: Context | None = None) -> None:
    ctx = ctx or context.require()
    if ctx.is_system:
        return
    if class_rank(classification) >= class_rank("restricted") and not ctx.purpose:
        raise PurposeRequired(classification)
    if not ctx.cleared_for(classification):
        raise Forbidden(f"Your clearance does not cover {classification} data.", code="AUTH-CLEARANCE")


def validate_purpose(ctx: Context, purpose: str | None) -> str | None:
    """Check a declared purpose code against ``purpose_code`` and the caller's role."""
    if not purpose:
        return None
    from syntegra.iam.models import PurposeCode

    pc = PurposeCode.unscoped.using(_registry()).filter(tenant_id=ctx.state_tenant_id, code=purpose).first()
    if pc is None:
        raise Forbidden(f"Unknown purpose {purpose}.", code="AUTH-PURPOSE")
    allowed = pc.allowed_roles or []
    if allowed and ctx.role_code not in allowed and not ctx.is_system:
        raise Forbidden(f"Purpose {purpose} is not permitted for your role.", code="AUTH-PURPOSE")
    return purpose


def visible_fields(model: type, ctx: Context | None = None) -> list[str]:
    """Columns of ``model`` the caller may see: classification at or below clearance, never secrets."""
    ctx = ctx or context.require()
    out = []
    for name, info in getattr(model, "ceda_fields", {}).items():
        if info.get("type") in ("secret", "sealed", "hash") or name.endswith(("_enc", "_hmac", "_hash")):
            continue
        cls = info.get("class") or "internal"
        if ctx.cleared_for(cls) or ctx.has(f"{getattr(model, 'ceda_entity', '')}.{name}:reveal"):
            out.append(name)
    return out


def trim(model: type, row: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
    allowed = set(visible_fields(model, ctx))
    return {k: v for k, v in row.items() if k in allowed}
