"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``intelligence`` — Intelligence and automation.
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



class Agent(CedaModel):
    """Configured automation agent (owner, service identity, level, scope, limits, approval, status)"""

    ceda_entity = 'agent'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'template_code': {'type': 'code'}, 'template_version': {'type': 'int_u'}, 'service_identity_id': {'type': 'uuid'}, 'owner_user_id': {'type': 'uuid'}, 'level': {'type': 'enum', 'enum': 'autonomy_level'}, 'state_max_level': {'type': 'enum', 'enum': 'autonomy_level'}, 'triggers': {'type': 'json'}, 'limits': {'type': 'json'}, 'sandbox_result': {'type': 'json'}, 'approved_by': {'type': 'uuid'}, 'head_approved_by': {'type': 'uuid'}, 'next_reapproval_on': {'type': 'date'}, 'error_rate': {'type': 'ratio'}, 'paused_at': {'type': 'ts'}, 'paused_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'agent_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    template_code = models.CharField(max_length=40)
    template_version = models.PositiveIntegerField()
    service_identity_id = cf.UUID7Field(help_text='Registry service identity')
    owner_user_id = cf.UUID7Field()
    level = models.CharField(max_length=32, choices=[('a0', 'A0'), ('a1', 'A1'), ('a2', 'A2'), ('a3', 'A3')])
    state_max_level = models.CharField(max_length=32, choices=[('a0', 'A0'), ('a1', 'A1'), ('a2', 'A2'), ('a3', 'A3')], help_text='Institutions may only lower')
    triggers = models.JSONField()
    limits = models.JSONField(help_text='Messages, cost, records touched per day')
    sandbox_result = models.JSONField(null=True, blank=True, help_text="Simulation against last month's data")
    approved_by = cf.UUID7Field(null=True, blank=True)
    head_approved_by = cf.UUID7Field(null=True, blank=True, help_text='Required for A2 and above')
    next_reapproval_on = models.DateField(null=True, blank=True, help_text='Quarterly')
    error_rate = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    paused_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('sandbox', 'Sandbox'), ('awaiting_approval', 'Awaiting approval'), ('active', 'Active'), ('paused', 'Paused'), ('level_lowered', 'Level lowered'), ('retired', 'Retired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agent'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Configured automation agent (owner, service identity, level, scope, limits, appr'


class AgentAction(CedaModel):
    """Action taken or proposed by an agent — trigger, evidence, rule, tool call, outcome, owner ('Agent X for Owner Y'); append-only"""

    ceda_entity = 'agent_action'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INT'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = {'type': 'range_month', 'column': 'occurred_at'}
    ceda_retention = 'RS-AUDIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'agent_id': {'type': 'ref', 'ref': 'agent'}, 'owner_user_id': {'type': 'uuid'}, 'trigger_detail': {'type': 'json'}, 'evidence': {'type': 'json'}, 'rule_applied': {'type': 'str'}, 'tool': {'type': 'code'}, 'parameters': {'type': 'json'}, 'level': {'type': 'enum', 'enum': 'autonomy_level'}, 'outcome': {'type': 'enum', 'enum': 'agent_outcome'}, 'explanation': {'type': 'text'}, 'undo_until': {'type': 'ts'}, 'undone_action_id': {'type': 'uuid'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    agent_id = cf.UUID7Field()
    owner_user_id = cf.UUID7Field()
    trigger_detail = models.JSONField()
    evidence = models.JSONField()
    rule_applied = models.CharField(max_length=200, null=True, blank=True)
    tool = models.CharField(max_length=64)
    parameters = models.JSONField(help_text='Typed, validated parameters (retrieved text is never executed)')
    level = models.CharField(max_length=32, choices=[('a0', 'A0'), ('a1', 'A1'), ('a2', 'A2'), ('a3', 'A3')])
    outcome = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('executed', 'Executed'), ('held_paused', 'Held paused'), ('refused_policy', 'Refused policy'), ('failed', 'Failed'), ('undone', 'Undone')])
    explanation = models.TextField()
    undo_until = models.DateTimeField(null=True, blank=True, help_text='24-hour undo for reversible A2 actions')
    undone_action_id = cf.UUID7Field(null=True, blank=True, help_text='Undo record for a previous action')
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('id', 'occurred_at')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agent_action'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Action taken or proposed by an agent — trigger, evidence, rule, tool call, outco'


