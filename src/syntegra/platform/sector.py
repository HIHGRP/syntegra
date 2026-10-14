"""National sector registries (decision CD-23): registry tenants beside the 37 states.

A sector registry has its own tenant (kind ``sector_registry``), GLID block, roles, purposes and policies, and a scope
hierarchy rooted at ``NG → <code>``; owning bodies, their structures and institutions hang below the root, and the
36 states and the FCT sit under ``NG`` as location references for institutions. Used by the Federal Security Education
registry (``ng-fse``) and the Federal Institutions registry (``ng-fed``).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from syntegra.core import context, tenancy, uow
from syntegra.core.tenancy import state_tenant_id
from syntegra.platform.states import STATES


@dataclass
class Provisioned:
    tenant_id: uuid.UUID
    root_scope_id: uuid.UUID
    admin_user_id: uuid.UUID | None = None
    role_ids: dict[str, uuid.UUID] = field(default_factory=dict)


def system_context(code: str) -> context.Context:
    tid = state_tenant_id(code)
    return context.system(tid, tid, correlation_id=f"{code.lower()}-provision")


def provision(
    code: str,
    name: str,
    *,
    hosts: list[str],
    admin_role: str,
    admin_username: str | None = None,
    admin_password: str | None = None,
) -> Provisioned:
    """Create (idempotently) the registry tenant, scope root, state location nodes and configuration."""
    from syntegra.governance import services as gov
    from syntegra.governance.models import ScopeNode
    from syntegra.iam import services as iam
    from syntegra.iam.models import AppUser
    from syntegra.platform.bootstrap import _copy_code_lists, registry_tenant, seed_registry_config

    tid = registry_tenant(code, name, "sector_registry", hosts, state_code=None)
    tenancy.clear_caches()
    ctx = system_context(code)
    with context.use(ctx):
        _copy_code_lists(tid)
        with uow.command("registry", None, action="provision", record_kind="tenant") as cmd:
            cmd.record_id = tid
            ng = ScopeNode.objects.filter(code="NG").first() or gov.add_node(
                cmd, parent=None, level="country", code="NG", name="Nigeria"
            )
            root = ScopeNode.objects.filter(code=code).first() or gov.add_node(
                cmd, parent=ng, level="authority", code=code, name=name, ref_kind="tenant", ref_id=tid
            )
            have = set(ScopeNode.objects.filter(level="state").values_list("code", flat=True))
            for scode, sname, _cap in STATES:  # location references for institutions
                if scode not in have:
                    gov.add_node(cmd, parent=ng, level="state", code=scode, name=sname)
            out = Provisioned(tid, root.id)
            out.role_ids = seed_registry_config(cmd, root)
        if admin_username:
            admin = AppUser.objects.filter(username=admin_username).first()
            if admin is None:
                admin = iam.create_user(
                    ctx, username=admin_username, display_name=f"{name} Administrator", password=admin_password
                )
                iam.grant_role(ctx, user=admin, role_code=admin_role, scope_id=root.id)
            out.admin_user_id = admin.id
    return out


def location_nodes() -> dict[str, Any]:
    """State location nodes of the current sector registry (call inside its context)."""
    from syntegra.governance.models import ScopeNode

    return {s.code: s for s in ScopeNode.objects.filter(level="state")}
