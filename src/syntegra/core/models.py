"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``core`` — Audit trail, chain anchors and the transactional outbox.
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



class AuditAnchor(CedaModel):
    """Daily anchor of an audit chain written to write-once storage, and the nightly verification result"""

    ceda_entity = 'audit_anchor'
    ceda_zones = ('platform', 'registry', 'ops', 'vault', 'records')
    ceda_domain = 'AUD'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'chain_id': {'type': 'uuid'}, 'anchor_date': {'type': 'date'}, 'last_chain_seq': {'type': 'bigint'}, 'anchor_hash': {'type': 'hash'}, 'worm_object_key': {'type': 'object_key'}, 'verified_at': {'type': 'ts'}, 'verification_ok': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    chain_id = cf.UUID7Field()
    anchor_date = models.DateField()
    last_chain_seq = models.BigIntegerField()
    anchor_hash = models.BinaryField()
    worm_object_key = models.CharField(max_length=1024)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_ok = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'audit_anchor'
        app_label = 'core'
        base_manager_name = 'unscoped'
        verbose_name = 'Daily anchor of an audit chain written to write-once storage, and the nightly ve'


class AuditChainHead(CedaModel):
    """Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain"""

    ceda_entity = 'audit_chain_head'
    ceda_zones = ('platform', 'registry', 'ops', 'vault', 'records')
    ceda_domain = 'AUD'
    ceda_kind = 'projection'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'chain_id': {'type': 'uuid'}, 'lane': {'type': 'smallint'}, 'last_seq': {'type': 'bigint'}, 'last_hash': {'type': 'hash'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    chain_id = cf.UUID7Field(primary_key=True)
    lane = models.SmallIntegerField()
    last_seq = models.BigIntegerField()
    last_hash = models.BinaryField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'audit_chain_head'
        app_label = 'core'
        base_manager_name = 'unscoped'
        verbose_name = 'Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each '


class AuditEvent(CedaModel):
    """Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day)"""

    ceda_entity = 'audit_event'
    ceda_zones = ('platform', 'registry', 'ops', 'vault', 'records')
    ceda_domain = 'AUD'
    ceda_kind = 'event'
    ceda_class = 'restricted'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = {'type': 'range_day', 'column': 'occurred_at'}
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'chain_id': {'type': 'uuid'}, 'chain_seq': {'type': 'bigint'}, 'occurred_at': {'type': 'ts'}, 'event_id': {'type': 'uuid'}, 'actor_kind': {'type': 'enum', 'enum': 'actor_kind'}, 'actor_id': {'type': 'uuid'}, 'on_behalf_of_user_id': {'type': 'uuid'}, 'actor_grant_id': {'type': 'uuid'}, 'scope_node_id_at': {'type': 'uuid'}, 'action': {'type': 'code'}, 'record_kind': {'type': 'code'}, 'record_id': {'type': 'uuid'}, 'field_changes': {'type': 'json'}, 'reason': {'type': 'str'}, 'purpose_code': {'type': 'code'}, 'approval_ref': {'type': 'uuid'}, 'correlation_id': {'type': 'code'}, 'ip': {'type': 'ip'}, 'user_agent': {'type': 'str'}, 'prev_hash': {'type': 'hash'}, 'hash': {'type': 'hash'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    chain_id = cf.UUID7Field(help_text='Tenant id (or the platform chain id in the platform zone)')
    chain_seq = models.BigIntegerField(help_text='Monotonic sequence within the chain')
    occurred_at = models.DateTimeField()
    event_id = cf.UUID7Field(help_text='UUID v7 of the event')
    actor_kind = models.CharField(max_length=32, choices=[('user', 'User'), ('agent', 'Agent'), ('api_client', 'Api client'), ('system', 'System'), ('platform_operator', 'Platform operator')])
    actor_id = cf.UUID7Field(null=True, blank=True)
    on_behalf_of_user_id = cf.UUID7Field(null=True, blank=True, help_text='Agent X acting for Owner Y')
    actor_grant_id = cf.UUID7Field(null=True, blank=True, help_text='Active role-at-scope')
    scope_node_id_at = cf.UUID7Field(null=True, blank=True, help_text='Scope of the record at the time')
    action = models.CharField(max_length=80, help_text='e.g. learner.update, learner.nin.reveal, safeguarding_case.view, export.bulk')
    record_kind = models.CharField(max_length=64)
    record_id = cf.UUID7Field(null=True, blank=True)
    field_changes = models.JSONField(null=True, blank=True, help_text='[{field, from, to}] — special-category values as hashes')
    reason = models.CharField(max_length=1000, null=True, blank=True)
    purpose_code = models.CharField(max_length=40, null=True, blank=True, help_text='Required for restricted/special access')
    approval_ref = cf.UUID7Field(null=True, blank=True)
    correlation_id = models.CharField(max_length=64, null=True, blank=True)
    ip = cf.PackedIPField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, null=True, blank=True)
    prev_hash = models.BinaryField()
    hash = models.BinaryField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('chain_id', 'chain_seq', 'occurred_at')

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'audit_event'
        app_label = 'core'
        base_manager_name = 'unscoped'
        verbose_name = 'Tamper-evident audit event (append-only, hash-chained per tenant and zone, parti'


class OutboxEvent(CedaModel):
    """Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication)"""

    ceda_entity = 'outbox_event'
    ceda_zones = ('platform', 'registry', 'ops', 'vault', 'records')
    ceda_domain = 'AUD'
    ceda_kind = 'queue'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = {'type': 'range_day', 'column': 'created_on'}
    ceda_retention = 'RS-OUTBOX'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'created_on': {'type': 'date'}, 'event_type': {'type': 'code'}, 'schema_version': {'type': 'smallint'}, 'aggregate_kind': {'type': 'code'}, 'aggregate_id': {'type': 'uuid'}, 'scope_node_id_at': {'type': 'uuid'}, 'actor': {'type': 'str'}, 'correlation_id': {'type': 'code'}, 'payload': {'type': 'json'}, 'published_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    created_on = models.DateField()
    event_type = models.CharField(max_length=80, help_text='e.g. LRN.CREATED')
    schema_version = models.SmallIntegerField()
    aggregate_kind = models.CharField(max_length=64)
    aggregate_id = cf.UUID7Field()
    scope_node_id_at = cf.UUID7Field(null=True, blank=True)
    actor = models.CharField(max_length=120)
    correlation_id = models.CharField(max_length=64, null=True, blank=True)
    payload = models.JSONField()
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)
    pk = models.CompositePrimaryKey('id', 'created_on')

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'outbox_event'
        app_label = 'core'
        base_manager_name = 'unscoped'
        verbose_name = 'Transactional outbox of domain events (written with the change; published by CDC'
