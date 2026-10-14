"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``integration`` — Integration, data exchange, imports, webhooks, idempotency and data-subject requests.
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



class ApiClient(CedaModel):
    """API client (partner, verifier, government system, LMS) with OAuth scopes, mTLS binding and rate limits"""

    ceda_entity = 'api_client'
    ceda_zones = ('registry',)
    ceda_domain = 'INTG'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'client_kind': {'type': 'enum', 'enum': 'api_client_kind'}, 'client_id': {'type': 'code'}, 'secret_hash': {'type': 'hash'}, 'certificate_thumbprint': {'type': 'hash'}, 'scopes': {'type': 'json'}, 'agreement_id': {'type': 'ref', 'ref': 'data_sharing_agreement'}, 'rate_limit_per_minute': {'type': 'int_u'}, 'service_identity_id': {'type': 'ref', 'ref': 'service_identity'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    client_kind = models.CharField(max_length=32, choices=[('partner', 'Partner'), ('bulk_verifier', 'Bulk verifier'), ('government_system', 'Government system'), ('lms', 'Lms'), ('mobile_app', 'Mobile app'), ('internal_service', 'Internal service')])
    client_id = models.CharField(max_length=64)
    secret_hash = models.BinaryField(null=True, blank=True, help_text='Client secret hash (or mTLS certificate thumbprint)')
    certificate_thumbprint = models.BinaryField(null=True, blank=True)
    scopes = models.JSONField()
    agreement = models.ForeignKey("integration.DataSharingAgreement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agreement_id', null=True, blank=True)
    rate_limit_per_minute = models.PositiveIntegerField()
    service_identity = models.ForeignKey("iam.ServiceIdentity", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='service_identity_id')
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
        db_table = 'api_client'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'API client (partner, verifier, government system, LMS) with OAuth scopes, mTLS b'


class DataSharingAgreement(CedaModel):
    """Data-sharing agreement (purpose, datasets, legal basis, parties, residency, expiry)"""

    ceda_entity = 'data_sharing_agreement'
    ceda_zones = ('registry',)
    ceda_domain = 'INTG'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'counterparty': {'type': 'title'}, 'purpose': {'type': 'text'}, 'datasets': {'type': 'json'}, 'legal_basis': {'type': 'enum', 'enum': 'legal_basis'}, 'cross_border': {'type': 'bool'}, 'expires_on': {'type': 'date'}, 'document_id': {'type': 'uuid'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    counterparty = models.CharField(max_length=300)
    purpose = models.TextField()
    datasets = models.JSONField(help_text='Agreed fields only')
    legal_basis = models.CharField(max_length=32, choices=[('consent', 'Consent'), ('contract', 'Contract'), ('legal_obligation', 'Legal obligation'), ('vital_interests', 'Vital interests'), ('public_task', 'Public task'), ('legitimate_interests', 'Legitimate interests')])
    cross_border = models.BooleanField(default=False)
    expires_on = models.DateField()
    document_id = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'data_sharing_agreement'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Data-sharing agreement (purpose, datasets, legal basis, parties, residency, expi'


class ExchangeTransfer(CedaModel):
    """Global Education Data Exchange transfer (learner records, transcripts, results, institution, funding, attendance, outcomes)"""

    ceda_entity = 'exchange_transfer'
    ceda_zones = ('registry',)
    ceda_domain = 'INTG'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-INTG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'agreement_id': {'type': 'ref', 'ref': 'data_sharing_agreement'}, 'direction': {'type': 'enum', 'enum': 'message_direction'}, 'dataset': {'type': 'enum', 'enum': 'exchange_dataset'}, 'subject_ref': {'type': 'uuid'}, 'payload_hash': {'type': 'hash'}, 'payload_format': {'type': 'code'}, 'counterpart_ref': {'type': 'code'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    agreement = models.ForeignKey("integration.DataSharingAgreement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agreement_id')
    direction = models.CharField(max_length=32, choices=[('outbound', 'Outbound'), ('inbound', 'Inbound')])
    dataset = models.CharField(max_length=32, choices=[('learner_record', 'Learner record'), ('transcript', 'Transcript'), ('results', 'Results'), ('institution', 'Institution'), ('staff', 'Staff'), ('funding', 'Funding'), ('attendance', 'Attendance'), ('outcomes', 'Outcomes')])
    subject_ref = cf.UUID7Field(null=True, blank=True, help_text='Learner or institution')
    payload_hash = models.BinaryField()
    payload_format = models.CharField(max_length=32, help_text='OneRoster 1.2, Ed-Fi style, PESC transcript …')
    counterpart_ref = models.CharField(max_length=128, null=True, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'exchange_transfer'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Global Education Data Exchange transfer (learner records, transcripts, results, '


class IdempotencyKey(CedaModel):
    """Client Idempotency-Key and the stored response (retained 24 hours; offline sync operations use the same table)"""

    ceda_entity = 'idempotency_key'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INTG'
    ceda_kind = 'queue'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-TRANSIENT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'principal_id': {'type': 'uuid'}, 'idem_key': {'type': 'code'}, 'request_hash': {'type': 'hash'}, 'response_status': {'type': 'smallint'}, 'response_body': {'type': 'json'}, 'expires_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    principal_id = cf.UUID7Field()
    idem_key = models.CharField(max_length=128)
    request_hash = models.BinaryField()
    response_status = models.SmallIntegerField()
    response_body = models.JSONField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'idempotency_key'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Client Idempotency-Key and the stored response (retained 24 hours; offline sync '


class ImportJob(CedaModel):
    """Legacy data import or migration batch (mapping, validation, matching, staged commit, 30-day rollback)"""

    ceda_entity = 'import_job'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INTG'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'template': {'type': 'enum', 'enum': 'import_template'}, 'source_document_id': {'type': 'uuid'}, 'mapping': {'type': 'json'}, 'rows_total': {'type': 'int_u'}, 'rows_valid': {'type': 'int_u'}, 'rows_matched': {'type': 'int_u'}, 'rows_committed': {'type': 'int_u'}, 'committed_at': {'type': 'ts'}, 'rollback_until': {'type': 'ts'}, 'rolled_back_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'import_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    template = models.CharField(max_length=32, choices=[('learners', 'Learners'), ('guardians', 'Guardians'), ('staff', 'Staff'), ('classes', 'Classes'), ('enrolments', 'Enrolments'), ('marks', 'Marks'), ('balances', 'Balances'), ('assessments', 'Assessments'), ('curriculum', 'Curriculum')])
    source_document_id = cf.UUID7Field()
    mapping = models.JSONField()
    rows_total = models.PositiveIntegerField()
    rows_valid = models.PositiveIntegerField()
    rows_matched = models.PositiveIntegerField()
    rows_committed = models.PositiveIntegerField()
    committed_at = models.DateTimeField(null=True, blank=True)
    rollback_until = models.DateTimeField(null=True, blank=True)
    rolled_back_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'import_job'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Legacy data import or migration batch (mapping, validation, matching, staged com'


class ImportRowIssue(CedaModel):
    """Validation or matching issue on an import row"""

    ceda_entity = 'import_row_issue'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INTG'
    ceda_kind = 'queue'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'job_id': {'type': 'ref', 'ref': 'import_job'}, 'row_no': {'type': 'int_u'}, 'level': {'type': 'enum', 'enum': 'validation_level'}, 'message': {'type': 'str'}, 'error_code': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    job = models.ForeignKey("integration.ImportJob", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='job_id')
    row_no = models.PositiveIntegerField()
    level = models.CharField(max_length=32, choices=[('hard', 'Hard'), ('soft', 'Soft'), ('anomaly', 'Anomaly')])
    message = models.CharField(max_length=1000)
    error_code = models.CharField(max_length=16, null=True, blank=True)
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
        db_table = 'import_row_issue'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Validation or matching issue on an import row'


class InboundWebhook(CedaModel):
    """Inbound webhook received (payment gateway, exam body, WhatsApp, state revenue) — signature verified, processed once"""

    ceda_entity = 'inbound_webhook'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INTG'
    ceda_kind = 'queue'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'source': {'type': 'code'}, 'external_event_id': {'type': 'code'}, 'signature_valid': {'type': 'bool'}, 'payload': {'type': 'json'}, 'received_at': {'type': 'ts'}, 'processed_at': {'type': 'ts'}, 'error': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'delivery_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    source = models.CharField(max_length=40)
    external_event_id = models.CharField(max_length=128, help_text='Provider event id — idempotency key')
    signature_valid = models.BooleanField()
    payload = models.JSONField()
    received_at = models.DateTimeField()
    processed_at = models.DateTimeField(null=True, blank=True)
    error = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('queued', 'Queued'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read'), ('failed', 'Failed'), ('retrying', 'Retrying'), ('abandoned', 'Abandoned'), ('processed', 'Processed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'inbound_webhook'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Inbound webhook received (payment gateway, exam body, WhatsApp, state revenue) —'


class IntegrationConnection(CedaModel):
    """Configured integration (payment gateway, NIMC, exam body, LMS, SSO/SCIM, IFMIS, accounting, OCR engine, originality provider)"""

    ceda_entity = 'integration_connection'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INTG'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'integration_code': {'type': 'code'}, 'adapter_version': {'type': 'semver'}, 'settings': {'type': 'json'}, 'credentials_vault_ref': {'type': 'str'}, 'last_success_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    integration_code = models.CharField(max_length=40, help_text='paystack, flutterwave, remita, nimc, waec, moodle, entra, ifmis …')
    adapter_version = models.CharField(max_length=32)
    settings = models.JSONField(help_text='Non-secret settings')
    credentials_vault_ref = models.CharField(max_length=255, help_text='Secrets in the vault only')
    last_success_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'integration_connection'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Configured integration (payment gateway, NIMC, exam body, LMS, SSO/SCIM, IFMIS, '


class PrivacyRequest(CedaModel):
    """Data-subject request (access, rectification, erasure respecting legal holds, restriction, portability, objection)"""

    ceda_entity = 'privacy_request'
    ceda_zones = ('registry',)
    ceda_domain = 'INTG'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'request_kind': {'type': 'enum', 'enum': 'dsr_kind'}, 'subject_kind': {'type': 'enum', 'enum': 'person_kind'}, 'subject_id': {'type': 'uuid'}, 'requester_name': {'type': 'name', 'pii': True}, 'identity_verified_at': {'type': 'ts'}, 'received_at': {'type': 'ts'}, 'due_at': {'type': 'ts'}, 'outcome': {'type': 'json'}, 'export_document_id': {'type': 'uuid'}, 'handled_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    request_kind = models.CharField(max_length=32, choices=[('access', 'Access'), ('rectification', 'Rectification'), ('erasure', 'Erasure'), ('restriction', 'Restriction'), ('portability', 'Portability'), ('objection', 'Objection')])
    subject_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    subject_id = cf.UUID7Field(null=True, blank=True)
    requester_name = models.CharField(max_length=200)
    identity_verified_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField()
    due_at = models.DateTimeField()
    outcome = models.JSONField(null=True, blank=True, help_text='Per-entity actions (export, redact, crypto-shred, refused with basis)')
    export_document_id = cf.UUID7Field(null=True, blank=True)
    handled_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='handled_by', null=True, blank=True)
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
        db_table = 'privacy_request'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Data-subject request (access, rectification, erasure respecting legal holds, res'


class WebhookDelivery(CedaModel):
    """Delivery attempt of an outbound webhook"""

    ceda_entity = 'webhook_delivery'
    ceda_zones = ('ops',)
    ceda_domain = 'INTG'
    ceda_kind = 'queue'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'subscription_id': {'type': 'ref', 'ref': 'webhook_subscription'}, 'event_id': {'type': 'uuid'}, 'attempts': {'type': 'smallint'}, 'next_attempt_at': {'type': 'ts'}, 'last_status_code': {'type': 'smallint'}, 'delivered_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'delivery_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    subscription = models.ForeignKey("integration.WebhookSubscription", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='subscription_id')
    event_id = cf.UUID7Field()
    attempts = models.SmallIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    last_status_code = models.SmallIntegerField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('queued', 'Queued'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read'), ('failed', 'Failed'), ('retrying', 'Retrying'), ('abandoned', 'Abandoned'), ('processed', 'Processed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'webhook_delivery'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Delivery attempt of an outbound webhook'


class WebhookSubscription(CedaModel):
    """Outbound webhook subscription (tenant-configurable, HMAC-signed, retried with back-off for 24 h)"""

    ceda_entity = 'webhook_subscription'
    ceda_zones = ('ops',)
    ceda_domain = 'INTG'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'api_client_id': {'type': 'uuid'}, 'event_types': {'type': 'json'}, 'target_url': {'type': 'url'}, 'signing_secret_vault_ref': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    api_client_id = cf.UUID7Field(help_text='Registry API client')
    event_types = models.JSONField()
    target_url = models.CharField(max_length=2048)
    signing_secret_vault_ref = models.CharField(max_length=255)
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
        db_table = 'webhook_subscription'
        app_label = 'integration'
        base_manager_name = 'unscoped'
        verbose_name = 'Outbound webhook subscription (tenant-configurable, HMAC-signed, retried with ba'
