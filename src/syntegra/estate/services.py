"""Government property register, facility usability and proactive actions (CR-006, FR-EST-01 – FR-EST-05).

Sites (land) are registered here; buildings, rooms and equipment are the operations (OPS) entities. Every
assessment is a dated record of condition and usability. ``evaluate`` runs the proactive rules for an institution:
it proposes new actions to the head, keeps one open action per rule and subject, and closes actions whose
condition has cleared. ``escalate`` moves overdue actions to the LGA and then the ministry. The daily job runs both
for every institution in the registry.
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections import defaultdict
from typing import Any

from syntegra.core import authz, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.estate.domain import rules
from syntegra.estate.models import FacilityAction, FacilityAssessment, MaintenanceSchedule, PropertySite
from syntegra.institutions.models import Campus, Institution
from syntegra.operations.models import Asset, Building, MaintenanceRequest, Room

OPEN = ("open", "acknowledged", "in_progress")
PRIORITY_ORDER = {"critical": 0, "high": 1, "moderate": 2, "info": 3}
ESCALATION_OWNER = {0: "HEAD", 1: "LGA", 2: "STA"}


def _institution(institution_id: uuid.UUID) -> Institution:
    inst: Institution | None = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _main_campus(inst: Institution) -> Campus:
    """The institution's main campus (created on first use: buildings belong to a campus)."""
    c: Campus | None = Campus.objects.filter(institution_id=inst.id).order_by("-is_main", "created_at").first()
    if c is not None:
        return c
    with uow.command("registry", None, action="create", record_kind="campus") as cmd:
        return cmd.add(
            Campus(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                name=f"{inst.name} — main campus",
                address=inst.address,
                location=inst.location,
                is_main=True,
                status="active",
            )
        )


# --------------------------------------------------------------------------- the register (FR-EST-01)
def register_site(
    institution_id: uuid.UUID,
    *,
    site_code: str,
    name: str,
    owner: str,
    title_document: str,
    title_reference: str | None = None,
    area_sqm: float | None = None,
    location: tuple[float, float] | None = None,
    fenced: str = "unknown",
    encroachment: str = "unknown",
    acquired_on: dt.date | None = None,
    valuation_minor: int | None = None,
    valued_on: dt.date | None = None,
) -> PropertySite:
    inst = _institution(institution_id)
    code = site_code.strip().upper()
    if PropertySite.objects.filter(scope_node_id=inst.scope_node_id, site_code=code).exists():
        raise ConflictError("EST-SITE-EXISTS", "Site code in use", f"{code} is already a site of {inst.name}.")
    campus = _main_campus(inst)
    with uow.command("ops", "estate:manage", action="register", record_kind="property_site") as cmd:
        return cmd.add(
            PropertySite(
                scope_node_id=inst.scope_node_id,
                site_code=code,
                name=name,
                institution_id=inst.id,
                campus_id=campus.id,
                owner=owner,
                title_document=title_document,
                title_reference=title_reference,
                area_sqm=area_sqm,
                location=location,
                fenced=fenced,
                encroachment=encroachment,
                acquired_on=acquired_on,
                valuation_minor=valuation_minor,
                currency="NGN" if valuation_minor is not None else None,
                valued_on=valued_on,
                data_status="to_confirm",
                status="active",
            )
        )


def add_building(
    institution_id: uuid.UUID, name: str, *, built_year: int | None = None, facilities: dict[str, Any] | None = None
) -> Building:
    inst = _institution(institution_id)
    campus = _main_campus(inst)
    with uow.command("ops", "estate:manage", action="create", record_kind="building") as cmd:
        return cmd.add(
            Building(
                scope_node_id=inst.scope_node_id,
                campus_id=campus.id,
                name=name,
                built_year=built_year,
                facilities=facilities,
                status="active",
            )
        )


def add_room(building_id: uuid.UUID, code: str, room_type: str, capacity: int, *, name: str | None = None) -> Room:
    b = Building.objects.in_scope().filter(pk=building_id).first()
    if b is None:
        raise NotFound("building", building_id)
    code = code.strip().upper()
    if Room.objects.filter(campus_id=b.campus_id, code=code).exists():
        raise ConflictError("EST-ROOM-EXISTS", "Room code in use", f"{code} already exists on this campus.")
    with uow.command("ops", "estate:manage", action="create", record_kind="room") as cmd:
        return cmd.add(
            Room(
                scope_node_id=b.scope_node_id,
                campus_id=b.campus_id,
                building_id=b.id,
                code=code,
                name=name,
                room_type=room_type,
                capacity=capacity,
                status="active",
            )
        )


