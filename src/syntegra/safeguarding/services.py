"""Safeguarding (MFS SAF-01 – SAF-04): concerns, the designated safeguarding lead's caseload and cases.

Any member of staff records a welfare or safeguarding concern about a learner: what they saw or heard, when, and the
kind of concern. What they write is sealed at once with its own key (special category, vault zone) and goes to the
designated safeguarding lead (DSL); the reporter gets a receipt code and can see only their receipts afterwards — never
the concern, the case or what happened next.

The DSL sees new concerns on the caseload and opens a case from one or more of them, or adds them to the learner's
open case. A case has a reference (SG-YYYY-NNNN), a risk level set by the DSL only, a review date, and a chronology:
the concerns, actions, decisions, agency contacts, meetings and reviews, each sealed and append-only. Referrals to an
external agency (police, social welfare, health, an NGO) record the legal basis, the agency's contact and the outcome,
sealed. Closing a case needs a reason, sealed, and is signed by the DSL. The case page also shows the learner's recent
attendance and behaviour. Every opening of a case is written to the case's access log, which the case shows.

Only the DSL (``safeguarding:manage``) and users the DSL names on a case (``case_access_grant``) open cases.
"""

from __future__ import annotations

import datetime as dt
import secrets
import uuid
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings

from syntegra.core import authz, context, crypto, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.safeguarding.models import (
    CaseAccessGrant,
    CaseAccessLog,
    SafeguardingCase,
    SafeguardingConcern,
    SafeguardingEntry,
    SafeguardingReferral,
)

CATEGORIES = {
    "physical_abuse": "Physical abuse",
    "emotional_abuse": "Emotional abuse",
    "sexual_abuse": "Sexual abuse or exploitation",
    "neglect": "Neglect",
    "child_labour": "Child labour or hawking",
    "trafficking": "Trafficking",
    "early_marriage": "Early or forced marriage",
    "harmful_practice": "Harmful traditional practice",
    "domestic_violence": "Domestic violence at home",
    "online_harm": "Online harm",
    "self_harm": "Self-harm or suicidal thoughts",
    "bullying": "Serious bullying",
    "missing_education": "Missing from education",
    "other": "Other welfare concern",
}
RISK = {"low": "Low", "medium": "Medium", "high": "High", "immediate": "Immediate danger"}
ENTRY_KINDS = {
    "action": "Action",
    "decision": "Decision",
    "agency_contact": "Agency contact",
    "meeting": "Meeting",
    "review": "Review",
}
AGENCIES = (
    "Nigeria Police Force — Family Support Unit",
    "Ministry of Women Affairs and Social Development",
    "Primary health centre",
    "General hospital",
    "NAPTIP (trafficking)",
    "Sexual Assault Referral Centre",
    "Non-governmental organisation",
)
LEGAL_BASES = {
    "vital_interests": "Vital interests (the child's safety)",
    "legal_obligation": "Legal obligation (Child's Rights Law)",
    "public_task": "Public task",
    "consent": "Consent",
}
REVIEW_DAYS = 14


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.TIME_ZONE)


def _seal(text: str, kind: str) -> bytes:
    ctx = context.require()
    return crypto.seal(text, tenant_id=ctx.tenant_id, record_kind=kind)


def _unseal(blob: bytes | memoryview | None, kind: str) -> str:
    if not blob:
        return ""
    ctx = context.require()
    try:
        return crypto.unseal(bytes(blob), tenant_id=ctx.tenant_id, record_kind=kind)
    except ValueError:
        return "(erased)"


def _learner_school(learner_id: uuid.UUID) -> tuple[Any, Any]:
    """The learner and the school of their current enrolment, which must be in the user's scope."""
    from syntegra.institutions.models import Institution
    from syntegra.learners.models import Enrolment, Learner

    lr = Learner.objects.filter(pk=learner_id).first()
    if lr is None:
        raise NotFound("learner", learner_id)
    e = Enrolment.objects.filter(learner_id=lr.id, status="active").order_by("-created_at").first()
    inst = Institution.objects.filter(pk=e.institution_id).first() if e else None
    if inst is None:
        raise HardValidation("SAF-LEARNER", "The learner has no current school", "")
    authz.require_scope(inst.scope_node_id)
    return lr, inst


