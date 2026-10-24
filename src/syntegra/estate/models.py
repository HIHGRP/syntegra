"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``estate`` — Government property register, facility condition and usability, preventive maintenance and proactive actions.
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



class FacilityAction(CedaModel):
    """Proactive action proposed to the head of institution, with owner, due date and escalation to the LGA and ministry"""

    ceda_entity = 'facility_action'
    ceda_zones = ('ops',)
    ceda_domain = 'EST'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'rule': {'type': 'enum', 'enum': 'facility_rule'}, 'subject_kind': {'type': 'enum', 'enum': 'facility_subject'}, 'subject_id': {'type': 'uuid'}, 'dedupe_key': {'type': 'code'}, 'title': {'type': 'str'}, 'detail': {'type': 'text'}, 'priority': {'type': 'enum', 'enum': 'severity'}, 'owner_role': {'type': 'code'}, 'due_on': {'type': 'date'}, 'escalation_level': {'type': 'smallint'}, 'escalated_at': {'type': 'ts'}, 'maintenance_request_id': {'type': 'ref', 'ref': 'maintenance_request'}, 'resolved_by': {'type': 'uuid'}, 'resolved_at': {'type': 'ts'}, 'resolution': {'type': 'text'}, 'status': {'type': 'enum', 'enum': 'facility_action_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    rule = models.CharField(max_length=32, choices=[('unsafe_in_use', 'Unsafe in use'), ('assessment_overdue', 'Assessment overdue'), ('never_assessed', 'Never assessed'), ('maintenance_due', 'Maintenance due'), ('maintenance_overdue', 'Maintenance overdue'), ('condition_deteriorated', 'Condition deteriorated'), ('safety_check_overdue', 'Safety check overdue'), ('predicted_failure', 'Predicted failure'), ('encroachment', 'Encroachment'), ('no_title', 'No title')])
    subject_kind = models.CharField(max_length=32, choices=[('site', 'Site'), ('building', 'Building'), ('room', 'Room'), ('asset', 'Asset')])
    subject_id = cf.UUID7Field()
    dedupe_key = models.CharField(max_length=120, help_text='rule:subject while open; suffixed with the action id when closed')
    title = models.CharField(max_length=200)
    detail = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    owner_role = models.CharField(max_length=16)
    due_on = models.DateField()
    escalation_level = models.SmallIntegerField(default=0, help_text='0 institution, 1 LGA, 2 ministry')
    escalated_at = models.DateTimeField(null=True, blank=True)
    maintenance_request = models.ForeignKey("operations.MaintenanceRequest", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='maintenance_request_id', null=True, blank=True)
    resolved_by = cf.UUID7Field(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('acknowledged', 'Acknowledged'), ('in_progress', 'In progress'), ('done', 'Done'), ('dismissed', 'Dismissed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'facility_action'
        app_label = 'estate'
        base_manager_name = 'unscoped'
        verbose_name = 'Proactive action proposed to the head of institution, with owner, due date and e'


class FacilityAssessment(CedaModel):
    """Dated condition and usability assessment of a site, building, room or item of equipment"""

    ceda_entity = 'facility_assessment'
    ceda_zones = ('ops',)
    ceda_domain = 'EST'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'subject_kind': {'type': 'enum', 'enum': 'facility_subject'}, 'subject_id': {'type': 'uuid'}, 'assessed_on': {'type': 'date'}, 'assessor_kind': {'type': 'enum', 'enum': 'facility_assessor'}, 'assessed_by': {'type': 'uuid'}, 'condition_grade': {'type': 'cl', 'code_list': 'condition_grade'}, 'usability': {'type': 'enum', 'enum': 'usability_status'}, 'structural_risk': {'type': 'enum', 'enum': 'severity'}, 'defects': {'type': 'json'}, 'utilities': {'type': 'json'}, 'in_use': {'type': 'bool'}, 'learners_affected': {'type': 'int_u'}, 'repair_estimate_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'photo_document_ids': {'type': 'json'}, 'next_due_on': {'type': 'date'}, 'client_op_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    subject_kind = models.CharField(max_length=32, choices=[('site', 'Site'), ('building', 'Building'), ('room', 'Room'), ('asset', 'Asset')])
    subject_id = cf.UUID7Field()
    assessed_on = models.DateField()
    assessor_kind = models.CharField(max_length=32, choices=[('head_of_institution', 'Head of institution'), ('estate_officer', 'Estate officer'), ('engineer', 'Engineer'), ('quality_inspector', 'Quality inspector'), ('lga_officer', 'Lga officer'), ('contractor', 'Contractor'), ('community', 'Community')])
    assessed_by = cf.UUID7Field()
    condition_grade = models.CharField(max_length=32)
    usability = models.CharField(max_length=32, choices=[('fully_usable', 'Fully usable'), ('usable_minor_repairs', 'Usable minor repairs'), ('usable_major_repairs', 'Usable major repairs'), ('unsafe_restricted', 'Unsafe restricted'), ('unusable', 'Unusable'), ('condemned', 'Condemned')])
    structural_risk = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    defects = models.JSONField(null=True, blank=True, help_text='Element (roof, walls, floor, doors, windows, wiring, plumbing …), defect and severity')
    utilities = models.JSONField(null=True, blank=True, help_text='Water, power, sanitation and internet working at the time')
    in_use = models.BooleanField(help_text='Whether the facility is being used at the time of assessment')
    learners_affected = models.PositiveIntegerField(null=True, blank=True)
    repair_estimate_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    photo_document_ids = models.JSONField(null=True, blank=True)
    next_due_on = models.DateField(null=True, blank=True, help_text='When it should be assessed again')
    client_op_id = cf.UUID7Field(null=True, blank=True, help_text='Offline capture (idempotent)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'facility_assessment'
        app_label = 'estate'
        base_manager_name = 'unscoped'
        verbose_name = 'Dated condition and usability assessment of a site, building, room or item of eq'


class MaintenanceSchedule(CedaModel):
    """Planned preventive maintenance task for a site, building, room or item of equipment (frequency, next due, responsible person)"""

    ceda_entity = 'maintenance_schedule'
    ceda_zones = ('ops',)
    ceda_domain = 'EST'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'subject_kind': {'type': 'enum', 'enum': 'facility_subject'}, 'subject_id': {'type': 'uuid'}, 'task': {'type': 'str'}, 'task_kind': {'type': 'enum', 'enum': 'maintenance_task_kind'}, 'frequency_days': {'type': 'smallint'}, 'last_done_on': {'type': 'date'}, 'next_due_on': {'type': 'date'}, 'responsible_staff_id': {'type': 'ref', 'ref': 'staff'}, 'estimated_cost_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    subject_kind = models.CharField(max_length=32, choices=[('site', 'Site'), ('building', 'Building'), ('room', 'Room'), ('asset', 'Asset')])
    subject_id = cf.UUID7Field()
    task = models.CharField(max_length=200)
    task_kind = models.CharField(max_length=32, choices=[('inspection', 'Inspection'), ('servicing', 'Servicing'), ('statutory_test', 'Statutory test'), ('cleaning', 'Cleaning'), ('pest_control', 'Pest control'), ('roofing', 'Roofing'), ('plumbing', 'Plumbing'), ('electrical', 'Electrical'), ('painting', 'Painting'), ('generator_service', 'Generator service'), ('solar_service', 'Solar service'), ('borehole_service', 'Borehole service'), ('fire_safety', 'Fire safety'), ('replacement', 'Replacement'), ('other', 'Other')])
    frequency_days = models.SmallIntegerField()
    last_done_on = models.DateField(null=True, blank=True)
    next_due_on = models.DateField()
    responsible_staff_id = cf.UUID7Field(null=True, blank=True)
    estimated_cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
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
        db_table = 'maintenance_schedule'
        app_label = 'estate'
        base_manager_name = 'unscoped'
        verbose_name = 'Planned preventive maintenance task for a site, building, room or item of equipm'


class PropertySite(CedaModel):
    """Government property site (land) used by an institution — owner, title, area, boundary, fencing, encroachment, valuation"""

    ceda_entity = 'property_site'
    ceda_zones = ('ops',)
    ceda_domain = 'EST'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'site_code': {'type': 'code'}, 'name': {'type': 'title'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'campus_id': {'type': 'ref', 'ref': 'campus'}, 'owner': {'type': 'enum', 'enum': 'property_owner'}, 'title_document': {'type': 'enum', 'enum': 'land_title'}, 'title_reference': {'type': 'code'}, 'area_sqm': {'type': 'dec'}, 'location': {'type': 'point'}, 'boundary': {'type': 'json'}, 'fenced': {'type': 'enum', 'enum': 'fence_status'}, 'encroachment': {'type': 'enum', 'enum': 'encroachment_status'}, 'acquired_on': {'type': 'date'}, 'valuation_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'valued_on': {'type': 'date'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    site_code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    institution_id = cf.UUID7Field()
    campus_id = cf.UUID7Field(null=True, blank=True)
    owner = models.CharField(max_length=32, choices=[('federal_government', 'Federal government'), ('state_government', 'State government'), ('local_government', 'Local government'), ('community', 'Community'), ('mission_or_faith', 'Mission or faith'), ('private', 'Private'), ('leased', 'Leased')])
    title_document = models.CharField(max_length=32, choices=[('certificate_of_occupancy', 'Certificate of occupancy'), ('right_of_occupancy', 'Right of occupancy'), ('gazette', 'Gazette'), ('deed_of_assignment', 'Deed of assignment'), ('deed_of_gift', 'Deed of gift'), ('survey_plan_only', 'Survey plan only'), ('customary', 'Customary'), ('lease', 'Lease'), ('none_or_unknown', 'None or unknown')])
    title_reference = models.CharField(max_length=64, null=True, blank=True, help_text='C of O, gazette or survey plan number')
    area_sqm = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    location = cf.PointField(null=True, blank=True)
    boundary = models.JSONField(null=True, blank=True, help_text='GeoJSON polygon of the surveyed boundary')
    fenced = models.CharField(max_length=32, choices=[('fully_fenced', 'Fully fenced'), ('partly_fenced', 'Partly fenced'), ('not_fenced', 'Not fenced'), ('unknown', 'Unknown')])
    encroachment = models.CharField(max_length=32, choices=[('none', 'None'), ('suspected', 'Suspected'), ('confirmed', 'Confirmed'), ('in_dispute', 'In dispute'), ('resolved', 'Resolved'), ('unknown', 'Unknown')])
    acquired_on = models.DateField(null=True, blank=True)
    valuation_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    valued_on = models.DateField(null=True, blank=True)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
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
        db_table = 'property_site'
        app_label = 'estate'
        base_manager_name = 'unscoped'
        verbose_name = 'Government property site (land) used by an institution — owner, title, area, bou'