class AgentTemplate(CedaModel):
    """Agent library template (16 shipped agents) — triggers, tools, maximum autonomy, limits"""

    ceda_entity = 'agent_template'
    ceda_zones = ('platform',)
    ceda_domain = 'INT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'watches': {'type': 'text'}, 'tools': {'type': 'json'}, 'max_level': {'type': 'enum', 'enum': 'autonomy_level'}, 'human_only_actions': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    code = models.CharField(max_length=40, help_text='register_agent, coverage_agent, fee_agent …')
    name = models.CharField(max_length=300)
    watches = models.TextField()
    tools = models.JSONField(help_text='Declared typed commands')
    max_level = models.CharField(max_length=32, choices=[('a0', 'A0'), ('a1', 'A1'), ('a2', 'A2'), ('a3', 'A3')])
    human_only_actions = models.JSONField(help_text='Hard-wired consequential decisions (cannot exceed A1)')
    version = models.PositiveIntegerField()
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agent_template'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Agent library template (16 shipped agents) — triggers, tools, maximum autonomy, '


class AiModel(CedaModel):
    """Model register entry (purpose, owner, data, excluded features, oversight level) — AIX-03"""

    ceda_entity = 'ai_model'
    ceda_zones = ('platform',)
    ceda_domain = 'INT'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'purpose': {'type': 'text'}, 'owner': {'type': 'str'}, 'training_data': {'type': 'text'}, 'excluded_features': {'type': 'json'}, 'oversight_level': {'type': 'enum', 'enum': 'oversight_level'}, 'dpia_document_ref': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=300)
    purpose = models.TextField()
    owner = models.CharField(max_length=200)
    training_data = models.TextField()
    excluded_features = models.JSONField(help_text='Protected characteristics excluded from learner-risk features')
    oversight_level = models.CharField(max_length=32, choices=[('advisory', 'Advisory'), ('human_in_loop', 'Human in loop'), ('human_on_loop', 'Human on loop')])
    dpia_document_ref = models.CharField(max_length=200, null=True, blank=True)
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
        db_table = 'ai_model'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Model register entry (purpose, owner, data, excluded features, oversight level) '


