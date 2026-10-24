"""Remote learning (MFS LMS-101 course space, LMS-102 assignment, LMS-103 submission, LMS-104 marking, LMS-107
learner work; CR-009 phase 4).

Each class's subject has an online space, opened by its teacher of record: its learners are the class roster (kept
in step each time the space is opened — joiners added, leavers' membership ended), its teacher the owner. The
teacher posts units of notes and links, sets work with an opening time, a due time and a mark, and schedules live
lessons with the meeting link they will use (no video service is built in: the teacher gives the link of the one the
school uses).

Learners sign in with their own account and see the work set for their classes. A submission is a new version each
time and is never changed afterwards; each has a receipt (a SHA-256 of what was sent and when), and is marked late
when it arrives after the due time. Work set to close at the due time refuses late work; work that does not allow
resubmission refuses a second version. The learner says whether they used AI tools.

The teacher marks each submission with a score and feedback; marks stay with the teacher until they release them,
when learners — and their parents — see them. Parents see their child's work, due dates and released marks.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import uuid
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from django.conf import settings

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.families import portal
from syntegra.lms.models import (
    Assignment,
    CourseMember,
    CourseSpace,
    LiveClass,
    LmsContent,
    LmsUnit,
    Submission,
    SubmissionMark,
)

KINDS = {"homework": "Homework", "coursework": "Coursework", "ca_test": "Class test", "practical": "Practical"}
LATE = {"accept_flag": "Accept late work and mark it late", "close_at_due": "Close at the due time"}
AI = {"none_used": "I did not use AI tools", "used_acknowledged": "I used AI tools and say how below"}
MAX_TEXT = 20000


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.TIME_ZONE)


def _me_staff() -> uuid.UUID | None:
    from syntegra.iam.models import AppUser

    u = AppUser.objects.filter(pk=context.require().actor_id).first()
    return u.person_id if u is not None and u.person_kind == "staff" else None


def _teacher_of_record(plan_id: uuid.UUID, on: dt.date) -> uuid.UUID | None:
    from syntegra.academic import teaching
    from syntegra.academic.models import TeachingAssignment

    a = (
        teaching.current(TeachingAssignment.objects.filter(class_subject_plan_id=plan_id, role="teacher_of_record"), on)
        .order_by("-valid_from")
        .first()
    )
    return a.staff_id if a else None


def _url(value: str | None, what: str) -> str:
    v = (value or "").strip()
    p = urlparse(v)
    if p.scheme != "https" or not p.netloc:
        raise HardValidation("LMS-LINK", f"Give the {what} as a web address", "It starts with https://")
    return v[:1000]


# --------------------------------------------------------------------------- teacher: spaces
def my_classes(institution_id: uuid.UUID) -> dict[str, Any]:
    """The class-subjects the signed-in teacher teaches (the head sees every class-subject), each with its space."""
    from syntegra.academic import teaching
    from syntegra.academic.models import ClassGroup, ClassSubjectPlan, Subject, TeachingAssignment
    from syntegra.institutions.models import Institution

    ctx = context.require()
    authz.require("course:teach", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    today = dt.date.today()
    classes = {c.id: c for c in ClassGroup.objects.in_scope().filter(institution_id=inst.id, status="active")}
    plans = list(teaching._active(ClassSubjectPlan.objects.filter(class_group_id__in=list(classes)), today))
    teachers = {
        a.class_subject_plan_id: a.staff_id
        for a in teaching.current(
            TeachingAssignment.objects.filter(
                class_subject_plan_id__in=[p.id for p in plans], role="teacher_of_record"
            ),
            today,
        )
    }
    me = _me_staff()
    everyone = ctx.has("course:manage")
    plans = [p for p in plans if everyone or teachers.get(p.id) == me]
    subjects = {s.id: s.name for s in Subject.objects.filter(id__in={p.subject_id for p in plans})}
    spaces = {
        s.class_subject_plan_id: s
        for s in CourseSpace.objects.filter(class_subject_plan_id__in=[p.id for p in plans], status="active")
    }
    due: dict[uuid.UUID, int] = {}
    now = dt.datetime.now(_tz())
    for a in Assignment.objects.filter(course_space_id__in=[s.id for s in spaces.values()], status="published"):
        if a.due_at >= now:
            due[a.course_space_id] = due.get(a.course_space_id, 0) + 1
    rows = [
        {
            "plan_id": p.id,
            "class": classes[p.class_group_id].name,
            "subject": subjects.get(p.subject_id, "Subject"),
            "mine": teachers.get(p.id) == me,
            "space_id": spaces[p.id].id if p.id in spaces else None,
            "open_work": due.get(spaces[p.id].id, 0) if p.id in spaces else 0,
        }
        for p in plans
    ]
    return {"institution": {"id": inst.id, "name": inst.name},
            "rows": sorted(rows, key=lambda r: (not r["mine"], r["class"], r["subject"]))}  # fmt: skip


def open_space(plan_id: uuid.UUID) -> CourseSpace:
    """The class-subject's space, created on first use; its roster brought into step with the class."""
    from syntegra.academic.models import ClassGroup, ClassMembership, ClassSubjectPlan, Subject

    ctx = context.require()
    authz.require("course:teach", ctx)
    plan = ClassSubjectPlan.objects.filter(pk=plan_id).first()
    cls = ClassGroup.objects.in_scope().filter(pk=plan.class_group_id).first() if plan else None
    if plan is None or cls is None:
        raise NotFound("class_subject_plan", plan_id)
    today = dt.date.today()
    owner = _teacher_of_record(plan.id, today)
    if not ctx.has("course:manage") and (owner is None or owner != _me_staff()):
        raise Forbidden("The subject's teacher of record opens its online space.", code="LMS-OWN")
    if owner is None:
        raise ConflictError("LMS-TEACHER", "The subject has no teacher of record", "Assign one on the class plan.")
    subject = Subject.objects.filter(pk=plan.subject_id).first()
    roster = set(
        ClassMembership.objects.filter(class_group_id=cls.id, valid_from__lte=today)
        .exclude(valid_to__lt=today)
        .values_list("learner_id", flat=True)
    )
    with uow.command("ops", "course:teach", action="sync_course_space", record_kind="course_space") as cmd:
        space = CourseSpace.objects.filter(class_subject_plan_id=plan.id, status="active").first()
        if space is None:
            space = cmd.add(
                CourseSpace(
                    scope_node_id=cls.scope_node_id,
                    space_kind="class_subject",
                    class_subject_plan_id=plan.id,
                    title=f"{cls.name} {subject.name if subject else 'Subject'}",
                    owner_staff_id=owner,
                    storage_bytes=0,
                    status="active",
                )
            )
        elif space.owner_staff_id != owner:
            cmd.update(space, owner_staff_id=owner)
        members = list(CourseMember.objects.filter(course_space_id=space.id, valid_to__isnull=True))
        learners = {m.member_id: m for m in members if m.member_kind == "learner"}
        for lid in roster - set(learners):
            cmd.add(CourseMember(course_space_id=space.id, member_kind="learner", member_id=lid,
                                 space_role="learner", valid_from=today))  # fmt: skip
        for lid in set(learners) - roster:
            cmd.update(learners[lid], valid_to=today)
        staff = {m.member_id: m for m in members if m.member_kind == "staff"}
        if owner not in staff:
            cmd.add(CourseMember(course_space_id=space.id, member_kind="staff", member_id=owner, space_role="owner",
                                 valid_from=today))  # fmt: skip
        for sid, m in staff.items():
            if sid != owner and m.space_role == "owner":
                cmd.update(m, valid_to=today)
        return space


