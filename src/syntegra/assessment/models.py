"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``assessment`` — Assessment, grading, moderation, targets, report cards, examinations, results, GPA and transcripts.
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



class AcademicStanding(CedaModel):
    """GPA/CGPA, credits, progression and classification per learner per period (borderline cases flagged)"""

    ceda_entity = 'academic_standing'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the enrolment's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'credits_attempted': {'type': 'dec'}, 'credits_earned': {'type': 'dec'}, 'gpa': {'type': 'dec'}, 'cgpa': {'type': 'dec'}, 'progression': {'type': 'enum', 'enum': 'progression_decision'}, 'classification': {'type': 'cl', 'code_list': 'degree_class'}, 'is_borderline': {'type': 'bool'}, 'board_decision': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field()
    period_id = cf.UUID7Field()
    credits_attempted = models.DecimalField(max_digits=6, decimal_places=1)
    credits_earned = models.DecimalField(max_digits=6, decimal_places=1)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    progression = models.CharField(max_length=32, choices=[('progress', 'Progress'), ('progress_with_carryover', 'Progress with carryover'), ('repeat', 'Repeat'), ('probation', 'Probation'), ('withdraw', 'Withdraw'), ('graduate', 'Graduate')], null=True, blank=True)
    classification = models.CharField(max_length=32, null=True, blank=True)
    is_borderline = models.BooleanField(default=False)
    board_decision = models.CharField(max_length=500, null=True, blank=True)
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
        db_table = 'academic_standing'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'GPA/CGPA, credits, progression and classification per learner per period (border'


