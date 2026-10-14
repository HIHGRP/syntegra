"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``platform`` — Platform, tenancy and operator commercial records.
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



class BackupRun(CedaModel):
    """Database backup or restore test (DR readiness evidence for provider staff)"""

    ceda_entity = 'backup_run'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-LOG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'residency_region_id': {'type': 'ref', 'ref': 'residency_region'}, 'store': {'type': 'code'}, 'kind': {'type': 'enum', 'enum': 'backup_kind'}, 'started_at': {'type': 'ts'}, 'finished_at': {'type': 'ts'}, 'outcome': {'type': 'enum', 'enum': 'run_outcome'}, 'size_bytes': {'type': 'bigint'}, 'rpo_seconds': {'type': 'int'}, 'rto_seconds': {'type': 'int'}, 'report_ref': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    residency_region = models.ForeignKey("platform.ResidencyRegion", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='residency_region_id')
    store = models.CharField(max_length=40, help_text='mysql-ops, mysql-registry, objectstore, opensearch …')
    kind = models.CharField(max_length=32, choices=[('full_backup', 'Full backup'), ('incremental_backup', 'Incremental backup'), ('binlog_stream', 'Binlog stream'), ('tenant_restore_test', 'Tenant restore test'), ('site_failover_test', 'Site failover test')])
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('succeeded', 'Succeeded'), ('failed', 'Failed'), ('partial', 'Partial')])
    size_bytes = models.BigIntegerField(null=True, blank=True)
    rpo_seconds = models.IntegerField(null=True, blank=True, help_text='Measured recovery point for failover tests')
    rto_seconds = models.IntegerField(null=True, blank=True, help_text='Measured recovery time for failover tests')
    report_ref = cf.UUID7Field(null=True, blank=True, help_text='Published test report document')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'backup_run'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Database backup or restore test (DR readiness evidence for provider staff)'


class ExchangePeer(CedaModel):
    """National clearance network directory — one row per state registry (36 states and the FCT)"""

    ceda_entity = 'exchange_peer'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'state_code': {'type': 'subdivision'}, 'state_name': {'type': 'title'}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'hosting': {'type': 'enum', 'enum': 'peer_hosting'}, 'endpoint_url': {'type': 'url'}, 'kid': {'type': 'code'}, 'public_jwk': {'type': 'json'}, 'agreement_ref': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'peer_status'}, 'onboarded_at': {'type': 'ts'}, 'last_seen_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    state_code = models.CharField(max_length=6, help_text='ISO 3166-2:NG, e.g. NG-LA')
    state_name = models.CharField(max_length=300)
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id', null=True, blank=True)
    hosting = models.CharField(max_length=32, choices=[('co_hosted', 'Co hosted'), ('remote', 'Remote')])
    endpoint_url = models.CharField(max_length=2048, null=True, blank=True, help_text="Remote peers: base URL of the state's exchange API")
    kid = models.CharField(max_length=64, null=True, blank=True, help_text="Key id of the state's exchange signing key")
    public_jwk = models.JSONField(null=True, blank=True, help_text='Verification key (EC P-256)')
    agreement_ref = models.CharField(max_length=64, null=True, blank=True, help_text='National clearance data-sharing agreement reference')
    status = models.CharField(max_length=32, choices=[('not_on_network', 'Not on network'), ('onboarding', 'Onboarding'), ('active', 'Active'), ('suspended', 'Suspended')])
    onboarded_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'exchange_peer'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'National clearance network directory — one row per state registry (36 states and'


class FeatureFlag(CedaModel):
    """Feature flag per tenant and phase (continuous delivery, freeze windows)"""

    ceda_entity = 'feature_flag'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'flag_key': {'type': 'code'}, 'is_enabled': {'type': 'bool'}, 'rollout_percent': {'type': 'smallint'}, 'phase': {'type': 'code'}, 'reason': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id', null=True, blank=True)
    flag_key = models.CharField(max_length=80)
    is_enabled = models.BooleanField(default=False)
    rollout_percent = models.SmallIntegerField(null=True, blank=True, help_text='Progressive rollout share')
    phase = models.CharField(max_length=8, null=True, blank=True, help_text='Delivery phase gating the feature (P0–P7)')
    reason = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'feature_flag'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Feature flag per tenant and phase (continuous delivery, freeze windows)'


