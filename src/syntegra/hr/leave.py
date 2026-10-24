"""Leave management (FR-HRM-05/06): entitlements from policy, balances the database refuses to over-book,
four-eyes approval, and the staff absence that starts the cover process (G8)."""

from __future__ import annotations

import datetime as dt
import uuid
from decimal import Decimal

from django.db import DatabaseError, transaction

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.hr.domain import leave as rules
from syntegra.hr.establishment import active_record
from syntegra.hr.models import Cadre, LeaveBalance, LeavePolicy, LeaveRequest
from syntegra.people.models import Staff, StaffAbsence


def _policies() -> list[rules.Policy]:
    rows = LeavePolicy.objects.filter(status="published")
    latest: dict[str, LeavePolicy] = {}
    for p in rows.order_by("code", "-version"):
        latest.setdefault(p.code, p)
    return [
        rules.Policy(
            p.code,
            p.leave_type,
            p.cadre_code,
            p.grade_level_min,
            p.grade_level_max,
            Decimal(p.days_per_year),
            p.day_basis,
            Decimal(p.carry_over_max),
        )
        for p in latest.values()
    ]


def _policy_for(staff_id: uuid.UUID, leave_type: str) -> tuple[rules.Policy, int]:
    rec = active_record(staff_id)
    cadre = Cadre.objects.get(pk=rec.cadre_id)
    pol = rules.select_policy(_policies(), leave_type, cadre.code, rec.grade_level)
    if pol is None:
        raise HardValidation(
            "HR-LEAVE-POLICY", "No leave policy", f"No {leave_type} entitlement for {cadre.code} GL {rec.grade_level}."
        )
    return pol, rec.grade_level


def balance(staff_id: uuid.UUID, leave_type: str, year: int, cmd: uow.Command | None = None) -> LeaveBalance:
    """The staff member's balance for the year, created from policy on first use (with carry-over)."""
    b: LeaveBalance | None = LeaveBalance.objects.filter(
        staff_id=staff_id, leave_type=leave_type, leave_year=year
    ).first()
    if b is not None:
        return b
    pol, _ = _policy_for(staff_id, leave_type)
    prev = LeaveBalance.objects.filter(staff_id=staff_id, leave_type=leave_type, leave_year=year - 1).first()
    carried = Decimal(0)
    if prev is not None:
        carried = min(pol.carry_over_max, rules.available(prev.entitled, prev.carried_over, prev.taken, prev.pending))
    b = LeaveBalance(
        staff_id=staff_id,
        leave_type=leave_type,
        leave_year=year,
        entitled=pol.days_per_year,
        carried_over=max(carried, Decimal(0)),
        taken=0,
        pending=0,
    )
    if cmd is not None:
        return cmd.add(b)
    with uow.command("ops", None, action="open_balance", record_kind="leave_balance") as c:
        return c.add(b)


def _own_staff_id() -> uuid.UUID | None:
    ctx = context.require()
    s = Staff.objects.filter(user_id=ctx.actor_id).first()
    return s.id if s else None


def request_leave(
    staff_id: uuid.UUID,
    leave_type: str,
    starts_on: dt.date,
    ends_on: dt.date,
    *,
    note: str | None = None,
    holidays: list[dt.date] | None = None,
) -> LeaveRequest:
    ctx = context.require()
    if staff_id != _own_staff_id():
        authz.require("hr:leave_manage", ctx)  # on behalf of someone else
    else:
        authz.require("hr:leave_request", ctx)
    if ends_on < starts_on:
        raise HardValidation("HR-LEAVE-DATES", "Leave ends before it starts", "")
    pol, _ = _policy_for(staff_id, leave_type)
    days = rules.leave_days(starts_on, ends_on, pol.day_basis, holidays or [])
    if days <= 0:
        raise HardValidation("HR-LEAVE-DAYS", "No working days in the period", "")
    rec = active_record(staff_id)
    with uow.command("ops", None, action="request", record_kind="leave_request") as cmd:
        b = balance(staff_id, leave_type, starts_on.year, cmd)
        b = cmd.lock(LeaveBalance, b.id)
        if rules.available(b.entitled, b.carried_over, b.taken, b.pending) < days:
            raise HardValidation(
                "HR-LEAVE-BALANCE",
                "Not enough leave left",
                f"{days} day(s) requested; "
                f"{rules.available(b.entitled, b.carried_over, b.taken, b.pending)} available.",
            )
        try:
            with transaction.atomic(using=cmd.alias):
                cmd.update(b, pending=b.pending + days)  # CHECK within_entitlement guards concurrent requests
        except DatabaseError as exc:
            raise HardValidation(
                "HR-LEAVE-BALANCE", "Not enough leave left", "Another request used the balance."
            ) from exc
        return cmd.add(
            LeaveRequest(
                scope_node_id=rec.scope_node_id,
                staff_id=staff_id,
                staff_post_id=rec.staff_post_id,
                leave_type=leave_type,
                starts_on=starts_on,
                ends_on=ends_on,
                days=days,
                note=note,
                requested_by=ctx.actor_id,
                status="requested",
            )
        )