def add_asset(
    institution_id: uuid.UUID,
    asset_tag: str,
    name: str,
    category: str,
    *,
    room_id: uuid.UUID | None = None,
    acquired_on: dt.date | None = None,
    value_minor: int | None = None,
    next_service_on: dt.date | None = None,
    safety_check_due_on: dt.date | None = None,
) -> Asset:
    inst = _institution(institution_id)
    tag = asset_tag.strip().upper()
    if Asset.objects.filter(scope_node_id=inst.scope_node_id, asset_tag=tag).exists():
        raise ConflictError("EST-ASSET-EXISTS", "Asset tag in use", tag)
    with uow.command("ops", "estate:manage", action="create", record_kind="asset") as cmd:
        return cmd.add(
            Asset(
                scope_node_id=inst.scope_node_id,
                asset_tag=tag,
                name=name,
                category=category,
                room_id=room_id,
                acquired_on=acquired_on,
                value_minor=value_minor,
                currency="NGN" if value_minor is not None else None,
                next_service_on=next_service_on,
                safety_check_due_on=safety_check_due_on,
                status="in_use",
            )
        )


SUBJECTS: dict[str, Any] = {"site": PropertySite, "building": Building, "room": Room, "asset": Asset}


def _subject(kind: str, subject_id: uuid.UUID) -> tuple[Any, Institution]:
    model = SUBJECTS.get(kind)
    if model is None:
        raise HardValidation("EST-SUBJECT", "Unknown facility kind", kind)
    obj = model.objects.in_scope().filter(pk=subject_id).first()
    if obj is None:
        raise NotFound(kind, subject_id)
    inst = Institution.objects.filter(scope_node_id=obj.scope_node_id).first()
    if inst is None:
        raise NotFound("institution of facility", subject_id)
    return obj, inst


# --------------------------------------------------------------------------- assessments (FR-EST-02)
def assess(
    subject_kind: str,
    subject_id: uuid.UUID,
    *,
    condition_grade: str,
    usability: str,
    structural_risk: str,
    in_use: bool,
    assessor_kind: str = "head_of_institution",
    defects: list[dict[str, Any]] | None = None,
    utilities: dict[str, Any] | None = None,
    learners_affected: int | None = None,
    repair_estimate_minor: int | None = None,
    next_due_on: dt.date | None = None,
    assessed_on: dt.date | None = None,
    client_op_id: uuid.UUID | None = None,
) -> FacilityAssessment:
    """Record a condition and usability assessment, update the facility's condition grade and re-run the rules."""
    obj, inst = _subject(subject_kind, subject_id)
    assessed_on = assessed_on or dt.date.today()
    if assessed_on > dt.date.today():
        raise HardValidation("EST-DATE", "Assessment date is in the future", "")
    if usability in rules.UNSAFE and condition_grade == "good":
        raise HardValidation(
            "EST-INCONSISTENT", "Condition and usability disagree", "A facility in good condition cannot be unsafe."
        )
    if client_op_id:
        dup: FacilityAssessment | None = FacilityAssessment.objects.filter(
            subject_id=subject_id, client_op_id=client_op_id
        ).first()
        if dup is not None:
            return dup  # offline replay
    with uow.command("ops", "estate:assess", action="assess", record_kind="facility_assessment") as cmd:
        a = cmd.add(
            FacilityAssessment(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                subject_kind=subject_kind,
                subject_id=subject_id,
                assessed_on=assessed_on,
                assessor_kind=assessor_kind,
                assessed_by=cmd.ctx.actor_id,
                condition_grade=condition_grade,
                usability=usability,
                structural_risk=structural_risk,
                defects=defects,
                utilities=utilities,
                in_use=in_use,
                learners_affected=learners_affected,
                repair_estimate_minor=repair_estimate_minor,
                currency="NGN" if repair_estimate_minor is not None else None,
                next_due_on=next_due_on,
                client_op_id=client_op_id,
            )
        )
        if subject_kind in ("building", "room", "asset"):
            changes: dict[str, Any] = {"condition_grade": condition_grade}
            if subject_kind == "asset" and usability == "condemned":
                changes["status"] = "condemned"
            cmd.update(obj, **changes)
        cmd.emit(
            "EST.FACILITY_ASSESSED",
            aggregate_id=a.id,
            payload={"facility_assessment_id": str(a.id), "subject_kind": subject_kind, "usability": usability},
            scope_node_id=inst.scope_node_id,
        )
    evaluate(inst.id)
    return a


