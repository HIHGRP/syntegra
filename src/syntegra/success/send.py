"""Special educational needs (MFS SEN-01 – SEN-03): the register, support profiles, plans and what teachers see.

The special educational needs coordinator (SENCO, ``send:*``) keeps the school's register: each learner with their
level of support (monitoring, school support, specialist support, a statutory plan), their areas of need with the
primary one marked, and a support profile — strengths, needs, how they communicate best, what helps them learn, and
the learner's and parents' own words. The profile and any detail of a need are sealed (special category, vault
zone); every opening of a profile is written to its access log.

A support plan (an individual education or support plan, or a statutory plan) sets the outcomes to work towards, who
takes part, and how often it is reviewed. A new version supersedes the last. Each review records what was found and
moves the next review on by the plan's cycle; a plan past its review date is flagged on the register.

What teachers need in class is kept apart from the diagnosis: adjustments (extra time, seating, large print, a reader,
rest breaks, visual supports, assistive technology) and individual teaching strategies, authorised by the SENCO with
a short note for the teacher (``adjustment``, confidential). A teacher sees these — and only these — for the learners
of the classes they teach, on their lesson page; the seating plan and examination access arrangements use them too.
"""

from __future__ import annotations

import calendar
import datetime as dt
import json
import uuid
from typing import Any

from syntegra.academic.models import ClassGroup, ClassMembership
from syntegra.core import authz, context, crypto, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.safeguarding.models import CaseAccessLog
from syntegra.success.models import Adjustment, SendNeed, SendProfile, SupportPlan, SupportPlanReview

NEED_AREAS = {
    "cognition_learning": "Cognition and learning",
    "specific_learning": "Specific learning difficulty (e.g. dyslexia, dyscalculia)",
    "communication": "Speech, language and communication",
    "autism": "Autism",
    "semh": "Social, emotional and mental health",
    "visual": "Visual impairment",
    "hearing": "Hearing impairment",
    "physical": "Physical disability",
    "medical": "Medical condition affecting learning",
}
SUPPORT_LEVELS = {
    "monitoring": "Monitoring",
    "school_support": "School support",
    "specialist_support": "Specialist support",
    "statutory_plan": "Statutory plan",
}
PLAN_TYPES = {
    "iep": "Individual education plan",
    "isp": "Individual support plan",
    "statutory": "Statutory plan",
}
ADJUSTMENTS = {
    "strategy": "Teaching strategy",
    "seating": "Seating position",
    "extra_time": "Extra time",
    "large_print": "Large print",
    "read_aloud": "Reader / read aloud",
    "scribe": "Scribe",
    "rest_breaks": "Rest breaks",
    "visual_supports": "Visual supports",
    "assistive_technology": "Assistive technology",
}
PROFILE_FIELDS = (
    ("strengths", "Strengths and interests"),
    ("needs", "What the learner finds difficult"),
    ("communication", "How they communicate best"),
    ("helps", "What helps them learn"),
    ("learner_voice", "In the learner's own words"),
    ("parent_voice", "What parents or carers say"),
)


def _seal(text: str, kind: str) -> bytes:
    return crypto.seal(text, tenant_id=context.require().tenant_id, record_kind=kind)


def _unseal(blob: bytes | memoryview | None, kind: str) -> str:
    if not blob:
        return ""
    try:
        return crypto.unseal(bytes(blob), tenant_id=context.require().tenant_id, record_kind=kind)
    except ValueError:
        return "(erased)"


