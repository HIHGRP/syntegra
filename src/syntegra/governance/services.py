"""Governance hierarchy services: scope nodes with a maintained closure table (MFS §4, CEDA §7.3)."""

from __future__ import annotations

import datetime as dt
import uuid

from syntegra.core import uow
from syntegra.core.errors import HardValidation
from syntegra.governance.models import ScopeClosure, ScopeNode

LEVEL_ORDER = ["global", "country", "state", "authority", "lga", "network", "institution", "campus", "faculty",
               "department", "programme", "class"]


def add_node(cmd: uow.Command, *, parent: ScopeNode | None, level: str, code: str, name: str,
             ref_kind: str | None = None, ref_id: uuid.UUID | None = None, ownership: str | None = None) -> ScopeNode:
    """Create a scope node and its closure rows inside an open command (registry zone)."""
    if parent is not None and LEVEL_ORDER.index(level) <= LEVEL_ORDER.index(parent.level) and level != "network":
        raise HardValidation("GOV-SCOPE-LEVEL", "Invalid hierarchy",
                             f"A {level} cannot sit under a {parent.level}.")
    node = ScopeNode(
        parent_id=parent.id if parent else None, level=level, code=code, name=name,
        path=f"{parent.path}.{code}" if parent else code, depth=(parent.depth + 1) if parent else 0,
        ref_kind=ref_kind, ref_id=ref_id, ownership=ownership, valid_from=dt.date.today(),
    )
    # scope nodes are themselves authorised by their parent: add under lock-free insert
    node.save(using=cmd.alias)
    cmd._capture(node, None)
    rows = [ScopeClosure(tenant_id=node.tenant_id, ancestor_id=node.id, descendant_id=node.id, depth=0)]
    if parent is not None:
        for anc in ScopeClosure.unscoped.using(cmd.alias).filter(tenant_id=node.tenant_id, descendant_id=parent.id):
            rows.append(ScopeClosure(tenant_id=node.tenant_id, ancestor_id=anc.ancestor_id, descendant_id=node.id,
                                     depth=anc.depth + 1))
    ScopeClosure.unscoped.using(cmd.alias).bulk_create(rows)
    if cmd.record_id is None:
        cmd.record_id = node.id
    return node