class Assessment(CedaModel):
    """Assessment 360 definition (formative, summative, coursework, practical, competency, CA test, examination)"""

    ceda_entity = 'assessment'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'class_subject_plan_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'course_section_id': {'type': 'ref', 'ref': 'course_section'}, 'assignment_id': {'type': 'ref', 'ref': 'assignment'}, 'title': {'type': 'title'}, 'assessment_kind': {'type': 'enum', 'enum': 'assessment_kind'}, 'max_mark': {'type': 'dec'}, 'weight': {'type': 'pct'}, 'assessed_on': {'type': 'date'}, 'grading_scale_id': {'type': 'ref', 'ref': 'grading_scale'}, 'node_ids': {'type': 'json'}, 'is_moderated': {'type': 'bool'}, 'locked_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'assessment_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    class_subject_plan = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_subject_plan_id', null=True, blank=True)
    course_section = models.ForeignKey("academic.CourseSection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_section_id', null=True, blank=True)
    assignment = models.ForeignKey("lms.Assignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assignment_id', null=True, blank=True)
    title = models.CharField(max_length=300)
    assessment_kind = models.CharField(max_length=32, choices=[('formative', 'Formative'), ('summative', 'Summative'), ('coursework', 'Coursework'), ('practical', 'Practical'), ('competency', 'Competency'), ('ca_test', 'Ca test'), ('examination', 'Examination'), ('homework', 'Homework'), ('quiz', 'Quiz')])
    max_mark = models.DecimalField(max_digits=7, decimal_places=3)
    weight = models.DecimalField(max_digits=6, decimal_places=3)
    assessed_on = models.DateField(null=True, blank=True)
    grading_scale_id = cf.UUID7Field(null=True, blank=True)
    node_ids = models.JSONField(null=True, blank=True, help_text='Curriculum objectives assessed (G7)')
    is_moderated = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True, help_text='Results locked after approval')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('open', 'Open'), ('marking', 'Marking'), ('moderated', 'Moderated'), ('approved', 'Approved'), ('locked', 'Locked')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'assessment'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Assessment 360 definition (formative, summative, coursework, practical, competen'


class AssessmentResult(CedaModel):
    """Mark per learner per assessment (hard ≤ max mark; corrections after lock need head approval)"""

    ceda_entity = 'assessment_result'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the assessment's class"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'assessment_id': {'type': 'ref', 'ref': 'assessment'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'score': {'type': 'dec'}, 'grade_label': {'type': 'code'}, 'objective_results': {'type': 'json'}, 'is_missing_work': {'type': 'bool'}, 'access_arrangement': {'type': 'str'}, 'comment': {'type': 'str'}, 'entered_by': {'type': 'uuid'}, 'corrected_after_lock': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    assessment = models.ForeignKey("assessment.Assessment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assessment_id')
    learner_id = cf.UUID7Field()
    score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    grade_label = models.CharField(max_length=16, null=True, blank=True)
    objective_results = models.JSONField(null=True, blank=True, help_text='Per curriculum objective (curriculum evidence)')
    is_missing_work = models.BooleanField(default=False)
    access_arrangement = models.CharField(max_length=200, null=True, blank=True, help_text='Applied adjustment (no need detail)')
    comment = models.CharField(max_length=1000, null=True, blank=True)
    entered_by = cf.UUID7Field()
    corrected_after_lock = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'assessment_result'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Mark per learner per assessment (hard ≤ max mark; corrections after lock need he'


class ExamAnomaly(CedaModel):
    """Statistical anomaly for human review (distribution shift, similarity cluster, improbable improvement) — never auto-penalised"""

    ceda_entity = 'exam_anomaly'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'queue'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'series_id': {'type': 'ref', 'ref': 'exam_series'}, 'anomaly_kind': {'type': 'enum', 'enum': 'anomaly_kind'}, 'evidence': {'type': 'json'}, 'affected_entry_ids': {'type': 'json'}, 'assigned_to': {'type': 'uuid'}, 'outcome': {'type': 'enum', 'enum': 'review_outcome'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    series = models.ForeignKey("assessment.ExamSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='series_id')
    anomaly_kind = models.CharField(max_length=32, choices=[('distribution_shift', 'Distribution shift'), ('similarity_cluster', 'Similarity cluster'), ('improbable_improvement', 'Improbable improvement'), ('timing', 'Timing'), ('other', 'Other')])
    evidence = models.JSONField()
    affected_entry_ids = models.JSONField(null=True, blank=True)
    assigned_to = cf.UUID7Field(null=True, blank=True)
    outcome = models.CharField(max_length=32, choices=[('no_issue', 'No issue'), ('explained', 'Explained'), ('action_taken', 'Action taken'), ('referred', 'Referred'), ('confirmed', 'Confirmed')], null=True, blank=True)
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
        db_table = 'exam_anomaly'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Statistical anomaly for human review (distribution shift, similarity cluster, im'


class ExamEntry(CedaModel):
    """Candidate entry (eligibility checks, access arrangements, fees)"""

    ceda_entity = 'exam_entry'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'series_id': {'type': 'ref', 'ref': 'exam_series'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'candidate_number': {'type': 'code'}, 'subjects': {'type': 'json'}, 'eligibility': {'type': 'json'}, 'access_arrangements': {'type': 'json'}, 'is_external_candidate': {'type': 'bool'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'status': {'type': 'enum', 'enum': 'entry_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    series = models.ForeignKey("assessment.ExamSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='series_id')
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field()
    candidate_number = models.CharField(max_length=32, null=True, blank=True)
    subjects = models.JSONField()
    eligibility = models.JSONField(null=True, blank=True, help_text='Checks: enrolment, subjects studied, identity verified, attendance, institution authorisation')
    access_arrangements = models.JSONField(null=True, blank=True, help_text='Authorised arrangements (no need detail)')
    is_external_candidate = models.BooleanField(default=False)
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('eligible', 'Eligible'), ('blocked', 'Blocked'), ('entered', 'Entered'), ('withdrawn', 'Withdrawn'), ('absent', 'Absent'), ('resulted', 'Resulted')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'exam_entry'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Candidate entry (eligibility checks, access arrangements, fees)'


class ExamPaper(CedaModel):
    """Paper or component of a series (subject, duration, OSCE station)"""

    ceda_entity = 'exam_paper'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'derived: the series'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'series_id': {'type': 'ref', 'ref': 'exam_series'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'paper_code': {'type': 'code'}, 'title': {'type': 'title'}, 'duration_minutes': {'type': 'minutes'}, 'is_osce_station': {'type': 'bool'}, 'station_rubric': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    series = models.ForeignKey("assessment.ExamSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='series_id')
    subject_id = cf.UUID7Field(null=True, blank=True)
    paper_code = models.CharField(max_length=20)
    title = models.CharField(max_length=300)
    duration_minutes = models.IntegerField()
    is_osce_station = models.BooleanField(default=False)
    station_rubric = models.JSONField(null=True, blank=True, help_text='OSCE station design and scoring')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'exam_paper'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Paper or component of a series (subject, duration, OSCE station)'


class ExamResult(CedaModel):
    """Result per candidate per paper (immutable once committed)"""

    ceda_entity = 'exam_result'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'derived: the entry'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'entry_id': {'type': 'ref', 'ref': 'exam_entry'}, 'paper_id': {'type': 'ref', 'ref': 'exam_paper'}, 'score': {'type': 'dec'}, 'grade_label': {'type': 'code'}, 'result_import_id': {'type': 'ref', 'ref': 'result_import'}, 'committed_at': {'type': 'ts'}, 'committed_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    entry = models.ForeignKey("assessment.ExamEntry", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='entry_id')
    paper = models.ForeignKey("assessment.ExamPaper", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='paper_id')
    score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    grade_label = models.CharField(max_length=16)
    result_import = models.ForeignKey("assessment.ResultImport", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='result_import_id', null=True, blank=True)
    committed_at = models.DateTimeField()
    committed_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'exam_result'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Result per candidate per paper (immutable once committed)'


class ExamSeries(CedaModel):
    """Examination 360 series (internal or external body, qualification, curriculum, programme)"""

    ceda_entity = 'exam_series'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'exam_body': {'type': 'cl', 'code_list': 'exam_body'}, 'name': {'type': 'title'}, 'qualification_id': {'type': 'ref', 'ref': 'qualification'}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'curriculum_version_id': {'type': 'ref', 'ref': 'curriculum_version'}, 'entry_opens_on': {'type': 'date'}, 'entry_closes_on': {'type': 'date'}, 'results_release_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'series_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    exam_body = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    qualification_id = cf.UUID7Field(null=True, blank=True)
    programme_id = cf.UUID7Field(null=True, blank=True)
    curriculum_version_id = cf.UUID7Field(null=True, blank=True)
    entry_opens_on = models.DateField(null=True, blank=True)
    entry_closes_on = models.DateField(null=True, blank=True)
    results_release_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('setup', 'Setup'), ('entries_open', 'Entries open'), ('entries_closed', 'Entries closed'), ('sitting', 'Sitting'), ('results_import', 'Results import'), ('results_approved', 'Results approved'), ('released', 'Released'), ('closed', 'Closed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'exam_series'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Examination 360 series (internal or external body, qualification, curriculum, pr'


class ExamSitting(CedaModel):
    """Sitting of a paper — room, desk layout, seat allocation and invigilators"""

    ceda_entity = 'exam_sitting'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'paper_id': {'type': 'ref', 'ref': 'exam_paper'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'starts_at': {'type': 'ts'}, 'desk_layout': {'type': 'json'}, 'seat_allocations': {'type': 'json'}, 'invigilator_staff_ids': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    paper = models.ForeignKey("assessment.ExamPaper", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='paper_id')
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id')
    starts_at = models.DateTimeField()
    desk_layout = models.JSONField()
    seat_allocations = models.JSONField(help_text='Candidate → desk label')
    invigilator_staff_ids = models.JSONField(null=True, blank=True)
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
        db_table = 'exam_sitting'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Sitting of a paper — room, desk layout, seat allocation and invigilators'


class ExternalAssessmentImport(CedaModel):
    """Historical or external assessment data import for longitudinal tracking and benchmarking"""

    ceda_entity = 'external_assessment_import'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'source': {'type': 'str'}, 'cohort_label': {'type': 'str'}, 'rows_total': {'type': 'int_u'}, 'rows_matched': {'type': 'int_u'}, 'import_job_id': {'type': 'ref', 'ref': 'import_job'}, 'status': {'type': 'enum', 'enum': 'import_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    source = models.CharField(max_length=200)
    cohort_label = models.CharField(max_length=60, null=True, blank=True)
    rows_total = models.PositiveIntegerField()
    rows_matched = models.PositiveIntegerField()
    import_job = models.ForeignKey("integration.ImportJob", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='import_job_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('uploaded', 'Uploaded'), ('mapped', 'Mapped'), ('validating', 'Validating'), ('validated', 'Validated'), ('matching', 'Matching'), ('staged', 'Staged'), ('committed', 'Committed'), ('rolled_back', 'Rolled back'), ('failed', 'Failed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'external_assessment_import'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Historical or external assessment data import for longitudinal tracking and benc'


class GradeBand(CedaModel):
    """Band of a grading scale (contiguous and non-overlapping)"""

    ceda_entity = 'grade_band'
    ceda_zones = ('registry',)
    ceda_domain = 'ASM'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'grading_scale_id': {'type': 'ref', 'ref': 'grading_scale'}, 'label': {'type': 'code'}, 'min_score': {'type': 'dec'}, 'max_score': {'type': 'dec'}, 'grade_points': {'type': 'dec'}, 'is_pass': {'type': 'bool'}, 'is_credit': {'type': 'bool'}, 'sort_order': {'type': 'smallint'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    grading_scale = models.ForeignKey("assessment.GradingScale", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='grading_scale_id')
    label = models.CharField(max_length=16, help_text='A1, B2, C4, Distinction, Level 3')
    min_score = models.DecimalField(max_digits=7, decimal_places=3)
    max_score = models.DecimalField(max_digits=7, decimal_places=3)
    grade_points = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    is_pass = models.BooleanField()
    is_credit = models.BooleanField(default=False, help_text='Counts as a credit (5 credits incl. English and Mathematics)')
    sort_order = models.SmallIntegerField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'grade_band'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Band of a grading scale (contiguous and non-overlapping)'


class GradeBroadsheet(CedaModel):
    """Grade broadsheet per class, subject and series (spreadsheet export)"""

    ceda_entity = 'grade_broadsheet'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'projection'
    ceda_class = 'confidential'
    ceda_history = 'snapshot'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'series_id': {'type': 'ref', 'ref': 'exam_series'}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'generated_at': {'type': 'ts'}, 'document_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    series = models.ForeignKey("assessment.ExamSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='series_id', null=True, blank=True)
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    generated_at = models.DateTimeField()
    document_id = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'grade_broadsheet'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Grade broadsheet per class, subject and series (spreadsheet export)'


class GradingScale(CedaModel):
    """Configurable grading scale (percentage, letter, grade points, GPA, pass/fail, competency levels, degree classes)"""

    ceda_entity = 'grading_scale'
    ceda_zones = ('registry',)
    ceda_domain = 'ASM'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'scale_kind': {'type': 'enum', 'enum': 'scale_kind'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=300)
    scale_kind = models.CharField(max_length=32, choices=[('percentage', 'Percentage'), ('letter', 'Letter'), ('grade_points', 'Grade points'), ('gpa', 'Gpa'), ('pass_fail', 'Pass fail'), ('competency', 'Competency'), ('degree_class', 'Degree class')])
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
        db_table = 'grading_scale'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Configurable grading scale (percentage, letter, grade points, GPA, pass/fail, co'


class MarkbookColumn(CedaModel):
    """Teacher marksheet column (yes/no, numeric, grade, date, comment) for offline spreadsheet round-trips"""

    ceda_entity = 'markbook_column'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'derived: the class-subject'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'class_subject_plan_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'assessment_id': {'type': 'ref', 'ref': 'assessment'}, 'label': {'type': 'str'}, 'column_kind': {'type': 'enum', 'enum': 'markbook_column_kind'}, 'sort_order': {'type': 'smallint'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    class_subject_plan = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_subject_plan_id')
    assessment = models.ForeignKey("assessment.Assessment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assessment_id', null=True, blank=True)
    label = models.CharField(max_length=80)
    column_kind = models.CharField(max_length=32, choices=[('yes_no', 'Yes no'), ('numeric', 'Numeric'), ('grade', 'Grade'), ('date', 'Date'), ('comment', 'Comment')])
    sort_order = models.SmallIntegerField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'markbook_column'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Teacher marksheet column (yes/no, numeric, grade, date, comment) for offline spr'


class ModerationSample(CedaModel):
    """Moderation sample with moderator mark and tolerance outcome"""

    ceda_entity = 'moderation_sample'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the assessment's class"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'assessment_id': {'type': 'ref', 'ref': 'assessment'}, 'submission_mark_id': {'type': 'ref', 'ref': 'submission_mark'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'original_score': {'type': 'dec'}, 'moderated_score': {'type': 'dec'}, 'moderator_staff_id': {'type': 'ref', 'ref': 'staff'}, 'within_tolerance': {'type': 'bool'}, 'note': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    assessment = models.ForeignKey("assessment.Assessment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assessment_id', null=True, blank=True)
    submission_mark = models.ForeignKey("lms.SubmissionMark", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='submission_mark_id', null=True, blank=True)
    learner_id = cf.UUID7Field()
    original_score = models.DecimalField(max_digits=7, decimal_places=3)
    moderated_score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    moderator_staff_id = cf.UUID7Field()
    within_tolerance = models.BooleanField(null=True, blank=True)
    note = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'moderation_sample'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Moderation sample with moderator mark and tolerance outcome'


class ReportCard(CedaModel):
    """Published report card of a learner for a period (document stored to the learner record)"""

    ceda_entity = 'report_card'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = "derived: the learner's class"
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'run_id': {'type': 'ref', 'ref': 'report_card_run'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'document_id': {'type': 'uuid'}, 'content_hash': {'type': 'hash'}, 'released_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    run = models.ForeignKey("assessment.ReportCardRun", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='run_id')
    learner_id = cf.UUID7Field()
    document_id = cf.UUID7Field(help_text='PDF in the records zone')
    content_hash = models.BinaryField()
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'report_card'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Published report card of a learner for a period (document stored to the learner '


class ReportCardRun(CedaModel):
    """Report-card generation run (templates, completeness checks, publication to the parent portal)"""

    ceda_entity = 'report_card_run'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'template_code': {'type': 'code'}, 'class_group_ids': {'type': 'json'}, 'completeness': {'type': 'json'}, 'withholding_policy_id': {'type': 'ref', 'ref': 'policy_rule'}, 'published_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'run_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    period_id = cf.UUID7Field()
    template_code = models.CharField(max_length=40)
    class_group_ids = models.JSONField()
    completeness = models.JSONField(null=True, blank=True, help_text='Missing marks and comments per class')
    withholding_policy_id = cf.UUID7Field(null=True, blank=True, help_text='Only an explicitly approved policy; never for SEND or safeguarding-flagged learners')
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('previewed', 'Previewed'), ('running', 'Running'), ('awaiting_approval', 'Awaiting approval'), ('approved', 'Approved'), ('issued', 'Issued'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'report_card_run'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Report-card generation run (templates, completeness checks, publication to the p'


class ResultImport(CedaModel):
    """Import of results from an exam body (file or API) with candidate matching and anomaly review"""

    ceda_entity = 'result_import'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'series_id': {'type': 'ref', 'ref': 'exam_series'}, 'source_document_id': {'type': 'uuid'}, 'rows_total': {'type': 'int_u'}, 'rows_matched': {'type': 'int_u'}, 'rows_in_review': {'type': 'int_u'}, 'anomalies': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'import_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    series = models.ForeignKey("assessment.ExamSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='series_id')
    source_document_id = cf.UUID7Field(null=True, blank=True)
    rows_total = models.PositiveIntegerField()
    rows_matched = models.PositiveIntegerField()
    rows_in_review = models.PositiveIntegerField()
    anomalies = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('uploaded', 'Uploaded'), ('mapped', 'Mapped'), ('validating', 'Validating'), ('validated', 'Validated'), ('matching', 'Matching'), ('staged', 'Staged'), ('committed', 'Committed'), ('rolled_back', 'Rolled back'), ('failed', 'Failed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'result_import'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Import of results from an exam body (file or API) with candidate matching and an'


class TargetGrade(CedaModel):
    """Target grade from prior attainment and tracking points, with RAG progress"""

    ceda_entity = 'target_grade'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = "derived: the learner's class"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'target_label': {'type': 'code'}, 'method': {'type': 'enum', 'enum': 'target_method'}, 'working_at_label': {'type': 'code'}, 'rag': {'type': 'enum', 'enum': 'rag'}, 'gap_points': {'type': 'dec'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    subject_id = cf.UUID7Field()
    target_label = models.CharField(max_length=16)
    method = models.CharField(max_length=32, choices=[('prior_attainment', 'Prior attainment'), ('tracking_points', 'Tracking points'), ('manual', 'Manual')])
    working_at_label = models.CharField(max_length=16, null=True, blank=True)
    rag = models.CharField(max_length=32, choices=[('red', 'Red'), ('amber', 'Amber'), ('green', 'Green')], null=True, blank=True)
    gap_points = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
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
        db_table = 'target_grade'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Target grade from prior attainment and tracking points, with RAG progress'


class Transcript(CedaModel):
    """Digitally signed, verifiable transcript (registered in the certificate registry as a credential of kind transcript)"""

    ceda_entity = 'transcript'
    ceda_zones = ('ops',)
    ceda_domain = 'ASM'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'derived: the learner'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'certificate_id': {'type': 'ref', 'ref': 'certificate'}, 'document_id': {'type': 'uuid'}, 'content_hash': {'type': 'hash'}, 'issued_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field()
    certificate_id = cf.UUID7Field(null=True, blank=True, help_text='Registry record carrying number, hash and signature')
    document_id = cf.UUID7Field()
    content_hash = models.BinaryField()
    issued_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'transcript'
        app_label = 'assessment'
        base_manager_name = 'unscoped'
        verbose_name = 'Digitally signed, verifiable transcript (registered in the certificate registry '
