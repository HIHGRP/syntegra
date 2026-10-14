"""Attendance services (MFS §12, FR-ATT-*): registers, idempotent (offline) mark submission, corrections, rates.

* One register per class, kind, date (and lesson) — enforced by ``uq_attendance_register_…``.
* Marks carry the client's ``client_op_id``: a replayed offline sync is accepted and changes nothing.
* Only learners in the class on the session date can be marked; a register is complete only when every
  member has a mark. Submitting after the deadline marks the register *late*.
* A submitted mark is corrected, not overwritten silently: the change is audited with its reason.
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any

from django.db.models import Q

from syntegra.academic import services as academic
from syntegra.academic.models import ClassGroup, ClassMembership
from syntegra.attendance.domain import rates
from syntegra.attendance.models import AttendanceMark, AttendanceRegister
from syntegra.core import authz, context, policy, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.core.fields import utcnow

DEFAULT_DUE = {"am": dt.time(8, 30), "pm": dt.time(13, 30), "daily": dt.time(9, 0)}


@dataclass
class Mark:
    learner_id: uuid.UUID
    code: str
    minutes_late: int | None = None
    client_op_id: uuid.UUID | None = None
    reason_source: str | None = None


def open_register(class_id: uuid.UUID, session_date: dt.date, kind: str = "daily") -> AttendanceRegister:
    """Return the class's register for the date, creating it when first opened (idempotent)."""
    ctx = context.require()
    authz.require("attendance:mark", ctx)
    cls = ClassGroup.objects.filter(pk=class_id).first()
    if cls is None:
        raise NotFound("class", class_id)
    authz.require_scope(cls.scope_node_id, ctx)
    existing: AttendanceRegister | None = AttendanceRegister.objects.filter(
        class_group_id=cls.id, register_kind=kind, session_date=session_date, lesson_occurrence__isnull=True
    ).first()
    if existing:
        return existing
    due = dt.datetime.combine(session_date, DEFAULT_DUE.get(kind, dt.time(9, 0)), tzinfo=dt.UTC) - dt.timedelta(hours=1)
    with uow.command("ops", None, action="open", record_kind="attendance_register") as cmd:
        return cmd.add(
            AttendanceRegister(
                scope_node_id=cls.scope_node_id,
                class_group_id=cls.id,
                register_kind=kind,
                session_date=session_date,
                due_at=due,
                status="due",
            )
        )


def submit(
    register_id: uuid.UUID,
    marks: list[Mark],
    *,
    device_captured_at: dt.datetime | None = None,
    if_match: int | None = None,
    source: str = "teacher",
) -> dict[str, Any]:
    ctx = context.require()
    errors: list[dict[str, Any]] = []
    for i, m in enumerate(marks):
        errors += [{"field": f"marks[{i}].code", "message": e} for e in rates.validate_mark(m.code, m.minutes_late)]
    if errors:
        raise HardValidation("ATT-MARKS", "Some marks need attention", errors=errors)
    with uow.command("ops", "attendance:mark", action="submit", record_kind="attendance_register") as cmd:
        reg = cmd.lock(AttendanceRegister, register_id, expected_version=if_match)
        cmd.record_id = reg.id
        roster = {m.learner_id: m for m in academic.members(reg.class_group_id, reg.session_date)}
        unknown = [str(m.learner_id) for m in marks if m.learner_id not in roster]
        if unknown:
            raise HardValidation(
                "ATT-NOT-IN-CLASS",
                "Learner not in this class",
                f"{len(unknown)} learner(s) are not members of the class on {reg.session_date}.",
                [{"field": "learner_id", "message": u} for u in unknown],
            )
        existing = {
            m.learner_id: m
            for m in AttendanceMark.unscoped.using(cmd.alias).filter(
                tenant_id=ctx.tenant_id, register_id=reg.id, session_date=reg.session_date
            )
        }
        created = replayed = corrected = 0
        for m in marks:
            cur = existing.get(m.learner_id)
            if cur is not None:
                if m.client_op_id and cur.client_op_id == m.client_op_id:
                    replayed += 1  # idempotent offline replay
                    continue
                if cur.code != m.code or (cur.minutes_late or None) != (m.minutes_late or None):
                    if reg.status in ("submitted", "late", "corrected"):
                        authz.require("attendance:correct", ctx)
                    cmd.update(
                        cur,
                        code=m.code,
                        minutes_late=m.minutes_late,
                        recorded_by=ctx.actor_id,
                        client_op_id=m.client_op_id,
                        reason_source=m.reason_source or "teacher",
                    )
                    corrected += 1
                continue
            mark = AttendanceMark(
                register_id=reg.id,
                learner_id=m.learner_id,
                enrolment_id=roster[m.learner_id].enrolment_id,
                session_date=reg.session_date,
                code=m.code,
                minutes_late=m.minutes_late,
                reason_source=m.reason_source,
                recorded_by=ctx.actor_id or uuid.UUID(int=0),
                source=source,
                client_op_id=m.client_op_id,
                device_captured_at=device_captured_at,
            )
            cmd.add(mark)
            existing[m.learner_id] = mark
            created += 1
        complete = set(roster) <= set(existing)
        now = utcnow()
        was_submitted = reg.status in ("submitted", "late", "corrected")
        if complete:
            status = (
                "corrected"
                if was_submitted and corrected
                else (reg.status if was_submitted else ("late" if now > reg.due_at else "submitted"))
            )
            cmd.update(
                reg,
                status=status,
                submitted_at=reg.submitted_at or now,
                marks_count=len(existing),
                taken_by_staff_id=reg.taken_by_staff_id,
                device_captured_at=device_captured_at,
            )
            if not was_submitted:
                cmd.emit(
                    "ATT.REGISTER_SUBMITTED",
                    aggregate_id=reg.id,
                    scope_node_id=reg.scope_node_id,
                    payload={
                        "attendance_register_id": reg.id,
                        "class_group_id": reg.class_group_id,
                        "session_date": reg.session_date,
                    },
                )
        else:
            cmd.update(reg, status="in_progress", marks_count=len(existing))
        if not (created or corrected):
            cmd.audited = False  # pure replay: nothing changed, nothing to audit
        return {
            "register_id": reg.id,
            "status": reg.status,
            "created": created,
            "corrected": corrected,
            "replayed": replayed,
            "missing": len(set(roster) - set(existing)),
            "row_version": reg.row_version,
        }


