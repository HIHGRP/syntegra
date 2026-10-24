"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``hr`` — Enterprise Human Resource Management Suite.
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



class Cadre(CedaModel):
    """Career cadre with progression and statutory retirement rule (e.g. Teacher, Education Officer, Principal, Lecturer)"""

    ceda_entity = 'cadre'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'staff_category': {'type': 'cl', 'code_list': 'staff_category'}, 'is_teaching': {'type': 'bool'}, 'salary_structure_code': {'type': 'code'}, 'entry_grade_level': {'type': 'smallint'}, 'max_grade_level': {'type': 'smallint'}, 'years_per_promotion': {'type': 'smallint'}, 'retirement_age': {'type': 'smallint'}, 'max_years_service': {'type': 'smallint'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=300)
    staff_category = models.CharField(max_length=32)
    is_teaching = models.BooleanField()
    salary_structure_code = models.CharField(max_length=20)
    entry_grade_level = models.SmallIntegerField()
    max_grade_level = models.SmallIntegerField()
    years_per_promotion = models.SmallIntegerField(default=3)
    retirement_age = models.SmallIntegerField(help_text='65 for teachers (Harmonised Retirement Age for Teachers in Nigeria Act 2022), 60 otherwise')
    max_years_service = models.SmallIntegerField(help_text='40 for teachers, 35 otherwise')
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
        db_table = 'cadre'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Career cadre with progression and statutory retirement rule (e.g. Teacher, Educa'


class EmployeeRelationsCase(CedaModel):
    """Employee relations case — query, disciplinary, grievance, appeal or petition with due-process steps and a human outcome"""

    ceda_entity = 'employee_relations_case'
    ceda_zones = ('ops',)
    ceda_domain = 'HRM'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'case_number': {'type': 'code'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'case_kind': {'type': 'enum', 'enum': 'er_case_kind'}, 'summary': {'type': 'text'}, 'vault_allegation_ref': {'type': 'uuid'}, 'raised_by': {'type': 'uuid'}, 'raised_on': {'type': 'date'}, 'response_due_on': {'type': 'date'}, 'steps': {'type': 'json'}, 'outcome': {'type': 'enum', 'enum': 'er_outcome'}, 'outcome_decided_by': {'type': 'uuid'}, 'outcome_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    case_number = models.CharField(max_length=32)
    staff_id = cf.UUID7Field()
    case_kind = models.CharField(max_length=32, choices=[('query', 'Query'), ('disciplinary', 'Disciplinary'), ('grievance', 'Grievance'), ('appeal', 'Appeal'), ('petition', 'Petition')])
    summary = models.TextField(help_text='No special-category content')
    vault_allegation_ref = cf.UUID7Field(null=True, blank=True, help_text='Allegation in the vault (reference only)')
    raised_by = cf.UUID7Field()
    raised_on = models.DateField()
    response_due_on = models.DateField(null=True, blank=True)
    steps = models.JSONField(help_text='Due-process timeline: query issued, response, panel, hearing, decision, appeal window')
    outcome = models.CharField(max_length=32, choices=[('no_case', 'No case'), ('advice', 'Advice'), ('warning', 'Warning'), ('severe_warning', 'Severe warning'), ('suspension', 'Suspension'), ('interdiction', 'Interdiction'), ('demotion', 'Demotion'), ('dismissal', 'Dismissal'), ('retirement_in_public_interest', 'Retirement in public interest'), ('upheld', 'Upheld'), ('not_upheld', 'Not upheld')], null=True, blank=True)
    outcome_decided_by = cf.UUID7Field(null=True, blank=True, help_text='Human decision (A1)')
    outcome_on = models.DateField(null=True, blank=True)
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
        db_table = 'employee_relations_case'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Employee relations case — query, disciplinary, grievance, appeal or petition wit'


class EmploymentRecord(CedaModel):
    """Employment record of a staff post — appointment, confirmation, grade and step, position held and projected retirement"""

    ceda_entity = 'employment_record'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'position_id': {'type': 'ref', 'ref': 'position'}, 'cadre_id': {'type': 'ref', 'ref': 'cadre'}, 'employer_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'appointment_type': {'type': 'enum', 'enum': 'appointment_type'}, 'appointment_letter_ref': {'type': 'code'}, 'first_appointment_on': {'type': 'date'}, 'present_appointment_on': {'type': 'date'}, 'confirmation_due_on': {'type': 'date'}, 'confirmed_on': {'type': 'date'}, 'salary_structure_id': {'type': 'ref', 'ref': 'salary_structure'}, 'grade_level': {'type': 'smallint'}, 'step': {'type': 'smallint'}, 'last_promotion_on': {'type': 'date'}, 'retirement_due_on': {'type': 'date'}, 'retirement_basis': {'type': 'enum', 'enum': 'retirement_basis'}, 'status': {'type': 'enum', 'enum': 'employment_status'}, 'seat_key': {'type': 'uuid', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff_post = models.ForeignKey("people.StaffPost", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_post_id')
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    position = models.ForeignKey("hr.Position", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='position_id', null=True, blank=True)
    cadre = models.ForeignKey("hr.Cadre", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='cadre_id')
    employer_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='employer_scope_id')
    appointment_type = models.CharField(max_length=32, choices=[('first_appointment', 'First appointment'), ('transfer_of_service', 'Transfer of service'), ('secondment', 'Secondment'), ('contract', 'Contract'), ('nysc', 'Nysc'), ('volunteer', 'Volunteer'), ('private_hire', 'Private hire')])
    appointment_letter_ref = models.CharField(max_length=64, null=True, blank=True)
    first_appointment_on = models.DateField(help_text='Date of first appointment into the service')
    present_appointment_on = models.DateField()
    confirmation_due_on = models.DateField(null=True, blank=True)
    confirmed_on = models.DateField(null=True, blank=True)
    salary_structure = models.ForeignKey("hr.SalaryStructure", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='salary_structure_id')
    grade_level = models.SmallIntegerField()
    step = models.SmallIntegerField()
    last_promotion_on = models.DateField(null=True, blank=True)
    retirement_due_on = models.DateField(null=True, blank=True, help_text='Earlier of retirement age and maximum years of service (cadre rule)')
    retirement_basis = models.CharField(max_length=32, choices=[('age', 'Age'), ('length_of_service', 'Length of service'), ('contract_end', 'Contract end'), ('none', 'None')], null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('probation', 'Probation'), ('confirmed', 'Confirmed'), ('suspended', 'Suspended'), ('seconded', 'Seconded'), ('separated', 'Separated')])
    seat_key = cf.generated(cf.UUID7Field(null=True, blank=True, help_text='position_id while the post is active (one active holder per position)', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'employment_record'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Employment record of a staff post — appointment, confirmation, grade and step, p'


class HeadcountExercise(CedaModel):
    """Staff headcount (verification) exercise at an institution — in person, biometric or video"""

    ceda_entity = 'headcount_exercise'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'label': {'type': 'code'}, 'method': {'type': 'enum', 'enum': 'headcount_method'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'conducted_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'plan_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    label = models.CharField(max_length=40, help_text='e.g. 2026-Q4')
    method = models.CharField(max_length=32, choices=[('in_person', 'In person'), ('biometric', 'Biometric'), ('video', 'Video')])
    starts_on = models.DateField()
    ends_on = models.DateField()
    conducted_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='conducted_by')
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
        db_table = 'headcount_exercise'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Staff headcount (verification) exercise at an institution — in person, biometric'


class HeadcountResult(CedaModel):
    """Outcome for one staff member in a headcount exercise"""

    ceda_entity = 'headcount_result'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'exercise_id': {'type': 'ref', 'ref': 'headcount_exercise'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'outcome': {'type': 'enum', 'enum': 'headcount_outcome'}, 'verified_at': {'type': 'ts'}, 'evidence': {'type': 'json'}, 'verifier_id': {'type': 'ref', 'ref': 'app_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    exercise = models.ForeignKey("hr.HeadcountExercise", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='exercise_id')
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    staff_post = models.ForeignKey("people.StaffPost", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_post_id', null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('absent_with_reason', 'Absent with reason'), ('absent_without_reason', 'Absent without reason'), ('not_on_nominal_roll', 'Not on nominal roll'), ('impersonation_suspected', 'Impersonation suspected')])
    verified_at = models.DateTimeField()
    evidence = models.JSONField(null=True, blank=True, help_text='Biometric match score, document seen, witness')
    verifier = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='verifier_id')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'headcount_result'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Outcome for one staff member in a headcount exercise'


class HrIntegrityFlag(CedaModel):
    """Payroll integrity flag across all employers in the state (ghost worker, double employment, pay after exit …)"""

    ceda_entity = 'hr_integrity_flag'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'queue'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'employer_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'flag_kind': {'type': 'enum', 'enum': 'hr_integrity_kind'}, 'evidence': {'type': 'json'}, 'detected_at': {'type': 'ts'}, 'run_label': {'type': 'code'}, 'payroll_hold': {'type': 'bool'}, 'decided_by': {'type': 'ref', 'ref': 'app_user'}, 'decision_reason': {'type': 'text'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'open_key': {'type': 'code', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    employer_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='employer_scope_id', null=True, blank=True)
    flag_kind = models.CharField(max_length=32, choices=[('shared_bank_account', 'Shared bank account'), ('shared_bvn', 'Shared bvn'), ('concurrent_public_posts', 'Concurrent public posts'), ('paid_after_separation', 'Paid after separation'), ('past_retirement_date', 'Past retirement date'), ('no_attendance_30_days', 'No attendance 30 days'), ('failed_headcount', 'Failed headcount'), ('post_without_position', 'Post without position'), ('grade_outside_position', 'Grade outside position')])
    evidence = models.JSONField(help_text='Matching records, dates and sources — never special-category data')
    detected_at = models.DateTimeField()
    run_label = models.CharField(max_length=40, null=True, blank=True)
    payroll_hold = models.BooleanField(default=False, help_text='Set only by a person (A1)')
    decided_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='decided_by', null=True, blank=True)
    decision_reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('in_progress', 'In progress'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed'), ('cancelled', 'Cancelled')])
    open_key = cf.generated(models.CharField(max_length=120, null=True, blank=True, help_text='kind:staff while open (one open flag per kind per staff member)', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'hr_integrity_flag'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Payroll integrity flag across all employers in the state (ghost worker, double e'


class LeaveBalance(CedaModel):
    """Leave balance per staff member, leave type and leave year (the database refuses over-booking)"""

    ceda_entity = 'leave_balance'
    ceda_zones = ('ops',)
    ceda_domain = 'HRM'
    ceda_kind = 'projection'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'leave_type': {'type': 'cl', 'code_list': 'absence_type'}, 'leave_year': {'type': 'smallint'}, 'entitled': {'type': 'dec'}, 'carried_over': {'type': 'dec'}, 'taken': {'type': 'dec'}, 'pending': {'type': 'dec'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff_id = cf.UUID7Field()
    leave_type = models.CharField(max_length=32)
    leave_year = models.SmallIntegerField()
    entitled = models.DecimalField(max_digits=6, decimal_places=1)
    carried_over = models.DecimalField(max_digits=6, decimal_places=1, default='0')
    taken = models.DecimalField(max_digits=6, decimal_places=1, default='0')
    pending = models.DecimalField(max_digits=6, decimal_places=1, default='0')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'leave_balance'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Leave balance per staff member, leave type and leave year (the database refuses '


class LeavePolicy(CedaModel):
    """Leave entitlement rule by leave type, cadre and grade-level band (versioned)"""

    ceda_entity = 'leave_policy'
    ceda_zones = ('ops',)
    ceda_domain = 'HRM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'leave_type': {'type': 'cl', 'code_list': 'absence_type'}, 'cadre_code': {'type': 'code'}, 'grade_level_min': {'type': 'smallint'}, 'grade_level_max': {'type': 'smallint'}, 'days_per_year': {'type': 'dec'}, 'day_basis': {'type': 'enum', 'enum': 'leave_day_basis'}, 'carry_over_max': {'type': 'dec'}, 'requires_document': {'type': 'bool'}, 'is_paid': {'type': 'bool'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    leave_type = models.CharField(max_length=32)
    cadre_code = models.CharField(max_length=20, null=True, blank=True, help_text='NULL = every cadre')
    grade_level_min = models.SmallIntegerField(default=1)
    grade_level_max = models.SmallIntegerField(default=17)
    days_per_year = models.DecimalField(max_digits=6, decimal_places=1)
    day_basis = models.CharField(max_length=32, choices=[('working_days', 'Working days'), ('calendar_days', 'Calendar days')])
    carry_over_max = models.DecimalField(max_digits=6, decimal_places=1, default='0')
    requires_document = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=True)
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
        db_table = 'leave_policy'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Leave entitlement rule by leave type, cadre and grade-level band (versioned)'


class LeaveRequest(CedaModel):
    """Leave request with approval; approval creates the staff absence that starts cover (G8)"""

    ceda_entity = 'leave_request'
    ceda_zones = ('ops',)
    ceda_domain = 'HRM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'leave_type': {'type': 'cl', 'code_list': 'absence_type'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'days': {'type': 'dec'}, 'note': {'type': 'str'}, 'requested_by': {'type': 'uuid'}, 'approver_id': {'type': 'uuid'}, 'decided_at': {'type': 'ts'}, 'relief_staff_id': {'type': 'ref', 'ref': 'staff'}, 'absence_id': {'type': 'ref', 'ref': 'staff_absence'}, 'status': {'type': 'enum', 'enum': 'absence_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff_id = cf.UUID7Field()
    staff_post_id = cf.UUID7Field(null=True, blank=True)
    leave_type = models.CharField(max_length=32)
    starts_on = models.DateField()
    ends_on = models.DateField()
    days = models.DecimalField(max_digits=6, decimal_places=1)
    note = models.CharField(max_length=500, null=True, blank=True, help_text='No medical detail — that goes to staff_absence.reason_note (sealed)')
    requested_by = cf.UUID7Field(help_text='app_user (registry)')
    approver_id = cf.UUID7Field(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    relief_staff_id = cf.UUID7Field(null=True, blank=True)
    absence = models.ForeignKey("people.StaffAbsence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='absence_id', null=True, blank=True)
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
        db_table = 'leave_request'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Leave request with approval; approval creates the staff absence that starts cove'


class PayElement(CedaModel):
    """Payroll element — earning, allowance, statutory or voluntary deduction, loan repayment or employer contribution (versioned)"""

    ceda_entity = 'pay_element'
    ceda_zones = ('ops',)
    ceda_domain = 'HRM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'element_kind': {'type': 'enum', 'enum': 'pay_element_kind'}, 'calc_method': {'type': 'enum', 'enum': 'pay_calc_method'}, 'rate': {'type': 'dec'}, 'table_kind': {'type': 'enum', 'enum': 'payroll_table_kind'}, 'is_taxable': {'type': 'bool'}, 'is_pensionable': {'type': 'bool'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=20, help_text='BASIC, HOUSING, TRANSPORT, RURAL, PAYE, PENSION_EE, PENSION_ER, NHF, UNION, COOP, LOAN …')
    title = models.CharField(max_length=300)
    element_kind = models.CharField(max_length=32, choices=[('earning', 'Earning'), ('allowance', 'Allowance'), ('statutory_deduction', 'Statutory deduction'), ('voluntary_deduction', 'Voluntary deduction'), ('loan_repayment', 'Loan repayment'), ('employer_contribution', 'Employer contribution')])
    calc_method = models.CharField(max_length=32, choices=[('fixed', 'Fixed'), ('pct_of_basic', 'Pct of basic'), ('pct_of_gross', 'Pct of gross'), ('pct_of_pensionable', 'Pct of pensionable'), ('table', 'Table')])
    rate = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True, help_text='Percentage or fixed rate per method')
    table_kind = models.CharField(max_length=32, choices=[('paye', 'Paye'), ('pension', 'Pension'), ('nhf', 'Nhf'), ('nhis', 'Nhis'), ('other', 'Other')], null=True, blank=True, help_text='Statutory table used (PAYE, pension, NHF)')
    is_taxable = models.BooleanField(default=True)
    is_pensionable = models.BooleanField(default=False)
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
        db_table = 'pay_element'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Payroll element — earning, allowance, statutory or voluntary deduction, loan rep'


class Position(CedaModel):
    """Approved establishment position (one seat) at an institution, unit or office, with cadre, grade range and specialism"""

    ceda_entity = 'position'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'position_code': {'type': 'code'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'org_unit_id': {'type': 'ref', 'ref': 'org_unit'}, 'employer_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'title': {'type': 'title'}, 'cadre_id': {'type': 'ref', 'ref': 'cadre'}, 'staff_category': {'type': 'cl', 'code_list': 'staff_category'}, 'grade_level_min': {'type': 'smallint'}, 'grade_level_max': {'type': 'smallint'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'education_levels': {'type': 'cls', 'code_list': 'education_level'}, 'funding': {'type': 'enum', 'enum': 'position_funding'}, 'budget_line': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'position_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    position_code = models.CharField(max_length=32, help_text='POS-<institution code>-NNNN')
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id', null=True, blank=True)
    org_unit = models.ForeignKey("institutions.OrgUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='org_unit_id', null=True, blank=True)
    employer_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='employer_scope_id')
    title = models.CharField(max_length=300)
    cadre = models.ForeignKey("hr.Cadre", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='cadre_id')
    staff_category = models.CharField(max_length=32)
    grade_level_min = models.SmallIntegerField()
    grade_level_max = models.SmallIntegerField()
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='subject_id', null=True, blank=True)
    education_levels = models.JSONField(null=True, blank=True)
    funding = models.CharField(max_length=32, choices=[('funded', 'Funded'), ('unfunded', 'Unfunded'), ('donor_funded', 'Donor funded'), ('privately_funded', 'Privately funded')])
    budget_line = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('approved', 'Approved'), ('frozen', 'Frozen'), ('abolished', 'Abolished')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'position'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Approved establishment position (one seat) at an institution, unit or office, wi'


class PromotionCase(CedaModel):
    """Promotion case of a staff member in a promotion exercise (eligibility, examination, board decision, effective date)"""

    ceda_entity = 'promotion_case'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'employment_record_id': {'type': 'ref', 'ref': 'employment_record'}, 'exercise_label': {'type': 'code'}, 'from_grade_level': {'type': 'smallint'}, 'from_step': {'type': 'smallint'}, 'to_grade_level': {'type': 'smallint'}, 'to_step': {'type': 'smallint'}, 'eligibility': {'type': 'json'}, 'exam_score': {'type': 'pct'}, 'board_decision': {'type': 'enum', 'enum': 'board_decision'}, 'decided_by': {'type': 'ref', 'ref': 'app_user'}, 'effective_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    employment_record = models.ForeignKey("hr.EmploymentRecord", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='employment_record_id')
    exercise_label = models.CharField(max_length=20, help_text='e.g. 2026-PROMO')
    from_grade_level = models.SmallIntegerField()
    from_step = models.SmallIntegerField()
    to_grade_level = models.SmallIntegerField()
    to_step = models.SmallIntegerField()
    eligibility = models.JSONField(help_text='Years on grade, appraisal ratings, examination, discipline status — each with pass/fail')
    exam_score = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    board_decision = models.CharField(max_length=32, choices=[('approved', 'Approved'), ('not_approved', 'Not approved'), ('deferred', 'Deferred')], null=True, blank=True)
    decided_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='decided_by', null=True, blank=True)
    effective_on = models.DateField(null=True, blank=True)
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
        db_table = 'promotion_case'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Promotion case of a staff member in a promotion exercise (eligibility, examinati'


class SalaryScalePoint(CedaModel):
    """Grade level and step of a salary structure version with annual basic and standard allowances"""

    ceda_entity = 'salary_scale_point'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'reference'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'structure_id': {'type': 'ref', 'ref': 'salary_structure'}, 'grade_level': {'type': 'smallint'}, 'step': {'type': 'smallint'}, 'annual_basic_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'allowances': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    structure = models.ForeignKey("hr.SalaryStructure", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='structure_id')
    grade_level = models.SmallIntegerField()
    step = models.SmallIntegerField()
    annual_basic_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    allowances = models.JSONField(null=True, blank=True, help_text='Standard allowances by element code, as amount or % of basic (housing, transport, rural posting …)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'salary_scale_point'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Grade level and step of a salary structure version with annual basic and standar'


class SalaryStructure(CedaModel):
    """Versioned salary structure (CONPSS, CONTISS, CONUASS, CONTEDISS, state teacher scales, private scales)"""

    ceda_entity = 'salary_structure'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'employer_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'currency': {'type': 'currency'}, 'effective_from': {'type': 'date'}, 'version': {'type': 'int_u'}, 'approval_instrument': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=20, help_text='e.g. CONPSS, CONTISS, AB-TSS')
    title = models.CharField(max_length=300)
    employer_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='employer_scope_id', null=True, blank=True)
    currency = models.CharField(max_length=3)
    effective_from = models.DateField()
    version = models.PositiveIntegerField()
    approval_instrument = models.CharField(max_length=200, null=True, blank=True, help_text='Circular or board resolution')
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
        db_table = 'salary_structure'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned salary structure (CONPSS, CONTISS, CONUASS, CONTEDISS, state teacher s'


class Separation(CedaModel):
    """Separation from a post (resignation, retirement, death, dismissal, end of contract, transfer of service) with exit clearance"""

    ceda_entity = 'separation'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'separation_kind': {'type': 'enum', 'enum': 'separation_kind'}, 'notice_on': {'type': 'date'}, 'effective_on': {'type': 'date'}, 'exit_checklist': {'type': 'json'}, 'pension_notified_on': {'type': 'date'}, 'recorded_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    staff_post = models.ForeignKey("people.StaffPost", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_post_id')
    separation_kind = models.CharField(max_length=32, choices=[('resignation', 'Resignation'), ('retirement_statutory', 'Retirement statutory'), ('retirement_voluntary', 'Retirement voluntary'), ('death', 'Death'), ('dismissal', 'Dismissal'), ('termination', 'Termination'), ('end_of_contract', 'End of contract'), ('transfer_of_service', 'Transfer of service'), ('abandonment', 'Abandonment')])
    notice_on = models.DateField(null=True, blank=True)
    effective_on = models.DateField()
    exit_checklist = models.JSONField(help_text='Handover of classes (G9), assets, ID card, final pay, pension notification, access removal')
    pension_notified_on = models.DateField(null=True, blank=True)
    recorded_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='recorded_by')
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
        db_table = 'separation'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Separation from a post (resignation, retirement, death, dismissal, end of contra'


class StaffBankAccount(CedaModel):
    """Staff salary bank account (encrypted; lookup token for duplicate detection; dual approval and call-back on change)"""

    ceda_entity = 'staff_bank_account'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'master'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'bank_code': {'type': 'code'}, 'account_number_hmac': {'type': 'hmac', 'class': 'restricted', 'secret_of': 'account_number'}, 'account_number_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'account_number'}, 'account_number_last4': {'type': 'code', 'class': 'restricted', 'secret_of': 'account_number'}, 'account_name': {'type': 'name', 'pii': True}, 'is_primary': {'type': 'bool'}, 'verified_via': {'type': 'enum', 'enum': 'bank_verification'}, 'verified_at': {'type': 'ts'}, 'requested_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    bank_code = models.CharField(max_length=10, help_text='CBN bank code')
    account_number_hmac = models.BinaryField(help_text='HMAC-SHA-256 lookup of account_number')
    account_number_enc = models.BinaryField(help_text='Envelope-encrypted account_number. NUBAN — envelope-encrypted')
    account_number_last4 = models.CharField(max_length=4, null=True, blank=True, help_text='Last four characters of account_number for masked display')
    account_name = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=True)
    verified_via = models.CharField(max_length=32, choices=[('call_back', 'Call back'), ('nibss_name_enquiry', 'Nibss name enquiry'), ('document', 'Document'), ('none', 'None')], null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    requested_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requested_by')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
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
        db_table = 'staff_bank_account'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Staff salary bank account (encrypted; lookup token for duplicate detection; dual'


class StaffPayElement(CedaModel):
    """Recurring pay element of a staff post (allowance, voluntary deduction, loan with balance), effective-dated"""

    ceda_entity = 'staff_pay_element'
    ceda_zones = ('ops',)
    ceda_domain = 'HRM'
    ceda_kind = 'link'
    ceda_class = 'restricted'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'element_code': {'type': 'code'}, 'amount_minor': {'type': 'money'}, 'rate': {'type': 'dec'}, 'currency': {'type': 'currency'}, 'loan_balance_minor': {'type': 'money'}, 'reference': {'type': 'code'}, 'approved_by': {'type': 'uuid'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff_post_id = cf.UUID7Field()
    element_code = models.CharField(max_length=20)
    amount_minor = models.BigIntegerField(null=True, blank=True, help_text='Monthly amount for fixed elements (minor units)')
    rate = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    currency = models.CharField(max_length=3)
    loan_balance_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    reference = models.CharField(max_length=64, null=True, blank=True)
    approved_by = cf.UUID7Field()
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
        db_table = 'staff_pay_element'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Recurring pay element of a staff post (allowance, voluntary deduction, loan with'


class StaffPosting(CedaModel):
    """Posting order — first posting, transfer, redeployment or secondment of a staff member between institutions and employers"""

    ceda_entity = 'staff_posting'
    ceda_zones = ('registry',)
    ceda_domain = 'HRM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-STF-FILE'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'order_number': {'type': 'code'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'from_staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'to_position_id': {'type': 'ref', 'ref': 'position'}, 'to_institution_id': {'type': 'ref', 'ref': 'institution'}, 'posting_kind': {'type': 'enum', 'enum': 'posting_kind'}, 'reason': {'type': 'text'}, 'effective_on': {'type': 'date'}, 'coverage_impact': {'type': 'json'}, 'requested_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'workflow_instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'new_staff_post_id': {'type': 'ref', 'ref': 'staff_post'}, 'status': {'type': 'enum', 'enum': 'posting_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    order_number = models.CharField(max_length=40)
    staff = models.ForeignKey("people.Staff", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_id')
    from_staff_post = models.ForeignKey("people.StaffPost", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='from_staff_post_id', null=True, blank=True)
    to_position = models.ForeignKey("hr.Position", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='to_position_id')
    to_institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='to_institution_id', null=True, blank=True)
    posting_kind = models.CharField(max_length=32, choices=[('first_posting', 'First posting'), ('transfer', 'Transfer'), ('redeployment', 'Redeployment'), ('secondment', 'Secondment'), ('promotion_posting', 'Promotion posting'), ('rationalisation', 'Rationalisation'), ('on_request', 'On request'), ('disciplinary', 'Disciplinary')])
    reason = models.TextField()
    effective_on = models.DateField()
    coverage_impact = models.JSONField(null=True, blank=True, help_text='Class-subjects left without a teacher of record (G9) at the sending institution')
    requested_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requested_by')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
    workflow_instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='workflow_instance_id', null=True, blank=True)
    new_staff_post = models.ForeignKey("people.StaffPost", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='new_staff_post_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('effective', 'Effective'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'staff_posting'
        app_label = 'hr'
        base_manager_name = 'unscoped'
        verbose_name = 'Posting order — first posting, transfer, redeployment or secondment of a staff m'
