"""Behaviour (MFS BEH-01, BEH-02, BEH-101): the school's policy, logging and the overview.

The school's behaviour policy lists the positive and negative behaviours staff record, each with its points and the
outcome that normally follows. A school without one starts from the state's default policy (below), which the head
publishes. Teachers log behaviour for one or several learners of a class in one step; the points are those of the
policy in force, so a later policy never re-scores past events. Outcomes above a detention — internal exclusion,
suspension, exclusion — are decisions for the head: a teacher can propose one, and it waits for the head's decision.
Bullying names the learners it was aimed at, so the pastoral side can support them. An entry can be withdrawn on the
day by the member of staff who made it, or by the head.

The overview gives a school (or one class) its pattern over a period: points and events by category, by class and by
day of the week, the learners with the most positive and the most concerning records, the decisions waiting for the
head, and the latest entries.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings

from syntegra.academic.models import ClassGroup, ClassMembership
from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.success.models import BehaviourEvent, BehaviourPolicy, BehaviourType

# code, label, polarity, category, points, default outcome
DEFAULT_TYPES: tuple[tuple[str, str, str, str, int, str], ...] = (
    ("EXCELLENT_WORK", "Excellent work", "positive", "achievement", 2, "none"),
    ("EFFORT", "Outstanding effort", "positive", "achievement", 1, "none"),
    ("HELPING", "Helping others", "positive", "positive_conduct", 1, "none"),
    ("LEADERSHIP", "Leadership and responsibility", "positive", "positive_conduct", 2, "none"),
    ("REPRESENTING", "Representing the school", "positive", "positive_conduct", 3, "none"),
    ("LATE", "Late to school or lesson", "negative", "lateness", -1, "warning"),
    ("HOMEWORK", "Homework not done", "negative", "homework", -1, "warning"),
    ("UNIFORM", "Out of uniform", "negative", "uniform", -1, "warning"),
    ("DISRUPTION", "Disrupting learning", "negative", "disruption", -2, "warning"),
    ("DISRESPECT", "Disrespect to staff", "negative", "disrespect", -3, "detention"),
    ("TRUANCY", "Truancy (left school or missed lessons)", "negative", "truancy", -3, "parent_contact"),
    ("FIGHTING", "Fighting", "negative", "violence", -5, "parent_contact"),
    ("BULLYING", "Bullying", "negative", "bullying", -5, "parent_contact"),
    ("MALPRACTICE", "Examination malpractice", "negative", "malpractice", -5, "suspension"),
)  # fmt: skip
OUTCOMES = {
    "none": "No further action",
    "warning": "Warning",
    "detention": "Detention",
    "on_report": "On report",
    "parent_contact": "Parent contacted",
    "intervention": "Intervention",
    "internal_exclusion": "Internal exclusion",
    "suspension": "Suspension",
    "exclusion": "Exclusion",
}
HEAD_DECISION = {"internal_exclusion", "suspension", "exclusion"}
CATEGORY_LABELS = {
    "achievement": "Achievement",
    "positive_conduct": "Positive conduct",
    "lateness": "Lateness",
    "homework": "Homework",
    "uniform": "Uniform",
    "disruption": "Disruption",
    "disrespect": "Disrespect",
    "truancy": "Truancy",
    "violence": "Violence",
    "bullying": "Bullying",
    "malpractice": "Malpractice",
}
BACKDATE_DAYS = 14
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.TIME_ZONE)


def _institution(institution_id: uuid.UUID) -> Any:
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def policy(institution_id: uuid.UUID) -> BehaviourPolicy | None:
    p: BehaviourPolicy | None = (
        BehaviourPolicy.objects.filter(institution_id=institution_id, status="published").order_by("-version").first()
    )
    return p


def types(institution_id: uuid.UUID) -> list[BehaviourType]:
    p = policy(institution_id)
    if p is None:
        return []
    return sorted(
        BehaviourType.objects.filter(policy_id=p.id), key=lambda t: (t.polarity != "positive", -abs(t.points))
    )


def adopt_default(institution_id: uuid.UUID) -> BehaviourPolicy:
    """Publish the state's default behaviour policy for a school that has none yet."""
    inst = _institution(institution_id)
    if policy(inst.id) is not None:
        raise ConflictError("BEH-POLICY", "The school already has a policy", "Its behaviours are listed below.")
    with uow.command("ops", "behaviour:manage", action="adopt_policy", record_kind="behaviour_policy") as cmd:
        p = cmd.add(
            BehaviourPolicy(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                framework_version=1,
                version=1,
                effective_from=dt.date.today(),
                status="published",
            )
        )
        for code, label, polarity, category, points, outcome in DEFAULT_TYPES:
            cmd.add(
                BehaviourType(
                    policy_id=p.id,
                    code=code,
                    label=label,
                    polarity=polarity,
                    category=category,
                    points=points,
                    default_outcome=outcome,
                    counts_in_reports=True,
                    counts_in_influences=True,
                )
            )
        cmd.record_id = p.id
        return p


