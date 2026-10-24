"""Semantic layer (CEDA §12): governed metric definitions computed within the caller's scope.

Every metric is looked up in the CEDA metric catalogue (``ENR-COUNT``, ``ATT-RATE`` …), computed only over
records inside the caller's grant subtree and grouped by scope node. Cells describing fewer than *k* people
(policy ``SUPPRESS``, default 5) are suppressed before they leave the service, so dashboards and exports
can never show small numbers that identify a child.
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections import defaultdict
from typing import Any

from django.db.models import Count, Q

from syntegra.attendance.domain import rates
from syntegra.attendance.models import AttendanceMark, AttendanceRegister
from syntegra.core import authz, catalog, context, policy
from syntegra.core.errors import HardValidation
from syntegra.governance.models import ScopeNode
from syntegra.learners.models import Enrolment

SUPPORTED = ("ENR-COUNT", "ATT-RATE", "CUR-GAPS-OPEN")


def _k(scope_node_id: uuid.UUID | None) -> int:
    rule = policy.effective_rule("SUPPRESS", scope_node_id) if scope_node_id else None
    return int(rule.parameters.get("k", 5)) if rule else 5


def _suppress(cells: list[dict[str, Any]], k: int, n_key: str = "n") -> list[dict[str, Any]]:
    for c in cells:
        if 0 < c[n_key] < k:
            c.update({"value": None, n_key: None, "suppressed": True})
        else:
            c["suppressed"] = False
    return cells


def _names(ids: set[uuid.UUID]) -> dict[uuid.UUID, tuple[str, str]]:
    return {n.id: (n.code, n.name) for n in ScopeNode.objects.filter(id__in=list(ids))}


def compute(
    metric_id: str, *, start: dt.date | None = None, end: dt.date | None = None, group_by: str = "institution"
) -> dict[str, Any]:
    ctx = context.require()
    authz.require("metric:view", ctx)
    if metric_id not in SUPPORTED:
        raise HardValidation(
            "METRIC-UNSUPPORTED",
            "Metric not available in the operational semantic layer",
            f"{metric_id} is served from the warehouse marts.",
        )
    spec = catalog.metric(metric_id)
    end = end or dt.date.today()
    start = start or end - dt.timedelta(days=30)
    k = _k(ctx.scope_node_id)
    scope = list(ctx.scope_ids) if ctx.scope_ids is not None else None
    if metric_id == "ENR-COUNT":
        qs = Enrolment.objects.filter(status="active", is_primary=True)
        if scope is not None:
            qs = qs.filter(scope_node_id__in=scope)
        rows = qs.values("scope_node_id").annotate(n=Count("learner_id", distinct=True))
        cells = [{"scope_node_id": r["scope_node_id"], "n": r["n"], "value": r["n"]} for r in rows]
    elif metric_id == "ATT-RATE":
        regs = AttendanceRegister.objects.filter(session_date__gte=start, session_date__lte=end)
        if scope is not None:
            regs = regs.filter(scope_node_id__in=scope)
        reg_scope = dict(regs.values_list("id", "scope_node_id"))
        codes: dict[uuid.UUID, list[str]] = defaultdict(list)
        learners: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
        for reg_id, code, learner in AttendanceMark.objects.filter(
            register_id__in=list(reg_scope), session_date__gte=start, session_date__lte=end
        ).values_list("register_id", "code", "learner_id"):
            node = reg_scope[reg_id]
            codes[node].append(code)
            learners[node].add(learner)
        cells = [
            {"scope_node_id": node, "n": len(learners[node]), "value": rates.summarise(c).rate}
            for node, c in codes.items()
        ]
    else:  # CUR-GAPS-OPEN
        from syntegra.curriculum.models import CoverageGap

        qs = CoverageGap.objects.filter(Q(status__in=("open", "in_progress", "escalated")))
        if scope is not None:
            qs = qs.filter(scope_node_id__in=scope)
        rows = qs.values("scope_node_id").annotate(n=Count("id"))
        cells = [{"scope_node_id": r["scope_node_id"], "n": r["n"], "value": r["n"], "count_of": "gaps"} for r in rows]
        k = 0  # counts of gaps describe classes, not children
    names = _names({c["scope_node_id"] for c in cells})
    for c in cells:
        c["scope_code"], c["scope_name"] = names.get(c["scope_node_id"], ("?", "?"))
    cells = _suppress(sorted(cells, key=lambda c: c["scope_code"]), k)
    visible = [c for c in cells if not c["suppressed"]]
    total_n = sum(c["n"] for c in visible)
    return {
        "metric": metric_id,
        "name": spec["name"],
        "formula": spec["formula"],
        "direction": spec.get("direction"),
        "from": start,
        "to": end,
        "group_by": group_by,
        "k": k,
        "cells": cells,
        "total_visible_n": total_n,
    }
