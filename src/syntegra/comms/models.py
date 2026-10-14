"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``comms`` — Communication.
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



class AnnouncementRecipient(CedaModel):
    """Delivery, read and acknowledgement per announcement recipient"""

    ceda_entity = 'announcement_recipient'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'link'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'announcement_id': {'type': 'ref', 'ref': 'staff_announcement'}, 'user_id': {'type': 'uuid'}, 'delivered_at': {'type': 'ts'}, 'read_at': {'type': 'ts'}, 'acknowledged_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    announcement = models.ForeignKey("comms.StaffAnnouncement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='announcement_id')
    user_id = cf.UUID7Field()
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'announcement_recipient'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Delivery, read and acknowledgement per announcement recipient'


class BroadcastCampaign(CedaModel):
    """Broadcast campaign (audience rules, scheduling, language variants, throttling, cost estimate, results)"""

    ceda_entity = 'broadcast_campaign'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'audience_rule': {'type': 'json'}, 'template_id': {'type': 'ref', 'ref': 'message_template'}, 'scheduled_at': {'type': 'ts'}, 'throttle_per_second': {'type': 'smallint'}, 'recipients_estimated': {'type': 'int_u'}, 'cost_estimate_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'results': {'type': 'json'}, 'approved_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'campaign_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    audience_rule = models.JSONField()
    template = models.ForeignKey("comms.MessageTemplate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='template_id')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    throttle_per_second = models.SmallIntegerField(null=True, blank=True)
    recipients_estimated = models.PositiveIntegerField(null=True, blank=True)
    cost_estimate_minor = models.BigIntegerField(null=True, blank=True, help_text='Counts only template messages outside open service windows (minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    results = models.JSONField(null=True, blank=True)
    approved_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('awaiting_approval', 'Awaiting approval'), ('scheduled', 'Scheduled'), ('sending', 'Sending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'broadcast_campaign'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Broadcast campaign (audience rules, scheduling, language variants, throttling, c'


class ChannelContact(CedaModel):
    """Contact endpoint of a person on a channel (phone or address) with HMAC lookup for inbound matching"""

    ceda_entity = 'channel_contact'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the person's institutions"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'person_kind': {'type': 'enum', 'enum': 'person_kind'}, 'person_id': {'type': 'uuid'}, 'channel': {'type': 'enum', 'enum': 'channel'}, 'endpoint_hmac': {'type': 'hmac', 'secret_of': 'endpoint'}, 'endpoint_enc': {'type': 'secret', 'secret_of': 'endpoint'}, 'endpoint_last4': {'type': 'code', 'secret_of': 'endpoint'}, 'is_verified': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    person_id = cf.UUID7Field()
    channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    endpoint_hmac = models.BinaryField(help_text='HMAC-SHA-256 lookup of endpoint')
    endpoint_enc = models.BinaryField(help_text='Envelope-encrypted endpoint. E.164 phone, e-mail or device token')
    endpoint_last4 = models.CharField(max_length=4, null=True, blank=True, help_text='Last four characters of endpoint for masked display')
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
        db_table = 'channel_contact'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Contact endpoint of a person on a channel (phone or address) with HMAC lookup fo'


class ChannelOptIn(CedaModel):
    """Opt-in / opt-out per contact and channel with evidence (STOP honoured immediately)"""

    ceda_entity = 'channel_opt_in'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'derived: the person'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'contact_id': {'type': 'ref', 'ref': 'channel_contact'}, 'decision': {'type': 'enum', 'enum': 'opt_decision'}, 'category': {'type': 'enum', 'enum': 'template_category'}, 'wording': {'type': 'str'}, 'source': {'type': 'enum', 'enum': 'channel'}, 'decided_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    contact = models.ForeignKey("comms.ChannelContact", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='contact_id')
    decision = models.CharField(max_length=32, choices=[('opt_in', 'Opt in'), ('opt_out', 'Opt out')])
    category = models.CharField(max_length=32, choices=[('utility', 'Utility'), ('authentication', 'Authentication'), ('marketing', 'Marketing'), ('service', 'Service'), ('internal', 'Internal')], null=True, blank=True)
    wording = models.CharField(max_length=1000, help_text='Wording shown at opt-in')
    source = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    decided_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'channel_opt_in'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Opt-in / opt-out per contact and channel with evidence (STOP honoured immediatel'


class ConsentRequest(CedaModel):
    """Request for parental consent (trip, photographs, event, data sharing) — versioned, reminders only to pending parents"""

    ceda_entity = 'consent_request'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'consent_type': {'type': 'cl', 'code_list': 'consent_type'}, 'title': {'type': 'title'}, 'body': {'type': 'text'}, 'version': {'type': 'int_u'}, 'learner_ids': {'type': 'json'}, 'respond_by': {'type': 'ts'}, 'trip_id': {'type': 'ref', 'ref': 'trip'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    consent_type = models.CharField(max_length=32)
    title = models.CharField(max_length=300)
    body = models.TextField()
    version = models.PositiveIntegerField()
    learner_ids = models.JSONField(help_text='Learners covered')
    respond_by = models.DateTimeField(null=True, blank=True)
    trip = models.ForeignKey("operations.Trip", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='trip_id', null=True, blank=True)
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
        db_table = 'consent_request'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Request for parental consent (trip, photographs, event, data sharing) — versione'


class Conversation(CedaModel):
    """Two-way conversation thread (WhatsApp inbox, workspace thread linked to a record, web chat)"""

    ceda_entity = 'conversation'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'channel_id': {'type': 'ref', 'ref': 'message_channel'}, 'contact_id': {'type': 'ref', 'ref': 'channel_contact'}, 'external_thread_ref': {'type': 'code'}, 'linked_record_kind': {'type': 'code'}, 'linked_record_id': {'type': 'uuid'}, 'assigned_office': {'type': 'enum', 'enum': 'office'}, 'assigned_user_id': {'type': 'uuid'}, 'service_window_ends_at': {'type': 'ts'}, 'sla_due_at': {'type': 'ts'}, 'is_bot_handled': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'conversation_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    channel = models.ForeignKey("comms.MessageChannel", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='channel_id')
    contact = models.ForeignKey("comms.ChannelContact", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='contact_id', null=True, blank=True)
    external_thread_ref = models.CharField(max_length=128, null=True, blank=True)
    linked_record_kind = models.CharField(max_length=40, null=True, blank=True, help_text='alert, coverage_gap, corrective_action, inspection, reissue_case')
    linked_record_id = cf.UUID7Field(null=True, blank=True)
    assigned_office = models.CharField(max_length=32, choices=[('class_teacher', 'Class teacher'), ('bursary', 'Bursary'), ('admissions', 'Admissions'), ('pastoral', 'Pastoral'), ('attendance', 'Attendance'), ('helpdesk', 'Helpdesk'), ('head', 'Head')], null=True, blank=True)
    assigned_user_id = cf.UUID7Field(null=True, blank=True)
    service_window_ends_at = models.DateTimeField(null=True, blank=True, help_text='WhatsApp 24-hour customer-service window')
    sla_due_at = models.DateTimeField(null=True, blank=True)
    is_bot_handled = models.BooleanField(default=False, help_text='Parent Concierge Agent; hand-over offered')
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('pending', 'Pending'), ('resolved', 'Resolved'), ('closed', 'Closed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'conversation'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Two-way conversation thread (WhatsApp inbox, workspace thread linked to a record'


class MailMergeJob(CedaModel):
    """Mail-merge run producing letters, labels or badges (every letter stored to the recipient record)"""

    ceda_entity = 'mail_merge_job'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'template_id': {'type': 'ref', 'ref': 'message_template'}, 'recipient_rule': {'type': 'json'}, 'output': {'type': 'enum', 'enum': 'merge_output'}, 'documents_created': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'run_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    template = models.ForeignKey("comms.MessageTemplate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='template_id')
    recipient_rule = models.JSONField()
    output = models.CharField(max_length=32, choices=[('letters_pdf', 'Letters pdf'), ('labels', 'Labels'), ('badges', 'Badges'), ('email', 'Email')])
    documents_created = models.PositiveIntegerField(null=True, blank=True)
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
        db_table = 'mail_merge_job'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Mail-merge run producing letters, labels or badges (every letter stored to the r'


class Message(CedaModel):
    """Message sent or received on any channel (delivery, read, failure status; stored against the recipient record)"""

    ceda_entity = 'message'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the recipient's institution"
    ceda_append_only = False
    ceda_partition = {'type': 'range_month', 'column': 'created_on'}
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'created_on': {'type': 'date'}, 'conversation_id': {'type': 'ref', 'ref': 'conversation'}, 'campaign_id': {'type': 'ref', 'ref': 'broadcast_campaign'}, 'notification_id': {'type': 'ref', 'ref': 'notification'}, 'direction': {'type': 'enum', 'enum': 'message_direction'}, 'channel': {'type': 'enum', 'enum': 'channel'}, 'recipient_kind': {'type': 'enum', 'enum': 'person_kind'}, 'recipient_id': {'type': 'uuid'}, 'about_learner_id': {'type': 'ref', 'ref': 'learner'}, 'template_id': {'type': 'ref', 'ref': 'message_template'}, 'language': {'type': 'lang'}, 'body': {'type': 'text'}, 'priority': {'type': 'enum', 'enum': 'message_priority'}, 'estimated_cost_minor': {'type': 'money'}, 'actual_cost_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'provider_message_ref': {'type': 'code'}, 'delivery_status': {'type': 'enum', 'enum': 'delivery_status'}, 'delivered_at': {'type': 'ts'}, 'read_at': {'type': 'ts'}, 'failure_reason': {'type': 'str'}, 'sent_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    created_on = models.DateField(help_text='Partition key (UTC date of creation)')
    conversation_id = cf.UUID7Field(null=True, blank=True)
    campaign_id = cf.UUID7Field(null=True, blank=True)
    notification_id = cf.UUID7Field(null=True, blank=True)
    direction = models.CharField(max_length=32, choices=[('outbound', 'Outbound'), ('inbound', 'Inbound')])
    channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    recipient_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')], null=True, blank=True)
    recipient_id = cf.UUID7Field(null=True, blank=True)
    about_learner_id = cf.UUID7Field(null=True, blank=True)
    template_id = cf.UUID7Field(null=True, blank=True)
    language = models.CharField(max_length=35, null=True, blank=True)
    body = models.TextField(null=True, blank=True, help_text='Rendered content (never special-category on external channels)')
    priority = models.CharField(max_length=32, choices=[('p1', 'P1'), ('high', 'High'), ('normal', 'Normal'), ('low', 'Low')], default='normal')
    estimated_cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    actual_cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    provider_message_ref = models.CharField(max_length=128, null=True, blank=True)
    delivery_status = models.CharField(max_length=32, choices=[('queued', 'Queued'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read'), ('failed', 'Failed'), ('retrying', 'Retrying'), ('abandoned', 'Abandoned'), ('processed', 'Processed')])
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.CharField(max_length=300, null=True, blank=True)
    sent_by = cf.UUID7Field(null=True, blank=True, help_text='User or agent service identity')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)
    pk = models.CompositePrimaryKey('id', 'created_on')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'message'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Message sent or received on any channel (delivery, read, failure status; stored '


class MessageChannel(CedaModel):
    """Connected channel (WhatsApp number, Zenzap workspace, SMS sender ID, e-mail domain, push app) held by the tenant"""

    ceda_entity = 'message_channel'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'channel': {'type': 'enum', 'enum': 'channel'}, 'provider': {'type': 'code'}, 'display_name': {'type': 'title'}, 'address': {'type': 'code'}, 'credentials_vault_ref': {'type': 'str'}, 'monthly_spend_cap_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'quiet_hours': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    provider = models.CharField(max_length=40, help_text='meta_cloud_api, bsp_name, zenzap, teams, slack, smpp_aggregator …')
    display_name = models.CharField(max_length=300)
    address = models.CharField(max_length=128, help_text='E.164 number, sender id, workspace id')
    credentials_vault_ref = models.CharField(max_length=255, help_text='Token stored in the vault; never in the database')
    monthly_spend_cap_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    quiet_hours = models.JSONField(null=True, blank=True, help_text='Default 20:00–07:00 local')
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
        db_table = 'message_channel'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Connected channel (WhatsApp number, Zenzap workspace, SMS sender ID, e-mail doma'


class MessageTemplate(CedaModel):
    """Approved message template (Meta category, multilingual variants, approval status, version)"""

    ceda_entity = 'message_template'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'channel_id': {'type': 'ref', 'ref': 'message_channel'}, 'template_key': {'type': 'code'}, 'category': {'type': 'enum', 'enum': 'template_category'}, 'variants': {'type': 'json'}, 'provider_template_ref': {'type': 'code'}, 'approval_status': {'type': 'enum', 'enum': 'template_approval'}, 'version': {'type': 'int_u'}, 'is_mail_merge': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    channel = models.ForeignKey("comms.MessageChannel", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='channel_id', null=True, blank=True)
    template_key = models.CharField(max_length=64)
    category = models.CharField(max_length=32, choices=[('utility', 'Utility'), ('authentication', 'Authentication'), ('marketing', 'Marketing'), ('service', 'Service'), ('internal', 'Internal')])
    variants = models.JSONField(help_text='Language → body with merge fields')
    provider_template_ref = models.CharField(max_length=128, null=True, blank=True)
    approval_status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paused', 'Paused'), ('retired', 'Retired')])
    version = models.PositiveIntegerField()
    is_mail_merge = models.BooleanField(default=False, help_text='Word-compatible letter/label/badge template')
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
        db_table = 'message_template'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Approved message template (Meta category, multilingual variants, approval status'


class Notification(CedaModel):
    """In-app notification to a user (permission-trimmed; may fan out to external channels)"""

    ceda_entity = 'notification'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = {'type': 'range_month', 'column': 'created_on'}
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'created_on': {'type': 'date'}, 'user_id': {'type': 'uuid'}, 'rule_id': {'type': 'ref', 'ref': 'notification_rule'}, 'event_id': {'type': 'uuid'}, 'title': {'type': 'title'}, 'body': {'type': 'str'}, 'link': {'type': 'str'}, 'priority': {'type': 'enum', 'enum': 'message_priority'}, 'read_at': {'type': 'ts'}, 'acknowledged_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    created_on = models.DateField()
    user_id = cf.UUID7Field()
    rule_id = cf.UUID7Field(null=True, blank=True)
    event_id = cf.UUID7Field(null=True, blank=True, help_text='Source domain event')
    title = models.CharField(max_length=300)
    body = models.CharField(max_length=1000, null=True, blank=True, help_text='Never special-category content')
    link = models.CharField(max_length=500, null=True, blank=True)
    priority = models.CharField(max_length=32, choices=[('p1', 'P1'), ('high', 'High'), ('normal', 'Normal'), ('low', 'Low')])
    read_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)
    pk = models.CompositePrimaryKey('id', 'created_on')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'notification'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'In-app notification to a user (permission-trimmed; may fan out to external chann'


class NotificationRule(CedaModel):
    """Rule turning domain events into notifications (recipients, channel policy, digest, quiet hours, escalation)"""

    ceda_entity = 'notification_rule'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'event_type': {'type': 'code'}, 'recipient_rule': {'type': 'json'}, 'channel_policy': {'type': 'json'}, 'is_digest': {'type': 'bool'}, 'bypass_quiet_hours': {'type': 'bool'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    event_type = models.CharField(max_length=64)
    recipient_rule = models.JSONField()
    channel_policy = models.JSONField()
    is_digest = models.BooleanField(default=False)
    bypass_quiet_hours = models.BooleanField(default=False, help_text='Priority 1 and DSL safeguarding only')
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
        db_table = 'notification_rule'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Rule turning domain events into notifications (recipients, channel policy, diges'


class StaffAnnouncement(CedaModel):
    """Announcement to staff or parents with relationship-based audience (timetabled teachers, heads of year, tutors), receipts and expiry"""

    ceda_entity = 'staff_announcement'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'body': {'type': 'text'}, 'audience_rule': {'type': 'json'}, 'requires_acknowledgement': {'type': 'bool'}, 'expires_at': {'type': 'ts'}, 'published_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    body = models.TextField()
    audience_rule = models.JSONField(help_text='e.g. timetabled_teachers_of(learner)')
    requires_acknowledgement = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'staff_announcement'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Announcement to staff or parents with relationship-based audience (timetabled te'


class WorkspaceChannel(CedaModel):
    """Workspace-messaging channel provisioned from the hierarchy and staff posts (state, LGA, institution, department, year group)"""

    ceda_entity = 'workspace_channel'
    ceda_zones = ('ops',)
    ceda_domain = 'COM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-COMMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'channel_id': {'type': 'ref', 'ref': 'message_channel'}, 'external_channel_ref': {'type': 'code'}, 'audience': {'type': 'enum', 'enum': 'workspace_audience'}, 'membership_rule': {'type': 'json'}, 'last_synced_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    channel = models.ForeignKey("comms.MessageChannel", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='channel_id')
    external_channel_ref = models.CharField(max_length=128)
    audience = models.CharField(max_length=32, choices=[('state_heads', 'State heads'), ('lga_heads', 'Lga heads'), ('all_staff', 'All staff'), ('department', 'Department'), ('year_group', 'Year group'), ('committee', 'Committee')])
    membership_rule = models.JSONField(help_text='Derived from grants and posts; removed automatically on leaving')
    last_synced_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'workspace_channel'
        app_label = 'comms'
        base_manager_name = 'unscoped'
        verbose_name = 'Workspace-messaging channel provisioned from the hierarchy and staff posts (stat'
