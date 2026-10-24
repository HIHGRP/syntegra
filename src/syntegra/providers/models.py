"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``providers`` — Private education provider admission and regulation.
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



class ApplicationEvidence(CedaModel):
    """Evidence item against the approval checklist (pre-checked by document intelligence)"""

    ceda_entity = 'application_evidence'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'application_id': {'type': 'ref', 'ref': 'provider_application'}, 'checklist_item_id': {'type': 'ref', 'ref': 'approval_checklist_item'}, 'document_id': {'type': 'uuid'}, 'ai_precheck': {'type': 'json'}, 'reviewer_status': {'type': 'enum', 'enum': 'evidence_status'}, 'reviewer_note': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    application = models.ForeignKey("providers.ProviderApplication", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='application_id')
    checklist_item = models.ForeignKey("providers.ApprovalChecklistItem", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='checklist_item_id')
    document_id = cf.UUID7Field(help_text='records zone')
    ai_precheck = models.JSONField(null=True, blank=True, help_text='Document-intelligence pre-check result and confidence')
    reviewer_status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('queried', 'Queried'), ('rejected', 'Rejected')])
    reviewer_note = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'application_evidence'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Evidence item against the approval checklist (pre-checked by document intelligen'


class ApplicationQuery(CedaModel):
    """Query sent back to the applicant during desk review, and the reply"""

    ceda_entity = 'application_query'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'application_id': {'type': 'ref', 'ref': 'provider_application'}, 'question': {'type': 'text'}, 'asked_by': {'type': 'ref', 'ref': 'app_user'}, 'reply': {'type': 'text'}, 'replied_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    application = models.ForeignKey("providers.ProviderApplication", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='application_id')
    question = models.TextField()
    asked_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='asked_by')
    reply = models.TextField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('in_progress', 'In progress'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'application_query'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Query sent back to the applicant during desk review, and the reply'


class Approval(CedaModel):
    """Approval certificate of a private institution (signed, QR-verifiable, levels, capacity, conditions, expiry)"""

    ceda_entity = 'approval'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'application_id': {'type': 'ref', 'ref': 'provider_application'}, 'approval_number': {'type': 'code'}, 'approved_levels': {'type': 'cls', 'code_list': 'education_level'}, 'approved_capacity': {'type': 'int_u'}, 'valid_from_on': {'type': 'date'}, 'expires_on': {'type': 'date'}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'status': {'type': 'enum', 'enum': 'approval_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    application = models.ForeignKey("providers.ProviderApplication", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='application_id')
    approval_number = models.CharField(max_length=40)
    approved_levels = models.JSONField()
    approved_capacity = models.PositiveIntegerField(null=True, blank=True)
    valid_from_on = models.DateField()
    expires_on = models.DateField(help_text='Default 3 years')
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('expiring', 'Expiring'), ('expired', 'Expired'), ('suspended', 'Suspended'), ('revoked', 'Revoked'), ('superseded', 'Superseded')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'approval'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Approval certificate of a private institution (signed, QR-verifiable, levels, ca'


class ApprovalChecklistItem(CedaModel):
    """State approval checklist item and minimum standard per level (policy data, not code)"""

    ceda_entity = 'approval_checklist_item'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'item_key': {'type': 'code'}, 'area': {'type': 'enum', 'enum': 'checklist_area'}, 'title': {'type': 'title'}, 'levels': {'type': 'cls', 'code_list': 'education_level'}, 'is_mandatory': {'type': 'bool'}, 'minimum_standard': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    item_key = models.CharField(max_length=40)
    area = models.CharField(max_length=32, choices=[('legal', 'Legal'), ('premises', 'Premises'), ('facilities', 'Facilities'), ('staffing', 'Staffing'), ('curriculum', 'Curriculum'), ('safeguarding_safety', 'Safeguarding safety'), ('finance', 'Finance')])
    title = models.CharField(max_length=300)
    levels = models.JSONField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)
    minimum_standard = models.JSONField(null=True, blank=True, help_text='e.g. classroom size, toilets by sex, laboratories')
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
        db_table = 'approval_checklist_item'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'State approval checklist item and minimum standard per level (policy data, not c'


class ApprovalCondition(CedaModel):
    """Condition attached to an approval, tracked as a corrective action with evidence"""

    ceda_entity = 'approval_condition'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'approval_id': {'type': 'ref', 'ref': 'approval'}, 'condition_text': {'type': 'text'}, 'due_on': {'type': 'date'}, 'corrective_action_id': {'type': 'ref', 'ref': 'corrective_action'}, 'status': {'type': 'enum', 'enum': 'action_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    approval = models.ForeignKey("providers.Approval", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approval_id')
    condition_text = models.TextField()
    due_on = models.DateField()
    corrective_action = models.ForeignKey("institutions.CorrectiveAction", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='corrective_action_id', null=True, blank=True)
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
        db_table = 'approval_condition'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Condition attached to an approval, tracked as a corrective action with evidence'


class ClosureCase(CedaModel):
    """Learner protection case when a private institution is suspended or closed (LGA tracks re-enrolment)"""

    ceda_entity = 'closure_case'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'sanction_id': {'type': 'ref', 'ref': 'sanction'}, 'learners_affected': {'type': 'int_u'}, 'learners_reenrolled': {'type': 'int_u'}, 'alternatives': {'type': 'json'}, 'lga_officer_id': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    sanction = models.ForeignKey("providers.Sanction", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='sanction_id', null=True, blank=True)
    learners_affected = models.PositiveIntegerField()
    learners_reenrolled = models.PositiveIntegerField(default=0)
    alternatives = models.JSONField(null=True, blank=True, help_text='Nearby approved institutions with places')
    lga_officer = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lga_officer_id', null=True, blank=True)
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
        db_table = 'closure_case'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner protection case when a private institution is suspended or closed (LGA t'


class Provider(CedaModel):
    """Private education provider (proprietor organisation) — Provider 360"""

    ceda_entity = 'provider'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'legal_name': {'type': 'title'}, 'trading_name': {'type': 'title'}, 'cac_number': {'type': 'code'}, 'tin': {'type': 'code'}, 'provider_tenant_id': {'type': 'uuid'}, 'registered_address': {'type': 'json'}, 'phone': {'type': 'phone'}, 'email': {'type': 'email'}, 'status': {'type': 'enum', 'enum': 'provider_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    legal_name = models.CharField(max_length=300)
    trading_name = models.CharField(max_length=300, null=True, blank=True)
    cac_number = models.CharField(max_length=20, null=True, blank=True, help_text='Corporate Affairs Commission registration')
    tin = models.CharField(max_length=20, null=True, blank=True, help_text='Tax identification number')
    provider_tenant_id = cf.UUID7Field(null=True, blank=True, help_text='Private tenant created on first approval')
    registered_address = models.JSONField()
    phone = models.CharField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('registered', 'Registered'), ('applicant', 'Applicant'), ('approved', 'Approved'), ('suspended', 'Suspended'), ('closed', 'Closed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'provider'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Private education provider (proprietor organisation) — Provider 360'


class ProviderApplication(CedaModel):
    """Application for approval (new, regularisation or renewal) of one or more proposed institutions"""

    ceda_entity = 'provider_application'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'provider_id': {'type': 'ref', 'ref': 'provider'}, 'application_number': {'type': 'code'}, 'kind': {'type': 'enum', 'enum': 'application_kind'}, 'proposed_institution': {'type': 'json'}, 'proposed_location': {'type': 'point'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'federal_approval': {'type': 'json'}, 'completeness': {'type': 'pct'}, 'submitted_at': {'type': 'ts'}, 'desk_review_due_on': {'type': 'date'}, 'inspection_due_on': {'type': 'date'}, 'decision': {'type': 'enum', 'enum': 'approval_decision'}, 'decision_reasons': {'type': 'text'}, 'decided_by': {'type': 'ref', 'ref': 'app_user'}, 'second_approver_id': {'type': 'ref', 'ref': 'app_user'}, 'decided_at': {'type': 'ts'}, 'appeal_route': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'application_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    provider = models.ForeignKey("providers.Provider", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='provider_id')
    application_number = models.CharField(max_length=32)
    kind = models.CharField(max_length=32, choices=[('new', 'New'), ('regularisation', 'Regularisation'), ('renewal', 'Renewal'), ('variation', 'Variation')])
    proposed_institution = models.JSONField(help_text='Name, levels, location, capacity, curricula, fee schedule, staffing plan')
    proposed_location = cf.PointField(null=True, blank=True, help_text='Map pin (duplicate check within 500 m)')
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id', null=True, blank=True)
    federal_approval = models.JSONField(null=True, blank=True, help_text='NUC / NBTE / NCCE / MDCN / NMCN evidence for tertiary and medical (FR-PVT-117)')
    completeness = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, help_text='Share of checklist items evidenced')
    submitted_at = models.DateTimeField(null=True, blank=True)
    desk_review_due_on = models.DateField(null=True, blank=True, help_text='10 working days')
    inspection_due_on = models.DateField(null=True, blank=True, help_text='20 working days')
    decision = models.CharField(max_length=32, choices=[('approve', 'Approve'), ('approve_with_conditions', 'Approve with conditions'), ('defer', 'Defer'), ('refuse', 'Refuse')], null=True, blank=True)
    decision_reasons = models.TextField(null=True, blank=True)
    decided_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='decided_by', null=True, blank=True)
    second_approver = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='second_approver_id', null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    appeal_route = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('fee_pending', 'Fee pending'), ('desk_review', 'Desk review'), ('query_raised', 'Query raised'), ('inspection', 'Inspection'), ('decision', 'Decision'), ('approved', 'Approved'), ('refused', 'Refused'), ('deferred', 'Deferred'), ('withdrawn', 'Withdrawn'), ('appealed', 'Appealed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'provider_application'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Application for approval (new, regularisation or renewal) of one or more propose'


class ProviderPerson(CedaModel):
    """Proprietor or director of a provider (identity verified by NIN)"""

    ceda_entity = 'provider_person'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'link'
    ceda_class = 'restricted'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'provider_id': {'type': 'ref', 'ref': 'provider'}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'given_name': {'type': 'name', 'pii': True}, 'family_name': {'type': 'name', 'pii': True}, 'role': {'type': 'enum', 'enum': 'provider_person_role'}, 'nin_verified': {'type': 'bool'}, 'ownership_share': {'type': 'pct'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    provider = models.ForeignKey("providers.Provider", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='provider_id')
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id', null=True, blank=True)
    given_name = models.CharField(max_length=200)
    family_name = models.CharField(max_length=200)
    role = models.CharField(max_length=32, choices=[('proprietor', 'Proprietor'), ('director', 'Director'), ('company_secretary', 'Company secretary'), ('head_designate', 'Head designate')])
    nin_verified = models.BooleanField(default=False, help_text='External identifier held in external_identifier')
    ownership_share = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
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
        db_table = 'provider_person'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Proprietor or director of a provider (identity verified by NIN)'


class RegDatasetDefinition(CedaModel):
    """Regulatory dataset that private institutions share with the state (configured per country/state, MFS §10.5)"""

    ceda_entity = 'reg_dataset_definition'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'dataset': {'type': 'enum', 'enum': 'dataset_kind'}, 'fields': {'type': 'json'}, 'frequency': {'type': 'enum', 'enum': 'refresh_frequency'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    dataset = models.CharField(max_length=32, choices=[('enrolment', 'Enrolment'), ('attendance', 'Attendance'), ('staffing', 'Staffing'), ('curriculum_coverage', 'Curriculum coverage'), ('results', 'Results'), ('safety', 'Safety'), ('fees', 'Fees'), ('compliance', 'Compliance'), ('finance', 'Finance'), ('registers', 'Registers')])
    fields = models.JSONField(help_text='Fields included')
    frequency = models.CharField(max_length=32, choices=[('live', 'Live'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('termly', 'Termly'), ('per_series', 'Per series'), ('per_session', 'Per session'), ('as_occurs', 'As occurs')])
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
        db_table = 'reg_dataset_definition'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Regulatory dataset that private institutions share with the state (configured pe'


class RegSnapshot(CedaModel):
    """Regulatory dataset delivery from a private institution (read-only to the regulator)"""

    ceda_entity = 'reg_snapshot'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'snapshot'
    ceda_class = 'confidential'
    ceda_history = 'snapshot'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'dataset': {'type': 'enum', 'enum': 'dataset_kind'}, 'definition_id': {'type': 'ref', 'ref': 'reg_dataset_definition'}, 'as_of': {'type': 'ts'}, 'payload': {'type': 'json'}, 'payload_hash': {'type': 'hash'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    dataset = models.CharField(max_length=32, choices=[('enrolment', 'Enrolment'), ('attendance', 'Attendance'), ('staffing', 'Staffing'), ('curriculum_coverage', 'Curriculum coverage'), ('results', 'Results'), ('safety', 'Safety'), ('fees', 'Fees'), ('compliance', 'Compliance'), ('finance', 'Finance'), ('registers', 'Registers')])
    definition = models.ForeignKey("providers.RegDatasetDefinition", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='definition_id')
    as_of = models.DateTimeField()
    payload = models.JSONField(help_text='Aggregates and permitted identities only')
    payload_hash = models.BinaryField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'reg_snapshot'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Regulatory dataset delivery from a private institution (read-only to the regulat'


class RegulatoryFee(CedaModel):
    """State regulatory fee (application, inspection, approval, renewal) — separate from the operator subscription"""

    ceda_entity = 'regulatory_fee'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'provider_id': {'type': 'ref', 'ref': 'provider'}, 'application_id': {'type': 'ref', 'ref': 'provider_application'}, 'fee_kind': {'type': 'enum', 'enum': 'regulatory_fee_kind'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'revenue_code': {'type': 'code'}, 'payment_reference': {'type': 'code'}, 'paid_at': {'type': 'ts'}, 'receipt_number': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'fee_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    provider = models.ForeignKey("providers.Provider", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='provider_id')
    application = models.ForeignKey("providers.ProviderApplication", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='application_id', null=True, blank=True)
    fee_kind = models.CharField(max_length=32, choices=[('application', 'Application'), ('inspection', 'Inspection'), ('approval', 'Approval'), ('renewal', 'Renewal'), ('late_renewal', 'Late renewal')])
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    revenue_code = models.CharField(max_length=40, help_text='State revenue code')
    payment_reference = models.CharField(max_length=64, null=True, blank=True, help_text='Remita RRR')
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('due', 'Due'), ('paid', 'Paid'), ('waived', 'Waived'), ('refunded', 'Refunded')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'regulatory_fee'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'State regulatory fee (application, inspection, approval, renewal) — separate fro'


class Sanction(CedaModel):
    """Sanction step on a private institution (warning → conditions → suspension of admissions → suspension → closure) with appeal"""

    ceda_entity = 'sanction'
    ceda_zones = ('registry',)
    ceda_domain = 'PVT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'step': {'type': 'enum', 'enum': 'sanction_step'}, 'grounds': {'type': 'text'}, 'evidence_document_ids': {'type': 'json'}, 'blocks_admissions': {'type': 'bool'}, 'blocks_exam_entries': {'type': 'bool'}, 'decided_by': {'type': 'ref', 'ref': 'app_user'}, 'effective_on': {'type': 'date'}, 'appeal_status': {'type': 'enum', 'enum': 'appeal_status'}, 'lifted_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'sanction_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    step = models.CharField(max_length=32, choices=[('warning', 'Warning'), ('conditions', 'Conditions'), ('admissions_suspended', 'Admissions suspended'), ('suspension', 'Suspension'), ('closure', 'Closure')])
    grounds = models.TextField()
    evidence_document_ids = models.JSONField()
    blocks_admissions = models.BooleanField(default=False)
    blocks_exam_entries = models.BooleanField(default=False)
    decided_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='decided_by')
    effective_on = models.DateField()
    appeal_status = models.CharField(max_length=32, choices=[('none', 'None'), ('lodged', 'Lodged'), ('upheld', 'Upheld'), ('dismissed', 'Dismissed')], null=True, blank=True)
    lifted_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('approved', 'Approved'), ('in_effect', 'In effect'), ('appealed', 'Appealed'), ('lifted', 'Lifted'), ('upheld', 'Upheld')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'sanction'
        app_label = 'providers'
        base_manager_name = 'unscoped'
        verbose_name = 'Sanction step on a private institution (warning → conditions → suspension of adm'
