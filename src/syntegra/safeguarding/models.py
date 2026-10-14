"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``safeguarding`` — Safeguarding.
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



class CaseAccessGrant(CedaModel):
    """Named need-to-know access to a case (DSL deputies and explicitly granted users)"""

    ceda_entity = 'case_access_grant'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'link'
    ceda_class = 'special'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'case_kind': {'type': 'enum', 'enum': 'vault_case_kind'}, 'case_id': {'type': 'uuid'}, 'user_id': {'type': 'uuid'}, 'granted_by': {'type': 'uuid'}, 'reason': {'type': 'str'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    case_kind = models.CharField(max_length=32, choices=[('safeguarding_case', 'Safeguarding case'), ('staff_case', 'Staff case'), ('community_report', 'Community report'), ('send_profile', 'Send profile')])
    case_id = cf.UUID7Field()
    user_id = cf.UUID7Field()
    granted_by = cf.UUID7Field()
    reason = models.CharField(max_length=500)
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
        db_table = 'case_access_grant'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Named need-to-know access to a case (DSL deputies and explicitly granted users)'


class CaseAccessLog(CedaModel):
    """Every view, export and print of a vault record (shown as the access log on the case)"""

    ceda_entity = 'case_access_log'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = {'type': 'range_month', 'column': 'accessed_at'}
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'case_kind': {'type': 'enum', 'enum': 'vault_case_kind'}, 'case_id': {'type': 'uuid'}, 'user_id': {'type': 'uuid'}, 'access': {'type': 'enum', 'enum': 'access_kind'}, 'purpose_code': {'type': 'code'}, 'accessed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    case_kind = models.CharField(max_length=32, choices=[('safeguarding_case', 'Safeguarding case'), ('staff_case', 'Staff case'), ('community_report', 'Community report'), ('send_profile', 'Send profile')])
    case_id = cf.UUID7Field()
    user_id = cf.UUID7Field()
    access = models.CharField(max_length=32, choices=[('view', 'View'), ('export', 'Export'), ('print', 'Print'), ('share', 'Share')])
    purpose_code = models.CharField(max_length=40)
    accessed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('id', 'accessed_at')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'case_access_log'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Every view, export and print of a vault record (shown as the access log on the c'


class CaseShare(CedaModel):
    """Time-limited, watermarked share of selected chronology entries or a case bundle with a named professional"""

    ceda_entity = 'case_share'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'transaction'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'case_id': {'type': 'ref', 'ref': 'safeguarding_case'}, 'recipient_name': {'type': 'sealed', 'class': 'special'}, 'recipient_email_hmac': {'type': 'hmac'}, 'purpose': {'type': 'str'}, 'legal_basis': {'type': 'enum', 'enum': 'legal_basis'}, 'entry_ids': {'type': 'json'}, 'bundle_hash': {'type': 'hash'}, 'token_hash': {'type': 'hash'}, 'expires_at': {'type': 'ts'}, 'revoked_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    case = models.ForeignKey("safeguarding.SafeguardingCase", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='case_id')
    recipient_name = models.BinaryField()
    recipient_email_hmac = models.BinaryField()
    purpose = models.CharField(max_length=300)
    legal_basis = models.CharField(max_length=32, choices=[('consent', 'Consent'), ('contract', 'Contract'), ('legal_obligation', 'Legal obligation'), ('vital_interests', 'Vital interests'), ('public_task', 'Public task'), ('legitimate_interests', 'Legitimate interests')])
    entry_ids = models.JSONField()
    bundle_hash = models.BinaryField()
    token_hash = models.BinaryField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'case_share'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Time-limited, watermarked share of selected chronology entries or a case bundle '


class CommunityReport(CedaModel):
    """Report received through a community form — anonymous by default; no IP or device data; reply by one-time code"""

    ceda_entity = 'community_report'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'transaction'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'form_id': {'type': 'ref', 'ref': 'reporting_form'}, 'form_version': {'type': 'int_u'}, 'answers': {'type': 'sealed', 'class': 'special'}, 'reporter_identity': {'type': 'sealed', 'class': 'special'}, 'reply_code_hash': {'type': 'hash'}, 'received_at': {'type': 'ts'}, 'triaged_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    form_id = cf.UUID7Field(null=True, blank=True)
    form_version = models.PositiveIntegerField()
    answers = models.BinaryField(help_text='Field-level encrypted answers')
    reporter_identity = models.BinaryField(null=True, blank=True, help_text='Only when the reporter volunteers it')
    reply_code_hash = models.BinaryField(help_text='One-time code for anonymous two-way replies')
    received_at = models.DateTimeField()
    triaged_by = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'community_report'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Report received through a community form — anonymous by default; no IP or device'


class CommunityReportReply(CedaModel):
    """Two-way message on an anonymous community report"""

    ceda_entity = 'community_report_reply'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'report_id': {'type': 'ref', 'ref': 'community_report'}, 'direction': {'type': 'enum', 'enum': 'message_direction'}, 'body': {'type': 'sealed', 'class': 'special'}, 'author_user_id': {'type': 'uuid'}, 'sent_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    report = models.ForeignKey("safeguarding.CommunityReport", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='report_id')
    direction = models.CharField(max_length=32, choices=[('outbound', 'Outbound'), ('inbound', 'Inbound')])
    body = models.BinaryField()
    author_user_id = cf.UUID7Field(null=True, blank=True, help_text='Staff author (NULL for the reporter)')
    sent_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'community_report_reply'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Two-way message on an anonymous community report'


class ReportingForm(CedaModel):
    """Community reporting form (branding, fields, languages; published by link, QR poster, website embed, WhatsApp keyword)"""

    ceda_entity = 'reporting_form'
    ceda_zones = ('ops',)
    ceda_domain = 'SAF'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'fields': {'type': 'json'}, 'languages': {'type': 'cls', 'code_list': 'language'}, 'branding': {'type': 'json'}, 'public_slug': {'type': 'code'}, 'whatsapp_keyword': {'type': 'code'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    fields = models.JSONField()
    languages = models.JSONField()
    branding = models.JSONField(null=True, blank=True)
    public_slug = models.CharField(max_length=64)
    whatsapp_keyword = models.CharField(max_length=32, null=True, blank=True)
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
        db_table = 'reporting_form'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Community reporting form (branding, fields, languages; published by link, QR pos'


class SafeguardingCase(CedaModel):
    """Safeguarding 360 case (risk assessment, actions, referrals, meetings, reviews, closure with sign-off)"""

    ceda_entity = 'safeguarding_case'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'master'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'case_reference': {'type': 'code'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'dsl_user_id': {'type': 'uuid'}, 'risk_level': {'type': 'cl', 'code_list': 'risk_level'}, 'opened_at': {'type': 'ts'}, 'review_due_on': {'type': 'date'}, 'closure_reason': {'type': 'sealed', 'class': 'special'}, 'closed_at': {'type': 'ts'}, 'closed_signed_by': {'type': 'uuid'}, 'transferred_to_institution_id': {'type': 'uuid'}, 'transfer_acknowledged_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    case_reference = models.CharField(max_length=20, help_text='SG-YYYY-NNNN')
    learner_id = cf.UUID7Field()
    dsl_user_id = cf.UUID7Field()
    risk_level = models.CharField(max_length=32, null=True, blank=True, help_text='Set by the DSL only')
    opened_at = models.DateTimeField()
    review_due_on = models.DateField(null=True, blank=True)
    closure_reason = models.BinaryField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_signed_by = cf.UUID7Field(null=True, blank=True)
    transferred_to_institution_id = cf.UUID7Field(null=True, blank=True, help_text='DSL-to-DSL transfer')
    transfer_acknowledged_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'safeguarding_case'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Safeguarding 360 case (risk assessment, actions, referrals, meetings, reviews, c'


class SafeguardingConcern(CedaModel):
    """Concern recorded by any adult (the reporter sees only a receipt afterwards)"""

    ceda_entity = 'safeguarding_concern'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'case_id': {'type': 'ref', 'ref': 'safeguarding_case'}, 'category': {'type': 'cl', 'code_list': 'concern_category'}, 'reported_by': {'type': 'uuid'}, 'source': {'type': 'enum', 'enum': 'concern_source'}, 'body': {'type': 'sealed', 'class': 'special'}, 'body_map': {'type': 'json'}, 'occurred_at': {'type': 'ts'}, 'receipt_code': {'type': 'code'}, 'community_report_id': {'type': 'ref', 'ref': 'community_report'}, 'wellbeing_concern_id': {'type': 'ref', 'ref': 'wellbeing_concern'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    case = models.ForeignKey("safeguarding.SafeguardingCase", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='case_id', null=True, blank=True)
    category = models.CharField(max_length=32, help_text='From the jurisdiction pack (Nigerian default)')
    reported_by = cf.UUID7Field()
    source = models.CharField(max_length=32, choices=[('staff', 'Staff'), ('learner', 'Learner'), ('parent', 'Parent'), ('community_report', 'Community report'), ('wellbeing_keyword', 'Wellbeing keyword'), ('agency', 'Agency')])
    body = models.BinaryField(help_text='What was seen or heard (encrypted, per-record key)')
    body_map = models.JSONField(null=True, blank=True, help_text='Body-map annotations (no free text)')
    occurred_at = models.DateTimeField(null=True, blank=True)
    receipt_code = models.CharField(max_length=16, help_text='Shown to the reporter')
    community_report = models.ForeignKey("safeguarding.CommunityReport", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='community_report_id', null=True, blank=True)
    wellbeing_concern = models.ForeignKey("success.WellbeingConcern", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='wellbeing_concern_id', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'safeguarding_concern'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Concern recorded by any adult (the reporter sees only a receipt afterwards)'


class SafeguardingEntry(CedaModel):
    """Chronology entry — concern, action, decision, agency contact, meeting, review (encrypted text, append-only)"""

    ceda_entity = 'safeguarding_entry'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'case_id': {'type': 'ref', 'ref': 'safeguarding_case'}, 'entry_kind': {'type': 'enum', 'enum': 'chronology_kind'}, 'occurred_at': {'type': 'ts'}, 'author_user_id': {'type': 'uuid'}, 'body': {'type': 'sealed', 'class': 'special'}, 'source_ref': {'type': 'json'}, 'document_ids': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    case = models.ForeignKey("safeguarding.SafeguardingCase", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='case_id')
    entry_kind = models.CharField(max_length=32, choices=[('concern', 'Concern'), ('action', 'Action'), ('decision', 'Decision'), ('agency_contact', 'Agency contact'), ('meeting', 'Meeting'), ('review', 'Review'), ('note', 'Note'), ('document', 'Document')])
    occurred_at = models.DateTimeField()
    author_user_id = cf.UUID7Field()
    body = models.BinaryField()
    source_ref = models.JSONField(null=True, blank=True, help_text='Linked concern, attendance or behaviour record the DSL may see')
    document_ids = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'safeguarding_entry'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Chronology entry — concern, action, decision, agency contact, meeting, review (e'


class SafeguardingReferral(CedaModel):
    """External referral (police, social welfare, health, NGO) with outcome"""

    ceda_entity = 'safeguarding_referral'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'transaction'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'case_id': {'type': 'ref', 'ref': 'safeguarding_case'}, 'agency': {'type': 'str'}, 'agency_contact': {'type': 'sealed', 'class': 'special'}, 'referred_at': {'type': 'ts'}, 'legal_basis': {'type': 'enum', 'enum': 'legal_basis'}, 'outcome': {'type': 'sealed', 'class': 'special'}, 'status': {'type': 'enum', 'enum': 'referral_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    case = models.ForeignKey("safeguarding.SafeguardingCase", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='case_id')
    agency = models.CharField(max_length=200)
    agency_contact = models.BinaryField(null=True, blank=True)
    referred_at = models.DateTimeField()
    legal_basis = models.CharField(max_length=32, choices=[('consent', 'Consent'), ('contract', 'Contract'), ('legal_obligation', 'Legal obligation'), ('vital_interests', 'Vital interests'), ('public_task', 'Public task'), ('legitimate_interests', 'Legitimate interests')])
    outcome = models.BinaryField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('drafted', 'Drafted'), ('sent', 'Sent'), ('acknowledged', 'Acknowledged'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('closed', 'Closed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'safeguarding_referral'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'External referral (police, social welfare, health, NGO) with outcome'


class StaffCase(CedaModel):
    """Allegation, low-level concern or self-referral about an adult (restricted area; head, LGA designated officer, named HR)"""

    ceda_entity = 'staff_case'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'master'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'case_reference': {'type': 'code'}, 'subject_staff_id': {'type': 'uuid'}, 'case_kind': {'type': 'enum', 'enum': 'staff_case_kind'}, 'is_about_head': {'type': 'bool'}, 'designated_officer_user_id': {'type': 'uuid'}, 'outcome': {'type': 'enum', 'enum': 'allegation_outcome'}, 'trcn_referral_at': {'type': 'ts'}, 'police_informed_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    case_reference = models.CharField(max_length=20, help_text='SC-YYYY-NNNN')
    subject_staff_id = cf.UUID7Field(help_text='Staff member concerned (registry)')
    case_kind = models.CharField(max_length=32, choices=[('allegation', 'Allegation'), ('low_level_concern', 'Low level concern'), ('self_referral', 'Self referral')])
    is_about_head = models.BooleanField(default=False)
    designated_officer_user_id = cf.UUID7Field(null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('substantiated', 'Substantiated'), ('unsubstantiated', 'Unsubstantiated'), ('unfounded', 'Unfounded'), ('false', 'False'), ('malicious', 'Malicious')], null=True, blank=True, help_text='substantiated, unsubstantiated, unfounded, false, malicious')
    trcn_referral_at = models.DateTimeField(null=True, blank=True)
    police_informed_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'staff_case'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Allegation, low-level concern or self-referral about an adult (restricted area; '


class StaffCaseEntry(CedaModel):
    """Chronology entry, decision or document on a staff case (hashed, tamper-evident, append-only)"""

    ceda_entity = 'staff_case_entry'
    ceda_zones = ('vault',)
    ceda_domain = 'SAF'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_case_id': {'type': 'ref', 'ref': 'staff_case'}, 'entry_kind': {'type': 'enum', 'enum': 'chronology_kind'}, 'author_user_id': {'type': 'uuid'}, 'body': {'type': 'sealed', 'class': 'special'}, 'document_ids': {'type': 'json'}, 'content_hash': {'type': 'hash'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    staff_case = models.ForeignKey("safeguarding.StaffCase", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='staff_case_id')
    entry_kind = models.CharField(max_length=32, choices=[('concern', 'Concern'), ('action', 'Action'), ('decision', 'Decision'), ('agency_contact', 'Agency contact'), ('meeting', 'Meeting'), ('review', 'Review'), ('note', 'Note'), ('document', 'Document')])
    author_user_id = cf.UUID7Field()
    body = models.BinaryField()
    document_ids = models.JSONField(null=True, blank=True)
    content_hash = models.BinaryField()
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'staff_case_entry'
        app_label = 'safeguarding'
        base_manager_name = 'unscoped'
        verbose_name = 'Chronology entry, decision or document on a staff case (hashed, tamper-evident, '
