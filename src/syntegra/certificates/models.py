"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``certificates`` — Certificate 360 and the state certificate registry.
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



class Certificate(CedaModel):
    """Certificate 360 — authoritative award record (status valid, suspended, revoked, superseded, corrected)"""

    ceda_entity = 'certificate'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'certificate_number': {'type': 'code'}, 'verification_code': {'type': 'code'}, 'credential_kind': {'type': 'enum', 'enum': 'credential_kind'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'qualification_id': {'type': 'ref', 'ref': 'qualification'}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'curriculum_version_id': {'type': 'ref', 'ref': 'curriculum_version'}, 'award_date': {'type': 'date'}, 'award_class': {'type': 'code'}, 'holder_name_on_award': {'type': 'name', 'pii': True}, 'eligibility_result_id': {'type': 'ref', 'ref': 'eligibility_result'}, 'exception_id': {'type': 'ref', 'ref': 'policy_exception'}, 'template_id': {'type': 'ref', 'ref': 'certificate_template'}, 'signatory_id': {'type': 'ref', 'ref': 'signatory'}, 'payload': {'type': 'json'}, 'payload_hash': {'type': 'hash'}, 'signature': {'type': 'bytes'}, 'signing_key_id': {'type': 'ref', 'ref': 'signing_key'}, 'vc_document': {'type': 'json'}, 'pdf_document_id': {'type': 'uuid'}, 'supersedes_id': {'type': 'ref', 'ref': 'certificate'}, 'superseded_by': {'type': 'ref', 'ref': 'certificate'}, 'legacy_award_id': {'type': 'ref', 'ref': 'legacy_award'}, 'status': {'type': 'enum', 'enum': 'certificate_status'}, 'status_changed_at': {'type': 'ts'}, 'award_key': {'type': 'code', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    certificate_number = models.CharField(max_length=32, help_text='<country>-<authority>-<year>-<seq><check>; never reused (decision CD-08)')
    verification_code = models.CharField(max_length=16, help_text='Separate short code printed with the QR')
    credential_kind = models.CharField(max_length=32, choices=[('certificate', 'Certificate'), ('transcript', 'Transcript'), ('testimonial', 'Testimonial'), ('approval_certificate', 'Approval certificate'), ('badge', 'Badge'), ('micro_credential', 'Micro credential'), ('certified_copy', 'Certified copy')])
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id', null=True, blank=True)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    qualification = models.ForeignKey("academic.Qualification", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='qualification_id', null=True, blank=True)
    programme = models.ForeignKey("academic.Programme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id', null=True, blank=True)
    curriculum_version = models.ForeignKey("curriculum.CurriculumVersion", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='curriculum_version_id', null=True, blank=True)
    award_date = models.DateField()
    award_class = models.CharField(max_length=40, null=True, blank=True, help_text='Grade, division or classification')
    holder_name_on_award = models.CharField(max_length=200, help_text='As printed')
    eligibility_result = models.ForeignKey("certificates.EligibilityResult", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='eligibility_result_id', null=True, blank=True)
    exception = models.ForeignKey("governance.PolicyException", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='exception_id', null=True, blank=True)
    template = models.ForeignKey("certificates.CertificateTemplate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='template_id')
    signatory = models.ForeignKey("certificates.Signatory", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='signatory_id')
    payload = models.JSONField(help_text='RFC 8785 canonical JSON payload that was signed')
    payload_hash = models.BinaryField()
    signature = models.BinaryField(help_text='ES256 signature')
    signing_key = models.ForeignKey("certificates.SigningKey", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='signing_key_id')
    vc_document = models.JSONField(null=True, blank=True, help_text='W3C Verifiable Credential 2.0 / Open Badges 3.0')
    pdf_document_id = cf.UUID7Field(null=True, blank=True, help_text='PDF/A with embedded signature (WORM bucket)')
    supersedes = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='supersedes_id', null=True, blank=True)
    superseded_by = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='superseded_by', null=True, blank=True)
    legacy_award = models.ForeignKey("certificates.LegacyAward", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='legacy_award_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('valid', 'Valid'), ('suspended', 'Suspended'), ('revoked', 'Revoked'), ('superseded', 'Superseded'), ('corrected', 'Corrected')])
    status_changed_at = models.DateTimeField()
    award_key = cf.generated(models.CharField(max_length=120, null=True, blank=True, help_text='One certificate per learner per qualification award while valid', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'certificate'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Certificate 360 — authoritative award record (status valid, suspended, revoked, '


class CertificateDelivery(CedaModel):
    """Collection in person or tracked courier delivery of a printed certificate, with recipient identity"""

    ceda_entity = 'certificate_delivery'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'method': {'type': 'enum', 'enum': 'delivery_method'}, 'recipient_name': {'type': 'name', 'pii': True}, 'recipient_id_checked': {'type': 'str'}, 'courier_tracking': {'type': 'code'}, 'delivered_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_id')
    method = models.CharField(max_length=32, choices=[('collection_in_person', 'Collection in person'), ('tracked_courier', 'Tracked courier'), ('digital_only', 'Digital only')])
    recipient_name = models.CharField(max_length=200)
    recipient_id_checked = models.CharField(max_length=120, null=True, blank=True, help_text='Document type checked (no number stored)')
    courier_tracking = models.CharField(max_length=64, null=True, blank=True)
    delivered_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'certificate_delivery'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Collection in person or tracked courier delivery of a printed certificate, with '


class CertificateEvent(CedaModel):
    """Certificate lifecycle event — issue, correct, suspend, reinstate, revoke, reissue, supersede (append-only)"""

    ceda_entity = 'certificate_event'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'event_kind': {'type': 'enum', 'enum': 'certificate_event_kind'}, 'reason': {'type': 'text'}, 'evidence_document_ids': {'type': 'json'}, 'actor_user_id': {'type': 'ref', 'ref': 'app_user'}, 'approver_user_id': {'type': 'ref', 'ref': 'app_user'}, 'workflow_instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_id')
    event_kind = models.CharField(max_length=32, choices=[('issued', 'Issued'), ('corrected', 'Corrected'), ('suspended', 'Suspended'), ('reinstated', 'Reinstated'), ('revoked', 'Revoked'), ('reissued', 'Reissued'), ('superseded', 'Superseded'), ('certified_copy', 'Certified copy')])
    reason = models.TextField()
    evidence_document_ids = models.JSONField(null=True, blank=True)
    actor_user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='actor_user_id')
    approver_user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approver_user_id', null=True, blank=True)
    workflow_instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='workflow_instance_id', null=True, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'certificate_event'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Certificate lifecycle event — issue, correct, suspend, reinstate, revoke, reissu'


class CertificateTemplate(CedaModel):
    """Certificate template (layout, fields, security-print profile) per credential kind and issuer"""

    ceda_entity = 'certificate_template'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'credential_kind': {'type': 'enum', 'enum': 'credential_kind'}, 'qualification_id': {'type': 'ref', 'ref': 'qualification'}, 'layout': {'type': 'json'}, 'print_profile': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    credential_kind = models.CharField(max_length=32, choices=[('certificate', 'Certificate'), ('transcript', 'Transcript'), ('testimonial', 'Testimonial'), ('approval_certificate', 'Approval certificate'), ('badge', 'Badge'), ('micro_credential', 'Micro credential'), ('certified_copy', 'Certified copy')])
    qualification = models.ForeignKey("academic.Qualification", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='qualification_id', null=True, blank=True)
    layout = models.JSONField()
    print_profile = models.JSONField(null=True, blank=True, help_text='Security paper features required')
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
        db_table = 'certificate_template'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Certificate template (layout, fields, security-print profile) per credential kin'


class EligibilityResult(CedaModel):
    """Eligibility-chain result for one learner (identity → institution → … → accreditation at award date → award approval)"""

    ceda_entity = 'eligibility_result'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'run_id': {'type': 'ref', 'ref': 'eligibility_run'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'qualification_id': {'type': 'ref', 'ref': 'qualification'}, 'checks': {'type': 'json'}, 'is_eligible': {'type': 'bool'}, 'evaluated_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    run = models.ForeignKey("certificates.EligibilityRun", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='run_id', null=True, blank=True)
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    qualification = models.ForeignKey("academic.Qualification", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='qualification_id')
    checks = models.JSONField(help_text='Ordered checks with pass/fail and evidence')
    is_eligible = models.BooleanField()
    evaluated_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'eligibility_result'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Eligibility-chain result for one learner (identity → institution → … → accredita'


class EligibilityRun(CedaModel):
    """Batch award-eligibility run for a cohort or series"""

    ceda_entity = 'eligibility_run'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'qualification_id': {'type': 'ref', 'ref': 'qualification'}, 'cohort_filter': {'type': 'json'}, 'learners_total': {'type': 'int_u'}, 'learners_eligible': {'type': 'int_u'}, 'learners_blocked': {'type': 'int_u'}, 'requested_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'run_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    qualification = models.ForeignKey("academic.Qualification", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='qualification_id')
    cohort_filter = models.JSONField()
    learners_total = models.PositiveIntegerField()
    learners_eligible = models.PositiveIntegerField()
    learners_blocked = models.PositiveIntegerField()
    requested_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requested_by')
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
        db_table = 'eligibility_run'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Batch award-eligibility run for a cohort or series'


class FeeSchedule(CedaModel):
    """State fee schedule for services (certificate reissue by type, reason and urgency; certified copies; record copies)"""

    ceda_entity = 'fee_schedule'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-FIN'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'service': {'type': 'enum', 'enum': 'fee_service'}, 'variant': {'type': 'code'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'revenue_code': {'type': 'code'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    service = models.CharField(max_length=32, choices=[('certificate_reissue', 'Certificate reissue'), ('certified_copy', 'Certified copy'), ('legacy_digital_copy', 'Legacy digital copy'), ('record_copy', 'Record copy'), ('transcript', 'Transcript')])
    variant = models.CharField(max_length=40, help_text='Certificate type / reason / urgency key')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    revenue_code = models.CharField(max_length=40)
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
        db_table = 'fee_schedule'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'State fee schedule for services (certificate reissue by type, reason and urgency'


class ForgeryReport(CedaModel):
    """Suspected-forgery report from a verifier, with evidence image, routed to integrity investigators"""

    ceda_entity = 'forgery_report'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'queried_number': {'type': 'code'}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'reporter_org': {'type': 'title'}, 'reporter_contact': {'type': 'str', 'pii': True}, 'evidence_document_id': {'type': 'uuid'}, 'investigator_id': {'type': 'ref', 'ref': 'app_user'}, 'outcome': {'type': 'enum', 'enum': 'review_outcome'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    queried_number = models.CharField(max_length=40)
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_id', null=True, blank=True)
    reporter_org = models.CharField(max_length=300, null=True, blank=True)
    reporter_contact = models.CharField(max_length=200, null=True, blank=True)
    evidence_document_id = cf.UUID7Field(null=True, blank=True)
    investigator = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='investigator_id', null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('no_issue', 'No issue'), ('explained', 'Explained'), ('action_taken', 'Action taken'), ('referred', 'Referred'), ('confirmed', 'Confirmed')], null=True, blank=True)
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
        db_table = 'forgery_report'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Suspected-forgery report from a verifier, with evidence image, routed to integri'


class IdentityCheck(CedaModel):
    """Identity-verification step for a reissue or record-request case (NIN, OTP, facial match with liveness, manual review)"""

    ceda_entity = 'identity_check'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'reissue_case_id': {'type': 'ref', 'ref': 'reissue_case'}, 'method': {'type': 'enum', 'enum': 'identity_method'}, 'outcome': {'type': 'enum', 'enum': 'verification_outcome'}, 'consent_captured': {'type': 'bool'}, 'detail': {'type': 'json'}, 'checked_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    reissue_case = models.ForeignKey("certificates.ReissueCase", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='reissue_case_id')
    method = models.CharField(max_length=32, choices=[('nin_check', 'Nin check'), ('otp', 'Otp'), ('facial_match', 'Facial match'), ('document_review', 'Document review'), ('manual_review', 'Manual review')])
    outcome = models.CharField(max_length=32, choices=[('match', 'Match'), ('partial_match', 'Partial match'), ('no_match', 'No match'), ('manual_review', 'Manual review'), ('error', 'Error')], help_text='A mismatch routes to manual review, never auto-rejects')
    consent_captured = models.BooleanField(default=False, help_text='Explicit consent for facial match; template discarded after the check')
    detail = models.JSONField(null=True, blank=True)
    checked_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'identity_check'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Identity-verification step for a reissue or record-request case (NIN, OTP, facia'


class LegacyAward(CedaModel):
    """Legacy award record created from the digitised archive (marked 'Verified from archive' with source pages)"""

    ceda_entity = 'legacy_award'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'qualification_label': {'type': 'title'}, 'award_year': {'type': 'smallint'}, 'original_number': {'type': 'code'}, 'source_document_id': {'type': 'uuid'}, 'verified_by': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    qualification_label = models.CharField(max_length=300)
    award_year = models.SmallIntegerField()
    original_number = models.CharField(max_length=40, null=True, blank=True)
    source_document_id = cf.UUID7Field(help_text='Digitised register, broadsheet or counterfoil page')
    verified_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='verified_by')
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
        db_table = 'legacy_award'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Legacy award record created from the digitised archive (marked "Verified from ar'


class PrintJob(CedaModel):
    """Print of a signed, approved certificate on registered stock by an authorised printer"""

    ceda_entity = 'print_job'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'stock_id': {'type': 'ref', 'ref': 'security_stock'}, 'printer_ref': {'type': 'code'}, 'printed_by': {'type': 'ref', 'ref': 'app_user'}, 'outcome': {'type': 'enum', 'enum': 'print_outcome'}, 'printed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_id')
    stock = models.ForeignKey("certificates.SecurityStock", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='stock_id')
    printer_ref = models.CharField(max_length=64)
    printed_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='printed_by')
    outcome = models.CharField(max_length=32, choices=[('printed', 'Printed'), ('spoiled', 'Spoiled'), ('refused', 'Refused')])
    printed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'print_job'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Print of a signed, approved certificate on registered stock by an authorised pri'


class RegistryPublication(CedaModel):
    """Publication of a certificate event to the state registry and linked platforms (≤ 60 s) and the Education Passport"""

    ceda_entity = 'registry_publication'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'queue'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'certificate_event_id': {'type': 'ref', 'ref': 'certificate_event'}, 'target': {'type': 'enum', 'enum': 'publication_target'}, 'attempts': {'type': 'smallint'}, 'published_at': {'type': 'ts'}, 'last_error': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'delivery_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    certificate_event = models.ForeignKey("certificates.CertificateEvent", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_event_id')
    target = models.CharField(max_length=32, choices=[('state_registry', 'State registry'), ('state_portal', 'State portal'), ('national_service', 'National service'), ('education_passport', 'Education passport')])
    attempts = models.SmallIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=1000, null=True, blank=True)
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
        db_table = 'registry_publication'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Publication of a certificate event to the state registry and linked platforms (≤'


class ReissueCase(CedaModel):
    """Certificate reissue, correction, certified copy or legacy digital copy request"""

    ceda_entity = 'reissue_case'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'case_number': {'type': 'code'}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'legacy_award_id': {'type': 'ref', 'ref': 'legacy_award'}, 'applicant_user_id': {'type': 'ref', 'ref': 'app_user'}, 'applicant_name': {'type': 'name', 'pii': True}, 'applicant_phone': {'type': 'phone', 'pii': True}, 'reason': {'type': 'enum', 'enum': 'reissue_reason'}, 'urgency': {'type': 'enum', 'enum': 'urgency'}, 'evidence_document_ids': {'type': 'json'}, 'fee_schedule_id': {'type': 'ref', 'ref': 'fee_schedule'}, 'amount_due_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'payment_reference': {'type': 'code'}, 'paid_at': {'type': 'ts'}, 'waiver_approved_by': {'type': 'ref', 'ref': 'app_user'}, 'integrity_flag': {'type': 'bool'}, 'reviewer_id': {'type': 'ref', 'ref': 'app_user'}, 'second_approver_id': {'type': 'ref', 'ref': 'app_user'}, 'new_certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'status': {'type': 'enum', 'enum': 'reissue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    case_number = models.CharField(max_length=32)
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_id', null=True, blank=True)
    legacy_award = models.ForeignKey("certificates.LegacyAward", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='legacy_award_id', null=True, blank=True)
    applicant_user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='applicant_user_id', null=True, blank=True)
    applicant_name = models.CharField(max_length=200)
    applicant_phone = models.CharField(max_length=16)
    reason = models.CharField(max_length=32, choices=[('lost_or_stolen', 'Lost or stolen'), ('damaged', 'Damaged'), ('change_of_name', 'Change of name'), ('issuer_error', 'Issuer error'), ('certified_copy', 'Certified copy'), ('legacy_digital_copy', 'Legacy digital copy')])
    urgency = models.CharField(max_length=32, choices=[('standard', 'Standard'), ('express', 'Express')], default='standard')
    evidence_document_ids = models.JSONField()
    fee_schedule = models.ForeignKey("certificates.FeeSchedule", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='fee_schedule_id', null=True, blank=True)
    amount_due_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    payment_reference = models.CharField(max_length=64, null=True, blank=True, help_text='Remita RRR')
    paid_at = models.DateTimeField(null=True, blank=True, help_text='No payment, no processing')
    waiver_approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='waiver_approved_by', null=True, blank=True)
    integrity_flag = models.BooleanField(default=False)
    reviewer = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='reviewer_id', null=True, blank=True)
    second_approver = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='second_approver_id', null=True, blank=True)
    new_certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='new_certificate_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('submitted', 'Submitted'), ('identity_check', 'Identity check'), ('archive_search', 'Archive search'), ('awaiting_payment', 'Awaiting payment'), ('in_review', 'In review'), ('approved', 'Approved'), ('issued', 'Issued'), ('delivered', 'Delivered'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'reissue_case'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Certificate reissue, correction, certified copy or legacy digital copy request'