def _learner_class(learner_id: uuid.UUID, on: dt.date) -> ClassGroup | None:
    m = (
        ClassMembership.objects.filter(learner_id=learner_id, valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .order_by("-valid_from")
        .first()
    )
    if m is None:
        return None
    cls: ClassGroup | None = ClassGroup.objects.filter(pk=m.class_group_id).first()
    return cls


def _schools() -> list[Any]:
    from syntegra.institutions.models import Institution

    ctx = context.require()
    qs = Institution.objects.filter(status="active")
    if ctx.scope_ids is not None:
        qs = qs.filter(scope_node_id__in=list(ctx.scope_ids))
    return list(qs.order_by("name")[:200])


def register(institution_id: uuid.UUID) -> dict[str, Any]:
    """The school's register: who is on it, at what level, their primary need, plan and review dates."""
    from syntegra.institutions.models import Institution
    from syntegra.learners.models import Learner

    ctx = context.require()
    authz.require("send:view", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    today = dt.date.today()
    profiles = list(SendProfile.objects.filter(scope_node_id=inst.scope_node_id, status="active"))
    needs: dict[uuid.UUID, list[SendNeed]] = {}
    for n in SendNeed.objects.filter(profile_id__in=[p.id for p in profiles], valid_from__lte=today).exclude(
        valid_to__lt=today
    ):
        needs.setdefault(n.profile_id, []).append(n)
    plans = {}
    for pl in SupportPlan.objects.filter(profile_id__in=[p.id for p in profiles], status="published"):
        plans[pl.profile_id] = pl
    people = {lr.id: lr for lr in Learner.objects.filter(id__in=[p.learner_id for p in profiles])}
    adjust: dict[uuid.UUID, int] = {}
    for lid in (
        Adjustment.objects.filter(learner_id__in=list(people), valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .values_list("learner_id", flat=True)
    ):
        adjust[lid] = adjust.get(lid, 0) + 1
    rows = []
    for p in profiles:
        lr = people.get(p.learner_id)
        cls = _learner_class(p.learner_id, today)
        ns = needs.get(p.id, [])
        primary = next((n for n in ns if n.is_primary), ns[0] if ns else None)
        plan = plans.get(p.id)
        dates = [d for d in (p.review_due_on, plan.next_review_on if plan else None) if d]
        due = min(dates) if dates else None
        rows.append(
            {
                "profile_id": p.id,
                "learner_id": p.learner_id,
                "name": f"{lr.legal_family_name}, {lr.legal_given_name}" if lr else "?",
                "class": cls.name if cls else "—",
                "level": SUPPORT_LEVELS.get(p.support_level, p.support_level),
                "level_code": p.support_level,
                "primary": NEED_AREAS.get(primary.need_area, primary.need_area) if primary else "—",
                "other_needs": len(ns) - (1 if primary else 0),
                "plan": PLAN_TYPES.get(plan.plan_type, plan.plan_type) if plan else None,
                "plan_version": plan.version if plan else None,
                "review": due,
                "overdue": bool(due and due < today),
                "adjustments": adjust.get(p.learner_id, 0),
            }
        )
    rows.sort(key=lambda r: (r["class"], r["name"]))
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["level_code"]] = counts.get(r["level_code"], 0) + 1
    areas: dict[str, int] = {}
    for ns in needs.values():
        for n in ns:
            if n.is_primary:
                areas[n.need_area] = areas.get(n.need_area, 0) + 1
    return {
        "institution": {"id": inst.id, "name": inst.name},
        "rows": rows,
        "levels": [{"code": k, "label": v, "count": counts.get(k, 0)} for k, v in SUPPORT_LEVELS.items()],
        "areas": sorted(
            ({"label": NEED_AREAS.get(k, k), "count": v} for k, v in areas.items()), key=lambda x: -x["count"]
        ),
        "overdue": sum(1 for r in rows if r["overdue"]),
        "schools": _schools(),
        "need_areas": NEED_AREAS,
        "support_levels": SUPPORT_LEVELS,
        "profile_fields": PROFILE_FIELDS,
        "can_manage": ctx.has("send:manage"),
    }


def _school_learner(learner_id: uuid.UUID) -> tuple[Any, Any]:
    from syntegra.institutions.models import Institution
    from syntegra.learners.models import Enrolment, Learner

    lr = Learner.objects.filter(pk=learner_id).first()
    if lr is None:
        raise NotFound("learner", learner_id)
    e = Enrolment.objects.filter(learner_id=lr.id, status="active").order_by("-created_at").first()
    inst = Institution.objects.filter(pk=e.institution_id).first() if e else None
    if inst is None:
        raise HardValidation("SEN-LEARNER", "The learner has no current school", "")
    authz.require_scope(inst.scope_node_id)
    return lr, inst


def add(
    learner_id: uuid.UUID,
    support_level: str,
    need_areas: list[str],
    primary: str,
    profile: dict[str, str],
    review_due_on: dt.date | None = None,
) -> SendProfile:
    """Put a learner on the register with their level of support, needs and profile."""
    ctx = context.require()
    authz.require("send:manage", ctx)
    if support_level not in SUPPORT_LEVELS:
        raise HardValidation("SEN-LEVEL", "Choose the level of support", ", ".join(SUPPORT_LEVELS.values()))
    areas = [a for a in dict.fromkeys(need_areas) if a]
    if not areas or any(a not in NEED_AREAS for a in areas):
        raise HardValidation("SEN-NEEDS", "Choose at least one area of need", "")
    if primary not in areas:
        primary = areas[0]
    text = {k: " ".join((profile.get(k) or "").split())[:2000] for k, _label in PROFILE_FIELDS}
    if not text["needs"] or not text["helps"]:
        raise HardValidation(
            "SEN-PROFILE", "Describe the needs and what helps", "Both are needed for the profile to be useful."
        )
    lr, inst = _school_learner(learner_id)
    if SendProfile.objects.filter(learner_id=lr.id, status="active").exists():
        raise ConflictError("SEN-EXISTS", "Already on the register", "Open the learner's profile to change it.")
    today = dt.date.today()
    with uow.command("vault", "send:manage", action="add_to_register", record_kind="send_profile") as cmd:
        p = cmd.add(
            SendProfile(
                scope_node_id=inst.scope_node_id,
                learner_id=lr.id,
                support_level=support_level,
                plan_type=None,
                profile=_seal(json.dumps(text), "send_profile"),
                senco_user_id=ctx.actor_id,
                review_due_on=review_due_on or today + dt.timedelta(days=90),
                status="active",
            )
        )
        for a in areas:
            cmd.add(SendNeed(profile_id=p.id, need_area=a, is_primary=a == primary, valid_from=today))
        cmd.record_id = p.id
        return p


def _profile(profile_id: uuid.UUID) -> SendProfile:
    p: SendProfile | None = SendProfile.objects.in_scope().filter(pk=profile_id).first()
    if p is None:
        raise NotFound("support profile", profile_id)
    return p


def profile_for(learner_id: uuid.UUID) -> SendProfile | None:
    p: SendProfile | None = SendProfile.objects.in_scope().filter(learner_id=learner_id, status="active").first()
    return p


def profile_view(profile_id: uuid.UUID) -> dict[str, Any]:
    """The learner's support profile, needs, plans, reviews and adjustments; the opening is logged."""
    from syntegra.iam.models import AppUser

    ctx = context.require()
    authz.require("send:view", ctx)
    p = _profile(profile_id)
    lr, inst = _school_learner(p.learner_id)
    with uow.command("vault", None, action="view_send_profile", record_kind="send_profile") as cmd:
        CaseAccessLog.unscoped.using(cmd.alias).bulk_create(
            [CaseAccessLog(tenant_id=ctx.tenant_id, case_kind="send_profile", case_id=p.id, user_id=ctx.actor_id,
                           access="view", purpose_code="send_support", accessed_at=utcnow(), created_by=ctx.actor_id)]
        )  # fmt: skip
        cmd.record_id = p.id
    today = dt.date.today()
    try:
        prof = json.loads(_unseal(p.profile, "send_profile") or "{}")
    except ValueError:
        prof = {}
    needs = list(SendNeed.objects.filter(profile_id=p.id).exclude(valid_to__lt=today).order_by("-is_primary"))
    plans = list(SupportPlan.objects.filter(profile_id=p.id).order_by("-version"))
    reviews = list(SupportPlanReview.objects.filter(plan_id__in=[x.id for x in plans]).order_by("-reviewed_on"))
    adjustments = list(
        Adjustment.objects.filter(learner_id=p.learner_id, valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .order_by("adjustment_kind")
    )
    log = list(CaseAccessLog.objects.filter(case_kind="send_profile", case_id=p.id).order_by("-accessed_at")[:15])
    users = dict(AppUser.objects.filter(id__in={x.user_id for x in log}).values_list("id", "display_name"))
    cls = _learner_class(p.learner_id, today)
    current = next((x for x in plans if x.status == "published"), None)
    return {
        "profile": {
            "id": p.id,
            "learner_id": p.learner_id,
            "name": f"{lr.legal_given_name} {lr.legal_family_name}",
            "class": cls.name if cls else "—",
            "school": inst.name,
            "level": SUPPORT_LEVELS.get(p.support_level, p.support_level),
            "level_code": p.support_level,
            "review_due_on": p.review_due_on,
            "overdue": bool(p.review_due_on and p.review_due_on < today),
            "fields": [{"key": k, "label": label, "text": prof.get(k, "")} for k, label in PROFILE_FIELDS],
        },
        "needs": [
            {"area": NEED_AREAS.get(n.need_area, n.need_area), "primary": n.is_primary, "since": n.valid_from}
            for n in needs
        ],
        "plan": _plan_row(current) if current else None,
        "plans": [_plan_row(x) for x in plans],
        "reviews": [
            {
                "on": r.reviewed_on,
                "notes": _unseal(r.notes, "support_plan_review"),
                "attendees": r.attendees or [],
                "version": next((x.version for x in plans if x.id == r.plan_id), None),
            }
            for r in reviews
        ],
        "adjustments": [_adjustment_row(a) for a in adjustments],
        "access_log": [{"who": users.get(x.user_id, "?"), "at": x.accessed_at} for x in log],
        "plan_types": PLAN_TYPES,
        "adjustment_kinds": ADJUSTMENTS,
        "support_levels": SUPPORT_LEVELS,
        "can_manage": ctx.has("send:manage"),
    }


def _plan_row(x: SupportPlan) -> dict[str, Any]:
    try:
        outcomes = json.loads(_unseal(x.outcomes, "support_plan") or "[]")
    except ValueError:
        outcomes = []
    return {
        "id": x.id,
        "type": PLAN_TYPES.get(x.plan_type, x.plan_type),
        "version": x.version,
        "outcomes": outcomes,
        "participants": x.participants or [],
        "cycle": x.review_cycle_months,
        "next_review_on": x.next_review_on,
        "overdue": x.status == "published" and x.next_review_on < dt.date.today(),
        "status": x.status,
    }


def _adjustment_row(a: Adjustment) -> dict[str, Any]:
    return {
        "id": a.id,
        "kind": ADJUSTMENTS.get(a.adjustment_kind, a.adjustment_kind.replace("_", " ").capitalize()),
        "note": (a.parameters or {}).get("note", ""),
        "applies_to": ", ".join(a.applies_to or []),
        "since": a.valid_from,
        "until": a.valid_to,
    }


def update_profile(
    profile_id: uuid.UUID, support_level: str, profile: dict[str, str], review_due_on: dt.date | None
) -> SendProfile:
    if support_level not in SUPPORT_LEVELS:
        raise HardValidation("SEN-LEVEL", "Choose the level of support", ", ".join(SUPPORT_LEVELS.values()))
    p0 = _profile(profile_id)
    text = {k: " ".join((profile.get(k) or "").split())[:2000] for k, _label in PROFILE_FIELDS}
    with uow.command("vault", "send:manage", action="update_send_profile", record_kind="send_profile") as cmd:
        p = cmd.lock(SendProfile, p0.id)
        updated: SendProfile = cmd.update(
            p,
            support_level=support_level,
            profile=_seal(json.dumps(text), "send_profile"),
            review_due_on=review_due_on or p.review_due_on,
        )
        return updated


def new_plan(
    profile_id: uuid.UUID, plan_type: str, outcomes: list[str], participants: list[str], cycle_months: int
) -> SupportPlan:
    """A new version of the learner's support plan; the previous published version is superseded."""
    if plan_type not in PLAN_TYPES:
        raise HardValidation("SEN-PLAN", "Choose the kind of plan", ", ".join(PLAN_TYPES.values()))
    goals = [" ".join(o.split())[:500] for o in outcomes if o and o.strip()]
    if not goals:
        raise HardValidation("SEN-OUTCOMES", "Set at least one outcome", "e.g. Reads a short passage aloud fluently")
    if not 1 <= cycle_months <= 12:
        raise HardValidation("SEN-CYCLE", "Review every 1 to 12 months", "")
    p = _profile(profile_id)
    with uow.command("vault", "send:manage", action="new_support_plan", record_kind="support_plan") as cmd:
        prior = list(SupportPlan.unscoped.using(cmd.alias).filter(profile_id=p.id).order_by("-version"))
        for old in prior:
            if old.status == "published":
                cmd.update(old, status="superseded")
        plan: SupportPlan = cmd.add(
            SupportPlan(
                profile_id=p.id,
                plan_type=plan_type,
                version=(prior[0].version + 1) if prior else 1,
                outcomes=_seal(json.dumps(goals), "support_plan"),
                participants=[x.strip()[:120] for x in participants if x.strip()] or None,
                review_cycle_months=cycle_months,
                next_review_on=_add_months(dt.date.today(), cycle_months),
                status="published",
            )
        )
        cmd.update(cmd.lock(SendProfile, p.id), plan_type=plan_type)
        cmd.record_id = plan.id
        return plan


def _add_months(d: dt.date, months: int) -> dt.date:
    m = d.month - 1 + months
    y, m = d.year + m // 12, m % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def review_plan(plan_id: uuid.UUID, notes: str, attendees: list[str]) -> SupportPlanReview:
    """Record a review of the current plan; the next review moves on by the plan's cycle."""
    x = SupportPlan.objects.filter(pk=plan_id).first()
    if x is None:
        raise NotFound("support plan", plan_id)
    _profile(x.profile_id)
    if x.status != "published":
        raise ConflictError("SEN-PLAN-OLD", "Only the current plan is reviewed", "")
    if len((notes or "").strip()) < 20:
        raise HardValidation("SEN-REVIEW", "Write what the review found", "Progress against each outcome, and changes.")
    today = dt.date.today()
    with uow.command("vault", "send:manage", action="review_support_plan", record_kind="support_plan_review") as cmd:
        r: SupportPlanReview = cmd.add(
            SupportPlanReview(
                plan_id=x.id,
                reviewed_on=today,
                notes=_seal(notes.strip()[:6000], "support_plan_review"),
                attendees=[a.strip()[:120] for a in attendees if a.strip()] or None,
            )
        )
        cmd.update(cmd.lock(SupportPlan, x.id), next_review_on=_add_months(today, x.review_cycle_months))
        cmd.record_id = r.id
        return r


def add_adjustment(
    learner_id: uuid.UUID, kind: str, note: str, applies_to: list[str], valid_to: dt.date | None = None
) -> Adjustment:
    """An adjustment or teaching strategy for the learner's teachers, with a short note (no diagnosis)."""
    ctx = context.require()
    authz.require("send:manage", ctx)
    if kind not in ADJUSTMENTS:
        raise HardValidation("SEN-ADJUSTMENT", "Choose the kind of adjustment", ", ".join(ADJUSTMENTS.values()))
    note = " ".join((note or "").split())[:300]
    if len(note) < 5:
        raise HardValidation("SEN-NOTE", "Tell teachers what to do", "e.g. Give instructions one step at a time")
    places = [a for a in applies_to if a in ("lessons", "assessments", "exams", "lms", "rooms")] or ["lessons"]
    _school_learner(learner_id)
    with uow.command("ops", "send:manage", action="add_adjustment", record_kind="adjustment") as cmd:
        a: Adjustment = cmd.add(
            Adjustment(
                learner_id=learner_id,
                adjustment_kind=kind,
                parameters={"note": note},
                applies_to=places,
                authorised_by=ctx.actor_id,
                valid_from=dt.date.today(),
                valid_to=valid_to,
            )
        )
        cmd.record_id = a.id
        return a


def end_adjustment(adjustment_id: uuid.UUID) -> Adjustment:
    with uow.command("ops", "send:manage", action="end_adjustment", record_kind="adjustment") as cmd:
        a = cmd.lock(Adjustment, adjustment_id)
        _school_learner(a.learner_id)
        updated: Adjustment = cmd.update(a, valid_to=dt.date.today() - dt.timedelta(days=1))
        return updated


def for_class(class_id: uuid.UUID) -> list[dict[str, Any]]:
    """For a class's teachers: each learner's adjustments and teaching strategies — never the needs behind them."""
    from syntegra.academic.models import ClassSubjectPlan, TeachingAssignment
    from syntegra.academic.teaching import current
    from syntegra.curriculum.lessons import my_staff_id
    from syntegra.learners.models import Learner

    ctx = context.require()
    authz.require("class:view", ctx)
    cls = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    if cls is None:
        raise NotFound("class", class_id)
    today = dt.date.today()
    if not (ctx.has("class:manage") or ctx.has("send:view")):
        mine = my_staff_id(ctx)
        plans = ClassSubjectPlan.objects.filter(class_group_id=cls.id).values_list("id", flat=True)
        teaches = mine is not None and (
            cls.form_teacher_staff_id == mine
            or current(
                TeachingAssignment.objects.filter(class_subject_plan_id__in=list(plans), staff_id=mine), today
            ).exists()
        )
        if not teaches:
            raise Forbidden("Only the class's teachers see its learners' adjustments.")
    ids = list(
        ClassMembership.objects.filter(class_group_id=cls.id, valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .values_list("learner_id", flat=True)
    )
    adj: dict[uuid.UUID, list[Adjustment]] = {}
    for a in Adjustment.objects.filter(learner_id__in=ids, valid_from__lte=today).exclude(valid_to__lt=today):
        adj.setdefault(a.learner_id, []).append(a)
    people = {lr.id: lr for lr in Learner.objects.filter(id__in=list(adj))}
    return sorted(
        (
            {
                "name": f"{people[lid].legal_family_name}, {people[lid].legal_given_name}",
                "adjustments": [_adjustment_row(a) for a in sorted(v, key=lambda a: a.adjustment_kind != "strategy")],
            }
            for lid, v in adj.items()
            if lid in people
        ),
        key=lambda x: x["name"],
    )
