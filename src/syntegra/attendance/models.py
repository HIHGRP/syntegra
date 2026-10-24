"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``attendance`` — Attendance registers, absence reporting and follow-up, staff sign-in, visitors and evacuation roll call.
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



class AbsenceContact(CedaModel):
    """First-day absence contact attempt and outcome (escalation and DSL alert for vulnerable learners not reached)"""

    ceda_entity = 'absence_contact'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-ATT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'session_date': {'type': 'date'}, 'contacted_guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'channel': {'type': 'enum', 'enum': 'channel'}, 'message_id': {'type': 'ref', 'ref': 'message'}, 'outcome': {'type': 'enum', 'enum': 'contact_outcome'}, 'reason_given': {'type': 'str'}, 'escalated_to': {'type': 'enum', 'enum': 'escalation_target'}, 'attempted_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    session_date = models.DateField()
    contacted_guardian_id = cf.UUID7Field(null=True, blank=True)
    channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    message_id = cf.UUID7Field(null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('reached_reason_given', 'Reached reason given'), ('reached_no_reason', 'Reached no reason'), ('no_answer', 'No answer'), ('message_sent', 'Message sent'), ('failed', 'Failed')])
    reason_given = models.CharField(max_length=500, null=True, blank=True)
    escalated_to = models.CharField(max_length=32, choices=[('pastoral_lead', 'Pastoral lead'), ('dsl', 'Dsl'), ('head', 'Head'), ('lga', 'Lga')], null=True, blank=True)
    attempted_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'absence_contact'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'First-day absence contact attempt and outcome (escalation and DSL alert for vuln'


class AbsenceReport(CedaModel):
    """Absence reported by a parent (app, WhatsApp, web, office) — acknowledged, accepted (pre-fills code) or queried"""

    ceda_entity = 'absence_report'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-ATT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'reported_by_guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'channel': {'type': 'enum', 'enum': 'channel'}, 'from_date': {'type': 'date'}, 'to_date': {'type': 'date'}, 'reason': {'type': 'cl', 'code_list': 'absence_reason'}, 'message_text': {'type': 'str'}, 'attachment_document_id': {'type': 'uuid'}, 'proposed_code': {'type': 'cl', 'code_list': 'attendance_code'}, 'conversation_id': {'type': 'ref', 'ref': 'conversation'}, 'handled_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'absence_report_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    reported_by_guardian_id = cf.UUID7Field(null=True, blank=True)
    channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.CharField(max_length=32)
    message_text = models.CharField(max_length=2000, null=True, blank=True)
    attachment_document_id = cf.UUID7Field(null=True, blank=True, help_text='Medical note')
    proposed_code = models.CharField(max_length=32, null=True, blank=True)
    conversation = models.ForeignKey("comms.Conversation", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='conversation_id', null=True, blank=True)
    handled_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('received', 'Received'), ('acknowledged', 'Acknowledged'), ('accepted', 'Accepted'), ('queried', 'Queried'), ('rejected', 'Rejected')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'absence_report'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'Absence reported by a parent (app, WhatsApp, web, office) — acknowledged, accept'


