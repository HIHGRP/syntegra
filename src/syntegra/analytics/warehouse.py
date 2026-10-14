"""State data warehouse loader for infrastructure, budgets and funding (CR-006, FR-IDW-01 – FR-IDW-04).

``load`` reads the registry and operations zones of the current state and writes the warehouse zone in one
transaction: conformed dimensions (scope, scope closure, institution, facility — SCD type 2: a changed row is closed
and a new current row inserted) and dated facts and aggregates for the load date (replaced if the date is loaded
again, so the load is idempotent). In production the same transformations run on the CDC stream; this loader is
the reference implementation and the scheduled batch.

``state_overview`` serves the Commissioner for Education (and the ministry and LGAs) from the warehouse, trimmed
to the caller's scope through ``dim_scope_closure``.
"""

from __future__ import annotations

import datetime as dt
import time
import uuid
from collections import defaultdict
from collections.abc import Callable, Iterable
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import Max

from syntegra.analytics.models import (
    AggInfrastructureScope,
    DimFacility,
    DimInstitution,
    DimScope,
    DimScopeClosure,
    FactBudgetExecution,
    FactFacilityCondition,
    FactFunding,
    FactMaintenanceWork,
)
from syntegra.core import authz, context
from syntegra.core.errors import NotFound
from syntegra.core.zones import current_alias
from syntegra.estate.domain import rules

ROLLUP_LEVELS = ("country", "state", "authority", "lga", "network", "institution", "agency", "formation")


def _date_key(d: dt.date) -> int:
    return int(d.strftime("%Y%m%d"))


class _Loader:
    def __init__(self, on: dt.date) -> None:
        ctx = context.require()
        self.tenant = ctx.state_tenant_id
        self.alias = current_alias("dw")
        self.on = on
        self.dk = _date_key(on)
        self.batch = int(time.time() * 1000)

    def q(self, model: Any) -> Any:
        return model.unscoped.using(self.alias).filter(tenant_id=self.tenant)

    def next_key(self, model: Any, field: str) -> Callable[[], int]:
        start = self.q(model).aggregate(m=Max(field))["m"] or 0
        counter = iter(range(start + 1, 2**62))
        return lambda: next(counter)

    def scd2(self, model: Any, key_field: str, natural: str, rows: dict[Any, dict[str, Any]]) -> dict[Any, int]:
        """Upsert current rows keyed by a natural id; returns natural id → surrogate key of the current row."""
        current = {getattr(r, natural): r for r in self.q(model).filter(is_current=True)}
        nxt = self.next_key(model, key_field)
        keys: dict[Any, int] = {}
        new = []
        for nat, attrs in rows.items():
            cur = current.get(nat)
            if cur is not None and all(getattr(cur, k) == v for k, v in attrs.items()):
                keys[nat] = getattr(cur, key_field)
                continue
            if cur is not None:
                self.q(model).filter(**{key_field: getattr(cur, key_field)}).update(
                    is_current=False, row_valid_to=self.on
                )
            keys[nat] = nxt()
            new.append(
                model(
                    tenant_id=self.tenant,
                    **{key_field: keys[nat], natural: nat},
                    **attrs,
                    row_valid_from=self.on,
                    row_valid_to=None,
                    is_current=True,
                    load_batch_id=self.batch,
                )
            )
        gone = set(current) - set(rows)
        if gone:
            self.q(model).filter(**{f"{natural}__in": list(gone)}, is_current=True).update(
                is_current=False, row_valid_to=self.on
            )
        model.unscoped.using(self.alias).bulk_create(new, batch_size=500)
        return keys

    def replace(self, model: Any, rows: Iterable[Any]) -> int:
        self.q(model).filter(date_key=self.dk).delete()
        objs = list(rows)
        model.unscoped.using(self.alias).bulk_create(objs, batch_size=500)
        return len(objs)


