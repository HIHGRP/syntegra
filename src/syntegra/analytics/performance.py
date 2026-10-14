"""School performance for the state control room and the institution league (MFS CMD-101, CMD-102).

For every institution in the caller's scope: learners on roll, the mean of each learner's weighted subject totals
(continuous assessment + examination, out of 100), the pass rate (subject totals of 50 or more), the share of
learners with five or more passes, and attendance (present, late or approved activity ÷ sessions recorded). The
performance index combines them — 60 % mean score, 25 % pass rate, 15 % attendance — and institutions are ranked
only within their comparison group (primary, secondary, tertiary: P7, context before comparison). The best learner
is the highest overall average with at least five assessed subjects (three in tertiary), attendance breaking ties.

Results are computed in the database from the marks and attendance, cached for ten minutes per state and scope.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import uuid
from collections import defaultdict
from typing import Any

from django.core.cache import cache
from django.db import connections

from syntegra.core import authz, context
from syntegra.core.zones import current_alias

GROUPS = {
    "primary": ("eccde_centre", "nursery_primary", "primary"),
    "secondary": ("junior_secondary", "senior_secondary", "combined_secondary", "technical_college"),
    "tertiary": ("university", "polytechnic", "monotechnic", "college_of_education", "school_of_nursing"),
}
GROUP_LABEL = {"primary": "Primary schools", "secondary": "Secondary schools", "tertiary": "Tertiary institutions"}
MIN_SUBJECTS = {"primary": 5, "secondary": 5, "tertiary": 3}
WEIGHTS = (0.60, 0.25, 0.15)
PRESENT = ("P", "L", "AA")


def group_of(category: str) -> str | None:
    return next((g for g, cats in GROUPS.items() if category in cats), None)


def index(mean: float | None, pass_rate: float | None, attendance: float | None) -> float | None:
    if mean is None:
        return None
    return round(WEIGHTS[0] * mean + WEIGHTS[1] * 100 * (pass_rate or 0) + WEIGHTS[2] * 100 * (attendance or 0), 2)


def _learner_results(tenant: uuid.UUID) -> dict[uuid.UUID, tuple[float, int, int]]:
    """learner → (mean weighted subject total, subjects assessed, subjects passed)."""
    sql = (
        "SELECT t.learner_id, AVG(t.total), COUNT(*), SUM(t.total >= 50) FROM ("
        " SELECT r.learner_id, a.class_subject_plan_id, SUM(r.score / a.max_mark * a.weight) AS total"
        " FROM assessment_result r JOIN assessment a ON a.id = r.assessment_id AND a.tenant_id = r.tenant_id"
        " WHERE r.tenant_id = %s AND r.score IS NOT NULL GROUP BY r.learner_id, a.class_subject_plan_id"
        ") t GROUP BY t.learner_id"
    )
    with connections[current_alias("ops")].cursor() as cur:
        cur.execute(sql, [tenant.bytes])
        return {uuid.UUID(bytes=bytes(r[0])): (float(r[1]), int(r[2]), int(r[3] or 0)) for r in cur.fetchall()}


def _learner_attendance(tenant: uuid.UUID) -> dict[uuid.UUID, tuple[int, int]]:
    """learner → (sessions attended, sessions recorded)."""
    sql = (
        "SELECT learner_id, SUM(code IN ('P', 'L', 'AA')), SUM(code <> 'NR') FROM attendance_mark"
        " WHERE tenant_id = %s GROUP BY learner_id"
    )
    with connections[current_alias("ops")].cursor() as cur:
        cur.execute(sql, [tenant.bytes])
        return {uuid.UUID(bytes=bytes(r[0])): (int(r[1] or 0), int(r[2] or 0)) for r in cur.fetchall()}


def _compute(tenant: uuid.UUID, scope_ids: frozenset[uuid.UUID] | None) -> dict[str, Any]:
    from syntegra.governance.models import ScopeNode
    from syntegra.institutions.models import Institution
    from syntegra.learners.models import Enrolment, Learner

    insts = {i.id: i for i in Institution.objects.exclude(status__in=("closed", "merged"))}
    if scope_ids is not None:
        insts = {k: i for k, i in insts.items() if i.scope_node_id in scope_ids}
    lgas = dict(ScopeNode.objects.filter(level="lga").values_list("id", "name"))
    results = _learner_results(tenant)
    attendance = _learner_attendance(tenant)
    per_inst: dict[uuid.UUID, dict[str, Any]] = defaultdict(
        lambda: {
            "learners": 0,
            "assessed": 0,
            "sum_mean": 0.0,
            "subjects": 0,
            "passes": 0,
            "five_passes": 0,
            "attended": 0,
            "sessions": 0,
        }
    )
    candidates: dict[str, list[tuple[float, float, uuid.UUID, uuid.UUID, int]]] = defaultdict(list)
    for lid, iid in Enrolment.objects.filter(
        status="active", is_primary=True, institution_id__in=list(insts)
    ).values_list("learner_id", "institution_id"):
        s = per_inst[iid]
        s["learners"] += 1
        att = attendance.get(lid)
        if att:
            s["attended"] += att[0]
            s["sessions"] += att[1]
        res = results.get(lid)
        if res is None:
            continue
        mean, n, passed = res
        s["assessed"] += 1
        s["sum_mean"] += mean
        s["subjects"] += n
        s["passes"] += passed
        s["five_passes"] += int(passed >= 5)
        group = group_of(insts[iid].category)
        if group and n >= MIN_SUBJECTS[group]:
            rate = att[0] / att[1] if att and att[1] else 0.0
            candidates[group].append((round(mean, 2), rate, lid, iid, n))
    rows = []
    for iid, s in per_inst.items():
        inst = insts[iid]
        group = group_of(inst.category)
        if group is None:
            continue
        avg: float | None = round(s["sum_mean"] / s["assessed"], 2) if s["assessed"] else None
        pass_rate = round(s["passes"] / s["subjects"], 4) if s["subjects"] else None
        att_rate = round(s["attended"] / s["sessions"], 4) if s["sessions"] else None
        rows.append(
            {
                "institution_id": iid,
                "name": inst.name,
                "group": group,
                "lga": lgas.get(inst.lga_scope_id, ""),
                "lga_scope_id": inst.lga_scope_id,
                "learners": s["learners"],
                "assessed": s["assessed"],
                "mean_score": avg,
                "pass_rate": pass_rate,
                "five_passes_rate": round(s["five_passes"] / s["assessed"], 4) if s["assessed"] else None,
                "attendance_rate": att_rate,
                "index": index(avg, pass_rate, att_rate),
            }
        )
    league: dict[str, list[dict[str, Any]]] = {}
    for g in GROUPS:
        ranked = sorted((r for r in rows if r["group"] == g and r["index"] is not None), key=lambda r: -r["index"])
        for i, r in enumerate(ranked, start=1):
            r["rank"] = i
            r["of"] = len(ranked)
        league[g] = ranked
    # best learners per group (names fetched only for the top ten)
    best: dict[str, list[dict[str, Any]]] = {}
    for g, cands in candidates.items():
        top = sorted(cands, key=lambda c: (-c[0], -c[1]))[:10]
        people = {lr.id: lr for lr in Learner.objects.filter(id__in=[c[2] for c in top])}
        best[g] = [
            {
                "learner_id": lid,
                "name": f"{people[lid].legal_given_name} {people[lid].legal_family_name}" if lid in people else "?",
                "global_learner_id": people[lid].global_learner_id if lid in people else "",
                "institution": insts[iid].name,
                "institution_id": iid,
                "average": mean,
                "attendance_rate": round(rate, 4),
                "subjects": n,
            }
            for mean, rate, lid, iid, n in top
        ]
    by_lga: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["index"] is not None and r["group"] in ("primary", "secondary"):
            by_lga[r["group"]][r["lga"]].append(r["index"])
    lga_rows = {
        g: sorted(
            ({"lga": k, "index": round(sum(v) / len(v), 2), "schools": len(v)} for k, v in d.items()),
            key=lambda x: -float(x["index"]),  # type: ignore[arg-type]
        )
        for g, d in by_lga.items()
    }
    schools = [r for r in rows if r["group"] in ("primary", "secondary") and r["index"] is not None]
    learners = sum(r["learners"] for r in rows)
    assessed = [r for r in rows if r["mean_score"] is not None]
    tot_att = sum(per_inst[r["institution_id"]]["attended"] for r in rows)
    tot_ses = sum(per_inst[r["institution_id"]]["sessions"] for r in rows)
    tot_sub = sum(per_inst[r["institution_id"]]["subjects"] for r in rows)
    tot_pass = sum(per_inst[r["institution_id"]]["passes"] for r in rows)
    weighted = sum((r["mean_score"] or 0) * r["assessed"] for r in assessed)
    n_assessed = sum(r["assessed"] for r in assessed)
    overall = max(
        (b[0] for g, b in best.items() if g in ("primary", "secondary") and b),
        key=lambda x: (x["average"], x["attendance_rate"]),
        default=None,
    )
    return {
        "computed_at": dt.datetime.now(dt.UTC),
        "kpis": {
            "institutions": len(rows),
            "schools": len(schools),
            "learners": learners,
            "mean_score": round(weighted / n_assessed, 2) if n_assessed else None,
            "pass_rate": round(tot_pass / tot_sub, 4) if tot_sub else None,
            "attendance_rate": round(tot_att / tot_ses, 4) if tot_ses else None,
        },
        "league": league,
        "by_lga": lga_rows,
        "best_learners": best,
        "best_school": max(schools, key=lambda r: r["index"], default=None),
        "best_school_by_group": {g: (v[0] if v else None) for g, v in league.items()},
        "best_learner": overall,
    }


def performance() -> dict[str, Any]:
    """CMD-101/CMD-102 data for the caller's scope (cached ten minutes)."""
    ctx = context.require()
    authz.require("metric:view", ctx)
    scope = ctx.scope_ids
    key_src = f"{ctx.state_tenant_id}:{sorted(map(str, scope)) if scope is not None else 'all'}"
    key = "perf:" + hashlib.sha256(key_src.encode()).hexdigest()[:32]
    data: dict[str, Any] | None = cache.get(key)
    if data is None:
        data = _compute(ctx.state_tenant_id, scope)  # type: ignore[arg-type]
        cache.set(key, data, 600)
    if not ctx.has("learner:view"):
        data = {**data, "best_learners": {}, "best_learner": None}  # names need learner:view
    return data