def _space(space_id: uuid.UUID) -> CourseSpace:
    s: CourseSpace | None = CourseSpace.objects.in_scope().filter(pk=space_id, status="active").first()
    if s is None:
        raise NotFound("course_space", space_id)
    return s


def _learners_of(space: CourseSpace) -> set[uuid.UUID]:
    return set(
        CourseMember.objects.filter(course_space_id=space.id, member_kind="learner", valid_to__isnull=True).values_list(
            "member_id", flat=True
        )
    )


def _viewer(space: CourseSpace, child: uuid.UUID | None = None) -> tuple[str, uuid.UUID | None]:
    """('teacher' | 'head' | 'learner' | 'parent', the learner id for a learner or parent). A parent with more than
    one child in the class names the ``child``."""
    ctx = context.require()
    me = portal.me_learner()
    if me is not None:
        if me["id"] in _learners_of(space):
            return "learner", me["id"]
        raise Forbidden("This class space is not one of yours.", code="LMS-OWN")
    if portal.is_parent():
        kids = {c["id"] for c in portal.children()} & _learners_of(space)
        if child in kids:
            return "parent", child
        if kids:
            return "parent", sorted(kids)[0]
        raise Forbidden("This class space is not one of your child's.", code="LMS-OWN")
    if ctx.has("course:teach") and space.owner_staff_id == _me_staff():
        return "teacher", None
    if ctx.has("course:manage"):
        return "head", None
    raise Forbidden("Only the class's teacher and its learners use this space.", code="LMS-OWN")


