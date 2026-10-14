"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``financing`` — Programme financing.
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



class BillingPeriod(CedaModel):
    """Term or semester billing period with census date (from each institution type's academic calendar)"""

    ceda_entity = 'billing_period'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'academic_period_id': {'type': 'ref', 'ref': 'academic_period'}, 'institution_types': {'type': 'cls', 'code_list': 'institution_category'}, 'label': {'type': 'code'}, 'census_on': {'type': 'date'}, 'confirmation_closes_on': {'type': 'date'}, 'collection_window_ends_on': {'type': 'date'}, 'remittance_due_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'period_state'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    academic_period = models.ForeignKey("academic.AcademicPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='academic_period_id')
    institution_types = models.JSONField()
    label = models.CharField(max_length=40, help_text='e.g. 2026/27-T1-BASIC, 2026/27-S1-TERTIARY')
    census_on = models.DateField(help_text='Default end of week 3 (term) or week 4 (semester)')
    confirmation_closes_on = models.DateField()
    collection_window_ends_on = models.DateField()
    remittance_due_on = models.DateField()
    status = models.CharField(max_length=32, choices=[('planned', 'Planned'), ('census_open', 'Census open'), ('confirming', 'Confirming'), ('demand_issued', 'Demand issued'), ('collecting', 'Collecting'), ('remitting', 'Remitting'), ('reconciled', 'Reconciled'), ('closed', 'Closed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'billing_period'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = "Term or semester billing period with census date (from each institution type's a"


class BillingPeriodBilled(CedaModel):
    """Once-per-period billing guard — a learner is billed once per period across channels and institutions"""

    ceda_entity = 'billing_period_billed'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'billing_period_id': {'type': 'ref', 'ref': 'billing_period'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'channel': {'type': 'enum', 'enum': 'financing_channel'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'snapshot_id': {'type': 'ref', 'ref': 'census_snapshot'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    billing_period = models.ForeignKey("financing.BillingPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_period_id')
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    channel = models.CharField(max_length=32, choices=[('sdaf', 'Sdaf'), ('direct_subscription', 'Direct subscription')])
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    snapshot = models.ForeignKey("financing.CensusSnapshot", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='snapshot_id')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'billing_period_billed'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Once-per-period billing guard — a learner is billed once per period across chann'


class CensusFlag(CedaModel):
    """Ghost-learner flag before freezing (no attendance since period start, identity conflict, unexplained rise) — cleared or explained by the head"""

    ceda_entity = 'census_flag'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'queue'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'snapshot_id': {'type': 'ref', 'ref': 'census_snapshot'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'flag_kind': {'type': 'enum', 'enum': 'census_flag_kind'}, 'evidence': {'type': 'json'}, 'resolution': {'type': 'enum', 'enum': 'flag_resolution'}, 'explanation': {'type': 'str'}, 'resolved_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    snapshot = models.ForeignKey("financing.CensusSnapshot", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='snapshot_id')
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id', null=True, blank=True)
    flag_kind = models.CharField(max_length=32, choices=[('no_attendance_since_start', 'No attendance since start'), ('identity_conflict', 'Identity conflict'), ('unexplained_rise', 'Unexplained rise')])
    evidence = models.JSONField()
    resolution = models.CharField(max_length=32, choices=[('cleared', 'Cleared'), ('explained', 'Explained'), ('removed_from_count', 'Removed from count')], null=True, blank=True)
    explanation = models.CharField(max_length=1000, null=True, blank=True)
    resolved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='resolved_by', null=True, blank=True)
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
        db_table = 'census_flag'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Ghost-learner flag before freezing (no attendance since period start, identity c'


class CensusLearner(CedaModel):
    """Learner included or excluded in a census snapshot, with reason (append-only)"""

    ceda_entity = 'census_learner'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'snapshot'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'snapshot_id': {'type': 'ref', 'ref': 'census_snapshot'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'inclusion': {'type': 'enum', 'enum': 'census_inclusion'}, 'reason': {'type': 'enum', 'enum': 'census_reason'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    snapshot = models.ForeignKey("financing.CensusSnapshot", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='snapshot_id')
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    enrolment = models.ForeignKey("learners.Enrolment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='enrolment_id')
    inclusion = models.CharField(max_length=32, choices=[('billable', 'Billable'), ('excluded', 'Excluded'), ('exempt', 'Exempt')])
    reason = models.CharField(max_length=32, choices=[('withdrawn_before_census', 'Withdrawn before census'), ('duplicate', 'Duplicate'), ('unverified', 'Unverified'), ('other_institution_holds', 'Other institution holds'), ('exempt', 'Exempt')], null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'census_learner'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner included or excluded in a census snapshot, with reason (append-only)'


class CensusSnapshot(CedaModel):
    """Billable-learner count of an institution for a period (flags cleared, head-confirmed, frozen and hashed; amendments versioned)"""

    ceda_entity = 'census_snapshot'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'snapshot'
    ceda_class = 'confidential'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'billing_period_id': {'type': 'ref', 'ref': 'billing_period'}, 'version': {'type': 'int_u'}, 'enrolled': {'type': 'int_u'}, 'verified': {'type': 'int_u'}, 'excluded': {'type': 'int_u'}, 'exempted': {'type': 'int_u'}, 'billable': {'type': 'int_u'}, 'open_flags': {'type': 'int_u'}, 'confirmed_by': {'type': 'ref', 'ref': 'app_user'}, 'confirmed_at': {'type': 'ts'}, 'frozen_at': {'type': 'ts'}, 'content_hash': {'type': 'hash'}, 'challenge': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'census_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    billing_period = models.ForeignKey("financing.BillingPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_period_id')
    version = models.PositiveIntegerField()
    enrolled = models.PositiveIntegerField()
    verified = models.PositiveIntegerField()
    excluded = models.PositiveIntegerField()
    exempted = models.PositiveIntegerField()
    billable = models.PositiveIntegerField()
    open_flags = models.PositiveIntegerField(default=0, help_text='Count cannot be frozen while flags are open')
    confirmed_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='confirmed_by', null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    frozen_at = models.DateTimeField(null=True, blank=True)
    content_hash = models.BinaryField(null=True, blank=True)
    challenge = models.JSONField(null=True, blank=True, help_text='Evidence-based challenge and decision')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('flags_open', 'Flags open'), ('awaiting_confirmation', 'Awaiting confirmation'), ('confirmed', 'Confirmed'), ('challenged', 'Challenged'), ('frozen', 'Frozen'), ('superseded', 'Superseded')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'census_snapshot'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Billable-learner count of an institution for a period (flags cleared, head-confi'


class ReconciliationLine(CedaModel):
    """Line of a reconciliation statement by institution (with logged disputes)"""

    ceda_entity = 'reconciliation_line'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'snapshot'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'statement_id': {'type': 'ref', 'ref': 'reconciliation_statement'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'billed_minor': {'type': 'money'}, 'exempted_minor': {'type': 'money'}, 'collected_minor': {'type': 'money'}, 'remitted_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'dispute': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    statement = models.ForeignKey("financing.ReconciliationStatement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='statement_id')
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    billed_minor = models.BigIntegerField(help_text='(minor units)')
    exempted_minor = models.BigIntegerField(help_text='(minor units)')
    collected_minor = models.BigIntegerField(help_text='(minor units)')
    remitted_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    dispute = models.JSONField(null=True, blank=True, help_text='Dispute logged against the line')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'reconciliation_line'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Line of a reconciliation statement by institution (with logged disputes)'


class ReconciliationStatement(CedaModel):
    """Period statement — billed, exempted, collected, remitted, outstanding — with dual sign-off (state + SDIN), locked and hashed"""

    ceda_entity = 'reconciliation_statement'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'snapshot'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'billing_period_id': {'type': 'ref', 'ref': 'billing_period'}, 'billed_minor': {'type': 'money'}, 'exempted_minor': {'type': 'money'}, 'collected_minor': {'type': 'money'}, 'remitted_minor': {'type': 'money'}, 'outstanding_minor': {'type': 'money'}, 'late_remittance_charge_minor': {'type': 'money'}, 'service_credits_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'state_signed_by': {'type': 'ref', 'ref': 'app_user'}, 'state_signed_at': {'type': 'ts'}, 'operator_signed_by': {'type': 'ref', 'ref': 'app_user'}, 'operator_signed_at': {'type': 'ts'}, 'content_hash': {'type': 'hash'}, 'status': {'type': 'enum', 'enum': 'statement_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    billing_period = models.ForeignKey("financing.BillingPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_period_id')
    billed_minor = models.BigIntegerField(help_text='(minor units)')
    exempted_minor = models.BigIntegerField(help_text='(minor units)')
    collected_minor = models.BigIntegerField(help_text='(minor units)')
    remitted_minor = models.BigIntegerField(help_text='(minor units)')
    outstanding_minor = models.BigIntegerField(help_text='(minor units)')
    late_remittance_charge_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    service_credits_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    state_signed_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='state_signed_by', null=True, blank=True)
    state_signed_at = models.DateTimeField(null=True, blank=True)
    operator_signed_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='operator_signed_by', null=True, blank=True)
    operator_signed_at = models.DateTimeField(null=True, blank=True)
    content_hash = models.BinaryField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('state_signed', 'State signed'), ('operator_signed', 'Operator signed'), ('signed_locked', 'Signed locked'), ('disputed', 'Disputed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'reconciliation_statement'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Period statement — billed, exempted, collected, remitted, outstanding — with dua'


class Remittance(CedaModel):
    """Remittance of collected SDAF from the State Government to SDIN, with advice (recorder ≠ approver; append-only)"""

    ceda_entity = 'remittance'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'billing_period_id': {'type': 'ref', 'ref': 'billing_period'}, 'advice_ref': {'type': 'code'}, 'bank_ref': {'type': 'code'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'remitted_on': {'type': 'date'}, 'recorded_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    billing_period = models.ForeignKey("financing.BillingPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_period_id')
    advice_ref = models.CharField(max_length=64)
    bank_ref = models.CharField(max_length=64)
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    remitted_on = models.DateField()
    recorded_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='recorded_by')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'remittance'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Remittance of collected SDAF from the State Government to SDIN, with advice (rec'


class RemittanceAllocation(CedaModel):
    """Allocation of a remittance to the collections it covers"""

    ceda_entity = 'remittance_allocation'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'remittance_id': {'type': 'ref', 'ref': 'remittance'}, 'collection_id': {'type': 'ref', 'ref': 'sdaf_collection'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    remittance = models.ForeignKey("financing.Remittance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='remittance_id')
    collection = models.ForeignKey("financing.SdafCollection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='collection_id')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'remittance_allocation'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Allocation of a remittance to the collections it covers'


class SdafCollection(CedaModel):
    """Payment into the state revenue account against a demand (posted idempotently from state notifications; append-only)"""

    ceda_entity = 'sdaf_collection'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'demand_id': {'type': 'ref', 'ref': 'sdaf_demand'}, 'state_receipt_ref': {'type': 'code'}, 'channel': {'type': 'enum', 'enum': 'revenue_channel'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'paid_at': {'type': 'ts'}, 'statement_matched_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    demand = models.ForeignKey("financing.SdafDemand", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='demand_id')
    state_receipt_ref = models.CharField(max_length=128, help_text='State e-receipt / collection-system id — idempotency key')
    channel = models.CharField(max_length=32, choices=[('state_portal', 'State portal'), ('remita', 'Remita'), ('bank_branch', 'Bank branch'), ('pos', 'Pos'), ('ussd', 'Ussd'), ('bank_transfer', 'Bank transfer')])
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    paid_at = models.DateTimeField()
    statement_matched_at = models.DateTimeField(null=True, blank=True, help_text='Daily reconciliation against the state collection-account statement')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'sdaf_collection'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Payment into the state revenue account against a demand (posted idempotently fro'


class SdafDemand(CedaModel):
    """SDAF demand notice (consolidated to a government payer) or individual assessment (never at basic-education level)"""

    ceda_entity = 'sdaf_demand'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'demand_number': {'type': 'code'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'billing_period_id': {'type': 'ref', 'ref': 'billing_period'}, 'snapshot_id': {'type': 'ref', 'ref': 'census_snapshot'}, 'payer_kind': {'type': 'enum', 'enum': 'sdaf_payer'}, 'payer_ref': {'type': 'uuid'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'billable_count': {'type': 'int_u'}, 'waived_count': {'type': 'int_u'}, 'rate_id': {'type': 'ref', 'ref': 'sdaf_rate'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'revenue_code': {'type': 'code'}, 'payment_reference': {'type': 'code'}, 'issued_at': {'type': 'ts'}, 'is_basic_education': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'demand_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    demand_number = models.CharField(max_length=32)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    billing_period = models.ForeignKey("financing.BillingPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_period_id')
    snapshot = models.ForeignKey("financing.CensusSnapshot", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='snapshot_id')
    payer_kind = models.CharField(max_length=32, choices=[('government', 'Government'), ('parent_or_student', 'Parent or student'), ('sponsor', 'Sponsor'), ('scholarship', 'Scholarship'), ('split', 'Split')])
    payer_ref = cf.UUID7Field(null=True, blank=True, help_text='Government payer, guardian, learner or sponsor')
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id', null=True, blank=True)
    billable_count = models.PositiveIntegerField()
    waived_count = models.PositiveIntegerField()
    rate = models.ForeignKey("financing.SdafRate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rate_id')
    amount_minor = models.BigIntegerField(help_text='(billable − waived) × rate (minor units)')
    currency = models.CharField(max_length=3)
    revenue_code = models.CharField(max_length=40)
    payment_reference = models.CharField(max_length=64, help_text='Remita RRR or state e-revenue reference')
    issued_at = models.DateTimeField()
    is_basic_education = models.BooleanField()
    status = models.CharField(max_length=32, choices=[('issued', 'Issued'), ('part_paid', 'Part paid'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'sdaf_demand'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'SDAF demand notice (consolidated to a government payer) or individual assessment'


class SdafExemption(CedaModel):
    """Approved SDAF exemption for a learner and period (learner stays in the headcount; reported separately)"""

    ceda_entity = 'sdaf_exemption'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'billing_period_id': {'type': 'ref', 'ref': 'billing_period'}, 'category_id': {'type': 'ref', 'ref': 'sdaf_exemption_category'}, 'evidence_document_id': {'type': 'uuid'}, 'requested_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    billing_period = models.ForeignKey("financing.BillingPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_period_id')
    category = models.ForeignKey("financing.SdafExemptionCategory", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='category_id')
    evidence_document_id = cf.UUID7Field()
    requested_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requested_by')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
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
        db_table = 'sdaf_exemption'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Approved SDAF exemption for a learner and period (learner stays in the headcount'


class SdafExemptionCategory(CedaModel):
    """Exemption category (SEND, orphans and vulnerable children, IDPs, scholarship holders) with funding rule"""

    ceda_entity = 'sdaf_exemption_category'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'funding_rule': {'type': 'enum', 'enum': 'exemption_funding'}, 'evidence_required': {'type': 'str'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    title = models.CharField(max_length=300)
    funding_rule = models.CharField(max_length=32, choices=[('borne_by_state', 'Borne by state'), ('waived', 'Waived')])
    evidence_required = models.CharField(max_length=500)
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
        db_table = 'sdaf_exemption_category'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Exemption category (SEND, orphans and vulnerable children, IDPs, scholarship hol'


class SdafPayerRule(CedaModel):
    """Who pays the SDAF for an institution type and level (government only for public primary and JSS)"""

    ceda_entity = 'sdaf_payer_rule'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_type': {'type': 'cl', 'code_list': 'institution_category'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'is_basic_education': {'type': 'bool'}, 'payer': {'type': 'enum', 'enum': 'sdaf_payer'}, 'split': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_type = models.CharField(max_length=32)
    education_level = models.CharField(max_length=32)
    is_basic_education = models.BooleanField(help_text='Public primary or junior secondary')
    payer = models.CharField(max_length=32, choices=[('government', 'Government'), ('parent_or_student', 'Parent or student'), ('sponsor', 'Sponsor'), ('scholarship', 'Scholarship'), ('split', 'Split')])
    split = models.JSONField(null=True, blank=True, help_text='Shares when payer = split')
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
        db_table = 'sdaf_payer_rule'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Who pays the SDAF for an institution type and level (government only for public '


class SdafPublicSummary(CedaModel):
    """Optional aggregated public summary per term (no learner data)"""

    ceda_entity = 'sdaf_public_summary'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'snapshot'
    ceda_class = 'public'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'billing_period_id': {'type': 'ref', 'ref': 'billing_period'}, 'published_at': {'type': 'ts'}, 'summary': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    billing_period = models.ForeignKey("financing.BillingPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_period_id')
    published_at = models.DateTimeField()
    summary = models.JSONField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'sdaf_public_summary'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Optional aggregated public summary per term (no learner data)'


class SdafRate(CedaModel):
    """Rate in a rate card for an institution type and level, per term or per semester (naira)"""

    ceda_entity = 'sdaf_rate'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'rate_card_id': {'type': 'ref', 'ref': 'sdaf_rate_card'}, 'institution_type': {'type': 'cl', 'code_list': 'institution_category'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'charge_period': {'type': 'enum', 'enum': 'charge_period'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    rate_card = models.ForeignKey("financing.SdafRateCard", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rate_card_id')
    institution_type = models.CharField(max_length=32)
    education_level = models.CharField(max_length=32)
    charge_period = models.CharField(max_length=32, choices=[('per_term', 'Per term'), ('per_semester', 'Per semester')])
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3, default='NGN')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'sdaf_rate'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Rate in a rate card for an institution type and level, per term or per semester '


class SdafRateCard(CedaModel):
    """Version of the state-approved SDAF rate card (propose → approve → publish)"""

    ceda_entity = 'sdaf_rate_card'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'version': {'type': 'int_u'}, 'proposed_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'approval_instrument': {'type': 'str'}, 'effective_from': {'type': 'date'}, 'published_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    version = models.PositiveIntegerField()
    proposed_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='proposed_by')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
    approval_instrument = models.CharField(max_length=200, null=True, blank=True, help_text='Approval reference (D25/D26)')
    effective_from = models.DateField()
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
        db_table = 'sdaf_rate_card'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'Version of the state-approved SDAF rate card (propose → approve → publish)'


class UnmatchedCollection(CedaModel):
    """State collection notification not matched to a demand, or a held duplicate"""

    ceda_entity = 'unmatched_collection'
    ceda_zones = ('registry',)
    ceda_domain = 'SUB'
    ceda_kind = 'queue'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SDAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'state_receipt_ref': {'type': 'code'}, 'payload': {'type': 'json'}, 'reason': {'type': 'enum', 'enum': 'unmatched_reason'}, 'resolved_demand_id': {'type': 'ref', 'ref': 'sdaf_demand'}, 'resolved_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    state_receipt_ref = models.CharField(max_length=128)
    payload = models.JSONField()
    reason = models.CharField(max_length=32, choices=[('no_reference', 'No reference'), ('unknown_reference', 'Unknown reference'), ('amount_mismatch', 'Amount mismatch'), ('duplicate', 'Duplicate')])
    resolved_demand = models.ForeignKey("financing.SdafDemand", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='resolved_demand_id', null=True, blank=True)
    resolved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='resolved_by', null=True, blank=True)
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
        db_table = 'unmatched_collection'
        app_label = 'financing'
        base_manager_name = 'unscoped'
        verbose_name = 'State collection notification not matched to a demand, or a held duplicate'
