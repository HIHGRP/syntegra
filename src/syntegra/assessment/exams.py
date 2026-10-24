"""Examinations: series, papers, candidate entries and sitting arrangements (MFS §11, FR-EXM-01 – FR-EXM-03).

An examinations officer (or the head) sets up a series — the first-term examinations, a mock WASSCE — with its papers,
enters whole classes as candidates (each gets a candidate number), and plans each paper's sitting: the halls, the start
time, the spacing, and the invigilators. Seats are allocated by ``assessment.seating``. Halls are rooms of the
institution; a room whose latest facility assessment says it is unsafe, unusable or condemned is refused, and a hall
already used by another paper at an overlapping time is refused. Re-planning a paper replaces its earlier plan.
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections import defaultdict
from typing import Any

from syntegra.academic.models import ClassGroup, ClassMembership
from syntegra.assessment import seating
from syntegra.assessment.models import ExamEntry, ExamPaper, ExamSeries, ExamSitting
from syntegra.core import authz, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.institutions.models import Institution

LIVE_ENTRY = ("eligible", "entered")


def _institution(institution_id: uuid.UUID) -> Institution:
    inst: Institution | None = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _series(series_id: uuid.UUID) -> ExamSeries:
    s: ExamSeries | None = ExamSeries.objects.in_scope().filter(pk=series_id).first()
    if s is None:
        raise NotFound("examination series", series_id)
    return s


def _paper(paper_id: uuid.UUID) -> tuple[ExamPaper, ExamSeries]:
    p: ExamPaper | None = ExamPaper.objects.filter(pk=paper_id).first()
    if p is None:
        raise NotFound("examination paper", paper_id)
    return p, _series(p.series_id)


# --------------------------------------------------------------------------- series, papers, entries
def create_series(
    institution_id: uuid.UUID, name: str, *, exam_body: str = "INSTITUTION", entry_closes_on: dt.date | None = None
) -> ExamSeries:
    inst = _institution(institution_id)
    if ExamSeries.objects.filter(scope_node_id=inst.scope_node_id, name=name.strip()).exists():
        raise ConflictError("EXM-SERIES-EXISTS", "Series exists", f"{name} is already a series of {inst.name}.")
    with uow.command("ops", "exam:manage", action="create", record_kind="exam_series") as cmd:
        return cmd.add(
            ExamSeries(
                scope_node_id=inst.scope_node_id,
                exam_body=exam_body,
                name=name.strip(),
                entry_closes_on=entry_closes_on,
                status="entries_open",
            )
        )


def add_paper(
    series_id: uuid.UUID, paper_code: str, title: str, duration_minutes: int, *, subject_id: uuid.UUID | None = None
) -> ExamPaper:
    s = _series(series_id)
    code = paper_code.strip().upper()
    if ExamPaper.objects.filter(series_id=s.id, paper_code=code).exists():
        raise ConflictError("EXM-PAPER-EXISTS", "Paper exists", f"{code} is already a paper of {s.name}.")
    if not 10 <= duration_minutes <= 480:
        raise HardValidation("EXM-DURATION", "Duration", "A paper lasts between 10 minutes and 8 hours.")
    with uow.command("ops", "exam:manage", action="add_paper", record_kind="exam_paper") as cmd:
        return cmd.add(
            ExamPaper(
                series_id=s.id,
                subject_id=subject_id,
                paper_code=code,
                title=title.strip(),
                duration_minutes=duration_minutes,
            )
        )


def enter_classes(series_id: uuid.UUID, class_ids: list[uuid.UUID], paper_codes: list[str]) -> dict[str, int]:
    """Enter every learner currently in the classes for the papers; candidate numbers follow on in class order."""
    s = _series(series_id)
    papers = set(ExamPaper.objects.filter(series_id=s.id).values_list("paper_code", flat=True))
    codes = [c.strip().upper() for c in paper_codes]
    unknown = [c for c in codes if c not in papers]
    if not codes or unknown:
        raise HardValidation("EXM-PAPERS", "Choose papers of this series", ", ".join(unknown) or "none chosen")
    classes = {c.id: c for c in ClassGroup.objects.in_scope().filter(id__in=class_ids, scope_node_id=s.scope_node_id)}
    if not classes or len(classes) != len(set(class_ids)):
        raise HardValidation("EXM-CLASSES", "Choose classes of this institution", "")
    members = list(ClassMembership.objects.filter(class_group_id__in=list(classes), valid_to__isnull=True, is_arm=True))
    have = {e.learner_id: e for e in ExamEntry.objects.filter(series_id=s.id)}
    inst = Institution.objects.filter(scope_node_id=s.scope_node_id).first()
    prefix = (inst.institution_code if inst else "EXM").replace("INS-NG-", "")
    n = {"entered": 0, "updated": 0}
    with uow.command("ops", "exam:manage", action="enter", record_kind="exam_entry") as cmd:
        seq = len(have)
        for m in sorted(members, key=lambda m: (classes[m.class_group_id].name, str(m.learner_id))):
            e = have.get(m.learner_id)
            if e is None:
                seq += 1
                cmd.add(
                    ExamEntry(
                        scope_node_id=s.scope_node_id,
                        series_id=s.id,
                        learner_id=m.learner_id,
                        enrolment_id=m.enrolment_id,
                        candidate_number=f"{prefix}/{seq:04d}",
                        subjects=sorted(codes),
                        eligibility={"class": classes[m.class_group_id].name},
                        status="entered",
                    )
                )
                n["entered"] += 1
            elif not set(codes) <= set(e.subjects or []):
                cmd.update(e, subjects=sorted(set(e.subjects or []) | set(codes)))
                n["updated"] += 1
        cmd.note("entries", None, n)
    return n


# --------------------------------------------------------------------------- halls and sitting arrangements
def halls(institution_id: uuid.UUID) -> list[dict[str, Any]]:
    """The institution's rooms that can be used as examination halls, with their latest usability."""
    from syntegra.estate import services as estate
    from syntegra.operations.models import Room

    inst = _institution(institution_id)
    rooms = list(
        Room.objects.filter(scope_node_id=inst.scope_node_id, status="active", capacity__gt=0)
        .exclude(room_type__in=("toilet", "store", "generator_house", "water_point", "guard_house", "kitchen_dining"))
        .order_by("code")
    )
    usability = estate.room_usability([r.id for r in rooms])
    return [
        {
            "id": r.id,
            "code": r.code,
            "name": r.name or r.code,
            "room_type": r.room_type,
            "capacity": r.capacity,
            "usability": usability.get(r.id),
            "usable": usability.get(r.id) not in estate.UNSAFE_USABILITY,
        }
        for r in rooms
    ]