def _teacher(space: CourseSpace) -> None:
    if _viewer(space)[0] != "teacher":
        raise Forbidden("Only the space's teacher changes it.", code="LMS-OWN")


def space(space_id: uuid.UUID) -> dict[str, Any]:
    from syntegra.people.models import Staff

    s = _space(space_id)
    viewer, learner_id = _viewer(s)
    now = dt.datetime.now(_tz())
    units = list(LmsUnit.objects.filter(course_space_id=s.id).order_by("sort_order"))
    content: dict[uuid.UUID, list[LmsContent]] = {}
    for c in LmsContent.objects.filter(unit_id__in=[u.id for u in units]).order_by("created_at"):
        content.setdefault(c.unit_id, []).append(c)
    work = list(
        Assignment.objects.filter(course_space_id=s.id).exclude(status__in=("draft", "archived")).order_by("due_at")
    )
    if viewer in ("learner", "parent"):
        work = [a for a in work if a.opens_at <= now]
    subs: dict[uuid.UUID, int] = {}
    for a_id in (
        Submission.objects.filter(assignment_id__in=[a.id for a in work], is_draft=False)
        .values_list("assignment_id", "learner_id")
        .distinct()
    ):
        subs[a_id[0]] = subs.get(a_id[0], 0) + 1
    live = [x for x in LiveClass.objects.filter(course_space_id=s.id).order_by("starts_at")
            if x.starts_at >= now - dt.timedelta(hours=2)]  # fmt: skip
    teacher = Staff.objects.filter(pk=s.owner_staff_id).first()
    return {
        "id": s.id,
        "title": s.title,
        "viewer": viewer,
        "learner_id": learner_id,
        "teacher": f"{teacher.given_name} {teacher.family_name}" if teacher else "",
        "learners": len(_learners_of(s)),
        "units": [
            {
                "id": u.id,
                "title": u.title,
                "contents": [
                    {"kind": c.content_kind, "title": c.title, "body": c.body, "link": c.object_key}
                    for c in content.get(u.id, [])
                ],
            }
            for u in units
        ],
        "work": [
            {
                "id": a.id,
                "title": a.title,
                "kind": KINDS.get(a.assignment_kind, a.assignment_kind),
                "opens": a.opens_at,
                "due": a.due_at,
                "max_mark": a.max_mark,
                "status": a.status,
                "submitted": subs.get(a.id, 0),
                "overdue": a.due_at < now,
            }
            for a in work
        ],
        "live": [{"at": x.starts_at, "link": x.provider_room_ref} for x in live],
        "kinds": KINDS,
        "late": LATE,
    }


