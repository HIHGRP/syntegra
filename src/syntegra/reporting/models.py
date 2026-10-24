"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``reporting`` — Reporting, semantic layer registry, government returns, scheduled reports and lineage.
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



class MetricDefinition(CedaModel):
    """Published semantic-layer metric (definition, formula, grain, source, owner, refresh, target, suppression)"""

    ceda_entity = 'metric_definition'
    ceda_zones = ('registry',)
    ceda_domain = 'RPT'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RPT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'metric_code': {'type': 'code'}, 'name': {'type': 'title'}, 'definition': {'type': 'json'}, 'target': {'type': 'dec'}, 'direction': {'type': 'enum', 'enum': 'metric_direction'}, 'label_kind': {'type': 'enum', 'enum': 'indicator_label'}, 'is_equity_indicator': {'type': 'bool'}, 'ceda_version': {'type': 'semver'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    metric_code = models.CharField(max_length=40, help_text='e.g. ATT-RATE, CUR-COVERAGE')
    name = models.CharField(max_length=300)
    definition = models.JSONField(help_text='From metrics.yaml at the published CEDA version')
    target = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    direction = models.CharField(max_length=32, choices=[('higher_is_better', 'Higher is better'), ('lower_is_better', 'Lower is better'), ('target_band', 'Target band')])
    label_kind = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('calculated', 'Calculated'), ('estimated', 'Estimated')], help_text='verified, calculated, estimated')
    is_equity_indicator = models.BooleanField(default=False, help_text='Shown only where jurisdiction policy allows')
    ceda_version = models.CharField(max_length=32)
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
        db_table = 'metric_definition'
        app_label = 'reporting'
        base_manager_name = 'unscoped'
        verbose_name = 'Published semantic-layer metric (definition, formula, grain, source, owner, refr'


class ReportDefinition(CedaModel):
    """Report in the library (standard, statutory or saved builder query) with permission trimming and suppression"""

    ceda_entity = 'report_definition'
    ceda_zones = ('registry',)
    ceda_domain = 'RPT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RPT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'report_kind': {'type': 'enum', 'enum': 'report_kind'}, 'query': {'type': 'json'}, 'min_cell_size': {'type': 'smallint'}, 'owner_user_id': {'type': 'ref', 'ref': 'app_user'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=48)
    title = models.CharField(max_length=300)
    report_kind = models.CharField(max_length=32, choices=[('standard', 'Standard'), ('statutory', 'Statutory'), ('saved_query', 'Saved query'), ('board_report', 'Board report'), ('inspection_pack', 'Inspection pack')])
    query = models.JSONField(help_text='Metrics, dimensions, filters over the semantic layer')
    min_cell_size = models.SmallIntegerField(default=10)
    owner_user = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='owner_user_id', null=True, blank=True)
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
        db_table = 'report_definition'
        app_label = 'reporting'
        base_manager_name = 'unscoped'
        verbose_name = 'Report in the library (standard, statutory or saved builder query) with permissi'


class ReportExport(CedaModel):
    """Export of a permitted table, chart or report (Excel/CSV/PDF), logged; bulk exports of confidential data audited"""

    ceda_entity = 'report_export'
    ceda_zones = ('ops',)
    ceda_domain = 'RPT'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'requested_by': {'type': 'uuid'}, 'source': {'type': 'str'}, 'format': {'type': 'enum', 'enum': 'export_format'}, 'row_count': {'type': 'int_u'}, 'object_key': {'type': 'object_key'}, 'expires_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    requested_by = cf.UUID7Field()
    source = models.CharField(max_length=200, help_text='Page region, report code or BI connector')
    format = models.CharField(max_length=32, choices=[('xlsx', 'Xlsx'), ('csv', 'Csv'), ('pdf', 'Pdf'), ('json', 'Json')])
    row_count = models.PositiveIntegerField()
    object_key = models.CharField(max_length=1024, null=True, blank=True, help_text='Expiring export object')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'report_export'
        app_label = 'reporting'
        base_manager_name = 'unscoped'
        verbose_name = 'Export of a permitted table, chart or report (Excel/CSV/PDF), logged; bulk expor'


class ReportSchedule(CedaModel):
    """Scheduled delivery of a report (recipients, formats, cadence)"""

    ceda_entity = 'report_schedule'
    ceda_zones = ('registry',)
    ceda_domain = 'RPT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RPT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'report_definition_id': {'type': 'ref', 'ref': 'report_definition'}, 'cron': {'type': 'code'}, 'recipients': {'type': 'json'}, 'format': {'type': 'enum', 'enum': 'export_format'}, 'last_run_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    report_definition = models.ForeignKey("reporting.ReportDefinition", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='report_definition_id')
    cron = models.CharField(max_length=64)
    recipients = models.JSONField()
    format = models.CharField(max_length=32, choices=[('xlsx', 'Xlsx'), ('csv', 'Csv'), ('pdf', 'Pdf'), ('json', 'Json')])
    last_run_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'report_schedule'
        app_label = 'reporting'
        base_manager_name = 'unscoped'
        verbose_name = 'Scheduled delivery of a report (recipients, formats, cadence)'


class ReturnDefinition(CedaModel):
    """Statutory return definition (UBEC census, capitation, exam-body, regulator exports) with validation rules"""

    ceda_entity = 'return_definition'
    ceda_zones = ('registry',)
    ceda_domain = 'RPT'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RPT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'recipient': {'type': 'str'}, 'spec': {'type': 'json'}, 'calendar': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    recipient = models.CharField(max_length=200)
    spec = models.JSONField(help_text='Datasets, metrics and validation')
    calendar = models.JSONField(null=True, blank=True, help_text='Due dates')
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
        db_table = 'return_definition'
        app_label = 'reporting'
        base_manager_name = 'unscoped'
        verbose_name = 'Statutory return definition (UBEC census, capitation, exam-body, regulator expor'


class ReturnSubmission(CedaModel):
    """Return generated from live data, validated, reviewed, head-certified and submitted (Accepted / Queried)"""

    ceda_entity = 'return_submission'
    ceda_zones = ('registry',)
    ceda_domain = 'RPT'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RPT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'return_definition_id': {'type': 'ref', 'ref': 'return_definition'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'period_label': {'type': 'code'}, 'generated_at': {'type': 'ts'}, 'anomalies': {'type': 'json'}, 'certified_by': {'type': 'ref', 'ref': 'app_user'}, 'certified_at': {'type': 'ts'}, 'submitted_at': {'type': 'ts'}, 'content_hash': {'type': 'hash'}, 'recipient_ref': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'return_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    return_definition = models.ForeignKey("reporting.ReturnDefinition", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='return_definition_id')
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id', null=True, blank=True)
    period_label = models.CharField(max_length=20)
    generated_at = models.DateTimeField()
    anomalies = models.JSONField(null=True, blank=True, help_text='Explained anomalies (Returns Agent draft)')
    certified_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='certified_by', null=True, blank=True)
    certified_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    content_hash = models.BinaryField(null=True, blank=True)
    recipient_ref = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('generated', 'Generated'), ('validated', 'Validated'), ('institution_review', 'Institution review'), ('certified', 'Certified'), ('submitted', 'Submitted'), ('accepted', 'Accepted'), ('queried', 'Queried')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'return_submission'
        app_label = 'reporting'
        base_manager_name = 'unscoped'
        verbose_name = 'Return generated from live data, validated, reviewed, head-certified and submitt'