class GlidBlock(CedaModel):
    """Block of Global Learner ID serials leased to a state registry (national uniqueness without per-insert coordination)"""

    ceda_entity = 'glid_block'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'first_serial': {'type': 'bigint'}, 'last_serial': {'type': 'bigint'}, 'leased_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id')
    first_serial = models.BigIntegerField()
    last_serial = models.BigIntegerField()
    leased_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'glid_block'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Block of Global Learner ID serials leased to a state registry (national uniquene'


class OperatorReceivable(CedaModel):
    """Operator receivables ledger line by channel (SDAF remittance, private subscription, other services)"""

    ceda_entity = 'operator_receivable'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'channel': {'type': 'enum', 'enum': 'receivable_channel'}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'source_kind': {'type': 'code'}, 'source_id': {'type': 'uuid'}, 'revenue_period': {'type': 'code'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'recognised_on': {'type': 'date'}, 'exported_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    channel = models.CharField(max_length=32, choices=[('sdaf_remittance', 'Sdaf remittance'), ('private_subscription', 'Private subscription'), ('other_service', 'Other service')])
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id')
    source_kind = models.CharField(max_length=40, help_text='remittance, subscription_invoice, digitisation_order …')
    source_id = cf.UUID7Field(help_text='Source record (soft; may be in the state registry)')
    revenue_period = models.CharField(max_length=7, help_text='YYYY-MM recognition period')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    recognised_on = models.DateField()
    exported_at = models.DateTimeField(null=True, blank=True, help_text='Exported to SDIN accounting through the adapter')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'operator_receivable'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Operator receivables ledger line by channel (SDAF remittance, private subscripti'


class PlatformUser(CedaModel):
    """Operator staff account (PLAT role) — no learner-data access by default; break-glass only"""

    ceda_entity = 'platform_user'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'master'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'email': {'type': 'email', 'pii': True}, 'display_name': {'type': 'name', 'pii': True}, 'idp_subject': {'type': 'str'}, 'is_break_glass_eligible': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'account_status'}, 'last_sign_in_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    email = models.CharField(max_length=254)
    display_name = models.CharField(max_length=200)
    idp_subject = models.CharField(max_length=255, help_text='Subject in Red Hat Identity Management / operator IdP (MFA enforced)')
    is_break_glass_eligible = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=[('invited', 'Invited'), ('active', 'Active'), ('locked', 'Locked'), ('suspended', 'Suspended'), ('deactivated', 'Deactivated')])
    last_sign_in_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'platform_user'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Operator staff account (PLAT role) — no learner-data access by default; break-gl'


class ResidencyRegion(CedaModel):
    """Data-residency region (in-country hosting location for a group of tenants)"""

    ceda_entity = 'residency_region'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'reference'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'country': {'type': 'country'}, 'primary_site': {'type': 'str'}, 'secondary_site': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    code = models.CharField(max_length=32, help_text='Region code, e.g. ng-lagos, ng-abuja')
    name = models.CharField(max_length=300)
    country = models.CharField(max_length=2, help_text='Country whose law governs the data (NDPA 2023 for NG)')
    primary_site = models.CharField(max_length=120, help_text='Primary data centre')
    secondary_site = models.CharField(max_length=120, null=True, blank=True, help_text='ClusterSet replica site (second in-country data centre)')
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'residency_region'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Data-residency region (in-country hosting location for a group of tenants)'


class ServiceCredit(CedaModel):
    """Service credit under the BOO service-level agreement"""

    ceda_entity = 'service_credit'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'period_start': {'type': 'date'}, 'period_end': {'type': 'date'}, 'sla_metric': {'type': 'code'}, 'target': {'type': 'dec'}, 'measured': {'type': 'dec'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'applied_to_kind': {'type': 'enum', 'enum': 'credit_target'}, 'applied_to_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id')
    period_start = models.DateField()
    period_end = models.DateField()
    sla_metric = models.CharField(max_length=40, help_text='availability_gov_tier, support_p1_response …')
    target = models.DecimalField(max_digits=9, decimal_places=4)
    measured = models.DecimalField(max_digits=9, decimal_places=4)
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    applied_to_kind = models.CharField(max_length=32, choices=[('reconciliation_statement', 'Reconciliation statement'), ('subscription_invoice', 'Subscription invoice')])
    applied_to_id = cf.UUID7Field(null=True, blank=True, help_text='Reconciliation statement (registry) or subscription invoice')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'service_credit'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Service credit under the BOO service-level agreement'


class Subscription(CedaModel):
    """A tenant's subscription to a plan (private providers pay SDIN directly; state tenants are SDAF-financed)"""

    ceda_entity = 'subscription'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'plan_id': {'type': 'ref', 'ref': 'subscription_plan'}, 'financing_channel': {'type': 'enum', 'enum': 'financing_channel'}, 'status': {'type': 'enum', 'enum': 'subscription_status'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'trial_ends_on': {'type': 'date'}, 'grace_days': {'type': 'smallint'}, 'restricted_since': {'type': 'ts'}, 'terms_version': {'type': 'semver'}, 'terms_accepted_at': {'type': 'ts'}, 'terms_accepted_by_name': {'type': 'name', 'pii': True}, 'billing_email': {'type': 'email', 'pii': True}, 'payment_method': {'type': 'enum', 'enum': 'sub_payment_method'}, 'virtual_account_ref': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id')
    plan = models.ForeignKey("platform.SubscriptionPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='plan_id')
    financing_channel = models.CharField(max_length=32, choices=[('sdaf', 'Sdaf'), ('direct_subscription', 'Direct subscription')])
    status = models.CharField(max_length=32, choices=[('trial', 'Trial'), ('active', 'Active'), ('grace', 'Grace'), ('restricted', 'Restricted'), ('suspended', 'Suspended'), ('terminated', 'Terminated')])
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    trial_ends_on = models.DateField(null=True, blank=True)
    grace_days = models.SmallIntegerField(default=30)
    restricted_since = models.DateTimeField(null=True, blank=True, help_text='Administrative features restricted (never registers, teaching, results, certificates — P9)')
    terms_version = models.CharField(max_length=32, null=True, blank=True, help_text='Subscription terms accepted')
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    terms_accepted_by_name = models.CharField(max_length=200, null=True, blank=True)
    billing_email = models.CharField(max_length=254, null=True, blank=True)
    payment_method = models.CharField(max_length=32, choices=[('gateway', 'Gateway'), ('virtual_account', 'Virtual account'), ('bank_transfer', 'Bank transfer'), ('direct_debit', 'Direct debit')], null=True, blank=True)
    virtual_account_ref = models.CharField(max_length=40, null=True, blank=True, help_text='Dedicated virtual account for transfers')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subscription'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = "A tenant's subscription to a plan (private providers pay SDIN directly; state te"


class SubscriptionCreditNote(CedaModel):
    """Credit note or refund against an operator invoice"""

    ceda_entity = 'subscription_credit_note'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'invoice_id': {'type': 'ref', 'ref': 'subscription_invoice'}, 'credit_number': {'type': 'code'}, 'reason': {'type': 'str'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'is_refund': {'type': 'bool'}, 'approved_by': {'type': 'ref', 'ref': 'platform_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    invoice = models.ForeignKey("platform.SubscriptionInvoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id')
    credit_number = models.CharField(max_length=32)
    reason = models.CharField(max_length=500)
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    is_refund = models.BooleanField(default=False)
    approved_by = models.ForeignKey("platform.PlatformUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subscription_credit_note'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Credit note or refund against an operator invoice'


class SubscriptionInvoice(CedaModel):
    """Invoice from the operator to a private provider (never edited after issue; credit notes for changes)"""

    ceda_entity = 'subscription_invoice'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'subscription_id': {'type': 'ref', 'ref': 'subscription'}, 'invoice_number': {'type': 'code'}, 'period_start': {'type': 'date'}, 'period_end': {'type': 'date'}, 'census_learners': {'type': 'int_u'}, 'net_amount_minor': {'type': 'money'}, 'discount_amount_minor': {'type': 'money'}, 'vat_amount_minor': {'type': 'money'}, 'total_amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'issued_on': {'type': 'date'}, 'due_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'invoice_status'}, 'content_hash': {'type': 'hash'}, 'e_invoice_ref': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    subscription = models.ForeignKey("platform.Subscription", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='subscription_id')
    invoice_number = models.CharField(max_length=32, help_text='SDIN-<year>-<seq>')
    period_start = models.DateField()
    period_end = models.DateField()
    census_learners = models.PositiveIntegerField(null=True, blank=True, help_text='From the census count used for SDAF (one counting rule)')
    net_amount_minor = models.BigIntegerField(help_text='(minor units)')
    discount_amount_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    vat_amount_minor = models.BigIntegerField(default=0, help_text='(minor units)')
    total_amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    issued_on = models.DateField()
    due_on = models.DateField()
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('issued', 'Issued'), ('part_paid', 'Part paid'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('credited', 'Credited'), ('void', 'Void')])
    content_hash = models.BinaryField(help_text='SHA-256 of the canonical invoice at issue')
    e_invoice_ref = models.CharField(max_length=64, null=True, blank=True, help_text='National e-invoicing reference where required (D27)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subscription_invoice'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Invoice from the operator to a private provider (never edited after issue; credi'


class SubscriptionInvoiceLine(CedaModel):
    """Line of an operator invoice (per campus for group invoices, proration, add-ons)"""

    ceda_entity = 'subscription_invoice_line'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'invoice_id': {'type': 'ref', 'ref': 'subscription_invoice'}, 'line_no': {'type': 'smallint'}, 'description': {'type': 'str'}, 'campus_ref': {'type': 'uuid'}, 'quantity': {'type': 'dec'}, 'unit_price_minor': {'type': 'money'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'is_proration': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    invoice = models.ForeignKey("platform.SubscriptionInvoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id')
    line_no = models.SmallIntegerField()
    description = models.CharField(max_length=300)
    campus_ref = cf.UUID7Field(null=True, blank=True, help_text='Registry campus id for group breakdowns (soft)')
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price_minor = models.BigIntegerField(help_text='(minor units)')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    is_proration = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subscription_invoice_line'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Line of an operator invoice (per campus for group invoices, proration, add-ons)'


class SubscriptionPayment(CedaModel):
    """Payment by a private provider directly to the operator"""

    ceda_entity = 'subscription_payment'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'invoice_id': {'type': 'ref', 'ref': 'subscription_invoice'}, 'method': {'type': 'enum', 'enum': 'sub_payment_method'}, 'gateway': {'type': 'code'}, 'gateway_ref': {'type': 'code'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'received_at': {'type': 'ts'}, 'receipt_number': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    invoice = models.ForeignKey("platform.SubscriptionInvoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id')
    method = models.CharField(max_length=32, choices=[('gateway', 'Gateway'), ('virtual_account', 'Virtual account'), ('bank_transfer', 'Bank transfer'), ('direct_debit', 'Direct debit')])
    gateway = models.CharField(max_length=32, null=True, blank=True, help_text='paystack, flutterwave, bank')
    gateway_ref = models.CharField(max_length=128, help_text='Idempotency: one row per gateway transaction')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    received_at = models.DateTimeField()
    receipt_number = models.CharField(max_length=32)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subscription_payment'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Payment by a private provider directly to the operator'


class SubscriptionPlan(CedaModel):
    """Operator plan and price-list version for private providers (and the State Enterprise plan)"""

    ceda_entity = 'subscription_plan'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'version': {'type': 'int_u'}, 'name': {'type': 'title'}, 'tier': {'type': 'enum', 'enum': 'plan_tier'}, 'price_basis': {'type': 'enum', 'enum': 'price_basis'}, 'unit_price_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'modules': {'type': 'json'}, 'limits': {'type': 'json'}, 'add_ons': {'type': 'json'}, 'vat_applicable': {'type': 'bool'}, 'effective_from': {'type': 'date'}, 'effective_to': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'approved_by': {'type': 'ref', 'ref': 'platform_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    code = models.CharField(max_length=40, help_text='Starter, Standard, Advanced, Tertiary, Group, State Enterprise')
    version = models.PositiveIntegerField()
    name = models.CharField(max_length=300)
    tier = models.CharField(max_length=32, choices=[('starter', 'Starter'), ('standard', 'Standard'), ('advanced', 'Advanced'), ('tertiary', 'Tertiary'), ('group', 'Group'), ('state_enterprise', 'State enterprise')])
    price_basis = models.CharField(max_length=32, choices=[('per_learner_term', 'Per learner term'), ('per_learner_semester', 'Per learner semester'), ('flat_term', 'Flat term'), ('per_campus_term', 'Per campus term'), ('sdaf', 'Sdaf')])
    unit_price_minor = models.BigIntegerField(help_text='Price per unit of the price basis (minor units)')
    currency = models.CharField(max_length=3, default='NGN')
    modules = models.JSONField(help_text='Module codes included (INS, LRN, LMS …)')
    limits = models.JSONField(null=True, blank=True, help_text='Learner, campus, storage and messaging limits')
    add_ons = models.JSONField(null=True, blank=True, help_text='Digitisation, messaging bundles, storage — with prices')
    vat_applicable = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    approved_by = models.ForeignKey("platform.PlatformUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subscription_plan'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Operator plan and price-list version for private providers (and the State Enterp'


class SubscriptionQuote(CedaModel):
    """Quote issued to a private provider before subscription acceptance"""

    ceda_entity = 'subscription_quote'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'provider_ref': {'type': 'uuid'}, 'plan_id': {'type': 'ref', 'ref': 'subscription_plan'}, 'learner_estimate': {'type': 'int_u'}, 'campus_count': {'type': 'smallint'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'valid_until': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'quote_status'}, 'document_ref': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id', null=True, blank=True)
    provider_ref = cf.UUID7Field(null=True, blank=True, help_text='Registry provider id (soft) before tenant creation')
    plan = models.ForeignKey("platform.SubscriptionPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='plan_id')
    learner_estimate = models.PositiveIntegerField()
    campus_count = models.SmallIntegerField(null=True, blank=True)
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    valid_until = models.DateField()
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'), ('expired', 'Expired'), ('withdrawn', 'Withdrawn')])
    document_ref = cf.UUID7Field(null=True, blank=True, help_text='Quote PDF (records zone)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'subscription_quote'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Quote issued to a private provider before subscription acceptance'


class Tenant(CedaModel):
    """Tenant — data boundary, configuration and billing unit (global, country, state, network, private provider)"""

    ceda_entity = 'tenant'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'parent_id': {'type': 'ref', 'ref': 'tenant'}, 'kind': {'type': 'enum', 'enum': 'tenant_kind'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'residency_region_id': {'type': 'ref', 'ref': 'residency_region'}, 'state_code': {'type': 'subdivision'}, 'isolation': {'type': 'enum', 'enum': 'isolation_mode'}, 'ops_schema': {'type': 'code'}, 'time_zone': {'type': 'code'}, 'default_language': {'type': 'lang'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'tenant_status'}, 'activated_at': {'type': 'ts'}, 'closed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    parent = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_id', null=True, blank=True)
    kind = models.CharField(max_length=32, choices=[('global', 'Global'), ('country', 'Country'), ('state', 'State'), ('network', 'Network'), ('private_provider', 'Private provider'), ('institution', 'Institution'), ('department', 'Department'), ('sector_registry', 'Sector registry')])
    code = models.CharField(max_length=40, help_text='Stable tenant code, e.g. ng, ng-ab, pvt-ng-ab-000123')
    name = models.CharField(max_length=300)
    residency_region = models.ForeignKey("platform.ResidencyRegion", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='residency_region_id')
    state_code = models.CharField(max_length=6, null=True, blank=True, help_text='ISO 3166-2 state for state and private-provider tenants')
    isolation = models.CharField(max_length=32, choices=[('dedicated_schema', 'Dedicated schema'), ('pooled_schema', 'Pooled schema')], help_text='Dedicated schema or pooled schema (MFS §16.3 layer 1)')
    ops_schema = models.CharField(max_length=64, help_text="MySQL schema of the tenant's ops zone")
    time_zone = models.CharField(max_length=64, default='Africa/Lagos', help_text='IANA time zone applied on display')
    default_language = models.CharField(max_length=35, default='en-NG')
    currency = models.CharField(max_length=3, default='NGN')
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('provisioning', 'Provisioning'), ('active', 'Active'), ('suspended', 'Suspended'), ('closed', 'Closed')])
    activated_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'tenant'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Tenant — data boundary, configuration and billing unit (global, country, state, '


class TenantDomain(CedaModel):
    """Hostname that resolves to a tenant at sign-in (tenant is never chosen from a list)"""

    ceda_entity = 'tenant_domain'
    ceda_zones = ('platform',)
    ceda_domain = 'PLT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-PLATFORM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'ref', 'ref': 'tenant'}, 'hostname': {'type': 'code'}, 'is_primary': {'type': 'bool'}, 'verified_at': {'type': 'ts'}, 'tls_certificate_ref': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant = models.ForeignKey("platform.Tenant", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='tenant_id')
    hostname = models.CharField(max_length=253, help_text='e.g. abia.syntegra.ng or portal.schoolname.ng')
    is_primary = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True, help_text='DNS ownership verified')
    tls_certificate_ref = models.CharField(max_length=200, null=True, blank=True, help_text='Certificate manager reference')
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'tenant_domain'
        app_label = 'platform'
        base_manager_name = 'unscoped'
        verbose_name = 'Hostname that resolves to a tenant at sign-in (tenant is never chosen from a lis'