def add_unit(space_id: uuid.UUID, title: str) -> LmsUnit:
    s = _space(space_id)
    _teacher(s)
    title = (title or "").strip()
    if len(title) < 3:
        raise HardValidation("LMS-UNIT", "Give the unit a title", "For example: Week 3 — Quadratic equations.")
    n = LmsUnit.objects.filter(course_space_id=s.id).count()
    with uow.command("ops", "course:teach", action="add_unit", record_kind="lms_unit") as cmd:
        return cmd.add(LmsUnit(course_space_id=s.id, title=title[:300], sort_order=n + 1))


def add_item(
    unit_id: uuid.UUID, *, kind: str, title: str, body: str | None = None, link: str | None = None
) -> LmsContent:
    u = LmsUnit.objects.filter(pk=unit_id).first()
    if u is None:
        raise NotFound("lms_unit", unit_id)
    s = _space(u.course_space_id)
    _teacher(s)
    title = (title or "").strip()
    if len(title) < 3:
        raise HardValidation("LMS-ITEM", "Give it a title", "So learners know what it is.")
    if kind == "note":
        text = (body or "").strip()
        if len(text) < 10:
            raise HardValidation("LMS-ITEM", "Write the note", "At least a sentence.")
        fields: dict[str, Any] = {"body": text[:MAX_TEXT], "object_key": None}
    elif kind in ("link", "video"):
        fields = {"body": (body or "").strip()[:1000] or None, "object_key": _url(link, "link")}
    else:
        raise HardValidation("LMS-ITEM", "Choose a note or a link", "")
    with uow.command("ops", "course:teach", action="add_content", record_kind="lms_content") as cmd:
        return cmd.add(LmsContent(unit_id=u.id, content_kind=kind, title=title[:300], is_offline_pack=kind == "note",
                                  **fields))  # fmt: skip


def set_work(
    space_id: uuid.UUID,
    *,
    title: str,
    instructions: str,
    kind: str,
    opens_at: dt.datetime,
    due_at: dt.datetime,
    max_mark: str | None,
    late_policy: str,
    allow_resubmission: bool,
) -> Assignment:
    s = _space(space_id)
    _teacher(s)
    title, instructions = (title or "").strip(), (instructions or "").strip()
    if len(title) < 3:
        raise HardValidation("LMS-WORK", "Give the work a title", "For example: Exercise 4.2, questions 1–10.")
    if len(instructions) < 10:
        raise HardValidation("LMS-WORK", "Write the instructions", "Say what learners must do.")
    if kind not in KINDS or late_policy not in LATE:
        raise HardValidation("LMS-WORK", "Choose the kind of work and the late rule", "")
    now = dt.datetime.now(_tz())
    if due_at <= opens_at:
        raise HardValidation("LMS-WORK", "Check the dates", "It is due after it opens.")
    if due_at <= now:
        raise HardValidation("LMS-WORK", "The due time has passed", "Give a due time in the future.")
    mark = None
    if max_mark:
        try:
            mark = Decimal(max_mark)
        except InvalidOperation as exc:
            raise HardValidation("LMS-WORK", "The mark must be a number", "For example 20.") from exc
        if not (0 < mark <= 1000):
            raise HardValidation("LMS-WORK", "The mark must be a number", "Between 1 and 1000.")
    with uow.command("ops", "course:teach", action="set_work", record_kind="assignment") as cmd:
        return cmd.add(
            Assignment(
                scope_node_id=s.scope_node_id,
                course_space_id=s.id,
                assignment_kind=kind,
                title=title[:300],
                instructions=instructions[:MAX_TEXT],
                max_mark=mark,
                opens_at=opens_at,
                due_at=due_at,
                late_policy=late_policy,
                allow_resubmission=allow_resubmission,
                ai_policy="allowed_with_acknowledgement",
                status="published" if opens_at <= now else "scheduled",
            )
        )


