"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``funding`` — Funding and loan platforms.
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



class FundingAgreement(CedaModel):
    """Funding agreement — principal, rate, tenor, moratorium, repayment basis, balances and arrears"""

    ceda_entity = 'funding_agreement'
    ceda_zones = ('ops',)
    ceda_domain = 'FND'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FUND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'agreement_number': {'type': 'code'}, 'application_id': {'type': 'ref', 'ref': 'funding_application'}, 'programme_id': {'type': 'ref', 'ref': 'funding_programme'}, 'beneficiary_kind': {'type': 'enum', 'enum': 'funding_beneficiary'}, 'beneficiary_id': {'type': 'uuid'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'instrument': {'type': 'enum', 'enum': 'funding_instrument'}, 'principal_minor': {'type': 'money'}, 'interest_rate': {'type': 'pct'}, 'tenor_months': {'type': 'smallint'}, 'moratorium_months': {'type': 'smallint'}, 'repayment_basis': {'type': 'enum', 'enum': 'repayment_basis'}, 'first_repayment_on': {'type': 'date'}, 'disbursed_minor': {'type': 'money'}, 'repaid_minor': {'type': 'money'}, 'outstanding_minor': {'type': 'money'}, 'arrears_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'signed_on': {'type': 'date'}, 'signed_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'funding_agreement_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    agreement_number = models.CharField(max_length=32)
    application = models.ForeignKey("funding.FundingApplication", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='application_id')
    programme = models.ForeignKey("funding.FundingProgramme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id')
    beneficiary_kind = models.CharField(max_length=32, choices=[('institution', 'Institution'), ('staff', 'Staff'), ('learner', 'Learner')])
    beneficiary_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    instrument = models.CharField(max_length=32, choices=[('loan', 'Loan'), ('grant', 'Grant'), ('scholarship', 'Scholarship'), ('bursary', 'Bursary'), ('intervention', 'Intervention'), ('matching_grant', 'Matching grant'), ('salary_advance', 'Salary advance'), ('bond', 'Bond'), ('guarantee', 'Guarantee'), ('in_kind', 'In kind')])
    principal_minor = models.BigIntegerField(help_text='(minor units)')
    interest_rate = models.DecimalField(max_digits=6, decimal_places=3, default='0')
    tenor_months = models.SmallIntegerField(null=True, blank=True)
    moratorium_months = models.SmallIntegerField(default=0)
    repayment_basis = models.CharField(max_length=32, choices=[('none', 'None'), ('fixed_instalment', 'Fixed instalment'), ('annuity', 'Annuity'), ('income_contingent', 'Income contingent'), ('payroll_deduction', 'Payroll deduction'), ('bullet', 'Bullet')])
    first_repayment_on = models.DateField(null=True, blank=True)
    disbursed_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    repaid_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    outstanding_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    arrears_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    signed_on = models.DateField()
    signed_by = cf.UUID7Field()
    status = models.CharField(max_length=32, choices=[('signed', 'Signed'), ('disbursing', 'Disbursing'), ('in_moratorium', 'In moratorium'), ('repaying', 'Repaying'), ('in_arrears', 'In arrears'), ('settled', 'Settled'), ('completed', 'Completed'), ('written_off', 'Written off'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'funding_agreement'
        app_label = 'funding'
        base_manager_name = 'unscoped'
        verbose_name = 'Funding agreement — principal, rate, tenor, moratorium, repayment basis, balance'


class FundingApplication(CedaModel):
    """Application to a funding programme by or for an institution, a member of staff or a learner"""

    ceda_entity = 'funding_application'
    ceda_zones = ('ops',)
    ceda_domain = 'FND'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FUND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'application_number': {'type': 'code'}, 'programme_id': {'type': 'ref', 'ref': 'funding_programme'}, 'applicant_kind': {'type': 'enum', 'enum': 'funding_beneficiary'}, 'applicant_id': {'type': 'uuid'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'amount_requested_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'purpose_detail': {'type': 'text'}, 'capital_plan_item_id': {'type': 'ref', 'ref': 'capital_plan_item'}, 'documents': {'type': 'json'}, 'eligibility': {'type': 'json'}, 'eligible': {'type': 'bool'}, 'submitted_by': {'type': 'uuid'}, 'submitted_at': {'type': 'ts'}, 'recommended_by': {'type': 'uuid'}, 'recommendation': {'type': 'text'}, 'decided_by': {'type': 'uuid'}, 'decided_at': {'type': 'ts'}, 'decision_reason': {'type': 'text'}, 'amount_approved_minor': {'type': 'money'}, 'status': {'type': 'enum', 'enum': 'funding_application_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    application_number = models.CharField(max_length=32)
    programme = models.ForeignKey("funding.FundingProgramme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id')
    applicant_kind = models.CharField(max_length=32, choices=[('institution', 'Institution'), ('staff', 'Staff'), ('learner', 'Learner')])
    applicant_id = cf.UUID7Field(help_text='Institution, staff or learner id')
    institution_id = cf.UUID7Field()
    amount_requested_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    purpose_detail = models.TextField()
    capital_plan_item = models.ForeignKey("operations.CapitalPlanItem", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='capital_plan_item_id', null=True, blank=True)
    documents = models.JSONField(null=True, blank=True, help_text='Supporting document references')
    eligibility = models.JSONField(null=True, blank=True, help_text='Each rule with its result, as evaluated at submission')
    eligible = models.BooleanField(null=True, blank=True)
    submitted_by = cf.UUID7Field()
    submitted_at = models.DateTimeField(null=True, blank=True)
    recommended_by = cf.UUID7Field(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    decided_by = cf.UUID7Field(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_reason = models.TextField(null=True, blank=True)
    amount_approved_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('under_review', 'Under review'), ('recommended', 'Recommended'), ('approved', 'Approved'), ('declined', 'Declined'), ('withdrawn', 'Withdrawn'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'funding_application'
        app_label = 'funding'
        base_manager_name = 'unscoped'
        verbose_name = 'Application to a funding programme by or for an institution, a member of staff o'


class FundingDisbursement(CedaModel):
    """Disbursement of an agreement to the institution, the beneficiary, a supplier or a contractor"""

    ceda_entity = 'funding_disbursement'
    ceda_zones = ('ops',)
    ceda_domain = 'FND'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FUND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'agreement_id': {'type': 'ref', 'ref': 'funding_agreement'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'payee_kind': {'type': 'enum', 'enum': 'disbursement_payee'}, 'payee_reference': {'type': 'str'}, 'purpose': {'type': 'str'}, 'budget_line_id': {'type': 'ref', 'ref': 'budget_line'}, 'capital_plan_item_id': {'type': 'ref', 'ref': 'capital_plan_item'}, 'reference': {'type': 'code'}, 'disbursed_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'disbursement_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    agreement = models.ForeignKey("funding.FundingAgreement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agreement_id')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    payee_kind = models.CharField(max_length=32, choices=[('institution', 'Institution'), ('beneficiary', 'Beneficiary'), ('supplier', 'Supplier'), ('contractor', 'Contractor')])
    payee_reference = models.CharField(max_length=120, null=True, blank=True, help_text='Institution account, beneficiary or supplier')
    purpose = models.CharField(max_length=200)
    budget_line = models.ForeignKey("finance.BudgetLine", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='budget_line_id', null=True, blank=True)
    capital_plan_item = models.ForeignKey("operations.CapitalPlanItem", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='capital_plan_item_id', null=True, blank=True)
    reference = models.CharField(max_length=64)
    disbursed_on = models.DateField()
    status = models.CharField(max_length=32, choices=[('scheduled', 'Scheduled'), ('paid', 'Paid'), ('failed', 'Failed'), ('reversed', 'Reversed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'funding_disbursement'
        app_label = 'funding'
        base_manager_name = 'unscoped'
        verbose_name = 'Disbursement of an agreement to the institution, the beneficiary, a supplier or '


class FundingProgramme(CedaModel):
    """Funding or loan programme — provider, beneficiary, purpose, instrument, terms and eligibility"""

    ceda_entity = 'funding_programme'
    ceda_zones = ('ops',)
    ceda_domain = 'FND'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'provider_name': {'type': 'str'}, 'provider_kind': {'type': 'enum', 'enum': 'funding_provider_kind'}, 'provider_body_code': {'type': 'code'}, 'beneficiary_kind': {'type': 'enum', 'enum': 'funding_beneficiary'}, 'purpose': {'type': 'enum', 'enum': 'funding_purpose'}, 'instrument': {'type': 'enum', 'enum': 'funding_instrument'}, 'interest_rate': {'type': 'pct'}, 'tenor_months': {'type': 'smallint'}, 'moratorium_months': {'type': 'smallint'}, 'repayment_basis': {'type': 'enum', 'enum': 'repayment_basis'}, 'max_amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'eligibility': {'type': 'json'}, 'terms': {'type': 'json'}, 'opens_on': {'type': 'date'}, 'closes_on': {'type': 'date'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    provider_name = models.CharField(max_length=200)
    provider_kind = models.CharField(max_length=32, choices=[('federal_government_agency', 'Federal government agency'), ('state_government', 'State government'), ('local_government', 'Local government'), ('development_partner', 'Development partner'), ('bank', 'Bank'), ('microfinance', 'Microfinance'), ('cooperative', 'Cooperative'), ('employer', 'Employer'), ('institution', 'Institution'), ('alumni', 'Alumni'), ('philanthropy', 'Philanthropy'), ('other', 'Other')])
    provider_body_code = models.CharField(max_length=16, null=True, blank=True, help_text="Education body in the regulators' directory, e.g. TETFUND, UBEC, NELFUND")
    beneficiary_kind = models.CharField(max_length=32, choices=[('institution', 'Institution'), ('staff', 'Staff'), ('learner', 'Learner')])
    purpose = models.CharField(max_length=32, choices=[('capital_works', 'Capital works'), ('equipment', 'Equipment'), ('ict', 'Ict'), ('research', 'Research'), ('staff_development', 'Staff development'), ('operations', 'Operations'), ('tuition_fees', 'Tuition fees'), ('upkeep', 'Upkeep'), ('housing', 'Housing'), ('vehicle', 'Vehicle'), ('welfare_emergency', 'Welfare emergency'), ('salary_advance', 'Salary advance'), ('scholarship', 'Scholarship'), ('bursary', 'Bursary'), ('special_needs', 'Special needs'), ('other', 'Other')])
    instrument = models.CharField(max_length=32, choices=[('loan', 'Loan'), ('grant', 'Grant'), ('scholarship', 'Scholarship'), ('bursary', 'Bursary'), ('intervention', 'Intervention'), ('matching_grant', 'Matching grant'), ('salary_advance', 'Salary advance'), ('bond', 'Bond'), ('guarantee', 'Guarantee'), ('in_kind', 'In kind')])
    interest_rate = models.DecimalField(max_digits=6, decimal_places=3, default='0', help_text='Annual nominal rate; 0 for interest-free loans and for grants')
    tenor_months = models.SmallIntegerField(null=True, blank=True)
    moratorium_months = models.SmallIntegerField(default=0)
    repayment_basis = models.CharField(max_length=32, choices=[('none', 'None'), ('fixed_instalment', 'Fixed instalment'), ('annuity', 'Annuity'), ('income_contingent', 'Income contingent'), ('payroll_deduction', 'Payroll deduction'), ('bullet', 'Bullet')])
    max_amount_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    eligibility = models.JSONField(null=True, blank=True, help_text='Rules: beneficiary levels, ownership, category, minimum service years, maximum income, matching contribution …')
    terms = models.JSONField(null=True, blank=True, help_text='Further terms as published (e.g. repayment as a share of salary after national service)')
    opens_on = models.DateField(null=True, blank=True)
    closes_on = models.DateField(null=True, blank=True)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
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
        db_table = 'funding_programme'
        app_label = 'funding'
        base_manager_name = 'unscoped'
        verbose_name = 'Funding or loan programme — provider, beneficiary, purpose, instrument, terms an'


class FundingRepayment(CedaModel):
    """Repayment received (payroll deduction, direct debit, transfer, employer remittance) and its allocation to instalments"""

    ceda_entity = 'funding_repayment'
    ceda_zones = ('ops',)
    ceda_domain = 'FND'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-FUND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'agreement_id': {'type': 'ref', 'ref': 'funding_agreement'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'method': {'type': 'enum', 'enum': 'repayment_method'}, 'source_kind': {'type': 'code'}, 'source_id': {'type': 'uuid'}, 'reference': {'type': 'code'}, 'received_on': {'type': 'date'}, 'allocations': {'type': 'json'}, 'recorded_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    agreement = models.ForeignKey("funding.FundingAgreement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agreement_id')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    method = models.CharField(max_length=32, choices=[('payroll_deduction', 'Payroll deduction'), ('direct_debit', 'Direct debit'), ('bank_transfer', 'Bank transfer'), ('employer_remittance', 'Employer remittance'), ('cash', 'Cash'), ('offset', 'Offset')])
    source_kind = models.CharField(max_length=40, null=True, blank=True, help_text='payroll_run, bank_statement_line, remittance')
    source_id = cf.UUID7Field(null=True, blank=True)
    reference = models.CharField(max_length=64)
    received_on = models.DateField()
    allocations = models.JSONField(help_text='Instalment sequence → amount')
    recorded_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'funding_repayment'
        app_label = 'funding'
        base_manager_name = 'unscoped'
        verbose_name = 'Repayment received (payroll deduction, direct debit, transfer, employer remittan'


class RepaymentInstalment(CedaModel):
    """Instalment of a repayment schedule — principal, interest, amount paid and status"""

    ceda_entity = 'repayment_instalment'
    ceda_zones = ('ops',)
    ceda_domain = 'FND'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FUND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'agreement_id': {'type': 'ref', 'ref': 'funding_agreement'}, 'sequence': {'type': 'smallint'}, 'due_on': {'type': 'date'}, 'principal_minor': {'type': 'money'}, 'interest_minor': {'type': 'money'}, 'paid_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'paid_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'instalment_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    agreement = models.ForeignKey("funding.FundingAgreement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agreement_id')
    sequence = models.SmallIntegerField()
    due_on = models.DateField()
    principal_minor = models.BigIntegerField(help_text='(minor units)')
    interest_minor = models.BigIntegerField(help_text='(minor units)')
    paid_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    currency = models.CharField(max_length=3)
    paid_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('due', 'Due'), ('partly_paid', 'Partly paid'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('waived', 'Waived')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'repayment_instalment'
        app_label = 'funding'
        base_manager_name = 'unscoped'
        verbose_name = 'Instalment of a repayment schedule — principal, interest, amount paid and status'
