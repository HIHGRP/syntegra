"""Option lists for the forms (``web.forms``). Every list is read through the caller's scope, so a form can only
offer — and only accept — records the signed-in user may act on.

Each provider takes the request parameters (GET or POST) so a list can be narrowed, e.g. by ``institution_id``.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Mapping
from typing import Any

from syntegra.core import catalog, context

Options = list[tuple[str, str]]
Provider = Callable[[Mapping[str, Any]], Options]
LIMIT = 2000


def human(code: str) -> str:
    return code.replace("_", " ").capitalize()


def as_uuid(value: Any) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None


def naira(minor: int | None) -> str:
    return f"₦{(minor or 0) / 100:,.2f}"


# --------------------------------------------------------------------------- fixed lists
def fixed(values: list[str] | tuple[str, ...], labels: Mapping[str, str] | None = None) -> Provider:
    opts = [(v, (labels or {}).get(v) or human(v)) for v in values]
    return lambda _p: opts


def enum(name: str) -> Provider:
    return lambda _p: [(v, human(v)) for v in catalog.enum_values(name)]


def code_list(name: str) -> Provider:
    return lambda _p: [(v, human(v) if "_" in v or v.islower() else v) for v in catalog.code_list(name)]


# --------------------------------------------------------------------------- places and institutions
def institutions(_p: Mapping[str, Any]) -> Options:
    from syntegra.institutions.models import Institution

    qs = Institution.objects.in_scope().filter(status="active").order_by("name")
    return [(str(i.id), i.name) for i in qs[:LIMIT]]


def lgas(_p: Mapping[str, Any]) -> Options:
    from syntegra.governance.models import ScopeNode

    qs = ScopeNode.objects.filter(level="lga").order_by("name")
    ids = context.require().scope_ids
    if ids is not None:
        qs = qs.filter(id__in=list(ids))
    return [(str(n.id), n.name) for n in qs[:LIMIT]]


def employer_scopes(_p: Mapping[str, Any]) -> Options:
    """Employing authorities: the state, its authorities (boards) and LGAs, agencies and formations."""
    from syntegra.governance.models import ScopeNode

    qs = ScopeNode.objects.filter(level__in=("state", "authority", "lga", "agency", "formation")).order_by(
        "depth", "name"
    )
    ids = context.require().scope_ids
    if ids is not None:
        qs = qs.filter(id__in=list(ids))
    return [(str(n.id), f"{n.name} ({n.level})") for n in qs[:LIMIT]]


def periods(_p: Mapping[str, Any]) -> Options:
    from syntegra.academic.models import AcademicPeriod

    # sessions and terms are set at state (or institution) level and shared by everything below
    qs = AcademicPeriod.objects.filter(status="active").exclude(kind="billing_period")
    return [(str(p.id), f"{p.name} ({human(p.kind)})") for p in qs.order_by("-starts_on")[:200]]


def classes(_p: Mapping[str, Any]) -> Options:
    from syntegra.academic.models import ClassGroup
    from syntegra.institutions.models import Institution

    rows = list(ClassGroup.objects.in_scope().filter(status="active").order_by("name")[:LIMIT])
    names = dict(Institution.objects.filter(id__in={c.institution_id for c in rows}).values_list("id", "name"))
    return [(str(c.id), f"{c.name} — {names.get(c.institution_id, '')}") for c in rows]


# --------------------------------------------------------------------------- certificates
def reissue_cases(_p: Mapping[str, Any]) -> Options:
    from syntegra.certificates.models import ReissueCase

    qs = ReissueCase.objects.in_scope().filter(
        status__in=("submitted", "identity_check", "in_review", "awaiting_payment")
    )
    return [(str(c.id), f"{c.case_number} — {human(c.reason)}, {c.applicant_name}") for c in qs.order_by("-id")[:500]]


# --------------------------------------------------------------------------- fee clearance
def _learner_names(ids: set[Any]) -> dict[Any, str]:
    from syntegra.learners.models import Learner

    return {
        lr.id: f"{lr.legal_given_name} {lr.legal_family_name} ({lr.global_learner_id})"
        for lr in Learner.objects.filter(id__in=ids)
    }


def open_obligations(_p: Mapping[str, Any]) -> Options:
    from syntegra.clearance.models import LearnerObligation

    rows = list(
        LearnerObligation.objects.in_scope()
        .filter(status__in=("outstanding", "payment_plan"))
        .order_by("-published_at")[:500]
    )
    who = _learner_names({o.learner_id for o in rows})
    return [
        (str(o.id), f"{who.get(o.learner_id, '?')} — {human(o.obligation_kind)} {naira(o.amount_outstanding_minor)}")
        for o in rows
    ]


def open_disputes(_p: Mapping[str, Any]) -> Options:
    from syntegra.clearance.models import LearnerObligation, ObligationDispute

    rows = list(ObligationDispute.objects.in_scope().filter(status__in=("open", "in_progress", "on_hold"))[:500])
    obs = {o.id: o for o in LearnerObligation.objects.filter(id__in={d.obligation_id for d in rows})}
    who = _learner_names({o.learner_id for o in obs.values()})
    out = []
    for d in rows:
        ob = obs.get(d.obligation_id)
        what = f"{who.get(ob.learner_id, '?')}, {human(ob.obligation_kind)}" if ob else "obligation"
        out.append((str(d.id), f"{what} — {human(d.grounds)} (raised by {human(d.raised_by_kind).lower()})"))
    return out


# --------------------------------------------------------------------------- coverage and financing
def open_gaps(_p: Mapping[str, Any]) -> Options:
    from syntegra.curriculum.models import CoverageGap
    from syntegra.institutions.models import Institution

    rows = list(CoverageGap.objects.in_scope().filter(status__in=("open", "in_progress", "escalated"))[:LIMIT])
    names = dict(Institution.objects.filter(id__in={g.institution_id for g in rows}).values_list("id", "name"))
    return [(str(g.id), f"{names.get(g.institution_id, '')} — rule {g.rule.upper()}, {g.severity}") for g in rows]


def billing_periods(_p: Mapping[str, Any]) -> Options:
    from syntegra.financing.models import BillingPeriod

    qs = BillingPeriod.objects.exclude(status__in=("reconciled", "closed")).order_by("-census_on")
    return [(str(b.id), f"{b.label} ({human(b.status).lower()})") for b in qs[:100]]


def _snapshots(*statuses: str) -> Provider:
    def provider(_p: Mapping[str, Any]) -> Options:
        from syntegra.financing.models import BillingPeriod, CensusSnapshot
        from syntegra.institutions.models import Institution

        rows = list(CensusSnapshot.objects.in_scope().filter(status__in=statuses)[:LIMIT])
        names = dict(Institution.objects.filter(id__in={s.institution_id for s in rows}).values_list("id", "name"))
        labels = dict(
            BillingPeriod.objects.filter(id__in={s.billing_period_id for s in rows}).values_list("id", "label")
        )
        return [(str(s.id), f"{names.get(s.institution_id, '')} — {labels.get(s.billing_period_id, '')}") for s in rows]

    return provider


census_awaiting = _snapshots("awaiting_confirmation")
census_frozen = _snapshots("frozen")


# --------------------------------------------------------------------------- HR
def _staff_names(ids: set[Any]) -> dict[Any, str]:
    from syntegra.people.models import Staff

    return {s.id: f"{s.given_name} {s.family_name} ({s.staff_number})" for s in Staff.objects.filter(id__in=ids)}


def staff(_p: Mapping[str, Any]) -> Options:
    from django.db.models import Q

    from syntegra.people.models import Staff, StaffPost

    ids = set(StaffPost.objects.in_scope().filter(valid_to__isnull=True).values_list("staff_id", flat=True)[:LIMIT])
    qs = Staff.objects.filter(status__in=("onboarding", "active")).order_by("family_name", "given_name")
    if context.require().scope_ids is not None:  # staff posted in scope, and new staff awaiting appointment
        qs = qs.filter(Q(id__in=ids) | Q(status="onboarding"))
    return [(str(s.id), f"{s.family_name}, {s.given_name} ({s.staff_number})") for s in qs[:LIMIT]]


def staff_posts(_p: Mapping[str, Any]) -> Options:
    from syntegra.institutions.models import Institution
    from syntegra.people.models import StaffPost

    rows = list(StaffPost.objects.in_scope().filter(valid_to__isnull=True)[:LIMIT])
    who = _staff_names({p.staff_id for p in rows})
    names = dict(Institution.objects.filter(id__in={p.institution_id for p in rows}).values_list("id", "name"))
    return sorted(
        ((str(p.id), f"{who.get(p.staff_id, '?')} — {p.job_title}, {names.get(p.institution_id, '')}") for p in rows),
        key=lambda o: o[1],
    )


def cadres(_p: Mapping[str, Any]) -> Options:
    from syntegra.hr.models import Cadre

    return [(c.code, f"{c.title} ({c.code})") for c in Cadre.objects.filter(status="active").order_by("title")]


def positions(_p: Mapping[str, Any]) -> Options:
    from syntegra.hr.models import Position
    from syntegra.institutions.models import Institution

    rows = list(Position.objects.in_scope().filter(status="approved").order_by("position_code")[:LIMIT])
    names = dict(Institution.objects.filter(id__in={p.institution_id for p in rows}).values_list("id", "name"))
    return [
        (str(p.id), f"{p.position_code} {p.title} — {names.get(p.institution_id) or 'no institution'}") for p in rows
    ]


def leave_types(_p: Mapping[str, Any]) -> Options:
    from syntegra.hr.models import LeavePolicy

    kinds = sorted(set(LeavePolicy.objects.filter(status="published").values_list("leave_type", flat=True)))
    return [(k, human(k)) for k in kinds]


def postings(_p: Mapping[str, Any]) -> Options:
    from syntegra.hr.models import StaffPosting

    rows = list(StaffPosting.objects.in_scope().filter(status__in=("submitted", "approved")).order_by("-id")[:500])
    who = _staff_names({p.staff_id for p in rows})
    return [
        (str(p.id), f"{p.order_number} — {who.get(p.staff_id, '?')}, {human(p.posting_kind).lower()} ({p.status})")
        for p in rows
    ]


def leave_requests(_p: Mapping[str, Any]) -> Options:
    from syntegra.hr.models import LeaveRequest

    rows = list(LeaveRequest.objects.in_scope().filter(status="requested").order_by("starts_on")[:500])
    who = _staff_names({r.staff_id for r in rows})
    return [
        (str(r.id), f"{who.get(r.staff_id, '?')} — {human(r.leave_type).lower()}, {r.starts_on} to {r.ends_on}")
        for r in rows
    ]


def promotion_cases(_p: Mapping[str, Any]) -> Options:
    from syntegra.hr.models import PromotionCase

    rows = list(PromotionCase.objects.in_scope().filter(status="submitted")[:500])
    who = _staff_names({c.staff_id for c in rows})
    return [
        (str(c.id), f"{who.get(c.staff_id, '?')} — {c.exercise_label}: GL {c.from_grade_level} → {c.to_grade_level}")
        for c in rows
    ]


def integrity_flags(_p: Mapping[str, Any]) -> Options:
    from syntegra.hr.models import HrIntegrityFlag

    qs = HrIntegrityFlag.objects.filter(status__in=("open", "in_progress"))
    ids = context.require().scope_ids
    if ids is not None:  # flags belong to an employing authority, not to a scope node of their own
        qs = qs.filter(employer_scope_id__in=list(ids))
    rows = list(qs[:500])
    who = _staff_names({f.staff_id for f in rows})
    return [(str(f.id), f"{who.get(f.staff_id, '?')} — {human(f.flag_kind).lower()} ({f.status})") for f in rows]


def payroll_runs(_p: Mapping[str, Any]) -> Options:
    from syntegra.people.models import PayrollRun

    rows = PayrollRun.objects.in_scope().filter(status__in=("calculated", "exceptions_review")).order_by("-pay_date")
    return [
        (str(r.id), f"{r.period_label} — net {naira(r.net_total_minor)}, pay date {r.pay_date} ({human(r.status)})")
        for r in rows[:100]
    ]


# --------------------------------------------------------------------------- regulation
def regulatory_bodies(_p: Mapping[str, Any]) -> Options:
    from syntegra.regulation import services as reg

    return sorted(((b.code, f"{b.code} — {b.name}") for b in reg.bodies().values()), key=lambda o: o[0])


def regulation_links(p: Mapping[str, Any]) -> Options:
    from syntegra.institutions.models import Institution
    from syntegra.regulation.models import InstitutionRegulation

    qs = InstitutionRegulation.objects.in_scope().filter(valid_to__isnull=True)
    if inst := as_uuid(p.get("institution_id")):
        qs = qs.filter(institution_id=inst)
    rows = list(qs.order_by("institution_id", "body_code")[:LIMIT])
    names = dict(Institution.objects.filter(id__in={r.institution_id for r in rows}).values_list("id", "name"))
    return [
        (str(r.id), f"{names.get(r.institution_id, '')} — {r.body_code}: {human(r.relationship).lower()}") for r in rows
    ]


# --------------------------------------------------------------------------- security agencies' training
def security_courses(_p: Mapping[str, Any]) -> Options:
    from syntegra.institutions.models import Institution
    from syntegra.security_training.models import SecurityCourse

    rows = list(SecurityCourse.objects.in_scope().filter(status__in=("approved", "published"))[:LIMIT])
    names = {i.id: i.short_name or i.name for i in Institution.objects.filter(id__in={c.institution_id for c in rows})}
    return sorted(((str(c.id), f"{names.get(c.institution_id, '')} — {c.title} ({c.code})") for c in rows), key=_second)


def security_intakes(_p: Mapping[str, Any]) -> Options:
    from syntegra.security_training.models import SecurityCourse, SecurityCourseIntake

    rows = list(SecurityCourseIntake.objects.in_scope().filter(status__in=("planned", "in_progress"))[:LIMIT])
    titles = dict(SecurityCourse.objects.filter(id__in={t.course_id for t in rows}).values_list("id", "title"))
    return [(str(t.id), f"{t.name} ({t.intake_code}) — {titles.get(t.course_id, '')}") for t in rows]


def trainees_in_training(_p: Mapping[str, Any]) -> Options:
    from syntegra.security_training.models import SecurityCourseIntake, TraineeRecord

    rows = list(TraineeRecord.objects.in_scope().filter(outcome="in_training")[:LIMIT])
    who = _learner_names({r.learner_id for r in rows})
    intakes = dict(SecurityCourseIntake.objects.filter(id__in={r.intake_id for r in rows}).values_list("id", "name"))
    return sorted(
        ((str(r.id), f"{who.get(r.learner_id, '?')} — {intakes.get(r.intake_id, '')}") for r in rows), key=_second
    )


def _second(o: tuple[str, str]) -> str:
    return o[1]


# --------------------------------------------------------------------------- budgets, funding and facilities (CR-006)
def _inst_names(ids: set[Any]) -> dict[Any, str]:
    from syntegra.institutions.models import Institution

    return dict(Institution.objects.filter(id__in=ids).values_list("id", "name"))


def _node_names(nodes: set[Any]) -> dict[Any, str]:
    from syntegra.institutions.models import Institution

    return dict(Institution.objects.filter(scope_node_id__in=nodes).values_list("scope_node_id", "name"))


def cost_centres(p: Mapping[str, Any]) -> Options:
    from syntegra.finance.models import CostCentre

    qs = CostCentre.objects.in_scope().filter(status="active").order_by("institution_id", "code")
    if (iid := as_uuid(p.get("institution_id"))) is not None:
        qs = qs.filter(institution_id=iid)
    rows = list(qs[:LIMIT])
    names = _inst_names({c.institution_id for c in rows})
    return [(str(c.id), f"{c.code} {c.name} — {names.get(c.institution_id, '')}") for c in rows]


def draft_budgets(_p: Mapping[str, Any]) -> Options:
    from syntegra.finance.models import Budget

    rows = list(Budget.objects.in_scope().filter(status="draft").order_by("-fiscal_year", "-version")[:500])
    names = _node_names({b.scope_node_id for b in rows})
    return [(str(b.id), f"{names.get(b.scope_node_id, '?')} — {b.fiscal_year} version {b.version}") for b in rows]


def budget_lines(_p: Mapping[str, Any]) -> Options:
    from syntegra.finance.budgets import available
    from syntegra.finance.models import Budget, BudgetLine, CostCentre

    budgets = list(Budget.objects.in_scope().filter(status="approved").values_list("id", flat=True)[:500])
    lines = list(BudgetLine.objects.filter(budget_id__in=budgets).order_by("economic_code")[:LIMIT])
    centres = {c.id: c for c in CostCentre.objects.filter(id__in={ln.cost_centre_id for ln in lines})}
    names = _inst_names({c.institution_id for c in centres.values()})
    out = []
    for ln in lines:
        cc = centres[ln.cost_centre_id]
        label = f"{names.get(cc.institution_id, '')} · {cc.code} · {ln.economic_code} {ln.description or ''}".strip()
        out.append((str(ln.id), f"{label} (available {naira(available(ln))})"))
    return sorted(out, key=lambda o: o[1])


def open_commitments(_p: Mapping[str, Any]) -> Options:
    from syntegra.finance.models import BudgetCommitment

    rows = BudgetCommitment.objects.in_scope().filter(status__in=("open", "partly_spent")).order_by("-created_at")
    return [
        (str(c.id), f"{c.description} — {naira(c.amount_minor - c.spent_minor - c.released_minor)} open")
        for c in rows[:LIMIT]
    ]


def submitted_virements(_p: Mapping[str, Any]) -> Options:
    from syntegra.finance.models import BudgetVirement

    rows = BudgetVirement.objects.in_scope().filter(status="submitted").order_by("-created_at")
    return [(str(v.id), f"{v.virement_number} — {naira(v.amount_minor)}: {v.reason[:60]}") for v in rows[:500]]


def _imprest(*statuses: str) -> Provider:
    def provider(_p: Mapping[str, Any]) -> Options:
        from syntegra.finance.models import Imprest

        rows = Imprest.objects.in_scope().filter(status__in=statuses).order_by("-created_at")
        return [(str(i.id), f"{i.imprest_number} — {naira(i.amount_minor)}: {i.purpose[:60]}") for i in rows[:500]]

    return provider


requested_imprest = _imprest("requested")
issued_imprest = _imprest("issued", "partly_retired", "overdue")


def funding_programmes(_p: Mapping[str, Any]) -> Options:
    from syntegra.funding.models import FundingProgramme

    rows = FundingProgramme.objects.filter(status="published").order_by("beneficiary_kind", "name")
    return [(str(p.id), f"{p.name} — for {p.beneficiary_kind}s ({p.instrument.replace('_', ' ')})") for p in rows]


def _applications(*statuses: str) -> Provider:
    def provider(_p: Mapping[str, Any]) -> Options:
        from syntegra.funding.models import FundingApplication

        rows = FundingApplication.objects.in_scope().filter(status__in=statuses).order_by("-created_at")[:500]
        return [
            (str(a.id), f"{a.application_number} — {a.applicant_kind} — {naira(a.amount_requested_minor)}")
            for a in rows
        ]

    return provider


applications_to_review = _applications("submitted", "under_review")
applications_to_decide = _applications("recommended", "submitted", "under_review")
applications_approved = _applications("approved")


def funding_agreements(_p: Mapping[str, Any]) -> Options:
    from syntegra.funding.models import FundingAgreement

    rows = FundingAgreement.objects.in_scope().exclude(status__in=("settled", "completed", "written_off", "cancelled"))
    return [
        (str(a.id), f"{a.agreement_number} — {a.instrument.replace('_', ' ')} — {naira(a.outstanding_minor)} owed")
        for a in rows.order_by("-signed_on")[:LIMIT]
    ]


def buildings(p: Mapping[str, Any]) -> Options:
    from syntegra.operations.models import Building

    rows = list(Building.objects.in_scope().filter(status="active").order_by("name")[:LIMIT])
    names = _node_names({b.scope_node_id for b in rows})
    return sorted(((str(b.id), f"{names.get(b.scope_node_id, '?')} — {b.name}") for b in rows), key=lambda o: o[1])


def rooms(_p: Mapping[str, Any]) -> Options:
    from syntegra.operations.models import Room

    rows = list(Room.objects.in_scope().filter(status="active").order_by("code")[:LIMIT])
    names = _node_names({r.scope_node_id for r in rows})
    return sorted(
        ((str(r.id), f"{names.get(r.scope_node_id, '?')} — {r.code} {r.name or human(r.room_type)}") for r in rows),
        key=lambda o: o[1],
    )


def facilities(_p: Mapping[str, Any]) -> Options:
    """Every site, building, room and item of equipment in scope, as ``kind:id``."""
    from syntegra.estate.models import PropertySite
    from syntegra.operations.models import Asset, Building, Room

    def label(kind: str, x: Any) -> str:
        if kind == "site":
            return f"Site {x.site_code} {x.name}"
        if kind == "building":
            return f"Building: {x.name}"
        if kind == "room":
            return f"Room {x.code} {x.name or human(x.room_type)}"
        return f"Equipment {x.asset_tag} {x.name}"

    out: Options = []
    for kind, model in (("site", PropertySite), ("building", Building), ("room", Room), ("asset", Asset)):
        rows = list(model.objects.in_scope()[:LIMIT])
        names = _node_names({x.scope_node_id for x in rows})
        out.extend((f"{kind}:{x.id}", f"{names.get(x.scope_node_id, '?')} — {label(kind, x)}") for x in rows)
    return sorted(out, key=lambda o: o[1])


def maintenance_schedules(_p: Mapping[str, Any]) -> Options:
    from syntegra.estate.models import MaintenanceSchedule

    rows = list(MaintenanceSchedule.objects.in_scope().filter(status="active").order_by("next_due_on")[:LIMIT])
    names = _node_names({s.scope_node_id for s in rows})
    return [(str(s.id), f"{names.get(s.scope_node_id, '?')} — {s.task} (due {s.next_due_on:%d %b %Y})") for s in rows]


def open_facility_actions(_p: Mapping[str, Any]) -> Options:
    from syntegra.estate.models import FacilityAction

    rows = FacilityAction.objects.in_scope().filter(status__in=("open", "acknowledged", "in_progress"))
    rows = list(rows.order_by("due_on")[:LIMIT])
    names = _inst_names({a.institution_id for a in rows})
    return [(str(a.id), f"[{a.priority}] {names.get(a.institution_id, '?')} — {a.title}") for a in rows]


# --------------------------------------------------------------------------- examinations (EXM-01, EXM-03)
def exam_series(_p: Mapping[str, Any]) -> Options:
    from syntegra.assessment.models import ExamSeries

    rows = list(ExamSeries.objects.in_scope().exclude(status="closed").order_by("-created_at")[:500])
    names = _node_names({s.scope_node_id for s in rows})
    return [(str(s.id), f"{s.name} — {names.get(s.scope_node_id, '?')}") for s in rows]


def exam_papers(_p: Mapping[str, Any]) -> Options:
    from syntegra.assessment.models import ExamPaper, ExamSeries

    series = {s.id: s for s in ExamSeries.objects.in_scope().exclude(status="closed")[:500]}
    rows = ExamPaper.objects.filter(series_id__in=list(series)).order_by("paper_code")
    return [(str(p.id), f"{p.paper_code} {p.title} — {series[p.series_id].name}") for p in rows[:LIMIT]]


def exam_paper_codes(_p: Mapping[str, Any]) -> Options:
    from syntegra.assessment.models import ExamPaper, ExamSeries

    series = list(ExamSeries.objects.in_scope().exclude(status="closed").values_list("id", flat=True)[:500])
    codes = dict(ExamPaper.objects.filter(series_id__in=series).values_list("paper_code", "title"))
    return [(c, f"{c} — {t}") for c, t in sorted(codes.items())]


def exam_halls(_p: Mapping[str, Any]) -> Options:
    """Rooms that may be examination halls, with capacity — and a warning on those assessed unsafe."""
    from syntegra.estate.services import UNSAFE_USABILITY, room_usability
    from syntegra.operations.models import Room

    rows = list(
        Room.objects.in_scope()
        .filter(status="active", capacity__gt=0)
        .exclude(room_type__in=("toilet", "store", "generator_house", "water_point", "guard_house", "kitchen_dining"))
        .order_by("code")[:LIMIT]
    )
    names = _node_names({r.scope_node_id for r in rows})
    use = room_usability([r.id for r in rows])
    out = []
    for r in rows:
        warn = f" — assessed {use[r.id].replace('_', ' ')}" if use.get(r.id) in UNSAFE_USABILITY else ""
        label = f"{r.code} {human(r.room_type)}, {r.capacity} seats{warn} — {names.get(r.scope_node_id, '?')}"
        out.append((str(r.id), label))
    return sorted(out, key=lambda o: o[1])
