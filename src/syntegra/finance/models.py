"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``finance`` — Billing, payments, funding, ledger, budgets, procurement and suppliers.
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



class Account(CedaModel):
    """Ledger account — learner, family, sponsor or funder account, and general-ledger accounts"""

    ceda_entity = 'account'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'master'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'account_kind': {'type': 'enum', 'enum': 'account_kind'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'holder_kind': {'type': 'enum', 'enum': 'account_holder'}, 'holder_id': {'type': 'uuid'}, 'currency': {'type': 'currency'}, 'gl_type': {'type': 'enum', 'enum': 'gl_type'}, 'virtual_account_number': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    account_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('family', 'Family'), ('sponsor', 'Sponsor'), ('funder', 'Funder'), ('general_ledger', 'General ledger')])
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    holder_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('family', 'Family'), ('guardian', 'Guardian'), ('sponsor', 'Sponsor'), ('funder', 'Funder'), ('government', 'Government'), ('employer', 'Employer'), ('institution', 'Institution')], null=True, blank=True)
    holder_id = cf.UUID7Field(null=True, blank=True, help_text='learner, family, sponsor or funder')
    currency = models.CharField(max_length=3)
    gl_type = models.CharField(max_length=32, choices=[('asset', 'Asset'), ('liability', 'Liability'), ('income', 'Income'), ('expense', 'Expense'), ('equity', 'Equity')], null=True, blank=True, help_text='asset, liability, income, expense, equity (GL accounts)')
    virtual_account_number = models.CharField(max_length=20, null=True, blank=True, help_text='Per-family virtual account for transfers')
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
        db_table = 'account'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Ledger account — learner, family, sponsor or funder account, and general-ledger '