# --------------------------------------------------------------------------- dimensions
def _scopes(ld: _Loader) -> tuple[dict[uuid.UUID, int], dict[uuid.UUID, Any]]:
    from syntegra.governance.models import ScopeClosure, ScopeNode

    nodes = {n.id: n for n in ScopeNode.objects.all()}
    keys = ld.scd2(
        DimScope,
        "scope_key",
        "scope_node_id",
        {
            n.id: {
                "level": n.level,
                "code": n.code[:40],
                "name": n.name,
                "path": n.path[:512],
                "state_code": None,
                "lga_code": n.code[:40] if n.level == "lga" else None,
                "ownership": n.ownership,
            }
            for n in nodes.values()
        },
    )
    ld.q(DimScopeClosure).delete()
    DimScopeClosure.unscoped.using(ld.alias).bulk_create(
        [
            DimScopeClosure(
                tenant_id=ld.tenant,
                ancestor_key=keys[a],
                descendant_key=keys[d],
                depth=depth,
                load_batch_id=ld.batch,
            )
            for a, d, depth in ScopeClosure.objects.values_list("ancestor_id", "descendant_id", "depth")
            if a in keys and d in keys
        ],
        batch_size=1000,
    )
    return keys, nodes


def _institutions(ld: _Loader, scope_keys: dict[uuid.UUID, int]) -> tuple[dict[uuid.UUID, int], list[Any]]:
    from syntegra.institutions.models import Institution

    insts = [i for i in Institution.objects.exclude(status__in=("closed", "merged")) if i.scope_node_id in scope_keys]
    keys = ld.scd2(
        DimInstitution,
        "institution_key",
        "institution_id",
        {
            i.id: {
                "scope_key": scope_keys[i.scope_node_id],
                "lga_scope_key": scope_keys.get(i.lga_scope_id, scope_keys[i.scope_node_id]),
                "institution_code": i.institution_code,
                "name": i.name,
                "category": i.category,
                "ownership": i.ownership,
                "is_public": i.is_public,
                "location_class": i.location_class,
                "comparison_group": None,
                "onboarding_status": i.onboarding_status,
            }
            for i in insts
        },
    )
    return keys, insts