def _members(class_id: uuid.UUID, on: dt.date) -> dict[uuid.UUID, Any]:
    from syntegra.learners.models import Learner

    ids = (
        ClassMembership.objects.filter(class_group_id=class_id, valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .values_list("learner_id", flat=True)
    )
    return {lr.id: lr for lr in Learner.objects.filter(id__in=list(ids))}


def _class(class_id: uuid.UUID) -> ClassGroup:
    cls: ClassGroup | None = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    if cls is None:
        raise NotFound("class", class_id)
    return cls


def class_list(class_id: uuid.UUID) -> dict[str, Any]:
    """What the logging form needs: the class's learners and the school's behaviours."""
    ctx = context.require()
    authz.require("behaviour:log", ctx)
    cls = _class(class_id)
    members = _members(cls.id, dt.date.today())
    kinds = types(cls.institution_id)
    return {
        "class": {"id": cls.id, "name": cls.name, "institution_id": cls.institution_id},
        "learners": sorted(
            ({"id": lr.id, "name": f"{lr.legal_family_name}, {lr.legal_given_name}"} for lr in members.values()),
            key=lambda x: x["name"],
        ),
        "positive": [_type_row(t) for t in kinds if t.polarity == "positive"],
        "negative": [_type_row(t) for t in kinds if t.polarity == "negative"],
        "outcomes": OUTCOMES,
        "head_decision": sorted(HEAD_DECISION),
        "has_policy": bool(kinds),
        "can_manage": ctx.has("behaviour:manage"),
        "classes": [
            {"id": c.id, "name": c.name}
            for c in ClassGroup.objects.in_scope()
            .filter(institution_id=cls.institution_id, status="active")
            .order_by("name")
        ],
    }


def _type_row(t: BehaviourType) -> dict[str, Any]:
    return {"id": t.id, "label": t.label, "points": t.points, "category": t.category, "outcome": t.default_outcome}


def log(
    class_id: uuid.UUID,
    learner_ids: list[uuid.UUID],
    type_id: uuid.UUID,
    *,
    occurred_at: dt.datetime | None = None,
    description: str | None = None,
    outcome: str | None = None,
    target_ids: list[uuid.UUID] | None = None,
    location: str | None = None,
) -> list[BehaviourEvent]:
    """Record one behaviour for one or more learners of a class."""
    from syntegra.curriculum.lessons import my_staff_id

    ctx = context.require()
    authz.require("behaviour:log", ctx)
    cls = _class(class_id)
    now = dt.datetime.now(_tz())
    occurred_at = occurred_at or now
    if occurred_at > now + dt.timedelta(minutes=5):
        raise HardValidation("BEH-TIME", "That time has not come yet", "Record behaviour after it happens.")
    if occurred_at < now - dt.timedelta(days=BACKDATE_DAYS):
        raise HardValidation("BEH-TIME", "Too long ago", f"Record behaviour within {BACKDATE_DAYS} days.")
    members = _members(cls.id, occurred_at.date())
    chosen = list(dict.fromkeys(learner_ids))
    if not chosen:
        raise HardValidation("BEH-LEARNERS", "Choose at least one learner", "")
    if any(lid not in members for lid in chosen):
        raise HardValidation("BEH-LEARNERS", "Not a learner of this class", f"Choose learners of {cls.name}.")
    kind = next((t for t in types(cls.institution_id) if t.id == type_id), None)
    if kind is None:
        raise HardValidation("BEH-TYPE", "Choose a behaviour from the school's policy", "")
    outcome = outcome or kind.default_outcome or "none"
    if outcome not in OUTCOMES:
        raise HardValidation("BEH-OUTCOME", "Unknown outcome", ", ".join(OUTCOMES.values()))
    text = " ".join((description or "").split())[:2000] or None
    if kind.polarity == "negative" and kind.points <= -3 and not text:
        raise HardValidation("BEH-DESCRIPTION", "Say what happened", f"{kind.label} needs a short description.")
    targets = [t for t in dict.fromkeys(target_ids or []) if t not in chosen]
    if kind.category == "bullying":
        if not targets:
            raise HardValidation(
                "BEH-TARGET",
                "Name who was bullied",
                "Bullying needs the learner(s) it was aimed at, for their support.",
            )
        on_roll = set(_members(cls.id, occurred_at.date())) | _school_roll(cls.institution_id, occurred_at.date())
        if any(t not in on_roll for t in targets):
            raise HardValidation("BEH-TARGET", "Not a learner of the school", "")
    decided = ctx.has("behaviour:manage") or outcome not in HEAD_DECISION
    staff = my_staff_id(ctx) or ctx.actor_id
    assert staff is not None
    with uow.command("ops", "behaviour:log", action="log_behaviour", record_kind="behaviour_event") as cmd:
        out = []
        for lid in chosen:
            e = cmd.add(
                BehaviourEvent(
                    scope_node_id=cls.scope_node_id,
                    learner_id=lid,
                    behaviour_type_id=kind.id,
                    points=kind.points,
                    location=(location or cls.name)[:120],
                    occurred_at=occurred_at,
                    recorded_by_staff_id=staff,
                    description=text,
                    target_learner_ids=[str(t) for t in targets] or None,
                    outcome=outcome,
                    decision_by=ctx.actor_id if decided and outcome in HEAD_DECISION else None,
                )
            )
            out.append(e)
        cmd.record_id = out[0].id
        return out


def _school_roll(institution_id: uuid.UUID, on: dt.date) -> set[uuid.UUID]:
    classes = ClassGroup.objects.filter(institution_id=institution_id, status="active").values_list("id", flat=True)
    return set(
        ClassMembership.objects.filter(class_group_id__in=list(classes), valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .values_list("learner_id", flat=True)
    )


def decide(event_id: uuid.UUID, outcome: str) -> BehaviourEvent:
    """The head's decision on a proposed exclusion or suspension (or any outcome)."""
    if outcome not in OUTCOMES:
        raise HardValidation("BEH-OUTCOME", "Unknown outcome", ", ".join(OUTCOMES.values()))
    ctx = context.require()
    with uow.command("ops", "behaviour:manage", action="decide_behaviour", record_kind="behaviour_event") as cmd:
        e = cmd.lock(BehaviourEvent, event_id)
        if e.reversed_at is not None:
            raise ConflictError("BEH-WITHDRAWN", "The entry was withdrawn", "")
        updated: BehaviourEvent = cmd.update(e, outcome=outcome, decision_by=ctx.actor_id)
        return updated


def withdraw(event_id: uuid.UUID) -> BehaviourEvent:
    """Withdraw an entry made in error: on the day by its author, at any time by the head."""
    from syntegra.curriculum.lessons import my_staff_id

    ctx = context.require()
    with uow.command("ops", "behaviour:log", action="withdraw_behaviour", record_kind="behaviour_event") as cmd:
        e = cmd.lock(BehaviourEvent, event_id)
        if e.reversed_at is not None:
            raise ConflictError("BEH-WITHDRAWN", "Already withdrawn", "")
        mine = e.recorded_by_staff_id in {my_staff_id(ctx), ctx.actor_id}
        same_day = e.created_at.astimezone(_tz()).date() == dt.datetime.now(_tz()).date()
        if not ctx.has("behaviour:manage") and not (mine and same_day):
            raise Forbidden("Only the person who recorded it, on the same day, or the head can withdraw an entry.")
        updated: BehaviourEvent = cmd.update(e, reversed_at=utcnow())
        return updated


def overview(
    institution_id: uuid.UUID, start: dt.date, end: dt.date, class_id: uuid.UUID | None = None
) -> dict[str, Any]:
    from syntegra.academic.teaching import _names
    from syntegra.learners.models import Learner

    ctx = context.require()
    authz.require("behaviour:view", ctx)
    inst = _institution(institution_id)
    tz = _tz()
    a = dt.datetime.combine(start, dt.time(0), tzinfo=tz)
    b = dt.datetime.combine(end + dt.timedelta(days=1), dt.time(0), tzinfo=tz)
    classes = {c.id: c for c in ClassGroup.objects.in_scope().filter(institution_id=inst.id, status="active")}
    roll: dict[uuid.UUID, uuid.UUID] = {}
    for m in ClassMembership.objects.filter(class_group_id__in=list(classes), valid_from__lte=end).exclude(
        valid_to__lt=start
    ):
        roll[m.learner_id] = m.class_group_id
    qs = BehaviourEvent.objects.filter(
        scope_node_id=inst.scope_node_id, occurred_at__gte=a, occurred_at__lt=b, reversed_at__isnull=True
    )
    if class_id is not None:
        qs = qs.filter(learner_id__in=[lid for lid, c in roll.items() if c == class_id])
    events = list(qs.order_by("-occurred_at"))
    kinds = {t.id: t for t in BehaviourType.objects.filter(id__in={e.behaviour_type_id for e in events})}
    targets = {uuid.UUID(t) for e in events for t in (e.target_learner_ids or [])}
    people = {lr.id: lr for lr in Learner.objects.filter(id__in={e.learner_id for e in events} | targets)}
    from syntegra.iam.models import AppUser

    staff = _names({e.recorded_by_staff_id for e in events})
    missing = {e.recorded_by_staff_id for e in events} - set(staff)
    staff |= dict(AppUser.objects.filter(id__in=missing).values_list("id", "display_name"))

    def name(lid: uuid.UUID) -> str:
        lr = people.get(lid)
        return f"{lr.legal_family_name}, {lr.legal_given_name}" if lr else "?"

    by_cat: dict[str, list[int]] = {}
    by_class: dict[uuid.UUID, list[int]] = {}
    by_day = [[0, 0] for _ in WEEKDAYS]
    per: dict[uuid.UUID, dict[str, int]] = {}
    for e in events:
        k = kinds[e.behaviour_type_id]
        pos = k.polarity == "positive"
        by_cat.setdefault(k.category, [0, 0])[0 if pos else 1] += 1
        c = roll.get(e.learner_id)
        if c is not None:
            tally = by_class.setdefault(c, [0, 0, 0])
            tally[0 if pos else 1] += 1
            tally[2] += e.points
        by_day[e.occurred_at.astimezone(tz).weekday()][0 if pos else 1] += 1
        p = per.setdefault(e.learner_id, {"positive": 0, "negative": 0, "points": 0})
        p["positive" if pos else "negative"] += 1
        p["points"] += e.points
    learners: list[dict[str, Any]] = [
        {"learner_id": lid, "name": name(lid), "class": classes[roll[lid]].name if lid in roll else "", **v}
        for lid, v in per.items()
    ]
    waiting = [e for e in events if e.outcome in HEAD_DECISION and e.decision_by is None]

    def row(e: BehaviourEvent) -> dict[str, Any]:
        k = kinds[e.behaviour_type_id]
        return {
            "id": e.id,
            "learner_id": e.learner_id,
            "learner": name(e.learner_id),
            "class": classes[roll[e.learner_id]].name if e.learner_id in roll else "",
            "behaviour": k.label,
            "polarity": k.polarity,
            "points": e.points,
            "outcome": OUTCOMES.get(e.outcome or "none", e.outcome),
            "awaiting": e.outcome in HEAD_DECISION and e.decision_by is None,
            "at": e.occurred_at.astimezone(tz),
            "by": staff.get(e.recorded_by_staff_id, "Staff"),
            "description": e.description,
            "targets": [name(uuid.UUID(t)) for t in (e.target_learner_ids or [])],
        }

    return {
        "institution": {"id": inst.id, "name": inst.name},
        "start": start,
        "end": end,
        "class_id": class_id,
        "classes": [{"id": c.id, "name": c.name} for c in sorted(classes.values(), key=lambda c: c.name)],
        "totals": {
            "positive": sum(1 for e in events if kinds[e.behaviour_type_id].polarity == "positive"),
            "negative": sum(1 for e in events if kinds[e.behaviour_type_id].polarity == "negative"),
            "points": sum(e.points for e in events),
            "learners": len(per),
            "bullying": sum(1 for e in events if kinds[e.behaviour_type_id].category == "bullying"),
        },
        "categories": sorted(
            (
                {"label": CATEGORY_LABELS.get(k, k.replace("_", " ").capitalize()), "positive": v[0], "negative": v[1]}
                for k, v in by_cat.items()
            ),
            key=lambda x: -(x["positive"] + x["negative"]),
        ),
        "by_class": sorted(
            (
                {"name": classes[c].name, "positive": v[0], "negative": v[1], "points": v[2]}
                for c, v in by_class.items()
            ),
            key=lambda x: x["name"],
        ),
        "by_day": [{"day": WEEKDAYS[i], "positive": v[0], "negative": v[1]} for i, v in enumerate(by_day[:5])],
        "top_positive": sorted(learners, key=lambda x: (-x["positive"], x["name"]))[:8],
        "concerns": sorted((x for x in learners if x["negative"]), key=lambda x: (x["points"], x["name"]))[:8],
        "waiting": [row(e) for e in waiting],
        "recent": [row(e) for e in events[:25]],
        "can_manage": ctx.has("behaviour:manage"),
        "outcomes": OUTCOMES,
    }


def learner_summary(learner_id: uuid.UUID, days: int = 90) -> dict[str, Any] | None:
    """Learner 360: the learner's behaviour over the last ``days`` days."""
    ctx = context.require()
    if not ctx.has("behaviour:view"):
        return None
    since = dt.datetime.now(_tz()) - dt.timedelta(days=days)
    events = list(
        BehaviourEvent.objects.filter(learner_id=learner_id, occurred_at__gte=since, reversed_at__isnull=True).order_by(
            "-occurred_at"
        )
    )
    if not events:
        return None
    kinds = {t.id: t for t in BehaviourType.objects.filter(id__in={e.behaviour_type_id for e in events})}
    return {
        "days": days,
        "positive": sum(1 for e in events if kinds[e.behaviour_type_id].polarity == "positive"),
        "negative": sum(1 for e in events if kinds[e.behaviour_type_id].polarity == "negative"),
        "points": sum(e.points for e in events),
        "recent": [
            {
                "at": e.occurred_at.astimezone(_tz()),
                "behaviour": kinds[e.behaviour_type_id].label,
                "points": e.points,
                "outcome": OUTCOMES.get(e.outcome or "none", e.outcome),
            }
            for e in events[:6]
        ],
    }
