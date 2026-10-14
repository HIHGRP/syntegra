"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``academic`` — Academic structure.
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



class AcademicPeriod(CedaModel):
    """Session, term, semester or half-term of a calendar (state calendar inherited by institutions)"""

    ceda_entity = 'academic_period'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'parent_id': {'type': 'ref', 'ref': 'academic_period'}, 'kind': {'type': 'enum', 'enum': 'period_kind'}, 'name': {'type': 'title'}, 'institution_types': {'type': 'cls', 'code_list': 'institution_category'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'teaching_days': {'type': 'smallint'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    parent = models.ForeignKey("academic.AcademicPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_id', null=True, blank=True)
    kind = models.CharField(max_length=32, choices=[('session', 'Session'), ('term', 'Term'), ('semester', 'Semester'), ('half_term', 'Half term'), ('billing_period', 'Billing period')])
    name = models.CharField(max_length=300)
    institution_types = models.JSONField(null=True, blank=True, help_text='Calendars differ by institution type')
    starts_on = models.DateField()
    ends_on = models.DateField()
    teaching_days = models.SmallIntegerField(null=True, blank=True, help_text='After closures')
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'academic_period'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Session, term, semester or half-term of a calendar (state calendar inherited by '


class CalendarEvent(CedaModel):
    """Closure, holiday, exam window or event on a calendar (school closures recalculate compliance with an automatic exception)"""

    ceda_entity = 'calendar_event'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'kind': {'type': 'enum', 'enum': 'calendar_event_kind'}, 'title': {'type': 'title'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'reduces_teaching_days': {'type': 'bool'}, 'is_remote_mode': {'type': 'bool'}, 'exception_id': {'type': 'ref', 'ref': 'policy_exception'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    period = models.ForeignKey("academic.AcademicPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='period_id')
    kind = models.CharField(max_length=32, choices=[('holiday', 'Holiday'), ('closure', 'Closure'), ('exam_window', 'Exam window'), ('event', 'Event'), ('inset_day', 'Inset day'), ('mid_term_break', 'Mid term break')])
    title = models.CharField(max_length=300)
    starts_on = models.DateField()
    ends_on = models.DateField()
    reduces_teaching_days = models.BooleanField(default=False)
    is_remote_mode = models.BooleanField(default=False, help_text='Closure switches classes to LMS remote mode')
    exception = models.ForeignKey("governance.PolicyException", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='exception_id', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'calendar_event'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Closure, holiday, exam window or event on a calendar (school closures recalculat'


class ClassGroup(CedaModel):
    """Class 360 — class (arm), set, cohort or course section for a period"""

    ceda_entity = 'class_group'
    ceda_zones = ('ops',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'campus_id': {'type': 'ref', 'ref': 'campus'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'kind': {'type': 'enum', 'enum': 'class_kind'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'name': {'type': 'title'}, 'stream': {'type': 'cl', 'code_list': 'stream'}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'parent_class_id': {'type': 'ref', 'ref': 'class_group'}, 'form_teacher_staff_id': {'type': 'ref', 'ref': 'staff'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'capacity': {'type': 'smallint'}, 'language_of_instruction': {'type': 'lang'}, 'session_shift': {'type': 'enum', 'enum': 'session_shift'}, 'rolled_from_id': {'type': 'ref', 'ref': 'class_group'}, 'status': {'type': 'enum', 'enum': 'class_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    campus_id = cf.UUID7Field(null=True, blank=True)
    period_id = cf.UUID7Field(help_text='Session')
    kind = models.CharField(max_length=32, choices=[('arm', 'Arm'), ('set', 'Set'), ('cohort', 'Cohort'), ('course_section', 'Course section'), ('group', 'Group')])
    education_level = models.CharField(max_length=32)
    name = models.CharField(max_length=300, help_text='Primary 4B, JSS 1 Gold, SS 2 Science A')
    stream = models.CharField(max_length=32, null=True, blank=True)
    programme_id = cf.UUID7Field(null=True, blank=True)
    parent_class = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_class_id', null=True, blank=True)
    form_teacher_staff_id = cf.UUID7Field(null=True, blank=True)
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    capacity = models.SmallIntegerField(help_text='Room capacity and state policy (default 40 primary, 45 secondary)')
    language_of_instruction = models.CharField(max_length=35, null=True, blank=True)
    session_shift = models.CharField(max_length=32, choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('single', 'Single')], null=True, blank=True, help_text='Double-shift schools')
    rolled_from = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rolled_from_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed'), ('archived', 'Archived')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'class_group'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Class 360 — class (arm), set, cohort or course section for a period'


class ClassMembership(CedaModel):
    """Learner membership of a class, set or grouping (exactly one class arm per session; sets in addition)"""

    ceda_entity = 'class_membership'
    ceda_zones = ('ops',)
    ceda_domain = 'ACA'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = 'derived: the class'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'is_arm': {'type': 'bool'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field()
    is_arm = models.BooleanField(help_text="True for the learner's single class arm")
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
        db_table = 'class_membership'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner membership of a class, set or grouping (exactly one class arm per sessio'


class ClassSubjectPlan(CedaModel):
    """Subject offered to a class — periods per week, room type, curriculum version, language of instruction"""

    ceda_entity = 'class_subject_plan'
    ceda_zones = ('ops',)
    ceda_domain = 'ACA'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'derived: the class'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'is_mandatory': {'type': 'bool'}, 'periods_per_week': {'type': 'smallint'}, 'required_hours': {'type': 'dec'}, 'room_type': {'type': 'cl', 'code_list': 'room_type'}, 'curriculum_version_id': {'type': 'ref', 'ref': 'curriculum_version'}, 'language_of_instruction': {'type': 'lang'}, 'copied_from_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    subject_id = cf.UUID7Field()
    is_mandatory = models.BooleanField(help_text='Pre-filled mandatory subjects cannot be removed')
    periods_per_week = models.SmallIntegerField()
    required_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='From the adopted curriculum')
    room_type = models.CharField(max_length=32, null=True, blank=True)
    curriculum_version_id = cf.UUID7Field(null=True, blank=True, help_text='Resolved and stored for history')
    language_of_instruction = models.CharField(max_length=35, null=True, blank=True)
    copied_from = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='copied_from_id', null=True, blank=True)
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
        db_table = 'class_subject_plan'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Subject offered to a class — periods per week, room type, curriculum version, la'


class Course(CedaModel):
    """Course 360 catalogue entry owned by a department (code, units, level, semester, prerequisites, benchmark)"""

    ceda_entity = 'course'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'department_id': {'type': 'ref', 'ref': 'department'}, 'subject_area_id': {'type': 'ref', 'ref': 'subject_area'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'units': {'type': 'dec'}, 'course_level': {'type': 'code'}, 'semester_no': {'type': 'smallint'}, 'is_service_course': {'type': 'bool'}, 'is_compulsory': {'type': 'bool'}, 'benchmark_ref': {'type': 'code'}, 'outline_document_id': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    department = models.ForeignKey("academic.Department", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='department_id')
    subject_area = models.ForeignKey("academic.SubjectArea", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='subject_area_id', null=True, blank=True)
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='subject_id', null=True, blank=True)
    code = models.CharField(max_length=20, help_text='e.g. COM 214, GST 111')
    title = models.CharField(max_length=300)
    units = models.DecimalField(max_digits=4, decimal_places=1)
    course_level = models.CharField(max_length=16)
    semester_no = models.SmallIntegerField(null=True, blank=True)
    is_service_course = models.BooleanField(default=False, help_text='Taught to other departments (GST)')
    is_compulsory = models.BooleanField(default=True)
    benchmark_ref = models.CharField(max_length=60, null=True, blank=True)
    outline_document_id = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'course'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Course 360 catalogue entry owned by a department (code, units, level, semester, '


class CourseRegistration(CedaModel):
    """Student semester course registration (unit limits, prerequisites, carry-overs, clashes, adviser approval)"""

    ceda_entity = 'course_registration'
    ceda_zones = ('ops',)
    ceda_domain = 'ACA'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the course section'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'course_section_id': {'type': 'ref', 'ref': 'course_section'}, 'is_carry_over': {'type': 'bool'}, 'units': {'type': 'dec'}, 'adviser_staff_id': {'type': 'ref', 'ref': 'staff'}, 'approved_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'registration_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field()
    course_section = models.ForeignKey("academic.CourseSection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_section_id')
    is_carry_over = models.BooleanField(default=False)
    units = models.DecimalField(max_digits=4, decimal_places=1)
    adviser_staff_id = cf.UUID7Field(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('adviser_approved', 'Adviser approved'), ('registered', 'Registered'), ('dropped', 'Dropped')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'course_registration'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Student semester course registration (unit limits, prerequisites, carry-overs, c'


class CourseSection(CedaModel):
    """Course offering section per semester (lecturer of record, co-lecturers, TAs, LMS space, assessment components)"""

    ceda_entity = 'course_section'
    ceda_zones = ('ops',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'course_id': {'type': 'ref', 'ref': 'course'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'section_code': {'type': 'code'}, 'capacity': {'type': 'smallint'}, 'consuming_department_ids': {'type': 'json'}, 'assessment_scheme': {'type': 'json'}, 'external_examiner': {'type': 'json'}, 'allocation_status': {'type': 'enum', 'enum': 'allocation_status'}, 'approved_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    course_id = cf.UUID7Field()
    period_id = cf.UUID7Field(help_text='Semester')
    section_code = models.CharField(max_length=8)
    capacity = models.SmallIntegerField(null=True, blank=True)
    consuming_department_ids = models.JSONField(null=True, blank=True, help_text='Service courses visible to consuming departments')
    assessment_scheme = models.JSONField(null=True, blank=True, help_text='CA and exam components')
    external_examiner = models.JSONField(null=True, blank=True, help_text='External examiners and moderators (FR-ACA-114)')
    allocation_status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('proposed', 'Proposed'), ('approved', 'Approved'), ('published', 'Published'), ('applied', 'Applied'), ('allocated', 'Allocated'), ('waitlisted', 'Waitlisted'), ('cancelled', 'Cancelled')], help_text='HOD approval publishes to timetables and the LMS')
    approved_by = cf.UUID7Field(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'course_section'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Course offering section per semester (lecturer of record, co-lecturers, TAs, LMS'


class Department(CedaModel):
    """Department 360 — academic department of a post-secondary institution"""

    ceda_entity = 'department'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'org_unit_id': {'type': 'ref', 'ref': 'org_unit'}, 'faculty_org_unit_id': {'type': 'ref', 'ref': 'org_unit'}, 'name': {'type': 'title'}, 'hod_staff_id': {'type': 'ref', 'ref': 'staff'}, 'acting_hod_staff_id': {'type': 'ref', 'ref': 'staff'}, 'load_policy': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    org_unit = models.ForeignKey("institutions.OrgUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='org_unit_id')
    faculty_org_unit = models.ForeignKey("institutions.OrgUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='faculty_org_unit_id', null=True, blank=True)
    name = models.CharField(max_length=300)
    hod_staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='hod_staff_id', null=True, blank=True)
    acting_hod_staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='acting_hod_staff_id', null=True, blank=True)
    load_policy = models.JSONField(null=True, blank=True, help_text='Maximum contact hours per rank')
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'department'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Department 360 — academic department of a post-secondary institution'


class Programme(CedaModel):
    """Programme 360 (qualification-bearing programmes, national or institutional)"""

    ceda_entity = 'programme'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'department_id': {'type': 'ref', 'ref': 'department'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'qualification_id': {'type': 'ref', 'ref': 'qualification'}, 'delivery_mode': {'type': 'enum', 'enum': 'delivery_mode'}, 'programme_family': {'type': 'cl', 'code_list': 'programme_family'}, 'professional_body_id': {'type': 'ref', 'ref': 'professional_body'}, 'duration_terms': {'type': 'smallint'}, 'rules': {'type': 'json'}, 'accreditation_status': {'type': 'enum', 'enum': 'accreditation_status'}, 'accreditation_expires_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id', null=True, blank=True)
    department = models.ForeignKey("academic.Department", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='department_id', null=True, blank=True)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    qualification = models.ForeignKey("academic.Qualification", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='qualification_id', null=True, blank=True)
    delivery_mode = models.CharField(max_length=32, choices=[('on_campus', 'On campus'), ('distance', 'Distance'), ('online', 'Online'), ('blended', 'Blended'), ('continuing', 'Continuing')], default='on_campus')
    programme_family = models.CharField(max_length=32, null=True, blank=True, help_text='Health-profession family (medicine, nursing, pharmacy …)')
    professional_body = models.ForeignKey("sectors.ProfessionalBody", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='professional_body_id', null=True, blank=True)
    duration_terms = models.SmallIntegerField(null=True, blank=True)
    rules = models.JSONField(help_text='Credits, CGPA, progression, classification scheme')
    accreditation_status = models.CharField(max_length=32, choices=[('full', 'Full'), ('interim', 'Interim'), ('denied', 'Denied'), ('expired', 'Expired'), ('not_required', 'Not required')], null=True, blank=True)
    accreditation_expires_on = models.DateField(null=True, blank=True)
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
        db_table = 'programme'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Programme 360 (qualification-bearing programmes, national or institutional)'


class ProgrammeComponent(CedaModel):
    """Course or module within a programme (credits, core/elective, prerequisites — cycle-checked)"""

    ceda_entity = 'programme_component'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'link'
    ceda_class = 'public'
    ceda_history = 'effective'
    ceda_scope = 'derived: the programme'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'course_id': {'type': 'ref', 'ref': 'course'}, 'programme_level': {'type': 'code'}, 'semester_no': {'type': 'smallint'}, 'credits': {'type': 'dec'}, 'is_core': {'type': 'bool'}, 'prerequisite_course_ids': {'type': 'json'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    programme = models.ForeignKey("academic.Programme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id')
    course = models.ForeignKey("academic.Course", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_id')
    programme_level = models.CharField(max_length=16, null=True, blank=True, help_text='100L, ND1, Year 2')
    semester_no = models.SmallIntegerField(null=True, blank=True)
    credits = models.DecimalField(max_digits=4, decimal_places=1)
    is_core = models.BooleanField()
    prerequisite_course_ids = models.JSONField(null=True, blank=True, help_text='Cycle-checked on save')
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
        db_table = 'programme_component'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Course or module within a programme (credits, core/elective, prerequisites — cyc'


class Qualification(CedaModel):
    """Qualification 360 (FSLC, BECE, SSC, NTC, NCE, ND, HND, B.Sc. …) with award rules"""

    ceda_entity = 'qualification'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'awarding_body': {'type': 'cl', 'code_list': 'regulator'}, 'framework_level': {'type': 'code'}, 'award_rules': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    awarding_body = models.CharField(max_length=32)
    framework_level = models.CharField(max_length=16, null=True, blank=True)
    award_rules = models.JSONField(help_text='Evaluated by the eligibility engine')
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'qualification'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Qualification 360 (FSLC, BECE, SSC, NTC, NCE, ND, HND, B.Sc. …) with award rules'


class StreamCombinationRule(CedaModel):
    """Stream subject-combination rule (WAEC, NECO, NABTEB, JAMB) for SSS classes and option choices"""

    ceda_entity = 'stream_combination_rule'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'stream': {'type': 'cl', 'code_list': 'stream'}, 'exam_body': {'type': 'cl', 'code_list': 'exam_body'}, 'rule': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    stream = models.CharField(max_length=32)
    exam_body = models.CharField(max_length=32, null=True, blank=True)
    rule = models.JSONField(help_text='Required, either-of and maximum subject sets')
    version = models.PositiveIntegerField()
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
        db_table = 'stream_combination_rule'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Stream subject-combination rule (WAEC, NECO, NABTEB, JAMB) for SSS classes and o'


class Subject(CedaModel):
    """Subject 360 master (country master list plus institution courses)"""

    ceda_entity = 'subject'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'levels': {'type': 'cls', 'code_list': 'education_level'}, 'subject_group': {'type': 'cl', 'code_list': 'subject_group'}, 'is_mandatory_core': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    levels = models.JSONField(null=True, blank=True)
    subject_group = models.CharField(max_length=32, null=True, blank=True, help_text='Core, science, arts, commercial, technical, vocational, language')
    is_mandatory_core = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subject'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Subject 360 master (country master list plus institution courses)'


class SubjectArea(CedaModel):
    """Discipline area of a department mapped to the national benchmark (NUC CCMAS, NBTE, NCCE)"""

    ceda_entity = 'subject_area'
    ceda_zones = ('registry',)
    ceda_domain = 'ACA'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the department'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'department_id': {'type': 'ref', 'ref': 'department'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'benchmark': {'type': 'cl', 'code_list': 'benchmark_framework'}, 'benchmark_area_code': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    department = models.ForeignKey("academic.Department", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='department_id')
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=300)
    benchmark = models.CharField(max_length=32)
    benchmark_area_code = models.CharField(max_length=40)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subject_area'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Discipline area of a department mapped to the national benchmark (NUC CCMAS, NBT'


class TeachingAssignment(CedaModel):
    """Teacher of record or co-teacher for a class-subject or lecturer for a course section (effective-dated)"""

    ceda_entity = 'teaching_assignment'
    ceda_zones = ('ops',)
    ceda_domain = 'ACA'
    ceda_kind = 'link'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'class_subject_plan_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'course_section_id': {'type': 'ref', 'ref': 'course_section'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'role': {'type': 'enum', 'enum': 'teaching_role'}, 'authorisation_id': {'type': 'ref', 'ref': 'staff_qualification'}, 'exception_id': {'type': 'ref', 'ref': 'policy_exception'}, 'justification': {'type': 'str'}, 'weekly_periods': {'type': 'dec'}, 'of_record_key': {'type': 'uuid', 'generated': True}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    class_subject_plan = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_subject_plan_id', null=True, blank=True)
    course_section = models.ForeignKey("academic.CourseSection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_section_id', null=True, blank=True)
    staff_id = cf.UUID7Field()
    staff_post_id = cf.UUID7Field()
    role = models.CharField(max_length=32, choices=[('teacher_of_record', 'Teacher of record'), ('co_teacher', 'Co teacher'), ('teaching_assistant', 'Teaching assistant'), ('specialist', 'Specialist')])
    authorisation_id = cf.UUID7Field(null=True, blank=True, help_text='Authorisation that satisfied G3')
    exception_id = cf.UUID7Field(null=True, blank=True, help_text='Time-boxed exception when unauthorised')
    justification = models.CharField(max_length=500, null=True, blank=True, help_text='Out-of-specialism or overload reason (HOD)')
    weekly_periods = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    of_record_key = cf.generated(cf.UUID7Field(null=True, blank=True, editable=False))
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
        db_table = 'teaching_assignment'
        app_label = 'academic'
        base_manager_name = 'unscoped'
        verbose_name = 'Teacher of record or co-teacher for a class-subject or lecturer for a course sec'
