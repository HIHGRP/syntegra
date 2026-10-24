"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``lms`` — Online coursework.
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



class Assignment(CedaModel):
    """Assignment — homework, coursework, CA test, quiz/CBT, practical, portfolio, peer review or digital-skills task"""

    ceda_entity = 'assignment'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'course_space_id': {'type': 'ref', 'ref': 'course_space'}, 'unit_id': {'type': 'ref', 'ref': 'lms_unit'}, 'assignment_kind': {'type': 'enum', 'enum': 'assignment_kind'}, 'title': {'type': 'title'}, 'instructions': {'type': 'text'}, 'node_ids': {'type': 'json'}, 'max_mark': {'type': 'dec'}, 'rubric_id': {'type': 'ref', 'ref': 'rubric'}, 'markbook_weight': {'type': 'pct'}, 'assessment_id': {'type': 'ref', 'ref': 'assessment'}, 'opens_at': {'type': 'ts'}, 'due_at': {'type': 'ts'}, 'late_policy': {'type': 'enum', 'enum': 'late_policy'}, 'allow_resubmission': {'type': 'bool'}, 'group_settings': {'type': 'json'}, 'accessibility_options': {'type': 'json'}, 'ai_policy': {'type': 'enum', 'enum': 'ai_policy'}, 'release_at': {'type': 'ts'}, 'homework_reason': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'assignment_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    course_space = models.ForeignKey("lms.CourseSpace", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_space_id')
    unit = models.ForeignKey("lms.LmsUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='unit_id', null=True, blank=True)
    assignment_kind = models.CharField(max_length=32, choices=[('homework', 'Homework'), ('coursework', 'Coursework'), ('ca_test', 'Ca test'), ('quiz_cbt', 'Quiz cbt'), ('practical', 'Practical'), ('portfolio', 'Portfolio'), ('peer_review', 'Peer review'), ('digital_skills_task', 'Digital skills task')])
    title = models.CharField(max_length=300)
    instructions = models.TextField()
    node_ids = models.JSONField(null=True, blank=True, help_text='Objectives assessed')
    max_mark = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    rubric = models.ForeignKey("lms.Rubric", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rubric_id', null=True, blank=True)
    markbook_weight = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    assessment = models.ForeignKey("assessment.Assessment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assessment_id', null=True, blank=True)
    opens_at = models.DateTimeField()
    due_at = models.DateTimeField()
    late_policy = models.CharField(max_length=32, choices=[('accept_flag', 'Accept flag'), ('accept_with_penalty', 'Accept with penalty'), ('close_at_due', 'Close at due')], default='accept_flag')
    allow_resubmission = models.BooleanField(default=False)
    group_settings = models.JSONField(null=True, blank=True)
    accessibility_options = models.JSONField(null=True, blank=True)
    ai_policy = models.CharField(max_length=32, choices=[('not_allowed', 'Not allowed'), ('allowed_with_acknowledgement', 'Allowed with acknowledgement'), ('encouraged', 'Encouraged')], default='allowed_with_acknowledgement')
    release_at = models.DateTimeField(null=True, blank=True, help_text='Scheduled release of marks and feedback')
    homework_reason = models.CharField(max_length=300, null=True, blank=True, help_text='Reason given when the nightly homework limit is exceeded')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('scheduled', 'Scheduled'), ('published', 'Published'), ('closed', 'Closed'), ('marked', 'Marked'), ('released', 'Released'), ('archived', 'Archived')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'assignment'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Assignment — homework, coursework, CA test, quiz/CBT, practical, portfolio, peer'


class ContentLibraryItem(CedaModel):
    """State content-library resource, curriculum-aligned, published by the state"""

    ceda_entity = 'content_library_item'
    ceda_zones = ('registry',)
    ceda_domain = 'LMS'
    ceda_kind = 'master'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'content_kind': {'type': 'enum', 'enum': 'content_kind'}, 'object_key': {'type': 'object_key'}, 'node_refs': {'type': 'json'}, 'licence': {'type': 'str'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    content_kind = models.CharField(max_length=32, choices=[('note', 'Note'), ('file', 'File'), ('video', 'Video'), ('audio', 'Audio'), ('link', 'Link'), ('h5p', 'H5p'), ('library_item', 'Library item'), ('live_recording', 'Live recording')])
    object_key = models.CharField(max_length=1024, null=True, blank=True)
    node_refs = models.JSONField(help_text='Curriculum versions and objectives')
    licence = models.CharField(max_length=120, null=True, blank=True)
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
        db_table = 'content_library_item'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'State content-library resource, curriculum-aligned, published by the state'


class CourseMember(CedaModel):
    """Roster membership of a course space (synced from enrolment, class membership, registration or allocation)"""

    ceda_entity = 'course_member'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = 'derived: the course space'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'course_space_id': {'type': 'ref', 'ref': 'course_space'}, 'member_kind': {'type': 'enum', 'enum': 'course_member_kind'}, 'member_id': {'type': 'uuid'}, 'space_role': {'type': 'enum', 'enum': 'space_role'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    course_space = models.ForeignKey("lms.CourseSpace", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_space_id')
    member_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('staff', 'Staff')])
    member_id = cf.UUID7Field(help_text='learner or staff id')
    space_role = models.CharField(max_length=32, choices=[('owner', 'Owner'), ('editor', 'Editor'), ('observer', 'Observer'), ('learner', 'Learner')])
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
        db_table = 'course_member'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Roster membership of a course space (synced from enrolment, class membership, re'


class CourseSpace(CedaModel):
    """LMS course space for a class-subject, course section or staff training course (auto-created; roster synced)"""

    ceda_entity = 'course_space'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'space_kind': {'type': 'enum', 'enum': 'space_kind'}, 'class_subject_plan_id': {'type': 'ref', 'ref': 'class_subject_plan'}, 'course_section_id': {'type': 'ref', 'ref': 'course_section'}, 'title': {'type': 'title'}, 'owner_staff_id': {'type': 'ref', 'ref': 'staff'}, 'external_lms': {'type': 'json'}, 'storage_bytes': {'type': 'bigint'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    space_kind = models.CharField(max_length=32, choices=[('class_subject', 'Class subject'), ('course_section', 'Course section'), ('staff_training', 'Staff training'), ('programme', 'Programme'), ('community', 'Community')])
    class_subject_plan = models.ForeignKey("academic.ClassSubjectPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_subject_plan_id', null=True, blank=True)
    course_section = models.ForeignKey("academic.CourseSection", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_section_id', null=True, blank=True)
    title = models.CharField(max_length=300)
    owner_staff_id = cf.UUID7Field()
    external_lms = models.JSONField(null=True, blank=True, help_text='LTI 1.3 / OneRoster link where an external LMS is used')
    storage_bytes = models.BigIntegerField(default=0, help_text='5 GB per institution per session included')
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
        db_table = 'course_space'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'LMS course space for a class-subject, course section or staff training course (a'


class DigitalSkillLevel(CedaModel):
    """Digital-skills level per person and strand (device use, information literacy, communication, content creation, safety, computational thinking)"""

    ceda_entity = 'digital_skill_level'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = "derived: the person's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'person_kind': {'type': 'enum', 'enum': 'person_kind'}, 'person_id': {'type': 'uuid'}, 'strand': {'type': 'cl', 'code_list': 'digital_strand'}, 'level': {'type': 'smallint'}, 'evidence': {'type': 'json'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')])
    person_id = cf.UUID7Field()
    strand = models.CharField(max_length=32)
    level = models.SmallIntegerField()
    evidence = models.JSONField(null=True, blank=True, help_text='LMS activity evidence')
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
        db_table = 'digital_skill_level'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Digital-skills level per person and strand (device use, information literacy, co'


class DiscussionPost(CedaModel):
    """Moderated discussion post (under-13s only in teacher-moderated threads; no private learner-to-learner messages)"""

    ceda_entity = 'discussion_post'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the course space'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'course_space_id': {'type': 'ref', 'ref': 'course_space'}, 'thread_ref': {'type': 'uuid'}, 'author_kind': {'type': 'enum', 'enum': 'course_member_kind'}, 'author_id': {'type': 'uuid'}, 'body': {'type': 'text'}, 'moderation': {'type': 'enum', 'enum': 'moderation_state'}, 'posted_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    course_space = models.ForeignKey("lms.CourseSpace", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_space_id')
    thread_ref = cf.UUID7Field()
    author_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('staff', 'Staff')])
    author_id = cf.UUID7Field()
    body = models.TextField()
    moderation = models.CharField(max_length=32, choices=[('visible', 'Visible'), ('pending_moderation', 'Pending moderation'), ('hidden', 'Hidden'), ('removed', 'Removed')])
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'discussion_post'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Moderated discussion post (under-13s only in teacher-moderated threads; no priva'


class Extension(CedaModel):
    """Individual extension with reason (no lateness flag before the extended date)"""

    ceda_entity = 'extension'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'assignment_id': {'type': 'ref', 'ref': 'assignment'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'new_due_at': {'type': 'ts'}, 'reason': {'type': 'str'}, 'granted_by': {'type': 'ref', 'ref': 'staff'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    assignment = models.ForeignKey("lms.Assignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assignment_id')
    learner_id = cf.UUID7Field()
    new_due_at = models.DateTimeField()
    reason = models.CharField(max_length=500)
    granted_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'extension'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Individual extension with reason (no lateness flag before the extended date)'


class HomeworkLimit(CedaModel):
    """Nightly homework timetable and load limit for a class"""

    ceda_entity = 'homework_limit'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'weekday': {'type': 'smallint'}, 'max_items': {'type': 'smallint'}, 'subject_slots': {'type': 'json'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    weekday = models.SmallIntegerField()
    max_items = models.SmallIntegerField()
    subject_slots = models.JSONField(null=True, blank=True, help_text='Subjects expected that night')
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
        db_table = 'homework_limit'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Nightly homework timetable and load limit for a class'


class LiveClass(CedaModel):
    """Scheduled live video class (attendance to the register; recording only with consent)"""

    ceda_entity = 'live_class'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'course_space_id': {'type': 'ref', 'ref': 'course_space'}, 'lesson_occurrence_id': {'type': 'ref', 'ref': 'lesson_occurrence'}, 'starts_at': {'type': 'ts'}, 'provider_room_ref': {'type': 'str'}, 'recording_object_key': {'type': 'object_key'}, 'recording_consent_complete': {'type': 'bool'}, 'captions_object_key': {'type': 'object_key'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    course_space = models.ForeignKey("lms.CourseSpace", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_space_id')
    lesson_occurrence = models.ForeignKey("timetable.LessonOccurrence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lesson_occurrence_id', null=True, blank=True)
    starts_at = models.DateTimeField()
    provider_room_ref = models.CharField(max_length=200, null=True, blank=True)
    recording_object_key = models.CharField(max_length=1024, null=True, blank=True)
    recording_consent_complete = models.BooleanField(default=False)
    captions_object_key = models.CharField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'live_class'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Scheduled live video class (attendance to the register; recording only with cons'


class LmsContent(CedaModel):
    """Content item — note, file, video, audio, link, H5P interactive or state content-library item"""

    ceda_entity = 'lms_content'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'unit_id': {'type': 'ref', 'ref': 'lms_unit'}, 'content_kind': {'type': 'enum', 'enum': 'content_kind'}, 'title': {'type': 'title'}, 'body': {'type': 'text'}, 'object_key': {'type': 'object_key'}, 'size_bytes': {'type': 'bigint'}, 'library_item_id': {'type': 'ref', 'ref': 'content_library_item'}, 'node_ids': {'type': 'json'}, 'is_offline_pack': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    unit = models.ForeignKey("lms.LmsUnit", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='unit_id')
    content_kind = models.CharField(max_length=32, choices=[('note', 'Note'), ('file', 'File'), ('video', 'Video'), ('audio', 'Audio'), ('link', 'Link'), ('h5p', 'H5p'), ('library_item', 'Library item'), ('live_recording', 'Live recording')])
    title = models.CharField(max_length=300)
    body = models.TextField(null=True, blank=True)
    object_key = models.CharField(max_length=1024, null=True, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True, help_text='Data-cost estimate before download')
    library_item_id = cf.UUID7Field(null=True, blank=True)
    node_ids = models.JSONField(null=True, blank=True)
    is_offline_pack = models.BooleanField(default=True, help_text='Included in the weekly offline download')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'lms_content'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Content item — note, file, video, audio, link, H5P interactive or state content-'


class LmsUnit(CedaModel):
    """Unit (week or topic) of a course space generated from the scheme of work and tagged to objectives"""

    ceda_entity = 'lms_unit'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'course_space_id': {'type': 'ref', 'ref': 'course_space'}, 'title': {'type': 'title'}, 'sort_order': {'type': 'smallint'}, 'node_ids': {'type': 'json'}, 'scheme_week_id': {'type': 'ref', 'ref': 'scheme_week'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    course_space = models.ForeignKey("lms.CourseSpace", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='course_space_id')
    title = models.CharField(max_length=300)
    sort_order = models.SmallIntegerField()
    node_ids = models.JSONField(null=True, blank=True)
    scheme_week = models.ForeignKey("curriculum.SchemeWeek", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='scheme_week_id', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'lms_unit'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Unit (week or topic) of a course space generated from the scheme of work and tag'


class OriginalityReport(CedaModel):
    """Originality check result from the configured provider (shown to the teacher only; never an automatic penalty)"""

    ceda_entity = 'originality_report'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'submission_id': {'type': 'ref', 'ref': 'submission'}, 'provider': {'type': 'code'}, 'similarity_pct': {'type': 'pct'}, 'report_ref': {'type': 'str'}, 'checked_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    submission = models.ForeignKey("lms.Submission", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='submission_id')
    provider = models.CharField(max_length=40)
    similarity_pct = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    report_ref = models.CharField(max_length=500, null=True, blank=True)
    checked_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'originality_report'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Originality check result from the configured provider (shown to the teacher only'


class Question(CedaModel):
    """Question-bank item owned by a department or the state (with difficulty and discrimination statistics)"""

    ceda_entity = 'question'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'bank_code': {'type': 'code'}, 'item_kind': {'type': 'enum', 'enum': 'question_kind'}, 'stem': {'type': 'text'}, 'options': {'type': 'json'}, 'answer_key_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'answer_key'}, 'node_ids': {'type': 'json'}, 'difficulty': {'type': 'ratio'}, 'discrimination': {'type': 'dec'}, 'qti_ref': {'type': 'str'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    bank_code = models.CharField(max_length=40)
    item_kind = models.CharField(max_length=32, choices=[('single_choice', 'Single choice'), ('multiple_choice', 'Multiple choice'), ('true_false', 'True false'), ('numeric', 'Numeric'), ('short_text', 'Short text'), ('essay', 'Essay'), ('matching', 'Matching')])
    stem = models.TextField()
    options = models.JSONField(null=True, blank=True)
    answer_key_enc = models.BinaryField(null=True, blank=True, help_text='Envelope-encrypted answer_key. Encrypted until the test closes')
    node_ids = models.JSONField(null=True, blank=True)
    difficulty = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    discrimination = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    qti_ref = models.CharField(max_length=200, null=True, blank=True, help_text='QTI 3.0 identifier')
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
        db_table = 'question'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Question-bank item owned by a department or the state (with difficulty and discr'


class QuizAttempt(CedaModel):
    """Online quiz or CBT attempt (randomised items, timing incl. extra-time adjustment, secure-mode, IP and device log)"""

    ceda_entity = 'quiz_attempt'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the assignment's course space"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'assignment_id': {'type': 'ref', 'ref': 'assignment'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'item_order': {'type': 'json'}, 'responses': {'type': 'json'}, 'time_allowed_minutes': {'type': 'minutes'}, 'started_at': {'type': 'ts'}, 'submitted_at': {'type': 'ts'}, 'device_log': {'type': 'json'}, 'auto_score': {'type': 'dec'}, 'invigilator_staff_id': {'type': 'ref', 'ref': 'staff'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    assignment = models.ForeignKey("lms.Assignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assignment_id')
    learner_id = cf.UUID7Field()
    item_order = models.JSONField()
    responses = models.JSONField(null=True, blank=True)
    time_allowed_minutes = models.IntegerField(help_text='Includes authorised extra time')
    started_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    device_log = models.JSONField(null=True, blank=True, help_text='Secure mode, IP, device')
    auto_score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    invigilator_staff_id = cf.UUID7Field(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'quiz_attempt'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Online quiz or CBT attempt (randomised items, timing incl. extra-time adjustment'


class Rubric(CedaModel):
    """Marking rubric (criteria and levels; digital-skills rubrics map to the framework)"""

    ceda_entity = 'rubric'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'criteria': {'type': 'json'}, 'framework_ref': {'type': 'code'}, 'version': {'type': 'int_u'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    criteria = models.JSONField(help_text='Criteria, levels, descriptors, points')
    framework_ref = models.CharField(max_length=60, null=True, blank=True, help_text='Digital-skills framework strand')
    version = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'rubric'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Marking rubric (criteria and levels; digital-skills rubrics map to the framework'


class Submission(CedaModel):
    """Learner submission version (hashed, timestamped receipt; device and sync times; AI-use declaration)"""

    ceda_entity = 'submission'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = "derived: the assignment's course space"
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'assignment_id': {'type': 'ref', 'ref': 'assignment'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'group_ref': {'type': 'code'}, 'version_no': {'type': 'smallint'}, 'is_draft': {'type': 'bool'}, 'text_body': {'type': 'text'}, 'device_submitted_at': {'type': 'ts'}, 'synced_at': {'type': 'ts'}, 'is_late': {'type': 'bool'}, 'receipt_hash': {'type': 'hash'}, 'ai_declaration': {'type': 'enum', 'enum': 'ai_declaration'}, 'source': {'type': 'enum', 'enum': 'submission_source'}, 'client_op_id': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    assignment = models.ForeignKey("lms.Assignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assignment_id')
    learner_id = cf.UUID7Field()
    group_ref = models.CharField(max_length=40, null=True, blank=True)
    version_no = models.SmallIntegerField()
    is_draft = models.BooleanField(default=False)
    text_body = models.TextField(null=True, blank=True)
    device_submitted_at = models.DateTimeField(null=True, blank=True, help_text='Device clock (offline work)')
    synced_at = models.DateTimeField(help_text='Server receipt time')
    is_late = models.BooleanField(help_text='Teacher decides when device and sync times straddle the due time')
    receipt_hash = models.BinaryField()
    ai_declaration = models.CharField(max_length=32, choices=[('none_used', 'None used'), ('used_acknowledged', 'Used acknowledged'), ('not_declared', 'Not declared')])
    source = models.CharField(max_length=32, choices=[('app', 'App'), ('web', 'Web'), ('scan_split', 'Scan split'), ('ussd_confirmation', 'Ussd confirmation'), ('offline_sync', 'Offline sync')], help_text='app, web, scan_split (QR cover sheet), ussd_confirmation')
    client_op_id = cf.UUID7Field(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'submission'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner submission version (hashed, timestamped receipt; device and sync times; '


class SubmissionFile(CedaModel):
    """File in a submission (compressed on upload; up to 200 MB per submission, configurable)"""

    ceda_entity = 'submission_file'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'submission_id': {'type': 'ref', 'ref': 'submission'}, 'object_key': {'type': 'object_key'}, 'mime_type': {'type': 'mime'}, 'size_bytes': {'type': 'bigint'}, 'sha256': {'type': 'hash'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    submission = models.ForeignKey("lms.Submission", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='submission_id')
    object_key = models.CharField(max_length=1024)
    mime_type = models.CharField(max_length=127)
    size_bytes = models.BigIntegerField()
    sha256 = models.BinaryField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'submission_file'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'File in a submission (compressed on upload; up to 200 MB per submission, configu'


class SubmissionMark(CedaModel):
    """Mark and feedback for a submission (rubric, comments, annotations, audio feedback; auto-marked items)"""

    ceda_entity = 'submission_mark'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LMS'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'submission_id': {'type': 'ref', 'ref': 'submission'}, 'marker_staff_id': {'type': 'ref', 'ref': 'staff'}, 'score': {'type': 'dec'}, 'rubric_levels': {'type': 'json'}, 'feedback': {'type': 'text'}, 'annotation_object_key': {'type': 'object_key'}, 'audio_feedback_object_key': {'type': 'object_key'}, 'objective_results': {'type': 'json'}, 'is_auto_marked': {'type': 'bool'}, 'released_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    submission = models.ForeignKey("lms.Submission", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='submission_id')
    marker_staff_id = cf.UUID7Field()
    score = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    rubric_levels = models.JSONField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    annotation_object_key = models.CharField(max_length=1024, null=True, blank=True)
    audio_feedback_object_key = models.CharField(max_length=1024, null=True, blank=True)
    objective_results = models.JSONField(null=True, blank=True)
    is_auto_marked = models.BooleanField(default=False)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'submission_mark'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'Mark and feedback for a submission (rubric, comments, annotations, audio feedbac'


class UssdSession(CedaModel):
    """USSD/SMS feature-phone interaction (due dates, completion confirmation)"""

    ceda_entity = 'ussd_session'
    ceda_zones = ('ops',)
    ceda_domain = 'LMS'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'msisdn_hmac': {'type': 'hmac'}, 'action': {'type': 'enum', 'enum': 'ussd_action'}, 'assignment_id': {'type': 'ref', 'ref': 'assignment'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field(null=True, blank=True)
    msisdn_hmac = models.BinaryField()
    action = models.CharField(max_length=32, choices=[('list_due', 'List due'), ('confirm_completed', 'Confirm completed'), ('help', 'Help')])
    assignment = models.ForeignKey("lms.Assignment", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='assignment_id', null=True, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'ussd_session'
        app_label = 'lms'
        base_manager_name = 'unscoped'
        verbose_name = 'USSD/SMS feature-phone interaction (due dates, completion confirmation)'
