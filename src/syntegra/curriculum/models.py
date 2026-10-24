"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``curriculum`` — Curriculum 360, adoption, teaching chain evidence and zero-gap coverage assurance.
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



class CoverageGap(CedaModel):
    """Coverage gap — a breached teaching-chain invariant (G1–G12) with owner, severity, due date and escalation"""

    ceda_entity = 'coverage_gap'
    ceda_zones = ('ops',)
    ceda_domain = 'CUR'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'rule': {'type': 'enum', 'enum': 'coverage_rule'}, 'severity': {'type': 'enum', 'enum': 'severity'}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'class_subject_plan_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'course_section_id': {'type': 'ref', 'ref': 'course_section'}, 'teaching_assignment_id': {'type': 'ref', 'ref': 'teaching_assignment'}, 'learners_affected': {'type': 'smallint'}, 'owner_role': {'type': 'code'}, 'owner_user_id': {'type': 'uuid'}, 'due_on': {'type': 'date'}, 'escalation_level': {'type': 'smallint'}, 'escalated_to_scope_id': {'type': 'uuid'}, 'suggested_fixes': {'type': 'json'}, 'accepted_by_head': {'type': 'bool'}, 'opened_at': {'type': 'ts'}, 'closed_at': {'type': 'ts'}, 'closed_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'gap_status'}, 'open_key': {'type': 'code', 'generated': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    rule = models.CharField(max_length=32, choices=[('g1', 'G1'), ('g2', 'G2'), ('g3', 'G3'), ('g4', 'G4'), ('g5', 'G5'), ('g6', 'G6'), ('g7', 'G7'), ('g8', 'G8'), ('g9', 'G9'), ('g10', 'G10'), ('g11', 'G11'), ('g12', 'G12')])
    severity = models.CharField(max_length=32, choices=[('critical', 'Critical'), ('high', 'High'), ('moderate', 'Moderate'), ('info', 'Info')])
    institution_id = cf.UUID7Field()
    class_subject_plan = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_subject_plan_id', null=True, blank=True)
    course_section = models.ForeignKey("academic.CourseSection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_section_id', null=True, blank=True)
    teaching_assignment = models.ForeignKey("academic.TeachingAssignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='teaching_assignment_id', null=True, blank=True)
    learners_affected = models.SmallIntegerField()
    owner_role = models.CharField(max_length=16)
    owner_user_id = cf.UUID7Field(null=True, blank=True)
    due_on = models.DateField()
    escalation_level = models.SmallIntegerField(default=0)
    escalated_to_scope_id = cf.UUID7Field(null=True, blank=True)
    suggested_fixes = models.JSONField(null=True, blank=True, help_text='Ranked qualified teachers with spare load, LGA deployment, remote teaching')
    accepted_by_head = models.BooleanField(default=False, help_text='Gap accepted (e.g. leaver handover)')
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('open', 'Open'), ('in_progress', 'In progress'), ('escalated', 'Escalated'), ('accepted', 'Accepted'), ('closed', 'Closed')])
    open_key = cf.generated(models.CharField(max_length=120, null=True, blank=True, help_text='rule:target while open; NULL when closed (one open gap per target per rule)', editable=False))
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'coverage_gap'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Coverage gap — a breached teaching-chain invariant (G1–G12) with owner, severity'


class Curriculum(CedaModel):
    """Curriculum 360 master (national, state, international or institutional framework)"""

    ceda_entity = 'curriculum'
    ceda_zones = ('registry',)
    ceda_domain = 'CUR'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'framework': {'type': 'cl', 'code_list': 'curriculum_framework'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'levels': {'type': 'cls', 'code_list': 'education_level'}, 'authority': {'type': 'cl', 'code_list': 'regulator'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=48, help_text='e.g. NG-NERDC-MATH-JSS')
    title = models.CharField(max_length=300)
    framework = models.CharField(max_length=32, help_text='national, state, cambridge, ib, pearson, competency, institutional')
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='subject_id', null=True, blank=True)
    levels = models.JSONField()
    authority = models.CharField(max_length=32, help_text='NERDC, State MoE, NBTE, NCCE, NUC …')
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
        db_table = 'curriculum'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Curriculum 360 master (national, state, international or institutional framework'


class CurriculumAdoption(CedaModel):
    """Which curriculum version applies to which institution, level, cohort and period (resolved automatically)"""

    ceda_entity = 'curriculum_adoption'
    ceda_zones = ('registry',)
    ceda_domain = 'CUR'
    ceda_kind = 'link'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'version_id': {'type': 'ref', 'ref': 'curriculum_version'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'cohort_start_year': {'type': 'smallint'}, 'is_additional': {'type': 'bool'}, 'resolved_by': {'type': 'enum', 'enum': 'adoption_source'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution = models.ForeignKey("institutions.Institution", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='institution_id')
    version = models.ForeignKey("curriculum.CurriculumVersion", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='version_id')
    education_level = models.CharField(max_length=32)
    cohort_start_year = models.SmallIntegerField(null=True, blank=True)
    is_additional = models.BooleanField(default=False, help_text='Approved institution addition (Cambridge, IB, faith studies)')
    resolved_by = models.CharField(max_length=32, choices=[('automatic', 'Automatic'), ('state_adaptation', 'State adaptation'), ('institution_addition', 'Institution addition'), ('exception', 'Exception')])
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
        db_table = 'curriculum_adoption'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Which curriculum version applies to which institution, level, cohort and period '


class CurriculumNode(CedaModel):
    """Strand, theme, topic, learning objective or competency of a curriculum version"""

    ceda_entity = 'curriculum_node'
    ceda_zones = ('registry',)
    ceda_domain = 'CUR'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'version_id': {'type': 'ref', 'ref': 'curriculum_version'}, 'parent_id': {'type': 'ref', 'ref': 'curriculum_node'}, 'node_code': {'type': 'code'}, 'kind': {'type': 'enum', 'enum': 'curriculum_node_kind'}, 'statement': {'type': 'text'}, 'requirement': {'type': 'enum', 'enum': 'requirement_status'}, 'is_state_addition': {'type': 'bool'}, 'min_hours': {'type': 'dec'}, 'is_assessment_required': {'type': 'bool'}, 'teacher_requirements': {'type': 'json'}, 'resource_requirements': {'type': 'json'}, 'term_hint': {'type': 'smallint'}, 'sort_key': {'type': 'int'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    version = models.ForeignKey("curriculum.CurriculumVersion", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='version_id')
    parent = models.ForeignKey("curriculum.CurriculumNode", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='parent_id', null=True, blank=True)
    node_code = models.CharField(max_length=48, help_text='Unique within the version')
    kind = models.CharField(max_length=32, choices=[('subject', 'Subject'), ('strand', 'Strand'), ('theme', 'Theme'), ('topic', 'Topic'), ('objective', 'Objective'), ('competency', 'Competency')])
    statement = models.TextField()
    requirement = models.CharField(max_length=32, choices=[('mandatory', 'Mandatory'), ('optional', 'Optional'), ('recommended', 'Recommended'), ('restricted', 'Restricted')], help_text='mandatory, optional, recommended, restricted')
    is_state_addition = models.BooleanField(default=False)
    min_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    is_assessment_required = models.BooleanField(default=False)
    teacher_requirements = models.JSONField(null=True, blank=True, help_text='Required qualification and specialism')
    resource_requirements = models.JSONField(null=True, blank=True)
    term_hint = models.SmallIntegerField(null=True, blank=True, help_text='Suggested term for scheme-of-work drafting')
    sort_key = models.IntegerField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'curriculum_node'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Strand, theme, topic, learning objective or competency of a curriculum version'


class CurriculumVersion(CedaModel):
    """Immutable published version of a curriculum (copy-on-write; author ≠ approver)"""

    ceda_entity = 'curriculum_version'
    ceda_zones = ('registry',)
    ceda_domain = 'CUR'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'curriculum_id': {'type': 'ref', 'ref': 'curriculum'}, 'version_label': {'type': 'semver'}, 'base_version_id': {'type': 'ref', 'ref': 'curriculum_version'}, 'is_adaptation': {'type': 'bool'}, 'language': {'type': 'lang'}, 'status': {'type': 'enum', 'enum': 'curriculum_status'}, 'effective_from': {'type': 'date'}, 'effective_to': {'type': 'date'}, 'authored_by': {'type': 'ref', 'ref': 'app_user'}, 'approved_by': {'type': 'ref', 'ref': 'app_user'}, 'approval_reason': {'type': 'text'}, 'source_document_id': {'type': 'uuid'}, 'content_hash': {'type': 'hash'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    curriculum = models.ForeignKey("curriculum.Curriculum", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='curriculum_id')
    version_label = models.CharField(max_length=32, help_text='e.g. 3.1')
    base_version = models.ForeignKey("curriculum.CurriculumVersion", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='base_version_id', null=True, blank=True)
    is_adaptation = models.BooleanField(default=False)
    language = models.CharField(max_length=35, null=True, blank=True, help_text='Curriculum versions by language of instruction')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('review', 'Review'), ('approved', 'Approved'), ('published', 'Published'), ('superseded', 'Superseded'), ('withdrawn', 'Withdrawn')])
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    authored_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='authored_by')
    approved_by = models.ForeignKey("iam.AppUser", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='approved_by', null=True, blank=True)
    approval_reason = models.TextField(null=True, blank=True)
    source_document_id = cf.UUID7Field(null=True, blank=True, help_text='Digitised source (captured from paper; human approval before publication)')
    content_hash = models.BinaryField(null=True, blank=True, help_text='Hash of the node tree at publication')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'curriculum_version'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Immutable published version of a curriculum (copy-on-write; author ≠ approver)'


class DeliveryLog(CedaModel):
    """Evidence that a lesson was delivered — objectives covered, learners present, note (G6)"""

    ceda_entity = 'delivery_log'
    ceda_zones = ('ops',)
    ceda_domain = 'CUR'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'lesson_occurrence_id': {'type': 'ref', 'ref': 'lesson_occurrence'}, 'teaching_assignment_id': {'type': 'ref', 'ref': 'teaching_assignment'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'node_ids': {'type': 'json'}, 'delivered_minutes': {'type': 'minutes'}, 'is_as_planned': {'type': 'bool'}, 'source': {'type': 'enum', 'enum': 'delivery_source'}, 'learners_present': {'type': 'smallint'}, 'note': {'type': 'str'}, 'delivered_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    lesson_occurrence = models.ForeignKey("timetable.LessonOccurrence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lesson_occurrence_id')
    teaching_assignment = models.ForeignKey("academic.TeachingAssignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='teaching_assignment_id')
    staff_id = cf.UUID7Field()
    node_ids = models.JSONField(help_text='Objectives covered')
    delivered_minutes = models.IntegerField()
    is_as_planned = models.BooleanField()
    source = models.CharField(max_length=32, choices=[('class_page', 'Class page'), ('staff_app', 'Staff app'), ('lms_lesson', 'Lms lesson'), ('import', 'Import')], help_text='class_page, staff_app, lms_lesson')
    learners_present = models.SmallIntegerField(null=True, blank=True)
    note = models.CharField(max_length=1000, null=True, blank=True)
    delivered_on = models.DateField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'delivery_log'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Evidence that a lesson was delivered — objectives covered, learners present, not'


class GapEvent(CedaModel):
    """History of a coverage gap (opened, reminded, escalated, fix proposed, closed) — append-only"""

    ceda_entity = 'gap_event'
    ceda_zones = ('ops',)
    ceda_domain = 'CUR'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'gap_id': {'type': 'ref', 'ref': 'coverage_gap'}, 'event_kind': {'type': 'enum', 'enum': 'gap_event_kind'}, 'actor': {'type': 'uuid'}, 'detail': {'type': 'json'}, 'linked_thread_ref': {'type': 'code'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    gap = models.ForeignKey("curriculum.CoverageGap", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='gap_id')
    event_kind = models.CharField(max_length=32, choices=[('opened', 'Opened'), ('updated', 'Updated'), ('reminded', 'Reminded'), ('fix_proposed', 'Fix proposed'), ('escalated', 'Escalated'), ('accepted', 'Accepted'), ('closed', 'Closed'), ('reopened', 'Reopened')])
    actor = cf.UUID7Field(null=True, blank=True, help_text='User or agent service identity')
    detail = models.JSONField(null=True, blank=True)
    linked_thread_ref = models.CharField(max_length=128, null=True, blank=True, help_text='Workspace-messaging thread (FR-COM-110)')
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'gap_event'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'History of a coverage gap (opened, reminded, escalated, fix proposed, closed) — '


class SchemeOfWork(CedaModel):
    """Scheme of work for a teaching assignment — auto-drafted from curriculum hours and the calendar, edited by the teacher (G5, G10)"""

    ceda_entity = 'scheme_of_work'
    ceda_zones = ('ops',)
    ceda_domain = 'CUR'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'derived: the class'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'class_subject_plan_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'course_section_id': {'type': 'ref', 'ref': 'course_section'}, 'teaching_assignment_id': {'type': 'ref', 'ref': 'teaching_assignment'}, 'curriculum_version_id': {'type': 'ref', 'ref': 'curriculum_version'}, 'version': {'type': 'int_u'}, 'is_auto_drafted': {'type': 'bool'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    class_subject_plan = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_subject_plan_id', null=True, blank=True)
    course_section = models.ForeignKey("academic.CourseSection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_section_id', null=True, blank=True)
    teaching_assignment = models.ForeignKey("academic.TeachingAssignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='teaching_assignment_id')
    curriculum_version_id = cf.UUID7Field()
    version = models.PositiveIntegerField()
    is_auto_drafted = models.BooleanField(default=True)
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
        db_table = 'scheme_of_work'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Scheme of work for a teaching assignment — auto-drafted from curriculum hours an'


class SchemeWeek(CedaModel):
    """Week of a scheme of work with the curriculum objectives placed in it"""

    ceda_entity = 'scheme_week'
    ceda_zones = ('ops',)
    ceda_domain = 'CUR'
    ceda_kind = 'link'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'derived: the scheme'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scheme_id': {'type': 'ref', 'ref': 'scheme_of_work'}, 'week_no': {'type': 'smallint'}, 'week_starts_on': {'type': 'date'}, 'node_ids': {'type': 'json'}, 'planned_minutes': {'type': 'minutes'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scheme = models.ForeignKey("curriculum.SchemeOfWork", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='scheme_id')
    week_no = models.SmallIntegerField()
    week_starts_on = models.DateField()
    node_ids = models.JSONField(help_text='Curriculum objectives planned for the week')
    planned_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'scheme_week'
        app_label = 'curriculum'
        base_manager_name = 'unscoped'
        verbose_name = 'Week of a scheme of work with the curriculum objectives placed in it'