def schedule_live(space_id: uuid.UUID, starts_at: dt.datetime, link: str) -> LiveClass:
    s = _space(space_id)
    _teacher(s)
    if starts_at <= dt.datetime.now(_tz()):
        raise HardValidation("LMS-LIVE", "Choose a time in the future", "Live lessons are scheduled ahead.")
    with uow.command("ops", "course:teach", action="schedule_live", record_kind="live_class") as cmd:
        return cmd.add(
            LiveClass(
                scope_node_id=s.scope_node_id,
                course_space_id=s.id,
                starts_at=starts_at,
                provider_room_ref=_url(link, "meeting link"),
                recording_consent_complete=False,
            )
        )


# --------------------------------------------------------------------------- learners and parents
def _assignment(assignment_id: uuid.UUID) -> tuple[Assignment, CourseSpace]:
    a: Assignment | None = Assignment.objects.in_scope().filter(pk=assignment_id).first()
    if a is None or a.status in ("draft", "archived"):
        raise NotFound("assignment", assignment_id)
    return a, _space(a.course_space_id)


def _released(sub_ids: list[uuid.UUID]) -> dict[uuid.UUID, SubmissionMark]:
    return {
        m.submission_id: m for m in SubmissionMark.objects.filter(submission_id__in=sub_ids, released_at__isnull=False)
    }


def work_for(learner_id: uuid.UUID) -> list[dict[str, Any]]:
    """The work set for a learner's classes that has opened, newest due first, with their latest version and mark."""
    now = dt.datetime.now(_tz())
    spaces = {
        s.id: s
        for s in CourseSpace.objects.in_scope().filter(
            id__in=list(
                CourseMember.objects.filter(
                    member_kind="learner", member_id=learner_id, valid_to__isnull=True
                ).values_list("course_space_id", flat=True)
            ),
            status="active",
        )
    }
    work = list(
        Assignment.objects.filter(course_space_id__in=list(spaces), opens_at__lte=now)
        .exclude(status__in=("draft", "archived"))
        .order_by("-due_at")
    )
    subs: dict[uuid.UUID, Submission] = {}
    for x in Submission.objects.filter(
        assignment_id__in=[a.id for a in work], learner_id=learner_id, is_draft=False
    ).order_by("version_no"):
        subs[x.assignment_id] = x
    marks = _released([x.id for x in subs.values()])
    rows = []
    for a in work:
        sub = subs.get(a.id)
        m = marks.get(sub.id) if sub else None
        rows.append(
            {
                "id": a.id,
                "title": a.title,
                "space": spaces[a.course_space_id].title,
                "space_id": a.course_space_id,
                "kind": KINDS.get(a.assignment_kind, a.assignment_kind),
                "due": a.due_at,
                "overdue": a.due_at < now and sub is None,
                "submitted_at": sub.synced_at if sub else None,
                "late": sub.is_late if sub else False,
                "score": m.score if m else None,
                "max_mark": a.max_mark,
                "feedback": m.feedback if m else None,
            }
        )
    return rows


def assignment(assignment_id: uuid.UUID, child: uuid.UUID | None = None) -> dict[str, Any]:
    a, s = _assignment(assignment_id)
    viewer, learner_id = _viewer(s, child)
    now = dt.datetime.now(_tz())
    if viewer in ("learner", "parent") and a.opens_at > now:
        raise NotFound("assignment", assignment_id)
    versions = (
        list(
            Submission.objects.filter(assignment_id=a.id, learner_id=learner_id, is_draft=False).order_by("version_no")
        )
        if learner_id
        else []
    )
    marks = _released([v.id for v in versions])
    latest = versions[-1] if versions else None
    can_submit = viewer == "learner" and (latest is None or a.allow_resubmission)
    if a.late_policy == "close_at_due" and now > a.due_at:
        can_submit = False
    return {
        "id": a.id,
        "space": {"id": s.id, "title": s.title},
        "title": a.title,
        "instructions": a.instructions,
        "kind": KINDS.get(a.assignment_kind, a.assignment_kind),
        "opens": a.opens_at,
        "due": a.due_at,
        "max_mark": a.max_mark,
        "late_policy": LATE.get(a.late_policy, a.late_policy),
        "allow_resubmission": a.allow_resubmission,
        "viewer": viewer,
        "versions": [
            {
                "no": v.version_no,
                "at": v.synced_at,
                "late": v.is_late,
                "text": v.text_body,
                "receipt": bytes(v.receipt_hash).hex()[:16].upper(),
                "ai": AI.get(v.ai_declaration, "Not declared"),
                "mark": marks.get(v.id),
            }
            for v in versions
        ],
        "can_submit": can_submit,
        "closed": a.late_policy == "close_at_due" and now > a.due_at,
        "ai_choices": AI,
    }