def record_concern(
    learner_id: uuid.UUID, category: str, what: str, occurred_at: dt.datetime | None = None
) -> dict[str, Any]:
    """Record a concern. The reporter gets a receipt only; the concern goes to the DSL."""
    ctx = context.require()
    authz.require("safeguarding:report", ctx)
    if category not in CATEGORIES:
        raise HardValidation("SAF-CATEGORY", "Choose the kind of concern", ", ".join(CATEGORIES.values()))
    text = (what or "").strip()
    if len(text) < 20:
        raise HardValidation(
            "SAF-WHAT", "Say what you saw or heard", "Write the facts in your own words — at least a sentence."
        )
    now = dt.datetime.now(_tz())
    if occurred_at is not None and occurred_at > now + dt.timedelta(minutes=5):
        raise HardValidation("SAF-WHEN", "That time has not come yet", "")
    lr, inst = _learner_school(learner_id)
    code = "SC-" + secrets.token_hex(3).upper()
    with uow.command(
        "vault", "safeguarding:report", action="record_concern", record_kind="safeguarding_concern"
    ) as cmd:
        c = cmd.add(
            SafeguardingConcern(
                scope_node_id=inst.scope_node_id,
                learner_id=lr.id,
                category=category,
                reported_by=ctx.actor_id,
                source="staff",
                body=_seal(text[:8000], "safeguarding_concern"),
                occurred_at=occurred_at,
                receipt_code=code,
            )
        )
        cmd.record_id = c.id
    return {"receipt": code, "at": now, "school": inst.name}


def my_receipts() -> list[dict[str, Any]]:
    """The concerns this user recorded — receipt, date and kind only."""
    ctx = context.require()
    authz.require("safeguarding:report", ctx)
    tz = _tz()
    return [
        {
            "receipt": c.receipt_code,
            "at": c.created_at.astimezone(tz),
            "category": CATEGORIES.get(c.category, c.category),
        }
        for c in SafeguardingConcern.objects.filter(reported_by=ctx.actor_id).order_by("-created_at")[:20]
    ]


# ------------------------------------------------------------------------------------------- the DSL's side
def _may_open(case: SafeguardingCase, ctx: context.Context) -> bool:
    if ctx.has("safeguarding:manage"):
        return True
    today = dt.date.today()
    return (
        CaseAccessGrant.objects.filter(
            case_kind="safeguarding_case", case_id=case.id, user_id=ctx.actor_id, valid_from__lte=today
        )
        .exclude(valid_to__lt=today)
        .exists()
    )


def _linked() -> dict[uuid.UUID, uuid.UUID]:
    """Concern → case, from the chronology entries that carry the concern."""
    out: dict[uuid.UUID, uuid.UUID] = {}
    for e in SafeguardingEntry.objects.filter(entry_kind="concern").only("case_id", "source_ref"):
        cid = (e.source_ref or {}).get("concern_id")
        if cid:
            out[uuid.UUID(cid)] = e.case_id
    return out


