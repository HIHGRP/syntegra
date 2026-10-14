"""Academic structure services (MFS §10): sessions, classes, memberships, subject plans, teaching assignments."""

from __future__ import annotations

import datetime as dt
import uuid
from decimal import Decimal

from django.db import IntegrityError, transaction

from syntegra.academic.models import AcademicPeriod, ClassGroup, ClassMembership, ClassSubjectPlan, Subject, TeachingAssignment
from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.institutions.models import Institution
from syntegra.learners.models import Enrolment

DEFAULT_CAPACITY = {"primary": 40, "jss": 45, "sss": 45}


def _institution(institution_id: uuid.UUID) -> Institution:
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def create_session(scope_node_id: uuid.UUID, name: str, starts_on: dt.date, ends_on: dt.date,
                   kind: str = "session", parent_id: uuid.UUID | None = None) -> AcademicPeriod:
    with uow.command("registry", "calendar:manage", action="create", record_kind="academic_period") as cmd:
        return cmd.add(AcademicPeriod(scope_node_id=scope_node_id, parent_id=parent_id, kind=kind, name=name,
                                      starts_on=starts_on, ends_on=ends_on, status="active"))


def create_subject(scope_node_id: uuid.UUID, code: str, name: str, levels: list[str], mandatory: bool = True) -> Subject:
    with uow.command("registry", "curriculum:manage", action="create", record_kind="subject") as cmd:
        return cmd.add(Subject(scope_node_id=scope_node_id, code=code, name=name, levels=levels,
                               is_mandatory_core=mandatory, status="active"))


def create_class(institution_id: uuid.UUID, period_id: uuid.UUID, name: str, education_level: str,
                 capacity: int | None = None) -> ClassGroup:
    inst = _institution(institution_id)
    with uow.command("ops", "class:manage", action="create", record_kind="class_group") as cmd:
        return cmd.add(ClassGroup(
            scope_node_id=inst.scope_node_id, institution_id=inst.id, period_id=period_id, kind="arm",
            education_level=education_level, name=name,
            capacity=capacity or DEFAULT_CAPACITY.get(education_level.split("_")[0].lower(), 40), status="active",
        ))


def add_member(class_id: uuid.UUID, learner_id: uuid.UUID, valid_from: dt.date | None = None) -> ClassMembership:
    ctx = context.require()
    with uow.command("ops", "class:manage", action="add_member", record_kind="class_group") as cmd:
        cls = cmd.lock(ClassGroup, class_id)
        enr = Enrolment.objects.filter(learner_id=learner_id, institution_id=cls.institution_id, status="active").first()
        if enr is None:
            raise HardValidation("CLS-NOT-ENROLLED", "Learner not enrolled here",
                                 "Enrol the learner at the institution before placing them in a class.")
        if ClassMembership.unscoped.using(cmd.alias).filter(tenant_id=ctx.tenant_id, learner_id=learner_id,
                                                            is_arm=True, valid_to__isnull=True).exists():
            raise ConflictError("CLS-ALREADY", "Learner already in a class arm", "End the current arm first.")
        cmd.record_id = cls.id
        return cmd.add(ClassMembership(class_group_id=cls.id, learner_id=learner_id, enrolment_id=enr.id, is_arm=True,
                                       valid_from=valid_from or dt.date.today()))


def members(class_id: uuid.UUID, on: dt.date | None = None) -> list[ClassMembership]:
    on = on or dt.date.today()
    return list(ClassMembership.objects.filter(class_group_id=class_id, valid_from__lte=on)
                .exclude(valid_to__lt=on))


def add_subject_plan(class_id: uuid.UUID, subject_id: uuid.UUID, periods_per_week: int, *,
                     mandatory: bool = True, required_hours: Decimal | None = None) -> ClassSubjectPlan:
    with uow.command("ops", "class:manage", action="add_subject", record_kind="class_group") as cmd:
        cls = cmd.lock(ClassGroup, class_id)
        cmd.record_id = cls.id
        return cmd.add(ClassSubjectPlan(class_group_id=cls.id, subject_id=subject_id, is_mandatory=mandatory,
                                        periods_per_week=periods_per_week, required_hours=required_hours,
                                        valid_from=dt.date.today()))


def assign_teacher(plan_id: uuid.UUID, staff_id: uuid.UUID, staff_post_id: uuid.UUID, *,
                   role: str = "teacher_of_record", weekly_periods: Decimal | None = None) -> TeachingAssignment:
    with uow.command("ops", "class:manage", action="assign", record_kind="teaching_assignment") as cmd:
        plan = cmd.lock(ClassSubjectPlan, plan_id)
        cls = ClassGroup.objects.get(pk=plan.class_group_id)
        ta = TeachingAssignment(scope_node_id=cls.scope_node_id, class_subject_plan_id=plan.id, staff_id=staff_id,
                                staff_post_id=staff_post_id, role=role, weekly_periods=weekly_periods,
                                valid_from=dt.date.today())
        try:
            with transaction.atomic(using=cmd.alias):
                cmd.add(ta)
        except IntegrityError as exc:
            if "of_record_key" in str(exc):
                raise ConflictError("G2-TWO-TEACHERS", "Class-subject already has a teacher of record",
                                    "End the current assignment or add this teacher as a co-teacher.") from exc
            raise
        cmd.emit("CUR.ASSIGNMENT_CHANGED", aggregate_id=ta.id, aggregate_kind="teaching_assignment",
                 scope_node_id=cls.scope_node_id, payload=_assignment_payload(ta, cls))
        return ta


def end_assignment(assignment_id: uuid.UUID, on: dt.date | None = None) -> TeachingAssignment:
    with uow.command("ops", "class:manage", action="end", record_kind="teaching_assignment") as cmd:
        ta = cmd.lock(TeachingAssignment, assignment_id)
        cmd.update(ta, valid_to=on or dt.date.today())
        cls = ClassGroup.objects.get(pk=ClassSubjectPlan.objects.get(pk=ta.class_subject_plan_id).class_group_id)
        cmd.emit("CUR.ASSIGNMENT_CHANGED", aggregate_id=ta.id, aggregate_kind="teaching_assignment",
                 scope_node_id=cls.scope_node_id, payload=_assignment_payload(ta, cls))
        return ta


def _assignment_payload(ta: TeachingAssignment, cls: ClassGroup) -> dict[str, object]:
    from syntegra.core import catalog

    spec = catalog.event("CUR.ASSIGNMENT_CHANGED").get("payload") or {}
    full = {"teaching_assignment_id": ta.id, "class_subject_plan_id": ta.class_subject_plan_id, "staff_id": ta.staff_id,
            "institution_id": cls.institution_id, "class_group_id": cls.id}
    return {k: v for k, v in full.items() if k in spec}