def submit(assignment_id: uuid.UUID, text: str, ai_declaration: str, ai_note: str | None = None) -> Submission:
    a, s = _assignment(assignment_id)
    ctx = context.require()
    authz.require("work:submit", ctx)
    viewer, learner_id = _viewer(s)
    if viewer != "learner" or learner_id is None:
        raise Forbidden("Learners hand in their own work.", code="LMS-OWN")
    body = (text or "").strip()
    if len(body) < 2:
        raise HardValidation("LMS-SUBMIT", "Write your answer", "The answer is empty.")
    if len(body) > MAX_TEXT:
        raise HardValidation("LMS-SUBMIT", "The answer is too long", f"At most {MAX_TEXT:,} characters.")
    if ai_declaration not in AI:
        raise HardValidation("LMS-SUBMIT", "Say whether you used AI tools", "Choose one of the two.")
    note = (ai_note or "").strip()
    if ai_declaration == "used_acknowledged":
        if len(note) < 10:
            raise HardValidation("LMS-SUBMIT", "Say how you used AI tools", "A sentence is enough.")
        body = f"{body}\n\n[How I used AI tools] {note[:500]}"
    now = utcnow()
    local = now.astimezone(_tz())
    if local < a.opens_at.astimezone(_tz()):
        raise ConflictError(
            "LMS-CLOSED", "This work has not opened yet", f"It opens {a.opens_at.astimezone(_tz()):%d %B at %H:%M}."
        )
    late = now > a.due_at
    if late and a.late_policy == "close_at_due":
        raise ConflictError("LMS-CLOSED", "The due time has passed", "This work closed at the due time.")
    with uow.command("ops", "work:submit", action="submit_work", record_kind="submission") as cmd:
        cmd.lock(Assignment, a.id)
        prev = (
            Submission.objects.filter(assignment_id=a.id, learner_id=learner_id, is_draft=False)
            .order_by("-version_no")
            .first()
        )
        if prev is not None and not a.allow_resubmission:
            raise ConflictError("LMS-ONCE", "You have already handed this in", "This work takes one submission.")
        version = (prev.version_no if prev else 0) + 1
        receipt = hashlib.sha256(f"{a.id}|{learner_id}|{version}|{now.isoformat()}|".encode() + body.encode()).digest()
        return cmd.add(
            Submission(
                assignment_id=a.id,
                learner_id=learner_id,
                version_no=version,
                is_draft=False,
                text_body=body,
                synced_at=now,
                is_late=late,
                receipt_hash=receipt,
                ai_declaration=ai_declaration,
                source="web",
            )
        )