def _names(learner_ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    from syntegra.learners.models import Learner

    return {
        lr.id: f"{lr.legal_family_name}, {lr.legal_given_name}" for lr in Learner.objects.filter(id__in=learner_ids)
    }


def caseload() -> dict[str, Any]:
    """New concerns not yet on a case, open cases by risk with their review dates, and recently closed cases."""
    ctx = context.require()
    authz.require("safeguarding:manage", ctx)
    tz = _tz()
    linked = _linked()
    concerns = [c for c in SafeguardingConcern.objects.in_scope().order_by("-created_at")[:500] if c.id not in linked]
    cases = list(SafeguardingCase.objects.in_scope().order_by("-opened_at")[:500])
    names = _names({c.learner_id for c in concerns} | {c.learner_id for c in cases})
    open_by_learner = {c.learner_id: c for c in cases if c.status not in ("closed", "transferred")}
    today = dt.date.today()
    order = {"immediate": 0, "high": 1, "medium": 2, "low": 3, None: 4}
    open_cases = sorted(
        (c for c in cases if c.status not in ("closed", "transferred")),
        key=lambda c: (order.get(c.risk_level, 4), c.review_due_on or today),
    )
    return {
        "new": [
            {
                "id": c.id,
                "learner_id": c.learner_id,
                "learner": names.get(c.learner_id, "?"),
                "category": CATEGORIES.get(c.category, c.category),
                "at": c.created_at.astimezone(tz),
                "receipt": c.receipt_code,
                "open_case": open_by_learner.get(c.learner_id).id if c.learner_id in open_by_learner else None,  # type: ignore[union-attr]
            }
            for c in concerns
        ],
        "open": [
            {
                "id": c.id,
                "reference": c.case_reference,
                "learner": names.get(c.learner_id, "?"),
                "risk": RISK.get(c.risk_level or "", "Not set"),
                "risk_code": c.risk_level or "",
                "opened": c.opened_at.astimezone(tz),
                "review_due_on": c.review_due_on,
                "overdue": bool(c.review_due_on and c.review_due_on < today),
                "status": c.status,
            }
            for c in open_cases
        ],
        "closed": [
            {"id": c.id, "reference": c.case_reference, "learner": names.get(c.learner_id, "?"), "closed": c.closed_at}
            for c in cases
            if c.status == "closed"
        ][:10],
        "risks": RISK,
    }


def _reference(cmd: Any) -> str:
    year = dt.date.today().year
    n = SafeguardingCase.unscoped.using(cmd.alias).filter(case_reference__startswith=f"SG-{year}-").count() + 1
    return f"SG-{year}-{n:04d}"


def open_case(concern_id: uuid.UUID, risk_level: str) -> SafeguardingCase:
    """Open a case from a new concern (or add the concern to the learner's open case)."""
    ctx = context.require()
    authz.require("safeguarding:manage", ctx)
    if risk_level not in RISK:
        raise HardValidation("SAF-RISK", "Set the risk level", ", ".join(RISK.values()))
    c = SafeguardingConcern.objects.in_scope().filter(pk=concern_id).first()
    if c is None:
        raise NotFound("concern", concern_id)
    if concern_id in _linked():
        raise ConflictError("SAF-LINKED", "The concern is already on a case", "")
    text = _unseal(c.body, "safeguarding_concern")
    with uow.command("vault", "safeguarding:manage", action="open_case", record_kind="safeguarding_case") as cmd:
        case = (
            SafeguardingCase.unscoped.using(cmd.alias)
            .filter(learner_id=c.learner_id, tenant_id=ctx.tenant_id)
            .exclude(status__in=("closed", "transferred"))
            .first()
        )
        now = utcnow()
        if case is None:
            case = cmd.add(
                SafeguardingCase(
                    scope_node_id=c.scope_node_id,
                    case_reference=_reference(cmd),
                    learner_id=c.learner_id,
                    dsl_user_id=ctx.actor_id,
                    risk_level=risk_level,
                    opened_at=now,
                    review_due_on=dt.date.today() + dt.timedelta(days=1 if risk_level == "immediate" else REVIEW_DAYS),
                    status="open",
                )
            )
        else:
            case = cmd.lock(SafeguardingCase, case.id)
            if order(risk_level) < order(case.risk_level):
                cmd.update(case, risk_level=risk_level)
        cmd.add(
            SafeguardingEntry(
                tenant_id=ctx.tenant_id,
                case_id=case.id,
                entry_kind="concern",
                occurred_at=c.occurred_at or c.created_at,
                author_user_id=c.reported_by,
                body=_seal(f"{CATEGORIES.get(c.category, c.category)} — {text}", "safeguarding_entry"),
                source_ref={"concern_id": str(c.id), "receipt": c.receipt_code},
            )
        )
        cmd.record_id = case.id
        return case


def order(risk: str | None) -> int:
    return {"immediate": 0, "high": 1, "medium": 2, "low": 3}.get(risk or "", 4)


def _case(case_id: uuid.UUID) -> SafeguardingCase:
    ctx = context.require()
    case: SafeguardingCase | None = SafeguardingCase.objects.in_scope().filter(pk=case_id).first()
    if case is None or not _may_open(case, ctx):
        raise Forbidden("Only the designated safeguarding lead and the people named on a case can open it.")
    return case


def case_view(case_id: uuid.UUID, purpose: str = "case_work") -> dict[str, Any]:
    """The case, its chronology and referrals; the opening is written to the case's access log."""
    from syntegra.iam.models import AppUser

    ctx = context.require()
    case = _case(case_id)
    tz = _tz()
    with uow.command("vault", None, action="view_case", record_kind="safeguarding_case") as cmd:
        CaseAccessLog.unscoped.using(cmd.alias).bulk_create(
            [
                CaseAccessLog(
                    tenant_id=ctx.tenant_id,
                    case_kind="safeguarding_case",
                    case_id=case.id,
                    user_id=ctx.actor_id,
                    access="view",
                    purpose_code=purpose[:40],
                    accessed_at=utcnow(),
                    created_by=ctx.actor_id,
                )
            ]
        )
        cmd.record_id = case.id
    entries = list(SafeguardingEntry.objects.filter(case_id=case.id).order_by("occurred_at", "created_at"))
    referrals = list(SafeguardingReferral.objects.filter(case_id=case.id).order_by("referred_at"))
    log = list(
        CaseAccessLog.objects.filter(case_kind="safeguarding_case", case_id=case.id).order_by("-accessed_at")[:30]
    )
    users = dict(
        AppUser.objects.filter(
            id__in={e.author_user_id for e in entries} | {x.user_id for x in log} | {case.dsl_user_id}
        ).values_list("id", "display_name")
    )
    learner = _names({case.learner_id}).get(case.learner_id, "?")
    return {
        "case": {
            "id": case.id,
            "reference": case.case_reference,
            "learner_id": case.learner_id,
            "learner": learner,
            "risk": case.risk_level or "",
            "risk_label": RISK.get(case.risk_level or "", "Not set"),
            "opened": case.opened_at.astimezone(tz),
            "review_due_on": case.review_due_on,
            "overdue": bool(case.review_due_on and case.review_due_on < dt.date.today() and case.status != "closed"),
            "status": case.status,
            "dsl": users.get(case.dsl_user_id, "?"),
            "closed": case.closed_at.astimezone(tz) if case.closed_at else None,
            "closure_reason": _unseal(case.closure_reason, "safeguarding_case") if case.closure_reason else None,
        },
        "chronology": [
            {
                "kind": "Concern" if e.entry_kind == "concern" else ENTRY_KINDS.get(e.entry_kind, e.entry_kind),
                "is_concern": e.entry_kind == "concern",
                "at": e.occurred_at.astimezone(tz),
                "by": users.get(e.author_user_id, "Staff"),
                "text": _unseal(e.body, "safeguarding_entry"),
                "receipt": (e.source_ref or {}).get("receipt"),
            }
            for e in entries
        ],
        "referrals": [
            {
                "id": r.id,
                "agency": r.agency,
                "contact": _unseal(r.agency_contact, "safeguarding_referral"),
                "at": r.referred_at.astimezone(tz),
                "basis": LEGAL_BASES.get(r.legal_basis or "", r.legal_basis),
                "outcome": _unseal(r.outcome, "safeguarding_referral") if r.outcome else None,
                "status": r.status,
            }
            for r in referrals
        ],
        "access_log": [
            {
                "who": users.get(x.user_id, "?"),
                "at": x.accessed_at.astimezone(tz),
                "access": x.access,
                "purpose": x.purpose_code,
            }
            for x in log
        ],
        "context": _context(case.learner_id),
        "risks": RISK,
        "kinds": ENTRY_KINDS,
        "agencies": AGENCIES,
        "bases": LEGAL_BASES,
        "can_manage": ctx.has("safeguarding:manage"),
    }


def _context(learner_id: uuid.UUID) -> dict[str, Any]:
    """What the DSL may see beside the case: the last 60 days' attendance and behaviour."""
    from syntegra.attendance.domain import rates
    from syntegra.attendance.models import AttendanceMark
    from syntegra.success.models import BehaviourEvent, BehaviourType

    since = dt.date.today() - dt.timedelta(days=60)
    codes = list(
        AttendanceMark.objects.filter(learner_id=learner_id, session_date__gte=since).values_list("code", flat=True)
    )
    s = rates.summarise(codes)
    events = list(
        BehaviourEvent.objects.filter(
            learner_id=learner_id, occurred_at__date__gte=since, reversed_at__isnull=True
        ).order_by("-occurred_at")[:8]
    )
    kinds = dict(BehaviourType.objects.filter(id__in={e.behaviour_type_id for e in events}).values_list("id", "label"))
    return {
        "attendance": {"possible": s.possible, "attended": s.attended, "rate": s.rate,
                       "unauthorised": s.unauthorised_absence},
        "behaviour": [{"at": e.occurred_at.astimezone(_tz()), "label": kinds.get(e.behaviour_type_id, "?"),
                       "points": e.points} for e in events],
    }  # fmt: skip


def add_entry(case_id: uuid.UUID, kind: str, text: str, occurred_at: dt.datetime | None = None) -> SafeguardingEntry:
    ctx = context.require()
    case = _case(case_id)
    if case.status in ("closed", "transferred"):
        raise ConflictError("SAF-CLOSED", "The case is closed", "")
    if kind not in ENTRY_KINDS:
        raise HardValidation("SAF-ENTRY", "Choose the kind of entry", ", ".join(ENTRY_KINDS.values()))
    if len((text or "").strip()) < 10:
        raise HardValidation("SAF-ENTRY", "Write what was done or decided", "")
    with uow.command("vault", "safeguarding:manage", action="add_entry", record_kind="safeguarding_entry") as cmd:
        e: SafeguardingEntry = cmd.add(
            SafeguardingEntry(
                tenant_id=ctx.tenant_id,
                case_id=case.id,
                entry_kind=kind,
                occurred_at=occurred_at or utcnow(),
                author_user_id=ctx.actor_id,
                body=_seal(text.strip()[:8000], "safeguarding_entry"),
            )
        )
        if kind == "review":
            due = dt.date.today() + dt.timedelta(days=REVIEW_DAYS)
            cmd.update(cmd.lock(SafeguardingCase, case.id), review_due_on=due, status="in_progress")
        cmd.record_id = e.id
        return e


def set_risk(case_id: uuid.UUID, risk_level: str, review_due_on: dt.date | None) -> SafeguardingCase:
    case = _case(case_id)
    if risk_level not in RISK:
        raise HardValidation("SAF-RISK", "Set the risk level", ", ".join(RISK.values()))
    with uow.command("vault", "safeguarding:manage", action="set_risk", record_kind="safeguarding_case") as cmd:
        c = cmd.lock(SafeguardingCase, case.id)
        updated: SafeguardingCase = cmd.update(
            c, risk_level=risk_level, review_due_on=review_due_on or c.review_due_on, status="in_progress"
        )
        return updated


def refer(case_id: uuid.UUID, agency: str, contact: str, legal_basis: str) -> SafeguardingReferral:
    ctx = context.require()
    case = _case(case_id)
    if case.status in ("closed", "transferred"):
        raise ConflictError("SAF-CLOSED", "The case is closed", "")
    agency = " ".join((agency or "").split())
    if len(agency) < 3:
        raise HardValidation("SAF-AGENCY", "Name the agency", "")
    if legal_basis not in LEGAL_BASES:
        raise HardValidation("SAF-BASIS", "Choose the legal basis for sharing", ", ".join(LEGAL_BASES.values()))
    with uow.command("vault", "safeguarding:manage", action="refer", record_kind="safeguarding_referral") as cmd:
        r: SafeguardingReferral = cmd.add(
            SafeguardingReferral(
                case_id=case.id,
                agency=agency[:200],
                agency_contact=_seal(contact.strip(), "safeguarding_referral") if (contact or "").strip() else None,
                referred_at=utcnow(),
                legal_basis=legal_basis,
                status="sent",
            )
        )
        cmd.add(
            SafeguardingEntry(
                tenant_id=ctx.tenant_id,
                case_id=case.id,
                entry_kind="agency_contact",
                occurred_at=utcnow(),
                author_user_id=ctx.actor_id,
                body=_seal(f"Referred to {agency} ({LEGAL_BASES[legal_basis]}).", "safeguarding_entry"),
            )
        )
        cmd.record_id = r.id
        return r


def record_outcome(referral_id: uuid.UUID, status: str, outcome: str) -> SafeguardingReferral:
    if status not in ("acknowledged", "accepted", "declined"):
        raise HardValidation("SAF-OUTCOME", "Choose acknowledged, accepted or declined", "")
    r0 = SafeguardingReferral.objects.filter(pk=referral_id).first()
    if r0 is None:
        raise NotFound("referral", referral_id)
    _case(r0.case_id)
    with uow.command(
        "vault", "safeguarding:manage", action="referral_outcome", record_kind="safeguarding_referral"
    ) as cmd:
        r = cmd.lock(SafeguardingReferral, referral_id)
        updated: SafeguardingReferral = cmd.update(
            r, status=status, outcome=_seal(outcome.strip(), "safeguarding_referral") if outcome.strip() else r.outcome
        )
        return updated


def close(case_id: uuid.UUID, reason: str) -> SafeguardingCase:
    ctx = context.require()
    case = _case(case_id)
    if case.status in ("closed", "transferred"):
        raise ConflictError("SAF-CLOSED", "The case is already closed", "")
    if len((reason or "").strip()) < 20:
        raise HardValidation("SAF-CLOSE", "Give the reason for closing", "Say why the child is now safe or supported.")
    pending = SafeguardingReferral.objects.filter(case_id=case.id, status__in=("drafted", "sent")).count()
    if pending:
        raise ConflictError(
            "SAF-REFERRALS", "Referrals are still waiting", f"{pending} referral(s) have no outcome yet."
        )
    with uow.command("vault", "safeguarding:manage", action="close_case", record_kind="safeguarding_case") as cmd:
        c = cmd.lock(SafeguardingCase, case.id)
        closed: SafeguardingCase = cmd.update(
            c,
            status="closed",
            closed_at=utcnow(),
            closed_signed_by=ctx.actor_id,
            closure_reason=_seal(reason.strip(), "safeguarding_case"),
        )
        return closed
