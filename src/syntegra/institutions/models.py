"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``institutions`` — Institution 360, state institution register, licensing, inspection and compliance.
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



class Campus(CedaModel):
    """Campus / site / branch of an institution"""

    ceda_entity = 'campus'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'name': {'type': 'title'}, 'address': {'type': 'json'}, 'location': {'type': 'point'}, 'is_main': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    name = models.CharField(max_length=300)
    address = models.JSONField(null=True, blank=True)
    location = cf.PointField(null=True, blank=True)
    is_main = models.BooleanField(default=False)
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
        db_table = 'campus'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Campus / site / branch of an institution'


class ComplianceRequirement(CedaModel):
    """Compliance requirement inherited down the policy hierarchy (fire, health and safety, certifications with expiry)"""

    ceda_entity = 'compliance_requirement'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'requirement_key': {'type': 'code'}, 'title': {'type': 'title'}, 'category': {'type': 'enum', 'enum': 'compliance_category'}, 'applies_to': {'type': 'json'}, 'evidence_required': {'type': 'text'}, 'renewal_months': {'type': 'smallint'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    requirement_key = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    category = models.CharField(max_length=32, choices=[('fire', 'Fire'), ('health_safety', 'Health safety'), ('structural', 'Structural'), ('food_hygiene', 'Food hygiene'), ('transport', 'Transport'), ('statutory_certification', 'Statutory certification'), ('data_protection', 'Data protection'), ('safeguarding', 'Safeguarding')])
    applies_to = models.JSONField(help_text='Institution categories, levels, ownership')
    evidence_required = models.TextField(null=True, blank=True)
    renewal_months = models.SmallIntegerField(null=True, blank=True)
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
        db_table = 'compliance_requirement'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Compliance requirement inherited down the policy hierarchy (fire, health and saf'


class ComplianceStatus(CedaModel):
    """Status of one compliance requirement at one institution (Compliant, Attention required, Overdue, Critical)"""

    ceda_entity = 'compliance_status'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'requirement_id': {'type': 'ref', 'ref': 'compliance_requirement'}, 'evidence_document_id': {'type': 'uuid'}, 'certified_on': {'type': 'date'}, 'expires_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'compliance_state'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    requirement = models.ForeignKey("institutions.ComplianceRequirement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requirement_id')
    evidence_document_id = cf.UUID7Field(null=True, blank=True)
    certified_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('compliant', 'Compliant'), ('attention_required', 'Attention required'), ('overdue', 'Overdue'), ('critical', 'Critical')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'compliance_status'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Status of one compliance requirement at one institution (Compliant, Attention re'


class CorrectiveAction(CedaModel):
    """Corrective action plan item (from findings, approval conditions, compliance or curriculum alerts)"""

    ceda_entity = 'corrective_action'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'source_kind': {'type': 'enum', 'enum': 'action_source'}, 'source_id': {'type': 'uuid'}, 'description': {'type': 'text'}, 'owner_user_id': {'type': 'ref', 'ref': 'app_user'}, 'due_on': {'type': 'date'}, 'evidence_document_ids': {'type': 'json'}, 'verified_by': {'type': 'ref', 'ref': 'app_user'}, 'verified_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'action_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    source_kind = models.CharField(max_length=32, choices=[('inspection_finding', 'Inspection finding'), ('approval_condition', 'Approval condition'), ('compliance', 'Compliance'), ('curriculum_alert', 'Curriculum alert'), ('alert', 'Alert'), ('intervention_workflow', 'Intervention workflow')])
    source_id = cf.UUID7Field()
    description = models.TextField()
    owner_user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='owner_user_id', null=True, blank=True)
    due_on = models.DateField()
    evidence_document_ids = models.JSONField(null=True, blank=True)
    verified_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='verified_by', null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('plan_submitted', 'Plan submitted'), ('plan_approved', 'Plan approved'), ('in_progress', 'In progress'), ('evidence_submitted', 'Evidence submitted'), ('verified', 'Verified'), ('overdue', 'Overdue'), ('closed', 'Closed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'corrective_action'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Corrective action plan item (from findings, approval conditions, compliance or c'


class FacilityCheck(CedaModel):
    """Fire inspection, health and safety check or certification with expiry (compliance centre evidence)"""

    ceda_entity = 'facility_check'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'campus_id': {'type': 'ref', 'ref': 'campus'}, 'check_kind': {'type': 'cl', 'code_list': 'facility_check_kind'}, 'performed_on': {'type': 'date'}, 'performed_by': {'type': 'str'}, 'result': {'type': 'enum', 'enum': 'check_result'}, 'certificate_document_id': {'type': 'uuid'}, 'expires_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    campus = models.ForeignKey("institutions.Campus", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='campus_id', null=True, blank=True)
    check_kind = models.CharField(max_length=32)
    performed_on = models.DateField()
    performed_by = models.CharField(max_length=200, null=True, blank=True)
    result = models.CharField(max_length=32, choices=[('pass', 'Pass'), ('pass_with_actions', 'Pass with actions'), ('fail', 'Fail')])
    certificate_document_id = cf.UUID7Field(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'facility_check'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Fire inspection, health and safety check or certification with expiry (complianc'


class HealthIndexPolicy(CedaModel):
    """Versioned health-index weights, targets and bands (decomposable score, P8)"""

    ceda_entity = 'health_index_policy'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'version': {'type': 'int_u'}, 'weights': {'type': 'json'}, 'targets': {'type': 'json'}, 'bands': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'effective_from': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    version = models.PositiveIntegerField()
    weights = models.JSONField(help_text='Indicator → weight (attendance, progress, exam outcomes … resource utilisation)')
    targets = models.JSONField(help_text='Indicator → normalisation target')
    bands = models.JSONField(help_text='strong ≥ 80, adequate 65–79, concern 50–64, critical < 50')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    effective_from = models.DateField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'health_index_policy'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned health-index weights, targets and bands (decomposable score, P8)'


class Inspection(CedaModel):
    """Inspection 360 — approval, routine, monitoring or follow-up inspection"""

    ceda_entity = 'inspection'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'kind': {'type': 'enum', 'enum': 'inspection_kind'}, 'programme_id': {'type': 'ref', 'ref': 'inspection_programme'}, 'provider_application_id': {'type': 'ref', 'ref': 'provider_application'}, 'scheduled_on': {'type': 'date'}, 'lead_inspector_id': {'type': 'ref', 'ref': 'staff'}, 'risk_score': {'type': 'score'}, 'briefing': {'type': 'json'}, 'overall_judgement': {'type': 'cl', 'code_list': 'inspection_judgement'}, 'report_document_id': {'type': 'uuid'}, 'visited_location': {'type': 'point'}, 'status': {'type': 'enum', 'enum': 'inspection_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    kind = models.CharField(max_length=32, choices=[('approval', 'Approval'), ('routine', 'Routine'), ('monitoring', 'Monitoring'), ('follow_up', 'Follow up'), ('thematic', 'Thematic'), ('renewal', 'Renewal')])
    programme = models.ForeignKey("institutions.InspectionProgramme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id', null=True, blank=True)
    provider_application = models.ForeignKey("providers.ProviderApplication", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='provider_application_id', null=True, blank=True)
    scheduled_on = models.DateField()
    lead_inspector = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lead_inspector_id', null=True, blank=True)
    risk_score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    briefing = models.JSONField(null=True, blank=True, help_text='Briefing pack snapshot (coverage, gaps, data, history, complaints)')
    overall_judgement = models.CharField(max_length=32, null=True, blank=True)
    report_document_id = cf.UUID7Field(null=True, blank=True)
    visited_location = cf.PointField(null=True, blank=True, help_text='GPS captured on site')
    status = models.CharField(max_length=32, choices=[('planned', 'Planned'), ('scheduled', 'Scheduled'), ('in_progress', 'In progress'), ('report_draft', 'Report draft'), ('report_approved', 'Report approved'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'inspection'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Inspection 360 — approval, routine, monitoring or follow-up inspection'


class InspectionFinding(CedaModel):
    """Finding recorded during an inspection (with photos and GPS evidence)"""

    ceda_entity = 'inspection_finding'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'inspection_id': {'type': 'ref', 'ref': 'inspection'}, 'area': {'type': 'cl', 'code_list': 'inspection_area'}, 'judgement': {'type': 'cl', 'code_list': 'inspection_judgement'}, 'evidence': {'type': 'text'}, 'evidence_document_ids': {'type': 'json'}, 'requires_action': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    inspection = models.ForeignKey("institutions.Inspection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='inspection_id')
    area = models.CharField(max_length=32)
    judgement = models.CharField(max_length=32)
    evidence = models.TextField()
    evidence_document_ids = models.JSONField(null=True, blank=True)
    requires_action = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'inspection_finding'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Finding recorded during an inspection (with photos and GPS evidence)'


class InspectionProgramme(CedaModel):
    """Risk-based inspection programme for a period, for inspectorate approval"""

    ceda_entity = 'inspection_programme'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'period_start': {'type': 'date'}, 'period_end': {'type': 'date'}, 'method': {'type': 'json'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    period_start = models.DateField()
    period_end = models.DateField()
    method = models.JSONField(null=True, blank=True, help_text='Weights: health index, compliance, alerts, time since last inspection')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
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
        db_table = 'inspection_programme'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Risk-based inspection programme for a period, for inspectorate approval'


class Institution(CedaModel):
    """Institution 360 master (public and private, every level)"""

    ceda_entity = 'institution'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_code': {'type': 'code'}, 'gov_reg_no': {'type': 'code'}, 'name': {'type': 'title'}, 'short_name': {'type': 'str'}, 'category': {'type': 'cl', 'code_list': 'institution_category'}, 'ownership': {'type': 'cl', 'code_list': 'ownership'}, 'is_public': {'type': 'bool'}, 'operating_tenant_id': {'type': 'uuid'}, 'provider_id': {'type': 'ref', 'ref': 'provider'}, 'network_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'lga_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'levels': {'type': 'cls', 'code_list': 'education_level'}, 'day_boarding': {'type': 'enum', 'enum': 'day_boarding'}, 'gender_intake': {'type': 'enum', 'enum': 'gender_intake'}, 'address': {'type': 'json'}, 'location': {'type': 'point'}, 'location_class': {'type': 'enum', 'enum': 'location_class'}, 'capacity': {'type': 'int_u'}, 'head_staff_id': {'type': 'ref', 'ref': 'staff'}, 'website': {'type': 'url'}, 'phone': {'type': 'phone'}, 'email': {'type': 'email'}, 'onboarding_status': {'type': 'enum', 'enum': 'onboarding_status'}, 'regulatory_status': {'type': 'enum', 'enum': 'regulatory_status'}, 'status': {'type': 'enum', 'enum': 'institution_status'}, 'merged_into': {'type': 'ref', 'ref': 'institution'}, 'is_regularisation': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_code = models.CharField(max_length=20, help_text='INS-<country>-NNNNNN')
    gov_reg_no = models.CharField(max_length=40, null=True, blank=True, help_text='Government registration number, e.g. AB/SS/0412')
    name = models.CharField(max_length=300)
    short_name = models.CharField(max_length=80, null=True, blank=True)
    category = models.CharField(max_length=32, help_text='ECCDE, primary, JSS, SSS, technical college, college of education, polytechnic, university, nursing, non-formal …')
    ownership = models.CharField(max_length=32, help_text='federal, state, lga, private, faith, community, ngo')
    is_public = models.BooleanField(help_text='Derived from ownership; drives the financing channel')
    operating_tenant_id = cf.UUID7Field(help_text='Tenant whose ops zone runs the institution (state for public; provider tenant for private)')
    provider = models.ForeignKey("providers.Provider", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='provider_id', null=True, blank=True)
    network_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='network_scope_id', null=True, blank=True)
    lga_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lga_scope_id')
    levels = models.JSONField(help_text='Education levels offered')
    day_boarding = models.CharField(max_length=32, choices=[('day', 'Day'), ('boarding', 'Boarding'), ('mixed', 'Mixed')], null=True, blank=True)
    gender_intake = models.CharField(max_length=32, choices=[('mixed', 'Mixed'), ('boys', 'Boys'), ('girls', 'Girls')], null=True, blank=True)
    address = models.JSONField(help_text='Structured address (street, town, LGA, state, postcode)')
    location = cf.PointField(null=True, blank=True, help_text='WGS84; NOT NULL once surveyed (500 m / 5 km duplicate checks)')
    location_class = models.CharField(max_length=32, choices=[('urban', 'Urban'), ('peri_urban', 'Peri urban'), ('rural', 'Rural')], null=True, blank=True, help_text='urban, peri-urban, rural (comparison context)')
    capacity = models.PositiveIntegerField(null=True, blank=True)
    head_staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='head_staff_id', null=True, blank=True)
    website = models.CharField(max_length=2048, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    onboarding_status = models.CharField(max_length=32, choices=[('not_onboarded', 'Not onboarded'), ('onboarding', 'Onboarding'), ('live', 'Live'), ('suspended', 'Suspended'), ('closed', 'Closed')], help_text='Not yet onboarded, Onboarding, Live, Suspended, Closed')
    regulatory_status = models.CharField(max_length=32, choices=[('approved', 'Approved'), ('approved_with_conditions', 'Approved with conditions'), ('regularising', 'Regularising'), ('suspended', 'Suspended'), ('closed', 'Closed'), ('unregistered', 'Unregistered'), ('public_owned', 'Public owned')], help_text='approved, approved_with_conditions, regularising, suspended, closed, unregistered')
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('active', 'Active'), ('suspended', 'Suspended'), ('closed', 'Closed'), ('merged', 'Merged')])
    merged_into = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='merged_into', null=True, blank=True)
    is_regularisation = models.BooleanField(default=False, help_text='Existing unregistered institution brought into compliance')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'institution'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Institution 360 master (public and private, every level)'


class InstitutionChangeRequest(CedaModel):
    """Change request to an institution's master fields (name, registration number, ownership, category, address, coordinates)"""

    ceda_entity = 'institution_change_request'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'field_changes': {'type': 'json'}, 'reason': {'type': 'text'}, 'evidence_document_id': {'type': 'uuid'}, 'requested_by': {'type': 'ref', 'ref': 'app_user'}, 'decided_by': {'type': 'ref', 'ref': 'app_user'}, 'decided_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    field_changes = models.JSONField(help_text='[{field, from, to}]')
    reason = models.TextField()
    evidence_document_id = cf.UUID7Field(null=True, blank=True)
    requested_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requested_by')
    decided_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='decided_by', null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('in_review', 'In review'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled'), ('fulfilled', 'Fulfilled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'institution_change_request'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = "Change request to an institution's master fields (name, registration number, own"


class InstitutionProfile(CedaModel):
    """Comparison context of an institution (level, ownership, location band, size, PTR, infrastructure band, share with additional needs)"""

    ceda_entity = 'institution_profile'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'projection'
    ceda_class = 'internal'
    ceda_history = 'snapshot'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'as_of': {'type': 'date'}, 'comparison_group': {'type': 'code'}, 'enrolment_band': {'type': 'code'}, 'ptr_band': {'type': 'code'}, 'infrastructure_band': {'type': 'code'}, 'additional_needs_share': {'type': 'pct'}, 'context': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    as_of = models.DateField()
    comparison_group = models.CharField(max_length=60, help_text='Group within which ranking is allowed')
    enrolment_band = models.CharField(max_length=16, null=True, blank=True)
    ptr_band = models.CharField(max_length=16, null=True, blank=True)
    infrastructure_band = models.CharField(max_length=16, null=True, blank=True)
    additional_needs_share = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    context = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'institution_profile'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Comparison context of an institution (level, ownership, location band, size, PTR'


class Licence(CedaModel):
    """Licence, accreditation or authorisation (operating licence, exam centre, certificate issuer, programme accreditation)"""

    ceda_entity = 'licence'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'kind': {'type': 'enum', 'enum': 'licence_kind'}, 'licence_number': {'type': 'code'}, 'issuing_body': {'type': 'cl', 'code_list': 'regulator'}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'scope_detail': {'type': 'json'}, 'conditions': {'type': 'text'}, 'issued_on': {'type': 'date'}, 'expires_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'licence_status'}, 'approval_id': {'type': 'ref', 'ref': 'approval'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    kind = models.CharField(max_length=32, choices=[('operating_licence', 'Operating licence'), ('private_approval', 'Private approval'), ('accreditation', 'Accreditation'), ('exam_centre', 'Exam centre'), ('certificate_issuer', 'Certificate issuer'), ('programme_accreditation', 'Programme accreditation'), ('federal_approval', 'Federal approval')])
    licence_number = models.CharField(max_length=60)
    issuing_body = models.CharField(max_length=32, help_text='State MoE, NBTE, NCCE, NUC, MDCN, NMCN, WAEC (centre) …')
    programme = models.ForeignKey("academic.Programme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id', null=True, blank=True)
    scope_detail = models.JSONField(null=True, blank=True, help_text='Levels, programmes or subjects covered')
    conditions = models.TextField(null=True, blank=True)
    issued_on = models.DateField()
    expires_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('valid', 'Valid'), ('expiring', 'Expiring'), ('expired', 'Expired'), ('suspended', 'Suspended'), ('revoked', 'Revoked')], help_text='Expired automatically the day after expiry')
    approval = models.ForeignKey("providers.Approval", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approval_id', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'licence'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Licence, accreditation or authorisation (operating licence, exam centre, certifi'


class OnboardingCheck(CedaModel):
    """Onboarding readiness step of an institution (structure, staff, learners matched, curriculum adopted, first register, first results)"""

    ceda_entity = 'onboarding_check'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'step': {'type': 'enum', 'enum': 'onboarding_step'}, 'target_on': {'type': 'date'}, 'completed_at': {'type': 'ts'}, 'blocking_reason': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'step_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    step = models.CharField(max_length=32, choices=[('structure_set_up', 'Structure set up'), ('staff_loaded', 'Staff loaded'), ('learners_loaded', 'Learners loaded'), ('learners_matched', 'Learners matched'), ('curriculum_adopted', 'Curriculum adopted'), ('first_register', 'First register'), ('first_results', 'First results'), ('live', 'Live')])
    target_on = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    blocking_reason = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('not_started', 'Not started'), ('in_progress', 'In progress'), ('done', 'Done'), ('blocked', 'Blocked'), ('not_applicable', 'Not applicable')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'onboarding_check'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Onboarding readiness step of an institution (structure, staff, learners matched,'


class OnboardingTarget(CedaModel):
    """Onboarding target date and wave per LGA (state rollout in LGA waves)"""

    ceda_entity = 'onboarding_target'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'lga_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'wave': {'type': 'smallint'}, 'target_live_on': {'type': 'date'}, 'readiness_gate': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    lga_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lga_scope_id')
    wave = models.SmallIntegerField()
    target_live_on = models.DateField()
    readiness_gate = models.JSONField(null=True, blank=True, help_text='Gate criteria for the wave')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'onboarding_target'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Onboarding target date and wave per LGA (state rollout in LGA waves)'


class OrgUnit(CedaModel):
    """Faculty / school / department / unit (effective-dated tree, cost centres and heads)"""

    ceda_entity = 'org_unit'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'campus_id': {'type': 'ref', 'ref': 'campus'}, 'parent_id': {'type': 'ref', 'ref': 'org_unit'}, 'unit_type': {'type': 'enum', 'enum': 'unit_type'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'head_staff_id': {'type': 'ref', 'ref': 'staff'}, 'acting_head_staff_id': {'type': 'ref', 'ref': 'staff'}, 'cost_centre': {'type': 'code'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    campus = models.ForeignKey("institutions.Campus", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='campus_id', null=True, blank=True)
    parent = models.ForeignKey("institutions.OrgUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_id', null=True, blank=True)
    unit_type = models.CharField(max_length=32, choices=[('faculty', 'Faculty'), ('school', 'School'), ('department', 'Department'), ('unit', 'Unit'), ('centre', 'Centre'), ('house', 'House'), ('year_group', 'Year group')])
    code = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=300)
    head_staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='head_staff_id', null=True, blank=True)
    acting_head_staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='acting_head_staff_id', null=True, blank=True)
    cost_centre = models.CharField(max_length=32, null=True, blank=True)
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
        db_table = 'org_unit'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Faculty / school / department / unit (effective-dated tree, cost centres and hea'


class UnknownInstitutionReference(CedaModel):
    """Reference to an institution not on the register (transfer, exam entry, certificate) — alert to the regulator"""

    ceda_entity = 'unknown_institution_reference'
    ceda_zones = ('registry',)
    ceda_domain = 'INS'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'source_kind': {'type': 'enum', 'enum': 'unknown_ref_source'}, 'source_id': {'type': 'uuid'}, 'reported_name': {'type': 'title'}, 'reported_address': {'type': 'str'}, 'lga_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'alert_id': {'type': 'uuid'}, 'resolved_institution_id': {'type': 'ref', 'ref': 'institution'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    source_kind = models.CharField(max_length=32, choices=[('transfer', 'Transfer'), ('exam_entry', 'Exam entry'), ('certificate', 'Certificate'), ('digitisation', 'Digitisation'), ('application', 'Application')])
    source_id = cf.UUID7Field()
    reported_name = models.CharField(max_length=300)
    reported_address = models.CharField(max_length=500, null=True, blank=True)
    lga_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lga_scope_id', null=True, blank=True)
    alert_id = cf.UUID7Field(null=True, blank=True, help_text='Alert raised to the regulator')
    resolved_institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='resolved_institution_id', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'unknown_institution_reference'
        app_label = 'institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Reference to an institution not on the register (transfer, exam entry, certifica'