# --------------------------------------------------------------------------- marking
def marking(assignment_id: uuid.UUID) -> dict[str, Any]:
    from syntegra.learners.models import Learner

    a, s = _assignment(assignment_id)
    viewer, _ = _viewer(s)
    if viewer not in ("teacher", "head"):
        raise Forbidden("Marking is for the class's teacher.", code="LMS-OWN")
    roster = _learners_of(s)
    latest: dict[uuid.UUID, Submission] = {}
    for x in Submission.objects.filter(assignment_id=a.id, is_draft=False).order_by("version_no"):
        latest[x.learner_id] = x
    marks = {
        m.submission_id: m for m in SubmissionMark.objects.filter(submission_id__in=[x.id for x in latest.values()])
    }
    learners = {lr.id: lr for lr in Learner.objects.filter(id__in=roster | set(latest))}
    rows = []
    for lid in roster | set(latest):
        lr = learners.get(lid)
        sub = latest.get(lid)
        m = marks.get(sub.id) if sub else None
        rows.append(
            {
                "learner_id": lid,
                "name": f"{lr.legal_family_name}, {lr.legal_given_name}" if lr else "Learner",
                "submission": sub,
                "text": sub.text_body if sub else None,
                "late": sub.is_late if sub else False,
                "version": sub.version_no if sub else None,
                "ai": AI.get(sub.ai_declaration, "Not declared") if sub else None,
                "score": m.score if m else None,
                "feedback": m.feedback if m else "",
                "released": bool(m and m.released_at),
            }
        )
    rows.sort(key=lambda r: (r["submission"] is None, r["name"]))
    marked = sum(1 for r in rows if r["score"] is not None)
    return {
        "assignment": {"id": a.id, "title": a.title, "due": a.due_at, "max_mark": a.max_mark, "status": a.status},
        "space": {"id": s.id, "title": s.title},
        "rows": rows,
        "submitted": len(latest),
        "marked": marked,
        "unreleased": sum(1 for r in rows if r["score"] is not None and not r["released"]),
        "can_mark": viewer == "teacher",
    }


def mark(submission_id: uuid.UUID, score: str, feedback: str | None) -> SubmissionMark:
    sub = Submission.objects.filter(pk=submission_id).first()
    if sub is None:
        raise NotFound("submission", submission_id)
    a, s = _assignment(sub.assignment_id)
    _teacher(s)
    latest = (
        Submission.objects.filter(assignment_id=a.id, learner_id=sub.learner_id, is_draft=False)
        .order_by("-version_no")
        .first()
    )
    if latest is None or latest.id != sub.id:
        raise ConflictError("LMS-VERSION", "A newer version has been handed in", "Mark the latest version.")
    try:
        value = Decimal(score)
    except InvalidOperation as exc:
        raise HardValidation("LMS-MARK", "The score must be a number", "For example 14.") from exc
    if value < 0 or (a.max_mark is not None and value > a.max_mark):
        raise HardValidation("LMS-MARK", "Check the score", f"Between 0 and {a.max_mark}.")
    text = (feedback or "").strip()[:4000] or None
    me = _me_staff()
    with uow.command("ops", "course:teach", action="mark_work", record_kind="submission_mark") as cmd:
        m = SubmissionMark.objects.filter(submission_id=sub.id).first()
        if m is None:
            return cmd.add(SubmissionMark(submission_id=sub.id, marker_staff_id=me, score=value, feedback=text,
                                          is_auto_marked=False))  # fmt: skip
        updated: SubmissionMark = cmd.update(m, score=value, feedback=text, marker_staff_id=me)
        return updated


def release(assignment_id: uuid.UUID) -> int:
    """Release the marks given so far: learners and their parents see them from now."""
    a, s = _assignment(assignment_id)
    _teacher(s)
    subs = list(Submission.objects.filter(assignment_id=a.id).values_list("id", flat=True))
    pending = list(SubmissionMark.objects.filter(submission_id__in=subs, released_at__isnull=True))
    if not pending:
        raise ConflictError("LMS-RELEASE", "There are no new marks to release", "Mark some work first.")
    now = utcnow()
    with uow.command("ops", "course:teach", action="release_marks", record_kind="assignment") as cmd:
        for m in pending:
            cmd.update(m, released_at=now)
        cmd.update(a, status="released" if a.due_at < now else a.status, release_at=now)
        return len(pending)