class SecurityStock(CedaModel):
    """Security paper sheet by serial (received → issued to institution → printed / spoiled / destroyed)"""

    ceda_entity = 'security_stock'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'master'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'serial': {'type': 'code'}, 'batch_ref': {'type': 'code'}, 'holder_institution_id': {'type': 'ref', 'ref': 'institution'}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'state': {'type': 'enum', 'enum': 'stock_state'}, 'state_changed_at': {'type': 'ts'}, 'destruction_witness': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    serial = models.CharField(max_length=32)
    batch_ref = models.CharField(max_length=40)
    holder_institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='holder_institution_id', null=True, blank=True)
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certificate_id', null=True, blank=True)
    state = models.CharField(max_length=32, choices=[('received', 'Received'), ('issued_to_institution', 'Issued to institution'), ('printed', 'Printed'), ('spoiled', 'Spoiled'), ('destroyed', 'Destroyed'), ('lost', 'Lost')])
    state_changed_at = models.DateTimeField()
    destruction_witness = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'security_stock'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Security paper sheet by serial (received → issued to institution → printed / spo'


class Signatory(CedaModel):
    """Authorised signatory of an issuing authority (with specimen and authority period)"""

    ceda_entity = 'signatory'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'title_on_award': {'type': 'title'}, 'signature_image_document_id': {'type': 'uuid'}, 'max_batch_without_second': {'type': 'int_u'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id')
    title_on_award = models.CharField(max_length=300)
    signature_image_document_id = cf.UUID7Field(null=True, blank=True)
    max_batch_without_second = models.PositiveIntegerField(null=True, blank=True, help_text='Four-eyes threshold for batches')
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
        db_table = 'signatory'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Authorised signatory of an issuing authority (with specimen and authority period'


class SigningKey(CedaModel):
    """Metadata of an HSM-held issuing key (the private key never leaves the HSM; public keys at the JWKS endpoint)"""

    ceda_entity = 'signing_key'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CERT-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'kid': {'type': 'code'}, 'algorithm': {'type': 'code'}, 'public_jwk': {'type': 'json'}, 'hsm_key_ref': {'type': 'str'}, 'ceremony_document_id': {'type': 'uuid'}, 'activated_at': {'type': 'ts'}, 'retired_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'key_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    kid = models.CharField(max_length=64, help_text='e.g. abia-moe-2026-01')
    algorithm = models.CharField(max_length=16, default='ES256')
    public_jwk = models.JSONField()
    hsm_key_ref = models.CharField(max_length=255, help_text='Key handle in the HSM/KMS')
    ceremony_document_id = cf.UUID7Field(null=True, blank=True, help_text='Key ceremony record with ministry witnesses')
    activated_at = models.DateTimeField()
    retired_at = models.DateTimeField(null=True, blank=True, help_text='Retired keys still verify old signatures')
    status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('active', 'Active'), ('retired', 'Retired'), ('compromised', 'Compromised')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'signing_key'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Metadata of an HSM-held issuing key (the private key never leaves the HSM; publi'


class Verification(CedaModel):
    """Public or API certificate verification (minimum disclosure, rate-limited, visible to the holder)"""

    ceda_entity = 'verification'
    ceda_zones = ('registry',)
    ceda_domain = 'CER'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = {'type': 'range_month', 'column': 'verified_at'}
    ceda_retention = 'RS-VERIFY'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'queried_number': {'type': 'code'}, 'channel': {'type': 'enum', 'enum': 'verification_channel_kind'}, 'api_client_id': {'type': 'ref', 'ref': 'api_client'}, 'result': {'type': 'enum', 'enum': 'verification_result'}, 'ip_hash': {'type': 'hmac'}, 'verified_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    certificate_id = cf.UUID7Field(null=True, blank=True, help_text='NULL when no match')
    queried_number = models.CharField(max_length=40)
    channel = models.CharField(max_length=32, choices=[('web_number', 'Web number'), ('qr', 'Qr'), ('secure_link', 'Secure link'), ('bulk_api', 'Bulk api'), ('passport_share', 'Passport share')])
    api_client_id = cf.UUID7Field(null=True, blank=True, help_text='Bulk verifiers')
    result = models.CharField(max_length=32, choices=[('valid', 'Valid'), ('superseded', 'Superseded'), ('revoked', 'Revoked'), ('corrected', 'Corrected'), ('suspended', 'Suspended'), ('not_found', 'Not found'), ('rate_limited', 'Rate limited')])
    ip_hash = models.BinaryField(null=True, blank=True, help_text='Keyed hash of the client IP (abuse detection without storing the IP)')
    verified_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('id', 'verified_at')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'verification'
        app_label = 'certificates'
        base_manager_name = 'unscoped'
        verbose_name = 'Public or API certificate verification (minimum disclosure, rate-limited, visibl'