# --------------------------------------------------------------------------- infrastructure (FR-IDW-01, FR-IDW-02)
def _infrastructure(
    ld: _Loader, inst_keys: dict[uuid.UUID, int], insts: list[Any]
) -> tuple[dict[uuid.UUID, dict[str, Any]], int]:
    from syntegra.estate.models import FacilityAction, FacilityAssessment, MaintenanceSchedule, PropertySite
    from syntegra.learners.models import Enrolment
    from syntegra.operations.models import Asset, Building, MaintenanceRequest, Room

    by_node = {i.scope_node_id: i for i in insts}
    facilities: list[tuple[str, Any, uuid.UUID]] = []  # kind, obj, institution id
    for kind, model, qs_filter in (
        ("site", PropertySite, {"status": "active"}),
        ("building", Building, {"status": "active"}),
        ("room", Room, {"status": "active"}),
        ("asset", Asset, {}),
    ):
        for obj in model.objects.filter(**qs_filter):
            inst = by_node.get(obj.scope_node_id)
            if inst is not None:
                facilities.append((kind, obj, inst.id))
    fac_keys = ld.scd2(
        DimFacility,
        "facility_key",
        "subject_id",
        {
            obj.id: {
                "subject_kind": kind,
                "institution_key": inst_keys[iid],
                "name": (getattr(obj, "name", None) or getattr(obj, "code", "") or "")[:300],
                "room_type": getattr(obj, "room_type", None) if kind == "room" else None,
                "asset_category": getattr(obj, "category", None) if kind == "asset" else None,
                "capacity": getattr(obj, "capacity", None) if kind == "room" else None,
                "built_year": getattr(obj, "built_year", None) if kind == "building" else None,
            }
            for kind, obj, iid in facilities
        },
    )
    latest: dict[uuid.UUID, Any] = {}
    for x in FacilityAssessment.objects.filter(assessed_on__lte=ld.on).order_by("-assessed_on", "-created_at"):
        latest.setdefault(x.subject_id, x)
    open_actions = list(FacilityAction.objects.filter(status__in=("open", "acknowledged", "in_progress")))
    acts: dict[uuid.UUID, list[Any]] = defaultdict(list)
    acts_by_inst: dict[uuid.UUID, list[Any]] = defaultdict(list)
    for a in open_actions:
        acts[a.subject_id].append(a)
        acts_by_inst[a.institution_id].append(a)
    sched_by_subject: dict[uuid.UUID, list[Any]] = defaultdict(list)
    sched_by_inst: dict[uuid.UUID, list[Any]] = defaultdict(list)
    for s in MaintenanceSchedule.objects.filter(status="active"):
        sched_by_subject[s.subject_id].append(s)
        sched_by_inst[s.institution_id].append(s)

    facts = []
    stats: dict[uuid.UUID, dict[str, Any]] = {
        i.id: defaultdict(int, {"water": False, "power": False, "assessed": False, "backlog": 0}) for i in insts
    }
    for kind, obj, iid in facilities:
        x = latest.get(obj.id)
        st = stats[iid]
        usable = x is None or x.usability in rules.USABLE
        unsafe = x is not None and x.usability in rules.UNSAFE
        backlog = (x.repair_estimate_minor or 0) if x is not None and x.usability != "fully_usable" else 0
        facts.append(
            FactFacilityCondition(
                tenant_id=ld.tenant,
                date_key=ld.dk,
                facility_key=fac_keys[obj.id],
                institution_key=inst_keys[iid],
                condition_grade=x.condition_grade if x else None,
                usability=x.usability if x else None,
                is_usable=usable,
                assessed_on=x.assessed_on if x else None,
                days_since_assessment=(ld.on - x.assessed_on).days if x else None,
                learners_affected=x.learners_affected if x else None,
                repair_estimate_minor=x.repair_estimate_minor if x else None,
                currency=x.currency if x else None,
                open_actions=len(acts[obj.id]),
                open_critical_actions=sum(1 for a in acts[obj.id] if a.priority == "critical"),
                overdue_maintenance=sum(1 for s in sched_by_subject[obj.id] if s.next_due_on < ld.on),
                load_batch_id=ld.batch,
            )
        )
        st["assessed"] = st["assessed"] or x is not None
        st["backlog"] += backlog
        st["unsafe_in_use"] += int(unsafe and x is not None and x.in_use)
        utilities = {**(getattr(obj, "facilities", None) or {}), **((x.utilities or {}) if x else {})}
        st["water"] = st["water"] or bool(utilities.get("water"))
        st["power"] = st["power"] or bool(utilities.get("power"))
        if kind == "site":
            st["sites"] += 1
            st["sites_fenced"] += int(obj.fenced == "fully_fenced")
            st["sites_encroached"] += int(obj.encroachment in ("suspected", "confirmed", "in_dispute"))
        elif kind == "building":
            st["buildings"] += 1
            st["buildings_unsafe"] += int(unsafe)
        elif kind == "room" and obj.room_type == "classroom":
            st["classrooms"] += 1
            st["classrooms_usable"] += int(usable)
        elif kind == "room" and obj.room_type == "toilet":
            st["toilets_usable"] += int(usable)
    n_conditions = ld.replace(FactFacilityCondition, facts)

    since = ld.on - dt.timedelta(days=30)
    work = []
    for i in insts:
        reqs = list(MaintenanceRequest.objects.filter(scope_node_id=i.scope_node_id))
        done = [r for r in reqs if r.completed_at and r.completed_at.date() >= since]
        days = [(r.completed_at - r.created_at).total_seconds() / 86400 for r in done if r.created_at]
        acts_i = acts_by_inst[i.id]
        st = stats[i.id]
        st["actions_open"] = len(acts_i)
        st["actions_critical_open"] = sum(1 for a in acts_i if a.priority == "critical")
        st["actions_overdue"] = sum(1 for a in acts_i if a.due_on < ld.on)
        work.append(
            FactMaintenanceWork(
                tenant_id=ld.tenant,
                date_key=ld.dk,
                institution_key=inst_keys[i.id],
                requests_open=sum(1 for r in reqs if r.status not in ("completed", "cancelled")),
                requests_completed_30d=len(done),
                preventive_completed_30d=sum(1 for r in done if r.is_preventive),
                mean_days_to_complete=Decimal(str(round(sum(days) / len(days), 2))) if days else None,
                maintenance_due=sum(
                    1 for s in sched_by_inst[i.id] if ld.on <= s.next_due_on <= ld.on + dt.timedelta(14)
                ),
                maintenance_overdue=sum(1 for s in sched_by_inst[i.id] if s.next_due_on < ld.on),
                actions_open=st["actions_open"],
                actions_overdue=st["actions_overdue"],
                cost_30d_minor=sum(r.cost_minor or 0 for r in done),
                currency="NGN",
                load_batch_id=ld.batch,
            )
        )
    ld.replace(FactMaintenanceWork, work)
    learners: dict[uuid.UUID, int] = defaultdict(int)
    for iid in Enrolment.objects.filter(status="active", is_primary=True).values_list("institution_id", flat=True):
        learners[iid] += 1
    for i in insts:
        stats[i.id]["learners"] = learners.get(i.id, 0)
    return stats, n_conditions


