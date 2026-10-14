"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``clearance`` — Fee-clearance due diligence.
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



class ClearanceCheck(CedaModel):
    """Clearance check run for an incoming learner (purpose-bound, logged, visible to the family)"""

    ceda_entity = 'clearance_check'
    ceda_zones = ('registry',)
    ceda_domain = 'FCL'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'requesting_institution_id': {'type': 'ref', 'ref': 'institution'}, 'purpose': {'type': 'enum', 'enum': 'clearance_purpose'}, 'basis': {'type': 'enum', 'enum': 'clearance_basis'}, 'admission_application_id': {'type': 'uuid'}, 'learner_transfer_id': {'type': 'ref', 'ref': 'learner_transfer'}, 'requested_by': {'type': 'uuid'}, 'checked_at': {'type': 'ts'}, 'coverage': {'type': 'enum', 'enum': 'clearance_coverage'}, 'result': {'type': 'enum', 'enum': 'clearance_result'}, 'obligations': {'type': 'json'}, 'total_outstanding_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'pattern_flags': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    requesting_institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requesting_institution_id')
    purpose = models.CharField(max_length=32, choices=[('admission', 'Admission'), ('transfer', 'Transfer'), ('re_enrolment', 'Re enrolment'), ('enquiry_with_consent', 'Enquiry with consent')])
    basis = models.CharField(max_length=32, choices=[('admission_due_diligence', 'Admission due diligence'), ('guardian_consent', 'Guardian consent')])
    admission_application_id = cf.UUID7Field(null=True, blank=True, help_text='ops-zone admission application')
    learner_transfer = models.ForeignKey("learners.LearnerTransfer", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_transfer_id', null=True, blank=True)
    requested_by = cf.UUID7Field()
    checked_at = models.DateTimeField()
    coverage = models.CharField(max_length=32, choices=[('state', 'State'), ('national', 'National')])
    result = models.CharField(max_length=32, choices=[('clear', 'Clear'), ('outstanding', 'Outstanding'), ('disputed_only', 'Disputed only'), ('protected', 'Protected')])
    obligations = models.JSONField(help_text='Snapshot: obligation id, creditor, kind, amount, oldest due date, status')
    total_outstanding_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    pattern_flags = models.JSONField(null=True, blank=True, help_text='e.g. repeat_unsettled_transfers (count, window)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'clearance_check'
        app_label = 'clearance'
        base_manager_name = 'unscoped'
        verbose_name = 'Clearance check run for an incoming learner (purpose-bound, logged, visible to t'


class ClearanceDecision(CedaModel):
    """Human admission decision recorded on a clearance check (or the automatic protection of a learner)"""

    ceda_entity = 'clearance_decision'
    ceda_zones = ('registry',)
    ceda_domain = 'FCL'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'check_id': {'type': 'ref', 'ref': 'clearance_check'}, 'decision': {'type': 'enum', 'enum': 'clearance_decision_kind'}, 'protected_reason': {'type': 'enum', 'enum': 'protected_reason'}, 'reason': {'type': 'text'}, 'payment_plan_ref': {'type': 'code'}, 'decided_by': {'type': 'uuid'}, 'decided_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    check_id = cf.UUID7Field()
    decision = models.CharField(max_length=32, choices=[('admit', 'Admit'), ('admit_with_payment_plan', 'Admit with payment plan'), ('defer_pending_settlement', 'Defer pending settlement'), ('admit_protected', 'Admit protected')])
    protected_reason = models.CharField(max_length=32, choices=[('public_basic_education', 'Public basic education'), ('send', 'Send'), ('safeguarding', 'Safeguarding'), ('child_in_care', 'Child in care'), ('displaced', 'Displaced'), ('other_vulnerability', 'Other vulnerability')], null=True, blank=True)
    reason = models.TextField()
    payment_plan_ref = models.CharField(max_length=64, null=True, blank=True)
    decided_by = cf.UUID7Field(help_text='app_user, or the system for automatic protection')
    decided_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'clearance_decision'
        app_label = 'clearance'
        base_manager_name = 'unscoped'
        verbose_name = 'Human admission decision recorded on a clearance check (or the automatic protect'


class LearnerObligation(CedaModel):
    """Outstanding obligation of a learner's payer to an institution (fees or other dues), published from the creditor's ledger"""

    ceda_entity = 'learner_obligation'
    ceda_zones = ('registry',)
    ceda_domain = 'FCL'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'creditor_institution_id': {'type': 'ref', 'ref': 'institution'}, 'creditor_tenant_id': {'type': 'uuid'}, 'obligation_kind': {'type': 'enum', 'enum': 'obligation_kind'}, 'payer_kind': {'type': 'enum', 'enum': 'account_holder'}, 'periods': {'type': 'json'}, 'amount_outstanding_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'oldest_due_on': {'type': 'date'}, 'evidence': {'type': 'json'}, 'evidence_hash': {'type': 'hash'}, 'source': {'type': 'enum', 'enum': 'obligation_source'}, 'published_by': {'type': 'uuid'}, 'published_at': {'type': 'ts'}, 'reconfirm_by': {'type': 'date'}, 'last_checked_at': {'type': 'ts'}, 'settled_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'obligation_status'}, 'open_key': {'type': 'code', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    creditor_institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='creditor_institution_id')
    creditor_tenant_id = cf.UUID7Field(help_text='Operating tenant whose ledger holds the invoices')
    obligation_kind = models.CharField(max_length=32, choices=[('tuition_fees', 'Tuition fees'), ('boarding', 'Boarding'), ('examination_fees', 'Examination fees'), ('transport', 'Transport'), ('meals', 'Meals'), ('books_and_materials', 'Books and materials'), ('uniform', 'Uniform'), ('development_levy', 'Development levy'), ('damaged_property', 'Damaged property'), ('library', 'Library'), ('other_dues', 'Other dues')])
    payer_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('family', 'Family'), ('guardian', 'Guardian'), ('sponsor', 'Sponsor'), ('funder', 'Funder'), ('government', 'Government'), ('employer', 'Employer'), ('institution', 'Institution')])
    periods = models.JSONField(null=True, blank=True, help_text='Billing periods covered, e.g. 2025/26-T2, 2025/26-T3')
    amount_outstanding_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    oldest_due_on = models.DateField()
    evidence = models.JSONField(help_text='Invoice numbers and content hashes, or document ids for manual claims')
    evidence_hash = models.BinaryField(help_text='SHA-256 of the canonical evidence')
    source = models.CharField(max_length=32, choices=[('ledger', 'Ledger'), ('manual_with_evidence', 'Manual with evidence')])
    published_by = cf.UUID7Field()
    published_at = models.DateTimeField()
    reconfirm_by = models.DateField(help_text='Expires if the creditor does not reconfirm (default 90 days)')
    last_checked_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('outstanding', 'Outstanding'), ('payment_plan', 'Payment plan'), ('disputed', 'Disputed'), ('settled', 'Settled'), ('written_off', 'Written off'), ('waived', 'Waived'), ('expired', 'Expired'), ('withdrawn', 'Withdrawn')])
    open_key = cf.generated(models.CharField(max_length=120, null=True, blank=True, help_text='learner:creditor:kind while open', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'learner_obligation'
        app_label = 'clearance'
        base_manager_name = 'unscoped'
        verbose_name = "Outstanding obligation of a learner's payer to an institution (fees or other due"


class ObligationDispute(CedaModel):
    """Dispute of a published obligation by the family, the admitting institution or the creditor (resolved by LGA or state)"""

    ceda_entity = 'obligation_dispute'
    ceda_zones = ('registry',)
    ceda_domain = 'FCL'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'obligation_id': {'type': 'ref', 'ref': 'learner_obligation'}, 'raised_by_kind': {'type': 'enum', 'enum': 'dispute_party'}, 'raised_by': {'type': 'uuid'}, 'grounds': {'type': 'enum', 'enum': 'dispute_grounds'}, 'statement': {'type': 'text'}, 'evidence_document_ids': {'type': 'json'}, 'due_by': {'type': 'date'}, 'resolver_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'resolution': {'type': 'enum', 'enum': 'dispute_resolution'}, 'resolved_amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'resolved_by': {'type': 'ref', 'ref': 'app_user'}, 'resolved_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    obligation = models.ForeignKey("clearance.LearnerObligation", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='obligation_id')
    raised_by_kind = models.CharField(max_length=32, choices=[('guardian', 'Guardian'), ('learner', 'Learner'), ('admitting_institution', 'Admitting institution'), ('creditor', 'Creditor')])
    raised_by = cf.UUID7Field()
    grounds = models.CharField(max_length=32, choices=[('already_paid', 'Already paid'), ('amount_wrong', 'Amount wrong'), ('not_liable', 'Not liable'), ('waiver_granted', 'Waiver granted'), ('statute_barred', 'Statute barred'), ('protected_learner', 'Protected learner'), ('other', 'Other')])
    statement = models.TextField()
    evidence_document_ids = models.JSONField(null=True, blank=True)
    due_by = models.DateField(help_text='Resolution service level (default 10 school days)')
    resolver_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='resolver_scope_id')
    resolution = models.CharField(max_length=32, choices=[('upheld', 'Upheld'), ('partly_upheld', 'Partly upheld'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn')], null=True, blank=True)
    resolved_amount_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    resolved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='resolved_by', null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'obligation_dispute'
        app_label = 'clearance'
        base_manager_name = 'unscoped'
        verbose_name = 'Dispute of a published obligation by the family, the admitting institution or th'
