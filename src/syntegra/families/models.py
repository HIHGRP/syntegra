"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``families`` — Family 360, guardians, contacts, contact restrictions and consent.
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



class ConsentRecord(CedaModel):
    """Consent given or refused by a guardian (or learner of age) for a learner — the consent record"""

    ceda_entity = 'consent_record'
    ceda_zones = ('ops',)
    ceda_domain = 'FAM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'consent_type': {'type': 'cl', 'code_list': 'consent_type'}, 'consent_request_id': {'type': 'ref', 'ref': 'consent_request'}, 'request_version': {'type': 'int_u'}, 'decision': {'type': 'enum', 'enum': 'consent_decision'}, 'legal_basis': {'type': 'enum', 'enum': 'legal_basis'}, 'channel': {'type': 'enum', 'enum': 'channel'}, 'comment': {'type': 'str'}, 'evidence': {'type': 'json'}, 'expires_on': {'type': 'date'}, 'withdrawn_at': {'type': 'ts'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    guardian_id = cf.UUID7Field(null=True, blank=True, help_text='NULL when the learner gives consent themselves')
    consent_type = models.CharField(max_length=32, help_text='photography, trips, data_sharing, medical, biometrics, digital_services, video_recording …')
    consent_request = models.ForeignKey("comms.ConsentRequest", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='consent_request_id', null=True, blank=True)
    request_version = models.PositiveIntegerField(null=True, blank=True, help_text='Version of the request answered')
    decision = models.CharField(max_length=32, choices=[('given', 'Given'), ('refused', 'Refused'), ('withdrawn', 'Withdrawn')])
    legal_basis = models.CharField(max_length=32, choices=[('consent', 'Consent'), ('contract', 'Contract'), ('legal_obligation', 'Legal obligation'), ('vital_interests', 'Vital interests'), ('public_task', 'Public task'), ('legitimate_interests', 'Legitimate interests')])
    channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    comment = models.CharField(max_length=1000, null=True, blank=True)
    evidence = models.JSONField(null=True, blank=True, help_text='Wording shown, device, time')
    expires_on = models.DateField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'consent_record'
        app_label = 'families'
        base_manager_name = 'unscoped'
        verbose_name = 'Consent given or refused by a guardian (or learner of age) for a learner — the c'


class ContactRestriction(CedaModel):
    """Court order or contact restriction detail (no communications, collection or portal access to the restricted child)"""

    ceda_entity = 'contact_restriction'
    ceda_zones = ('vault',)
    ceda_domain = 'FAM'
    ceda_kind = 'master'
    ceda_class = 'special'
    ceda_history = 'effective'
    ceda_scope = 'derived: the learner; DSL and named users only'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SAF'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'restriction': {'type': 'enum', 'enum': 'restriction_kind'}, 'order_reference': {'type': 'sealed', 'class': 'special'}, 'document_id': {'type': 'uuid'}, 'recorded_by': {'type': 'uuid'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    guardian_id = cf.UUID7Field()
    restriction = models.CharField(max_length=32, choices=[('no_contact', 'No contact'), ('no_collection', 'No collection'), ('no_information', 'No information'), ('supervised_only', 'Supervised only')])
    order_reference = models.BinaryField(null=True, blank=True, help_text='Court order reference and terms')
    document_id = cf.UUID7Field(null=True, blank=True, help_text='Order copy (records zone, special category)')
    recorded_by = cf.UUID7Field()
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
        db_table = 'contact_restriction'
        app_label = 'families'
        base_manager_name = 'unscoped'
        verbose_name = 'Court order or contact restriction detail (no communications, collection or port'


