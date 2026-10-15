"""Classroom seating plans (MFS BEH-102, FR-BEH-101, FR-BEH-102, FR-BEH-110).

A teacher arranges a class in its classroom: chooses the room and its layout (desks are kept as a reusable room
layout), and either generates an arrangement by strategy (``success.arrange``) or moves learners by hand. The plan shows
each learner's context from the class's seating field set — working grade (red, amber, green from this term's marks),
attendance and authorised adjustments — to staff entitled to see it; the board-safe view for the classroom screen
shows names only. Printing for an observer or inspector is logged with the viewer's name, which is watermarked on the
print. A room assessed unsafe, unusable or condemned is refused.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.academic.models import ClassGroup, ClassMembership
from syntegra.core import authz, context, uow
from syntegra.core.errors import HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.success import arrange
from syntegra.success.models import (
    Adjustment,
    InfluenceScore,
    RoomLayout,
    SeatingFieldSet,
    SeatingPlan,
    SeatingPlanPrint,
)

FRONT_ADJUSTMENTS = ("seating", "large_print")
DEFAULT_FIELDS = ["working_grade", "attendance", "adjustments"]
STYLE_LABEL = {"pairs": "Two-seater desks in rows", "rows": "Single desks in rows", "groups": "Tables of six"}


def _class(class_id: uuid.UUID) -> ClassGroup:
    c: ClassGroup | None = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    if c is None:
        raise NotFound("class", class_id)
    return c


def _room(class_: ClassGroup, room_id: uuid.UUID | None) -> Any:
    from syntegra.estate import services as estate
    from syntegra.operations.models import Room

    rid = room_id or class_.room_id
    if rid is None:
        raise HardValidation("SEAT-ROOM", "Choose the classroom", "This class has no home room yet.")
    room = Room.objects.filter(pk=rid, scope_node_id=class_.scope_node_id, status="active").first()
    if room is None:
        raise HardValidation("SEAT-ROOM", "Choose a classroom of this school", "")
    usability = estate.room_usability([room.id]).get(room.id)
    if usability in estate.UNSAFE_USABILITY:
        raise HardValidation(
            "SEAT-ROOM-UNSAFE",
            "This room cannot be used",
            f"{room.code} is assessed {usability.replace('_', ' ')} — choose another classroom.",
        )
    return room


def rooms(class_id: uuid.UUID) -> list[dict[str, Any]]:
    """Classrooms of the class's school, with their seats and latest usability."""
    from syntegra.estate import services as estate
    from syntegra.operations.models import Room

    c = _class(class_id)
    rows = list(
        Room.objects.filter(
            scope_node_id=c.scope_node_id,
            status="active",
            room_type__in=("classroom", "laboratory", "ict_suite", "hall"),
        ).order_by("code")
    )
    use = estate.room_usability([r.id for r in rows])
    return [
        {
            "id": r.id,
            "code": r.code,
            "capacity": r.capacity,
            "usability": use.get(r.id),
            "usable": use.get(r.id) not in estate.UNSAFE_USABILITY,
            "home": r.id == c.room_id,
        }
        for r in rows
    ]


def _layout(cmd: uow.Command, room: Any, style: str) -> RoomLayout:
    name = STYLE_LABEL[style]
    existing: RoomLayout | None = RoomLayout.objects.filter(room_id=room.id, name=name).first()
    if existing is not None:
        return existing
    seats = arrange.layout(room.capacity, style)
    return cmd.add(
        RoomLayout(
            room_id=room.id,
            name=name,
            desks={
                "style": style,
                "seats": [{"label": s.label, "row": s.row, "col": s.col, "unit": s.unit} for s in seats],
            },
        )
    )


def _seats(lay: RoomLayout) -> list[arrange.Seat]:
    return [arrange.Seat(d["label"], d["row"], d["col"], d["unit"]) for d in (lay.desks or {}).get("seats", [])]


def _field_set(cmd: uow.Command, class_: ClassGroup) -> SeatingFieldSet:
    fs: SeatingFieldSet | None = SeatingFieldSet.objects.filter(scope_node_id=class_.scope_node_id).first()
    if fs is None:
        fs = cmd.add(
            SeatingFieldSet(
                scope_node_id=class_.scope_node_id,
                name="Standard",
                applies_to={"levels": "all"},
                fields=DEFAULT_FIELDS,
                board_safe_fields=[],
            )
        )
    return fs


