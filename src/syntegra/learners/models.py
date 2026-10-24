"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``learners`` — Learner 360, state enrolment register, transfer and Education Passport.
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



class CmeReferral(CedaModel):
    """Child-missing-education referral to the LGA attendance desk (compulsory-age leaver with unknown destination)"""

    ceda_entity = 'cme_referral'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'lga_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'reason': {'type': 'str'}, 'assigned_to': {'type': 'ref', 'ref': 'app_user'}, 'outcome': {'type': 'enum', 'enum': 'cme_outcome'}, 'closed_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    enrolment = models.ForeignKey("learners.Enrolment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='enrolment_id')
    lga_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lga_scope_id')
    reason = models.CharField(max_length=500)
    assigned_to = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assigned_to', null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('located_enrolled', 'Located enrolled'), ('located_not_enrolled', 'Located not enrolled'), ('moved_out_of_state', 'Moved out of state'), ('not_located', 'Not located'), ('deceased', 'Deceased')], null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'cme_referral'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'Child-missing-education referral to the LGA attendance desk (compulsory-age leav'


class Enrolment(CedaModel):
    """State enrolment register — learner enrolled at an institution (and level, programme) for a period"""

    ceda_entity = 'enrolment'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'operating_tenant_id': {'type': 'uuid'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'cohort_label': {'type': 'str'}, 'is_primary': {'type': 'bool'}, 'basis': {'type': 'enum', 'enum': 'enrolment_basis'}, 'start_on': {'type': 'date'}, 'end_on': {'type': 'date'}, 'leaving_reason': {'type': 'cl', 'code_list': 'leaving_reason'}, 'destination': {'type': 'json'}, 'is_over_capacity_approved': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'enrolment_status'}, 'active_primary_key': {'type': 'uuid', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    operating_tenant_id = cf.UUID7Field(help_text='Tenant whose ops zone holds the operational record')
    education_level = models.CharField(max_length=32)
    programme = models.ForeignKey("academic.Programme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id', null=True, blank=True)
    class_group_id = cf.UUID7Field(null=True, blank=True, help_text='Ops-zone class (arm) for the session')
    cohort_label = models.CharField(max_length=60, null=True, blank=True, help_text='Intake cohort, e.g. 2026/2027 ND1')
    is_primary = models.BooleanField(default=True)
    basis = models.CharField(max_length=32, choices=[('admission', 'Admission'), ('transfer', 'Transfer'), ('promotion', 'Promotion'), ('re_enrolment', 'Re enrolment'), ('temporary', 'Temporary'), ('repeat', 'Repeat')])
    start_on = models.DateField()
    end_on = models.DateField(null=True, blank=True)
    leaving_reason = models.CharField(max_length=32, null=True, blank=True)
    destination = models.JSONField(null=True, blank=True, help_text='Destination institution, employment, unknown …')
    is_over_capacity_approved = models.BooleanField(default=False, help_text='Head approval recorded when capacity is exceeded')
    status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('active', 'Active'), ('completed', 'Completed'), ('withdrawn', 'Withdrawn'), ('transferred', 'Transferred'), ('suspended', 'Suspended')])
    active_primary_key = cf.generated(cf.UUID7Field(null=True, blank=True, help_text='= learner_id when status active and is_primary, else NULL (one active primary enrolment)', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'enrolment'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'State enrolment register — learner enrolled at an institution (and level, progra'


class ExternalExamRecord(CedaModel):
    """Verified external examination result linked to Learner 360 (WAEC, NECO, NABTEB, JAMB) — linked, never re-issued"""

    ceda_entity = 'external_exam_record'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the learner'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'exam_body': {'type': 'cl', 'code_list': 'exam_body'}, 'exam_year': {'type': 'smallint'}, 'candidate_number_hmac': {'type': 'hmac'}, 'results': {'type': 'json'}, 'verified_at': {'type': 'ts'}, 'verification_ref': {'type': 'code'}, 'holder_consents_display': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    exam_body = models.CharField(max_length=32)
    exam_year = models.SmallIntegerField()
    candidate_number_hmac = models.BinaryField(null=True, blank=True, help_text='Lookup token of the candidate number')
    results = models.JSONField(help_text='Subject → grade, as verified')
    verified_at = models.DateTimeField()
    verification_ref = models.CharField(max_length=128)
    holder_consents_display = models.BooleanField(default=False, help_text='Shown on verification results only with consent')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'external_exam_record'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'Verified external examination result linked to Learner 360 (WAEC, NECO, NABTEB, '


class HistoricalRecordImport(CedaModel):
    """Authorised historical record received from a previous institution at enrolment (no re-supply by families)"""

    ceda_entity = 'historical_record_import'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'source_institution_id': {'type': 'ref', 'ref': 'institution'}, 'source_system': {'type': 'str'}, 'datasets': {'type': 'json'}, 'received_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'import_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    enrolment = models.ForeignKey("learners.Enrolment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='enrolment_id')
    source_institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='source_institution_id', null=True, blank=True)
    source_system = models.CharField(max_length=120, null=True, blank=True)
    datasets = models.JSONField(help_text='Results, attendance summary, SEND/safeguarding handover flags')
    received_at = models.DateTimeField()
    status = models.CharField(max_length=32, choices=[('uploaded', 'Uploaded'), ('mapped', 'Mapped'), ('validating', 'Validating'), ('validated', 'Validated'), ('matching', 'Matching'), ('staged', 'Staged'), ('committed', 'Committed'), ('rolled_back', 'Rolled back'), ('failed', 'Failed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'historical_record_import'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'Authorised historical record received from a previous institution at enrolment ('


class Learner(CedaModel):
    """Learner 360 master — one row per person, lifelong"""

    ceda_entity = 'learner'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: visible through an enrolment at an institution inside the grant's subtree, or a purpose-bound state grant"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'global_learner_id': {'type': 'glid'}, 'legal_given_name': {'type': 'name', 'pii': True}, 'legal_middle_names': {'type': 'name', 'pii': True}, 'legal_family_name': {'type': 'name', 'pii': True}, 'preferred_name': {'type': 'name', 'pii': True}, 'name_phonetic': {'type': 'str'}, 'date_of_birth': {'type': 'date', 'pii': True}, 'dob_precision': {'type': 'enum', 'enum': 'date_precision'}, 'sex': {'type': 'cl', 'code_list': 'sex'}, 'nationality': {'type': 'country'}, 'state_of_origin': {'type': 'subdivision'}, 'home_languages': {'type': 'cls', 'code_list': 'language'}, 'photo_document_id': {'type': 'uuid', 'class': 'restricted'}, 'is_historic': {'type': 'bool'}, 'is_minimal_documentation': {'type': 'bool'}, 'identity_verified_level': {'type': 'enum', 'enum': 'identity_level'}, 'status': {'type': 'enum', 'enum': 'learner_status'}, 'merged_into': {'type': 'ref', 'ref': 'learner'}, 'deceased_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    global_learner_id = models.CharField(max_length=16, help_text="LRN-NNNN-NNNN-CC, assigned at creation from the state's leased block, never reused")
    legal_given_name = models.CharField(max_length=200)
    legal_middle_names = models.CharField(max_length=200, null=True, blank=True)
    legal_family_name = models.CharField(max_length=200)
    preferred_name = models.CharField(max_length=200, null=True, blank=True)
    name_phonetic = models.CharField(max_length=120, help_text='Double Metaphone keys + Nigerian name-variant keys for blocking')
    date_of_birth = models.DateField()
    dob_precision = models.CharField(max_length=32, choices=[('day', 'Day'), ('month', 'Month'), ('year', 'Year')], default='day', help_text='Displaced and historic learners may have month or year only')
    sex = models.CharField(max_length=32)
    nationality = models.CharField(max_length=2, null=True, blank=True)
    state_of_origin = models.CharField(max_length=6, null=True, blank=True)
    home_languages = models.JSONField(null=True, blank=True)
    photo_document_id = cf.UUID7Field(null=True, blank=True, help_text='Records zone; restricted')
    is_historic = models.BooleanField(default=False, help_text='Created from a digitised archive (FR-DOC-108)')
    is_minimal_documentation = models.BooleanField(default=False, help_text='Temporary enrolment (IDP camps); identity matching reconciles later')
    identity_verified_level = models.CharField(max_length=32, choices=[('unverified', 'Unverified'), ('document_seen', 'Document seen'), ('nin_verified', 'Nin verified'), ('archive_verified', 'Archive verified')], default='unverified')
    status = models.CharField(max_length=32, choices=[('registered', 'Registered'), ('active', 'Active'), ('left', 'Left'), ('deceased', 'Deceased'), ('merged', 'Merged')])
    merged_into = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='merged_into', null=True, blank=True)
    deceased_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'learner'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner 360 master — one row per person, lifelong'


class LearnerTransfer(CedaModel):
    """Transfer of a learner between institutions (within or across tenants and states), with DSL/SENCO handover acknowledgement"""

    ceda_entity = 'learner_transfer'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'from_enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'to_institution_id': {'type': 'ref', 'ref': 'institution'}, 'to_enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'exchange_transfer_id': {'type': 'ref', 'ref': 'exchange_transfer'}, 'requested_by': {'type': 'ref', 'ref': 'app_user'}, 'effective_on': {'type': 'date'}, 'records_package': {'type': 'json'}, 'dsl_handover_due_on': {'type': 'date'}, 'dsl_acknowledged_at': {'type': 'ts'}, 'senco_acknowledged_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'transfer_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    from_enrolment = models.ForeignKey("learners.Enrolment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='from_enrolment_id')
    to_institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='to_institution_id', null=True, blank=True)
    to_enrolment = models.ForeignKey("learners.Enrolment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='to_enrolment_id', null=True, blank=True)
    exchange_transfer = models.ForeignKey("integration.ExchangeTransfer", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='exchange_transfer_id', null=True, blank=True)
    requested_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requested_by')
    effective_on = models.DateField()
    records_package = models.JSONField(null=True, blank=True, help_text='Datasets transferred per policy')
    dsl_handover_due_on = models.DateField(null=True, blank=True)
    dsl_acknowledged_at = models.DateTimeField(null=True, blank=True, help_text='Safeguarding file acknowledged by receiving DSL')
    senco_acknowledged_at = models.DateTimeField(null=True, blank=True, help_text='SEND file acknowledged by receiving SENCO')
    status = models.CharField(max_length=32, choices=[('requested', 'Requested'), ('accepted', 'Accepted'), ('records_sent', 'Records sent'), ('handover_pending', 'Handover pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'learner_transfer'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'Transfer of a learner between institutions (within or across tenants and states)'


class PassportEntry(CedaModel):
    """Education Passport entry — qualification, certificate, badge, competency, credit, CPD or digital-skills milestone"""

    ceda_entity = 'passport_entry'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'projection'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the holder (learner) and their authorised viewers'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'entry_kind': {'type': 'enum', 'enum': 'passport_entry_kind'}, 'source_kind': {'type': 'code'}, 'source_id': {'type': 'uuid'}, 'title': {'type': 'title'}, 'issuer_name': {'type': 'title'}, 'awarded_on': {'type': 'date'}, 'credential': {'type': 'json'}, 'is_verified': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    entry_kind = models.CharField(max_length=32, choices=[('qualification', 'Qualification'), ('certificate', 'Certificate'), ('transcript', 'Transcript'), ('badge', 'Badge'), ('competency', 'Competency'), ('credit', 'Credit'), ('cpd', 'Cpd'), ('digital_skill', 'Digital skill'), ('guidance', 'Guidance')])
    source_kind = models.CharField(max_length=40)
    source_id = cf.UUID7Field(help_text='Certificate, badge award, competency record, training completion … (soft)')
    title = models.CharField(max_length=300)
    issuer_name = models.CharField(max_length=300, null=True, blank=True)
    awarded_on = models.DateField(null=True, blank=True)
    credential = models.JSONField(null=True, blank=True, help_text='Open Badges 3.0 / W3C VC 2.0 document when issued')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'passport_entry'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'Education Passport entry — qualification, certificate, badge, competency, credit'


class PassportShare(CedaModel):
    """Consented, time-limited, revocable share of a learner's Education Passport"""

    ceda_entity = 'passport_share'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the holder'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'recipient_name': {'type': 'title'}, 'recipient_email': {'type': 'email', 'pii': True}, 'entries': {'type': 'json'}, 'token_hash': {'type': 'hash'}, 'expires_at': {'type': 'ts'}, 'revoked_at': {'type': 'ts'}, 'view_count': {'type': 'int_u'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    recipient_name = models.CharField(max_length=300)
    recipient_email = models.CharField(max_length=254, null=True, blank=True)
    entries = models.JSONField(help_text='Passport entries included')
    token_hash = models.BinaryField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'passport_share'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = "Consented, time-limited, revocable share of a learner's Education Passport"


class PassportView(CedaModel):
    """Verification log of a passport share (holder sees who verified)"""

    ceda_entity = 'passport_view'
    ceda_zones = ('registry',)
    ceda_domain = 'LRN'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-VERIFY'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'share_id': {'type': 'ref', 'ref': 'passport_share'}, 'viewed_at': {'type': 'ts'}, 'ip_country': {'type': 'country'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    share = models.ForeignKey("learners.PassportShare", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='share_id')
    viewed_at = models.DateTimeField()
    ip_country = models.CharField(max_length=2, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'passport_view'
        app_label = 'learners'
        base_manager_name = 'unscoped'
        verbose_name = 'Verification log of a passport share (holder sees who verified)'