def plan_sitting(
    paper_id: uuid.UUID,
    room_ids: list[uuid.UUID],
    starts_at: dt.datetime,
    *,
    spacing: str = "alternate",
    invigilator_staff_ids: list[uuid.UUID] | None = None,
) -> list[ExamSitting]:
    paper, s = _paper(paper_id)
    inst = Institution.objects.filter(scope_node_id=s.scope_node_id).first()
    if inst is None:
        raise NotFound("institution of series", s.id)
    if spacing not in seating.SPACING:
        raise HardValidation("EXM-SPACING", "Spacing", "Choose alternate desks or every desk.")
    if not room_ids:
        raise HardValidation("EXM-HALLS", "Choose at least one hall", "")
    available = {h["id"]: h for h in halls(inst.id)}
    errors = []
    for rid in room_ids:
        h = available.get(rid)
        if h is None:
            errors.append({"field": "room_ids", "message": "a chosen room is not a hall of this institution"})
        elif not h["usable"]:
            errors.append(
                {
                    "field": "room_ids",
                    "message": f"{h['name']} is assessed {str(h['usability']).replace('_', ' ')} — choose another hall",
                }
            )
    if errors:
        raise HardValidation("EXM-HALL-UNSAFE", "Some halls cannot be used", errors=errors)
    ends_at = starts_at + dt.timedelta(minutes=paper.duration_minutes)
    clashes = _clashes(room_ids, starts_at, ends_at, exclude_paper=paper.id)
    if clashes:
        raise ConflictError("EXM-HALL-BUSY", "Hall already in use", "; ".join(clashes))
    entries = [
        e for e in ExamEntry.objects.filter(series_id=s.id, status__in=LIVE_ENTRY) if paper.paper_code in e.subjects
    ]
    if not entries:
        raise HardValidation("EXM-NO-CANDIDATES", "No candidates", f"No one is entered for {paper.paper_code} yet.")
    names = _learner_names({e.learner_id for e in entries})
    candidates = [
        seating.Candidate(
            key=str(e.id),
            number=e.candidate_number or "",
            name=names.get(e.learner_id, "?"),
            group=(e.eligibility or {}).get("class", ""),
            front="front_seat" in ((e.access_arrangements or {}).get("arrangements") or []),
        )
        for e in entries
    ]
    halls_ = [
        seating.Hall(str(rid), available[rid]["code"], available[rid]["name"], available[rid]["capacity"])
        for rid in room_ids
    ]
    try:
        placed = seating.allocate(candidates, halls_, spacing)
    except seating.NotEnoughSeats as exc:
        raise HardValidation(
            "EXM-SEATS",
            "Not enough seats",
            f"{exc.needed} candidates but {exc.available} seats with this spacing — add a hall or use every desk.",
        ) from exc
    staff = [str(x) for x in (invigilator_staff_ids or [])]
    if len(set(staff)) != len(staff):
        raise HardValidation("EXM-INVIGILATORS", "Each invigilator once", "")
    try:
        shares = seating.share_invigilators(placed, staff)
    except ValueError as exc:
        raise HardValidation(
            "EXM-INVIGILATORS",
            "Not enough invigilators",
            f"{exc} — at least one per hall and one more for every further {seating.CANDIDATES_PER_INVIGILATOR}"
            " candidates.",
        ) from exc
    with uow.command("ops", "exam:manage", action="plan_sitting", record_kind="exam_sitting") as cmd:
        for old in ExamSitting.objects.filter(paper_id=paper.id, status="active"):
            cmd.update(old, status="inactive")
        out = []
        for p, invigilators in zip(placed, shares, strict=True):
            out.append(
                cmd.add(
                    ExamSitting(
                        scope_node_id=s.scope_node_id,
                        paper_id=paper.id,
                        room_id=uuid.UUID(p.hall.key),
                        starts_at=starts_at,
                        desk_layout={
                            "rows": p.layout.rows,
                            "cols": p.layout.cols,
                            "spacing": spacing,
                            "hall_code": p.hall.code,
                            "desks": [p.label(rc) for rc in p.layout.desks],
                            "same_class_neighbours": seating.neighbours(p.seats),
                        },
                        seat_allocations={c.key: p.label(rc) for rc, c in p.seats.items()},
                        invigilator_staff_ids=invigilators,
                        status="active",
                    )
                )
            )
        if s.status in ("setup", "entries_open"):
            cmd.update(s, status="entries_closed")
        cmd.note("sitting", None, {"paper": paper.paper_code, "halls": len(out), "candidates": len(candidates)})
        return out