def roster(class_: ClassGroup) -> list[dict[str, Any]]:
    """Learners in the class with the context the seating plan shows."""
    from syntegra.attendance.models import AttendanceMark
    from syntegra.learners.models import Learner

    members = list(ClassMembership.objects.filter(class_group_id=class_.id, valid_to__isnull=True, is_arm=True))
    ids = [m.learner_id for m in members]
    people = {lr.id: lr for lr in Learner.objects.filter(id__in=ids)}
    averages: dict[uuid.UUID, float] = {}
    if context.require().has("assessment:view"):
        from syntegra.assessment.services import class_results

        averages = {r["learner_id"]: r["average"] for r in class_results(class_.id)["rows"] if r["average"] is not None}
    seen: dict[uuid.UUID, list[int]] = {i: [0, 0] for i in ids}
    for lid, code in AttendanceMark.objects.filter(learner_id__in=ids).values_list("learner_id", "code"):
        if code != "NR":
            seen[lid][1] += 1
            seen[lid][0] += int(code in ("P", "L", "AA"))
    today = dt.date.today()
    adjustments: dict[uuid.UUID, list[str]] = {}
    for a in Adjustment.objects.filter(learner_id__in=ids, valid_from__lte=today):
        if a.valid_to is None or a.valid_to >= today:
            adjustments.setdefault(a.learner_id, []).append(a.adjustment_kind)
    out = []
    for lid in ids:
        lr = people.get(lid)
        if lr is None:
            continue
        att = seen[lid]
        avg = averages.get(lid)
        out.append(
            {
                "key": str(lid),
                "given": lr.preferred_name or lr.legal_given_name,
                "family": lr.legal_family_name,
                "average": round(avg, 1) if avg is not None else None,
                "rag": arrange.rag(avg),
                "attendance": round(att[0] / att[1], 3) if att[1] else None,
                "adjustments": sorted(set(adjustments.get(lid, []))),
            }
        )
    return sorted(out, key=lambda x: (x["family"].lower(), x["given"].lower()))


def _avoid(class_: ClassGroup) -> list[tuple[str, str]]:
    rows = InfluenceScore.objects.filter(class_group_id=class_.id).values_list(
        "learner_a_id", "learner_b_id", "shared_events", "negative_adjacent", "negative_apart"
    )
    return arrange.influence_pairs([(str(a), str(b), s, na, nb) for a, b, s, na, nb in rows])


# --------------------------------------------------------------------------- commands
def generate(
    class_id: uuid.UUID,
    *,
    strategy: str,
    style: str = "pairs",
    room_id: uuid.UUID | None = None,
    seed: int | None = None,
) -> SeatingPlan:
    """A new active plan for the class, arranged by ``strategy`` on the room's layout (the previous plan is kept)."""
    if strategy not in arrange.STRATEGIES or strategy == "manual":
        raise HardValidation("SEAT-STRATEGY", "Choose a strategy", ", ".join(arrange.STRATEGIES[:-1]))
    if style not in arrange.STYLES:
        raise HardValidation("SEAT-LAYOUT", "Choose a layout", ", ".join(arrange.STYLES))
    c = _class(class_id)
    room = _room(c, room_id)
    people = roster(c)
    learners = [
        arrange.Learner(
            p["key"], p["family"], p["given"], p["average"], front=any(k in FRONT_ADJUSTMENTS for k in p["adjustments"])
        )
        for p in people
    ]
    evidence = _avoid(c)
    avoid = evidence if strategy == "separate_negative_influences" else []
    seed = seed if seed is not None else int(dt.datetime.now(dt.UTC).timestamp()) % 100_000
    with uow.command("ops", "seating:manage", action="generate", record_kind="seating_plan") as cmd:
        lay = _layout(cmd, room, style)
        seats = _seats(lay)
        if len(learners) > len(seats):
            raise HardValidation(
                "SEAT-CAPACITY",
                "Not enough seats",
                f"{len(learners)} learners but {len(seats)} seats in {room.code} — choose a larger room.",
            )
        placements = arrange.arrange(learners, seats, strategy, seed=seed, avoid=avoid)
        fs = _field_set(cmd, c)
        for old in SeatingPlan.objects.filter(class_group_id=c.id, is_active=True):
            cmd.update(old, is_active=False)
        plan = cmd.add(
            SeatingPlan(
                class_group_id=c.id,
                room_layout_id=lay.id,
                field_set_id=fs.id,
                strategy=strategy,
                placements={
                    "seats": placements,
                    "seed": seed,
                    "kept_apart": len(avoid),
                    "still_neighbours": len(arrange.conflicts(placements, seats, evidence)),
                },
                is_active=True,
            )
        )
        cmd.note("seating", None, {"class": c.name, "room": room.code, "strategy": strategy, "learners": len(learners)})
        return plan