# --------------------------------------------------------------------------- planned maintenance (FR-EST-03)
def schedule_maintenance(
    subject_kind: str,
    subject_id: uuid.UUID,
    *,
    task: str,
    task_kind: str,
    frequency_days: int,
    next_due_on: dt.date,
    responsible_staff_id: uuid.UUID | None = None,
    estimated_cost_minor: int | None = None,
) -> MaintenanceSchedule:
    _, inst = _subject(subject_kind, subject_id)
    if frequency_days < 1:
        raise HardValidation("EST-FREQUENCY", "Frequency must be at least one day", "")
    with uow.command("ops", "estate:manage", action="schedule", record_kind="maintenance_schedule") as cmd:
        sched = cmd.add(
            MaintenanceSchedule(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                subject_kind=subject_kind,
                subject_id=subject_id,
                task=task,
                task_kind=task_kind,
                frequency_days=frequency_days,
                next_due_on=next_due_on,
                responsible_staff_id=responsible_staff_id,
                estimated_cost_minor=estimated_cost_minor,
                currency="NGN" if estimated_cost_minor is not None else None,
                status="active",
            )
        )
    evaluate(inst.id)
    return sched


def complete_maintenance(
    schedule_id: uuid.UUID, *, done_on: dt.date | None = None, cost_minor: int | None = None, note: str | None = None
) -> MaintenanceSchedule:
    """Record the task as done: a completed preventive work order is kept, and the next due date moves on."""
    done_on = done_on or dt.date.today()
    with uow.command("ops", "estate:act", action="complete", record_kind="maintenance_schedule") as cmd:
        s = cmd.lock(MaintenanceSchedule, schedule_id)
        cmd.add(
            MaintenanceRequest(
                scope_node_id=s.scope_node_id,
                asset_id=s.subject_id if s.subject_kind == "asset" else None,
                room_id=s.subject_id if s.subject_kind == "room" else None,
                description=f"{s.task} (planned){': ' + note if note else ''}",
                risk="info",
                is_preventive=True,
                reported_by=cmd.ctx.actor_id,
                due_on=s.next_due_on,
                completed_at=utcnow(),
                cost_minor=cost_minor,
                currency="NGN" if cost_minor is not None else None,
                status="completed",
            )
        )
        s = cmd.update(s, last_done_on=done_on, next_due_on=done_on + dt.timedelta(days=s.frequency_days))
    evaluate(Institution.objects.get(scope_node_id=s.scope_node_id).id)
    return s


# --------------------------------------------------------------------------- proactive actions (FR-EST-04)
def _facilities(inst: Institution) -> list[rules.Facility]:
    node = inst.scope_node_id
    out: list[rules.Facility] = []
    for s in PropertySite.objects.filter(scope_node_id=node, status="active"):
        out.append(
            rules.Facility(
                "site",
                str(s.id),
                s.name,
                encroachment=s.encroachment,
                title_document=s.title_document,
                government_owned=s.owner in ("federal_government", "state_government", "local_government"),
            )
        )
    for b in Building.objects.filter(scope_node_id=node, status="active"):
        out.append(rules.Facility("building", str(b.id), b.name))
    for r in Room.objects.filter(scope_node_id=node, status="active"):
        out.append(rules.Facility("room", str(r.id), f"{r.code} {r.name or r.room_type.replace('_', ' ')}"))
    for a in Asset.objects.filter(scope_node_id=node).exclude(status__in=("disposed", "lost", "condemned")):
        out.append(
            rules.Facility(
                "asset",
                str(a.id),
                f"{a.name} ({a.asset_tag})",
                safety_check_due_on=a.safety_check_due_on,
                predicted_failure_on=a.predicted_failure_on,
                in_service=a.status == "in_use",
            )
        )
    by_id = {f.id: f for f in out}
    for x in FacilityAssessment.objects.filter(scope_node_id=node).order_by("-assessed_on", "-created_at"):
        f = by_id.get(str(x.subject_id))
        if f is not None:
            f.assessments.append(
                rules.Assessment(x.assessed_on, x.condition_grade, x.usability, x.in_use, x.next_due_on)
            )
    for s in MaintenanceSchedule.objects.filter(scope_node_id=node, status="active"):
        f = by_id.get(str(s.subject_id))
        if f is not None:
            f.schedules.append(rules.Schedule(str(s.id), s.task, s.next_due_on))
    return out