def _rollup(
    ld: _Loader, scope_keys: dict[uuid.UUID, int], nodes: dict[uuid.UUID, Any], insts: list[Any], stats: dict[Any, Any]
) -> int:
    from syntegra.governance.models import ScopeClosure

    node_inst = {i.scope_node_id: i.id for i in insts}
    totals: dict[uuid.UUID, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    for anc, desc in ScopeClosure.objects.filter(descendant_id__in=list(node_inst)).values_list(
        "ancestor_id", "descendant_id"
    ):
        node = nodes.get(anc)
        if node is None or node.level not in ROLLUP_LEVELS:
            continue
        s, t = stats[node_inst[desc]], totals[anc]
        t["institutions"] += 1
        t["institutions_assessed"] += int(s["assessed"])
        t["institutions_with_water"] += int(s["water"])
        t["institutions_with_power"] += int(s["power"])
        for k in (
            "sites",
            "sites_fenced",
            "sites_encroached",
            "buildings",
            "buildings_unsafe",
            "classrooms",
            "classrooms_usable",
            "learners",
            "toilets_usable",
            "unsafe_in_use",
            "actions_open",
            "actions_critical_open",
            "actions_overdue",
            "backlog",
        ):
            t[k] += s[k]
    rows = []
    for anc, t in totals.items():
        index = rules.infrastructure_index(
            t["classrooms"],
            t["classrooms_usable"],
            t["institutions"],
            t["institutions_with_water"],
            t["institutions_with_power"],
            t["unsafe_in_use"],
            t["actions_open"],
            t["actions_overdue"],
        )
        rows.append(
            AggInfrastructureScope(
                tenant_id=ld.tenant,
                date_key=ld.dk,
                scope_key=scope_keys[anc],
                level=nodes[anc].level,
                institutions=t["institutions"],
                institutions_assessed=t["institutions_assessed"],
                sites=t["sites"],
                sites_fenced=t["sites_fenced"],
                sites_encroached=t["sites_encroached"],
                buildings=t["buildings"],
                buildings_unsafe=t["buildings_unsafe"],
                classrooms=t["classrooms"],
                classrooms_usable=t["classrooms_usable"],
                learners=t["learners"],
                learners_per_usable_classroom=(
                    Decimal(str(round(t["learners"] / t["classrooms_usable"], 2))) if t["classrooms_usable"] else None
                ),
                toilets_usable=t["toilets_usable"],
                institutions_with_water=t["institutions_with_water"],
                institutions_with_power=t["institutions_with_power"],
                facilities_unsafe_in_use=t["unsafe_in_use"],
                actions_open=t["actions_open"],
                actions_critical_open=t["actions_critical_open"],
                actions_overdue=t["actions_overdue"],
                repair_backlog_minor=t["backlog"],
                currency="NGN",
                infrastructure_index=Decimal(str(index)) if index is not None else None,
                load_batch_id=ld.batch,
            )
        )
    return ld.replace(AggInfrastructureScope, rows)


# --------------------------------------------------------------------------- budgets and funding (FR-IDW-04)
def _budgets(ld: _Loader, inst_keys: dict[uuid.UUID, int]) -> int:
    from syntegra.finance.models import Budget, BudgetLine, CostCentre

    approved = {b.id: b for b in Budget.objects.filter(status="approved")}
    centres = {c.id: c for c in CostCentre.objects.all()}
    agg: dict[tuple[Any, ...], list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for ln in BudgetLine.objects.filter(budget_id__in=list(approved)):
        cc = centres.get(ln.cost_centre_id)
        if cc is None or cc.institution_id not in inst_keys:
            continue
        k = (cc.institution_id, cc.code, ln.economic_code, ln.funding_source_kind, approved[ln.budget_id].fiscal_year)
        v = agg[k]
        v[0] += ln.original_minor
        v[1] += ln.revised_minor
        v[2] += ln.committed_minor
        v[3] += ln.actual_minor
    return ld.replace(
        FactBudgetExecution,
        (
            FactBudgetExecution(
                tenant_id=ld.tenant,
                date_key=ld.dk,
                institution_key=inst_keys[iid],
                cost_centre_code=cc,
                economic_code=ec,
                funding_source_kind=src,
                fiscal_year=fy,
                original_minor=o,
                revised_minor=r,
                committed_minor=c,
                actual_minor=a,
                available_minor=r - c - a,
                currency="NGN",
                load_batch_id=ld.batch,
            )
            for (iid, cc, ec, src, fy), (o, r, c, a) in agg.items()
        ),
    )


def _funding(ld: _Loader, inst_keys: dict[uuid.UUID, int]) -> int:
    from syntegra.funding.models import FundingAgreement, FundingApplication, FundingProgramme

    codes = dict(FundingProgramme.objects.values_list("id", "code"))
    agg: dict[tuple[Any, ...], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for x in FundingApplication.objects.all():
        if x.institution_id not in inst_keys:
            continue
        t = agg[(x.institution_id, codes.get(x.programme_id, "?"), x.applicant_kind)]
        t["applications"] += 1
        if x.status == "approved":
            t["approved"] += 1
            t["approved_amount"] += x.amount_approved_minor or 0
    for a in FundingAgreement.objects.all():
        if a.institution_id not in inst_keys:
            continue
        t = agg[(a.institution_id, codes.get(a.programme_id, "?"), a.beneficiary_kind)]
        t["disbursed"] += a.disbursed_minor
        t["repaid"] += a.repaid_minor
        t["outstanding"] += a.outstanding_minor
        t["arrears"] += a.arrears_minor
        t["in_arrears"] += int(a.status == "in_arrears")
    return ld.replace(
        FactFunding,
        (
            FactFunding(
                tenant_id=ld.tenant,
                date_key=ld.dk,
                institution_key=inst_keys[iid],
                programme_code=code,
                beneficiary_kind=kind,
                applications=t["applications"],
                approved=t["approved"],
                agreements_in_arrears=t["in_arrears"],
                approved_amount_minor=t["approved_amount"],
                disbursed_minor=t["disbursed"],
                repaid_minor=t["repaid"],
                outstanding_minor=t["outstanding"],
                arrears_minor=t["arrears"],
                currency="NGN",
                load_batch_id=ld.batch,
            )
            for (iid, code, kind), t in agg.items()
        ),
    )


# --------------------------------------------------------------------------- entry points
def load(on: dt.date | None = None) -> dict[str, int]:
    """Load the warehouse for the current state for ``on`` (default today). Needs warehouse:load or a system context."""
    ctx = context.require()
    if ctx.actor_kind != "system":
        authz.require("warehouse:load", ctx)
    ld = _Loader(on or dt.date.today())
    with transaction.atomic(using=ld.alias):
        scope_keys, nodes = _scopes(ld)
        inst_keys, insts = _institutions(ld, scope_keys)
        stats, n_conditions = _infrastructure(ld, inst_keys, insts)
        aggregates = _rollup(ld, scope_keys, nodes, insts, stats)
        budget_rows = _budgets(ld, inst_keys)
        funding_rows = _funding(ld, inst_keys)
    return {
        "date_key": ld.dk,
        "scopes": len(scope_keys),
        "institutions": len(inst_keys),
        "facility_conditions": n_conditions,
        "scope_aggregates": aggregates,
        "budget_rows": budget_rows,
        "funding_rows": funding_rows,
    }


def _agg_row(a: AggInfrastructureScope, name: str, node_id: uuid.UUID) -> dict[str, Any]:
    return {
        "scope_node_id": node_id,
        "name": name,
        "level": a.level,
        **{
            f: getattr(a, f)
            for f in (
                "institutions",
                "institutions_assessed",
                "sites",
                "sites_fenced",
                "sites_encroached",
                "buildings",
                "buildings_unsafe",
                "classrooms",
                "classrooms_usable",
                "learners",
                "learners_per_usable_classroom",
                "toilets_usable",
                "institutions_with_water",
                "institutions_with_power",
                "facilities_unsafe_in_use",
                "actions_open",
                "actions_critical_open",
                "actions_overdue",
                "repair_backlog_minor",
                "infrastructure_index",
            )
        },
        "usable_share": round(a.classrooms_usable / a.classrooms, 4) if a.classrooms else None,
    }


def state_overview(scope_node_id: uuid.UUID | None = None) -> dict[str, Any]:
    """EST-03: the caller's scope (or a node within it) from the latest load, its children and its institutions."""
    ctx = context.require()
    authz.require("warehouse:view", ctx)
    node_id = scope_node_id or ctx.scope_node_id
    if node_id is None:
        raise NotFound("scope", "")
    authz.require_scope(node_id, ctx)
    alias = current_alias("dw")
    tenant = ctx.state_tenant_id
    dims = {d.scope_key: d for d in DimScope.unscoped.using(alias).filter(tenant_id=tenant, is_current=True)}
    key = next((k for k, d in dims.items() if d.scope_node_id == node_id), None)
    latest = AggInfrastructureScope.unscoped.using(alias).filter(tenant_id=tenant).aggregate(m=Max("date_key"))["m"]
    if key is None or latest is None:
        return {"loaded": False, "date": None, "scope": None, "children": [], "institutions": []}
    aggs = {
        a.scope_key: a for a in AggInfrastructureScope.unscoped.using(alias).filter(tenant_id=tenant, date_key=latest)
    }
    below = DimScopeClosure.unscoped.using(alias).filter(tenant_id=tenant, ancestor_key=key)
    child_keys = [c.descendant_key for c in below if c.depth == 1]
    inst_keys = [
        c.descendant_key
        for c in below
        if c.depth >= 1 and dims.get(c.descendant_key) and dims[c.descendant_key].level == "institution"
    ]

    def row(k: int) -> dict[str, Any] | None:
        a, d = aggs.get(k), dims.get(k)
        return _agg_row(a, d.name, d.scope_node_id) if a and d else None

    children = [r for r in (row(k) for k in child_keys) if r]
    institutions = [r for r in (row(k) for k in inst_keys) if r]
    institutions.sort(key=lambda r: (r["infrastructure_index"] is None, r["infrastructure_index"] or 0))
    return {
        "loaded": True,
        "date": dt.datetime.strptime(str(latest), "%Y%m%d").date(),
        "scope": row(key),
        "children": sorted(children, key=lambda r: r["name"]),
        "institutions": institutions[:200],
    }