class AiModelVersion(CedaModel):
    """Model version with metrics, fairness gaps, drift, approval and review date (MLflow-tracked)"""

    ceda_entity = 'ai_model_version'
    ceda_zones = ('platform',)
    ceda_domain = 'INT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'model_id': {'type': 'ref', 'ref': 'ai_model'}, 'version_label': {'type': 'semver'}, 'artifact_uri': {'type': 'str'}, 'metrics': {'type': 'json'}, 'fairness': {'type': 'json'}, 'drift': {'type': 'json'}, 'approved_by': {'type': 'ref', 'ref': 'platform_user'}, 'review_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    model = models.ForeignKey("intelligence.AiModel", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='model_id')
    version_label = models.CharField(max_length=32)
    artifact_uri = models.CharField(max_length=500)
    metrics = models.JSONField()
    fairness = models.JSONField()
    drift = models.JSONField(null=True, blank=True)
    approved_by = models.ForeignKey("platform.PlatformUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
    review_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'ai_model_version'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Model version with metrics, fairness gaps, drift, approval and review date (MLfl'


class Alert(CedaModel):
    """Alert instance (what changed, why it matters, evidence, severity, recommended action, owner, due date) — deduplicated and escalated"""

    ceda_entity = 'alert'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_key': {'type': 'code'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'priority': {'type': 'enum', 'enum': 'briefing_priority'}, 'title': {'type': 'title'}, 'what_changed': {'type': 'text'}, 'why_it_matters': {'type': 'text'}, 'evidence': {'type': 'json'}, 'recommended_action': {'type': 'text'}, 'subject_kind': {'type': 'code'}, 'subject_id': {'type': 'uuid'}, 'owner_role': {'type': 'code'}, 'owner_user_id': {'type': 'uuid'}, 'due_at': {'type': 'ts'}, 'dedupe_key': {'type': 'code'}, 'escalation_level': {'type': 'smallint'}, 'snoozed_until': {'type': 'ts'}, 'investigation_id': {'type': 'ref', 'ref': 'investigation'}, 'resolved_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'alert_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule_key = models.CharField(max_length=40)
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    priority = models.CharField(max_length=32, choices=[('p1', 'P1'), ('p2', 'P2'), ('p3', 'P3'), ('information', 'Information')])
    title = models.CharField(max_length=300)
    what_changed = models.TextField()
    why_it_matters = models.TextField()
    evidence = models.JSONField()
    recommended_action = models.TextField(null=True, blank=True)
    subject_kind = models.CharField(max_length=40)
    subject_id = cf.UUID7Field()
    owner_role = models.CharField(max_length=16)
    owner_user_id = cf.UUID7Field(null=True, blank=True)
    due_at = models.DateTimeField()
    dedupe_key = models.CharField(max_length=160, help_text='rule:subject while open')
    escalation_level = models.SmallIntegerField(default=0)
    snoozed_until = models.DateTimeField(null=True, blank=True)
    investigation = models.ForeignKey("intelligence.Investigation", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='investigation_id', null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('acknowledged', 'Acknowledged'), ('in_progress', 'In progress'), ('snoozed', 'Snoozed'), ('escalated', 'Escalated'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'alert'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Alert instance (what changed, why it matters, evidence, severity, recommended ac'


class AlertEvent(CedaModel):
    """History of an alert (raised, acknowledged, escalated, snoozed, resolved) — append-only"""

    ceda_entity = 'alert_event'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INT'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'alert_id': {'type': 'ref', 'ref': 'alert'}, 'event_kind': {'type': 'enum', 'enum': 'alert_event_kind'}, 'actor': {'type': 'uuid'}, 'note': {'type': 'str'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    alert = models.ForeignKey("intelligence.Alert", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='alert_id')
    event_kind = models.CharField(max_length=32, choices=[('raised', 'Raised'), ('acknowledged', 'Acknowledged'), ('assigned', 'Assigned'), ('escalated', 'Escalated'), ('snoozed', 'Snoozed'), ('commented', 'Commented'), ('resolved', 'Resolved'), ('reopened', 'Reopened')])
    actor = cf.UUID7Field(null=True, blank=True)
    note = models.CharField(max_length=1000, null=True, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'alert_event'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'History of an alert (raised, acknowledged, escalated, snoozed, resolved) — appen'


class AlertRule(CedaModel):
    """Alert rule (indicator, threshold, severity, owner role, due, escalation chain) — policy-engine backed"""

    ceda_entity = 'alert_rule'
    ceda_zones = ('registry',)
    ceda_domain = 'INT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_key': {'type': 'code'}, 'policy_rule_id': {'type': 'ref', 'ref': 'policy_rule'}, 'metric_id': {'type': 'code'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'owner_role': {'type': 'code'}, 'due_days': {'type': 'smallint'}, 'escalation': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule_key = models.CharField(max_length=40)
    policy_rule = models.ForeignKey("governance.PolicyRule", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='policy_rule_id', null=True, blank=True)
    metric_id = models.CharField(max_length=40, null=True, blank=True, help_text='Semantic-layer metric')
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    owner_role = models.CharField(max_length=16)
    due_days = models.SmallIntegerField()
    escalation = models.JSONField()
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
        db_table = 'alert_rule'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Alert rule (indicator, threshold, severity, owner role, due, escalation chain) —'


class AssistantConversation(CedaModel):
    """Education assistant conversation (answers executed as the user; every figure cited) — never used for training"""

    ceda_entity = 'assistant_conversation'
    ceda_zones = ('ops',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-AI-LOG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'user_id': {'type': 'uuid'}, 'title': {'type': 'str'}, 'messages': {'type': 'json'}, 'expires_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    user_id = cf.UUID7Field()
    title = models.CharField(max_length=200, null=True, blank=True)
    messages = models.JSONField(help_text='Turns with citations (records, time window, record count, DQI)')
    expires_at = models.DateTimeField(help_text='30-day retention')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'assistant_conversation'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Education assistant conversation (answers executed as the user; every figure cit'


class DocumentExtraction(CedaModel):
    """Document-intelligence extraction (forms, PDFs, certificates, transcripts, invoices) with per-field confidence and human validation"""

    ceda_entity = 'document_extraction'
    ceda_zones = ('records',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'document_id': {'type': 'ref', 'ref': 'document'}, 'schema_code': {'type': 'code'}, 'fields': {'type': 'json'}, 'findings': {'type': 'json'}, 'validated_by': {'type': 'uuid'}, 'validated_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'qa_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    document = models.ForeignKey("records.Document", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='document_id')
    schema_code = models.CharField(max_length=40)
    fields = models.JSONField(help_text='Field → value, confidence')
    findings = models.JSONField(null=True, blank=True, help_text='Missing, duplicate, contradictory, expired documents; key dates with reminders')
    validated_by = cf.UUID7Field(null=True, blank=True, help_text='Consequential fields validated by a person')
    validated_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('auto_accepted', 'Auto accepted'), ('needs_review', 'Needs review'), ('verified', 'Verified'), ('rejected', 'Rejected')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'document_extraction'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Document-intelligence extraction (forms, PDFs, certificates, transcripts, invoic'


class ImprovementPlan(CedaModel):
    """Improvement workspace (problem, evidence, contributing indicators, actions, owner, review and outcome vs target and counterfactual)"""

    ceda_entity = 'improvement_plan'
    ceda_zones = ('ops',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'uuid'}, 'problem': {'type': 'text'}, 'contributing_indicators': {'type': 'json'}, 'actions': {'type': 'json'}, 'owner_user_id': {'type': 'uuid'}, 'review_on': {'type': 'date'}, 'target': {'type': 'json'}, 'outcome': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'plan_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field(help_text='Registry institution')
    problem = models.TextField()
    contributing_indicators = models.JSONField(null=True, blank=True)
    actions = models.JSONField()
    owner_user_id = cf.UUID7Field()
    review_on = models.DateField()
    target = models.JSONField()
    outcome = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('active', 'Active'), ('under_review', 'Under review'), ('completed', 'Completed'), ('closed', 'Closed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'improvement_plan'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Improvement workspace (problem, evidence, contributing indicators, actions, owne'


class Investigation(CedaModel):
    """Follow-the-Problem investigation (Problem → Evidence → Root cause → Intervention → Responsible person → Outcome)"""

    ceda_entity = 'investigation'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'stage': {'type': 'enum', 'enum': 'investigation_stage'}, 'problem': {'type': 'text'}, 'evidence': {'type': 'json'}, 'root_cause': {'type': 'text'}, 'intervention_ref': {'type': 'uuid'}, 'responsible_user_id': {'type': 'uuid'}, 'due_on': {'type': 'date'}, 'outcome': {'type': 'text'}, 'owner_user_id': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'case_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    stage = models.CharField(max_length=32, choices=[('problem', 'Problem'), ('evidence', 'Evidence'), ('root_cause', 'Root cause'), ('intervention', 'Intervention'), ('responsible_person', 'Responsible person'), ('outcome', 'Outcome')])
    problem = models.TextField()
    evidence = models.JSONField(null=True, blank=True)
    root_cause = models.TextField(null=True, blank=True)
    intervention_ref = cf.UUID7Field(null=True, blank=True, help_text='Intervention or corrective action')
    responsible_user_id = cf.UUID7Field(null=True, blank=True, help_text='Required before advancing to outcome')
    due_on = models.DateField(null=True, blank=True)
    outcome = models.TextField(null=True, blank=True)
    owner_user_id = cf.UUID7Field()
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
        db_table = 'investigation'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Follow-the-Problem investigation (Problem → Evidence → Root cause → Intervention'


class LlmCallLog(CedaModel):
    """LLM gateway call log (prompt and output, PII-minimised; 30-day retention; residency-aware)"""

    ceda_entity = 'llm_call_log'
    ceda_zones = ('ops',)
    ceda_domain = 'INT'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = {'type': 'range_day', 'column': 'called_at'}
    ceda_retention = 'RS-AI-LOG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'caller_kind': {'type': 'enum', 'enum': 'llm_caller'}, 'caller_id': {'type': 'uuid'}, 'model': {'type': 'code'}, 'region': {'type': 'code'}, 'prompt_ref': {'type': 'object_key'}, 'output_ref': {'type': 'object_key'}, 'tokens_in': {'type': 'int_u'}, 'tokens_out': {'type': 'int_u'}, 'called_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(default=uuid7)
    tenant_id = cf.UUID7Field()
    caller_kind = models.CharField(max_length=32, choices=[('assistant', 'Assistant'), ('agent', 'Agent'), ('document_intelligence', 'Document intelligence'), ('other', 'Other')])
    caller_id = cf.UUID7Field()
    model = models.CharField(max_length=80)
    region = models.CharField(max_length=32)
    prompt_ref = models.CharField(max_length=1024, help_text='Encrypted object, deleted after 30 days')
    output_ref = models.CharField(max_length=1024, null=True, blank=True)
    tokens_in = models.PositiveIntegerField()
    tokens_out = models.PositiveIntegerField()
    called_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    pk = models.CompositePrimaryKey('id', 'called_at')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'llm_call_log'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'LLM gateway call log (prompt and output, PII-minimised; 30-day retention; reside'


class ModelDeployment(CedaModel):
    """Approval of a model version for use in a state (state DPO and ministry sign-off)"""

    ceda_entity = 'model_deployment'
    ceda_zones = ('registry',)
    ceda_domain = 'INT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'model_version_id': {'type': 'uuid'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'conditions': {'type': 'text'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    model_version_id = cf.UUID7Field(help_text='Platform model version (soft)')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by')
    conditions = models.TextField(null=True, blank=True)
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
        db_table = 'model_deployment'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Approval of a model version for use in a state (state DPO and ministry sign-off)'


class PlanningScenario(CedaModel):
    """Planning scenario (assumptions, capacity, forecast, gap, cost, comparison; university places, skills demand, ICT)"""

    ceda_entity = 'planning_scenario'
    ceda_zones = ('registry',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'assumptions': {'type': 'json'}, 'outputs': {'type': 'json'}, 'compared_with_ids': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    assumptions = models.JSONField()
    outputs = models.JSONField(null=True, blank=True, help_text='Forecasts with Monte Carlo intervals')
    compared_with_ids = models.JSONField(null=True, blank=True)
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
        db_table = 'planning_scenario'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Planning scenario (assumptions, capacity, forecast, gap, cost, comparison; unive'


class PracticeShare(CedaModel):
    """What's working — successful practice, intervention or outstanding teacher recognition (teacher consent; never a public ranking)"""

    ceda_entity = 'practice_share'
    ceda_zones = ('registry',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'evidence': {'type': 'json'}, 'subject_kind': {'type': 'code'}, 'subject_id': {'type': 'uuid'}, 'consent_given_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    evidence = models.JSONField()
    subject_kind = models.CharField(max_length=40)
    subject_id = cf.UUID7Field()
    consent_given_at = models.DateTimeField(null=True, blank=True, help_text='Teacher consent before sharing')
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
        db_table = 'practice_share'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = "What's working — successful practice, intervention or outstanding teacher recogn"


class Recommendation(CedaModel):
    """AI recommendation awaiting a human decision (finding, evidence, confidence, recommendation, decision, outcome)"""

    ceda_entity = 'recommendation'
    ceda_zones = ('ops',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'model_version_id': {'type': 'uuid'}, 'kind': {'type': 'enum', 'enum': 'recommendation_kind'}, 'subject_kind': {'type': 'code'}, 'subject_id': {'type': 'uuid'}, 'finding': {'type': 'text'}, 'evidence': {'type': 'json'}, 'confidence': {'type': 'ratio'}, 'recommendation': {'type': 'text'}, 'decision': {'type': 'enum', 'enum': 'recommendation_decision'}, 'decision_reason': {'type': 'str'}, 'decided_by': {'type': 'uuid'}, 'decided_at': {'type': 'ts'}, 'outcome': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    model_version_id = cf.UUID7Field(help_text='Platform model version (soft)')
    kind = models.CharField(max_length=32, choices=[('intervention', 'Intervention'), ('cover', 'Cover'), ('fee_match', 'Fee match'), ('resource_reallocation', 'Resource reallocation'), ('curriculum_fix', 'Curriculum fix'), ('data_fix', 'Data fix'), ('seating', 'Seating'), ('recognition', 'Recognition')])
    subject_kind = models.CharField(max_length=40)
    subject_id = cf.UUID7Field()
    finding = models.TextField()
    evidence = models.JSONField(help_text='Top factors (SHAP) and source records')
    confidence = models.DecimalField(max_digits=7, decimal_places=6)
    recommendation = models.TextField()
    decision = models.CharField(max_length=32, choices=[('accepted', 'Accepted'), ('modified', 'Modified'), ('dismissed', 'Dismissed')], null=True, blank=True)
    decision_reason = models.CharField(max_length=1000, null=True, blank=True, help_text='Required for dismissals')
    decided_by = cf.UUID7Field(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    outcome = models.JSONField(null=True, blank=True, help_text='Closed-loop outcome')
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
        db_table = 'recommendation'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'AI recommendation awaiting a human decision (finding, evidence, confidence, reco'


class ResourceProposal(CedaModel):
    """Resource-imbalance proposal for human decision (never reallocated automatically)"""

    ceda_entity = 'resource_proposal'
    ceda_zones = ('registry',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'imbalance_kind': {'type': 'enum', 'enum': 'imbalance_kind'}, 'evidence': {'type': 'json'}, 'proposal': {'type': 'text'}, 'decided_by': {'type': 'uuid'}, 'decision': {'type': 'enum', 'enum': 'recommendation_decision'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    imbalance_kind = models.CharField(max_length=32, choices=[('teachers', 'Teachers'), ('classrooms', 'Classrooms'), ('textbooks', 'Textbooks'), ('ict', 'Ict'), ('funding', 'Funding')])
    evidence = models.JSONField()
    proposal = models.TextField()
    decided_by = cf.UUID7Field(null=True, blank=True)
    decision = models.CharField(max_length=32, choices=[('accepted', 'Accepted'), ('modified', 'Modified'), ('dismissed', 'Dismissed')], null=True, blank=True)
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
        db_table = 'resource_proposal'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Resource-imbalance proposal for human decision (never reallocated automatically)'


class RiskFlag(CedaModel):
    """Learner early-warning flag (dropout, attendance, behaviour, academic decline, wellbeing, SEND support gap) with explanation"""

    ceda_entity = 'risk_flag'
    ceda_zones = ('ops',)
    ceda_domain = 'INT'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INTEL'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'flag_kind': {'type': 'enum', 'enum': 'risk_kind'}, 'probability': {'type': 'ratio'}, 'explanation': {'type': 'json'}, 'model_version_id': {'type': 'uuid'}, 'scored_on': {'type': 'date'}, 'recommendation_id': {'type': 'ref', 'ref': 'recommendation'}, 'dismissed_reason': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'flag_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    flag_kind = models.CharField(max_length=32, choices=[('dropout', 'Dropout'), ('attendance', 'Attendance'), ('behaviour', 'Behaviour'), ('academic_decline', 'Academic decline'), ('wellbeing', 'Wellbeing'), ('send_support_gap', 'Send support gap')])
    probability = models.DecimalField(max_digits=7, decimal_places=6, help_text='Calibrated')
    explanation = models.JSONField(help_text='Factors; protected characteristics excluded')
    model_version_id = cf.UUID7Field()
    scored_on = models.DateField()
    recommendation = models.ForeignKey("intelligence.Recommendation", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='recommendation_id', null=True, blank=True)
    dismissed_reason = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('new', 'New'), ('reviewed', 'Reviewed'), ('actioned', 'Actioned'), ('dismissed', 'Dismissed'), ('expired', 'Expired')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'risk_flag'
        app_label = 'intelligence'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner early-warning flag (dropout, attendance, behaviour, academic decline, we'