def evaluate(institution_id: uuid.UUID, on: dt.date | None = None) -> dict[str, int]:
    """Run the rules for one institution: raise new actions, close those whose condition has cleared."""
    on = on or dt.date.today()
    inst = Institution.objects.get(pk=institution_id)
    proposals = {p.key: p for f in _facilities(inst) for p in rules.evaluate(f, on)}
    open_ = {a.dedupe_key: a for a in FacilityAction.objects.filter(institution_id=inst.id, status__in=OPEN)}
    n = {"raised": 0, "cleared": 0, "open": 0}
    with uow.command("ops", None, action="evaluate", record_kind="facility_action") as cmd:
        for key, p in proposals.items():
            if key in open_:
                continue
            a = cmd.add(
                FacilityAction(
                    scope_node_id=inst.scope_node_id,
                    institution_id=inst.id,
                    rule=p.rule,
                    subject_kind=p.subject_kind,
                    subject_id=uuid.UUID(p.subject_id),
                    dedupe_key=key,
                    title=p.title[:200],
                    detail=p.detail,
                    priority=p.priority,
                    owner_role=p.owner_role,
                    due_on=p.due_on,
                    escalation_level=0,
                    status="open",
                ),
                cross_scope_basis="proactive facility rule",
            )
            cmd.emit(
                "EST.ACTION_RAISED",
                aggregate_id=a.id,
                payload={"facility_action_id": str(a.id), "rule": p.rule, "priority": p.priority},
                scope_node_id=inst.scope_node_id,
            )
            n["raised"] += 1
        for key, a in open_.items():
            if key not in proposals:
                cmd.update(
                    a,
                    status="done",
                    dedupe_key=f"x:{a.id}",
                    resolved_at=utcnow(),
                    resolution=a.resolution or "Cleared: the condition no longer applies.",
                )
                n["cleared"] += 1
        n["open"] = len(proposals)
        if not (n["raised"] or n["cleared"]):
            cmd.audited = False
    return n


def escalate(on: dt.date | None = None) -> int:
    """Move overdue actions up the hierarchy: the LGA, then the ministry (FR-EST-04)."""
    on = on or dt.date.today()
    n = 0
    with uow.command("ops", None, action="escalate", record_kind="facility_action") as cmd:
        for a in FacilityAction.objects.filter(status__in=OPEN, due_on__lt=on):
            level = rules.escalation(a.priority, a.due_on, a.escalation_level, on)
            if level > a.escalation_level:
                cmd.update(a, escalation_level=level, escalated_at=utcnow(), owner_role=ESCALATION_OWNER[level])
                cmd.emit(
                    "EST.ACTION_ESCALATED",
                    aggregate_id=a.id,
                    payload={"facility_action_id": str(a.id), "escalation_level": level},
                    scope_node_id=a.scope_node_id,
                )
                n += 1
        if not n:
            cmd.audited = False
    return n


def run_daily(on: dt.date | None = None) -> dict[str, int]:
    """Daily job for the registry: evaluate every institution with facilities, then escalate overdue actions."""
    on = on or dt.date.today()
    nodes = set(Building.objects.values_list("scope_node_id", flat=True)) | set(
        PropertySite.objects.values_list("scope_node_id", flat=True)
    )
    totals: dict[str, int] = defaultdict(int)
    for inst in Institution.objects.filter(scope_node_id__in=list(nodes)):
        for k, v in evaluate(inst.id, on).items():
            totals[k] += v
    totals["escalated"] = escalate(on)
    return dict(totals)


def act(action_id: uuid.UUID, status: str, note: str | None = None) -> FacilityAction:
    """The head (or the LGA or ministry once escalated) acknowledges, starts, completes or dismisses an action."""
    if status not in ("acknowledged", "in_progress", "done", "dismissed"):
        raise HardValidation("EST-STATUS", "Unknown action status", status)
    if status == "dismissed" and len((note or "").strip()) < 10:
        raise HardValidation("EST-REASON", "Reason required", "Say why the action is dismissed (10+ characters).")
    with uow.command("ops", "estate:act", action=status, record_kind="facility_action") as cmd:
        a = cmd.lock(FacilityAction, action_id)
        if a.status not in OPEN:
            raise ConflictError("EST-ACTION-CLOSED", "Action is closed", f"It is {a.status}.")
        changes: dict[str, Any] = {"status": status}
        if status in ("done", "dismissed"):
            changes.update(dedupe_key=f"x:{a.id}", resolved_by=cmd.ctx.actor_id, resolved_at=utcnow(), resolution=note)
        return cmd.update(a, **changes)


