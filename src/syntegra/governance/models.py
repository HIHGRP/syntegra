"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``governance`` — Governance hierarchy, configuration, reference data, policy and workflow.
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



class CodeList(CedaModel):
    """Jurisdiction code list (education levels, attendance codes, ownership, sex, concern categories …)"""

    ceda_entity = 'code_list'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'pack': {'type': 'code'}, 'is_extensible': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    code = models.CharField(max_length=48)
    title = models.CharField(max_length=300)
    pack = models.CharField(max_length=40, help_text='Jurisdiction pack that seeds the list')
    is_extensible = models.BooleanField(default=False, help_text='Lower layers may add values (never remove)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'code_list'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Jurisdiction code list (education levels, attendance codes, ownership, sex, conc'


class CodeValue(CedaModel):
    """Value of a jurisdiction code list (effective-dated; never deleted)"""

    ceda_entity = 'code_value'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'code_list_id': {'type': 'ref', 'ref': 'code_list'}, 'code': {'type': 'code'}, 'label': {'type': 'title'}, 'labels_i18n': {'type': 'json'}, 'parent_code': {'type': 'code'}, 'sort_order': {'type': 'smallint'}, 'attributes': {'type': 'json'}, 'owner_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    code_list = models.ForeignKey("governance.CodeList", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='code_list_id')
    code = models.CharField(max_length=32)
    label = models.CharField(max_length=300)
    labels_i18n = models.JSONField(null=True, blank=True, help_text='Translations keyed by BCP 47 tag')
    parent_code = models.CharField(max_length=32, null=True, blank=True, help_text='Hierarchical lists (level → stage)')
    sort_order = models.SmallIntegerField()
    attributes = models.JSONField(null=True, blank=True, help_text='e.g. age band for a level, statutory flag for an attendance code')
    owner_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='owner_scope_id', null=True, blank=True)
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
        db_table = 'code_value'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Value of a jurisdiction code list (effective-dated; never deleted)'