class AttendanceMark(CedaModel):
    """Attendance mark per learner per register (partitioned by month; integrity checked nightly)"""

    ceda_entity = 'attendance_mark'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = "derived: the register's class"
    ceda_append_only = False
    ceda_partition = {'type': 'range_month', 'column': 'session_date'}
    ceda_retention = 'RS-ATT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'register_id': {'type': 'ref', 'ref': 'attendance_register'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'session_date': {'type': 'date'}, 'code': {'type': 'cl', 'code_list': 'attendance_code'}, 'minutes_late': {'type': 'smallint'}, 'reason_source': {'type': 'enum', 'enum': 'reason_source'}, 'absence_report_id': {'type': 'ref', 'ref': 'absence_report'}, 'recorded_by': {'type': 'uuid'}, 'source': {'type': 'enum', 'enum': 'mark_source'}, 'client_op_id': {'type': 'uuid'}, 'device_captured_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    register_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field()
    session_date = models.DateField()
    code = models.CharField(max_length=32, help_text='Present, Late, Absent (unauthorised), Medical, Excused, Approved activity, Not required')
    minutes_late = models.SmallIntegerField(null=True, blank=True)
    reason_source = models.CharField(max_length=32, choices=[('teacher', 'Teacher'), ('parent', 'Parent'), ('office', 'Office'), ('system', 'System')], null=True, blank=True)
    absence_report_id = cf.UUID7Field(null=True, blank=True)
    recorded_by = cf.UUID7Field()
    source = models.CharField(max_length=32, choices=[('teacher', 'Teacher'), ('office', 'Office'), ('kiosk', 'Kiosk'), ('biometric_device', 'Biometric device'), ('lms_live_class', 'Lms live class'), ('parent_prefill', 'Parent prefill'), ('import', 'Import')], help_text='teacher, office, kiosk, biometric_device, lms_live_class, parent_prefill')
    client_op_id = cf.UUID7Field(null=True, blank=True, help_text='Offline idempotency key')
    device_captured_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)
    pk = models.CompositePrimaryKey('id', 'session_date')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'attendance_mark'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'Attendance mark per learner per register (partitioned by month; integrity checke'