def raise_work_order(action_id: uuid.UUID) -> MaintenanceRequest:
    """Turn an action into a maintenance request (work order) with the action's priority and due date."""
    with uow.command("ops", "estate:act", action="work_order", record_kind="maintenance_request") as cmd:
        a = cmd.lock(FacilityAction, action_id)
        if a.status not in OPEN:
            raise ConflictError("EST-ACTION-CLOSED", "Action is closed", f"It is {a.status}.")
        if a.maintenance_request_id:
            raise ConflictError("EST-WORK-ORDER", "A work order already exists", str(a.maintenance_request_id))
        mr = cmd.add(
            MaintenanceRequest(
                scope_node_id=a.scope_node_id,
                asset_id=a.subject_id if a.subject_kind == "asset" else None,
                room_id=a.subject_id if a.subject_kind == "room" else None,
                description=f"{a.title}. {a.detail or ''}".strip(),
                risk=a.priority,
                is_preventive=a.rule in ("maintenance_due", "maintenance_overdue", "predicted_failure"),
                reported_by=cmd.ctx.actor_id,
                due_on=a.due_on,
                status="reported",
            )
        )
        cmd.update(a, maintenance_request_id=mr.id, status="in_progress")
        return mr


# --------------------------------------------------------------------------- reads (FR-EST-05, EST-01, EST-02)
def _latest(subject_ids: list[uuid.UUID]) -> dict[uuid.UUID, FacilityAssessment]:
    out: dict[uuid.UUID, FacilityAssessment] = {}
    for x in FacilityAssessment.objects.filter(subject_id__in=subject_ids).order_by("-assessed_on", "-created_at"):
        out.setdefault(x.subject_id, x)
    return out


def _a(x: FacilityAssessment | None) -> dict[str, Any] | None:
    if x is None:
        return None
    return {
        "assessed_on": x.assessed_on,
        "condition_grade": x.condition_grade,
        "usability": x.usability,
        "in_use": x.in_use,
        "repair_estimate": x.repair_estimate_minor,
        "learners_affected": x.learners_affected,
    }


def _action_row(a: FacilityAction) -> dict[str, Any]:
    return {
        "id": a.id,
        "rule": a.rule,
        "title": a.title,
        "detail": a.detail,
        "priority": a.priority,
        "owner_role": a.owner_role,
        "due_on": a.due_on,
        "escalation_level": a.escalation_level,
        "status": a.status,
        "subject_kind": a.subject_kind,
        "work_order": a.maintenance_request_id,
    }


