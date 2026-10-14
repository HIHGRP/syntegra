"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``success`` — Behaviour, rewards, seating plans and influences, intelligence events, detentions, on-call and on-report; SEND and inclusion, gifted and talented, wellbeing, interventions and personal learning plans.
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



class Adjustment(CedaModel):
    """Authorised reasonable adjustment — the teacher-visible layer (extra time, large print, read-aloud, seating, access arrangements)"""

    ceda_entity = 'adjustment'
    ceda_zones = ('ops',)
    ceda_domain = 'SEN'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = "derived: the learner's classes"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'adjustment_kind': {'type': 'cl', 'code_list': 'adjustment_kind'}, 'parameters': {'type': 'json'}, 'applies_to': {'type': 'json'}, 'authorised_by': {'type': 'uuid'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    adjustment_kind = models.CharField(max_length=32)
    parameters = models.JSONField(null=True, blank=True, help_text='e.g. extra_time_pct 25, font_scale 1.5')
    applies_to = models.JSONField(help_text='lessons, assessments, exams, lms, rooms')
    authorised_by = cf.UUID7Field()
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
        db_table = 'adjustment'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Authorised reasonable adjustment — the teacher-visible layer (extra time, large '


class BadgeAward(CedaModel):
    """Badge awarded to a learner"""

    ceda_entity = 'badge_award'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'badge_id': {'type': 'ref', 'ref': 'reward_badge'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'awarded_at': {'type': 'ts'}, 'source': {'type': 'enum', 'enum': 'badge_source'}, 'intel_firing_id': {'type': 'ref', 'ref': 'intel_firing'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    badge = models.ForeignKey("success.RewardBadge", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='badge_id')
    learner_id = cf.UUID7Field()
    awarded_at = models.DateTimeField()
    source = models.CharField(max_length=32, choices=[('points_threshold', 'Points threshold'), ('rule', 'Rule'), ('staff_award', 'Staff award'), ('activity', 'Activity')])
    intel_firing = models.ForeignKey("success.IntelFiring", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='intel_firing_id', null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'badge_award'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Badge awarded to a learner'


class BehaviourEvent(CedaModel):
    """Behaviour log entry (two taps from register, class list, seating plan or app; online or offline)"""

    ceda_entity = 'behaviour_event'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'behaviour_type_id': {'type': 'ref', 'ref': 'behaviour_type'}, 'points': {'type': 'smallint'}, 'lesson_occurrence_id': {'type': 'ref', 'ref': 'lesson_occurrence'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'location': {'type': 'str'}, 'occurred_at': {'type': 'ts'}, 'recorded_by_staff_id': {'type': 'ref', 'ref': 'staff'}, 'description': {'type': 'str'}, 'target_learner_ids': {'type': 'json'}, 'outcome': {'type': 'enum', 'enum': 'behaviour_outcome'}, 'decision_by': {'type': 'uuid'}, 'appeal_status': {'type': 'enum', 'enum': 'appeal_status'}, 'client_op_id': {'type': 'uuid'}, 'reversed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    behaviour_type = models.ForeignKey("success.BehaviourType", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='behaviour_type_id')
    points = models.SmallIntegerField(help_text='Points of the policy version in force')
    lesson_occurrence = models.ForeignKey("timetable.LessonOccurrence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lesson_occurrence_id', null=True, blank=True)
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    location = models.CharField(max_length=120, null=True, blank=True)
    occurred_at = models.DateTimeField()
    recorded_by_staff_id = cf.UUID7Field()
    description = models.CharField(max_length=2000, null=True, blank=True)
    target_learner_ids = models.JSONField(null=True, blank=True, help_text='Targets of bullying (routes to the pastoral lead)')
    outcome = models.CharField(max_length=32, choices=[('none', 'None'), ('warning', 'Warning'), ('detention', 'Detention'), ('on_report', 'On report'), ('parent_contact', 'Parent contact'), ('intervention', 'Intervention'), ('internal_exclusion', 'Internal exclusion'), ('suspension', 'Suspension'), ('exclusion', 'Exclusion')], null=True, blank=True)
    decision_by = cf.UUID7Field(null=True, blank=True, help_text='Head for outcomes above detention')
    appeal_status = models.CharField(max_length=32, choices=[('none', 'None'), ('lodged', 'Lodged'), ('upheld', 'Upheld'), ('dismissed', 'Dismissed')], null=True, blank=True)
    client_op_id = cf.UUID7Field(null=True, blank=True, help_text='Offline idempotency key')
    reversed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'behaviour_event'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Behaviour log entry (two taps from register, class list, seating plan or app; on'


class BehaviourFramework(CedaModel):
    """State minimum behaviour framework (required categories, maximum points, head-decision outcomes)"""

    ceda_entity = 'behaviour_framework'
    ceda_zones = ('registry',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'version': {'type': 'int_u'}, 'required_categories': {'type': 'json'}, 'max_points_per_event': {'type': 'smallint'}, 'head_decision_outcomes': {'type': 'json'}, 'after_school_detention_rule': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'effective_from': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    version = models.PositiveIntegerField()
    required_categories = models.JSONField()
    max_points_per_event = models.SmallIntegerField()
    head_decision_outcomes = models.JSONField(help_text='Outcomes above detention')
    after_school_detention_rule = models.JSONField(null=True, blank=True, help_text='Per-LGA permission and default parent notice (D21)')
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
        db_table = 'behaviour_framework'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'State minimum behaviour framework (required categories, maximum points, head-dec'


class BehaviourPolicy(CedaModel):
    """Versioned behaviour policy of an institution (immutable once published; never re-scores past events)"""

    ceda_entity = 'behaviour_policy'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'framework_version': {'type': 'int_u'}, 'version': {'type': 'int_u'}, 'missing_homework_is_behaviour': {'type': 'bool'}, 'effective_from': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    framework_version = models.PositiveIntegerField(help_text='State framework version it conforms to')
    version = models.PositiveIntegerField()
    missing_homework_is_behaviour = models.BooleanField(default=False)
    effective_from = models.DateField()
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
        db_table = 'behaviour_policy'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Versioned behaviour policy of an institution (immutable once published; never re'


class BehaviourType(CedaModel):
    """Positive or negative behaviour with icon, points, default outcome and use in reports/influences"""

    ceda_entity = 'behaviour_type'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'policy_id': {'type': 'ref', 'ref': 'behaviour_policy'}, 'code': {'type': 'code'}, 'label': {'type': 'title'}, 'polarity': {'type': 'enum', 'enum': 'polarity'}, 'category': {'type': 'cl', 'code_list': 'behaviour_category'}, 'points': {'type': 'smallint'}, 'icon': {'type': 'code'}, 'default_outcome': {'type': 'enum', 'enum': 'behaviour_outcome'}, 'detention_type_id': {'type': 'ref', 'ref': 'detention_type'}, 'counts_in_reports': {'type': 'bool'}, 'counts_in_influences': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    policy = models.ForeignKey("success.BehaviourPolicy", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='policy_id')
    code = models.CharField(max_length=32)
    label = models.CharField(max_length=300)
    polarity = models.CharField(max_length=32, choices=[('positive', 'Positive'), ('negative', 'Negative')])
    category = models.CharField(max_length=32, help_text='bullying, violence, lateness, positive conduct …')
    points = models.SmallIntegerField()
    icon = models.CharField(max_length=40, null=True, blank=True)
    default_outcome = models.CharField(max_length=32, choices=[('none', 'None'), ('warning', 'Warning'), ('detention', 'Detention'), ('on_report', 'On report'), ('parent_contact', 'Parent contact'), ('intervention', 'Intervention'), ('internal_exclusion', 'Internal exclusion'), ('suspension', 'Suspension'), ('exclusion', 'Exclusion')], null=True, blank=True)
    detention_type = models.ForeignKey("success.DetentionType", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='detention_type_id', null=True, blank=True)
    counts_in_reports = models.BooleanField(default=True)
    counts_in_influences = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'behaviour_type'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Positive or negative behaviour with icon, points, default outcome and use in rep'


class Detention(CedaModel):
    """Detention session and attendance (Attended, Pending, Not attended, Escalated)"""

    ceda_entity = 'detention'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'detention_type_id': {'type': 'ref', 'ref': 'detention_type'}, 'behaviour_event_id': {'type': 'ref', 'ref': 'behaviour_event'}, 'intel_firing_id': {'type': 'ref', 'ref': 'intel_firing'}, 'escalated_from_id': {'type': 'ref', 'ref': 'detention'}, 'scheduled_at': {'type': 'ts'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'supervisor_staff_id': {'type': 'ref', 'ref': 'staff'}, 'parent_notified_at': {'type': 'ts'}, 'transport_checked': {'type': 'bool'}, 'minutes_owed': {'type': 'minutes'}, 'attendance': {'type': 'enum', 'enum': 'detention_attendance'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    detention_type = models.ForeignKey("success.DetentionType", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='detention_type_id')
    behaviour_event = models.ForeignKey("success.BehaviourEvent", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='behaviour_event_id', null=True, blank=True)
    intel_firing = models.ForeignKey("success.IntelFiring", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='intel_firing_id', null=True, blank=True)
    escalated_from = models.ForeignKey("success.Detention", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='escalated_from_id', null=True, blank=True)
    scheduled_at = models.DateTimeField()
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    supervisor_staff_id = cf.UUID7Field(null=True, blank=True)
    parent_notified_at = models.DateTimeField(null=True, blank=True)
    transport_checked = models.BooleanField(default=False)
    minutes_owed = models.IntegerField()
    attendance = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('attended', 'Attended'), ('not_attended', 'Not attended'), ('escalated', 'Escalated'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'detention'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Detention session and attendance (Attended, Pending, Not attended, Escalated)'


class DetentionType(CedaModel):
    """Detention level in the institution ladder (duration, default room and supervisor, escalation to next level)"""

    ceda_entity = 'detention_type'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'ladder_level': {'type': 'smallint'}, 'duration_minutes': {'type': 'minutes'}, 'default_room_id': {'type': 'ref', 'ref': 'room'}, 'default_supervisor_staff_id': {'type': 'ref', 'ref': 'staff'}, 'is_after_school': {'type': 'bool'}, 'parent_notice_hours': {'type': 'smallint'}, 'next_level_id': {'type': 'ref', 'ref': 'detention_type'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300, help_text='Lunchtime, Head of year, Senior leadership')
    ladder_level = models.SmallIntegerField()
    duration_minutes = models.IntegerField()
    default_room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='default_room_id', null=True, blank=True)
    default_supervisor_staff_id = cf.UUID7Field(null=True, blank=True)
    is_after_school = models.BooleanField(default=False)
    parent_notice_hours = models.SmallIntegerField(default=24)
    next_level = models.ForeignKey("success.DetentionType", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='next_level_id', null=True, blank=True)
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
        db_table = 'detention_type'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Detention level in the institution ladder (duration, default room and supervisor'


class ExternalReferral(CedaModel):
    """Therapy or external-agency referral (speech, occupational, educational psychology, health) with consent and returned reports"""

    ceda_entity = 'external_referral'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'transaction'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'agency_kind': {'type': 'cl', 'code_list': 'referral_agency'}, 'agency_name': {'type': 'str'}, 'consent_record_id': {'type': 'uuid'}, 'referred_on': {'type': 'date'}, 'report_document_id': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'referral_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    agency_kind = models.CharField(max_length=32)
    agency_name = models.CharField(max_length=200)
    consent_record_id = cf.UUID7Field(help_text='Consent (ops)')
    referred_on = models.DateField()
    report_document_id = cf.UUID7Field(null=True, blank=True, help_text='Returned report stored in the support profile')
    status = models.CharField(max_length=32, choices=[('drafted', 'Drafted'), ('sent', 'Sent'), ('acknowledged', 'Acknowledged'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('closed', 'Closed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'external_referral'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Therapy or external-agency referral (speech, occupational, educational psycholog'


class GiftedRegisterEntry(CedaModel):
    """Gifted and talented register entry with provision tracking"""

    ceda_entity = 'gifted_register_entry'
    ceda_zones = ('ops',)
    ceda_domain = 'SEN'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'domain_area': {'type': 'cl', 'code_list': 'gifted_domain'}, 'evidence': {'type': 'str'}, 'provision_note': {'type': 'str'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    domain_area = models.CharField(max_length=32)
    evidence = models.CharField(max_length=1000, null=True, blank=True)
    provision_note = models.CharField(max_length=1000, null=True, blank=True)
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
        db_table = 'gifted_register_entry'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Gifted and talented register entry with provision tracking'


class InfluenceScore(CedaModel):
    """Pairwise influence between two learners from behaviour in shared lessons (adjacent vs apart; ≥ 20 events)"""

    ceda_entity = 'influence_score'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'projection'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'derived: the class; visible only to its teachers and pastoral staff'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'learner_a_id': {'type': 'ref', 'ref': 'learner'}, 'learner_b_id': {'type': 'ref', 'ref': 'learner'}, 'shared_events': {'type': 'int_u'}, 'negative_adjacent': {'type': 'int_u'}, 'negative_apart': {'type': 'int_u'}, 'positive_adjacent': {'type': 'int_u'}, 'positive_apart': {'type': 'int_u'}, 'computed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    learner_a_id = cf.UUID7Field()
    learner_b_id = cf.UUID7Field()
    shared_events = models.PositiveIntegerField()
    negative_adjacent = models.PositiveIntegerField()
    negative_apart = models.PositiveIntegerField()
    positive_adjacent = models.PositiveIntegerField()
    positive_apart = models.PositiveIntegerField()
    computed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'influence_score'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Pairwise influence between two learners from behaviour in shared lessons (adjace'


class IntelFiring(CedaModel):
    """Each time an intelligence rule fires (append-only; staff may reverse its effects)"""

    ceda_entity = 'intel_firing'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'rule_id': {'type': 'ref', 'ref': 'intel_rule'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'evidence': {'type': 'json'}, 'actions_taken': {'type': 'json'}, 'agent_action_id': {'type': 'ref', 'ref': 'agent_action'}, 'fired_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    rule = models.ForeignKey("success.IntelRule", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='rule_id')
    learner_id = cf.UUID7Field()
    evidence = models.JSONField()
    actions_taken = models.JSONField()
    agent_action_id = cf.UUID7Field(null=True, blank=True, help_text='Behaviour agent action')
    fired_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'intel_firing'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Each time an intelligence rule fires (append-only; staff may reverse its effects'


class IntelFiringReversal(CedaModel):
    """Staff reversal of an intelligence-rule firing's effects"""

    ceda_entity = 'intel_firing_reversal'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'firing_id': {'type': 'ref', 'ref': 'intel_firing'}, 'reversed_by': {'type': 'uuid'}, 'reason': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    firing = models.ForeignKey("success.IntelFiring", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='firing_id')
    reversed_by = cf.UUID7Field()
    reason = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'intel_firing_reversal'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = "Staff reversal of an intelligence-rule firing's effects"


class IntelRule(CedaModel):
    """Threshold rule over behaviour, attendance, homework or wellbeing data with actions (simulated before activation)"""

    ceda_entity = 'intel_rule'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'source_data': {'type': 'enum', 'enum': 'intel_source'}, 'rule_expression': {'type': 'json'}, 'actions': {'type': 'json'}, 'is_positive_milestone': {'type': 'bool'}, 'simulation_result': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    source_data = models.CharField(max_length=32, choices=[('behaviour', 'Behaviour'), ('attendance', 'Attendance'), ('homework', 'Homework'), ('wellbeing', 'Wellbeing'), ('mixed', 'Mixed')])
    rule_expression = models.JSONField(help_text='e.g. 10 negative events in 7 days; 100 positive points')
    actions = models.JSONField(help_text='notify, message_parent, detention, on_report, intervention, badge, dsl_alert')
    is_positive_milestone = models.BooleanField(default=False)
    simulation_result = models.JSONField(null=True, blank=True, help_text='Learners who would have triggered in the last 30 days')
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
        db_table = 'intel_rule'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Threshold rule over behaviour, attendance, homework or wellbeing data with actio'


class Intervention(CedaModel):
    """Intervention with baseline, target, learners, lead, review date and outcome (closed loop)"""

    ceda_entity = 'intervention'
    ceda_zones = ('ops',)
    ceda_domain = 'SEN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'intervention_kind': {'type': 'cl', 'code_list': 'intervention_kind'}, 'lead_staff_id': {'type': 'ref', 'ref': 'staff'}, 'learner_ids': {'type': 'json'}, 'baseline': {'type': 'json'}, 'target': {'type': 'json'}, 'review_on': {'type': 'date'}, 'outcome': {'type': 'json'}, 'effect_estimate': {'type': 'json'}, 'recommendation_id': {'type': 'ref', 'ref': 'recommendation'}, 'cost_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'intervention_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    intervention_kind = models.CharField(max_length=32)
    lead_staff_id = cf.UUID7Field()
    learner_ids = models.JSONField(help_text='Participants (≤ a class; larger groups use cohorts)')
    baseline = models.JSONField()
    target = models.JSONField()
    review_on = models.DateField()
    outcome = models.JSONField(null=True, blank=True)
    effect_estimate = models.JSONField(null=True, blank=True, help_text='Outcome against target and counterfactual trend')
    recommendation = models.ForeignKey("intelligence.Recommendation", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='recommendation_id', null=True, blank=True)
    cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('planned', 'Planned'), ('active', 'Active'), ('review_due', 'Review due'), ('closed_success', 'Closed success'), ('closed_partial', 'Closed partial'), ('closed_no_effect', 'Closed no effect'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'intervention'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Intervention with baseline, target, learners, lead, review date and outcome (clo'


class LearningPlan(CedaModel):
    """Personal learning plan for a learner (any learner, not only SEND)"""

    ceda_entity = 'learning_plan'
    ceda_zones = ('ops',)
    ceda_domain = 'SEN'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'template_id': {'type': 'ref', 'ref': 'learning_plan_template'}, 'template_version': {'type': 'int_u'}, 'owner_staff_id': {'type': 'ref', 'ref': 'staff'}, 'next_review_on': {'type': 'date'}, 'time_spent_minutes': {'type': 'minutes'}, 'cost_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'plan_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    template = models.ForeignKey("success.LearningPlanTemplate", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='template_id', null=True, blank=True)
    template_version = models.PositiveIntegerField(null=True, blank=True)
    owner_staff_id = cf.UUID7Field()
    next_review_on = models.DateField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(null=True, blank=True)
    cost_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
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
        db_table = 'learning_plan'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Personal learning plan for a learner (any learner, not only SEND)'


class LearningPlanEntry(CedaModel):
    """Action, learner reflection, parent comment, evidence or review on a learning plan (append-only)"""

    ceda_entity = 'learning_plan_entry'
    ceda_zones = ('ops',)
    ceda_domain = 'SEN'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'plan_id': {'type': 'ref', 'ref': 'learning_plan'}, 'goal_id': {'type': 'ref', 'ref': 'learning_plan_goal'}, 'entry_kind': {'type': 'enum', 'enum': 'plan_entry_kind'}, 'author_kind': {'type': 'enum', 'enum': 'comment_author'}, 'author_id': {'type': 'uuid'}, 'body': {'type': 'text'}, 'evidence_ref': {'type': 'json'}, 'owner_staff_id': {'type': 'ref', 'ref': 'staff'}, 'due_on': {'type': 'date'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    plan = models.ForeignKey("success.LearningPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='plan_id')
    goal = models.ForeignKey("success.LearningPlanGoal", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='goal_id', null=True, blank=True)
    entry_kind = models.CharField(max_length=32, choices=[('action', 'Action'), ('learner_reflection', 'Learner reflection'), ('parent_comment', 'Parent comment'), ('evidence', 'Evidence'), ('review', 'Review'), ('note', 'Note')])
    author_kind = models.CharField(max_length=32, choices=[('teacher', 'Teacher'), ('owner', 'Owner'), ('parent', 'Parent'), ('learner', 'Learner'), ('staff', 'Staff')])
    author_id = cf.UUID7Field()
    body = models.TextField()
    evidence_ref = models.JSONField(null=True, blank=True, help_text='LMS submission or assessment result')
    owner_staff_id = cf.UUID7Field(null=True, blank=True, help_text='Owner of an action')
    due_on = models.DateField(null=True, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'learning_plan_entry'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Action, learner reflection, parent comment, evidence or review on a learning pla'


class LearningPlanGoal(CedaModel):
    """Goal in a learning plan linked to curriculum objectives and target grades"""

    ceda_entity = 'learning_plan_goal'
    ceda_zones = ('ops',)
    ceda_domain = 'SEN'
    ceda_kind = 'config'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'plan_id': {'type': 'ref', 'ref': 'learning_plan'}, 'goal_text': {'type': 'str'}, 'node_ids': {'type': 'json'}, 'target_grade_id': {'type': 'ref', 'ref': 'target_grade'}, 'status': {'type': 'enum', 'enum': 'goal_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    plan = models.ForeignKey("success.LearningPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='plan_id')
    goal_text = models.CharField(max_length=1000)
    node_ids = models.JSONField(null=True, blank=True, help_text='Curriculum objectives')
    target_grade = models.ForeignKey("assessment.TargetGrade", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='target_grade_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('not_started', 'Not started'), ('in_progress', 'In progress'), ('achieved', 'Achieved'), ('partly_achieved', 'Partly achieved'), ('not_achieved', 'Not achieved'), ('dropped', 'Dropped')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'learning_plan_goal'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Goal in a learning plan linked to curriculum objectives and target grades'


class LearningPlanTemplate(CedaModel):
    """Reusable personal learning plan template (state or institution; catch-up, re-entry, gifted extension, exam readiness, TVET pathway)"""

    ceda_entity = 'learning_plan_template'
    ceda_zones = ('ops',)
    ceda_domain = 'SEN'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'content': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    content = models.JSONField()
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
        db_table = 'learning_plan_template'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Reusable personal learning plan template (state or institution; catch-up, re-ent'


class OnReportCard(CedaModel):
    """Learner on report for a period at tutor, head-of-year or senior-leadership level"""

    ceda_entity = 'on_report_card'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'level': {'type': 'enum', 'enum': 'report_level'}, 'owner_staff_id': {'type': 'ref', 'ref': 'staff'}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'outcome': {'type': 'str'}, 'intervention_id': {'type': 'ref', 'ref': 'intervention'}, 'status': {'type': 'enum', 'enum': 'on_report_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    level = models.CharField(max_length=32, choices=[('tutor', 'Tutor'), ('head_of_year', 'Head of year'), ('senior_leadership', 'Senior leadership')])
    owner_staff_id = cf.UUID7Field()
    starts_on = models.DateField()
    ends_on = models.DateField()
    outcome = models.CharField(max_length=1000, null=True, blank=True)
    intervention = models.ForeignKey("success.Intervention", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='intervention_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('completed', 'Completed'), ('ended_early', 'Ended early')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'on_report_card'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner on report for a period at tutor, head-of-year or senior-leadership level'


class OnReportRating(CedaModel):
    """Rating and comment for a target in one lesson, or a parent or learner comment (append-only)"""

    ceda_entity = 'on_report_rating'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'card_id': {'type': 'ref', 'ref': 'on_report_card'}, 'target_id': {'type': 'ref', 'ref': 'on_report_target'}, 'lesson_occurrence_id': {'type': 'ref', 'ref': 'lesson_occurrence'}, 'author_kind': {'type': 'enum', 'enum': 'comment_author'}, 'author_id': {'type': 'uuid'}, 'rating': {'type': 'smallint'}, 'comment': {'type': 'str'}, 'rated_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    card = models.ForeignKey("success.OnReportCard", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='card_id')
    target = models.ForeignKey("success.OnReportTarget", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='target_id', null=True, blank=True)
    lesson_occurrence = models.ForeignKey("timetable.LessonOccurrence", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='lesson_occurrence_id', null=True, blank=True)
    author_kind = models.CharField(max_length=32, choices=[('teacher', 'Teacher'), ('owner', 'Owner'), ('parent', 'Parent'), ('learner', 'Learner'), ('staff', 'Staff')])
    author_id = cf.UUID7Field()
    rating = models.SmallIntegerField(null=True, blank=True)
    comment = models.CharField(max_length=1000, null=True, blank=True)
    rated_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'on_report_rating'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Rating and comment for a target in one lesson, or a parent or learner comment (a'


class OnReportTarget(CedaModel):
    """Personalised target on an on-report card"""

    ceda_entity = 'on_report_target'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'card_id': {'type': 'ref', 'ref': 'on_report_card'}, 'target_text': {'type': 'str'}, 'sort_order': {'type': 'smallint'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    card = models.ForeignKey("success.OnReportCard", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='card_id')
    target_text = models.CharField(max_length=300)
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
        db_table = 'on_report_target'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Personalised target on an on-report card'


class OncallRequest(CedaModel):
    """On-call request raised from a classroom (routed to the rota; acknowledgement target 2 min; emergency reason)"""

    ceda_entity = 'oncall_request'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'raised_by_staff_id': {'type': 'ref', 'ref': 'staff'}, 'reason': {'type': 'enum', 'enum': 'oncall_reason'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'responder_staff_id': {'type': 'ref', 'ref': 'staff'}, 'raised_at': {'type': 'ts'}, 'acknowledged_at': {'type': 'ts'}, 'escalated_at': {'type': 'ts'}, 'resolved_at': {'type': 'ts'}, 'outcome': {'type': 'str'}, 'status': {'type': 'enum', 'enum': 'oncall_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id', null=True, blank=True)
    raised_by_staff_id = cf.UUID7Field()
    reason = models.CharField(max_length=32, choices=[('behaviour', 'Behaviour'), ('medical', 'Medical'), ('safeguarding', 'Safeguarding'), ('emergency', 'Emergency'), ('other', 'Other')])
    learner_id = cf.UUID7Field(null=True, blank=True)
    responder_staff_id = cf.UUID7Field(null=True, blank=True)
    raised_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    outcome = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('raised', 'Raised'), ('acknowledged', 'Acknowledged'), ('escalated', 'Escalated'), ('resolved', 'Resolved'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'oncall_request'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'On-call request raised from a classroom (routed to the rota; acknowledgement tar'


class Provision(CedaModel):
    """Provision type offered (type, staff, hours, cost) for the provision map"""

    ceda_entity = 'provision'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'config'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'provision_kind': {'type': 'cl', 'code_list': 'provision_kind'}, 'staff_ids': {'type': 'json'}, 'hours_per_week': {'type': 'dec'}, 'cost_per_term_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    provision_kind = models.CharField(max_length=32)
    staff_ids = models.JSONField(null=True, blank=True)
    hours_per_week = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cost_per_term_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
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
        db_table = 'provision'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Provision type offered (type, staff, hours, cost) for the provision map'


class ProvisionAllocation(CedaModel):
    """Learner allocated to a provision, with impact measured"""

    ceda_entity = 'provision_allocation'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'link'
    ceda_class = 'special'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'provision_id': {'type': 'ref', 'ref': 'provision'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'impact': {'type': 'sealed', 'class': 'special'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    provision = models.ForeignKey("success.Provision", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='provision_id')
    learner_id = cf.UUID7Field()
    impact = models.BinaryField(null=True, blank=True)
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
        db_table = 'provision_allocation'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Learner allocated to a provision, with impact measured'


class RewardBadge(CedaModel):
    """Achievement badge awarded at a points threshold or by rule (recognition only; never a credential)"""

    ceda_entity = 'reward_badge'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'label': {'type': 'title'}, 'rule': {'type': 'json'}, 'image_ref': {'type': 'object_key'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32)
    label = models.CharField(max_length=300)
    rule = models.JSONField(help_text='Points threshold or rule')
    image_ref = models.CharField(max_length=1024, null=True, blank=True)
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
        db_table = 'reward_badge'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Achievement badge awarded at a points threshold or by rule (recognition only; ne'


class RoomLayout(CedaModel):
    """Reusable room desk layout for seating plans"""

    ceda_entity = 'room_layout'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'name': {'type': 'str'}, 'desks': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id')
    name = models.CharField(max_length=80)
    desks = models.JSONField(help_text='Desk positions and labels')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'room_layout'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Reusable room desk layout for seating plans'


class SeatingFieldSet(CedaModel):
    """Set of up to 16 learner data fields shown on seating plans for a class, subject or level"""

    ceda_entity = 'seating_field_set'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'none'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'str'}, 'applies_to': {'type': 'json'}, 'fields': {'type': 'json'}, 'board_safe_fields': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=80)
    applies_to = models.JSONField(help_text='Class, subject or level')
    fields = models.JSONField(help_text='Up to 16 field codes (SEND, free meals/CCT, gifted, working and target grade RAG, attendance, home language)')
    board_safe_fields = models.JSONField(help_text='Fields still shown in board-safe view (never sensitive ones)')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'seating_field_set'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Set of up to 16 learner data fields shown on seating plans for a class, subject '


class SeatingPlan(CedaModel):
    """Seating plan for a class in a room (drag-and-drop or strategy-generated)"""

    ceda_entity = 'seating_plan'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the class'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'class_group_id': {'type': 'ref', 'ref': 'class_group'}, 'subject_id': {'type': 'ref', 'ref': 'subject'}, 'room_layout_id': {'type': 'ref', 'ref': 'room_layout'}, 'field_set_id': {'type': 'ref', 'ref': 'seating_field_set'}, 'strategy': {'type': 'enum', 'enum': 'seating_strategy'}, 'placements': {'type': 'json'}, 'is_active': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    class_group = models.ForeignKey("academic.ClassGroup", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='class_group_id')
    subject_id = cf.UUID7Field(null=True, blank=True)
    room_layout = models.ForeignKey("success.RoomLayout", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_layout_id')
    field_set = models.ForeignKey("success.SeatingFieldSet", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='field_set_id', null=True, blank=True)
    strategy = models.CharField(max_length=32, choices=[('manual', 'Manual'), ('ability', 'Ability'), ('mixed_ability', 'Mixed ability'), ('alphabetical', 'Alphabetical'), ('random', 'Random'), ('separate_negative_influences', 'Separate negative influences')], null=True, blank=True)
    placements = models.JSONField(help_text='Learner → desk')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'seating_plan'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Seating plan for a class in a room (drag-and-drop or strategy-generated)'


class SeatingPlanPrint(CedaModel):
    """Logged, watermarked print of a seating plan for observers or inspectors"""

    ceda_entity = 'seating_plan_print'
    ceda_zones = ('ops',)
    ceda_domain = 'BEH'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-BEH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'seating_plan_id': {'type': 'ref', 'ref': 'seating_plan'}, 'printed_by': {'type': 'uuid'}, 'viewer_name': {'type': 'name'}, 'printed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    seating_plan = models.ForeignKey("success.SeatingPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='seating_plan_id')
    printed_by = cf.UUID7Field()
    viewer_name = models.CharField(max_length=200, help_text='Watermarked on the print')
    printed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'seating_plan_print'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Logged, watermarked print of a seating plan for observers or inspectors'


class SendNeed(CedaModel):
    """Need area of a learner (coded; diagnosis detail encrypted)"""

    ceda_entity = 'send_need'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'master'
    ceda_class = 'special'
    ceda_history = 'effective'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'profile_id': {'type': 'ref', 'ref': 'send_profile'}, 'need_area': {'type': 'cl', 'code_list': 'send_need_area'}, 'is_primary': {'type': 'bool'}, 'detail': {'type': 'sealed', 'class': 'special'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    profile = models.ForeignKey("success.SendProfile", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='profile_id')
    need_area = models.CharField(max_length=32)
    is_primary = models.BooleanField(default=False)
    detail = models.BinaryField(null=True, blank=True)
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
        db_table = 'send_need'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Need area of a learner (coded; diagnosis detail encrypted)'


class SendProfile(CedaModel):
    """SEND 360 support profile (need areas, support level, plan type, strengths, communication, learner voice)"""

    ceda_entity = 'send_profile'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'master'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'support_level': {'type': 'cl', 'code_list': 'send_support_level'}, 'plan_type': {'type': 'cl', 'code_list': 'send_plan_type'}, 'profile': {'type': 'sealed', 'class': 'special'}, 'senco_user_id': {'type': 'uuid'}, 'review_due_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    support_level = models.CharField(max_length=32)
    plan_type = models.CharField(max_length=32, null=True, blank=True)
    profile = models.BinaryField(help_text='Strengths, needs, preferences, communication, strategies, assistive technology, learner and parent voice')
    senco_user_id = cf.UUID7Field(null=True, blank=True)
    review_due_on = models.DateField(null=True, blank=True)
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
        db_table = 'send_profile'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'SEND 360 support profile (need areas, support level, plan type, strengths, commu'


class SupportPlan(CedaModel):
    """IEP/ISP or statutory plan (outcomes, provision, participants, review cycle; overdue reviews alerted)"""

    ceda_entity = 'support_plan'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'transaction'
    ceda_class = 'special'
    ceda_history = 'versioned'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'profile_id': {'type': 'ref', 'ref': 'send_profile'}, 'plan_type': {'type': 'cl', 'code_list': 'send_plan_type'}, 'version': {'type': 'int_u'}, 'outcomes': {'type': 'sealed', 'class': 'special'}, 'participants': {'type': 'json'}, 'review_cycle_months': {'type': 'smallint'}, 'next_review_on': {'type': 'date'}, 'linked_learning_plan_id': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    profile = models.ForeignKey("success.SendProfile", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='profile_id')
    plan_type = models.CharField(max_length=32)
    version = models.PositiveIntegerField()
    outcomes = models.BinaryField()
    participants = models.JSONField(null=True, blank=True)
    review_cycle_months = models.SmallIntegerField()
    next_review_on = models.DateField()
    linked_learning_plan_id = cf.UUID7Field(null=True, blank=True, help_text='Personal learning plan (ops)')
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
        db_table = 'support_plan'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'IEP/ISP or statutory plan (outcomes, provision, participants, review cycle; over'


class SupportPlanReview(CedaModel):
    """Review of a support plan"""

    ceda_entity = 'support_plan_review'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'plan_id': {'type': 'ref', 'ref': 'support_plan'}, 'reviewed_on': {'type': 'date'}, 'notes': {'type': 'sealed', 'class': 'special'}, 'attendees': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    plan = models.ForeignKey("success.SupportPlan", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='plan_id')
    reviewed_on = models.DateField()
    notes = models.BinaryField()
    attendees = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'support_plan_review'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Review of a support plan'


class WellbeingCheckin(CedaModel):
    """Opt-in, age-appropriate wellbeing check-in or staff observation (five-point scale)"""

    ceda_entity = 'wellbeing_checkin'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'source': {'type': 'enum', 'enum': 'wellbeing_source'}, 'score': {'type': 'smallint'}, 'tracker_code': {'type': 'code'}, 'note': {'type': 'sealed', 'class': 'special'}, 'checked_in_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    source = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('parent', 'Parent'), ('staff', 'Staff')])
    score = models.SmallIntegerField()
    tracker_code = models.CharField(max_length=32, null=True, blank=True)
    note = models.BinaryField(null=True, blank=True)
    checked_in_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'wellbeing_checkin'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Opt-in, age-appropriate wellbeing check-in or staff observation (five-point scal'


class WellbeingConcern(CedaModel):
    """Wellbeing concern reported by a learner, parent or staff member (routed to a pastoral lead; DSL alert on keywords)"""

    ceda_entity = 'wellbeing_concern'
    ceda_zones = ('vault',)
    ceda_domain = 'SEN'
    ceda_kind = 'transaction'
    ceda_class = 'special'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-SEND'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'reported_by_kind': {'type': 'enum', 'enum': 'wellbeing_source'}, 'reported_by_id': {'type': 'uuid'}, 'concern_type': {'type': 'cl', 'code_list': 'wellbeing_concern_type'}, 'body': {'type': 'sealed', 'class': 'special'}, 'keyword_alert': {'type': 'bool'}, 'assigned_to': {'type': 'uuid'}, 'respond_by': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'queue_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    reported_by_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('parent', 'Parent'), ('staff', 'Staff')])
    reported_by_id = cf.UUID7Field(null=True, blank=True)
    concern_type = models.CharField(max_length=32, help_text='exam pressure, anxiety, bullying, friendships, family, sleep, online safety, food, transport')
    body = models.BinaryField()
    keyword_alert = models.BooleanField(default=False, help_text='Safeguarding keywords detected; DSL alerted')
    assigned_to = cf.UUID7Field(null=True, blank=True)
    respond_by = models.DateTimeField()
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
        db_table = 'wellbeing_concern'
        app_label = 'success'
        base_manager_name = 'unscoped'
        verbose_name = 'Wellbeing concern reported by a learner, parent or staff member (routed to a pas'
