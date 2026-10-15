"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``iam`` — Identity, access, permissions and service identities.
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



class AccessReview(CedaModel):
    """Periodic access review decision on a grant"""

    ceda_entity = 'access_review'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'grant_id': {'type': 'ref', 'ref': 'role_grant'}, 'reviewer_id': {'type': 'ref', 'ref': 'app_user'}, 'decision': {'type': 'enum', 'enum': 'review_decision'}, 'reason': {'type': 'str'}, 'reviewed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    grant = models.ForeignKey("iam.RoleGrant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='grant_id')
    reviewer = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='reviewer_id')
    decision = models.CharField(max_length=32, choices=[('keep', 'Keep'), ('reduce', 'Reduce'), ('revoke', 'Revoke'), ('escalate', 'Escalate')])
    reason = models.CharField(max_length=500, null=True, blank=True)
    reviewed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'access_review'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Periodic access review decision on a grant'


class AppUser(CedaModel):
    """Sign-in identity (a person may also be a learner, guardian or staff member) — Administrator 360 root"""

    ceda_entity = 'app_user'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'username': {'type': 'email', 'pii': True}, 'display_name': {'type': 'name', 'pii': True}, 'phone': {'type': 'phone', 'pii': True}, 'person_kind': {'type': 'enum', 'enum': 'person_kind'}, 'person_id': {'type': 'uuid'}, 'idp': {'type': 'enum', 'enum': 'identity_provider'}, 'idp_subject': {'type': 'str'}, 'password_hash': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'account_status'}, 'locked_until': {'type': 'ts'}, 'failed_attempts': {'type': 'smallint'}, 'last_sign_in_at': {'type': 'ts'}, 'preferences': {'type': 'json'}, 'deactivated_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    username = models.CharField(max_length=254, help_text='Sign-in name (e-mail or issued username)')
    display_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=16, null=True, blank=True, help_text='E.164; used for OTP and magic links')
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')], null=True, blank=True, help_text='Linked master record type')
    person_id = cf.UUID7Field(null=True, blank=True, help_text='learner, guardian or staff id (registry)')
    idp = models.CharField(max_length=32, choices=[('local', 'Local'), ('gov_sso', 'Gov sso'), ('entra', 'Entra'), ('google', 'Google'), ('magic_link', 'Magic link'), ('otp', 'Otp')])
    idp_subject = models.CharField(max_length=255, null=True, blank=True, help_text='Subject at the federated IdP')
    password_hash = models.CharField(max_length=255, null=True, blank=True, help_text='Argon2id (local accounts only)')
    status = models.CharField(max_length=32, choices=[('invited', 'Invited'), ('active', 'Active'), ('locked', 'Locked'), ('suspended', 'Suspended'), ('deactivated', 'Deactivated')])
    locked_until = models.DateTimeField(null=True, blank=True, help_text='Lockout after 5 failures in 10 minutes')
    failed_attempts = models.SmallIntegerField(default=0)
    last_sign_in_at = models.DateTimeField(null=True, blank=True)
    preferences = models.JSONField(null=True, blank=True, help_text='Language, text size, theme, density, digest, briefing horizons')
    deactivated_at = models.DateTimeField(null=True, blank=True, help_text='Automatic from the HR leaving date')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'app_user'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Sign-in identity (a person may also be a learner, guardian or staff member) — Ad'