class AttendanceRegister(CedaModel):
    """Register header — one daily (AM/PM) or lesson register for a class or section on a date"""

    ceda_entity = 'attendance_register'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-ATT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'register_kind': {'type': 'enum', 'enum': 'register_kind'}, 'session_date': {'type': 'date'}, 'lesson_occurrence_id': {'type': 'ref', 'ref': 'lesson_occurrence'}, 'due_at': {'type': 'ts'}, 'taken_by_staff_id': {'type': 'ref', 'ref': 'staff'}, 'submitted_at': {'type': 'ts'}, 'device_captured_at': {'type': 'ts'}, 'marks_count': {'type': 'smallint'}, 'release_to_parents_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'register_status'}, 'lesson_key': {'type': 'uuid', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    register_kind = models.CharField(max_length=32, choices=[('am', 'Am'), ('pm', 'Pm'), ('daily', 'Daily'), ('lesson', 'Lesson'), ('activity', 'Activity'), ('trip', 'Trip')])
    session_date = models.DateField()
    lesson_occurrence = models.ForeignKey("timetable.LessonOccurrence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lesson_occurrence_id', null=True, blank=True)
    due_at = models.DateTimeField(help_text='Deadline (missing-register nudge at +10 min, escalation at +30 min)')
    taken_by_staff_id = cf.UUID7Field(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    device_captured_at = models.DateTimeField(null=True, blank=True, help_text='Offline capture time')
    marks_count = models.SmallIntegerField(null=True, blank=True)
    release_to_parents_at = models.DateTimeField(null=True, blank=True, help_text='Live or delayed sharing per institution setting')
    status = models.CharField(max_length=32, choices=[('due', 'Due'), ('in_progress', 'In progress'), ('submitted', 'Submitted'), ('late', 'Late'), ('missing', 'Missing'), ('corrected', 'Corrected')])
    lesson_key = cf.generated(cf.UUID7Field(null=True, blank=True, help_text='lesson_occurrence_id, or all-zero for daily registers (uniqueness)', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'attendance_register'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'Register header — one daily (AM/PM) or lesson register for a class or section on'


class EvacuationEvent(CedaModel):
    """Evacuation or drill (start, all-clear, timings as safe-schools inspection evidence)"""

    ceda_entity = 'evacuation_event'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-ATT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'campus_id': {'type': 'ref', 'ref': 'campus'}, 'kind': {'type': 'enum', 'enum': 'evacuation_kind'}, 'started_at': {'type': 'ts'}, 'all_clear_at': {'type': 'ts'}, 'incident_lead_staff_id': {'type': 'ref', 'ref': 'staff'}, 'expected_count': {'type': 'int_u'}, 'accounted_count': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'evacuation_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    campus_id = cf.UUID7Field()
    kind = models.CharField(max_length=32, choices=[('fire', 'Fire'), ('drill', 'Drill'), ('lockdown', 'Lockdown'), ('invacuation', 'Invacuation'), ('other', 'Other')])
    started_at = models.DateTimeField()
    all_clear_at = models.DateTimeField(null=True, blank=True)
    incident_lead_staff_id = cf.UUID7Field(null=True, blank=True)
    expected_count = models.PositiveIntegerField(null=True, blank=True)
    accounted_count = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('in_progress', 'In progress'), ('all_clear', 'All clear'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'evacuation_event'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'Evacuation or drill (start, all-clear, timings as safe-schools inspection eviden'


class EvacuationMark(CedaModel):
    """Roll-call mark for a person at an assembly point (learner, staff or visitor), captured offline"""

    ceda_entity = 'evacuation_mark'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-ATT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'evacuation_event_id': {'type': 'ref', 'ref': 'evacuation_event'}, 'person_kind': {'type': 'enum', 'enum': 'roll_call_person'}, 'person_id': {'type': 'uuid'}, 'assembly_point': {'type': 'str'}, 'marshal_staff_id': {'type': 'ref', 'ref': 'staff'}, 'state': {'type': 'enum', 'enum': 'roll_call_state'}, 'marked_at': {'type': 'ts'}, 'client_op_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    evacuation_event = models.ForeignKey("attendance.EvacuationEvent", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='evacuation_event_id')
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('staff', 'Staff'), ('visitor', 'Visitor')])
    person_id = cf.UUID7Field()
    assembly_point = models.CharField(max_length=60)
    marshal_staff_id = cf.UUID7Field()
    state = models.CharField(max_length=32, choices=[('safe', 'Safe'), ('missing', 'Missing'), ('absent_today', 'Absent today'), ('left_site', 'Left site')])
    marked_at = models.DateTimeField()
    client_op_id = cf.UUID7Field(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'evacuation_mark'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'Roll-call mark for a person at an assembly point (learner, staff or visitor), ca'


class StaffAttendance(CedaModel):
    """Staff sign-in and sign-out (manual, kiosk or biometric device — templates never leave the device)"""

    ceda_entity = 'staff_attendance'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = {'type': 'range_month', 'column': 'signed_on'}
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'signed_on': {'type': 'date'}, 'direction': {'type': 'enum', 'enum': 'sign_direction'}, 'at': {'type': 'ts'}, 'source': {'type': 'enum', 'enum': 'mark_source'}, 'device_ref': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff_id = cf.UUID7Field()
    signed_on = models.DateField()
    direction = models.CharField(max_length=32, choices=[('in', 'In'), ('out', 'Out')])
    at = models.DateTimeField()
    source = models.CharField(max_length=32, choices=[('teacher', 'Teacher'), ('office', 'Office'), ('kiosk', 'Kiosk'), ('biometric_device', 'Biometric device'), ('lms_live_class', 'Lms live class'), ('parent_prefill', 'Parent prefill'), ('import', 'Import')])
    device_ref = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('id', 'signed_on')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'staff_attendance'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'Staff sign-in and sign-out (manual, kiosk or biometric device — templates never '


class VisitorVisit(CedaModel):
    """Visitor log entry (included in evacuation roll calls)"""

    ceda_entity = 'visitor_visit'
    ceda_zones = ('ops',)
    ceda_domain = 'ATT'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'visitor_name': {'type': 'name', 'pii': True}, 'organisation': {'type': 'title'}, 'phone': {'type': 'phone', 'pii': True}, 'host_staff_id': {'type': 'ref', 'ref': 'staff'}, 'purpose': {'type': 'str'}, 'badge_no': {'type': 'code'}, 'arrived_at': {'type': 'ts'}, 'departed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    visitor_name = models.CharField(max_length=200)
    organisation = models.CharField(max_length=300, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    host_staff_id = cf.UUID7Field(null=True, blank=True)
    purpose = models.CharField(max_length=300, null=True, blank=True)
    badge_no = models.CharField(max_length=20, null=True, blank=True)
    arrived_at = models.DateTimeField()
    departed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'visitor_visit'
        app_label = 'attendance'
        base_manager_name = 'unscoped'
        verbose_name = 'Visitor log entry (included in evacuation roll calls)'
