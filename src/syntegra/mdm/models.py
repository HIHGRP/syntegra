"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``mdm`` — Master data management, identity matching and data quality.
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



class DataQualityIssue(CedaModel):
    """Open data-quality issue on a record (validation failure, probable duplicate, stale dataset, conflict)"""

    ceda_entity = 'data_quality_issue'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'MDM'
    ceda_kind = 'queue'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-MDM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_key': {'type': 'code'}, 'dimension': {'type': 'enum', 'enum': 'dq_dimension'}, 'record_kind': {'type': 'code'}, 'record_id': {'type': 'uuid'}, 'detail': {'type': 'str'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'detected_at': {'type': 'ts'}, 'owner_user_id': {'type': 'uuid'}, 'resolved_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule_key = models.CharField(max_length=40)
    dimension = models.CharField(max_length=32, choices=[('completeness', 'Completeness'), ('uniqueness', 'Uniqueness'), ('validity', 'Validity'), ('timeliness', 'Timeliness'), ('consistency', 'Consistency'), ('verification', 'Verification')])
    record_kind = models.CharField(max_length=64)
    record_id = cf.UUID7Field(null=True, blank=True)
    detail = models.CharField(max_length=1000)
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    detected_at = models.DateTimeField()
    owner_user_id = cf.UUID7Field(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'data_quality_issue'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Open data-quality issue on a record (validation failure, probable duplicate, sta'


class DataQualityRule(CedaModel):
    """Data-quality rule feeding the DQI components (completeness, uniqueness, validity, timeliness, consistency, verification)"""

    ceda_entity = 'data_quality_rule'
    ceda_zones = ('registry',)
    ceda_domain = 'MDM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-MDM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_key': {'type': 'code'}, 'dimension': {'type': 'enum', 'enum': 'dq_dimension'}, 'entity': {'type': 'code'}, 'expression': {'type': 'text'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule_key = models.CharField(max_length=40)
    dimension = models.CharField(max_length=32, choices=[('completeness', 'Completeness'), ('uniqueness', 'Uniqueness'), ('validity', 'Validity'), ('timeliness', 'Timeliness'), ('consistency', 'Consistency'), ('verification', 'Verification')])
    entity = models.CharField(max_length=64, help_text='CEDA entity checked')
    expression = models.TextField(help_text='Rule DSL or SQL template over the semantic layer')
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
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
        db_table = 'data_quality_rule'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Data-quality rule feeding the DQI components (completeness, uniqueness, validity'


class DatasetFreshness(CedaModel):
    """Last data received per institution per dataset (stale institutions shown, not hidden)"""

    ceda_entity = 'dataset_freshness'
    ceda_zones = ('registry',)
    ceda_domain = 'MDM'
    ceda_kind = 'projection'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-MDM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'dataset': {'type': 'enum', 'enum': 'dataset_kind'}, 'last_received_at': {'type': 'ts'}, 'expected_interval_hours': {'type': 'smallint'}, 'is_stale': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    dataset = models.CharField(max_length=32, choices=[('enrolment', 'Enrolment'), ('attendance', 'Attendance'), ('staffing', 'Staffing'), ('curriculum_coverage', 'Curriculum coverage'), ('results', 'Results'), ('safety', 'Safety'), ('fees', 'Fees'), ('compliance', 'Compliance'), ('finance', 'Finance'), ('registers', 'Registers')])
    last_received_at = models.DateTimeField(null=True, blank=True)
    expected_interval_hours = models.SmallIntegerField()
    is_stale = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dataset_freshness'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Last data received per institution per dataset (stale institutions shown, not hi'


class ExternalIdentifier(CedaModel):
    """Authorised external identifier of a person (NIN, exam candidate number, UPN, TRCN number …)"""

    ceda_entity = 'external_identifier'
    ceda_zones = ('registry',)
    ceda_domain = 'MDM'
    ceda_kind = 'master'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'person_kind': {'type': 'enum', 'enum': 'person_kind'}, 'person_id': {'type': 'uuid'}, 'scheme': {'type': 'cl', 'code_list': 'identifier_scheme'}, 'value_hmac': {'type': 'hmac', 'class': 'restricted', 'secret_of': 'value'}, 'value_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'value'}, 'value_last4': {'type': 'code', 'class': 'restricted', 'secret_of': 'value'}, 'value_national_hmac': {'type': 'hmac'}, 'issuer': {'type': 'str'}, 'verified_at': {'type': 'ts'}, 'verified_via': {'type': 'enum', 'enum': 'verification_channel'}, 'status': {'type': 'enum', 'enum': 'identifier_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    person_id = cf.UUID7Field(help_text='learner, guardian, staff or provider_person id (polymorphic)')
    scheme = models.CharField(max_length=32, help_text='NG-NIN, WAEC-CAND, NECO-CAND, JAMB-REG, TRCN, UPN, INST-ID …')
    value_hmac = models.BinaryField(help_text='HMAC-SHA-256 lookup of value')
    value_enc = models.BinaryField(help_text='Envelope-encrypted value. Identifier value — envelope-encrypted per tenant and scheme')
    value_last4 = models.CharField(max_length=4, null=True, blank=True, help_text='Last four characters of value for masked display')
    value_national_hmac = models.BinaryField(null=True, blank=True, help_text='National lookup token (federation key) — NIN only, for cross-state matching without exchanging the NIN (CR-002)')
    issuer = models.CharField(max_length=120, null=True, blank=True, help_text='Issuing body where not implied by the scheme')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_via = models.CharField(max_length=32, choices=[('nimc', 'Nimc'), ('registrar', 'Registrar'), ('exam_body', 'Exam body'), ('trcn', 'Trcn'), ('cac', 'Cac'), ('manual', 'Manual')], null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('unverified', 'Unverified'), ('verified', 'Verified'), ('mismatch', 'Mismatch'), ('revoked', 'Revoked')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'external_identifier'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Authorised external identifier of a person (NIN, exam candidate number, UPN, TRC'


class IdentityVerification(CedaModel):
    """Identity verification attempt against a national source (NIMC NIN, TRCN, CAC) — result only, not the source data"""

    ceda_entity = 'identity_verification'
    ceda_zones = ('registry',)
    ceda_domain = 'MDM'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'person_kind': {'type': 'enum', 'enum': 'person_kind'}, 'person_id': {'type': 'uuid'}, 'scheme': {'type': 'cl', 'code_list': 'identifier_scheme'}, 'channel': {'type': 'enum', 'enum': 'verification_channel'}, 'requested_by': {'type': 'uuid'}, 'purpose_code': {'type': 'code'}, 'outcome': {'type': 'enum', 'enum': 'verification_outcome'}, 'match_detail': {'type': 'json'}, 'provider_ref': {'type': 'code'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    person_id = cf.UUID7Field()
    scheme = models.CharField(max_length=32)
    channel = models.CharField(max_length=32, choices=[('nimc', 'Nimc'), ('registrar', 'Registrar'), ('exam_body', 'Exam body'), ('trcn', 'Trcn'), ('cac', 'Cac'), ('manual', 'Manual')])
    requested_by = cf.UUID7Field(help_text='User or service identity')
    purpose_code = models.CharField(max_length=40)
    outcome = models.CharField(max_length=32, choices=[('match', 'Match'), ('partial_match', 'Partial match'), ('no_match', 'No match'), ('manual_review', 'Manual review'), ('error', 'Error')])
    match_detail = models.JSONField(null=True, blank=True, help_text='Field-level agreement (name, DOB) — no source photo or address stored')
    provider_ref = models.CharField(max_length=128, null=True, blank=True, help_text='Gateway transaction reference')
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'identity_verification'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Identity verification attempt against a national source (NIMC NIN, TRCN, CAC) — '


class MatchPairDecision(CedaModel):
    """Remembered steward decision on a pair (suppresses re-raising; trains matching weights)"""

    ceda_entity = 'match_pair_decision'
    ceda_zones = ('registry',)
    ceda_domain = 'MDM'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-MDM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'entity_kind': {'type': 'enum', 'enum': 'match_entity'}, 'record_a_id': {'type': 'uuid'}, 'record_b_id': {'type': 'uuid'}, 'decision': {'type': 'enum', 'enum': 'match_decision'}, 'model_version': {'type': 'semver'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    entity_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('institution', 'Institution'), ('provider', 'Provider'), ('supplier', 'Supplier'), ('course', 'Course'), ('programme', 'Programme')])
    record_a_id = cf.UUID7Field()
    record_b_id = cf.UUID7Field()
    decision = models.CharField(max_length=32, choices=[('same', 'Same'), ('different', 'Different'), ('unsure', 'Unsure')])
    model_version = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'match_pair_decision'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Remembered steward decision on a pair (suppresses re-raising; trains matching we'


class MatchReview(CedaModel):
    """Probable-duplicate pair awaiting or holding a steward decision"""

    ceda_entity = 'match_review'
    ceda_zones = ('registry',)
    ceda_domain = 'MDM'
    ceda_kind = 'queue'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-MDM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'entity_kind': {'type': 'enum', 'enum': 'match_entity'}, 'candidate_id': {'type': 'uuid'}, 'existing_id': {'type': 'uuid'}, 'score': {'type': 'ratio'}, 'evidence': {'type': 'json'}, 'source': {'type': 'enum', 'enum': 'match_source'}, 'assigned_to': {'type': 'ref', 'ref': 'app_user'}, 'decision': {'type': 'enum', 'enum': 'match_decision'}, 'decision_reason': {'type': 'str'}, 'decided_by': {'type': 'ref', 'ref': 'app_user'}, 'decided_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    entity_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('institution', 'Institution'), ('provider', 'Provider'), ('supplier', 'Supplier'), ('course', 'Course'), ('programme', 'Programme')])
    candidate_id = cf.UUID7Field(help_text='Incoming or newer record')
    existing_id = cf.UUID7Field(help_text='Existing master record')
    score = models.DecimalField(max_digits=7, decimal_places=6, help_text='0.80–0.98 probable band; ≥ 0.98 auto-linked (still logged)')
    evidence = models.JSONField(help_text='Field comparisons, blocking keys, model version')
    source = models.CharField(max_length=32, choices=[('registration', 'Registration'), ('import', 'Import'), ('transfer', 'Transfer'), ('digitisation', 'Digitisation'), ('exam_import', 'Exam import'), ('application', 'Application'), ('nightly_scan', 'Nightly scan')])
    assigned_to = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assigned_to', null=True, blank=True)
    decision = models.CharField(max_length=32, choices=[('same', 'Same'), ('different', 'Different'), ('unsure', 'Unsure')], null=True, blank=True)
    decision_reason = models.CharField(max_length=500, null=True, blank=True)
    decided_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='decided_by', null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'match_review'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Probable-duplicate pair awaiting or holding a steward decision'


class MergeJournal(CedaModel):
    """Merge of two master records with survivorship and re-pointed references (un-merge within 90 days)"""

    ceda_entity = 'merge_journal'
    ceda_zones = ('registry',)
    ceda_domain = 'MDM'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-MDM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'entity_kind': {'type': 'enum', 'enum': 'match_entity'}, 'survivor_id': {'type': 'uuid'}, 'merged_id': {'type': 'uuid'}, 'survivorship': {'type': 'json'}, 'repointed': {'type': 'json'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'second_approver_id': {'type': 'ref', 'ref': 'app_user'}, 'merged_at': {'type': 'ts'}, 'unmerge_deadline': {'type': 'date'}, 'unmerged_at': {'type': 'ts'}, 'unmerged_by': {'type': 'ref', 'ref': 'app_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    entity_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('institution', 'Institution'), ('provider', 'Provider'), ('supplier', 'Supplier'), ('course', 'Course'), ('programme', 'Programme')])
    survivor_id = cf.UUID7Field()
    merged_id = cf.UUID7Field(help_text='Becomes an alias that still resolves')
    survivorship = models.JSONField(help_text='Field → chosen source and rule')
    repointed = models.JSONField(help_text='Table → count of references re-pointed')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by')
    second_approver = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='second_approver_id', null=True, blank=True)
    merged_at = models.DateTimeField()
    unmerge_deadline = models.DateField()
    unmerged_at = models.DateTimeField(null=True, blank=True)
    unmerged_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='unmerged_by', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'merge_journal'
        app_label = 'mdm'
        base_manager_name = 'unscoped'
        verbose_name = 'Merge of two master records with survivorship and re-pointed references (un-merg'