def workspace(institution_id: uuid.UUID) -> dict[str, Any]:
    """The head's facilities workspace: sites, buildings and rooms with their latest usability, equipment due for
    service, the maintenance plan and every open action (FR-EST-05)."""
    authz.require("estate:view")
    inst = _institution(institution_id)
    node = inst.scope_node_id
    sites = list(PropertySite.objects.filter(scope_node_id=node).order_by("site_code"))
    buildings = list(Building.objects.filter(scope_node_id=node, status="active").order_by("name"))
    rooms = list(Room.objects.filter(scope_node_id=node, status="active").order_by("code"))
    assets = list(Asset.objects.filter(scope_node_id=node).exclude(status__in=("disposed", "lost")).order_by("name"))
    latest = _latest([x.id for x in (*sites, *buildings, *rooms, *assets)])
    rooms_by_building: dict[uuid.UUID | None, list[Room]] = defaultdict(list)
    for r in rooms:
        rooms_by_building[r.building_id].append(r)
    classrooms = [r for r in rooms if r.room_type == "classroom"]
    usable = [r for r in classrooms if latest.get(r.id) is None or latest[r.id].usability in rules.USABLE]
    actions = sorted(
        FacilityAction.objects.filter(institution_id=inst.id, status__in=OPEN),
        key=lambda a: (PRIORITY_ORDER[a.priority], a.due_on),
    )
    from syntegra.learners.models import Enrolment

    learners = Enrolment.objects.filter(institution_id=inst.id, status="active", is_primary=True).count()
    return {
        "institution": {"id": inst.id, "name": inst.name, "category": inst.category},
        "summary": {
            "sites": len(sites),
            "buildings": len(buildings),
            "classrooms": len(classrooms),
            "classrooms_usable": len(usable),
            "learners": learners,
            "learners_per_usable_classroom": round(learners / len(usable), 1) if usable else None,
            "unsafe": sum(1 for x in latest.values() if x.usability in rules.UNSAFE),
            "open_actions": len(actions),
            "critical_actions": sum(1 for a in actions if a.priority == "critical"),
            "repair_backlog": sum(
                x.repair_estimate_minor or 0 for x in latest.values() if x.usability != "fully_usable"
            ),
        },
        "sites": [
            {
                "id": s.id,
                "site_code": s.site_code,
                "name": s.name,
                "owner": s.owner,
                "title_document": s.title_document,
                "fenced": s.fenced,
                "encroachment": s.encroachment,
                "area_sqm": s.area_sqm,
                "latest": _a(latest.get(s.id)),
            }
            for s in sites
        ],
        "buildings": [
            {
                "id": b.id,
                "name": b.name,
                "built_year": b.built_year,
                "condition_grade": b.condition_grade,
                "latest": _a(latest.get(b.id)),
                "rooms": [
                    {
                        "id": r.id,
                        "code": r.code,
                        "name": r.name,
                        "room_type": r.room_type,
                        "capacity": r.capacity,
                        "latest": _a(latest.get(r.id)),
                    }
                    for r in rooms_by_building.get(b.id, [])
                ],
            }
            for b in buildings
        ],
        "assets": [
            {
                "id": a.id,
                "asset_tag": a.asset_tag,
                "name": a.name,
                "category": a.category,
                "status": a.status,
                "next_service_on": a.next_service_on,
                "safety_check_due_on": a.safety_check_due_on,
                "latest": _a(latest.get(a.id)),
            }
            for a in assets
        ],
        "schedules": [
            {
                "id": s.id,
                "task": s.task,
                "task_kind": s.task_kind,
                "next_due_on": s.next_due_on,
                "last_done_on": s.last_done_on,
                "frequency_days": s.frequency_days,
            }
            for s in MaintenanceSchedule.objects.filter(scope_node_id=node, status="active").order_by("next_due_on")
        ],
        "actions": [_action_row(a) for a in actions],
    }


def property_register() -> list[dict[str, Any]]:
    """EST-01: every government property site in scope with its institution and latest usability."""
    authz.require("estate:view")
    sites = list(PropertySite.objects.in_scope().filter(status="active").order_by("institution_id", "site_code"))
    names = dict(Institution.objects.filter(id__in={s.institution_id for s in sites}).values_list("id", "name"))
    buildings: dict[uuid.UUID, int] = defaultdict(int)
    for node in Building.objects.in_scope().filter(status="active").values_list("scope_node_id", flat=True):
        buildings[node] += 1
    latest = _latest([s.id for s in sites])
    return [
        {
            "id": s.id,
            "institution_id": s.institution_id,
            "institution": names.get(s.institution_id),
            "site_code": s.site_code,
            "name": s.name,
            "owner": s.owner,
            "title_document": s.title_document,
            "title_reference": s.title_reference,
            "area_sqm": s.area_sqm,
            "fenced": s.fenced,
            "encroachment": s.encroachment,
            "valuation": s.valuation_minor,
            "buildings": buildings.get(s.scope_node_id, 0),
            "latest": _a(latest.get(s.id)),
            "data_status": s.data_status,
        }
        for s in sites
    ]


def actions_in_scope(*, status: str = "open") -> list[dict[str, Any]]:
    """EST-02 across institutions (LGA and ministry): open actions in scope, escalated first."""
    authz.require("estate:view")
    qs = FacilityAction.objects.in_scope().filter(status__in=OPEN if status == "open" else (status,))
    rows = list(qs[:1000])
    names = dict(Institution.objects.filter(id__in={a.institution_id for a in rows}).values_list("id", "name"))
    return [
        {**_action_row(a), "institution": names.get(a.institution_id), "institution_id": a.institution_id}
        for a in sorted(rows, key=lambda a: (-a.escalation_level, PRIORITY_ORDER[a.priority], a.due_on))
    ]
