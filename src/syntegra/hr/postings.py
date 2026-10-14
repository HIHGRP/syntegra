"""Postings, transfers and separations — the HR events that move people across the ecosystem (FR-HRM-04/09).

Integration (CR-001): a posting or separation changes four other parts of the CEDA in the same flow —
IAM (role grants follow the posting, access ends at separation), the staff register (posts), academic
(teaching assignments of the old post end) and the coverage engine (G9 impact before, gaps re-evaluated after).
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.academic.models import ClassGroup, ClassSubjectPlan, TeachingAssignment
from syntegra.core import authz, context, uow
from syntegra.core.context import Context
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.hr.establishment import ACTIVE, scale_point
from syntegra.hr.models import Cadre, EmploymentRecord, Position, Separation, StaffPosting
from syntegra.iam.models import AppUser, RoleGrant, UserSession
from syntegra.institutions.models import Institution
from syntegra.people.models import Staff, StaffPost


# --------------------------------------------------------------------------- coverage impact (G9)
def coverage_impact(staff_post_id: uuid.UUID | None, on: dt.date | None = None) -> dict[str, Any]:
    """Class-subjects the post is teacher of record for — they lose their teacher when the post ends."""
    if staff_post_id is None:
        return {"class_subjects": [], "count": 0}
    on = on or dt.date.today()
    tas = list(
        TeachingAssignment.unscoped.using(_ops())
        .filter(staff_post_id=staff_post_id, role="teacher_of_record", valid_from__lte=on)
        .exclude(valid_to__lt=on)
    )
    rows = []
    for ta in tas:
        plan = ClassSubjectPlan.unscoped.using(_ops()).filter(pk=ta.class_subject_plan_id).first()
        cls = ClassGroup.unscoped.using(_ops()).filter(pk=plan.class_group_id).first() if plan else None
        rows.append(
            {
                "teaching_assignment_id": str(ta.id),
                "class_subject_plan_id": str(ta.class_subject_plan_id),
                "class": cls.name if cls else None,
                "institution_id": str(cls.institution_id) if cls else None,
            }
        )
    return {"class_subjects": rows, "count": len(rows)}


def _ops() -> str:
    from syntegra.core.zones import current_alias

    return current_alias("ops")


# --------------------------------------------------------------------------- posting orders
def request_posting(
    staff_id: uuid.UUID, to_position_id: uuid.UUID, *, posting_kind: str, reason: str, effective_on: dt.date
) -> StaffPosting:
    ctx = context.require()
    authz.require("hr:posting_request", ctx)
    pos = Position.objects.filter(pk=to_position_id, status="approved").first()
    if pos is None:
        raise NotFound("approved position", to_position_id)
    if EmploymentRecord.objects.filter(position_id=pos.id, status__in=ACTIVE).exists():
        raise ConflictError("HR-POSITION-FILLED", "Receiving position is filled", pos.position_code)
    current = (
        EmploymentRecord.objects.filter(staff_id=staff_id, status__in=ACTIVE)
        .order_by("-present_appointment_on")
        .first()
    )
    if current is None and posting_kind != "first_posting":
        raise HardValidation("HR-NO-POST", "No current post", "Use a first posting for a new appointee.")
    if current is not None:
        authz.require_scope(current.scope_node_id, ctx)  # the sending side (or a higher level) raises the order
        if not pos.grade_level_min <= current.grade_level <= pos.grade_level_max:
            raise HardValidation(
                "HR-GRADE-POSITION",
                "Grade outside the receiving position's band",
                f"{pos.position_code} is GL {pos.grade_level_min}–{pos.grade_level_max}.",
            )
    impact = coverage_impact(current.staff_post_id if current else None, effective_on)
    with uow.command("registry", None, action="request", record_kind="staff_posting", reason=reason) as cmd:
        n = StaffPosting.objects.count() + 1
        return cmd.add(
            StaffPosting(
                scope_node_id=current.scope_node_id if current else pos.scope_node_id,
                order_number=f"PO-{effective_on:%Y}-{n:06d}",
                staff_id=staff_id,
                from_staff_post_id=current.staff_post_id if current else None,
                to_position_id=pos.id,
                to_institution_id=pos.institution_id,
                posting_kind=posting_kind,
                reason=reason,
                effective_on=effective_on,
                coverage_impact=impact,
                requested_by_id=ctx.actor_id,
                status="submitted",
            )
        )


def approve_posting(posting_id: uuid.UUID, *, approve: bool = True, note: str | None = None) -> StaffPosting:
    ctx = context.require()
    authz.require("hr:posting_approve", ctx)
    with uow.command(
        "registry", None, action="approve" if approve else "reject", record_kind="staff_posting", reason=note
    ) as cmd:
        p = cmd.lock(StaffPosting, posting_id)
        if p.status != "submitted":
            raise ConflictError("HR-POSTING-STATE", "Posting not awaiting approval", f"It is {p.status}.")
        if p.requested_by_id == ctx.actor_id:
            raise Forbidden("The person who raised the posting order cannot approve it.", code="FOUR-EYES")
        if approve and p.coverage_impact and p.coverage_impact.get("count") and not note:
            raise HardValidation(
                "HR-G9",
                "Classes would lose their teacher",
                f"{p.coverage_impact['count']} class-subject(s) need a handover plan (G9); "
                "record it in the approval note.",
            )
        cmd.update(p, status="approved" if approve else "rejected", approved_by_id=ctx.actor_id)
        if approve:
            cmd.emit(
                "HR.POSTING_APPROVED",
                aggregate_id=p.id,
                payload={
                    "staff_posting_id": p.id,
                    "staff_id": p.staff_id,
                    "to_position_id": p.to_position_id,
                    "effective_on": p.effective_on,
                },
            )
        return p


def make_effective(posting_id: uuid.UUID) -> StaffPosting:
    """Old post ends, new post fills the position, role grants move, teaching assignments end, coverage re-runs."""
    ctx = context.require()
    authz.require("hr:posting_approve", ctx)
    old_inst: uuid.UUID | None = None
    with uow.command("registry", None, action="effective", record_kind="staff_posting") as cmd:
        p = cmd.lock(StaffPosting, posting_id)
        if p.status != "approved":
            raise ConflictError("HR-POSTING-STATE", "Posting not approved", f"It is {p.status}.")
        pos = cmd.lock(Position, p.to_position_id)
        staff = Staff.unscoped.using(cmd.alias).get(pk=p.staff_id)
        old_rec = None
        if p.from_staff_post_id:
            old_post = cmd.lock(StaffPost, p.from_staff_post_id)
            old_inst = old_post.institution_id
            cmd.update(old_post, valid_to=p.effective_on - dt.timedelta(days=1), leaving_reason="transferred")
            old_rec = (
                EmploymentRecord.unscoped.using(cmd.alias).select_for_update().filter(staff_post_id=old_post.id).first()
            )
            if old_rec is not None:
                cmd.update(old_rec, status="separated")
        c = Cadre.unscoped.using(cmd.alias).get(pk=pos.cadre_id)
        grade = old_rec.grade_level if old_rec else pos.grade_level_min
        step = old_rec.step if old_rec else 1
        structure = old_rec.salary_structure_id if old_rec else None
        if structure is None:
            from syntegra.hr.establishment import current_structure

            structure = current_structure(c.salary_structure_code).id
        scale_point(structure, grade, step)
        new_post = cmd.add(
            StaffPost(
                scope_node_id=pos.scope_node_id,
                staff_id=staff.id,
                institution_id=pos.institution_id,
                job_title=pos.title,
                staff_category=pos.staff_category,
                grade_step=f"GL{grade:02d}/{step:02d}",
                contract="permanent",
                fte=1,
                employer_scope_id=pos.employer_scope_id,
                valid_from=p.effective_on,
            )
        )
        cmd.add(
            EmploymentRecord(
                scope_node_id=pos.scope_node_id,
                staff_post_id=new_post.id,
                staff_id=staff.id,
                position_id=pos.id,
                cadre_id=c.id,
                employer_scope_id=pos.employer_scope_id,
                appointment_type="transfer_of_service"
                if old_rec and old_rec.employer_scope_id != pos.employer_scope_id
                else (old_rec.appointment_type if old_rec else "first_appointment"),
                first_appointment_on=old_rec.first_appointment_on if old_rec else p.effective_on,
                present_appointment_on=old_rec.present_appointment_on if old_rec else p.effective_on,
                confirmation_due_on=old_rec.confirmation_due_on if old_rec else None,
                confirmed_on=old_rec.confirmed_on if old_rec else None,
                salary_structure_id=structure,
                grade_level=grade,
                step=step,
                last_promotion_on=old_rec.last_promotion_on if old_rec else None,
                retirement_due_on=old_rec.retirement_due_on if old_rec else None,
                retirement_basis=old_rec.retirement_basis if old_rec else None,
                status=old_rec.status
                if old_rec and old_rec.status != "separated"
                else "confirmed"
                if old_rec
                else "probation",
            )
        )
        cmd.update(p, status="effective", new_staff_post_id=new_post.id)
        moved = _move_grants(cmd, staff, old_inst, pos.institution_id, p.effective_on)
        cmd.note("role_grants_moved", None, moved)
        cmd.record_id = p.id
        cmd.emit(
            "HR.POSTING_EFFECTIVE",
            aggregate_id=p.id,
            payload={"staff_posting_id": p.id, "staff_id": staff.id, "new_staff_post_id": new_post.id},
        )
    if p.from_staff_post_id:
        _end_teaching(p.from_staff_post_id, p.effective_on - dt.timedelta(days=1), ctx)
        if old_inst:
            _reevaluate_coverage(old_inst, ctx, p.effective_on)
    return p


def _institution_node(institution_id: uuid.UUID | None) -> uuid.UUID | None:
    if institution_id is None:
        return None
    inst = Institution.objects.filter(pk=institution_id).first()
    return inst.scope_node_id if inst else None


def _move_grants(
    cmd: uow.Command, staff: Staff, from_inst: uuid.UUID | None, to_inst: uuid.UUID | None, on: dt.date
) -> list[dict[str, str]]:
    """Role grants held at the old institution end; the same roles are granted at the new institution."""
    if staff.user_id is None:
        return []
    old_node, new_node = _institution_node(from_inst), _institution_node(to_inst)
    moved: list[dict[str, str]] = []
    if old_node is None:
        return moved
    for g in (
        RoleGrant.unscoped.using(cmd.alias)
        .select_for_update()
        .filter(tenant_id=cmd.ctx.state_tenant_id, user_id=staff.user_id, scope_id=old_node, status="active")
    ):
        cmd.update(g, status="inactive", valid_to=on - dt.timedelta(days=1))
        if new_node is not None:
            ng = cmd.add(
                RoleGrant(
                    user_id=staff.user_id,
                    role_id=g.role_id,
                    scope_id=new_node,
                    clearance_cap=g.clearance_cap,
                    granted_by_id=cmd.ctx.actor_id,
                    status="active",
                    valid_from=on,
                )
            )
            moved.append({"from_grant": str(g.id), "to_grant": str(ng.id)})
    return moved


def _end_teaching(staff_post_id: uuid.UUID, last_day: dt.date, ctx: Context) -> int:
    n = 0
    with uow.command("ops", None, action="end_assignments", record_kind="staff_post", ctx=ctx) as cmd:
        cmd.record_id = staff_post_id
        for ta in (
            TeachingAssignment.unscoped.using(cmd.alias)
            .select_for_update()
            .filter(tenant_id=ctx.tenant_id, staff_post_id=staff_post_id, valid_to__isnull=True)
        ):
            cmd.update(ta, valid_to=max(last_day, ta.valid_from))
            n += 1
        if not n:
            cmd.audited = False
    return n


def _reevaluate_coverage(institution_id: uuid.UUID, ctx: Context, first_day_without: dt.date) -> None:
    """Run the coverage engine for the sending institution as the HR system job, as of the first day without
    the teacher (G9: the gap is visible — and owned — before the teacher actually leaves)."""
    from syntegra.curriculum import services as coverage

    job = ctx.with_(actor_kind="system", permissions=frozenset({"*"}), scope_ids=None, clearance="special")
    with context.use(job):
        coverage.evaluate_institution(institution_id, on=first_day_without)


# --------------------------------------------------------------------------- separation
def record_separation(
    staff_post_id: uuid.UUID,
    separation_kind: str,
    *,
    effective_on: dt.date,
    notice_on: dt.date | None = None,
    checklist: dict[str, Any] | None = None,
) -> Separation:
    """Exit from a post. Access ends automatically; classes lose their teacher of record at once (G9)."""
    ctx = context.require()
    authz.require("hr:separate", ctx)
    impact = coverage_impact(staff_post_id, effective_on)
    with uow.command("registry", None, action="separate", record_kind="separation") as cmd:
        post = cmd.lock(StaffPost, staff_post_id)
        if post.valid_to is not None and post.valid_to < effective_on:
            raise ConflictError("HR-POST-ENDED", "Post already ended", f"Ended on {post.valid_to}.")
        staff = Staff.unscoped.using(cmd.alias).select_for_update().get(pk=post.staff_id)
        sep = cmd.add(
            Separation(
                scope_node_id=post.scope_node_id,
                staff_id=staff.id,
                staff_post_id=post.id,
                separation_kind=separation_kind,
                notice_on=notice_on,
                effective_on=effective_on,
                exit_checklist={
                    "classes_to_reassign": impact,
                    "assets_returned": False,
                    "id_card_returned": False,
                    "final_pay": "not_started",
                    "pension_notified": False,
                    "access_removed": True,
                    **(checklist or {}),
                },
                recorded_by_id=ctx.actor_id,
                status="approved",
            )
        )
        cmd.update(post, valid_to=effective_on, leaving_reason=_leaving(separation_kind))
        rec = EmploymentRecord.unscoped.using(cmd.alias).select_for_update().filter(staff_post_id=post.id).first()
        if rec is not None:
            cmd.update(rec, status="separated")
        others = (
            StaffPost.unscoped.using(cmd.alias).filter(staff_id=staff.id, valid_to__isnull=True).exclude(pk=post.id)
        )
        fully_left = not others.exists()
        if fully_left:
            cmd.update(staff, status="leaver")
            _end_access(cmd, staff, effective_on)
            cmd.emit("STF.LEFT", aggregate_id=staff.id, aggregate_kind="staff", payload={"staff_id": staff.id})
        else:
            node = _institution_node(post.institution_id)
            if staff.user_id and node:
                for g in RoleGrant.unscoped.using(cmd.alias).filter(
                    user_id=staff.user_id, scope_id=node, status="active"
                ):
                    cmd.update(g, status="inactive", valid_to=effective_on)
        cmd.record_id = sep.id
        cmd.emit(
            "HR.SEPARATION_RECORDED",
            aggregate_id=sep.id,
            payload={"separation_id": sep.id, "staff_id": staff.id, "effective_on": effective_on},
        )
    _end_teaching(staff_post_id, effective_on, ctx)
    if post.institution_id:
        _reevaluate_coverage(post.institution_id, ctx, effective_on + dt.timedelta(days=1))
    return sep


def _end_access(cmd: uow.Command, staff: Staff, on: dt.date) -> None:
    if staff.user_id is None:
        return
    user = AppUser.unscoped.using(cmd.alias).select_for_update().get(pk=staff.user_id)
    cmd.update(user, status="deactivated", deactivated_at=utcnow())
    for g in RoleGrant.unscoped.using(cmd.alias).filter(user_id=user.id, status="active"):
        cmd.update(g, status="inactive", valid_to=on)
    UserSession.unscoped.using(cmd.alias).filter(user_id=user.id, revoked_at__isnull=True).update(revoked_at=utcnow())


def _leaving(kind: str) -> str:
    return {"death": "deceased", "transfer_of_service": "transferred"}.get(kind, "employment")