def decide_leave(request_id: uuid.UUID, approve: bool, *, relief_staff_id: uuid.UUID | None = None) -> LeaveRequest:
    ctx = context.require()
    authz.require("hr:leave_approve", ctx)
    with uow.command("ops", None, action="approve" if approve else "reject", record_kind="leave_request") as cmd:
        lr = cmd.lock(LeaveRequest, request_id)
        if lr.status != "requested":
            raise ConflictError("HR-LEAVE-STATE", "Leave already decided", f"It is {lr.status}.")
        if lr.requested_by == ctx.actor_id or lr.staff_id == _own_staff_id():
            raise Forbidden("You cannot approve your own leave.", code="FOUR-EYES")
        b = (
            LeaveBalance.unscoped.using(cmd.alias)
            .select_for_update()
            .get(tenant_id=ctx.tenant_id, staff_id=lr.staff_id, leave_type=lr.leave_type, leave_year=lr.starts_on.year)
        )
        if not approve:
            cmd.update(b, pending=b.pending - lr.days)
            return cmd.update(lr, status="rejected", approver_id=ctx.actor_id, decided_at=utcnow())
        cmd.update(b, pending=b.pending - lr.days, taken=b.taken + lr.days)
        absence = cmd.add(
            StaffAbsence(
                scope_node_id=lr.scope_node_id,
                staff_id=lr.staff_id,
                staff_post_id=lr.staff_post_id,
                absence_type=lr.leave_type,
                is_planned=True,
                approved_by=ctx.actor_id,
                status="approved",
                starts_at=dt.datetime.combine(lr.starts_on, dt.time(0, 0), tzinfo=dt.UTC),
                ends_at=dt.datetime.combine(lr.ends_on, dt.time(23, 59), tzinfo=dt.UTC),
            )
        )
        cmd.update(
            lr,
            status="approved",
            approver_id=ctx.actor_id,
            decided_at=utcnow(),
            absence_id=absence.id,
            relief_staff_id=relief_staff_id,
        )
        cmd.emit(
            "HR.LEAVE_APPROVED",
            aggregate_id=lr.id,
            scope_node_id=lr.scope_node_id,
            payload={
                "leave_request_id": lr.id,
                "staff_id": lr.staff_id,
                "starts_on": lr.starts_on,
                "ends_on": lr.ends_on,
            },
        )
        cmd.emit(
            "STF.ABSENCE_RECORDED",
            aggregate_id=absence.id,
            aggregate_kind="staff_absence",
            scope_node_id=lr.scope_node_id,
            payload=_absence_payload(absence),
        )
        return lr


def _absence_payload(a: StaffAbsence) -> dict[str, object]:
    from syntegra.core import catalog

    spec = catalog.event("STF.ABSENCE_RECORDED").get("payload") or {}
    full = {"staff_absence_id": a.id, "staff_id": a.staff_id, "starts_at": a.starts_at, "ends_at": a.ends_at}
    return {k: v for k, v in full.items() if k in spec}


def cancel_leave(request_id: uuid.UUID) -> LeaveRequest:
    ctx = context.require()
    with uow.command("ops", None, action="cancel", record_kind="leave_request") as cmd:
        lr = cmd.lock(LeaveRequest, request_id)
        if lr.staff_id != _own_staff_id():
            authz.require("hr:leave_manage", ctx)
        if lr.status not in ("requested", "approved") or (lr.status == "approved" and lr.starts_on <= dt.date.today()):
            raise ConflictError("HR-LEAVE-CANCEL", "Leave can no longer be cancelled", "")
        b = (
            LeaveBalance.unscoped.using(cmd.alias)
            .select_for_update()
            .get(tenant_id=ctx.tenant_id, staff_id=lr.staff_id, leave_type=lr.leave_type, leave_year=lr.starts_on.year)
        )
        if lr.status == "requested":
            cmd.update(b, pending=b.pending - lr.days)
        else:
            cmd.update(b, taken=b.taken - lr.days)
            if lr.absence_id:
                a = cmd.lock(StaffAbsence, lr.absence_id)
                cmd.update(a, status="cancelled")
        return cmd.update(lr, status="cancelled")


def get(request_id: uuid.UUID) -> LeaveRequest:
    lr: LeaveRequest | None = LeaveRequest.objects.in_scope().filter(pk=request_id).first()
    if lr is None:
        raise NotFound("leave request", request_id)
    return lr