def save_manual(plan_id: uuid.UUID, placements: dict[str, str]) -> SeatingPlan:
    """The teacher's own arrangement (drag and drop): every learner of the class at most once, on a seat of the room."""
    with uow.command("ops", "seating:manage", action="rearrange", record_kind="seating_plan") as cmd:
        plan = cmd.lock(SeatingPlan, plan_id)
        c = _class(plan.class_group_id)
        lay = RoomLayout.objects.get(pk=plan.room_layout_id)
        labels = {s.label for s in _seats(lay)}
        members = {p["key"] for p in roster(c)}
        bad = [k for k, v in placements.items() if k not in members or v not in labels]
        if bad or len(set(placements.values())) != len(placements):
            raise HardValidation("SEAT-PLACEMENTS", "Each learner of this class on one seat, one learner per seat", "")
        avoid = _avoid(c)
        data = dict(plan.placements or {})
        data.update(seats=placements, still_neighbours=len(arrange.conflicts(placements, _seats(lay), avoid)))
        return cmd.update(plan, placements=data, strategy="manual")


def log_print(plan_id: uuid.UUID, viewer_name: str) -> SeatingPlanPrint:
    if len(viewer_name.strip()) < 3:
        raise HardValidation("SEAT-VIEWER", "Who is the print for?", "Give the observer's or inspector's name.")
    with uow.command("ops", "seating:manage", action="print", record_kind="seating_plan_print") as cmd:
        plan = SeatingPlan.objects.filter(pk=plan_id).first()
        if plan is None:
            raise NotFound("seating plan", plan_id)
        _class(plan.class_group_id)
        return cmd.add(
            SeatingPlanPrint(
                seating_plan_id=plan.id,
                printed_by=cmd.ctx.actor_id,
                viewer_name=viewer_name.strip()[:200],
                printed_at=utcnow(),
            )
        )


# --------------------------------------------------------------------------- read model (BEH-102)
def plan_view(class_id: uuid.UUID, *, board: bool = False) -> dict[str, Any]:
    """The active plan as a grid of seats; the board-safe view carries names only."""
    ctx = context.require()
    authz.require("seating:view", ctx)
    c = _class(class_id)
    plan: SeatingPlan | None = (
        SeatingPlan.objects.filter(class_group_id=c.id, is_active=True).order_by("-created_at").first()
    )
    people = {p["key"]: p for p in roster(c)}
    from syntegra.institutions.models import Institution

    inst = Institution.objects.filter(pk=c.institution_id).first()
    base: dict[str, Any] = {
        "class": {"id": c.id, "name": c.name, "level": c.education_level},
        "institution": inst.name if inst else "",
        "learners": len(people),
        "plan": None,
        "board": board,
        "kept_apart_pairs": len(_avoid(c)),
    }
    if plan is None:
        return base
    lay = RoomLayout.objects.get(pk=plan.room_layout_id)
    from syntegra.operations.models import Room

    room = Room.objects.filter(pk=lay.room_id).first()
    seats = _seats(lay)
    at = {v: k for k, v in (plan.placements or {}).get("seats", {}).items()}
    rows: dict[int, list[dict[str, Any]]] = {}
    for s in sorted(seats, key=lambda s: (s.row, s.col)):
        key = at.get(s.label)
        p = people.get(key) if key else None
        cell: dict[str, Any] = {"label": s.label, "unit": s.unit, "col": s.col, "learner": None}
        if p is not None:
            cell["learner"] = (
                {"key": p["key"], "name": f"{p['given']} {p['family']}"}
                if board
                else {**p, "name": f"{p['given']} {p['family']}"}
            )
        rows.setdefault(s.row, []).append(cell)
    unplaced = [] if board else [p for k, p in people.items() if k not in (plan.placements or {}).get("seats", {})]
    placed = (plan.placements or {}).get("seats", {})
    near = arrange.neighbours(seats)
    evidence = []
    if not board:
        counted = {tuple(x) for x in _avoid(c)}
        for row in InfluenceScore.objects.filter(class_group_id=c.id).order_by("-shared_events"):
            a, b = str(row.learner_a_id), str(row.learner_b_id)
            if a not in people or b not in people:
                continue
            evidence.append(
                {
                    "a": f"{people[a]['given']} {people[a]['family']}",
                    "b": f"{people[b]['given']} {people[b]['family']}",
                    "shared": row.shared_events,
                    "negative_adjacent": row.negative_adjacent,
                    "negative_apart": row.negative_apart,
                    "counts": (a, b) in counted,
                    "together": a in placed and b in placed and placed[b] in near[placed[a]],
                    "seats": (placed.get(a), placed.get(b)),
                }
            )
    base["plan"] = {
        "id": plan.id,
        "strategy": plan.strategy,
        "style": (lay.desks or {}).get("style", "pairs"),
        "layout": lay.name,
        "room": room.code if room else "?",
        "capacity": len(seats),
        "rows": [rows[r] for r in sorted(rows)],
        "unplaced": unplaced,
        "still_neighbours": (plan.placements or {}).get("still_neighbours", 0),
        "kept_apart": (plan.placements or {}).get("kept_apart", 0),
        "evidence": evidence,
        "updated_at": plan.updated_at,
    }
    return base
