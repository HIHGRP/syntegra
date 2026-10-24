"""Clubs and activities (MFS OPS-05; CR-009 phase 4).

The head (or the operations manager) sets up the school's clubs, sports and events: who may join (by class level),
how many places, when it meets and the member of staff who leads it. Places are given first come, first served;
when a club is full, a learner joins the waiting list and moves up — in order — as soon as someone leaves.

A parent asks for a place for their child from the parent pages; a member of staff can add a learner directly.
A place is refused when the learner's level is not eligible, when they already have a place or are waiting, or when
the club meets at the same time as another club they are in.

The leader takes a register at each meeting: the learners present are counted, so the roster shows each learner's
attendance. A register is taken once per meeting day, on the club's own weekday, on or before today.

Where the details are kept: the activity record carries eligibility, capacity and allocation as columns; the
meeting day and time, the leader, the description and the dates the register was taken are kept in its
``eligibility_rule`` document until a CEDA release gives them columns of their own (CEDA §37).
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.families import portal
from syntegra.operations.models import Activity, ActivityEnrolment

KINDS = {"club": "Club", "sport": "Sport", "event": "Event", "holiday_programme": "Holiday programme"}
LEVELS = {"JSS1": "JSS 1", "JSS2": "JSS 2", "JSS3": "JSS 3", "SSS1": "SS 1", "SSS2": "SS 2", "SSS3": "SS 3"}
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
HOLDING = ("allocated", "waitlisted")


def _institution(institution_id: uuid.UUID) -> Any:
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _activity(activity_id: uuid.UUID) -> Activity:
    a: Activity | None = Activity.objects.in_scope().filter(pk=activity_id).first()
    if a is None:
        raise NotFound("activity", activity_id)
    return a


def _rule(a: Activity) -> dict[str, Any]:
    return dict(a.eligibility_rule or {})


def _times(a: Activity) -> tuple[int, dt.time, dt.time] | None:
    m = _rule(a).get("meets")
    if not m:
        return None
    return int(m["day"]), dt.time.fromisoformat(m["from"]), dt.time.fromisoformat(m["to"])


def _my_staff_id() -> uuid.UUID | None:
    from syntegra.iam.models import AppUser

    u = AppUser.objects.filter(pk=context.require().actor_id).first()
    return u.person_id if u is not None and u.person_kind == "staff" else None


def _leads(a: Activity) -> bool:
    lead = _rule(a).get("lead_staff_id")
    return lead is not None and str(_my_staff_id()) == lead


def create(
    institution_id: uuid.UUID,
    *,
    name: str,
    kind: str,
    levels: list[str],
    capacity: int,
    day: int,
    starts: str,
    ends: str,
    lead_staff_id: uuid.UUID | None,
    description: str | None = None,
) -> Activity:
    from syntegra.academic import teaching

    inst = _institution(institution_id)
    name = (name or "").strip()
    if len(name) < 3:
        raise HardValidation("ACT-NAME", "Give the activity a name", "For example: Chess club.")
    if kind not in KINDS:
        raise HardValidation("ACT-KIND", "Choose the kind of activity", ", ".join(KINDS.values()))
    levels = [lv for lv in levels if lv in LEVELS]
    if not levels:
        raise HardValidation("ACT-LEVELS", "Who may join", "Tick at least one class level.")
    if not (2 <= capacity <= 200):
        raise HardValidation("ACT-CAPACITY", "Number of places", "Between 2 and 200.")
    if not (0 <= day < len(WEEKDAYS)):
        raise HardValidation("ACT-DAY", "Choose the day it meets", "Monday to Saturday.")
    try:
        a, b = dt.time.fromisoformat(starts), dt.time.fromisoformat(ends)
    except (TypeError, ValueError) as exc:
        raise HardValidation("ACT-TIME", "Give the times", "For example 14:30 to 15:30.") from exc
    if b <= a:
        raise HardValidation("ACT-TIME", "Check the times", "It has to finish after it starts.")
    if lead_staff_id is None or lead_staff_id not in {p.staff_id for p in teaching.staff_of(inst.id)}:
        raise HardValidation("ACT-LEAD", "Choose who leads it", "A member of staff at the school.")
    if Activity.objects.filter(scope_node_id=inst.scope_node_id, name=name, status="active").exists():
        raise ConflictError("ACT-NAME", "There is already an activity with this name", "Choose another name.")
    rule = {
        "levels": levels,
        "meets": {"day": day, "from": a.strftime("%H:%M"), "to": b.strftime("%H:%M")},
        "lead_staff_id": str(lead_staff_id),
        "description": (description or "").strip()[:500] or None,
        "sessions": [],
    }
    with uow.command("ops", "activity:manage", action="create_activity", record_kind="activity") as cmd:
        return cmd.add(
            Activity(
                scope_node_id=inst.scope_node_id,
                name=name,
                activity_kind=kind,
                eligibility_rule=rule,
                capacity=capacity,
                allocation_method="first_come",
                status="active",
            )
        )


def _row(a: Activity, counts: dict[uuid.UUID, dict[str, int]], leads: dict[str, str]) -> dict[str, Any]:
    rule = _rule(a)
    t = _times(a)
    c = counts.get(a.id, {})
    return {
        "id": a.id,
        "name": a.name,
        "kind": KINDS.get(a.activity_kind, a.activity_kind),
        "levels": [LEVELS[lv] for lv in rule.get("levels", []) if lv in LEVELS],
        "level_codes": rule.get("levels", []),
        "when": f"{WEEKDAYS[t[0]]} {t[1]:%H:%M}–{t[2]:%H:%M}" if t else "",
        "lead": leads.get(rule.get("lead_staff_id", ""), ""),
        "description": rule.get("description"),
        "capacity": a.capacity,
        "allocated": c.get("allocated", 0),
        "waiting": c.get("waitlisted", 0),
        "left": max(0, (a.capacity or 0) - c.get("allocated", 0)),
        "sessions": len(rule.get("sessions", [])),
    }


def _counts(ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, int]]:
    out: dict[uuid.UUID, dict[str, int]] = {}
    for e in ActivityEnrolment.objects.filter(activity_id__in=ids, allocation__in=HOLDING):
        d = out.setdefault(e.activity_id, {})
        d[e.allocation] = d.get(e.allocation, 0) + 1
    return out


def _lead_names(acts: list[Activity]) -> dict[str, str]:
    from syntegra.people.models import Staff

    ids = {_rule(a).get("lead_staff_id") for a in acts} - {None}
    return {str(s.id): f"{s.given_name} {s.family_name}" for s in Staff.objects.filter(id__in=list(ids))}


def catalogue(institution_id: uuid.UUID) -> dict[str, Any]:
    from syntegra.academic import teaching
    from syntegra.people.models import Staff

    inst = _institution(institution_id)
    acts = list(Activity.objects.in_scope().filter(scope_node_id=inst.scope_node_id, status="active").order_by("name"))
    counts = _counts([a.id for a in acts])
    leads = _lead_names(acts)
    me = str(_my_staff_id())
    staff = {p.staff_id for p in teaching.staff_of(inst.id)}
    return {
        "institution": {"id": inst.id, "name": inst.name},
        "activities": [{**_row(a, counts, leads), "mine": _rule(a).get("lead_staff_id") == me} for a in acts],
        "staff": sorted(
            ({"id": s.id, "name": f"{s.given_name} {s.family_name}"} for s in Staff.objects.filter(id__in=staff)),
            key=lambda x: x["name"],
        ),
        "can_manage": context.require().has("activity:manage"),
        "kinds": KINDS,
        "levels": LEVELS,
        "weekdays": list(enumerate(WEEKDAYS)),
    }


def _level_of(class_id: uuid.UUID) -> str | None:
    from syntegra.academic.models import ClassGroup

    c = ClassGroup.objects.filter(pk=class_id).first()
    return c.education_level if c else None


def _current_class(learner_id: uuid.UUID) -> uuid.UUID | None:
    from syntegra.academic.models import ClassMembership

    return (
        ClassMembership.objects.filter(learner_id=learner_id, is_arm=True, valid_to__isnull=True)
        .values_list("class_group_id", flat=True)
        .first()
    )


def for_parent() -> list[dict[str, Any]]:
    """For each child: the activities they hold a place in or are waiting for, and those open to their level."""
    kids = portal.children()
    if not kids:
        return []
    acts = list(Activity.objects.in_scope().filter(status="active").order_by("name"))
    counts = _counts([a.id for a in acts])
    leads = _lead_names(acts)
    held = list(ActivityEnrolment.objects.filter(learner_id__in=[k["id"] for k in kids], allocation__in=HOLDING))
    out = []
    for k in kids:
        level = _level_of(k["class_id"])
        mine = {e.activity_id: e for e in held if e.learner_id == k["id"]}
        rows = []
        for a in acts:
            r = _row(a, counts, leads)
            e = mine.get(a.id)
            if e is None and level not in r["level_codes"]:
                continue
            r["enrolment"] = (
                {
                    "id": e.id,
                    "allocation": e.allocation,
                    "position": e.waiting_position,
                    "attended": e.sessions_attended,
                }
                if e
                else None
            )
            rows.append(r)
        out.append({**k, "activities": rows})
    return out


def _clash(a: Activity, learner_id: uuid.UUID) -> str | None:
    t = _times(a)
    if t is None:
        return None
    for e in ActivityEnrolment.objects.filter(learner_id=learner_id, allocation="allocated").exclude(activity_id=a.id):
        other = Activity.objects.filter(pk=e.activity_id, status="active").first()
        u = _times(other) if other else None
        if u and u[0] == t[0] and t[1] < u[2] and u[1] < t[2]:
            name: str = other.name  # type: ignore[union-attr]
            return name
    return None


def join(activity_id: uuid.UUID, learner_id: uuid.UUID) -> ActivityEnrolment:
    """A place (or a place on the waiting list) for a learner: asked for by their parent, or added by staff."""
    ctx = context.require()
    a = _activity(activity_id)
    if portal.is_parent():
        authz.require("activity:apply", ctx)
        portal.require_child(learner_id)
    elif not (ctx.has("activity:manage") or _leads(a)):
        raise Forbidden("Parents ask for places; the head or the activity's leader adds learners.", code="ACT-OWN")
    cls = _current_class(learner_id)
    if cls is None:
        raise HardValidation("ACT-LEARNER", "The learner is not on roll", "Choose a learner in a class.")
    if _level_of(cls) not in _rule(a).get("levels", []):
        raise HardValidation("ACT-LEVEL", f"{a.name} is not open to the learner's class level", "Choose another.")
    with uow.command("ops", None, action="join_activity", record_kind="activity_enrolment") as cmd:
        a = cmd.lock(Activity, a.id)
        existing = ActivityEnrolment.objects.filter(activity_id=a.id, learner_id=learner_id).first()
        if existing is not None and existing.allocation in HOLDING:
            what = "has a place" if existing.allocation == "allocated" else "is already on the waiting list"
            raise ConflictError("ACT-TWICE", f"The learner {what}", f"For {a.name}.")
        other = _clash(a, learner_id)
        if other:
            raise ConflictError(
                "ACT-CLASH", f"It meets at the same time as {other}", "A learner can be in one of them."
            )
        holding = list(ActivityEnrolment.objects.filter(activity_id=a.id, allocation__in=HOLDING))
        placed = sum(1 for e in holding if e.allocation == "allocated")
        waiting = [e.waiting_position or 0 for e in holding if e.allocation == "waitlisted"]
        if placed < (a.capacity or 0):
            allocation, position = "allocated", None
        else:
            allocation, position = "waitlisted", max(waiting, default=0) + 1
        if existing is not None:
            again: ActivityEnrolment = cmd.update(
                existing, allocation=allocation, waiting_position=position, preference_rank=1
            )
            return again
        return cmd.add(
            ActivityEnrolment(
                activity_id=a.id,
                learner_id=learner_id,
                preference_rank=1,
                allocation=allocation,
                waiting_position=position,
                sessions_attended=0,
            )
        )


def leave(enrolment_id: uuid.UUID) -> ActivityEnrolment | None:
    """Give up a place or leave the waiting list. A freed place goes to the first learner waiting, who is returned."""
    ctx = context.require()
    e = ActivityEnrolment.objects.filter(pk=enrolment_id, allocation__in=HOLDING).first()
    if e is None:
        raise NotFound("activity_enrolment", enrolment_id)
    a = _activity(e.activity_id)
    if portal.is_parent():
        portal.require_child(e.learner_id)
    elif not (ctx.has("activity:manage") or _leads(a)):
        raise Forbidden("Only the learner's parent, the leader or the head can do this.", code="ACT-OWN")
    with uow.command("ops", None, action="leave_activity", record_kind="activity_enrolment") as cmd:
        cmd.lock(Activity, a.id)
        e = cmd.lock(ActivityEnrolment, e.id)
        was = e.allocation
        cmd.update(e, allocation="withdrawn", waiting_position=None)
        queue = sorted(
            ActivityEnrolment.objects.filter(activity_id=a.id, allocation="waitlisted"),
            key=lambda x: x.waiting_position or 0,
        )
        promoted = None
        if was == "allocated" and queue:
            promoted = cmd.update(queue.pop(0), allocation="allocated", waiting_position=None)
        for i, w in enumerate(queue, start=1):
            if w.waiting_position != i:
                cmd.update(w, waiting_position=i)
        return promoted


def roster(activity_id: uuid.UUID) -> dict[str, Any]:
    from syntegra.academic.models import ClassGroup, ClassMembership
    from syntegra.learners.models import Learner

    ctx = context.require()
    a = _activity(activity_id)
    if not (ctx.has("activity:manage") or ctx.has("activity:lead")):
        raise Forbidden("The roster is for the school's staff.", code="ACT-OWN")
    rule = _rule(a)
    es = list(ActivityEnrolment.objects.filter(activity_id=a.id, allocation__in=HOLDING))
    learners = {lr.id: lr for lr in Learner.objects.filter(id__in=[e.learner_id for e in es])}
    members = {
        m.learner_id: m.class_group_id
        for m in ClassMembership.objects.filter(learner_id__in=list(learners), is_arm=True, valid_to__isnull=True)
    }
    classes = {c.id: c.name for c in ClassGroup.objects.filter(id__in=set(members.values()))}
    held = len(rule.get("sessions", []))

    def person(e: ActivityEnrolment) -> dict[str, Any]:
        lr = learners.get(e.learner_id)
        return {
            "enrolment_id": e.id,
            "learner_id": e.learner_id,
            "name": f"{lr.legal_family_name}, {lr.legal_given_name}" if lr else "Learner",
            "class": classes.get(members.get(e.learner_id), ""),
            "attended": e.sessions_attended,
            "rate": round(100 * e.sessions_attended / held) if held else None,
            "position": e.waiting_position,
        }

    placed = sorted((person(e) for e in es if e.allocation == "allocated"), key=lambda r: r["name"])
    waiting = sorted((person(e) for e in es if e.allocation == "waitlisted"), key=lambda r: r["position"] or 0)
    eligible: list[dict[str, Any]] = []
    if ctx.has("activity:manage") or _leads(a):
        inst_classes = list(
            ClassGroup.objects.in_scope().filter(
                scope_node_id=a.scope_node_id, education_level__in=rule.get("levels", []), status="active"
            )
        )
        eligible = [{"id": c.id, "name": c.name} for c in sorted(inst_classes, key=lambda c: c.name)]
    counts = _counts([a.id])
    return {
        "activity": _row(a, counts, _lead_names([a])),
        "placed": placed,
        "waiting": waiting,
        "sessions": sorted((dt.date.fromisoformat(x) for x in rule.get("sessions", [])), reverse=True),
        "can_register": _leads(a) or ctx.has("activity:manage"),
        "eligible_classes": eligible,
    }


def register(activity_id: uuid.UUID, on: dt.date, present: list[uuid.UUID]) -> int:
    """The leader's register for one meeting: each learner present has the meeting counted."""
    ctx = context.require()
    a = _activity(activity_id)
    if not (_leads(a) or ctx.has("activity:manage")):
        raise Forbidden("The leader takes the register.", code="ACT-OWN")
    t = _times(a)
    if t is None or on.weekday() != t[0]:
        raise HardValidation(
            "ACT-DAY", f"{a.name} does not meet on {on:%A}", f"It meets on {WEEKDAYS[t[0]] if t else '—'}."
        )
    if on > dt.date.today():
        raise HardValidation("ACT-DAY", "That day has not come yet", "Take the register on the day.")
    with uow.command("ops", None, action="activity_register", record_kind="activity") as cmd:
        a = cmd.lock(Activity, a.id)
        rule = _rule(a)
        if on.isoformat() in rule.get("sessions", []):
            raise ConflictError("ACT-REGISTER", "The register for that day is already taken", f"{on:%d %B %Y}.")
        placed = {e.learner_id: e for e in ActivityEnrolment.objects.filter(activity_id=a.id, allocation="allocated")}
        unknown = set(present) - set(placed)
        if unknown:
            raise HardValidation("ACT-REGISTER", "A learner is not in the activity", "Tick learners from the list.")
        for lid in present:
            e = placed[lid]
            cmd.update(e, sessions_attended=e.sessions_attended + 1)
        rule["sessions"] = sorted([*rule.get("sessions", []), on.isoformat()])
        cmd.update(a, eligibility_rule=rule)
        cmd.note("present", None, len(present))
        return len(present)