class BankStatementLine(CedaModel):
    """Imported bank statement line (MT940/CSV/open banking) reconciled to payments and disbursements"""

    ceda_entity = 'bank_statement_line'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'bank_account_ref': {'type': 'code'}, 'statement_date': {'type': 'date'}, 'value_date': {'type': 'date'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'narrative': {'type': 'str'}, 'bank_ref': {'type': 'code'}, 'matched_kind': {'type': 'code'}, 'matched_id': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'reconciliation_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    bank_account_ref = models.CharField(max_length=40)
    statement_date = models.DateField()
    value_date = models.DateField()
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    narrative = models.CharField(max_length=500, null=True, blank=True)
    bank_ref = models.CharField(max_length=64)
    matched_kind = models.CharField(max_length=40, null=True, blank=True)
    matched_id = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('unmatched', 'Unmatched'), ('matched', 'Matched'), ('part_matched', 'Part matched'), ('disputed', 'Disputed'), ('reconciled', 'Reconciled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'bank_statement_line'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Imported bank statement line (MT940/CSV/open banking) reconciled to payments and'


class BillingRule(CedaModel):
    """Versioned, effective-dated billing rule (conditions, amount, priority, discount stacking); tested before publishing"""

    ceda_entity = 'billing_rule'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_key': {'type': 'code'}, 'charge_type_id': {'type': 'ref', 'ref': 'charge_type'}, 'billing_basis': {'type': 'enum', 'enum': 'billing_basis'}, 'conditions': {'type': 'json'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'priority': {'type': 'smallint'}, 'discount_policy': {'type': 'json'}, 'version': {'type': 'int_u'}, 'effective_from': {'type': 'date'}, 'effective_to': {'type': 'date'}, 'test_results': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule_key = models.CharField(max_length=40)
    charge_type = models.ForeignKey("finance.ChargeType", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='charge_type_id')
    billing_basis = models.CharField(max_length=32, choices=[('term', 'Term'), ('semester', 'Semester'), ('annual', 'Annual'), ('monthly', 'Monthly'), ('weekly', 'Weekly'), ('course', 'Course'), ('credit', 'Credit'), ('module', 'Module'), ('session', 'Session'), ('hour', 'Hour'), ('exam', 'Exam'), ('registration', 'Registration'), ('learner', 'Learner'), ('family', 'Family'), ('service', 'Service'), ('subscription', 'Subscription'), ('pay_as_you_go', 'Pay as you go')])
    conditions = models.JSONField(help_text='Institution, campus, programme, course, level, category, residency, scholarship, family …')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    priority = models.SmallIntegerField()
    discount_policy = models.JSONField(null=True, blank=True, help_text='Sibling/family discounts and stacking')
    version = models.PositiveIntegerField()
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    test_results = models.JSONField(null=True, blank=True, help_text='Results against sample learners')
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
        db_table = 'billing_rule'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned, effective-dated billing rule (conditions, amount, priority, discount '


class BillingRun(CedaModel):
    """Billing run with preview, exceptions, approval and issue (no duplicate invoice per learner per period)"""

    ceda_entity = 'billing_run'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'period_label': {'type': 'code'}, 'billing_basis': {'type': 'enum', 'enum': 'billing_basis'}, 'learners_in_scope': {'type': 'int_u'}, 'exceptions': {'type': 'json'}, 'total_amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'approved_by': {'type': 'uuid'}, 'issued_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'run_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    period_label = models.CharField(max_length=20)
    billing_basis = models.CharField(max_length=32, choices=[('term', 'Term'), ('semester', 'Semester'), ('annual', 'Annual'), ('monthly', 'Monthly'), ('weekly', 'Weekly'), ('course', 'Course'), ('credit', 'Credit'), ('module', 'Module'), ('session', 'Session'), ('hour', 'Hour'), ('exam', 'Exam'), ('registration', 'Registration'), ('learner', 'Learner'), ('family', 'Family'), ('service', 'Service'), ('subscription', 'Subscription'), ('pay_as_you_go', 'Pay as you go')])
    learners_in_scope = models.PositiveIntegerField()
    exceptions = models.JSONField(null=True, blank=True)
    total_amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    approved_by = cf.UUID7Field(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('previewed', 'Previewed'), ('running', 'Running'), ('awaiting_approval', 'Awaiting approval'), ('approved', 'Approved'), ('issued', 'Issued'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'billing_run'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Billing run with preview, exceptions, approval and issue (no duplicate invoice p'


class Budget(CedaModel):
    """Budget by cost centre and account linked to enrolment and staffing forecasts (approved via workflow)"""

    ceda_entity = 'budget'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'fiscal_year': {'type': 'smallint'}, 'version': {'type': 'int_u'}, 'line_items': {'type': 'json'}, 'assumptions': {'type': 'json'}, 'currency': {'type': 'currency'}, 'variance_notes': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    fiscal_year = models.SmallIntegerField()
    version = models.PositiveIntegerField()
    line_items = models.JSONField(help_text='Cost centre × account × period amounts')
    assumptions = models.JSONField(null=True, blank=True, help_text='Enrolment and staffing forecasts')
    currency = models.CharField(max_length=3)
    variance_notes = models.JSONField(null=True, blank=True, help_text='Explanations and forecast outturn')
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
        db_table = 'budget'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Budget by cost centre and account linked to enrolment and staffing forecasts (ap'


class BudgetCommitment(CedaModel):
    """Commitment of a budget line by a requisition, purchase order, imprest, payroll or disbursement (released, spent or cancelled)"""

    ceda_entity = 'budget_commitment'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'budget_line_id': {'type': 'ref', 'ref': 'budget_line'}, 'source_kind': {'type': 'enum', 'enum': 'commitment_source'}, 'source_id': {'type': 'uuid'}, 'description': {'type': 'str'}, 'amount_minor': {'type': 'money'}, 'spent_minor': {'type': 'money'}, 'released_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'committed_on': {'type': 'date'}, 'committed_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'commitment_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    budget_line = models.ForeignKey("finance.BudgetLine", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='budget_line_id')
    source_kind = models.CharField(max_length=32, choices=[('requisition', 'Requisition'), ('purchase_order', 'Purchase order'), ('imprest', 'Imprest'), ('payroll', 'Payroll'), ('funding_disbursement', 'Funding disbursement'), ('contract', 'Contract'), ('manual', 'Manual')])
    source_id = cf.UUID7Field()
    description = models.CharField(max_length=300)
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    spent_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    released_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    committed_on = models.DateField()
    committed_by = cf.UUID7Field()
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('partly_spent', 'Partly spent'), ('spent', 'Spent'), ('released', 'Released'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'budget_commitment'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Commitment of a budget line by a requisition, purchase order, imprest, payroll o'


class BudgetLine(CedaModel):
    """Approved budget line — cost centre × ledger account × economic code × funding source, with original, revised, committed and actual amounts"""

    ceda_entity = 'budget_line'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'budget_id': {'type': 'ref', 'ref': 'budget'}, 'cost_centre_id': {'type': 'ref', 'ref': 'cost_centre'}, 'account_id': {'type': 'ref', 'ref': 'account'}, 'economic_code': {'type': 'code'}, 'funding_source_kind': {'type': 'enum', 'enum': 'budget_funding_kind'}, 'funding_source_id': {'type': 'ref', 'ref': 'funding_source'}, 'description': {'type': 'str'}, 'original_minor': {'type': 'money'}, 'revised_minor': {'type': 'money'}, 'committed_minor': {'type': 'money'}, 'actual_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    budget = models.ForeignKey("finance.Budget", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='budget_id')
    cost_centre = models.ForeignKey("finance.CostCentre", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='cost_centre_id')
    account = models.ForeignKey("finance.Account", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='account_id')
    economic_code = models.CharField(max_length=16, help_text='Economic segment of the National Chart of Accounts, e.g. 22020101')
    funding_source_kind = models.CharField(max_length=32, choices=[('subvention', 'Subvention'), ('personnel_cost', 'Personnel cost'), ('overhead', 'Overhead'), ('capital_allocation', 'Capital allocation'), ('internally_generated_revenue', 'Internally generated revenue'), ('fees', 'Fees'), ('grant', 'Grant'), ('intervention', 'Intervention'), ('loan', 'Loan'), ('donation', 'Donation'), ('other', 'Other')])
    funding_source = models.ForeignKey("finance.FundingSource", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='funding_source_id', null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    original_minor = models.BigIntegerField(help_text='(minor units)')
    revised_minor = models.BigIntegerField(help_text='(minor units)')
    committed_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    actual_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'budget_line'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Approved budget line — cost centre × ledger account × economic code × funding so'


class BudgetVirement(CedaModel):
    """Virement — budget moved between two lines with a reason, approved by someone other than the requester"""

    ceda_entity = 'budget_virement'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'virement_number': {'type': 'code'}, 'from_line_id': {'type': 'ref', 'ref': 'budget_line'}, 'to_line_id': {'type': 'ref', 'ref': 'budget_line'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'reason': {'type': 'text'}, 'requested_by': {'type': 'uuid'}, 'decided_by': {'type': 'uuid'}, 'decided_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    virement_number = models.CharField(max_length=32)
    from_line = models.ForeignKey("finance.BudgetLine", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='from_line_id')
    to_line = models.ForeignKey("finance.BudgetLine", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='to_line_id')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    reason = models.TextField()
    requested_by = cf.UUID7Field()
    decided_by = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'budget_virement'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Virement — budget moved between two lines with a reason, approved by someone oth'


class ChargeType(CedaModel):
    """Charge type (tuition, registration, exam, accommodation, transport, meals, uniform, books, ICT, lab, clinical, trips …) with GL account and tax treatment"""

    ceda_entity = 'charge_type'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'income_account_id': {'type': 'ref', 'ref': 'account'}, 'tax_code': {'type': 'code'}, 'is_digital_services_line': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    income_account = models.ForeignKey("finance.Account", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='income_account_id')
    tax_code = models.CharField(max_length=16, null=True, blank=True)
    is_digital_services_line = models.BooleanField(default=False, help_text='Labelled pass-through line for private providers')
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
        db_table = 'charge_type'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Charge type (tuition, registration, exam, accommodation, transport, meals, unifo'


class CostCentre(CedaModel):
    """Cost centre of an institution (administration, department, boarding, feeding, estate, ICT, transport, project, welfare) with its budget holder"""

    ceda_entity = 'cost_centre'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'cost_centre_kind': {'type': 'enum', 'enum': 'cost_centre_kind'}, 'parent_id': {'type': 'ref', 'ref': 'cost_centre'}, 'org_unit_id': {'type': 'ref', 'ref': 'org_unit'}, 'holder_staff_id': {'type': 'ref', 'ref': 'staff'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    cost_centre_kind = models.CharField(max_length=32, choices=[('administration', 'Administration'), ('academic_department', 'Academic department'), ('boarding', 'Boarding'), ('feeding', 'Feeding'), ('estate', 'Estate'), ('ict', 'Ict'), ('transport', 'Transport'), ('health', 'Health'), ('library', 'Library'), ('sports', 'Sports'), ('project', 'Project'), ('welfare', 'Welfare'), ('revenue_generating', 'Revenue generating'), ('other', 'Other')])
    parent = models.ForeignKey("finance.CostCentre", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_id', null=True, blank=True)
    org_unit_id = cf.UUID7Field(null=True, blank=True, help_text='Department or unit the cost centre belongs to')
    holder_staff_id = cf.UUID7Field(null=True, blank=True, help_text='Budget holder')
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
        db_table = 'cost_centre'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Cost centre of an institution (administration, department, boarding, feeding, es'


class CreditNote(CedaModel):
    """Credit note against an invoice"""

    ceda_entity = 'credit_note'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'credit_number': {'type': 'code'}, 'reason': {'type': 'str'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'approved_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id')
    credit_number = models.CharField(max_length=32)
    reason = models.CharField(max_length=500)
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    approved_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'credit_note'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Credit note against an invoice'


class FiscalPeriod(CedaModel):
    """Fiscal period (open/closed); closed periods accept no postings"""

    ceda_entity = 'fiscal_period'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'closed_at': {'type': 'ts'}, 'closed_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=10, help_text='YYYY-MM')
    starts_on = models.DateField()
    ends_on = models.DateField()
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = cf.UUID7Field(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fiscal_period'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Fiscal period (open/closed); closed periods accept no postings'


class FundingAward(CedaModel):
    """Funding awarded to a learner (scholarship, bursary, capitation share) — never double counted"""

    ceda_entity = 'funding_award'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'effective'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'funding_source_id': {'type': 'ref', 'ref': 'funding_source'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'awarded_by': {'type': 'uuid'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    funding_source = models.ForeignKey("finance.FundingSource", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='funding_source_id')
    learner_id = cf.UUID7Field()
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    awarded_by = cf.UUID7Field()
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
        db_table = 'funding_award'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Funding awarded to a learner (scholarship, bursary, capitation share) — never do'


class FundingSource(CedaModel):
    """Scholarship, bursary, grant, sponsor, capitation, employer funding or loan (budget and per-learner caps)"""

    ceda_entity = 'funding_source'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'funding_kind': {'type': 'enum', 'enum': 'funding_kind'}, 'funder_account_id': {'type': 'ref', 'ref': 'account'}, 'budget_minor': {'type': 'money'}, 'per_learner_cap_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'priority': {'type': 'smallint'}, 'eligibility_rule': {'type': 'json'}, 'valid_until': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    funding_kind = models.CharField(max_length=32, choices=[('government', 'Government'), ('capitation', 'Capitation'), ('scholarship', 'Scholarship'), ('bursary', 'Bursary'), ('grant', 'Grant'), ('sponsorship', 'Sponsorship'), ('employer', 'Employer'), ('loan', 'Loan'), ('instalment', 'Instalment')])
    funder_account = models.ForeignKey("finance.Account", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='funder_account_id', null=True, blank=True)
    budget_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    per_learner_cap_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    priority = models.SmallIntegerField()
    eligibility_rule = models.JSONField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
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
        db_table = 'funding_source'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Scholarship, bursary, grant, sponsor, capitation, employer funding or loan (budg'


class FxRate(CedaModel):
    """Exchange rate captured per source and day (local and reporting currency)"""

    ceda_entity = 'fx_rate'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'rate_date': {'type': 'date'}, 'base_currency': {'type': 'currency'}, 'quote_currency': {'type': 'currency'}, 'rate': {'type': 'dec'}, 'source': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    rate_date = models.DateField()
    base_currency = models.CharField(max_length=3)
    quote_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=8)
    source = models.CharField(max_length=32)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fx_rate'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Exchange rate captured per source and day (local and reporting currency)'


class GovernmentFundingReceipt(CedaModel):
    """Capitation or government grant tranche received, reconciled against learners funded"""

    ceda_entity = 'government_funding_receipt'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'funding_source_id': {'type': 'ref', 'ref': 'funding_source'}, 'tranche_label': {'type': 'code'}, 'amount_due_minor': {'type': 'money'}, 'amount_received_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'received_on': {'type': 'date'}, 'learners_funded': {'type': 'int_u'}, 'reconciliation': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'reconciliation_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    funding_source = models.ForeignKey("finance.FundingSource", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='funding_source_id')
    tranche_label = models.CharField(max_length=40)
    amount_due_minor = models.BigIntegerField(help_text='(minor units)')
    amount_received_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    received_on = models.DateField(null=True, blank=True)
    learners_funded = models.PositiveIntegerField(null=True, blank=True)
    reconciliation = models.JSONField(null=True, blank=True, help_text='Government + student + scholarship + sponsor = total, no double counting')
    status = models.CharField(max_length=32, choices=[('unmatched', 'Unmatched'), ('matched', 'Matched'), ('part_matched', 'Part matched'), ('disputed', 'Disputed'), ('reconciled', 'Reconciled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'government_funding_receipt'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Capitation or government grant tranche received, reconciled against learners fun'


class Imprest(CedaModel):
    """Imprest — cash advance to a named holder against a budget line, to be retired with receipts by a due date"""

    ceda_entity = 'imprest'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'imprest_number': {'type': 'code'}, 'holder_staff_id': {'type': 'ref', 'ref': 'staff'}, 'cost_centre_id': {'type': 'ref', 'ref': 'cost_centre'}, 'budget_line_id': {'type': 'ref', 'ref': 'budget_line'}, 'commitment_id': {'type': 'ref', 'ref': 'budget_commitment'}, 'purpose': {'type': 'str'}, 'amount_minor': {'type': 'money'}, 'retired_minor': {'type': 'money'}, 'refunded_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'requested_by': {'type': 'uuid'}, 'approved_by': {'type': 'uuid'}, 'issued_on': {'type': 'date'}, 'retire_by': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'imprest_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    imprest_number = models.CharField(max_length=32)
    holder_staff_id = cf.UUID7Field()
    cost_centre = models.ForeignKey("finance.CostCentre", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='cost_centre_id')
    budget_line = models.ForeignKey("finance.BudgetLine", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='budget_line_id')
    commitment = models.ForeignKey("finance.BudgetCommitment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='commitment_id', null=True, blank=True)
    purpose = models.CharField(max_length=300)
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    retired_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    refunded_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    requested_by = cf.UUID7Field()
    approved_by = cf.UUID7Field(null=True, blank=True)
    issued_on = models.DateField(null=True, blank=True)
    retire_by = models.DateField()
    status = models.CharField(max_length=32, choices=[('requested', 'Requested'), ('approved', 'Approved'), ('issued', 'Issued'), ('partly_retired', 'Partly retired'), ('retired', 'Retired'), ('overdue', 'Overdue'), ('written_off', 'Written off'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'imprest'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Imprest — cash advance to a named holder against a budget line, to be retired wi'


class ImprestRetirement(CedaModel):
    """Retirement of an imprest — receipts, amount accounted for and cash refunded"""

    ceda_entity = 'imprest_retirement'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'imprest_id': {'type': 'ref', 'ref': 'imprest'}, 'receipts': {'type': 'json'}, 'amount_minor': {'type': 'money'}, 'refund_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'retired_on': {'type': 'date'}, 'verified_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    imprest = models.ForeignKey("finance.Imprest", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='imprest_id')
    receipts = models.JSONField(help_text='Receipt references, payees and amounts')
    amount_minor = models.BigIntegerField(help_text='Amount accounted for by receipts (minor units)')
    refund_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    retired_on = models.DateField()
    verified_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'imprest_retirement'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Retirement of an imprest — receipts, amount accounted for and cash refunded'


class Invoice(CedaModel):
    """Invoice to a payer (immutable once issued; credit notes for changes)"""

    ceda_entity = 'invoice'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'invoice_number': {'type': 'code'}, 'billing_run_id': {'type': 'ref', 'ref': 'billing_run'}, 'account_id': {'type': 'ref', 'ref': 'account'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'payer_kind': {'type': 'enum', 'enum': 'account_holder'}, 'payer_id': {'type': 'uuid'}, 'period_label': {'type': 'code'}, 'issued_on': {'type': 'date'}, 'due_on': {'type': 'date'}, 'total_minor': {'type': 'money'}, 'balance_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'fx_rate_to_reporting': {'type': 'dec'}, 'content_hash': {'type': 'hash'}, 'status': {'type': 'enum', 'enum': 'invoice_status'}, 'dedupe_key': {'type': 'code', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    invoice_number = models.CharField(max_length=32)
    billing_run = models.ForeignKey("finance.BillingRun", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_run_id', null=True, blank=True)
    account = models.ForeignKey("finance.Account", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='account_id')
    learner_id = cf.UUID7Field(null=True, blank=True)
    payer_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('family', 'Family'), ('guardian', 'Guardian'), ('sponsor', 'Sponsor'), ('funder', 'Funder'), ('government', 'Government'), ('employer', 'Employer'), ('institution', 'Institution')])
    payer_id = cf.UUID7Field()
    period_label = models.CharField(max_length=20, null=True, blank=True)
    issued_on = models.DateField()
    due_on = models.DateField()
    total_minor = models.BigIntegerField(help_text='(minor units)')
    balance_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    fx_rate_to_reporting = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True, help_text='Rate captured per transaction')
    content_hash = models.BinaryField()
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('issued', 'Issued'), ('part_paid', 'Part paid'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('credited', 'Credited'), ('void', 'Void')])
    dedupe_key = cf.generated(models.CharField(max_length=120, null=True, blank=True, help_text='learner:period:run — prevents duplicate invoices per learner per period', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'invoice'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Invoice to a payer (immutable once issued; credit notes for changes)'


class InvoiceLine(CedaModel):
    """Invoice line (charge, rule version used, discount and funding applied)"""

    ceda_entity = 'invoice_line'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'line_no': {'type': 'smallint'}, 'charge_type_id': {'type': 'ref', 'ref': 'charge_type'}, 'billing_rule_id': {'type': 'ref', 'ref': 'billing_rule'}, 'rule_version': {'type': 'int_u'}, 'description': {'type': 'str'}, 'gross_minor': {'type': 'money'}, 'discount_minor': {'type': 'money'}, 'funded_minor': {'type': 'money'}, 'net_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id')
    line_no = models.SmallIntegerField()
    charge_type = models.ForeignKey("finance.ChargeType", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='charge_type_id')
    billing_rule = models.ForeignKey("finance.BillingRule", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_rule_id', null=True, blank=True)
    rule_version = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=300)
    gross_minor = models.BigIntegerField(help_text='(minor units)')
    discount_minor = models.BigIntegerField(help_text='(minor units)')
    funded_minor = models.BigIntegerField(help_text='Applied funding sources (no double funding) (minor units)')
    net_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'invoice_line'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Invoice line (charge, rule version used, discount and funding applied)'


class Journal(CedaModel):
    """Journal (balanced set of ledger entries) in a fiscal period"""

    ceda_entity = 'journal'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'journal_number': {'type': 'code'}, 'fiscal_period_id': {'type': 'ref', 'ref': 'fiscal_period'}, 'description': {'type': 'str'}, 'posted_by': {'type': 'uuid'}, 'exported_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'journal_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    journal_number = models.CharField(max_length=32)
    fiscal_period = models.ForeignKey("finance.FiscalPeriod", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='fiscal_period_id')
    description = models.CharField(max_length=500)
    posted_by = cf.UUID7Field()
    exported_at = models.DateTimeField(null=True, blank=True, help_text='Exported to an external ERP/IFMIS where it is the ledger of record')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('posted', 'Posted'), ('reversed', 'Reversed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'journal'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Journal (balanced set of ledger entries) in a fiscal period'


class LedgerEntry(CedaModel):
    """Double-entry posting (append-only; reverse, never edit; partitioned by month)"""

    ceda_entity = 'ledger_entry'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = {'type': 'range_month', 'column': 'posted_on'}
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'journal_id': {'type': 'ref', 'ref': 'journal'}, 'account_id': {'type': 'ref', 'ref': 'account'}, 'posted_on': {'type': 'date'}, 'debit_minor': {'type': 'money'}, 'credit_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'source_kind': {'type': 'code'}, 'source_id': {'type': 'uuid'}, 'rule_versions': {'type': 'json'}, 'reverses_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    journal_id = cf.UUID7Field()
    account_id = cf.UUID7Field()
    posted_on = models.DateField()
    debit_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    credit_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    source_kind = models.CharField(max_length=40, help_text='invoice, payment, payroll_run, credit_note, journal')
    source_id = cf.UUID7Field()
    rule_versions = models.JSONField(null=True, blank=True, help_text='Billing rule versions referenced')
    reverses_id = cf.UUID7Field(null=True, blank=True, help_text='Entry this one reverses')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('id', 'posted_on')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'ledger_entry'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Double-entry posting (append-only; reverse, never edit; partitioned by month)'


class Payment(CedaModel):
    """Incoming payment (gateway, virtual account, transfer, card, USSD, mobile money, cash, cheque, government, employer, scholarship)"""

    ceda_entity = 'payment'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'method': {'type': 'enum', 'enum': 'payment_method'}, 'gateway': {'type': 'code'}, 'gateway_ref': {'type': 'code'}, 'payer_name': {'type': 'name', 'pii': True}, 'payer_contact_hmac': {'type': 'hmac'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'fx_rate_to_reporting': {'type': 'dec'}, 'received_at': {'type': 'ts'}, 'confirmed_at': {'type': 'ts'}, 'receipt_number': {'type': 'code'}, 'allocation_status': {'type': 'enum', 'enum': 'allocation_state'}, 'possible_duplicate_of_id': {'type': 'ref', 'ref': 'payment'}, 'status': {'type': 'enum', 'enum': 'payment_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    method = models.CharField(max_length=32, choices=[('bank_transfer', 'Bank transfer'), ('virtual_account', 'Virtual account'), ('card', 'Card'), ('direct_debit', 'Direct debit'), ('mobile_money', 'Mobile money'), ('ussd', 'Ussd'), ('gateway', 'Gateway'), ('remita', 'Remita'), ('cash', 'Cash'), ('cheque', 'Cheque'), ('government', 'Government'), ('employer', 'Employer'), ('scholarship', 'Scholarship')])
    gateway = models.CharField(max_length=32, null=True, blank=True)
    gateway_ref = models.CharField(max_length=128, null=True, blank=True, help_text='Hard duplicate check')
    payer_name = models.CharField(max_length=200, null=True, blank=True)
    payer_contact_hmac = models.BinaryField(null=True, blank=True, help_text='Soft duplicate check (payer + amount within 10 minutes)')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    fx_rate_to_reporting = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    received_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=32, null=True, blank=True)
    allocation_status = models.CharField(max_length=32, choices=[('unallocated', 'Unallocated'), ('suggested', 'Suggested'), ('part_allocated', 'Part allocated'), ('allocated', 'Allocated')])
    possible_duplicate_of = models.ForeignKey("finance.Payment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='possible_duplicate_of_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('failed', 'Failed'), ('refunded', 'Refunded'), ('held_duplicate', 'Held duplicate')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'payment'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Incoming payment (gateway, virtual account, transfer, card, USSD, mobile money, '


class PaymentAllocation(CedaModel):
    """Allocation of a payment to an invoice (virtual account → reference → payer → heuristic suggestion)"""

    ceda_entity = 'payment_allocation'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'payment_id': {'type': 'ref', 'ref': 'payment'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'method': {'type': 'enum', 'enum': 'allocation_method'}, 'confidence': {'type': 'ratio'}, 'allocated_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    payment = models.ForeignKey("finance.Payment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='payment_id')
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    method = models.CharField(max_length=32, choices=[('virtual_account', 'Virtual account'), ('reference', 'Reference'), ('payer_contact', 'Payer contact'), ('heuristic', 'Heuristic'), ('manual', 'Manual')])
    confidence = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True, help_text='Fee Agent allocates only ≥ 0.95; below that it suggests')
    allocated_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'payment_allocation'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Allocation of a payment to an invoice (virtual account → reference → payer → heu'


class PaymentPlan(CedaModel):
    """Payment plan and hardship assessment under the ethical recovery policy"""

    ceda_entity = 'payment_plan'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'account_id': {'type': 'ref', 'ref': 'account'}, 'instalments': {'type': 'json'}, 'hardship_assessment': {'type': 'sealed', 'class': 'special'}, 'approved_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'plan_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    account = models.ForeignKey("finance.Account", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='account_id')
    instalments = models.JSONField()
    hardship_assessment = models.BinaryField(null=True, blank=True, help_text='Household circumstances (encrypted)')
    approved_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('active', 'Active'), ('under_review', 'Under review'), ('completed', 'Completed'), ('closed', 'Closed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'payment_plan'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Payment plan and hardship assessment under the ethical recovery policy'


class PurchaseOrder(CedaModel):
    """Purchase order, goods receipt and three-way match to the supplier invoice"""

    ceda_entity = 'purchase_order'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'po_number': {'type': 'code'}, 'requisition_id': {'type': 'ref', 'ref': 'requisition'}, 'supplier_id': {'type': 'ref', 'ref': 'supplier'}, 'total_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'received_on': {'type': 'date'}, 'supplier_invoice_ref': {'type': 'code'}, 'match_status': {'type': 'enum', 'enum': 'match_status_3way'}, 'paid_journal_id': {'type': 'ref', 'ref': 'journal'}, 'status': {'type': 'enum', 'enum': 'po_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    po_number = models.CharField(max_length=32)
    requisition = models.ForeignKey("finance.Requisition", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requisition_id', null=True, blank=True)
    supplier = models.ForeignKey("finance.Supplier", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='supplier_id')
    total_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    received_on = models.DateField(null=True, blank=True)
    supplier_invoice_ref = models.CharField(max_length=64, null=True, blank=True)
    match_status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('matched', 'Matched'), ('mismatch', 'Mismatch'), ('override_approved', 'Override approved')])
    paid_journal = models.ForeignKey("finance.Journal", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='paid_journal_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('approved', 'Approved'), ('issued', 'Issued'), ('received', 'Received'), ('invoiced', 'Invoiced'), ('paid', 'Paid'), ('closed', 'Closed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'purchase_order'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Purchase order, goods receipt and three-way match to the supplier invoice'


class RecoveryPolicy(CedaModel):
    """Ethical recovery policy (reminder cadence, payment-plan offers); core education restrictions cannot be configured"""

    ceda_entity = 'recovery_policy'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'version': {'type': 'int_u'}, 'steps': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    version = models.PositiveIntegerField()
    steps = models.JSONField()
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
        db_table = 'recovery_policy'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Ethical recovery policy (reminder cadence, payment-plan offers); core education '


class Requisition(CedaModel):
    """Purchase requisition (delegated approval limits; split-purchase detection)"""

    ceda_entity = 'requisition'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'requisition_number': {'type': 'code'}, 'requested_by': {'type': 'uuid'}, 'cost_centre': {'type': 'code'}, 'line_items': {'type': 'json'}, 'total_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'split_purchase_flag': {'type': 'bool'}, 'workflow_instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    requisition_number = models.CharField(max_length=32)
    requested_by = cf.UUID7Field()
    cost_centre = models.CharField(max_length=32)
    line_items = models.JSONField()
    total_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    split_purchase_flag = models.BooleanField(default=False)
    workflow_instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='workflow_instance_id', null=True, blank=True)
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
        db_table = 'requisition'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Purchase requisition (delegated approval limits; split-purchase detection)'


class Supplier(CedaModel):
    """Supplier 360 master (duplicate detection; call-back verification and dual approval for bank-detail changes)"""

    ceda_entity = 'supplier'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'cac_number': {'type': 'code'}, 'tin': {'type': 'code'}, 'contacts': {'type': 'json', 'pii': True}, 'bank_account_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'bank_account'}, 'bank_account_last4': {'type': 'code', 'class': 'restricted', 'secret_of': 'bank_account'}, 'bank_change_verified_by': {'type': 'uuid'}, 'bank_change_approved_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    cac_number = models.CharField(max_length=20, null=True, blank=True)
    tin = models.CharField(max_length=20, null=True, blank=True)
    contacts = models.JSONField(null=True, blank=True)
    bank_account_enc = models.BinaryField(null=True, blank=True, help_text='Envelope-encrypted bank_account.')
    bank_account_last4 = models.CharField(max_length=4, null=True, blank=True, help_text='Last four characters of bank_account for masked display')
    bank_change_verified_by = cf.UUID7Field(null=True, blank=True)
    bank_change_approved_by = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'supplier'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Supplier 360 master (duplicate detection; call-back verification and dual approv'


class TaxRule(CedaModel):
    """Tax rule (VAT 7.5% where applicable, withholding) by charge type and jurisdiction"""

    ceda_entity = 'tax_rule'
    ceda_zones = ('ops',)
    ceda_domain = 'FIN'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'tax_code': {'type': 'code'}, 'rate': {'type': 'pct'}, 'applies_to': {'type': 'json'}, 'version': {'type': 'int_u'}, 'effective_from': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    tax_code = models.CharField(max_length=16)
    rate = models.DecimalField(max_digits=6, decimal_places=3)
    applies_to = models.JSONField()
    version = models.PositiveIntegerField()
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
        db_table = 'tax_rule'
        app_label = 'finance'
        base_manager_name = 'unscoped'
        verbose_name = 'Tax rule (VAT 7.5% where applicable, withholding) by charge type and jurisdictio'
