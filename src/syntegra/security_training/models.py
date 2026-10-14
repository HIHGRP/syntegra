"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``security_training`` — Education and training institutions of the security agencies.
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



class AgencyRank(CedaModel):
    """Rank of an agency in seniority order (officer, warrant, non-commissioned, senior and junior staff, cadet, recruit)"""

    ceda_entity = 'agency_rank'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'agency_id': {'type': 'ref', 'ref': 'security_agency'}, 'code': {'type': 'code'}, 'title': {'type': 'str'}, 'abbreviation': {'type': 'str'}, 'rank_category': {'type': 'enum', 'enum': 'rank_category'}, 'seniority': {'type': 'smallint'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    agency = models.ForeignKey("security_training.SecurityAgency", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agency_id')
    code = models.CharField(max_length=24, help_text='e.g. LT, CAPT, ASP, CPL')
    title = models.CharField(max_length=80)
    abbreviation = models.CharField(max_length=16, null=True, blank=True)
    rank_category = models.CharField(max_length=32, choices=[('commissioned_officer', 'Commissioned officer'), ('warrant_officer', 'Warrant officer'), ('non_commissioned', 'Non commissioned'), ('other_rank', 'Other rank'), ('senior_staff', 'Senior staff'), ('junior_staff', 'Junior staff'), ('cadet', 'Cadet'), ('recruit', 'Recruit')])
    seniority = models.SmallIntegerField(help_text='1 = most junior')
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
        db_table = 'agency_rank'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = 'Rank of an agency in seniority order (officer, warrant, non-commissioned, senior'


class AgencyUnit(CedaModel):
    """Unit of an agency's own structure (headquarters, service, directorate, command, formation, state command)"""

    ceda_entity = 'agency_unit'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'agency_id': {'type': 'ref', 'ref': 'security_agency'}, 'parent_unit_id': {'type': 'ref', 'ref': 'agency_unit'}, 'unit_type': {'type': 'enum', 'enum': 'agency_unit_type'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'headquarters_state': {'type': 'subdivision'}, 'headquarters_town': {'type': 'str'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    agency = models.ForeignKey("security_training.SecurityAgency", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agency_id')
    parent_unit = models.ForeignKey("security_training.AgencyUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_unit_id', null=True, blank=True)
    unit_type = models.CharField(max_length=32, choices=[('headquarters', 'Headquarters'), ('service', 'Service'), ('directorate', 'Directorate'), ('department', 'Department'), ('command', 'Command'), ('training_command', 'Training command'), ('formation', 'Formation'), ('zone', 'Zone'), ('state_command', 'State command'), ('area_command', 'Area command'), ('sector_command', 'Sector command')])
    code = models.CharField(max_length=40, help_text='Unique within the agency, e.g. TRADOC, NAVTRAC, ATC, LA-CMD')
    name = models.CharField(max_length=300)
    headquarters_state = models.CharField(max_length=6, null=True, blank=True, help_text="ISO 3166-2 state of the unit's headquarters")
    headquarters_town = models.CharField(max_length=120, null=True, blank=True)
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
        db_table = 'agency_unit'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = "Unit of an agency's own structure (headquarters, service, directorate, command, "


class SecurityAgency(CedaModel):
    """Security agency (armed service, police, paramilitary, law-enforcement, emergency or security service)"""

    ceda_entity = 'security_agency'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'category': {'type': 'enum', 'enum': 'agency_category'}, 'supervising_ministry': {'type': 'str'}, 'establishing_law': {'type': 'str'}, 'website': {'type': 'url'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=16, help_text='e.g. NA, NN, NAF, DHQ, NPF, NSCDC, NCoS, NIS, NCS, FFS, FRSC, NDLEA, DSS, EFCC')
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=32, choices=[('armed_forces', 'Armed forces'), ('police', 'Police'), ('paramilitary', 'Paramilitary'), ('law_enforcement', 'Law enforcement'), ('intelligence_security', 'Intelligence security'), ('emergency_service', 'Emergency service')])
    supervising_ministry = models.CharField(max_length=200, null=True, blank=True, help_text='Ministry or office the agency reports to')
    establishing_law = models.CharField(max_length=300, null=True, blank=True, help_text='Act establishing the agency')
    website = models.CharField(max_length=2048, null=True, blank=True)
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')], help_text='verified by the agency, illustrative, or to be confirmed')
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
        db_table = 'security_agency'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = 'Security agency (armed service, police, paramilitary, law-enforcement, emergency'


class SecurityCourse(CedaModel):
    """Course in an institution's catalogue — its curriculum (versioned; award, duration, entry, target ranks)"""

    ceda_entity = 'security_course'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'agency_id': {'type': 'ref', 'ref': 'security_agency'}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'category': {'type': 'enum', 'enum': 'training_course_category'}, 'award': {'type': 'enum', 'enum': 'training_award'}, 'award_title': {'type': 'str'}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'curriculum_id': {'type': 'ref', 'ref': 'curriculum'}, 'accrediting_body': {'type': 'cl', 'code_list': 'regulator'}, 'duration_weeks': {'type': 'smallint'}, 'entry_requirements': {'type': 'json'}, 'target_ranks': {'type': 'json'}, 'description': {'type': 'text'}, 'version': {'type': 'semver'}, 'content_held': {'type': 'bool'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    agency = models.ForeignKey("security_training.SecurityAgency", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agency_id')
    code = models.CharField(max_length=32, help_text='Unique within the institution')
    title = models.CharField(max_length=300)
    category = models.CharField(max_length=32, choices=[('initial_officer', 'Initial officer'), ('cadet_degree', 'Cadet degree'), ('recruit_basic', 'Recruit basic'), ('junior_leadership', 'Junior leadership'), ('promotion_career', 'Promotion career'), ('specialist', 'Specialist'), ('command_and_staff', 'Command and staff'), ('strategic_leadership', 'Strategic leadership'), ('academic_programme', 'Academic programme'), ('continuing_professional', 'Continuing professional')])
    award = models.CharField(max_length=32, choices=[('degree', 'Degree'), ('postgraduate', 'Postgraduate'), ('diploma', 'Diploma'), ('nce', 'Nce'), ('certificate', 'Certificate'), ('staff_qualification', 'Staff qualification'), ('attendance', 'Attendance')])
    award_title = models.CharField(max_length=120, null=True, blank=True, help_text='e.g. B.Sc., psc, fdc, Certificate of Basic Training')
    programme = models.ForeignKey("academic.Programme", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='programme_id', null=True, blank=True)
    curriculum = models.ForeignKey("curriculum.Curriculum", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='curriculum_id', null=True, blank=True)
    accrediting_body = models.CharField(max_length=32, null=True, blank=True)
    duration_weeks = models.SmallIntegerField(null=True, blank=True)
    entry_requirements = models.JSONField(null=True, blank=True, help_text='Entry qualifications, age limits, medical and other conditions (as published)')
    target_ranks = models.JSONField(null=True, blank=True, help_text='Rank codes the course is for (e.g. officer cadets, CAPT–MAJ)')
    description = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=32)
    content_held = models.BooleanField(default=True, help_text='false: the agency does not release module detail (access regime)')
    data_status = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('illustrative', 'Illustrative'), ('to_confirm', 'To confirm')])
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
        db_table = 'security_course'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = "Course in an institution's catalogue — its curriculum (versioned; award, duratio"


class SecurityCourseIntake(CedaModel):
    """Intake (run) of a course, e.g. 77 Regular Course, with dates and capacity"""

    ceda_entity = 'security_course_intake'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'course_id': {'type': 'ref', 'ref': 'security_course'}, 'intake_code': {'type': 'code'}, 'name': {'type': 'title'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'capacity': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'intake_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    course = models.ForeignKey("security_training.SecurityCourse", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_id')
    intake_code = models.CharField(max_length=40, help_text='e.g. RC77, SC-2026-1')
    name = models.CharField(max_length=300)
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('planned', 'Planned'), ('in_progress', 'In progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'security_course_intake'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = 'Intake (run) of a course, e.g. 77 Regular Course, with dates and capacity'


class SecurityCourseModule(CedaModel):
    """Module (syllabus heading) of a training course — area, contact hours, assessment"""

    ceda_entity = 'security_course_module'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'course_id': {'type': 'ref', 'ref': 'security_course'}, 'sequence': {'type': 'smallint'}, 'code': {'type': 'code'}, 'title': {'type': 'str'}, 'area': {'type': 'enum', 'enum': 'training_module_area'}, 'contact_hours': {'type': 'smallint'}, 'assessment': {'type': 'enum', 'enum': 'training_assessment'}, 'is_mandatory': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    course = models.ForeignKey("security_training.SecurityCourse", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_id')
    sequence = models.SmallIntegerField()
    code = models.CharField(max_length=32)
    title = models.CharField(max_length=200, help_text='Syllabus heading only — never operational or tactical content')
    area = models.CharField(max_length=32, choices=[('academic', 'Academic'), ('professional_core', 'Professional core'), ('leadership_ethics', 'Leadership ethics'), ('law_human_rights', 'Law human rights'), ('physical_fitness', 'Physical fitness'), ('field_practical', 'Field practical'), ('ict_cyber', 'Ict cyber'), ('health_first_aid', 'Health first aid'), ('management_administration', 'Management administration'), ('community_relations', 'Community relations'), ('research', 'Research')])
    contact_hours = models.SmallIntegerField(null=True, blank=True)
    assessment = models.CharField(max_length=32, choices=[('written', 'Written'), ('practical', 'Practical'), ('continuous', 'Continuous'), ('project', 'Project'), ('oral', 'Oral'), ('mixed', 'Mixed'), ('none', 'None')])
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'security_course_module'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = 'Module (syllabus heading) of a training course — area, contact hours, assessment'


class SecurityInstitution(CedaModel):
    """Security-agency profile of an education or training institution (agency, owning command, type, access regime)"""

    ceda_entity = 'security_institution'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-INS-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'agency_id': {'type': 'ref', 'ref': 'security_agency'}, 'unit_id': {'type': 'ref', 'ref': 'agency_unit'}, 'institution_type': {'type': 'enum', 'enum': 'security_institution_type'}, 'access_regime': {'type': 'enum', 'enum': 'security_access_regime'}, 'accreditation': {'type': 'json'}, 'commandant_title': {'type': 'str'}, 'established_year': {'type': 'smallint'}, 'data_status': {'type': 'enum', 'enum': 'reference_data_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    agency = models.ForeignKey("security_training.SecurityAgency", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='agency_id')
    unit = models.ForeignKey("security_training.AgencyUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='unit_id')
    institution_type = models.CharField(max_length=32, choices=[('military_academy', 'Military academy'), ('police_academy', 'Police academy'), ('service_academy', 'Service academy'), ('defence_university', 'Defence university'), ('staff_college', 'Staff college'), ('war_college', 'War college'), ('defence_college', 'Defence college'), ('depot', 'Depot'), ('training_school', 'Training school'), ('specialist_school', 'Specialist school'), ('training_college', 'Training college'), ('technical_institute', 'Technical institute'), ('health_sciences_school', 'Health sciences school'), ('strategic_institute', 'Strategic institute')])
    access_regime = models.CharField(max_length=32, choices=[('standard', 'Standard'), ('restricted', 'Restricted'), ('content_not_held', 'Content not held')], help_text='content_not_held: CEDA holds administration only')
    accreditation = models.JSONField(null=True, blank=True, help_text='Academic regulators and affiliations, e.g. NUC, NBTE, affiliated university')
    commandant_title = models.CharField(max_length=80, null=True, blank=True, help_text='Commandant, Rector, Vice-Chancellor, Director, Principal')
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
        db_table = 'security_institution'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = 'Security-agency profile of an education or training institution (agency, owning '


class TraineeRecord(CedaModel):
    """A trainee on an intake — rank at entry and outcome, on the lifelong learner record"""

    ceda_entity = 'trainee_record'
    ceda_zones = ('registry',)
    ceda_domain = 'STI'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'intake_id': {'type': 'ref', 'ref': 'security_course_intake'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'rank_at_entry_id': {'type': 'ref', 'ref': 'agency_rank'}, 'outcome': {'type': 'enum', 'enum': 'trainee_outcome'}, 'result': {'type': 'str'}, 'outcome_on': {'type': 'date'}, 'outcome_reason': {'type': 'text'}, 'recorded_by': {'type': 'ref', 'ref': 'app_user'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner = models.ForeignKey("learners.Learner", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='learner_id')
    intake = models.ForeignKey("security_training.SecurityCourseIntake", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='intake_id')
    enrolment = models.ForeignKey("learners.Enrolment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='enrolment_id', null=True, blank=True)
    rank_at_entry = models.ForeignKey("security_training.AgencyRank", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rank_at_entry_id', null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('in_training', 'In training'), ('passed', 'Passed'), ('passed_out', 'Passed out'), ('commissioned', 'Commissioned'), ('failed', 'Failed'), ('relegated', 'Relegated'), ('withdrawn', 'Withdrawn'), ('discharged', 'Discharged')])
    result = models.CharField(max_length=120, null=True, blank=True, help_text='Grade, class of degree or order of merit, as awarded')
    outcome_on = models.DateField(null=True, blank=True)
    outcome_reason = models.TextField(null=True, blank=True)
    recorded_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='recorded_by', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'trainee_record'
        app_label = 'security_training'
        base_manager_name = 'unscoped'
        verbose_name = 'A trainee on an intake — rank at entry and outcome, on the lifelong learner reco'
