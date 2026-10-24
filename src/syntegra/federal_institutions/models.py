"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``federal_institutions`` — Federal unity colleges and federal special training institutions.
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



class FederalBody(CedaModel):
    """Federal ministry, department, parastatal or commission that owns or supervises federal institutions"""

    ceda_entity = 'federal_body'
    ceda_zones = ('registry',)
    ceda_domain = 'FED'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'category': {'type': 'enum', 'enum': 'federal_body_category'}, 'parent_body_id': {'type': 'ref', 'ref': 'federal_body'}, 'website': {'type': 'url'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=16, help_text='e.g. FME, FMAFS, FMOH, FMAV, FMT')
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=32, choices=[('ministry', 'Ministry'), ('department', 'Department'), ('parastatal', 'Parastatal'), ('commission', 'Commission'), ('agency', 'Agency')])
    parent_body = models.ForeignKey("federal_institutions.FederalBody", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_body_id', null=True, blank=True)
    website = models.CharField(max_length=2048, null=True, blank=True)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
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
        db_table = 'federal_body'
        app_label = 'federal_institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Federal ministry, department, parastatal or commission that owns or supervises f'


class FederalBodyUnit(CedaModel):
    """Unit of a federal body's own structure (department, directorate, division, geopolitical zone)"""

    ceda_entity = 'federal_body_unit'
    ceda_zones = ('registry',)
    ceda_domain = 'FED'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'body_id': {'type': 'ref', 'ref': 'federal_body'}, 'parent_unit_id': {'type': 'ref', 'ref': 'federal_body_unit'}, 'unit_type': {'type': 'enum', 'enum': 'federal_unit_type'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    body = models.ForeignKey("federal_institutions.FederalBody", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='body_id')
    parent_unit = models.ForeignKey("federal_institutions.FederalBodyUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_unit_id', null=True, blank=True)
    unit_type = models.CharField(max_length=32, choices=[('department', 'Department'), ('directorate', 'Directorate'), ('division', 'Division'), ('unit', 'Unit'), ('zone', 'Zone')])
    code = models.CharField(max_length=40, help_text='Unique within the body')
    name = models.CharField(max_length=300)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
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
        db_table = 'federal_body_unit'
        app_label = 'federal_institutions'
        base_manager_name = 'unscoped'
        verbose_name = "Unit of a federal body's own structure (department, directorate, division, geopo"


class FederalInstitution(CedaModel):
    """Federal profile of a unity college or federal special training institution"""

    ceda_entity = 'federal_institution'
    ceda_zones = ('registry',)
    ceda_domain = 'FED'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'body_id': {'type': 'ref', 'ref': 'federal_body'}, 'unit_id': {'type': 'ref', 'ref': 'federal_body_unit'}, 'institution_type': {'type': 'enum', 'enum': 'federal_institution_type'}, 'geopolitical_zone': {'type': 'enum', 'enum': 'geopolitical_zone'}, 'gender_intake': {'type': 'enum', 'enum': 'gender_intake'}, 'day_boarding': {'type': 'enum', 'enum': 'day_boarding'}, 'admission_basis': {'type': 'enum', 'enum': 'admission_basis'}, 'established_year': {'type': 'smallint'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    body = models.ForeignKey("federal_institutions.FederalBody", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='body_id')
    unit = models.ForeignKey("federal_institutions.FederalBodyUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='unit_id')
    institution_type = models.CharField(max_length=32, choices=[('unity_college', 'Unity college'), ('unity_college_girls', 'Unity college girls'), ('unity_college_boys', 'Unity college boys'), ('science_technical_college', 'Science technical college'), ('special_needs_college', 'Special needs college'), ('college_of_education', 'College of education'), ('college_of_education_technical', 'College of education technical'), ('college_of_education_special', 'College of education special'), ('college_of_agriculture', 'College of agriculture'), ('college_of_forestry', 'College of forestry'), ('college_of_fisheries', 'College of fisheries'), ('college_of_animal_health', 'College of animal health'), ('college_of_land_resources', 'College of land resources'), ('college_of_veterinary_laboratory', 'College of veterinary laboratory'), ('cooperative_college', 'Cooperative college'), ('school_of_statistics', 'School of statistics'), ('school_of_surveying', 'School of surveying'), ('aviation_college', 'Aviation college'), ('maritime_academy', 'Maritime academy'), ('petroleum_training_institute', 'Petroleum training institute'), ('policy_institute', 'Policy institute'), ('teacher_training_institute', 'Teacher training institute'), ('other_special', 'Other special')])
    geopolitical_zone = models.CharField(max_length=32, choices=[('north_central', 'North central'), ('north_east', 'North east'), ('north_west', 'North west'), ('south_east', 'South east'), ('south_south', 'South south'), ('south_west', 'South west')])
    gender_intake = models.CharField(max_length=32, choices=[('mixed', 'Mixed'), ('boys', 'Boys'), ('girls', 'Girls')], null=True, blank=True)
    day_boarding = models.CharField(max_length=32, choices=[('day', 'Day'), ('boarding', 'Boarding'), ('mixed', 'Mixed')], null=True, blank=True)
    admission_basis = models.CharField(max_length=32, choices=[('national_common_entrance', 'National common entrance'), ('utme', 'Utme'), ('direct_entry', 'Direct entry'), ('merit_and_quota', 'Merit and quota'), ('agency_recruitment', 'Agency recruitment'), ('other', 'Other')], null=True, blank=True, help_text='e.g. national_common_entrance for unity colleges')
    established_year = models.SmallIntegerField(null=True, blank=True)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'federal_institution'
        app_label = 'federal_institutions'
        base_manager_name = 'unscoped'
        verbose_name = 'Federal profile of a unity college or federal special training institution'