class ConfigVersion(CedaModel):
    """Versioned configuration document for a layer (country, state, network, institution, department)"""

    ceda_entity = 'config_version'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'layer': {'type': 'enum', 'enum': 'config_layer'}, 'section': {'type': 'code'}, 'version': {'type': 'int_u'}, 'document': {'type': 'json'}, 'locked_keys': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'effective_from': {'type': 'date'}, 'published_by': {'type': 'ref', 'ref': 'app_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    layer = models.CharField(max_length=32, choices=[('global', 'Global'), ('country', 'Country'), ('state', 'State'), ('network', 'Network'), ('institution', 'Institution'), ('department', 'Department')])
    section = models.CharField(max_length=40, help_text='e.g. levels, identifiers, calendar, branding, languages, messaging, health_index')
    version = models.PositiveIntegerField()
    document = models.JSONField(help_text="Validated against the section's JSON Schema")
    locked_keys = models.JSONField(null=True, blank=True, help_text='Keys marked mandatory_below by a higher layer (shown locked with source)')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    effective_from = models.DateField()
    published_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='published_by', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'config_version'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned configuration document for a layer (country, state, network, instituti'


class JurisdictionPack(CedaModel):
    """Versioned jurisdiction pack (statutory references, categories, timescales — e.g. Nigerian safeguarding pack)"""

    ceda_entity = 'jurisdiction_pack'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'version': {'type': 'int_u'}, 'title': {'type': 'title'}, 'country': {'type': 'country'}, 'content': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'effective_from': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    code = models.CharField(max_length=40, help_text='e.g. ng-core, ng-safeguarding, uk-kcsie, ib-dp')
    version = models.PositiveIntegerField()
    title = models.CharField(max_length=300)
    country = models.CharField(max_length=2, null=True, blank=True)
    content = models.JSONField(help_text='Statutory references, categories, timescales, forms')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    effective_from = models.DateField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'jurisdiction_pack'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned jurisdiction pack (statutory references, categories, timescales — e.g.'


class PolicyConflict(CedaModel):
    """Detected conflict between a lower-level configuration and a higher mandatory rule"""

    ceda_entity = 'policy_conflict'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_id': {'type': 'ref', 'ref': 'policy_rule'}, 'attempted_by': {'type': 'ref', 'ref': 'app_user'}, 'config_section': {'type': 'code'}, 'attempted_value': {'type': 'json'}, 'resolution': {'type': 'enum', 'enum': 'conflict_resolution'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule = models.ForeignKey("governance.PolicyRule", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rule_id')
    attempted_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='attempted_by')
    config_section = models.CharField(max_length=40, null=True, blank=True)
    attempted_value = models.JSONField()
    resolution = models.CharField(max_length=32, choices=[('cancelled', 'Cancelled'), ('exception_requested', 'Exception requested'), ('revised', 'Revised')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'policy_conflict'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Detected conflict between a lower-level configuration and a higher mandatory rul'


class PolicyException(CedaModel):
    """Approved, time-boxed exception to a rule (never modifies the rule; evaluated at run time)"""

    ceda_entity = 'policy_exception'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_id': {'type': 'ref', 'ref': 'policy_rule'}, 'subject_kind': {'type': 'code'}, 'subject_id': {'type': 'uuid'}, 'reason': {'type': 'text'}, 'evidence_document_id': {'type': 'uuid'}, 'requested_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'start_on': {'type': 'date'}, 'end_on': {'type': 'date'}, 'review_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'exception_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule = models.ForeignKey("governance.PolicyRule", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rule_id')
    subject_kind = models.CharField(max_length=40, null=True, blank=True, help_text='Record the exception applies to (teaching_assignment, institution …)')
    subject_id = cf.UUID7Field(null=True, blank=True)
    reason = models.TextField()
    evidence_document_id = cf.UUID7Field(null=True, blank=True, help_text='records zone (soft)')
    requested_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='requested_by')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
    start_on = models.DateField()
    end_on = models.DateField(help_text='≤ 12 months after start')
    review_on = models.DateField()
    status = models.CharField(max_length=32, choices=[('requested', 'Requested'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('active', 'Active'), ('expired', 'Expired'), ('renewed', 'Renewed'), ('revoked', 'Revoked')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'policy_exception'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Approved, time-boxed exception to a rule (never modifies the rule; evaluated at '


class PolicyRule(CedaModel):
    """Versioned rule at a governance level (Ministry policy engine)"""

    ceda_entity = 'policy_rule'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule_key': {'type': 'code'}, 'rule_domain': {'type': 'enum', 'enum': 'rule_domain'}, 'title': {'type': 'title'}, 'version': {'type': 'int_u'}, 'is_mandatory_below': {'type': 'bool'}, 'expression': {'type': 'longtext'}, 'parameters': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'effective_from': {'type': 'date'}, 'effective_to': {'type': 'date'}, 'authored_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule_key = models.CharField(max_length=40, help_text='e.g. ATT-INST-02, ID-NG-01, G2')
    rule_domain = models.CharField(max_length=32, choices=[('attendance', 'Attendance'), ('curriculum', 'Curriculum'), ('coverage', 'Coverage'), ('teacher_qualification', 'Teacher qualification'), ('examination', 'Examination'), ('progression', 'Progression'), ('certification', 'Certification'), ('accreditation', 'Accreditation'), ('registration', 'Registration'), ('alerting', 'Alerting'), ('billing', 'Billing'), ('behaviour', 'Behaviour'), ('safeguarding', 'Safeguarding'), ('financing', 'Financing'), ('identity', 'Identity'), ('messaging', 'Messaging'), ('agents', 'Agents')])
    title = models.CharField(max_length=300)
    version = models.PositiveIntegerField()
    is_mandatory_below = models.BooleanField(default=False, help_text='Lower levels may tighten, never relax')
    expression = models.TextField(help_text='Rule DSL source')
    parameters = models.JSONField(null=True, blank=True, help_text='Thresholds and weights')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('in_review', 'In review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('retired', 'Retired'), ('withdrawn', 'Withdrawn')])
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    authored_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='authored_by', null=True, blank=True)
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'policy_rule'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned rule at a governance level (Ministry policy engine)'


class PolicyRuleTest(CedaModel):
    """Unit test of a rule version (given context → expected outcome)"""

    ceda_entity = 'policy_rule_test'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'rule_id': {'type': 'ref', 'ref': 'policy_rule'}, 'name': {'type': 'title'}, 'given_context': {'type': 'json'}, 'expected': {'type': 'json'}, 'last_result': {'type': 'enum', 'enum': 'test_result'}, 'last_run_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    rule = models.ForeignKey("governance.PolicyRule", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rule_id')
    name = models.CharField(max_length=300)
    given_context = models.JSONField()
    expected = models.JSONField()
    last_result = models.CharField(max_length=32, choices=[('pass', 'Pass'), ('fail', 'Fail'), ('error', 'Error')], null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'policy_rule_test'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Unit test of a rule version (given context → expected outcome)'


class ScopeClosure(CedaModel):
    """Ancestor/descendant pairs of the governance hierarchy for fast subtree tests"""

    ceda_entity = 'scope_closure'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'projection'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'ancestor_id': {'type': 'ref', 'ref': 'scope_node'}, 'descendant_id': {'type': 'ref', 'ref': 'scope_node'}, 'depth': {'type': 'smallint'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    tenant_id = cf.UUID7Field()
    ancestor = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='ancestor_id')
    descendant = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='descendant_id')
    depth = models.SmallIntegerField(help_text='0 = self')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)
    pk = models.CompositePrimaryKey('tenant_id', 'ancestor_id', 'descendant_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'scope_closure'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Ancestor/descendant pairs of the governance hierarchy for fast subtree tests'


class ScopeNode(CedaModel):
    """Governance hierarchy node (country, state, LGA, network, institution, campus, unit, class/programme)"""

    ceda_entity = 'scope_node'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'parent_id': {'type': 'ref', 'ref': 'scope_node'}, 'level': {'type': 'enum', 'enum': 'scope_level'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'path': {'type': 'path'}, 'depth': {'type': 'smallint'}, 'ref_kind': {'type': 'enum', 'enum': 'scope_ref_kind'}, 'ref_id': {'type': 'uuid'}, 'ownership': {'type': 'cl', 'code_list': 'ownership'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    parent = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_id', null=True, blank=True)
    level = models.CharField(max_length=32, choices=[('global', 'Global'), ('country', 'Country'), ('state', 'State'), ('authority', 'Authority'), ('lga', 'Lga'), ('network', 'Network'), ('institution', 'Institution'), ('campus', 'Campus'), ('faculty', 'Faculty'), ('department', 'Department'), ('programme', 'Programme'), ('class', 'Class'), ('agency', 'Agency'), ('formation', 'Formation')])
    code = models.CharField(max_length=40, help_text='Official code, e.g. NG, NG-AB, AB-ABS, AB/SS/0412')
    name = models.CharField(max_length=300)
    path = models.CharField(max_length=512, help_text='Materialised path of codes, e.g. NG.AB.ABS.0412')
    depth = models.SmallIntegerField()
    ref_kind = models.CharField(max_length=32, choices=[('tenant', 'Tenant'), ('institution', 'Institution'), ('campus', 'Campus'), ('org_unit', 'Org unit'), ('class_group', 'Class group'), ('course_section', 'Course section'), ('programme', 'Programme'), ('network', 'Network'), ('security_agency', 'Security agency'), ('agency_unit', 'Agency unit')], null=True, blank=True, help_text='Entity the node represents')
    ref_id = cf.UUID7Field(null=True, blank=True, help_text='Institution, campus, org unit, class group or course section id (soft)')
    ownership = models.CharField(max_length=32, null=True, blank=True, help_text='Denormalised for oversight filters (public/private)')
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
        db_table = 'scope_node'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Governance hierarchy node (country, state, LGA, network, institution, campus, un'


class Translation(CedaModel):
    """Platform or tenant translation and terminology override (UI strings, RTL languages)"""

    ceda_entity = 'translation'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'override_scope_id': {'type': 'ref', 'ref': 'scope_node'}, 'lang': {'type': 'lang'}, 'msg_key': {'type': 'code'}, 'text': {'type': 'text'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    override_scope = models.ForeignKey("governance.ScopeNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='override_scope_id', null=True, blank=True)
    lang = models.CharField(max_length=35)
    msg_key = models.CharField(max_length=200)
    text = models.TextField()
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
        db_table = 'translation'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Platform or tenant translation and terminology override (UI strings, RTL languag'


class WorkflowDefinition(CedaModel):
    """Versioned workflow definition (state machine, human steps, SLAs, escalations)"""

    ceda_entity = 'workflow_definition'
    ceda_zones = ('registry',)
    ceda_domain = 'GOV'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'workflow_key': {'type': 'code'}, 'version': {'type': 'int_u'}, 'title': {'type': 'title'}, 'definition': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    workflow_key = models.CharField(max_length=60, help_text='admission, recruitment, safeguarding, procurement, curriculum_version, certificate_issue …')
    version = models.PositiveIntegerField()
    title = models.CharField(max_length=300)
    definition = models.JSONField(help_text='States, transitions, guards, actions, human steps, timers')
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
        db_table = 'workflow_definition'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned workflow definition (state machine, human steps, SLAs, escalations)'


class WorkflowInstance(CedaModel):
    """Running workflow on a subject record"""

    ceda_entity = 'workflow_instance'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'GOV'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'definition_id': {'type': 'ref', 'ref': 'workflow_definition'}, 'subject_kind': {'type': 'code'}, 'subject_id': {'type': 'uuid'}, 'state': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'workflow_status'}, 'started_by': {'type': 'uuid'}, 'completed_at': {'type': 'ts'}, 'context': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    definition_id = cf.UUID7Field(null=True, blank=True, help_text='Definition version the instance runs on (never changes)')
    subject_kind = models.CharField(max_length=40)
    subject_id = cf.UUID7Field()
    state = models.CharField(max_length=60)
    status = models.CharField(max_length=32, choices=[('running', 'Running'), ('waiting', 'Waiting'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('failed', 'Failed')])
    started_by = cf.UUID7Field(null=True, blank=True, help_text='Actor (user or service identity)')
    completed_at = models.DateTimeField(null=True, blank=True)
    context = models.JSONField(null=True, blank=True, help_text='Workflow variables (no special-category content)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'workflow_instance'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Running workflow on a subject record'


class WorkflowTask(CedaModel):
    """Human task in a workflow (assignee resolved from role-at-scope, SLA, escalation)"""

    ceda_entity = 'workflow_task'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'GOV'
    ceda_kind = 'queue'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'step_key': {'type': 'code'}, 'title': {'type': 'title'}, 'assignee_role': {'type': 'code'}, 'assignee_scope_id': {'type': 'uuid'}, 'assignee_user_id': {'type': 'uuid'}, 'approval_type': {'type': 'enum', 'enum': 'approval_type'}, 'due_at': {'type': 'ts'}, 'reminded_at': {'type': 'ts'}, 'escalated_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'task_status'}, 'decision': {'type': 'code'}, 'decided_by': {'type': 'uuid'}, 'decided_at': {'type': 'ts'}, 'external_task_ref': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='instance_id')
    step_key = models.CharField(max_length=60)
    title = models.CharField(max_length=300)
    assignee_role = models.CharField(max_length=16, null=True, blank=True, help_text='Role code when assigned by role-at-scope')
    assignee_scope_id = cf.UUID7Field(null=True, blank=True, help_text='Scope of the role assignment')
    assignee_user_id = cf.UUID7Field(null=True, blank=True, help_text='Resolved user')
    approval_type = models.CharField(max_length=32, choices=[('single', 'Single'), ('any_of', 'Any of'), ('all_of', 'All of'), ('sequential', 'Sequential')], null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    reminded_at = models.DateTimeField(null=True, blank=True, help_text='75% of SLA reminder')
    escalated_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('claimed', 'Claimed'), ('completed', 'Completed'), ('escalated', 'Escalated'), ('reassigned', 'Reassigned'), ('cancelled', 'Cancelled')])
    decision = models.CharField(max_length=40, null=True, blank=True)
    decided_by = cf.UUID7Field(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    external_task_ref = models.CharField(max_length=128, null=True, blank=True, help_text='Linked workspace-messaging task (Zenzap) for two-way sync')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'workflow_task'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Human task in a workflow (assignee resolved from role-at-scope, SLA, escalation)'


class WorkflowTransition(CedaModel):
    """Transition of a workflow instance (append-only; mirrored in the audit trail)"""

    ceda_entity = 'workflow_transition'
    ceda_zones = ('registry', 'ops')
    ceda_domain = 'GOV'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'instance_id': {'type': 'ref', 'ref': 'workflow_instance'}, 'from_state': {'type': 'code'}, 'to_state': {'type': 'code'}, 'actor': {'type': 'uuid'}, 'reason': {'type': 'text'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    instance = models.ForeignKey("governance.WorkflowInstance", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='instance_id')
    from_state = models.CharField(max_length=60, null=True, blank=True)
    to_state = models.CharField(max_length=60)
    actor = cf.UUID7Field(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'workflow_transition'
        app_label = 'governance'
        base_manager_name = 'unscoped'
        verbose_name = 'Transition of a workflow instance (append-only; mirrored in the audit trail)'
