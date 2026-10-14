"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``timetable`` — Timetable, lesson occurrences, cover rota, duties and room bookings.
Tables are created from ceda/generated/mysql (``managed = False``); put behaviour in the module's
domain/ and services/ packages, never here.
"""
# ruff: noqa
from __future__ import annotations

from django.db import models

from syntegra.core import fields as cf
from syntegra.core.ids import uuid7
from syntegra.core.managers import TenantScopedManager
from syntegra.core.models_base import CedaModel



class DutyRota(CedaModel):
    """Break, duty or on-call rota slot (fair distribution; on-call responders for BEH-105)"""

    ceda_entity = 'duty_rota'
    ceda_zones = ('ops',)
    ceda_domain = 'TIM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'duty_kind': {'type': 'enum', 'enum': 'duty_kind'}, 'location': {'type': 'str'}, 'cycle_day': {'type': 'smallint'}, 'period_code': {'type': 'code'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'backup_staff_id': {'type': 'ref', 'ref': 'staff'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    duty_kind = models.CharField(max_length=32, choices=[('break_duty', 'Break duty'), ('lunch_duty', 'Lunch duty'), ('gate_duty', 'Gate duty'), ('on_call', 'On call'), ('bus_duty', 'Bus duty')])
    location = models.CharField(max_length=120, null=True, blank=True)
    cycle_day = models.SmallIntegerField()
    period_code = models.CharField(max_length=16)
    staff_id = cf.UUID7Field()
    backup_staff_id = cf.UUID7Field(null=True, blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'duty_rota'
        app_label = 'timetable'
        base_manager_name = 'unscoped'
        verbose_name = 'Break, duty or on-call rota slot (fair distribution; on-call responders for BEH-'


class LessonOccurrence(CedaModel):
    """Dated occurrence of a lesson, materialised when a register, cover, delivery log or rating refers to it"""

    ceda_entity = 'lesson_occurrence'
    ceda_zones = ('ops',)
    ceda_domain = 'TIM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'timetable_lesson_id': {'type': 'ref', 'ref': 'timetable_lesson'}, 'occurs_on': {'type': 'date'}, 'starts_at': {'type': 'ts'}, 'ends_at': {'type': 'ts'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'is_remote': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'lesson_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    timetable_lesson = models.ForeignKey("timetable.TimetableLesson", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='timetable_lesson_id')
    occurs_on = models.DateField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    staff_id = cf.UUID7Field(help_text='Teacher actually responsible (cover changes it)')
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=[('scheduled', 'Scheduled'), ('taught', 'Taught'), ('covered', 'Covered'), ('cancelled', 'Cancelled'), ('remote', 'Remote')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'lesson_occurrence'
        app_label = 'timetable'
        base_manager_name = 'unscoped'
        verbose_name = 'Dated occurrence of a lesson, materialised when a register, cover, delivery log '


class Letting(CedaModel):
    """External letting of facilities with charges posted to finance"""

    ceda_entity = 'letting'
    ceda_zones = ('ops',)
    ceda_domain = 'TIM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'room_booking_id': {'type': 'ref', 'ref': 'room_booking'}, 'hirer_name': {'type': 'title'}, 'hirer_contact': {'type': 'str', 'pii': True}, 'charge_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'status': {'type': 'enum', 'enum': 'booking_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    room_booking = models.ForeignKey("timetable.RoomBooking", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_booking_id')
    hirer_name = models.CharField(max_length=300)
    hirer_contact = models.CharField(max_length=200, null=True, blank=True)
    charge_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('requested', 'Requested'), ('confirmed', 'Confirmed'), ('declined', 'Declined'), ('cancelled', 'Cancelled'), ('completed', 'Completed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'letting'
        app_label = 'timetable'
        base_manager_name = 'unscoped'
        verbose_name = 'External letting of facilities with charges posted to finance'


class PeriodStructure(CedaModel):
    """Bell schedule — named periods with times per day of the cycle and per year-group structure"""

    ceda_entity = 'period_structure'
    ceda_zones = ('ops',)
    ceda_domain = 'TIM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'derived: the timetable'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'timetable_id': {'type': 'ref', 'ref': 'timetable'}, 'structure_code': {'type': 'code'}, 'cycle_day': {'type': 'smallint'}, 'period_code': {'type': 'code'}, 'starts_at': {'type': 'time'}, 'ends_at': {'type': 'time'}, 'is_teaching': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    timetable = models.ForeignKey("timetable.Timetable", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='timetable_id')
    structure_code = models.CharField(max_length=20, help_text='Year-group structure')
    cycle_day = models.SmallIntegerField()
    period_code = models.CharField(max_length=16)
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    is_teaching = models.BooleanField(default=True, help_text='Breaks and registration periods are not teaching')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'period_structure'
        app_label = 'timetable'
        base_manager_name = 'unscoped'
        verbose_name = 'Bell schedule — named periods with times per day of the cycle and per year-group'


class RoomBooking(CedaModel):
    """Booking of a room or shared resource (labs, halls, laptop trolleys) — recurring, approval rules, weekly limits"""

    ceda_entity = 'room_booking'
    ceda_zones = ('ops',)
    ceda_domain = 'TIM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'asset_id': {'type': 'ref', 'ref': 'asset'}, 'booked_by': {'type': 'uuid'}, 'purpose': {'type': 'str'}, 'starts_at': {'type': 'ts'}, 'ends_at': {'type': 'ts'}, 'recurrence': {'type': 'json'}, 'approved_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'booking_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    asset = models.ForeignKey("operations.Asset", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='asset_id', null=True, blank=True)
    booked_by = cf.UUID7Field()
    purpose = models.CharField(max_length=300)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    recurrence = models.JSONField(null=True, blank=True, help_text='RRULE for recurring bookings')
    approved_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('requested', 'Requested'), ('confirmed', 'Confirmed'), ('declined', 'Declined'), ('cancelled', 'Cancelled'), ('completed', 'Completed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'room_booking'
        app_label = 'timetable'
        base_manager_name = 'unscoped'
        verbose_name = 'Booking of a room or shared resource (labs, halls, laptop trolleys) — recurring,'


class Timetable(CedaModel):
    """Timetable version for an institution and session (one- or two-week cycles, structures per year group)"""

    ceda_entity = 'timetable'
    ceda_zones = ('ops',)
    ceda_domain = 'TIM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'version': {'type': 'int_u'}, 'cycle_weeks': {'type': 'smallint'}, 'sessions_per_day': {'type': 'smallint'}, 'solver_run': {'type': 'json'}, 'unmet_requirements': {'type': 'json'}, 'exception_id': {'type': 'ref', 'ref': 'policy_exception'}, 'published_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    period_id = cf.UUID7Field()
    version = models.PositiveIntegerField()
    cycle_weeks = models.SmallIntegerField(default=1)
    sessions_per_day = models.SmallIntegerField(default=1, help_text='Double-shift schools')
    solver_run = models.JSONField(null=True, blank=True, help_text='Constraint set, objective value and unmet soft constraints')
    unmet_requirements = models.JSONField(null=True, blank=True, help_text='Mandatory hours not met (publication blocked unless an exception exists)')
    exception_id = cf.UUID7Field(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'timetable'
        app_label = 'timetable'
        base_manager_name = 'unscoped'
        verbose_name = 'Timetable version for an institution and session (one- or two-week cycles, struc'


class TimetableLesson(CedaModel):
    """Recurring scheduled lesson (class or section × subject × teacher × room × cycle slot)"""

    ceda_entity = 'timetable_lesson'
    ceda_zones = ('ops',)
    ceda_domain = 'TIM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'derived: the timetable'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'timetable_id': {'type': 'ref', 'ref': 'timetable'}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'class_subject_plan_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'course_section_id': {'type': 'ref', 'ref': 'course_section'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'cycle_day': {'type': 'smallint'}, 'period_code': {'type': 'code'}, 'duration_minutes': {'type': 'minutes'}, 'lesson_kind': {'type': 'enum', 'enum': 'lesson_kind'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    timetable = models.ForeignKey("timetable.Timetable", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='timetable_id')
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    class_subject_plan = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_subject_plan_id', null=True, blank=True)
    course_section = models.ForeignKey("academic.CourseSection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_section_id', null=True, blank=True)
    subject_id = cf.UUID7Field()
    staff_id = cf.UUID7Field()
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    cycle_day = models.SmallIntegerField()
    period_code = models.CharField(max_length=16)
    duration_minutes = models.IntegerField()
    lesson_kind = models.CharField(max_length=32, choices=[('lesson', 'Lesson'), ('lecture', 'Lecture'), ('tutorial', 'Tutorial'), ('practical', 'Practical'), ('live_class', 'Live class'), ('registration', 'Registration')], default='lesson', help_text='lesson, lecture, tutorial, practical, live_class')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'timetable_lesson'
        app_label = 'timetable'
        base_manager_name = 'unscoped'
        verbose_name = 'Recurring scheduled lesson (class or section × subject × teacher × room × cycle '
