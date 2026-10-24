"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``people`` — Staff / Teacher 360, authorisations, HR, cover, recruitment, CPD, training and payroll.
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



class Appraisal(CedaModel):
    """Annual appraisal with objectives, evidence, ratings and development plan"""

    ceda_entity = 'appraisal'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'reviewer_staff_id': {'type': 'ref', 'ref': 'staff'}, 'cycle_label': {'type': 'code'}, 'objectives': {'type': 'json'}, 'evidence': {'type': 'json'}, 'rating': {'type': 'cl', 'code_list': 'appraisal_rating'}, 'development_plan': {'type': 'text'}, 'status': {'type': 'enum', 'enum': 'appraisal_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff_id = cf.UUID7Field()
    reviewer_staff_id = cf.UUID7Field()
    cycle_label = models.CharField(max_length=20, help_text='e.g. 2026/2027')
    objectives = models.JSONField(null=True, blank=True)
    evidence = models.JSONField(null=True, blank=True)
    rating = models.CharField(max_length=32, null=True, blank=True)
    development_plan = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('planned', 'Planned'), ('objectives_set', 'Objectives set'), ('mid_year', 'Mid year'), ('final_review', 'Final review'), ('signed_off', 'Signed off')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'appraisal'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Annual appraisal with objectives, evidence, ratings and development plan'


class CoverAssignment(CedaModel):
    """Cover for a lesson affected by staff absence (never auto-assigned unqualified; G8)"""

    ceda_entity = 'cover_assignment'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'absence_id': {'type': 'ref', 'ref': 'staff_absence'}, 'lesson_occurrence_id': {'type': 'ref', 'ref': 'lesson_occurrence'}, 'cover_staff_id': {'type': 'ref', 'ref': 'staff'}, 'is_qualified': {'type': 'bool'}, 'rank_evidence': {'type': 'json'}, 'alternative': {'type': 'enum', 'enum': 'cover_alternative'}, 'proposed_by': {'type': 'uuid'}, 'confirmed_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'cover_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    absence = models.ForeignKey("people.StaffAbsence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='absence_id')
    lesson_occurrence = models.ForeignKey("timetable.LessonOccurrence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lesson_occurrence_id')
    cover_staff_id = cf.UUID7Field(null=True, blank=True)
    is_qualified = models.BooleanField()
    rank_evidence = models.JSONField(null=True, blank=True, help_text='Qualified → free → lowest cover load → same department')
    alternative = models.CharField(max_length=32, choices=[('supervised_study_with_lms_work', 'Supervised study with lms work'), ('merged_class', 'Merged class'), ('cancelled_lesson', 'Cancelled lesson')], null=True, blank=True, help_text='supervised_study_with_lms_work when no qualified cover')
    proposed_by = cf.UUID7Field(null=True, blank=True, help_text='Cover Agent service identity or SLT user')
    confirmed_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('booked', 'Booked'), ('confirmed', 'Confirmed'), ('declined', 'Declined'), ('gap', 'Gap')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'cover_assignment'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Cover for a lesson affected by staff absence (never auto-assigned unqualified; G'


class CpdRecord(CedaModel):
    """CPD and professional learning record (including LMS training and evidenced digital teaching practice)"""

    ceda_entity = 'cpd_record'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the staff member's posts"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'title': {'type': 'title'}, 'provider_name': {'type': 'title'}, 'cpd_kind': {'type': 'cl', 'code_list': 'cpd_kind'}, 'hours': {'type': 'dec'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'completed_on': {'type': 'date'}, 'evidence_document_id': {'type': 'uuid'}, 'source_kind': {'type': 'code'}, 'source_id': {'type': 'uuid'}, 'expires_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    provider_name = models.CharField(max_length=300, null=True, blank=True)
    cpd_kind = models.CharField(max_length=32)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    subject_id = cf.UUID7Field(null=True, blank=True, help_text='Route to a teaching authorisation')
    completed_on = models.DateField()
    evidence_document_id = cf.UUID7Field(null=True, blank=True)
    source_kind = models.CharField(max_length=40, null=True, blank=True, help_text='lms_course, digital_practice, external')
    source_id = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'cpd_record'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'CPD and professional learning record (including LMS training and evidenced digit'


class JobApplication(CedaModel):
    """Application for a vacancy (blind scoring by default; references and checks before offer)"""

    ceda_entity = 'job_application'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the vacancy'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RECRUIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'vacancy_id': {'type': 'ref', 'ref': 'vacancy'}, 'applicant_name': {'type': 'name', 'pii': True}, 'applicant_email': {'type': 'email', 'pii': True}, 'applicant_phone': {'type': 'phone', 'pii': True}, 'cv_document_id': {'type': 'uuid'}, 'blind_score': {'type': 'dec'}, 'scores': {'type': 'json'}, 'stage': {'type': 'enum', 'enum': 'recruitment_stage'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    vacancy = models.ForeignKey("people.Vacancy", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='vacancy_id')
    applicant_name = models.CharField(max_length=200)
    applicant_email = models.CharField(max_length=254)
    applicant_phone = models.CharField(max_length=16, null=True, blank=True)
    cv_document_id = cf.UUID7Field(null=True, blank=True)
    blind_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    scores = models.JSONField(null=True, blank=True, help_text='Per criterion and panel member')
    stage = models.CharField(max_length=32, choices=[('applied', 'Applied'), ('shortlisted', 'Shortlisted'), ('interview', 'Interview'), ('references', 'References'), ('checks', 'Checks'), ('offer', 'Offer'), ('appointed', 'Appointed'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn')])
    staff_id = cf.UUID7Field(null=True, blank=True, help_text='Set on appointment (after identity matching)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'job_application'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Application for a vacancy (blind scoring by default; references and checks befor'


class PayrollRun(CedaModel):
    """Pay run (two-person approval, bank file export, ledger posting)"""

    ceda_entity = 'payroll_run'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'employer_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'period_label': {'type': 'code'}, 'pay_date': {'type': 'date'}, 'gross_total_minor': {'type': 'money'}, 'net_total_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'prepared_by': {'type': 'uuid'}, 'approved_by': {'type': 'uuid'}, 'second_approver_id': {'type': 'uuid'}, 'bank_file_document_id': {'type': 'uuid'}, 'journal_id': {'type': 'ref', 'ref': 'journal'}, 'status': {'type': 'enum', 'enum': 'payrun_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    employer_scope_id = cf.UUID7Field()
    period_label = models.CharField(max_length=7, help_text='YYYY-MM')
    pay_date = models.DateField()
    gross_total_minor = models.BigIntegerField(help_text='(minor units)')
    net_total_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    prepared_by = cf.UUID7Field()
    approved_by = cf.UUID7Field(null=True, blank=True)
    second_approver_id = cf.UUID7Field(null=True, blank=True)
    bank_file_document_id = cf.UUID7Field(null=True, blank=True)
    journal = models.ForeignKey("finance.Journal", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='journal_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('calculated', 'Calculated'), ('exceptions_review', 'Exceptions review'), ('approved', 'Approved'), ('exported', 'Exported'), ('posted', 'Posted'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'payroll_run'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Pay run (two-person approval, bank file export, ledger posting)'


class PayrollTaxTable(CedaModel):
    """Versioned payroll statutory table (PAYE, pension/PenCom, NHF)"""

    ceda_entity = 'payroll_tax_table'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'table_kind': {'type': 'enum', 'enum': 'payroll_table_kind'}, 'version': {'type': 'int_u'}, 'bands': {'type': 'json'}, 'effective_from': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    table_kind = models.CharField(max_length=32, choices=[('paye', 'Paye'), ('pension', 'Pension'), ('nhf', 'Nhf'), ('nhis', 'Nhis'), ('other', 'Other')])
    version = models.PositiveIntegerField()
    bands = models.JSONField()
    effective_from = models.DateField()
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
        db_table = 'payroll_tax_table'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned payroll statutory table (PAYE, pension/PenCom, NHF)'


class Payslip(CedaModel):
    """Payslip of one staff post in a pay run"""

    ceda_entity = 'payslip'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'payroll_run_id': {'type': 'ref', 'ref': 'payroll_run'}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'gross_minor': {'type': 'money'}, 'deductions_minor': {'type': 'money'}, 'net_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'line_items': {'type': 'json'}, 'bank_account_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'bank_account'}, 'bank_account_last4': {'type': 'code', 'class': 'restricted', 'secret_of': 'bank_account'}, 'exception_flags': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    payroll_run = models.ForeignKey("people.PayrollRun", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='payroll_run_id')
    staff_post_id = cf.UUID7Field()
    gross_minor = models.BigIntegerField(help_text='(minor units)')
    deductions_minor = models.BigIntegerField(help_text='(minor units)')
    net_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    line_items = models.JSONField(help_text='Earnings and deductions by code with tax table versions used')
    bank_account_enc = models.BinaryField(null=True, blank=True, help_text='Envelope-encrypted bank_account. Payee bank account')
    bank_account_last4 = models.CharField(max_length=4, null=True, blank=True, help_text='Last four characters of bank_account for masked display')
    exception_flags = models.JSONField(null=True, blank=True, help_text='Exceptions reviewed before approval')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'payslip'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Payslip of one staff post in a pay run'


class ProfessionalRegistrationCheck(CedaModel):
    """Verification of a professional registration with its register (TRCN, MDCN, NMCN …)"""

    ceda_entity = 'professional_registration_check'
    ceda_zones = ('registry',)
    ceda_domain = 'STF'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'qualification_id': {'type': 'ref', 'ref': 'staff_qualification'}, 'register': {'type': 'cl', 'code_list': 'regulator'}, 'outcome': {'type': 'enum', 'enum': 'verification_outcome'}, 'checked_at': {'type': 'ts'}, 'provider_ref': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    qualification = models.ForeignKey("people.StaffQualification", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='qualification_id')
    register = models.CharField(max_length=32)
    outcome = models.CharField(max_length=32, choices=[('match', 'Match'), ('partial_match', 'Partial match'), ('no_match', 'No match'), ('manual_review', 'Manual review'), ('error', 'Error')])
    checked_at = models.DateTimeField()
    provider_ref = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'professional_registration_check'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Verification of a professional registration with its register (TRCN, MDCN, NMCN '


class Staff(CedaModel):
    """Staff / Teacher 360 master (one person, many posts)"""

    ceda_entity = 'staff'
    ceda_zones = ('registry',)
    ceda_domain = 'STF'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: through the person's posts"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_number': {'type': 'code'}, 'given_name': {'type': 'name', 'pii': True}, 'middle_names': {'type': 'name', 'pii': True}, 'family_name': {'type': 'name', 'pii': True}, 'name_phonetic': {'type': 'str'}, 'date_of_birth': {'type': 'date', 'pii': True}, 'sex': {'type': 'cl', 'code_list': 'sex'}, 'phone': {'type': 'phone', 'pii': True}, 'email': {'type': 'email', 'pii': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'is_historic': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'staff_status'}, 'merged_into': {'type': 'ref', 'ref': 'staff'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff_number = models.CharField(max_length=20, help_text='STF-NNNN-NNNN with check digit')
    given_name = models.CharField(max_length=200)
    middle_names = models.CharField(max_length=200, null=True, blank=True)
    family_name = models.CharField(max_length=200)
    name_phonetic = models.CharField(max_length=120)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=32, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id', null=True, blank=True)
    is_historic = models.BooleanField(default=False, help_text='Created from a digitised personal file')
    status = models.CharField(max_length=32, choices=[('onboarding', 'Onboarding'), ('active', 'Active'), ('leaver', 'Leaver'), ('merged', 'Merged')])
    merged_into = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='merged_into', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'staff'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Staff / Teacher 360 master (one person, many posts)'


class StaffAbsence(CedaModel):
    """Staff absence (triggers the cover process and G8 checks)"""

    ceda_entity = 'staff_absence'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'absence_type': {'type': 'cl', 'code_list': 'absence_type'}, 'starts_at': {'type': 'ts'}, 'ends_at': {'type': 'ts'}, 'is_planned': {'type': 'bool'}, 'reason_note': {'type': 'sealed', 'class': 'special'}, 'approved_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'absence_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff_id = cf.UUID7Field()
    staff_post_id = cf.UUID7Field(null=True, blank=True)
    absence_type = models.CharField(max_length=32)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_planned = models.BooleanField(default=False)
    reason_note = models.BinaryField(null=True, blank=True, help_text='Medical or personal detail (encrypted)')
    approved_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('requested', 'Requested'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('recorded', 'Recorded'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'staff_absence'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Staff absence (triggers the cover process and G8 checks)'


class StaffPost(CedaModel):
    """Post held by a staff member at an institution (employer, unit, title, grade, contract, FTE, line manager)"""

    ceda_entity = 'staff_post'
    ceda_zones = ('registry',)
    ceda_domain = 'STF'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'org_unit_id': {'type': 'ref', 'ref': 'org_unit'}, 'job_title': {'type': 'title'}, 'staff_category': {'type': 'cl', 'code_list': 'staff_category'}, 'academic_rank': {'type': 'cl', 'code_list': 'academic_rank'}, 'grade_step': {'type': 'code'}, 'contract': {'type': 'enum', 'enum': 'contract_kind'}, 'fte': {'type': 'dec'}, 'employer_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'line_manager_staff_id': {'type': 'ref', 'ref': 'staff'}, 'is_temporary': {'type': 'bool'}, 'leaving_reason': {'type': 'cl', 'code_list': 'leaving_reason'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    org_unit = models.ForeignKey("institutions.OrgUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='org_unit_id', null=True, blank=True)
    job_title = models.CharField(max_length=300)
    staff_category = models.CharField(max_length=32, help_text='teaching, non_teaching, lecturer, graduate_assistant …')
    academic_rank = models.CharField(max_length=32, null=True, blank=True, help_text='Professor, Senior Lecturer, Lecturer I … (load policy)')
    grade_step = models.CharField(max_length=20, null=True, blank=True)
    contract = models.CharField(max_length=32, choices=[('permanent', 'Permanent'), ('fixed_term', 'Fixed term'), ('part_time', 'Part time'), ('adjunct', 'Adjunct'), ('visiting', 'Visiting'), ('nysc', 'Nysc'), ('volunteer', 'Volunteer'), ('graduate_assistant', 'Graduate assistant')])
    fte = models.DecimalField(max_digits=4, decimal_places=2)
    employer_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='employer_scope_id', null=True, blank=True)
    line_manager_staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='line_manager_staff_id', null=True, blank=True)
    is_temporary = models.BooleanField(default=False)
    leaving_reason = models.CharField(max_length=32, null=True, blank=True)
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
        db_table = 'staff_post'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Post held by a staff member at an institution (employer, unit, title, grade, con'


class StaffPulseResponse(CedaModel):
    """Anonymous staff wellbeing pulse response (reported only in aggregate; no staff identifier stored)"""

    ceda_entity = 'staff_pulse_response'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'survey_code': {'type': 'code'}, 'org_unit_id': {'type': 'ref', 'ref': 'org_unit'}, 'answers': {'type': 'json'}, 'submitted_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    survey_code = models.CharField(max_length=40)
    org_unit_id = cf.UUID7Field(null=True, blank=True)
    answers = models.JSONField()
    submitted_on = models.DateField(help_text='Date only — no timestamp to resist re-identification')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'staff_pulse_response'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Anonymous staff wellbeing pulse response (reported only in aggregate; no staff i'


class StaffQualification(CedaModel):
    """Qualification, professional registration, teaching authorisation (subject × level) or check, with expiry and verification"""

    ceda_entity = 'staff_qualification'
    ceda_zones = ('registry',)
    ceda_domain = 'STF'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the staff member'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'kind': {'type': 'enum', 'enum': 'qualification_kind'}, 'title': {'type': 'title'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'subject_area_code': {'type': 'code'}, 'levels': {'type': 'cls', 'code_list': 'education_level'}, 'issuer': {'type': 'cl', 'code_list': 'regulator'}, 'reference': {'type': 'code'}, 'issued_on': {'type': 'date'}, 'expires_on': {'type': 'date'}, 'verification': {'type': 'enum', 'enum': 'verification_status'}, 'verified_by': {'type': 'ref', 'ref': 'app_user'}, 'document_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    kind = models.CharField(max_length=32, choices=[('degree', 'Degree'), ('certificate', 'Certificate'), ('registration', 'Registration'), ('teaching_authorisation', 'Teaching authorisation'), ('specialism', 'Specialism'), ('check', 'Check')])
    title = models.CharField(max_length=300)
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='subject_id', null=True, blank=True)
    subject_area_code = models.CharField(max_length=40, null=True, blank=True, help_text='Tertiary specialism (subject area)')
    levels = models.JSONField(null=True, blank=True)
    issuer = models.CharField(max_length=32, null=True, blank=True, help_text='TRCN, university, professional body')
    reference = models.CharField(max_length=64, null=True, blank=True)
    issued_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    verification = models.CharField(max_length=32, choices=[('unverified', 'Unverified'), ('pending', 'Pending'), ('verified', 'Verified'), ('failed', 'Failed'), ('expired', 'Expired')])
    verified_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='verified_by', null=True, blank=True)
    document_id = cf.UUID7Field(null=True, blank=True, help_text='Certificate scan (records zone)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'staff_qualification'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Qualification, professional registration, teaching authorisation (subject × leve'


class TrainingCompletion(CedaModel):
    """Completion of a training course by an adult (writes to Staff 360, CPD and the Education Passport)"""

    ceda_entity = 'training_completion'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the staff member's posts"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'course_id': {'type': 'ref', 'ref': 'training_course'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'assigned_on': {'type': 'date'}, 'completed_on': {'type': 'date'}, 'score': {'type': 'pct'}, 'passed': {'type': 'bool'}, 'certificate_document_id': {'type': 'uuid'}, 'expires_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'training_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    course = models.ForeignKey("people.TrainingCourse", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_id')
    staff_id = cf.UUID7Field()
    assigned_on = models.DateField()
    completed_on = models.DateField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)
    certificate_document_id = cf.UUID7Field(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('assigned', 'Assigned'), ('in_progress', 'In progress'), ('passed', 'Passed'), ('failed', 'Failed'), ('expired', 'Expired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'training_completion'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Completion of a training course by an adult (writes to Staff 360, CPD and the Ed'


class TrainingCourse(CedaModel):
    """Safeguarding or statutory training course (native LMS staff course space or SCORM/xAPI package)"""

    ceda_entity = 'training_course'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'topic': {'type': 'cl', 'code_list': 'training_topic'}, 'course_space_id': {'type': 'ref', 'ref': 'course_space'}, 'package_format': {'type': 'enum', 'enum': 'content_package'}, 'pass_mark': {'type': 'pct'}, 'renewal_months': {'type': 'smallint'}, 'required_for_roles': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    topic = models.CharField(max_length=32, help_text='child protection, safe schools, first aid, fire safety, data protection, online safety, SEND awareness')
    course_space = models.ForeignKey("lms.CourseSpace", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_space_id', null=True, blank=True)
    package_format = models.CharField(max_length=32, choices=[('native_lms', 'Native lms'), ('scorm', 'Scorm'), ('xapi', 'Xapi')], null=True, blank=True)
    pass_mark = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    renewal_months = models.SmallIntegerField(null=True, blank=True)
    required_for_roles = models.JSONField(null=True, blank=True, help_text='Role codes')
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
        db_table = 'training_course'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Safeguarding or statutory training course (native LMS staff course space or SCOR'


class Vacancy(CedaModel):
    """Vacancy in the recruitment workflow"""

    ceda_entity = 'vacancy'
    ceda_zones = ('ops',)
    ceda_domain = 'STF'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RECRUIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'org_unit_id': {'type': 'ref', 'ref': 'org_unit'}, 'title': {'type': 'title'}, 'subjects': {'type': 'json'}, 'coverage_gap_id': {'type': 'ref', 'ref': 'coverage_gap'}, 'closing_on': {'type': 'date'}, 'workflow_instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'status': {'type': 'enum', 'enum': 'vacancy_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    org_unit_id = cf.UUID7Field(null=True, blank=True)
    title = models.CharField(max_length=300)
    subjects = models.JSONField(null=True, blank=True, help_text='Subjects and levels needed (links to coverage gaps)')
    coverage_gap = models.ForeignKey("curriculum.CoverageGap", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='coverage_gap_id', null=True, blank=True)
    closing_on = models.DateField(null=True, blank=True)
    workflow_instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='workflow_instance_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('open', 'Open'), ('closed', 'Closed'), ('filled', 'Filled'), ('withdrawn', 'Withdrawn')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'vacancy'
        app_label = 'people'
        base_manager_name = 'unscoped'
        verbose_name = 'Vacancy in the recruitment workflow'