def _clashes(
    room_ids: list[uuid.UUID], starts_at: dt.datetime, ends_at: dt.datetime, *, exclude_paper: uuid.UUID
) -> list[str]:
    from syntegra.operations.models import Room

    out = []
    others = ExamSitting.objects.filter(room_id__in=room_ids, status="active").exclude(paper_id=exclude_paper)
    papers = {p.id: p for p in ExamPaper.objects.filter(id__in={o.paper_id for o in others})}
    rooms = dict(Room.objects.filter(id__in=room_ids).values_list("id", "code"))
    for o in others:
        p = papers.get(o.paper_id)
        if p is None:
            continue
        o_end = o.starts_at + dt.timedelta(minutes=p.duration_minutes)
        if o.starts_at < ends_at and starts_at < o_end:
            out.append(f"{rooms.get(o.room_id, 'hall')} is used for {p.paper_code} from {o.starts_at:%d %b %H:%M}")
    return out


def _learner_names(ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    from syntegra.learners.models import Learner

    return {
        lr.id: f"{lr.legal_family_name.upper()}, {lr.legal_given_name}" for lr in Learner.objects.filter(id__in=ids)
    }


def _staff_names(ids: set[str]) -> dict[str, str]:
    from syntegra.people.models import Staff

    out = {}
    for s in Staff.objects.filter(id__in=[uuid.UUID(x) for x in ids]):
        out[str(s.id)] = f"{s.given_name} {s.family_name}"
    return out


# --------------------------------------------------------------------------- read models (EXM-01, EXM-03)
def series_list() -> list[dict[str, Any]]:
    authz.require("exam:view")
    rows = list(ExamSeries.objects.in_scope().order_by("-created_at")[:200])
    names = dict(
        Institution.objects.filter(scope_node_id__in={s.scope_node_id for s in rows}).values_list(
            "scope_node_id", "name"
        )
    )
    papers: dict[uuid.UUID, int] = defaultdict(int)
    for sid in ExamPaper.objects.filter(series_id__in=[s.id for s in rows]).values_list("series_id", flat=True):
        papers[sid] += 1
    entries: dict[uuid.UUID, int] = defaultdict(int)
    for sid in ExamEntry.objects.filter(series_id__in=[s.id for s in rows], status__in=LIVE_ENTRY).values_list(
        "series_id", flat=True
    ):
        entries[sid] += 1
    return [
        {
            "id": s.id,
            "name": s.name,
            "institution": names.get(s.scope_node_id, ""),
            "exam_body": s.exam_body,
            "status": s.status,
            "papers": papers[s.id],
            "candidates": entries[s.id],
        }
        for s in rows
    ]


def arrangements(series_id: uuid.UUID) -> dict[str, Any]:
    """EXM-03: every paper's sittings with each hall's seat chart, seating list and invigilators."""
    authz.require("exam:view")
    from syntegra.operations.models import Room

    s = _series(series_id)
    papers = list(ExamPaper.objects.filter(series_id=s.id).order_by("paper_code"))
    sittings = list(ExamSitting.objects.filter(paper_id__in=[p.id for p in papers], status="active"))
    entries = {str(e.id): e for e in ExamEntry.objects.filter(series_id=s.id)}
    names = _learner_names({e.learner_id for e in entries.values()})
    rooms = {r.id: r for r in Room.objects.filter(id__in={x.room_id for x in sittings})}
    staff = _staff_names({sid for x in sittings for sid in (x.invigilator_staff_ids or [])})
    classes = sorted({(e.eligibility or {}).get("class", "") for e in entries.values()} - {""})
    by_paper: dict[uuid.UUID, list[dict[str, Any]]] = defaultdict(list)
    for x in sorted(sittings, key=lambda x: (x.starts_at, rooms[x.room_id].code if x.room_id in rooms else "")):
        lay = x.desk_layout or {}
        at_desk = {desk: entries[k] for k, desk in (x.seat_allocations or {}).items() if k in entries}
        grid = []
        code = lay.get("hall_code", "")
        for r in range(int(lay.get("rows", 0))):
            row = []
            for c in range(int(lay.get("cols", 0))):
                label = seating.desk_label(code, r, c)
                e = at_desk.get(label)
                row.append(
                    {
                        "desk": label,
                        "in_use": label in (lay.get("desks") or []),
                        "candidate": None
                        if e is None
                        else {
                            "number": e.candidate_number,
                            "name": names.get(e.learner_id, "?"),
                            "class": (e.eligibility or {}).get("class", ""),
                        },
                    }
                )
            grid.append(row)
        room = rooms.get(x.room_id)
        seated = sorted(
            (
                {
                    "desk": desk,
                    "number": e.candidate_number,
                    "name": names.get(e.learner_id, "?"),
                    "class": (e.eligibility or {}).get("class", ""),
                }
                for desk, e in at_desk.items()
            ),
            key=lambda d: d["number"] or "",
        )
        by_paper[x.paper_id].append(
            {
                "id": x.id,
                "hall": room.name or room.code if room else "?",
                "hall_code": code,
                "starts_at": x.starts_at,
                "spacing": lay.get("spacing"),
                "grid": grid,
                "seated": seated,
                "candidates": len(seated),
                "desks": len(lay.get("desks") or []),
                "same_class_neighbours": lay.get("same_class_neighbours", 0),
                "invigilators": [staff.get(i, "?") for i in (x.invigilator_staff_ids or [])],
            }
        )
    inst = Institution.objects.filter(scope_node_id=s.scope_node_id).first()
    return {
        "series": {"id": s.id, "name": s.name, "status": s.status, "exam_body": s.exam_body},
        "institution": {"id": inst.id, "name": inst.name} if inst else None,
        "classes": classes,
        "candidates": sum(1 for e in entries.values() if e.status in LIVE_ENTRY),
        "papers": [
            {
                "id": p.id,
                "code": p.paper_code,
                "title": p.title,
                "duration": p.duration_minutes,
                "entered": sum(
                    1 for e in entries.values() if e.status in LIVE_ENTRY and p.paper_code in (e.subjects or [])
                ),
                "sittings": by_paper.get(p.id, []),
            }
            for p in sorted(papers, key=lambda p: (_first_start(by_paper.get(p.id)), p.paper_code))
        ],
    }


def _first_start(sittings: list[dict[str, Any]] | None) -> dt.datetime:
    """Papers in the order they are sat; papers without an arrangement last."""
    return min((x["starts_at"] for x in sittings or []), default=dt.datetime.max.replace(tzinfo=dt.UTC))
