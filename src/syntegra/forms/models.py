"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``forms`` — Forms and Daybook engine and parents' meetings.
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



class FormDefinition(CedaModel):
    """Form template (versioned; text, number, date, choice, signature, upload, body-map, cost and table fields)"""

    ceda_entity = 'form_definition'
    ceda_zones = ('ops',)
    ceda_domain = 'FRM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'field_schema': {'type': 'json'}, 'raised_by_roles': {'type': 'json'}, 'confidentiality': {'type': 'enum', 'enum': 'classification'}, 'workflow_definition_id': {'type': 'ref', 'ref': 'workflow_definition'}, 'cost_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'requires_payment_before_continue': {'type': 'bool'}, 'files_to': {'type': 'enum', 'enum': 'daybook_target'}, 'is_template_library': {'type': 'bool'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    field_schema = models.JSONField(help_text='Fields, mandatory and conditional rules')
    raised_by_roles = models.JSONField(help_text='Staff, learners, parents, on behalf')
    confidentiality = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')])
    workflow_definition_id = cf.UUID7Field(null=True, blank=True)
    cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    requires_payment_before_continue = models.BooleanField(default=False)
    files_to = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('staff', 'Staff'), ('family', 'Family'), ('institution', 'Institution')])
    is_template_library = models.BooleanField(default=False)
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
        db_table = 'form_definition'
        app_label = 'forms'
        base_manager_name = 'unscoped'
        verbose_name = 'Form template (versioned; text, number, date, choice, signature, upload, body-ma'


class FormResponse(CedaModel):
    """Submitted form (keeps the version it was submitted on; filed to the Daybook timeline)"""

    ceda_entity = 'form_response'
    ceda_zones = ('ops',)
    ceda_domain = 'FRM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'form_id': {'type': 'ref', 'ref': 'form_definition'}, 'form_version': {'type': 'int_u'}, 'subject_kind': {'type': 'enum', 'enum': 'person_kind'}, 'subject_id': {'type': 'uuid'}, 'submitted_by': {'type': 'uuid'}, 'on_behalf_of': {'type': 'uuid'}, 'answers': {'type': 'json'}, 'attachment_document_ids': {'type': 'json'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'workflow_instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'submitted_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'form_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    form_id = cf.UUID7Field(null=True, blank=True)
    form_version = models.PositiveIntegerField()
    subject_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    subject_id = cf.UUID7Field()
    submitted_by = cf.UUID7Field()
    on_behalf_of = cf.UUID7Field(null=True, blank=True)
    answers = models.JSONField()
    attachment_document_ids = models.JSONField(null=True, blank=True)
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id', null=True, blank=True)
    workflow_instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='workflow_instance_id', null=True, blank=True)
    submitted_at = models.DateTimeField()
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('in_workflow', 'In workflow'), ('awaiting_payment', 'Awaiting payment'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('filed', 'Filed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'form_response'
        app_label = 'forms'
        base_manager_name = 'unscoped'
        verbose_name = 'Submitted form (keeps the version it was submitted on; filed to the Daybook time'


class MeetingBooking(CedaModel):
    """Booked slot for a parent with a teacher (clash prevention; interpreter; attendance and notes to the learner timeline)"""

    ceda_entity = 'meeting_booking'
    ceda_zones = ('ops',)
    ceda_domain = 'FRM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'meeting_event_id': {'type': 'ref', 'ref': 'meeting_event'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'starts_at': {'type': 'ts'}, 'mode': {'type': 'enum', 'enum': 'meeting_mode'}, 'interpreter_language': {'type': 'lang'}, 'video_room_ref': {'type': 'str'}, 'recording_consent_all': {'type': 'bool'}, 'attended': {'type': 'bool'}, 'note': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'booking_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    meeting_event = models.ForeignKey("forms.MeetingEvent", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='meeting_event_id')
    staff_id = cf.UUID7Field()
    guardian_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    starts_at = models.DateTimeField()
    mode = models.CharField(max_length=32, choices=[('in_person', 'In person'), ('video', 'Video'), ('hybrid', 'Hybrid')])
    interpreter_language = models.CharField(max_length=35, null=True, blank=True)
    video_room_ref = models.CharField(max_length=200, null=True, blank=True)
    recording_consent_all = models.BooleanField(default=False)
    attended = models.BooleanField(null=True, blank=True)
    note = models.CharField(max_length=1000, null=True, blank=True)
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
        db_table = 'meeting_booking'
        app_label = 'forms'
        base_manager_name = 'unscoped'
        verbose_name = 'Booked slot for a parent with a teacher (clash prevention; interpreter; attendan'


class MeetingEvent(CedaModel):
    """Parents' meeting event across one or more days (in-person, video and hybrid slots per teacher)"""

    ceda_entity = 'meeting_event'
    ceda_zones = ('ops',)
    ceda_domain = 'FRM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'class_group_ids': {'type': 'json'}, 'days': {'type': 'json'}, 'slot_minutes': {'type': 'smallint'}, 'travel_gap_minutes': {'type': 'smallint'}, 'modes': {'type': 'json'}, 'booking_opens_at': {'type': 'ts'}, 'booking_closes_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    class_group_ids = models.JSONField()
    days = models.JSONField(help_text='Dates and session windows')
    slot_minutes = models.SmallIntegerField()
    travel_gap_minutes = models.SmallIntegerField(default=5)
    modes = models.JSONField(help_text='in_person, video, hybrid')
    booking_opens_at = models.DateTimeField()
    booking_closes_at = models.DateTimeField()
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
        db_table = 'meeting_event'
        app_label = 'forms'
        base_manager_name = 'unscoped'
        verbose_name = "Parents' meeting event across one or more days (in-person, video and hybrid slot"