class Family(CedaModel):
    """Family 360 household and billing group (per operating tenant)"""

    ceda_entity = 'family'
    ceda_zones = ('ops',)
    ceda_domain = 'FAM'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the institutions of its learners'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'primary_payer_guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'billing_account_id': {'type': 'ref', 'ref': 'account'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    primary_payer_guardian_id = cf.UUID7Field(null=True, blank=True, help_text='Registry guardian (soft)')
    billing_account = models.ForeignKey("finance.Account", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='billing_account_id', null=True, blank=True)
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
        db_table = 'family'
        app_label = 'families'
        base_manager_name = 'unscoped'
        verbose_name = 'Family 360 household and billing group (per operating tenant)'


class FamilyMember(CedaModel):
    """Membership of a learner or guardian in a household"""

    ceda_entity = 'family_member'
    ceda_zones = ('ops',)
    ceda_domain = 'FAM'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = 'derived: the family'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'family_id': {'type': 'ref', 'ref': 'family'}, 'member_kind': {'type': 'enum', 'enum': 'family_member_kind'}, 'member_id': {'type': 'uuid'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    family = models.ForeignKey("families.Family", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='family_id')
    member_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian')])
    member_id = cf.UUID7Field(help_text='learner or guardian id (registry)')
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
        db_table = 'family_member'
        app_label = 'families'
        base_manager_name = 'unscoped'
        verbose_name = 'Membership of a learner or guardian in a household'


class Guardian(CedaModel):
    """Parent/Guardian 360 master"""

    ceda_entity = 'guardian'
    ceda_zones = ('registry',)
    ceda_domain = 'FAM'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: through the learners the guardian is linked to'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'given_name': {'type': 'name', 'pii': True}, 'family_name': {'type': 'name', 'pii': True}, 'title': {'type': 'str'}, 'name_phonetic': {'type': 'str'}, 'phone': {'type': 'phone', 'pii': True}, 'email': {'type': 'email', 'pii': True}, 'preferred_language': {'type': 'lang'}, 'preferred_channel': {'type': 'enum', 'enum': 'channel'}, 'address': {'type': 'json', 'pii': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'status': {'type': 'enum', 'enum': 'person_status'}, 'merged_into': {'type': 'ref', 'ref': 'guardian'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    given_name = models.CharField(max_length=200)
    family_name = models.CharField(max_length=200)
    title = models.CharField(max_length=30, null=True, blank=True)
    name_phonetic = models.CharField(max_length=120)
    phone = models.CharField(max_length=16, null=True, blank=True, help_text='E.164; inbound WhatsApp matching uses phone_hmac in channel contacts')
    email = models.CharField(max_length=254, null=True, blank=True)
    preferred_language = models.CharField(max_length=35, null=True, blank=True)
    preferred_channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')], null=True, blank=True)
    address = models.JSONField(null=True, blank=True)
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('merged', 'Merged'), ('deceased', 'Deceased')])
    merged_into = models.ForeignKey("families.Guardian", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='merged_into', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'guardian'
        app_label = 'families'
        base_manager_name = 'unscoped'
        verbose_name = 'Parent/Guardian 360 master'


class LearnerGuardian(CedaModel):
    """Relationship between a learner and a guardian (parental responsibility, priority, lives-with, restriction flag)"""

    ceda_entity = 'learner_guardian'
    ceda_zones = ('registry',)
    ceda_domain = 'FAM'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = 'derived: the learner'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'relationship': {'type': 'cl', 'code_list': 'relationship'}, 'has_parental_responsibility': {'type': 'bool'}, 'contact_priority': {'type': 'smallint'}, 'lives_with': {'type': 'bool'}, 'is_contact_restricted': {'type': 'bool'}, 'is_authorised_collector': {'type': 'bool'}, 'is_payer': {'type': 'bool'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    guardian = models.ForeignKey("families.Guardian", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='guardian_id')
    relationship = models.CharField(max_length=32)
    has_parental_responsibility = models.BooleanField()
    contact_priority = models.SmallIntegerField(null=True, blank=True)
    lives_with = models.BooleanField(null=True, blank=True)
    is_contact_restricted = models.BooleanField(default=False, help_text='Detail held in the vault (contact_restriction)')
    is_authorised_collector = models.BooleanField(default=False)
    is_payer = models.BooleanField(default=False)
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
        db_table = 'learner_guardian'
        app_label = 'families'
        base_manager_name = 'unscoped'
        verbose_name = 'Relationship between a learner and a guardian (parental responsibility, priority'


class OrganisationContact(CedaModel):
    """Organisation contact (other schools, doctors, suppliers, agencies) and additional learner contacts"""

    ceda_entity = 'organisation_contact'
    ceda_zones = ('ops',)
    ceda_domain = 'FAM'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'kind': {'type': 'enum', 'enum': 'org_contact_kind'}, 'name': {'type': 'title'}, 'contact_person': {'type': 'name', 'pii': True}, 'phone': {'type': 'phone', 'pii': True}, 'email': {'type': 'email', 'pii': True}, 'address': {'type': 'json'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'relationship': {'type': 'str'}, 'priority': {'type': 'smallint'}, 'preferred_channel': {'type': 'enum', 'enum': 'channel'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    kind = models.CharField(max_length=32, choices=[('school', 'School'), ('doctor', 'Doctor'), ('supplier', 'Supplier'), ('agency', 'Agency'), ('employer', 'Employer'), ('other', 'Other')])
    name = models.CharField(max_length=300)
    contact_person = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    address = models.JSONField(null=True, blank=True)
    learner_id = cf.UUID7Field(null=True, blank=True, help_text='When the contact is linked to one learner (with relationship and priority)')
    relationship = models.CharField(max_length=80, null=True, blank=True)
    priority = models.SmallIntegerField(null=True, blank=True)
    preferred_channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')], null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'organisation_contact'
        app_label = 'families'
        base_manager_name = 'unscoped'
        verbose_name = 'Organisation contact (other schools, doctors, suppliers, agencies) and additiona'
