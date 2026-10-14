"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``regulation`` — Education watchdogs, regulators and examination bodies.
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



class BodyDependency(CedaModel):
    """Dependency between two watchdogs (supervised by, recognises the results of, accredits with, funded by, member of)"""

    ceda_entity = 'body_dependency'
    ceda_zones = ('platform',)
    ceda_domain = 'REG'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'from_body_id': {'type': 'ref', 'ref': 'regulatory_body'}, 'to_body_id': {'type': 'ref', 'ref': 'regulatory_body'}, 'dependency_type': {'type': 'enum', 'enum': 'body_dependency_type'}, 'note': {'type': 'str'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    from_body = models.ForeignKey("regulation.RegulatoryBody", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='from_body_id')
    to_body = models.ForeignKey("regulation.RegulatoryBody", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='to_body_id')
    dependency_type = models.CharField(max_length=32, choices=[('supervised_by', 'Supervised by'), ('recognises_results_of', 'Recognises results of'), ('accredits_with', 'Accredits with'), ('funded_by', 'Funded by'), ('member_of', 'Member of')])
    note = models.CharField(max_length=300, null=True, blank=True)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'body_dependency'
        app_label = 'regulation'
        base_manager_name = 'unscoped'
        verbose_name = 'Dependency between two watchdogs (supervised by, recognises the results of, accr'


class InstitutionRegulation(CedaModel):
    """Link from an institution to a watchdog it depends on — relationship, what it covers, effective dates"""

    ceda_entity = 'institution_regulation'
    ceda_zones = ('registry',)
    ceda_domain = 'REG'
    ceda_kind = 'link'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'regulatory_body_id': {'type': 'uuid'}, 'body_code': {'type': 'code'}, 'relationship': {'type': 'enum', 'enum': 'regulation_relationship'}, 'covers': {'type': 'str'}, 'levels': {'type': 'json'}, 'is_mandatory': {'type': 'bool'}, 'source': {'type': 'enum', 'enum': 'regulation_source'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    regulatory_body_id = cf.UUID7Field(help_text='Soft reference to regulatory_body (platform zone)')
    body_code = models.CharField(max_length=16, help_text='Denormalised code of the body, e.g. NECO')
    relationship = models.CharField(max_length=32, choices=[('supervision', 'Supervision'), ('accreditation', 'Accreditation'), ('licensing', 'Licensing'), ('curriculum', 'Curriculum'), ('examination', 'Examination'), ('admission', 'Admission'), ('teacher_registration', 'Teacher registration'), ('professional_regulation', 'Professional regulation'), ('funding', 'Funding'), ('affiliation', 'Affiliation')])
    covers = models.CharField(max_length=200, null=True, blank=True, help_text='e.g. BECE and SSCE, UTME admissions, ND/HND programmes, teacher registration')
    levels = models.JSONField(null=True, blank=True, help_text='Education levels the link applies to')
    is_mandatory = models.BooleanField(default=True)
    source = models.CharField(max_length=32, choices=[('rule', 'Rule'), ('institution', 'Institution'), ('import', 'Import')])
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
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
        db_table = 'institution_regulation'
        app_label = 'regulation'
        base_manager_name = 'unscoped'
        verbose_name = 'Link from an institution to a watchdog it depends on — relationship, what it cov'


class RegulatoryBody(CedaModel):
    """Education watchdog — ministry, regulator, examination, admission, curriculum, teacher, funding or professional body"""

    ceda_entity = 'regulatory_body'
    ceda_zones = ('platform',)
    ceda_domain = 'REG'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'body_type': {'type': 'enum', 'enum': 'regulatory_body_type'}, 'statutory_basis': {'type': 'str'}, 'jurisdiction': {'type': 'enum', 'enum': 'regulatory_jurisdiction'}, 'levels': {'type': 'json'}, 'functions': {'type': 'text'}, 'website': {'type': 'url'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    code = models.CharField(max_length=16, help_text='Matches the regulator code list where one exists, e.g. NUC, WAEC, JAMB')
    name = models.CharField(max_length=300)
    body_type = models.CharField(max_length=32, choices=[('ministry', 'Ministry'), ('regulator_accreditor', 'Regulator accreditor'), ('examination_body', 'Examination body'), ('admissions_body', 'Admissions body'), ('curriculum_authority', 'Curriculum authority'), ('teacher_regulator', 'Teacher regulator'), ('professional_council', 'Professional council'), ('funding_agency', 'Funding agency'), ('sector_regulator', 'Sector regulator'), ('training_institute', 'Training institute')])
    statutory_basis = models.CharField(max_length=300, null=True, blank=True, help_text='Establishing law')
    jurisdiction = models.CharField(max_length=32, choices=[('federal', 'Federal'), ('regional', 'Regional'), ('state', 'State')])
    levels = models.JSONField(null=True, blank=True, help_text='Education levels the body covers (education_level codes)')
    functions = models.TextField(null=True, blank=True, help_text='What the body does for institutions')
    website = models.CharField(max_length=2048, null=True, blank=True)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
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
        db_table = 'regulatory_body'
        app_label = 'regulation'
        base_manager_name = 'unscoped'
        verbose_name = 'Education watchdog — ministry, regulator, examination, admission, curriculum, te'