class BreakGlassGrant(CedaModel):
    """Time-boxed elevated emergency access (DPO and data owner notified; reviewed within 24 h)"""

    ceda_entity = 'break_glass_grant'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'reason': {'type': 'text'}, 'starts_at': {'type': 'ts'}, 'ends_at': {'type': 'ts'}, 'dpo_notified_at': {'type': 'ts'}, 'reviewed_by': {'type': 'ref', 'ref': 'app_user'}, 'reviewed_at': {'type': 'ts'}, 'review_outcome': {'type': 'enum', 'enum': 'review_decision'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id')
    scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='scope_id')
    reason = models.TextField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    dpo_notified_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='reviewed_by', null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_outcome = models.CharField(max_length=32, choices=[('keep', 'Keep'), ('reduce', 'Reduce'), ('revoke', 'Revoke'), ('escalate', 'Escalate')], null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'break_glass_grant'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Time-boxed elevated emergency access (DPO and data owner notified; reviewed with'


class CredentialReset(CedaModel):
    """Password-reset or magic-link token (hashed, single use, short expiry; generic responses)"""

    ceda_entity = 'credential_reset'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SESSION'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'purpose': {'type': 'enum', 'enum': 'reset_purpose'}, 'token_hash': {'type': 'hash'}, 'requested_ip': {'type': 'ip'}, 'expires_at': {'type': 'ts'}, 'used_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id')
    purpose = models.CharField(max_length=32, choices=[('password_reset', 'Password reset'), ('magic_link', 'Magic link'), ('mfa_recovery', 'Mfa recovery')])
    token_hash = models.BinaryField()
    requested_ip = cf.PackedIPField(null=True, blank=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'credential_reset'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Password-reset or magic-link token (hashed, single use, short expiry; generic re'


class IdentityProviderConfig(CedaModel):
    """Federated sign-in provider of a state (OpenID Connect — government IdP, Microsoft Entra ID, Google Workspace)"""

    ceda_entity = 'identity_provider_config'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'config'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'provider': {'type': 'enum', 'enum': 'identity_provider'}, 'label': {'type': 'str'}, 'issuer': {'type': 'url'}, 'client_id': {'type': 'str'}, 'client_secret_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'client_secret'}, 'scopes': {'type': 'str'}, 'allowed_domains': {'type': 'json'}, 'trust_idp_mfa': {'type': 'bool'}, 'sort_order': {'type': 'smallint'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    provider = models.CharField(max_length=32, choices=[('local', 'Local'), ('gov_sso', 'Gov sso'), ('entra', 'Entra'), ('google', 'Google'), ('magic_link', 'Magic link'), ('otp', 'Otp')])
    label = models.CharField(max_length=80, help_text='Button text, e.g. Sign in with Abia Government ID')
    issuer = models.CharField(max_length=2048, help_text='OIDC issuer; discovery document at {issuer}/.well-known/openid-configuration')
    client_id = models.CharField(max_length=255)
    client_secret_enc = models.BinaryField(null=True, blank=True, help_text='Envelope-encrypted client_secret. Confidential-client secret (envelope-encrypted)')
    scopes = models.CharField(max_length=200, help_text='Space-separated, always including openid and email')
    allowed_domains = models.JSONField(help_text='E-mail domains whose verified addresses may sign in through this provider')
    trust_idp_mfa = models.BooleanField(default=False, help_text="Accept the provider's MFA (amr/acr) as the second factor")
    sort_order = models.SmallIntegerField(null=True, blank=True)
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
        db_table = 'identity_provider_config'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Federated sign-in provider of a state (OpenID Connect — government IdP, Microsof'


class MfaFactor(CedaModel):
    """Multi-factor authentication factor (TOTP, FIDO2 passkey, SMS/e-mail OTP fallback)"""

    ceda_entity = 'mfa_factor'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'master'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'factor_type': {'type': 'enum', 'enum': 'mfa_type'}, 'label': {'type': 'str'}, 'secret_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'secret'}, 'credential_id': {'type': 'code'}, 'last_used_at': {'type': 'ts'}, 'last_step': {'type': 'bigint'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id')
    factor_type = models.CharField(max_length=32, choices=[('totp', 'Totp'), ('passkey', 'Passkey'), ('sms_otp', 'Sms otp'), ('email_otp', 'Email otp')])
    label = models.CharField(max_length=80, null=True, blank=True)
    secret_enc = models.BinaryField(null=True, blank=True, help_text='Envelope-encrypted secret. TOTP seed or WebAuthn credential (public key and id)')
    credential_id = models.CharField(max_length=255, null=True, blank=True, help_text='WebAuthn credential id')
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_step = models.BigIntegerField(null=True, blank=True, help_text='TOTP time step of the last accepted code — a code is never accepted twice (FR-AUT-03)')
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
        db_table = 'mfa_factor'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Multi-factor authentication factor (TOTP, FIDO2 passkey, SMS/e-mail OTP fallback'


class PurposeCode(CedaModel):
    """Purpose recorded when restricted fields are revealed or special-category records opened"""

    ceda_entity = 'purpose_code'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'label': {'type': 'title'}, 'requires_reason_text': {'type': 'bool'}, 'allowed_roles': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    code = models.CharField(max_length=40, help_text='registration, safeguarding, investigation, transfer_query, exam_integrity, child_missing_education …')
    label = models.CharField(max_length=300)
    requires_reason_text = models.BooleanField(default=False)
    allowed_roles = models.JSONField(null=True, blank=True, help_text='Role codes permitted to use the purpose')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'purpose_code'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Purpose recorded when restricted fields are revealed or special-category records'


class Role(CedaModel):
    """Role template (41 built-in roles plus REV, ACG, OPF; built-ins cloneable, never editable)"""

    ceda_entity = 'role'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'clearance': {'type': 'enum', 'enum': 'classification'}, 'is_builtin': {'type': 'bool'}, 'cloned_from_id': {'type': 'ref', 'ref': 'role'}, 'created_by_clearance': {'type': 'enum', 'enum': 'classification'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    code = models.CharField(max_length=16, help_text='TCH, DSL, STA, PROP, REV …')
    name = models.CharField(max_length=300)
    clearance = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')], help_text='Highest classification the role normally receives — its access level (1 public … 5 special, CR-007)')
    is_builtin = models.BooleanField(default=False)
    cloned_from = models.ForeignKey("iam.Role", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='cloned_from_id', null=True, blank=True)
    created_by_clearance = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')], null=True, blank=True, help_text="Custom role may never exceed its creator's clearance")
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
        db_table = 'role'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Role template (41 built-in roles plus REV, ACG, OPF; built-ins cloneable, never '


class RoleGrant(CedaModel):
    """Role granted to a user at a scope (role-at-scope), with clearance cap and access review date"""

    ceda_entity = 'role_grant'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'link'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'role_id': {'type': 'ref', 'ref': 'role'}, 'scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'clearance_cap': {'type': 'enum', 'enum': 'classification'}, 'granted_by': {'type': 'ref', 'ref': 'app_user'}, 'review_due_on': {'type': 'date'}, 'delegation_of_id': {'type': 'ref', 'ref': 'role_grant'}, 'supervised_until': {'type': 'date'}, 'office_scope_id': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id')
    role = models.ForeignKey("iam.Role", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='role_id')
    scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='scope_id')
    clearance_cap = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')], null=True, blank=True, help_text='Narrows the role clearance for this grant')
    granted_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='granted_by', null=True, blank=True)
    review_due_on = models.DateField(null=True, blank=True, help_text='Access review')
    delegation_of = models.ForeignKey("iam.RoleGrant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='delegation_of_id', null=True, blank=True)
    supervised_until = models.DateField(null=True, blank=True, help_text='Time-limited supervised exception approved by the head while mandatory checks are pending (FR-STF-03)')
    office_scope_id = cf.UUID7Field(null=True, blank=True, help_text="School or office the holder works in when it differs from the grant's scope — e.g. a ministry official with state-wide scope works in the Ministry of Education (soft; CR-007)")
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
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
        db_table = 'role_grant'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Role granted to a user at a scope (role-at-scope), with clearance cap and access'


class RolePermission(CedaModel):
    """Permission granted by a role (resource:action with optional ABAC condition)"""

    ceda_entity = 'role_permission'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'role_id': {'type': 'ref', 'ref': 'role'}, 'permission': {'type': 'code'}, 'abac_condition': {'type': 'json'}, 'field_scope': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    role = models.ForeignKey("iam.Role", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='role_id')
    permission = models.CharField(max_length=80, help_text='resource:action, e.g. learner:view, learner.nin:reveal, certificate:issue')
    abac_condition = models.JSONField(null=True, blank=True, help_text='own_classes, own_children, assigned_cases, assigned_inspections, own_placements')
    field_scope = models.JSONField(null=True, blank=True, help_text='Restricted/special fields this permission reveals')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'role_permission'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Permission granted by a role (resource:action with optional ABAC condition)'


class ServiceIdentity(CedaModel):
    """Non-human principal — automation agent, integration client or system job — bound to a human owner's grant"""

    ceda_entity = 'service_identity'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-IAM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'kind': {'type': 'enum', 'enum': 'service_identity_kind'}, 'name': {'type': 'title'}, 'owner_user_id': {'type': 'ref', 'ref': 'app_user'}, 'owner_grant_id': {'type': 'ref', 'ref': 'role_grant'}, 'allowed_tools': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'paused_at': {'type': 'ts'}, 'paused_by': {'type': 'ref', 'ref': 'app_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    kind = models.CharField(max_length=32, choices=[('agent', 'Agent'), ('api_client', 'Api client'), ('integration', 'Integration'), ('system_job', 'System job')])
    name = models.CharField(max_length=300)
    owner_user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='owner_user_id')
    owner_grant = models.ForeignKey("iam.RoleGrant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='owner_grant_id')
    allowed_tools = models.JSONField(null=True, blank=True, help_text='Declared typed commands (agents) or API scopes (clients)')
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    paused_at = models.DateTimeField(null=True, blank=True, help_text='Kill switch')
    paused_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='paused_by', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'service_identity'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Non-human principal — automation agent, integration client or system job — bound'


class UserPin(CedaModel):
    """Pinned page, record or saved view of a user (navigation v2)"""

    ceda_entity = 'user_pin'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SESSION'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'target_kind': {'type': 'enum', 'enum': 'pin_kind'}, 'target_ref': {'type': 'str'}, 'label': {'type': 'str'}, 'sort_order': {'type': 'smallint'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id')
    target_kind = models.CharField(max_length=32, choices=[('page', 'Page'), ('record', 'Record'), ('saved_view', 'Saved view')])
    target_ref = models.CharField(max_length=300, help_text='Page id, record reference or saved-view id')
    label = models.CharField(max_length=120, null=True, blank=True)
    sort_order = models.SmallIntegerField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'user_pin'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Pinned page, record or saved view of a user (navigation v2)'


class UserSession(CedaModel):
    """Server-side session (idle timeout 30 min for restricted/special roles, 8 h otherwise)"""

    ceda_entity = 'user_session'
    ceda_zones = ('registry',)
    ceda_domain = 'IAM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SESSION'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'ref', 'ref': 'app_user'}, 'session_hash': {'type': 'hash'}, 'active_grant_id': {'type': 'ref', 'ref': 'role_grant'}, 'device_label': {'type': 'str'}, 'is_trusted_device': {'type': 'bool'}, 'ip': {'type': 'ip'}, 'user_agent': {'type': 'str'}, 'mfa_at': {'type': 'ts'}, 'auth_method': {'type': 'code'}, 'started_at': {'type': 'ts'}, 'last_seen_at': {'type': 'ts'}, 'expires_at': {'type': 'ts'}, 'revoked_at': {'type': 'ts'}, 'ended_reason': {'type': 'enum', 'enum': 'session_end_reason'}, 'affiliation_scope_id': {'type': 'uuid'}, 'affiliation_name': {'type': 'str'}, 'affiliation_address': {'type': 'str'}, 'affiliation_confirmed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='user_id')
    session_hash = models.BinaryField(help_text='SHA-256 of the session token')
    active_grant = models.ForeignKey("iam.RoleGrant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='active_grant_id', null=True, blank=True)
    device_label = models.CharField(max_length=120, null=True, blank=True)
    is_trusted_device = models.BooleanField(default=False, help_text='Trusted for 30 days')
    ip = cf.PackedIPField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, null=True, blank=True)
    mfa_at = models.DateTimeField(null=True, blank=True)
    auth_method = models.CharField(max_length=40, null=True, blank=True, help_text='password, password+totp, password+recovery, sso:<provider>, sso:<provider>+idp_mfa')
    started_at = models.DateTimeField()
    last_seen_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    ended_reason = models.CharField(max_length=32, choices=[('signed_out', 'Signed out'), ('idle_timeout', 'Idle timeout'), ('expired', 'Expired'), ('replaced', 'Replaced'), ('ended_by_administrator', 'Ended by administrator'), ('account_inactive', 'Account inactive')], null=True, blank=True, help_text='Why the session ended (CR-007)')
    affiliation_scope_id = cf.UUID7Field(null=True, blank=True, help_text='Scope node of the school or office the user signed in for (soft; CR-007)')
    affiliation_name = models.CharField(max_length=300, null=True, blank=True, help_text='School or office name as shown at sign-in')
    affiliation_address = models.CharField(max_length=500, null=True, blank=True, help_text='School or office address as shown at sign-in')
    affiliation_confirmed_at = models.DateTimeField(null=True, blank=True, help_text='When the user confirmed the school or office after the password')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'user_session'
        app_label = 'iam'
        base_manager_name = 'unscoped'
        verbose_name = 'Server-side session (idle timeout 30 min for restricted/special roles, 8 h other'
