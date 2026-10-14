"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``operations`` — Operations.
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



class Activity(CedaModel):
    """Club, activity or event with eligibility, capacity, fees and achievements"""

    ceda_entity = 'activity'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'activity_kind': {'type': 'enum', 'enum': 'activity_kind'}, 'eligibility_rule': {'type': 'json'}, 'capacity': {'type': 'smallint'}, 'fee_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'allocation_method': {'type': 'enum', 'enum': 'allocation_method_fair'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    activity_kind = models.CharField(max_length=32, choices=[('club', 'Club'), ('sport', 'Sport'), ('event', 'Event'), ('trip_series', 'Trip series'), ('holiday_programme', 'Holiday programme')])
    eligibility_rule = models.JSONField(null=True, blank=True)
    capacity = models.SmallIntegerField(null=True, blank=True)
    fee_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    allocation_method = models.CharField(max_length=32, choices=[('first_come', 'First come'), ('preference_lottery', 'Preference lottery'), ('priority_rules', 'Priority rules')])
    period_id = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'activity'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Club, activity or event with eligibility, capacity, fees and achievements'


class ActivityEnrolment(CedaModel):
    """Learner preference, allocation, waiting list and attendance for an activity"""

    ceda_entity = 'activity_enrolment'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'activity_id': {'type': 'ref', 'ref': 'activity'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'preference_rank': {'type': 'smallint'}, 'allocation': {'type': 'enum', 'enum': 'allocation_outcome'}, 'waiting_position': {'type': 'smallint'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'sessions_attended': {'type': 'smallint'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    activity = models.ForeignKey("operations.Activity", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='activity_id')
    learner_id = cf.UUID7Field()
    preference_rank = models.SmallIntegerField(null=True, blank=True)
    allocation = models.CharField(max_length=32, choices=[('preferred', 'Preferred'), ('allocated', 'Allocated'), ('waitlisted', 'Waitlisted'), ('declined', 'Declined'), ('withdrawn', 'Withdrawn')])
    waiting_position = models.SmallIntegerField(null=True, blank=True)
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id', null=True, blank=True)
    sessions_attended = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'activity_enrolment'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner preference, allocation, waiting list and attendance for an activity'


class Asset(CedaModel):
    """Asset register entry (custodian, location, value, condition, service and safety-check dates)"""

    ceda_entity = 'asset'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'asset_tag': {'type': 'code'}, 'name': {'type': 'title'}, 'category': {'type': 'cl', 'code_list': 'asset_category'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'custodian_staff_id': {'type': 'ref', 'ref': 'staff'}, 'acquired_on': {'type': 'date'}, 'value_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'condition_grade': {'type': 'cl', 'code_list': 'condition_grade'}, 'next_service_on': {'type': 'date'}, 'safety_check_due_on': {'type': 'date'}, 'predicted_failure_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'asset_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    asset_tag = models.CharField(max_length=40)
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=32)
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    custodian_staff_id = cf.UUID7Field(null=True, blank=True)
    acquired_on = models.DateField(null=True, blank=True)
    value_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    condition_grade = models.CharField(max_length=32, null=True, blank=True)
    next_service_on = models.DateField(null=True, blank=True)
    safety_check_due_on = models.DateField(null=True, blank=True, help_text='Equipment past this date cannot be allocated (FR-TVT-02)')
    predicted_failure_on = models.DateField(null=True, blank=True, help_text='Predictive maintenance estimate')
    status = models.CharField(max_length=32, choices=[('in_use', 'In use'), ('in_store', 'In store'), ('under_repair', 'Under repair'), ('condemned', 'Condemned'), ('disposed', 'Disposed'), ('lost', 'Lost')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'asset'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Asset register entry (custodian, location, value, condition, service and safety-'


class AssetInspection(CedaModel):
    """Technician inspection of an asset (mobile, offline, checklist and photos) or stock-take record"""

    ceda_entity = 'asset_inspection'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'asset_id': {'type': 'ref', 'ref': 'asset'}, 'inspected_by': {'type': 'uuid'}, 'checklist': {'type': 'json'}, 'photo_document_ids': {'type': 'json'}, 'condition_grade': {'type': 'cl', 'code_list': 'condition_grade'}, 'inspected_at': {'type': 'ts'}, 'client_op_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    asset = models.ForeignKey("operations.Asset", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='asset_id')
    inspected_by = cf.UUID7Field()
    checklist = models.JSONField()
    photo_document_ids = models.JSONField(null=True, blank=True)
    condition_grade = models.CharField(max_length=32)
    inspected_at = models.DateTimeField()
    client_op_id = cf.UUID7Field(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'asset_inspection'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Technician inspection of an asset (mobile, offline, checklist and photos) or sto'


class BoardingRecord(CedaModel):
    """Boarding or alighting record on a route"""

    ceda_entity = 'boarding_record'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = {'type': 'range_month', 'column': 'boarded_on'}
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'route_id': {'type': 'ref', 'ref': 'transport_route'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'boarded_on': {'type': 'date'}, 'event': {'type': 'enum', 'enum': 'boarding_event'}, 'at': {'type': 'ts'}, 'recorded_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    route_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    boarded_on = models.DateField()
    event = models.CharField(max_length=32, choices=[('boarded', 'Boarded'), ('alighted', 'Alighted'), ('no_show', 'No show')])
    at = models.DateTimeField()
    recorded_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('id', 'boarded_on')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'boarding_record'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Boarding or alighting record on a route'


class Building(CedaModel):
    """Building on a campus (condition, structural safety, water, power, toilets by sex)"""

    ceda_entity = 'building'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'campus_id': {'type': 'ref', 'ref': 'campus'}, 'name': {'type': 'title'}, 'built_year': {'type': 'smallint'}, 'condition_grade': {'type': 'cl', 'code_list': 'condition_grade'}, 'facilities': {'type': 'json'}, 'plan_document_ids': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    campus_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    built_year = models.SmallIntegerField(null=True, blank=True)
    condition_grade = models.CharField(max_length=32, null=True, blank=True)
    facilities = models.JSONField(null=True, blank=True, help_text='Toilets by sex, water, power, accessibility')
    plan_document_ids = models.JSONField(null=True, blank=True, help_text='Campus plan archive over time')
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
        db_table = 'building'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Building on a campus (condition, structural safety, water, power, toilets by sex'


class CapitalPlanItem(CedaModel):
    """Multi-year capital plan item linked to asset and building condition (cost estimate and priority)"""

    ceda_entity = 'capital_plan_item'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'building_id': {'type': 'ref', 'ref': 'building'}, 'asset_id': {'type': 'ref', 'ref': 'asset'}, 'title': {'type': 'title'}, 'planned_year': {'type': 'smallint'}, 'estimate_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'priority': {'type': 'smallint'}, 'status': {'type': 'enum', 'enum': 'work_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    building = models.ForeignKey("operations.Building", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='building_id', null=True, blank=True)
    asset = models.ForeignKey("operations.Asset", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='asset_id', null=True, blank=True)
    title = models.CharField(max_length=300)
    planned_year = models.SmallIntegerField()
    estimate_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    priority = models.SmallIntegerField()
    status = models.CharField(max_length=32, choices=[('reported', 'Reported'), ('triaged', 'Triaged'), ('scheduled', 'Scheduled'), ('in_progress', 'In progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'capital_plan_item'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Multi-year capital plan item linked to asset and building condition (cost estima'


class DietaryRequirement(CedaModel):
    """Learner dietary requirement (allergy detail is health data — kept as a coded flag here)"""

    ceda_entity = 'dietary_requirement'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'requirement': {'type': 'cl', 'code_list': 'dietary_code'}, 'is_allergy': {'type': 'bool'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    requirement = models.CharField(max_length=32)
    is_allergy = models.BooleanField(default=False)
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
        db_table = 'dietary_requirement'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner dietary requirement (allergy detail is health data — kept as a coded fla'


class FacilityIncident(CedaModel):
    """Facility safety incident (location, severity, photos, follow-up)"""

    ceda_entity = 'facility_incident'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'location_text': {'type': 'str'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'description': {'type': 'text'}, 'photo_document_ids': {'type': 'json'}, 'occurred_at': {'type': 'ts'}, 'follow_up': {'type': 'text'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    location_text = models.CharField(max_length=200, null=True, blank=True)
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    description = models.TextField()
    photo_document_ids = models.JSONField(null=True, blank=True)
    occurred_at = models.DateTimeField()
    follow_up = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('in_progress', 'In progress'), ('on_hold', 'On hold'), ('closed', 'Closed'), ('transferred', 'Transferred')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'facility_incident'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Facility safety incident (location, severity, photos, follow-up)'


class LearningResource(CedaModel):
    """Textbook or learning material title held in stock (government-supplied or institution-bought) by subject and level"""

    ceda_entity = 'learning_resource'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'source': {'type': 'enum', 'enum': 'resource_source'}, 'stock': {'type': 'int_u'}, 'content_library_item_id': {'type': 'ref', 'ref': 'content_library_item'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    subject_id = cf.UUID7Field()
    education_level = models.CharField(max_length=32)
    source = models.CharField(max_length=32, choices=[('government_supplied', 'Government supplied'), ('institution_bought', 'Institution bought'), ('donated', 'Donated')])
    stock = models.PositiveIntegerField()
    content_library_item_id = cf.UUID7Field(null=True, blank=True, help_text='Digital resource linked to objectives')
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
        db_table = 'learning_resource'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Textbook or learning material title held in stock (government-supplied or instit'


class LibraryItem(CedaModel):
    """Library catalogue item (or link to an external library system)"""

    ceda_entity = 'library_item'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'authors': {'type': 'str'}, 'isbn': {'type': 'code'}, 'copies': {'type': 'smallint'}, 'external_ref': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    authors = models.CharField(max_length=500, null=True, blank=True)
    isbn = models.CharField(max_length=17, null=True, blank=True)
    copies = models.SmallIntegerField()
    external_ref = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'library_item'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Library catalogue item (or link to an external library system)'


class LibraryLoan(CedaModel):
    """Library loan"""

    ceda_entity = 'library_loan'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'library_item_id': {'type': 'ref', 'ref': 'library_item'}, 'borrower_kind': {'type': 'enum', 'enum': 'person_kind'}, 'borrower_id': {'type': 'uuid'}, 'loaned_on': {'type': 'date'}, 'due_on': {'type': 'date'}, 'returned_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    library_item = models.ForeignKey("operations.LibraryItem", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='library_item_id')
    borrower_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    borrower_id = cf.UUID7Field()
    loaned_on = models.DateField()
    due_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'library_loan'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Library loan'


class MaintenanceRequest(CedaModel):
    """Maintenance request with safety-risk rating (critical → Priority 1 to head and LGA); preventive work orders"""

    ceda_entity = 'maintenance_request'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'asset_id': {'type': 'ref', 'ref': 'asset'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'description': {'type': 'text'}, 'risk': {'type': 'enum', 'enum': 'severity'}, 'is_preventive': {'type': 'bool'}, 'reported_by': {'type': 'uuid'}, 'assigned_to': {'type': 'uuid'}, 'due_on': {'type': 'date'}, 'completed_at': {'type': 'ts'}, 'cost_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'work_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    asset = models.ForeignKey("operations.Asset", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='asset_id', null=True, blank=True)
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    description = models.TextField()
    risk = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    is_preventive = models.BooleanField(default=False)
    reported_by = cf.UUID7Field()
    assigned_to = cf.UUID7Field(null=True, blank=True)
    due_on = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('reported', 'Reported'), ('triaged', 'Triaged'), ('scheduled', 'Scheduled'), ('in_progress', 'In progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'maintenance_request'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Maintenance request with safety-risk rating (critical → Priority 1 to head and L'


class MealService(CedaModel):
    """Meals served per day and session (school feeding programme numbers reconciled against attendance)"""

    ceda_entity = 'meal_service'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'served_on': {'type': 'date'}, 'meal_session': {'type': 'enum', 'enum': 'meal_session'}, 'programme': {'type': 'cl', 'code_list': 'feeding_programme'}, 'meals_served': {'type': 'int_u'}, 'learners_present': {'type': 'int_u'}, 'menu': {'type': 'json'}, 'variance_note': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    served_on = models.DateField()
    meal_session = models.CharField(max_length=32, choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('snack', 'Snack'), ('dinner', 'Dinner')])
    programme = models.CharField(max_length=32, null=True, blank=True)
    meals_served = models.PositiveIntegerField()
    learners_present = models.PositiveIntegerField(null=True, blank=True, help_text='From attendance')
    menu = models.JSONField(null=True, blank=True)
    variance_note = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'meal_service'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Meals served per day and session (school feeding programme numbers reconciled ag'


class ResourceIssue(CedaModel):
    """Issue, return, loss and condition of a learning resource per learner or class"""

    ceda_entity = 'resource_issue'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'resource_id': {'type': 'ref', 'ref': 'learning_resource'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'quantity': {'type': 'smallint'}, 'issued_on': {'type': 'date'}, 'returned_on': {'type': 'date'}, 'outcome': {'type': 'enum', 'enum': 'resource_outcome'}, 'condition_grade': {'type': 'cl', 'code_list': 'condition_grade'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    resource = models.ForeignKey("operations.LearningResource", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='resource_id')
    learner_id = cf.UUID7Field(null=True, blank=True)
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id', null=True, blank=True)
    quantity = models.SmallIntegerField(default=1)
    issued_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('returned', 'Returned'), ('lost', 'Lost'), ('damaged', 'Damaged'), ('retained', 'Retained')], null=True, blank=True)
    condition_grade = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'resource_issue'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Issue, return, loss and condition of a learning resource per learner or class'


class Room(CedaModel):
    """Room or space — Infrastructure 360 (classroom, lab, workshop, hall, ICT suite, hostel room, skills lab)"""

    ceda_entity = 'room'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'campus_id': {'type': 'ref', 'ref': 'campus'}, 'building_id': {'type': 'ref', 'ref': 'building'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'room_type': {'type': 'cl', 'code_list': 'room_type'}, 'capacity': {'type': 'smallint'}, 'accessibility': {'type': 'json'}, 'condition_grade': {'type': 'cl', 'code_list': 'condition_grade'}, 'ict': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    campus_id = cf.UUID7Field()
    building = models.ForeignKey("operations.Building", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='building_id', null=True, blank=True)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300, null=True, blank=True)
    room_type = models.CharField(max_length=32)
    capacity = models.SmallIntegerField()
    accessibility = models.JSONField(null=True, blank=True, help_text='step_free, hearing_loop …')
    condition_grade = models.CharField(max_length=32, null=True, blank=True)
    ict = models.JSONField(null=True, blank=True)
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
        db_table = 'room'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Room or space — Infrastructure 360 (classroom, lab, workshop, hall, ICT suite, h'


class TransportAllocation(CedaModel):
    """Learner allocated to a route and stop (detention transport check uses it)"""

    ceda_entity = 'transport_allocation'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'route_id': {'type': 'ref', 'ref': 'transport_route'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'stop_code': {'type': 'code'}, 'direction': {'type': 'enum', 'enum': 'route_direction'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    route = models.ForeignKey("operations.TransportRoute", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='route_id')
    learner_id = cf.UUID7Field()
    stop_code = models.CharField(max_length=16)
    direction = models.CharField(max_length=32, choices=[('to_school', 'To school'), ('from_school', 'From school')])
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
        db_table = 'transport_allocation'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner allocated to a route and stop (detention transport check uses it)'


class TransportRoute(CedaModel):
    """Transport route with stops"""

    ceda_entity = 'transport_route'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'stops': {'type': 'json'}, 'vehicle_id': {'type': 'ref', 'ref': 'vehicle'}, 'driver_staff_id': {'type': 'ref', 'ref': 'staff'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    stops = models.JSONField(help_text='Ordered stops with times and coordinates')
    vehicle = models.ForeignKey("operations.Vehicle", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='vehicle_id', null=True, blank=True)
    driver_staff_id = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'transport_route'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Transport route with stops'


class Trip(CedaModel):
    """Trip or visit (planning, risk assessment, approval, consent, payment, on-the-day register)"""

    ceda_entity = 'trip'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'destination': {'type': 'str'}, 'departs_at': {'type': 'ts'}, 'returns_at': {'type': 'ts'}, 'leader_staff_id': {'type': 'ref', 'ref': 'staff'}, 'risk_assessment_document_id': {'type': 'uuid'}, 'workflow_instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'charge_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'trip_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    destination = models.CharField(max_length=300)
    departs_at = models.DateTimeField()
    returns_at = models.DateTimeField()
    leader_staff_id = cf.UUID7Field(help_text='Must hold valid safeguarding training when gating is on')
    risk_assessment_document_id = cf.UUID7Field(null=True, blank=True)
    workflow_instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='workflow_instance_id', null=True, blank=True)
    charge_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('planning', 'Planning'), ('awaiting_approval', 'Awaiting approval'), ('approved', 'Approved'), ('consent_collection', 'Consent collection'), ('departed', 'Departed'), ('returned', 'Returned'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'trip'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Trip or visit (planning, risk assessment, approval, consent, payment, on-the-day'


class TripParticipant(CedaModel):
    """Learner on a trip (blocked without consent) and on-the-day register"""

    ceda_entity = 'trip_participant'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'trip_id': {'type': 'ref', 'ref': 'trip'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'consent_record_id': {'type': 'ref', 'ref': 'consent_record'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'present_out': {'type': 'bool'}, 'present_return': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    trip = models.ForeignKey("operations.Trip", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='trip_id')
    learner_id = cf.UUID7Field()
    consent_record = models.ForeignKey("families.ConsentRecord", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='consent_record_id', null=True, blank=True)
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id', null=True, blank=True)
    present_out = models.BooleanField(null=True, blank=True)
    present_return = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'trip_participant'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner on a trip (blocked without consent) and on-the-day register'


class Vehicle(CedaModel):
    """Vehicle (registration, capacity, roadworthiness and insurance expiry)"""

    ceda_entity = 'vehicle'
    ceda_zones = ('ops',)
    ceda_domain = 'OPS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'registration': {'type': 'code'}, 'capacity': {'type': 'smallint'}, 'roadworthy_until': {'type': 'date'}, 'insured_until': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    registration = models.CharField(max_length=16)
    capacity = models.SmallIntegerField()
    roadworthy_until = models.DateField(null=True, blank=True)
    insured_until = models.DateField(null=True, blank=True)
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
        db_table = 'vehicle'
        app_label = 'operations'
        base_manager_name = 'unscoped'
        verbose_name = 'Vehicle (registration, capacity, roadworthiness and insurance expiry)'
