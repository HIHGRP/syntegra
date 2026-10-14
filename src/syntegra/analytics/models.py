"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``analytics`` — Analytics warehouse.
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



class AggAttendanceDaily(CedaModel):
    """Daily attendance aggregate by institution and class (live tiles refreshed ≤ 15 min in school hours)"""

    ceda_entity = 'agg_attendance_daily'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'aggregate'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'class_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'possible_sessions': {'type': 'int_u'}, 'present_sessions': {'type': 'int_u'}, 'late_sessions': {'type': 'int_u'}, 'authorised_absences': {'type': 'int_u'}, 'unauthorised_absences': {'type': 'int_u'}, 'registers_due': {'type': 'smallint'}, 'registers_on_time': {'type': 'smallint'}, 'registers_missing': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    class_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    possible_sessions = models.PositiveIntegerField()
    present_sessions = models.PositiveIntegerField()
    late_sessions = models.PositiveIntegerField()
    authorised_absences = models.PositiveIntegerField()
    unauthorised_absences = models.PositiveIntegerField()
    registers_due = models.SmallIntegerField()
    registers_on_time = models.SmallIntegerField()
    registers_missing = models.SmallIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'class_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agg_attendance_daily'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Daily attendance aggregate by institution and class (live tiles refreshed ≤ 15 m'


class AggEnrolmentDaily(CedaModel):
    """Daily enrolment counts by institution, level and sex"""

    ceda_entity = 'agg_enrolment_daily'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'aggregate'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'sex': {'type': 'cl', 'code_list': 'sex'}, 'enrolled': {'type': 'int_u'}, 'new_entrants': {'type': 'int_u'}, 'leavers': {'type': 'int_u'}, 'dropouts': {'type': 'int_u'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField()
    education_level = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    enrolled = models.PositiveIntegerField()
    new_entrants = models.PositiveIntegerField()
    leavers = models.PositiveIntegerField()
    dropouts = models.PositiveIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'institution_key', 'education_level', 'sex')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agg_enrolment_daily'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Daily enrolment counts by institution, level and sex'


class AggLearnerAttendanceTerm(CedaModel):
    """Learner attendance rate per term (persistent < 90% and severe < 50% absence)"""

    ceda_entity = 'agg_learner_attendance_term'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'aggregate'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'period_key': {'type': 'bigint'}, 'learner_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'possible_sessions': {'type': 'int_u'}, 'present_sessions': {'type': 'int_u'}, 'attendance_rate': {'type': 'pct'}, 'is_persistent_absence': {'type': 'bool'}, 'is_severe_absence': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    period_key = models.BigIntegerField()
    learner_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    possible_sessions = models.PositiveIntegerField()
    present_sessions = models.PositiveIntegerField()
    attendance_rate = models.DecimalField(max_digits=6, decimal_places=3)
    is_persistent_absence = models.BooleanField()
    is_severe_absence = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'period_key', 'learner_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agg_learner_attendance_term'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner attendance rate per term (persistent < 90% and severe < 50% absence)'


class AggMetric(CedaModel):
    """Generic metric aggregate served by the semantic layer (value, numerator, denominator, suppression) per scope and period"""

    ceda_entity = 'agg_metric'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'aggregate'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'metric_code': {'type': 'code'}, 'scope_key': {'type': 'bigint'}, 'grain': {'type': 'code'}, 'period_label': {'type': 'code'}, 'dims_hash': {'type': 'hash'}, 'dims': {'type': 'json'}, 'value': {'type': 'dec'}, 'numerator': {'type': 'dec'}, 'denominator': {'type': 'dec'}, 'is_suppressed': {'type': 'bool'}, 'label_kind': {'type': 'enum', 'enum': 'indicator_label'}, 'computed_at': {'type': 'ts'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    metric_code = models.CharField(max_length=40)
    scope_key = models.BigIntegerField()
    grain = models.CharField(max_length=16, help_text='day, week, term, session, year')
    period_label = models.CharField(max_length=20)
    dims_hash = models.BinaryField(help_text='Hash of the dimension filter (sex, level, ownership …)')
    dims = models.JSONField()
    value = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    numerator = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    denominator = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    is_suppressed = models.BooleanField(help_text='Cells < 10 outside the institution scope')
    label_kind = models.CharField(max_length=32, choices=[('verified', 'Verified'), ('calculated', 'Calculated'), ('estimated', 'Estimated')])
    computed_at = models.DateTimeField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'metric_code', 'scope_key', 'grain', 'period_label', 'dims_hash')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agg_metric'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Generic metric aggregate served by the semantic layer (value, numerator, denomin'


class AggWellbeingSafeguardingCount(CedaModel):
    """Governed daily counts of safeguarding concerns, SEND provision and wellbeing concerns (counts only; produced inside the vault)"""

    ceda_entity = 'agg_wellbeing_safeguarding_count'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'aggregate'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'measure': {'type': 'code'}, 'category': {'type': 'code'}, 'count_value': {'type': 'int_u'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField()
    measure = models.CharField(max_length=40, help_text='safeguarding_concerns, send_register, send_provision_covered, wellbeing_concerns')
    category = models.CharField(max_length=40, help_text="Concern category or '*'")
    count_value = models.PositiveIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'institution_key', 'measure', 'category')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'agg_wellbeing_safeguarding_count'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Governed daily counts of safeguarding concerns, SEND provision and wellbeing con'


class DimClass(CedaModel):
    """Class (arm/set/section) dimension per session"""

    ceda_entity = 'dim_class'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'class_key': {'type': 'bigint'}, 'class_group_id': {'type': 'uuid'}, 'institution_key': {'type': 'bigint'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'stream': {'type': 'cl', 'code_list': 'stream'}, 'session_label': {'type': 'code'}, 'name': {'type': 'title'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    class_key = models.BigIntegerField()
    class_group_id = cf.UUID7Field()
    institution_key = models.BigIntegerField()
    education_level = models.CharField(max_length=32)
    stream = models.CharField(max_length=32, null=True, blank=True)
    session_label = models.CharField(max_length=20)
    name = models.CharField(max_length=300)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'class_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_class'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Class (arm/set/section) dimension per session'


class DimCurriculumNode(CedaModel):
    """Curriculum objective dimension (version-aware)"""

    ceda_entity = 'dim_curriculum_node'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'public'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'node_key': {'type': 'bigint'}, 'node_id': {'type': 'uuid'}, 'curriculum_code': {'type': 'code'}, 'version_label': {'type': 'semver'}, 'node_code': {'type': 'code'}, 'kind': {'type': 'enum', 'enum': 'curriculum_node_kind'}, 'requirement': {'type': 'enum', 'enum': 'requirement_status'}, 'subject_key': {'type': 'bigint'}, 'min_hours': {'type': 'dec'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    node_key = models.BigIntegerField()
    node_id = cf.UUID7Field()
    curriculum_code = models.CharField(max_length=48)
    version_label = models.CharField(max_length=32)
    node_code = models.CharField(max_length=48)
    kind = models.CharField(max_length=32, choices=[('subject', 'Subject'), ('strand', 'Strand'), ('theme', 'Theme'), ('topic', 'Topic'), ('objective', 'Objective'), ('competency', 'Competency')])
    requirement = models.CharField(max_length=32, choices=[('mandatory', 'Mandatory'), ('optional', 'Optional'), ('recommended', 'Recommended'), ('restricted', 'Restricted')])
    subject_key = models.BigIntegerField(null=True, blank=True)
    min_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'node_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_curriculum_node'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Curriculum objective dimension (version-aware)'


class DimDate(CedaModel):
    """Calendar date dimension"""

    ceda_entity = 'dim_date'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'public'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'calendar_date': {'type': 'date'}, 'day_of_week': {'type': 'smallint'}, 'iso_week': {'type': 'smallint'}, 'month_no': {'type': 'smallint'}, 'year_no': {'type': 'smallint'}, 'is_weekend': {'type': 'bool'}, 'state_session_label': {'type': 'code'}, 'state_term_label': {'type': 'code'}, 'is_state_school_day': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField(help_text='YYYYMMDD')
    calendar_date = models.DateField()
    day_of_week = models.SmallIntegerField()
    iso_week = models.SmallIntegerField()
    month_no = models.SmallIntegerField()
    year_no = models.SmallIntegerField()
    is_weekend = models.BooleanField()
    state_session_label = models.CharField(max_length=20, null=True, blank=True)
    state_term_label = models.CharField(max_length=20, null=True, blank=True)
    is_state_school_day = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_date'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Calendar date dimension'


class DimInstitution(CedaModel):
    """Institution dimension (SCD2) with comparison context (P7)"""

    ceda_entity = 'dim_institution'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'institution_key': {'type': 'bigint'}, 'institution_id': {'type': 'uuid'}, 'scope_key': {'type': 'bigint'}, 'lga_scope_key': {'type': 'bigint'}, 'institution_code': {'type': 'code'}, 'name': {'type': 'title'}, 'category': {'type': 'cl', 'code_list': 'institution_category'}, 'ownership': {'type': 'cl', 'code_list': 'ownership'}, 'is_public': {'type': 'bool'}, 'location_class': {'type': 'enum', 'enum': 'location_class'}, 'comparison_group': {'type': 'code'}, 'onboarding_status': {'type': 'enum', 'enum': 'onboarding_status'}, 'row_valid_from': {'type': 'date'}, 'row_valid_to': {'type': 'date'}, 'is_current': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    institution_key = models.BigIntegerField()
    institution_id = cf.UUID7Field()
    scope_key = models.BigIntegerField()
    lga_scope_key = models.BigIntegerField()
    institution_code = models.CharField(max_length=20)
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=32)
    ownership = models.CharField(max_length=32)
    is_public = models.BooleanField()
    location_class = models.CharField(max_length=32, choices=[('urban', 'Urban'), ('peri_urban', 'Peri urban'), ('rural', 'Rural')], null=True, blank=True)
    comparison_group = models.CharField(max_length=60, null=True, blank=True)
    onboarding_status = models.CharField(max_length=32, choices=[('not_onboarded', 'Not onboarded'), ('onboarding', 'Onboarding'), ('live', 'Live'), ('suspended', 'Suspended'), ('closed', 'Closed')])
    row_valid_from = models.DateField()
    row_valid_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'institution_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_institution'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Institution dimension (SCD2) with comparison context (P7)'


class DimLearner(CedaModel):
    """Pseudonymised learner dimension (SCD2) — no names, no identifiers"""

    ceda_entity = 'dim_learner'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_key': {'type': 'bigint'}, 'learner_pseudo': {'type': 'hmac'}, 'birth_year': {'type': 'smallint'}, 'sex': {'type': 'cl', 'code_list': 'sex'}, 'is_historic': {'type': 'bool'}, 'row_valid_from': {'type': 'date'}, 'row_valid_to': {'type': 'date'}, 'is_current': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    learner_key = models.BigIntegerField()
    learner_pseudo = models.BinaryField(help_text='Keyed HMAC of learner_id (key held outside the warehouse)')
    birth_year = models.SmallIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=32, null=True, blank=True)
    is_historic = models.BooleanField()
    row_valid_from = models.DateField()
    row_valid_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'learner_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_learner'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Pseudonymised learner dimension (SCD2) — no names, no identifiers'


class DimPeriod(CedaModel):
    """Academic and billing period dimension (session, term, semester, billing period)"""

    ceda_entity = 'dim_period'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'public'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'period_key': {'type': 'bigint'}, 'period_id': {'type': 'uuid'}, 'kind': {'type': 'enum', 'enum': 'period_kind'}, 'label': {'type': 'code'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    period_key = models.BigIntegerField()
    period_id = cf.UUID7Field()
    kind = models.CharField(max_length=32, choices=[('session', 'Session'), ('term', 'Term'), ('semester', 'Semester'), ('half_term', 'Half term'), ('billing_period', 'Billing period')])
    label = models.CharField(max_length=40)
    starts_on = models.DateField()
    ends_on = models.DateField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'period_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_period'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Academic and billing period dimension (session, term, semester, billing period)'


class DimScope(CedaModel):
    """Governance scope dimension (SCD2) — country, state, LGA, network, institution, campus, unit, class"""

    ceda_entity = 'dim_scope'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_key': {'type': 'bigint'}, 'scope_node_id': {'type': 'uuid'}, 'level': {'type': 'enum', 'enum': 'scope_level'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'path': {'type': 'path'}, 'state_code': {'type': 'subdivision'}, 'lga_code': {'type': 'code'}, 'ownership': {'type': 'cl', 'code_list': 'ownership'}, 'row_valid_from': {'type': 'date'}, 'row_valid_to': {'type': 'date'}, 'is_current': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    scope_key = models.BigIntegerField()
    scope_node_id = cf.UUID7Field()
    level = models.CharField(max_length=32, choices=[('global', 'Global'), ('country', 'Country'), ('state', 'State'), ('authority', 'Authority'), ('lga', 'Lga'), ('network', 'Network'), ('institution', 'Institution'), ('campus', 'Campus'), ('faculty', 'Faculty'), ('department', 'Department'), ('programme', 'Programme'), ('class', 'Class'), ('agency', 'Agency'), ('formation', 'Formation')])
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=300)
    path = models.CharField(max_length=512)
    state_code = models.CharField(max_length=6, null=True, blank=True)
    lga_code = models.CharField(max_length=40, null=True, blank=True)
    ownership = models.CharField(max_length=32, null=True, blank=True)
    row_valid_from = models.DateField()
    row_valid_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'scope_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_scope'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Governance scope dimension (SCD2) — country, state, LGA, network, institution, c'


class DimScopeClosure(CedaModel):
    """Scope ancestor/descendant pairs in the warehouse (permission trimming and roll-up)"""

    ceda_entity = 'dim_scope_closure'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'ancestor_key': {'type': 'bigint'}, 'descendant_key': {'type': 'bigint'}, 'depth': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    ancestor_key = models.BigIntegerField()
    descendant_key = models.BigIntegerField()
    depth = models.SmallIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'ancestor_key', 'descendant_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_scope_closure'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Scope ancestor/descendant pairs in the warehouse (permission trimming and roll-u'


class DimStaff(CedaModel):
    """Pseudonymised staff dimension (SCD2)"""

    ceda_entity = 'dim_staff'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'staff_key': {'type': 'bigint'}, 'staff_pseudo': {'type': 'hmac'}, 'sex': {'type': 'cl', 'code_list': 'sex'}, 'staff_category': {'type': 'cl', 'code_list': 'staff_category'}, 'academic_rank': {'type': 'cl', 'code_list': 'academic_rank'}, 'is_qualified_teacher': {'type': 'bool'}, 'is_trcn_registered': {'type': 'bool'}, 'row_valid_from': {'type': 'date'}, 'row_valid_to': {'type': 'date'}, 'is_current': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    staff_key = models.BigIntegerField()
    staff_pseudo = models.BinaryField()
    sex = models.CharField(max_length=32, null=True, blank=True)
    staff_category = models.CharField(max_length=32, null=True, blank=True)
    academic_rank = models.CharField(max_length=32, null=True, blank=True)
    is_qualified_teacher = models.BooleanField(null=True, blank=True)
    is_trcn_registered = models.BooleanField(null=True, blank=True)
    row_valid_from = models.DateField()
    row_valid_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'staff_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_staff'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Pseudonymised staff dimension (SCD2)'


class DimSubject(CedaModel):
    """Subject dimension"""

    ceda_entity = 'dim_subject'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'dimension'
    ceda_class = 'public'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'subject_key': {'type': 'bigint'}, 'subject_id': {'type': 'uuid'}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'subject_group': {'type': 'cl', 'code_list': 'subject_group'}, 'is_mandatory_core': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    subject_key = models.BigIntegerField()
    subject_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    subject_group = models.CharField(max_length=32, null=True, blank=True)
    is_mandatory_core = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'subject_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'dim_subject'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Subject dimension'


class FactAlert(CedaModel):
    """Alert fact (raised, acknowledged, escalated, resolved; age)"""

    ceda_entity = 'fact_alert'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'alert_id': {'type': 'uuid'}, 'scope_key': {'type': 'bigint'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'rule_key': {'type': 'code'}, 'raised_date_key': {'type': 'int'}, 'resolved_date_key': {'type': 'int'}, 'escalations': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    alert_id = cf.UUID7Field()
    scope_key = models.BigIntegerField()
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    rule_key = models.CharField(max_length=40)
    raised_date_key = models.IntegerField()
    resolved_date_key = models.IntegerField(null=True, blank=True)
    escalations = models.SmallIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'alert_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_alert'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Alert fact (raised, acknowledged, escalated, resolved; age)'


class FactAssessmentResult(CedaModel):
    """Assessment result fact (score %, objective results)"""

    ceda_entity = 'fact_assessment_result'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'assessment_id': {'type': 'uuid'}, 'learner_key': {'type': 'bigint'}, 'date_key': {'type': 'int'}, 'class_key': {'type': 'bigint'}, 'subject_key': {'type': 'bigint'}, 'assessment_kind': {'type': 'enum', 'enum': 'assessment_kind'}, 'score_pct': {'type': 'pct'}, 'is_missing_work': {'type': 'bool'}, 'target_gap_points': {'type': 'dec'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    assessment_id = cf.UUID7Field()
    learner_key = models.BigIntegerField()
    date_key = models.IntegerField()
    class_key = models.BigIntegerField()
    subject_key = models.BigIntegerField()
    assessment_kind = models.CharField(max_length=32, choices=[('formative', 'Formative'), ('summative', 'Summative'), ('coursework', 'Coursework'), ('practical', 'Practical'), ('competency', 'Competency'), ('ca_test', 'Ca test'), ('examination', 'Examination'), ('homework', 'Homework'), ('quiz', 'Quiz')])
    score_pct = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    is_missing_work = models.BooleanField()
    target_gap_points = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'assessment_id', 'learner_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_assessment_result'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Assessment result fact (score %, objective results)'


class FactAttendance(CedaModel):
    """Attendance mark fact (pseudonymised learner) — grain learner × register (partitioned by month)"""

    ceda_entity = 'fact_attendance'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'register_id': {'type': 'uuid'}, 'learner_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'class_key': {'type': 'bigint'}, 'register_kind': {'type': 'enum', 'enum': 'register_kind'}, 'code': {'type': 'cl', 'code_list': 'attendance_code'}, 'is_present': {'type': 'bool'}, 'is_late': {'type': 'bool'}, 'is_authorised_absence': {'type': 'bool'}, 'minutes_late': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    register_id = cf.UUID7Field()
    learner_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    class_key = models.BigIntegerField()
    register_kind = models.CharField(max_length=32, choices=[('am', 'Am'), ('pm', 'Pm'), ('daily', 'Daily'), ('lesson', 'Lesson'), ('activity', 'Activity'), ('trip', 'Trip')])
    code = models.CharField(max_length=32)
    is_present = models.BooleanField()
    is_late = models.BooleanField()
    is_authorised_absence = models.BooleanField()
    minutes_late = models.SmallIntegerField(null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'register_id', 'learner_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_attendance'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Attendance mark fact (pseudonymised learner) — grain learner × register (partiti'


class FactBehaviour(CedaModel):
    """Behaviour event fact"""

    ceda_entity = 'fact_behaviour'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'behaviour_event_id': {'type': 'uuid'}, 'date_key': {'type': 'int'}, 'learner_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'class_key': {'type': 'bigint'}, 'polarity': {'type': 'enum', 'enum': 'polarity'}, 'category': {'type': 'cl', 'code_list': 'behaviour_category'}, 'points': {'type': 'smallint'}, 'outcome': {'type': 'enum', 'enum': 'behaviour_outcome'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    behaviour_event_id = cf.UUID7Field()
    date_key = models.IntegerField()
    learner_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    class_key = models.BigIntegerField(null=True, blank=True)
    polarity = models.CharField(max_length=32, choices=[('positive', 'Positive'), ('negative', 'Negative')])
    category = models.CharField(max_length=32)
    points = models.SmallIntegerField()
    outcome = models.CharField(max_length=32, choices=[('none', 'None'), ('warning', 'Warning'), ('detention', 'Detention'), ('on_report', 'On report'), ('parent_contact', 'Parent contact'), ('intervention', 'Intervention'), ('internal_exclusion', 'Internal exclusion'), ('suspension', 'Suspension'), ('exclusion', 'Exclusion')], null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'behaviour_event_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_behaviour'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Behaviour event fact'


class FactCertificateEvent(CedaModel):
    """Certificate lifecycle and verification fact"""

    ceda_entity = 'fact_certificate_event'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'event_id': {'type': 'uuid'}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'event_kind': {'type': 'code'}, 'credential_kind': {'type': 'enum', 'enum': 'credential_kind'}, 'channel': {'type': 'code'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    event_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField(null=True, blank=True)
    event_kind = models.CharField(max_length=24, help_text='issued, revoked, reissued, corrected, verified_ok, verified_failed, reissue_requested')
    credential_kind = models.CharField(max_length=32, choices=[('certificate', 'Certificate'), ('transcript', 'Transcript'), ('testimonial', 'Testimonial'), ('approval_certificate', 'Approval certificate'), ('badge', 'Badge'), ('micro_credential', 'Micro credential'), ('certified_copy', 'Certified copy')], null=True, blank=True)
    channel = models.CharField(max_length=24, null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'event_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_certificate_event'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Certificate lifecycle and verification fact'


class FactClassSubjectCoverage(CedaModel):
    """Daily coverage snapshot per class-subject — teacher of record, qualified, hours required vs scheduled vs delivered"""

    ceda_entity = 'fact_class_subject_coverage'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'class_key': {'type': 'bigint'}, 'subject_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'is_mandatory': {'type': 'bool'}, 'has_teacher_of_record': {'type': 'bool'}, 'is_teacher_qualified': {'type': 'bool'}, 'required_hours_to_date': {'type': 'dec'}, 'scheduled_hours_to_date': {'type': 'dec'}, 'delivered_hours_to_date': {'type': 'dec'}, 'objectives_due': {'type': 'smallint'}, 'objectives_delivered': {'type': 'smallint'}, 'objectives_assessed_due': {'type': 'smallint'}, 'objectives_assessed': {'type': 'smallint'}, 'open_gaps': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    class_key = models.BigIntegerField()
    subject_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    is_mandatory = models.BooleanField()
    has_teacher_of_record = models.BooleanField()
    is_teacher_qualified = models.BooleanField()
    required_hours_to_date = models.DecimalField(max_digits=7, decimal_places=1)
    scheduled_hours_to_date = models.DecimalField(max_digits=7, decimal_places=1)
    delivered_hours_to_date = models.DecimalField(max_digits=7, decimal_places=1)
    objectives_due = models.SmallIntegerField()
    objectives_delivered = models.SmallIntegerField()
    objectives_assessed_due = models.SmallIntegerField()
    objectives_assessed = models.SmallIntegerField()
    open_gaps = models.SmallIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'class_key', 'subject_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_class_subject_coverage'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Daily coverage snapshot per class-subject — teacher of record, qualified, hours '


class FactComplianceScore(CedaModel):
    """Curriculum compliance per institution per day with components (subject coverage 20, hours 25, objectives 25, assessment 15, qualified staff 15)"""

    ceda_entity = 'fact_compliance_score'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'component': {'type': 'code'}, 'score': {'type': 'score'}, 'weight': {'type': 'dec'}, 'band': {'type': 'code'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField()
    component = models.CharField(max_length=32, help_text='subject_coverage, teaching_hours, objectives, assessment, qualified_staff, total')
    score = models.DecimalField(max_digits=7, decimal_places=3)
    weight = models.DecimalField(max_digits=6, decimal_places=4)
    band = models.CharField(max_length=24, null=True, blank=True, help_text='compliant, partial, non_compliant, not_assessed')
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'institution_key', 'component')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_compliance_score'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Curriculum compliance per institution per day with components (subject coverage '


class FactCoverageGap(CedaModel):
    """Coverage gap fact (opened, closed, age, severity, rule)"""

    ceda_entity = 'fact_coverage_gap'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'gap_id': {'type': 'uuid'}, 'institution_key': {'type': 'bigint'}, 'class_key': {'type': 'bigint'}, 'subject_key': {'type': 'bigint'}, 'rule': {'type': 'enum', 'enum': 'coverage_rule'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'opened_date_key': {'type': 'int'}, 'closed_date_key': {'type': 'int'}, 'escalation_level': {'type': 'smallint'}, 'learners_affected': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    gap_id = cf.UUID7Field()
    institution_key = models.BigIntegerField()
    class_key = models.BigIntegerField(null=True, blank=True)
    subject_key = models.BigIntegerField(null=True, blank=True)
    rule = models.CharField(max_length=32, choices=[('g1', 'G1'), ('g2', 'G2'), ('g3', 'G3'), ('g4', 'G4'), ('g5', 'G5'), ('g6', 'G6'), ('g7', 'G7'), ('g8', 'G8'), ('g9', 'G9'), ('g10', 'G10'), ('g11', 'G11'), ('g12', 'G12')])
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    opened_date_key = models.IntegerField()
    closed_date_key = models.IntegerField(null=True, blank=True)
    escalation_level = models.SmallIntegerField()
    learners_affected = models.SmallIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'gap_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_coverage_gap'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Coverage gap fact (opened, closed, age, severity, rule)'


class FactCurriculumDelivery(CedaModel):
    """Lesson delivery fact per objective"""

    ceda_entity = 'fact_curriculum_delivery'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'delivery_id': {'type': 'uuid'}, 'node_key': {'type': 'bigint'}, 'date_key': {'type': 'int'}, 'class_key': {'type': 'bigint'}, 'staff_key': {'type': 'bigint'}, 'delivered_minutes': {'type': 'minutes'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    delivery_id = cf.UUID7Field()
    node_key = models.BigIntegerField()
    date_key = models.IntegerField()
    class_key = models.BigIntegerField()
    staff_key = models.BigIntegerField()
    delivered_minutes = models.IntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'delivery_id', 'node_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_curriculum_delivery'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Lesson delivery fact per objective'


class FactDataQuality(CedaModel):
    """Data Quality Index components per institution per day (DQI = 0.30C + 0.20U + 0.20V + 0.15T + 0.10K + 0.05Ve)"""

    ceda_entity = 'fact_data_quality'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'completeness': {'type': 'ratio'}, 'uniqueness': {'type': 'ratio'}, 'validity': {'type': 'ratio'}, 'timeliness': {'type': 'ratio'}, 'consistency': {'type': 'ratio'}, 'verification': {'type': 'ratio'}, 'dqi': {'type': 'score'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField()
    completeness = models.DecimalField(max_digits=7, decimal_places=6)
    uniqueness = models.DecimalField(max_digits=7, decimal_places=6)
    validity = models.DecimalField(max_digits=7, decimal_places=6)
    timeliness = models.DecimalField(max_digits=7, decimal_places=6)
    consistency = models.DecimalField(max_digits=7, decimal_places=6)
    verification = models.DecimalField(max_digits=7, decimal_places=6)
    dqi = models.DecimalField(max_digits=7, decimal_places=3)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'institution_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_data_quality'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Data Quality Index components per institution per day (DQI = 0.30C + 0.20U + 0.2'


class FactDigitalSkill(CedaModel):
    """Digital-skills level snapshot per person and strand"""

    ceda_entity = 'fact_digital_skill'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'person_pseudo': {'type': 'hmac'}, 'person_kind': {'type': 'enum', 'enum': 'person_kind'}, 'institution_key': {'type': 'bigint'}, 'strand': {'type': 'cl', 'code_list': 'digital_strand'}, 'level': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    person_pseudo = models.BinaryField()
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    institution_key = models.BigIntegerField()
    strand = models.CharField(max_length=32)
    level = models.SmallIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'person_pseudo', 'strand')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_digital_skill'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Digital-skills level snapshot per person and strand'


class FactDigitisation(CedaModel):
    """Digitisation throughput and quality fact per batch and day"""

    ceda_entity = 'fact_digitisation'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'batch_id': {'type': 'uuid'}, 'hub': {'type': 'str'}, 'lga_scope_key': {'type': 'bigint'}, 'pages_captured': {'type': 'int_u'}, 'pages_indexed': {'type': 'int_u'}, 'key_field_accuracy': {'type': 'pct'}, 'hours_scan_to_searchable': {'type': 'dec'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    batch_id = cf.UUID7Field()
    hub = models.CharField(max_length=80, null=True, blank=True)
    lga_scope_key = models.BigIntegerField(null=True, blank=True)
    pages_captured = models.PositiveIntegerField()
    pages_indexed = models.PositiveIntegerField()
    key_field_accuracy = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    hours_scan_to_searchable = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'batch_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_digitisation'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Digitisation throughput and quality fact per batch and day'


class FactEnrolmentCensus(CedaModel):
    """Enrolment at the census date per learner and period (billable, exempt) — grain learner × period"""

    ceda_entity = 'fact_enrolment_census'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'period_key': {'type': 'bigint'}, 'learner_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'is_billable': {'type': 'bool'}, 'is_exempt': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    period_key = models.BigIntegerField()
    learner_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    education_level = models.CharField(max_length=32)
    is_billable = models.BooleanField()
    is_exempt = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'period_key', 'learner_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_enrolment_census'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Enrolment at the census date per learner and period (billable, exempt) — grain l'


class FactExamResult(CedaModel):
    """Examination result fact (internal and external series; credits and passes)"""

    ceda_entity = 'fact_exam_result'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'series_id': {'type': 'uuid'}, 'learner_key': {'type': 'bigint'}, 'subject_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'exam_body': {'type': 'cl', 'code_list': 'exam_body'}, 'exam_year': {'type': 'smallint'}, 'grade_label': {'type': 'code'}, 'is_pass': {'type': 'bool'}, 'is_credit': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    series_id = cf.UUID7Field()
    learner_key = models.BigIntegerField()
    subject_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    exam_body = models.CharField(max_length=32)
    exam_year = models.SmallIntegerField()
    grade_label = models.CharField(max_length=16)
    is_pass = models.BooleanField()
    is_credit = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'series_id', 'learner_key', 'subject_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_exam_result'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Examination result fact (internal and external series; credits and passes)'


class FactFinance(CedaModel):
    """Finance fact (invoiced, collected, outstanding by charge type; budget vs actual)"""

    ceda_entity = 'fact_finance'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'charge_type_code': {'type': 'code'}, 'measure': {'type': 'code'}, 'amount_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField()
    charge_type_code = models.CharField(max_length=32)
    measure = models.CharField(max_length=24, help_text='invoiced, collected, outstanding, budget, actual')
    amount_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'institution_key', 'charge_type_code', 'measure')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_finance'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Finance fact (invoiced, collected, outstanding by charge type; budget vs actual)'


class FactHealthIndex(CedaModel):
    """Institution health index per day with decomposed indicator scores and weights (P8)"""

    ceda_entity = 'fact_health_index'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'indicator': {'type': 'code'}, 'raw_value': {'type': 'dec'}, 'normalised_score': {'type': 'score'}, 'weight': {'type': 'dec'}, 'policy_version': {'type': 'int_u'}, 'is_partial': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField()
    indicator = models.CharField(max_length=40, help_text="attendance, progress, exam_outcomes, retention, dropout … or 'index'")
    raw_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    normalised_score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    policy_version = models.PositiveIntegerField()
    is_partial = models.BooleanField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'institution_key', 'indicator')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_health_index'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Institution health index per day with decomposed indicator scores and weights (P'


class FactInfrastructure(CedaModel):
    """Infrastructure snapshot per institution per term (classrooms per learner, toilets, water, power, ICT, condition)"""

    ceda_entity = 'fact_infrastructure'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'period_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'classrooms': {'type': 'smallint'}, 'learners_per_classroom': {'type': 'dec'}, 'toilets': {'type': 'smallint'}, 'has_water': {'type': 'bool'}, 'has_power': {'type': 'bool'}, 'ict_devices': {'type': 'int_u'}, 'condition_score': {'type': 'score'}, 'textbook_ratio': {'type': 'json'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    period_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    classrooms = models.SmallIntegerField()
    learners_per_classroom = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    toilets = models.SmallIntegerField(null=True, blank=True)
    has_water = models.BooleanField(null=True, blank=True)
    has_power = models.BooleanField(null=True, blank=True)
    ict_devices = models.PositiveIntegerField(null=True, blank=True)
    condition_score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    textbook_ratio = models.JSONField(null=True, blank=True, help_text='Subject × level → textbooks per learner')
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'period_key', 'institution_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_infrastructure'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Infrastructure snapshot per institution per term (classrooms per learner, toilet'


class FactLmsActivity(CedaModel):
    """LMS activity fact per assignment (set, submitted, on time, late, missing, marked)"""

    ceda_entity = 'fact_lms_activity'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'assignment_id': {'type': 'uuid'}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'class_key': {'type': 'bigint'}, 'staff_key': {'type': 'bigint'}, 'assignment_kind': {'type': 'enum', 'enum': 'assignment_kind'}, 'learners_expected': {'type': 'smallint'}, 'submitted': {'type': 'smallint'}, 'on_time': {'type': 'smallint'}, 'late': {'type': 'smallint'}, 'missing': {'type': 'smallint'}, 'marked': {'type': 'smallint'}, 'returned_online': {'type': 'smallint'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    assignment_id = cf.UUID7Field()
    date_key = models.IntegerField(help_text='Due date')
    institution_key = models.BigIntegerField()
    class_key = models.BigIntegerField(null=True, blank=True)
    staff_key = models.BigIntegerField()
    assignment_kind = models.CharField(max_length=32, choices=[('homework', 'Homework'), ('coursework', 'Coursework'), ('ca_test', 'Ca test'), ('quiz_cbt', 'Quiz cbt'), ('practical', 'Practical'), ('portfolio', 'Portfolio'), ('peer_review', 'Peer review'), ('digital_skills_task', 'Digital skills task')])
    learners_expected = models.SmallIntegerField()
    submitted = models.SmallIntegerField()
    on_time = models.SmallIntegerField()
    late = models.SmallIntegerField()
    missing = models.SmallIntegerField()
    marked = models.SmallIntegerField()
    returned_online = models.SmallIntegerField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'assignment_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_lms_activity'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'LMS activity fact per assignment (set, submitted, on time, late, missing, marked'


class FactMessage(CedaModel):
    """Messaging fact (volumes, delivery, read, cost by channel)"""

    ceda_entity = 'fact_message'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'message_id': {'type': 'uuid'}, 'date_key': {'type': 'int'}, 'institution_key': {'type': 'bigint'}, 'channel': {'type': 'enum', 'enum': 'channel'}, 'direction': {'type': 'enum', 'enum': 'message_direction'}, 'is_delivered': {'type': 'bool'}, 'is_read': {'type': 'bool'}, 'response_minutes': {'type': 'int'}, 'cost_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    message_id = cf.UUID7Field()
    date_key = models.IntegerField()
    institution_key = models.BigIntegerField(null=True, blank=True)
    channel = models.CharField(max_length=32, choices=[('in_app', 'In app'), ('push', 'Push'), ('sms', 'Sms'), ('whatsapp', 'Whatsapp'), ('email', 'Email'), ('voice', 'Voice'), ('ussd', 'Ussd'), ('workspace', 'Workspace'), ('web', 'Web'), ('post', 'Post')])
    direction = models.CharField(max_length=32, choices=[('outbound', 'Outbound'), ('inbound', 'Inbound')])
    is_delivered = models.BooleanField()
    is_read = models.BooleanField()
    response_minutes = models.IntegerField(null=True, blank=True)
    cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'message_id')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_message'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Messaging fact (volumes, delivery, read, cost by channel)'


class FactSdaf(CedaModel):
    """SDAF fact per institution and billing period (billed, exempted, collected, remitted, outstanding)"""

    ceda_entity = 'fact_sdaf'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'period_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'billable_learners': {'type': 'int_u'}, 'exempt_learners': {'type': 'int_u'}, 'billed_minor': {'type': 'money'}, 'exempted_minor': {'type': 'money'}, 'collected_minor': {'type': 'money'}, 'remitted_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    period_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    billable_learners = models.PositiveIntegerField()
    exempt_learners = models.PositiveIntegerField()
    billed_minor = models.BigIntegerField(help_text='(minor units)')
    exempted_minor = models.BigIntegerField(help_text='(minor units)')
    collected_minor = models.BigIntegerField(help_text='(minor units)')
    remitted_minor = models.BigIntegerField(help_text='(minor units)')
    currency = models.CharField(max_length=3)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'period_key', 'institution_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_sdaf'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'SDAF fact per institution and billing period (billed, exempted, collected, remit'


class FactStaffPresence(CedaModel):
    """Staff presence per day (sign-in or register-derived)"""

    ceda_entity = 'fact_staff_presence'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'fact'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'date_key': {'type': 'int'}, 'staff_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'is_expected': {'type': 'bool'}, 'is_present': {'type': 'bool'}, 'absence_type': {'type': 'cl', 'code_list': 'absence_type'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    date_key = models.IntegerField()
    staff_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    is_expected = models.BooleanField()
    is_present = models.BooleanField()
    absence_type = models.CharField(max_length=32, null=True, blank=True)
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'date_key', 'staff_key', 'institution_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'fact_staff_presence'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Staff presence per day (sign-in or register-derived)'


class FeatureLearnerWeekly(CedaModel):
    """Point-in-time learner feature set for early-warning models (no protected characteristics)"""

    ceda_entity = 'feature_learner_weekly'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'feature'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'week_start_key': {'type': 'int'}, 'learner_key': {'type': 'bigint'}, 'institution_key': {'type': 'bigint'}, 'attendance_rate_4w': {'type': 'ratio'}, 'attendance_trend': {'type': 'dec'}, 'attainment_trend': {'type': 'dec'}, 'negative_behaviour_4w': {'type': 'smallint'}, 'missing_work_4w': {'type': 'smallint'}, 'transitions': {'type': 'smallint'}, 'label_dropout_next_term': {'type': 'bool'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    week_start_key = models.IntegerField()
    learner_key = models.BigIntegerField()
    institution_key = models.BigIntegerField()
    attendance_rate_4w = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    attendance_trend = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
    attainment_trend = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
    negative_behaviour_4w = models.SmallIntegerField(null=True, blank=True)
    missing_work_4w = models.SmallIntegerField(null=True, blank=True)
    transitions = models.SmallIntegerField(null=True, blank=True, help_text='Moves between institutions')
    label_dropout_next_term = models.BooleanField(null=True, blank=True, help_text='Training label, filled retrospectively')
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'week_start_key', 'learner_key')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'feature_learner_weekly'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Point-in-time learner feature set for early-warning models (no protected charact'


class LiveKpi(CedaModel):
    """Live KPI read model (attendance today, registers, staff presence) refreshed by stream aggregation ≤ 5 min"""

    ceda_entity = 'live_kpi'
    ceda_zones = ('dw',)
    ceda_domain = 'DW'
    ceda_kind = 'aggregate'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = None
    ceda_fields = {'tenant_id': {'type': 'uuid', 'standard': True}, 'metric_code': {'type': 'code'}, 'scope_key': {'type': 'bigint'}, 'as_of_date': {'type': 'date'}, 'value': {'type': 'dec'}, 'numerator': {'type': 'dec'}, 'denominator': {'type': 'dec'}, 'is_suppressed': {'type': 'bool'}, 'refreshed_at': {'type': 'ts'}, 'loaded_at': {'type': 'ts', 'standard': True}, 'load_batch_id': {'type': 'bigint', 'standard': True}}

    tenant_id = cf.UUID7Field()
    metric_code = models.CharField(max_length=40)
    scope_key = models.BigIntegerField()
    as_of_date = models.DateField()
    value = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    numerator = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    denominator = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    is_suppressed = models.BooleanField()
    refreshed_at = models.DateTimeField()
    loaded_at = models.DateTimeField(default=cf.utcnow)
    load_batch_id = models.BigIntegerField()
    pk = models.CompositePrimaryKey('tenant_id', 'metric_code', 'scope_key', 'as_of_date')

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'live_kpi'
        app_label = 'analytics'
        base_manager_name = 'unscoped'
        verbose_name = 'Live KPI read model (attendance today, registers, staff presence) refreshed by s'