def register_view(register_id: uuid.UUID) -> dict[str, Any]:
    reg = AttendanceRegister.objects.in_scope().filter(pk=register_id).first()
    if reg is None:
        raise NotFound("attendance register", register_id)
    roster = academic.members(reg.class_group_id, reg.session_date)
    marks = {m.learner_id: m for m in AttendanceMark.objects.filter(register_id=reg.id, session_date=reg.session_date)}
    return {"register": reg, "roster": roster, "marks": marks}


def learner_summary(learner_id: uuid.UUID, start: dt.date, end: dt.date) -> dict[str, Any]:
    """Attendance rate for a learner with the effective persistent/severe thresholds from policy."""
    ctx = context.require()
    authz.require("attendance:view", ctx)
    codes = list(
        AttendanceMark.objects.filter(
            learner_id=learner_id, session_date__gte=start, session_date__lte=end
        ).values_list("code", flat=True)
    )
    s = rates.summarise(codes)
    flags: dict[str, bool | None] = {}
    m = ClassMembership.objects.filter(learner_id=learner_id).order_by("-valid_from").first()
    scope = ClassGroup.objects.get(pk=m.class_group_id).scope_node_id if m else ctx.scope_node_id
    for key in ("ATT-PERSISTENT", "ATT-SEVERE"):
        rule = policy.effective_rule(key, scope) if scope else None
        flags[key] = bool(rule.evaluate({"rate": s.rate})) if rule and s.rate is not None else None
    return {
        "learner_id": learner_id,
        "from": start,
        "to": end,
        "possible": s.possible,
        "attended": s.attended,
        "authorised_absence": s.authorised_absence,
        "unauthorised_absence": s.unauthorised_absence,
        "late": s.late,
        "rate": s.rate,
        "flags": flags,
    }


def missing_registers(on: dt.date) -> list[ClassGroup]:
    """Classes in scope with no submitted daily register for the date (Register Agent nudges)."""
    done = (
        AttendanceRegister.objects.filter(session_date=on)
        .filter(Q(status="submitted") | Q(status="late") | Q(status="corrected"))
        .values("class_group_id")
    )
    return list(ClassGroup.objects.in_scope().filter(status="active").exclude(id__in=done))


def class_rate(class_id: uuid.UUID, start: dt.date, end: dt.date) -> float | None:
    if not ClassGroup.objects.in_scope().filter(pk=class_id).exists():
        raise ConflictError("ATT-SCOPE", "Class not visible", "The class is outside your scope.")
    regs = AttendanceRegister.objects.filter(class_group_id=class_id, session_date__gte=start, session_date__lte=end)
    codes = AttendanceMark.objects.filter(
        register_id__in=regs.values("id"), session_date__gte=start, session_date__lte=end
    ).values_list("code", flat=True)
    return rates.summarise(codes).rate
