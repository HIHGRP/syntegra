"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``sectors`` — Sector extensions.
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



class AccommodationAllocation(CedaModel):
    """Hostel accommodation application and allocation (accessibility needs considered)"""

    ceda_entity = 'accommodation_allocation'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'room_id': {'type': 'ref', 'ref': 'room'}, 'bed_label': {'type': 'code'}, 'has_accessibility_need': {'type': 'bool'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'status': {'type': 'enum', 'enum': 'allocation_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    period_id = cf.UUID7Field()
    room = models.ForeignKey("operations.Room", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_id', null=True, blank=True)
    bed_label = models.CharField(max_length=16, null=True, blank=True)
    has_accessibility_need = models.BooleanField(default=False)
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('proposed', 'Proposed'), ('approved', 'Approved'), ('published', 'Published'), ('applied', 'Applied'), ('allocated', 'Allocated'), ('waitlisted', 'Waitlisted'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'accommodation_allocation'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Hostel accommodation application and allocation (accessibility needs considered)'


class AdmissionApplication(CedaModel):
    """Admission application for a school place or tertiary programme (entry checks, O'Level verification, decisions, offers)"""

    ceda_entity = 'admission_application'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'programme_id': {'type': 'ref', 'ref': 'programme'}, 'education_level': {'type': 'cl', 'code_list': 'education_level'}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'applicant_name': {'type': 'name', 'pii': True}, 'applicant_dob': {'type': 'date', 'pii': True}, 'applicant_email': {'type': 'email', 'pii': True}, 'applicant_phone': {'type': 'phone', 'pii': True}, 'channel': {'type': 'enum', 'enum': 'application_channel'}, 'answers': {'type': 'json'}, 'olevel_verification': {'type': 'json'}, 'decision': {'type': 'enum', 'enum': 'admission_decision'}, 'decided_by': {'type': 'uuid'}, 'offer_expires_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'admission_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    programme_id = cf.UUID7Field(null=True, blank=True)
    education_level = models.CharField(max_length=32, null=True, blank=True)
    learner_id = cf.UUID7Field(null=True, blank=True, help_text='Matched or created at offer acceptance')
    applicant_name = models.CharField(max_length=200)
    applicant_dob = models.DateField(null=True, blank=True)
    applicant_email = models.CharField(max_length=254, null=True, blank=True)
    applicant_phone = models.CharField(max_length=16, null=True, blank=True)
    channel = models.CharField(max_length=32, choices=[('online', 'Online'), ('office', 'Office'), ('agent', 'Agent'), ('exam_body_adapter', 'Exam body adapter'), ('import', 'Import')])
    answers = models.JSONField()
    olevel_verification = models.JSONField(null=True, blank=True, help_text='Via Certificate 360 or exam-body adapters')
    decision = models.CharField(max_length=32, choices=[('offer', 'Offer'), ('conditional_offer', 'Conditional offer'), ('waitlist', 'Waitlist'), ('refuse', 'Refuse')], null=True, blank=True)
    decided_by = cf.UUID7Field(null=True, blank=True, help_text='Admission refusal is human-only')
    offer_expires_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('reviewing', 'Reviewing'), ('assessment', 'Assessment'), ('decided', 'Decided'), ('offer_accepted', 'Offer accepted'), ('enrolled', 'Enrolled'), ('declined', 'Declined'), ('withdrawn', 'Withdrawn')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'admission_application'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = "Admission application for a school place or tertiary programme (entry checks, O'"


class AdmissionEnquiry(CedaModel):
    """Admissions enquiry, open-day or visit booking, waiting list position (website widget posts here)"""

    ceda_entity = 'admission_enquiry'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-RECRUIT'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'contact_name': {'type': 'name', 'pii': True}, 'contact_phone': {'type': 'phone', 'pii': True}, 'contact_email': {'type': 'email', 'pii': True}, 'child_name': {'type': 'name', 'pii': True}, 'intended_level': {'type': 'cl', 'code_list': 'education_level'}, 'source': {'type': 'enum', 'enum': 'enquiry_source'}, 'visit_at': {'type': 'ts'}, 'waiting_list_position': {'type': 'int_u'}, 'application_id': {'type': 'ref', 'ref': 'admission_application'}, 'status': {'type': 'enum', 'enum': 'enquiry_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    contact_name = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=16, null=True, blank=True)
    contact_email = models.CharField(max_length=254, null=True, blank=True)
    child_name = models.CharField(max_length=200, null=True, blank=True)
    intended_level = models.CharField(max_length=32, null=True, blank=True)
    source = models.CharField(max_length=32, choices=[('website_widget', 'Website widget'), ('walk_in', 'Walk in'), ('phone', 'Phone'), ('whatsapp', 'Whatsapp'), ('open_day', 'Open day'), ('referral', 'Referral')])
    visit_at = models.DateTimeField(null=True, blank=True)
    waiting_list_position = models.PositiveIntegerField(null=True, blank=True)
    application = models.ForeignKey("sectors.AdmissionApplication", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='application_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('new', 'New'), ('contacted', 'Contacted'), ('visit_booked', 'Visit booked'), ('applied', 'Applied'), ('waitlisted', 'Waitlisted'), ('enrolled', 'Enrolled'), ('lost', 'Lost')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'admission_enquiry'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Admissions enquiry, open-day or visit booking, waiting list position (website wi'


class Alumnus(CedaModel):
    """Alumni record (consented contact after graduation)"""

    ceda_entity = 'alumnus'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'graduated_on': {'type': 'date'}, 'contact_consent': {'type': 'bool'}, 'contact_email': {'type': 'email', 'pii': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    graduated_on = models.DateField()
    contact_consent = models.BooleanField(default=False)
    contact_email = models.CharField(max_length=254, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'alumnus'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Alumni record (consented contact after graduation)'


class AuthorisedCollector(CedaModel):
    """Person authorised to collect an early-years child (photo check at pick-up)"""

    ceda_entity = 'authorised_collector'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'effective'
    ceda_scope = 'derived: the learner'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'guardian_id': {'type': 'ref', 'ref': 'guardian'}, 'name': {'type': 'name', 'pii': True}, 'phone': {'type': 'phone', 'pii': True}, 'photo_document_id': {'type': 'uuid', 'class': 'restricted'}, 'password_phrase_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'password_phrase'}, 'valid_from': {'type': 'date', 'standard': True}, 'valid_to': {'type': 'date', 'standard': True}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    guardian_id = cf.UUID7Field(null=True, blank=True, help_text='When the collector is a guardian')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=16, null=True, blank=True)
    photo_document_id = cf.UUID7Field(null=True, blank=True)
    password_phrase_enc = models.BinaryField(null=True, blank=True, help_text='Envelope-encrypted password_phrase. Collection password')
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
        db_table = 'authorised_collector'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Person authorised to collect an early-years child (photo check at pick-up)'


class CareLog(CedaModel):
    """Early-years daily care log (meals, sleep, nappies, medication given) shared with parents"""

    ceda_entity = 'care_log'
    ceda_zones = ('vault',)
    ceda_domain = 'SEC'
    ceda_kind = 'event'
    ceda_class = 'special'
    ceda_history = 'append'
    ceda_scope = 'owned'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-HEALTH'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'log_kind': {'type': 'enum', 'enum': 'care_log_kind'}, 'detail': {'type': 'sealed', 'class': 'special'}, 'recorded_by': {'type': 'uuid'}, 'recorded_at': {'type': 'ts'}, 'shared_with_parents_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    log_kind = models.CharField(max_length=32, choices=[('meal', 'Meal'), ('sleep', 'Sleep'), ('nappy', 'Nappy'), ('medication_given', 'Medication given'), ('incident', 'Incident'), ('note', 'Note')])
    detail = models.BinaryField()
    recorded_by = cf.UUID7Field()
    recorded_at = models.DateTimeField()
    shared_with_parents_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'care_log'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Early-years daily care log (meals, sleep, nappies, medication given) shared with'


class ClinicalSite(CedaModel):
    """Hospital or clinical department hosting rotations (capacity, supervisors)"""

    ceda_entity = 'clinical_site'
    ceda_zones = ('registry',)
    ceda_domain = 'SEC'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'department': {'type': 'str'}, 'capacity': {'type': 'smallint'}, 'fhir_endpoint': {'type': 'url'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    department = models.CharField(max_length=120, null=True, blank=True)
    capacity = models.SmallIntegerField(null=True, blank=True)
    fhir_endpoint = models.CharField(max_length=2048, null=True, blank=True, help_text='Placement attendance confirmation only (Practitioner/Encounter references)')
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
        db_table = 'clinical_site'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Hospital or clinical department hosting rotations (capacity, supervisors)'


class CollectionRecord(CedaModel):
    """Pick-up record with photo check against authorised collectors"""

    ceda_entity = 'collection_record'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'append'
    ceda_scope = 'derived: the learner'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-OPS-3'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'collector_id': {'type': 'ref', 'ref': 'authorised_collector'}, 'is_verified': {'type': 'bool'}, 'staff_id': {'type': 'ref', 'ref': 'staff'}, 'collected_at': {'type': 'ts'}, 'exception_note': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    collector = models.ForeignKey("sectors.AuthorisedCollector", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='collector_id', null=True, blank=True)
    is_verified = models.BooleanField()
    staff_id = cf.UUID7Field()
    collected_at = models.DateTimeField()
    exception_note = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'collection_record'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Pick-up record with photo check against authorised collectors'


class CompetencyFramework(CedaModel):
    """Competency framework (NSQ, NABTEB trade syllabus, industry certification, clinical competencies, digital skills)"""

    ceda_entity = 'competency_framework'
    ceda_zones = ('registry',)
    ceda_domain = 'SEC'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'framework_kind': {'type': 'enum', 'enum': 'competency_framework_kind'}, 'units': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    framework_kind = models.CharField(max_length=32, choices=[('nsq', 'Nsq'), ('trade_syllabus', 'Trade syllabus'), ('industry_certification', 'Industry certification'), ('clinical', 'Clinical'), ('digital_skills', 'Digital skills'), ('other', 'Other')])
    units = models.JSONField(help_text='Units and elements with performance criteria')
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
        db_table = 'competency_framework'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Competency framework (NSQ, NABTEB trade syllabus, industry certification, clinic'


class CompetencyRecord(CedaModel):
    """Competency evidence and assessor sign-off (including approved workplace assessors and clinical supervisors)"""

    ceda_entity = 'competency_record'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'framework_id': {'type': 'ref', 'ref': 'competency_framework'}, 'unit_code': {'type': 'code'}, 'evidence_document_ids': {'type': 'json'}, 'assessor_kind': {'type': 'enum', 'enum': 'assessor_kind'}, 'assessor_ref': {'type': 'uuid'}, 'level_achieved': {'type': 'code'}, 'signed_off_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'competency_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    framework_id = cf.UUID7Field()
    unit_code = models.CharField(max_length=40)
    evidence_document_ids = models.JSONField(null=True, blank=True)
    assessor_kind = models.CharField(max_length=32, choices=[('staff', 'Staff'), ('workplace_assessor', 'Workplace assessor'), ('clinical_supervisor', 'Clinical supervisor')])
    assessor_ref = cf.UUID7Field(help_text='Staff or employer contact')
    level_achieved = models.CharField(max_length=16, null=True, blank=True)
    signed_off_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('in_progress', 'In progress'), ('evidence_submitted', 'Evidence submitted'), ('signed_off', 'Signed off'), ('not_yet_competent', 'Not yet competent')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'competency_record'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Competency evidence and assessor sign-off (including approved workplace assessor'


class DestinationRecord(CedaModel):
    """Post-education destination (further education, employment, apprenticeship, entrepreneurship, professional qualification)"""

    ceda_entity = 'destination_record'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's last institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'destination': {'type': 'cl', 'code_list': 'destination_kind'}, 'detail': {'type': 'json'}, 'recorded_on': {'type': 'date'}, 'source': {'type': 'enum', 'enum': 'destination_source'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field(null=True, blank=True)
    destination = models.CharField(max_length=32)
    detail = models.JSONField(null=True, blank=True)
    recorded_on = models.DateField()
    source = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('institution', 'Institution'), ('survey', 'Survey'), ('exchange', 'Exchange')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'destination_record'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Post-education destination (further education, employment, apprenticeship, entre'


class DevelopmentMilestone(CedaModel):
    """Early-years development area and milestone framework"""

    ceda_entity = 'development_milestone'
    ceda_zones = ('registry',)
    ceda_domain = 'SEC'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'area_code': {'type': 'code'}, 'milestone_code': {'type': 'code'}, 'statement': {'type': 'text'}, 'age_band_months': {'type': 'code'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    area_code = models.CharField(max_length=32)
    milestone_code = models.CharField(max_length=32)
    statement = models.TextField()
    age_band_months = models.CharField(max_length=16)
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
        db_table = 'development_milestone'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Early-years development area and milestone framework'


class EmployerPartner(CedaModel):
    """Employer Partner 360 (placements, sponsorships, assessors, agreements, hiring outcomes)"""

    ceda_entity = 'employer_partner'
    ceda_zones = ('registry',)
    ceda_domain = 'SEC'
    ceda_kind = 'master'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'name': {'type': 'title'}, 'cac_number': {'type': 'code'}, 'sector': {'type': 'cl', 'code_list': 'industry_sector'}, 'address': {'type': 'json'}, 'contacts': {'type': 'json', 'pii': True}, 'agreements': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    name = models.CharField(max_length=300)
    cac_number = models.CharField(max_length=20, null=True, blank=True)
    sector = models.CharField(max_length=32, null=True, blank=True)
    address = models.JSONField(null=True, blank=True)
    contacts = models.JSONField(null=True, blank=True)
    agreements = models.JSONField(null=True, blank=True)
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
        db_table = 'employer_partner'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Employer Partner 360 (placements, sponsorships, assessors, agreements, hiring ou'


class EthicsApplication(CedaModel):
    """Research ethics application and decision"""

    ceda_entity = 'ethics_application'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'derived: the candidature'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'candidature_id': {'type': 'ref', 'ref': 'research_candidature'}, 'title': {'type': 'title'}, 'document_id': {'type': 'uuid'}, 'decision': {'type': 'enum', 'enum': 'approval_decision'}, 'decided_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    candidature = models.ForeignKey("sectors.ResearchCandidature", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='candidature_id')
    title = models.CharField(max_length=300)
    document_id = cf.UUID7Field()
    decision = models.CharField(max_length=32, choices=[('approve', 'Approve'), ('approve_with_conditions', 'Approve with conditions'), ('defer', 'Defer'), ('refuse', 'Refuse')], null=True, blank=True)
    decided_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'ethics_application'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Research ethics application and decision'


class EyrObservation(CedaModel):
    """Early-years observation (text, photo, video) against development areas and milestones, shared with parents"""

    ceda_entity = 'eyr_observation'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's class"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'observed_by_staff_id': {'type': 'ref', 'ref': 'staff'}, 'observed_at': {'type': 'ts'}, 'milestone_codes': {'type': 'json'}, 'note': {'type': 'text'}, 'media_document_ids': {'type': 'json'}, 'pictured_learner_ids': {'type': 'json'}, 'shared_with_parents_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    observed_by_staff_id = cf.UUID7Field()
    observed_at = models.DateTimeField()
    milestone_codes = models.JSONField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    media_document_ids = models.JSONField(null=True, blank=True, help_text='Shared only when every pictured child has photo consent')
    pictured_learner_ids = models.JSONField(null=True, blank=True)
    shared_with_parents_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'eyr_observation'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Early-years observation (text, photo, video) against development areas and miles'


class EyrSessionBooking(CedaModel):
    """Daycare-linked early-years session booking (staff-to-child ratio monitoring)"""

    ceda_entity = 'eyr_session_booking'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'session_date': {'type': 'date'}, 'session_code': {'type': 'code'}, 'invoice_id': {'type': 'ref', 'ref': 'invoice'}, 'status': {'type': 'enum', 'enum': 'booking_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    session_date = models.DateField()
    session_code = models.CharField(max_length=16)
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='invoice_id', null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('requested', 'Requested'), ('confirmed', 'Confirmed'), ('declined', 'Declined'), ('cancelled', 'Cancelled'), ('completed', 'Completed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'eyr_session_booking'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Daycare-linked early-years session booking (staff-to-child ratio monitoring)'


class GraduationList(CedaModel):
    """Graduation list from classification and certificate eligibility; ceremony"""

    ceda_entity = 'graduation_list'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'institution_id': {'type': 'ref', 'ref': 'institution'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'ceremony_on': {'type': 'date'}, 'learner_ids': {'type': 'json'}, 'approved_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    institution_id = cf.UUID7Field()
    period_id = cf.UUID7Field()
    ceremony_on = models.DateField(null=True, blank=True)
    learner_ids = models.JSONField()
    approved_by = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'graduation_list'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Graduation list from classification and certificate eligibility; ceremony'


class GuidanceSession(CedaModel):
    """Career guidance session (counsellor, interests, aptitude, recommended stream, agreed next steps)"""

    ceda_entity = 'guidance_session'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'event'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'counsellor_staff_id': {'type': 'ref', 'ref': 'staff'}, 'held_on': {'type': 'date'}, 'topic': {'type': 'cl', 'code_list': 'guidance_topic'}, 'interests': {'type': 'json'}, 'aptitude': {'type': 'json'}, 'recommended_stream': {'type': 'cl', 'code_list': 'stream'}, 'next_steps': {'type': 'text'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    counsellor_staff_id = cf.UUID7Field()
    held_on = models.DateField()
    topic = models.CharField(max_length=32)
    interests = models.JSONField(null=True, blank=True)
    aptitude = models.JSONField(null=True, blank=True)
    recommended_stream = models.CharField(max_length=32, null=True, blank=True)
    next_steps = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'guidance_session'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Career guidance session (counsellor, interests, aptitude, recommended stream, ag'


class HeApplication(CedaModel):
    """Higher-education application tracked through an adapter (JAMB UTME/CAPS, UCAS-equivalent) — choices, references, offers"""

    ceda_entity = 'he_application'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'scheme': {'type': 'cl', 'code_list': 'admission_scheme'}, 'choices': {'type': 'json'}, 'personal_statement_document_id': {'type': 'uuid'}, 'reference_document_ids': {'type': 'json'}, 'offer': {'type': 'json'}, 'accepted_choice': {'type': 'str'}, 'external_ref': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'application_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    scheme = models.CharField(max_length=32)
    choices = models.JSONField()
    personal_statement_document_id = cf.UUID7Field(null=True, blank=True)
    reference_document_ids = models.JSONField(null=True, blank=True)
    offer = models.JSONField(null=True, blank=True)
    accepted_choice = models.CharField(max_length=200, null=True, blank=True)
    external_ref = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('fee_pending', 'Fee pending'), ('desk_review', 'Desk review'), ('query_raised', 'Query raised'), ('inspection', 'Inspection'), ('decision', 'Decision'), ('approved', 'Approved'), ('refused', 'Refused'), ('deferred', 'Deferred'), ('withdrawn', 'Withdrawn'), ('appealed', 'Appealed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'he_application'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Higher-education application tracked through an adapter (JAMB UTME/CAPS, UCAS-eq'


class IndustrialTraining(CedaModel):
    """Industrial training / SIWES placement (letters, employer acceptance, logbook, visits, ITF forms, grading)"""

    ceda_entity = 'industrial_training'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'placement_id': {'type': 'ref', 'ref': 'placement'}, 'itf_reference': {'type': 'code'}, 'logbook_document_id': {'type': 'uuid'}, 'supervisor_visits': {'type': 'json'}, 'grade': {'type': 'code'}, 'status': {'type': 'enum', 'enum': 'placement_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    placement = models.ForeignKey("sectors.Placement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='placement_id')
    itf_reference = models.CharField(max_length=40, null=True, blank=True)
    logbook_document_id = cf.UUID7Field(null=True, blank=True)
    supervisor_visits = models.JSONField(null=True, blank=True)
    grade = models.CharField(max_length=16, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('agreed', 'Agreed'), ('active', 'Active'), ('completed', 'Completed'), ('terminated', 'Terminated')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'industrial_training'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Industrial training / SIWES placement (letters, employer acceptance, logbook, vi'


class InternationalStudentRecord(CedaModel):
    """Institutional information for an international student (visa-related records) — restricted"""

    ceda_entity = 'international_student_record'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'master'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'nationality': {'type': 'country'}, 'visa_reference_enc': {'type': 'secret', 'class': 'restricted', 'secret_of': 'visa_reference'}, 'visa_reference_last4': {'type': 'code', 'class': 'restricted', 'secret_of': 'visa_reference'}, 'visa_expires_on': {'type': 'date'}, 'sponsor_institution_ref': {'type': 'str'}, 'document_ids': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    nationality = models.CharField(max_length=2)
    visa_reference_enc = models.BinaryField(null=True, blank=True, help_text='Envelope-encrypted visa_reference.')
    visa_reference_last4 = models.CharField(max_length=4, null=True, blank=True, help_text='Last four characters of visa_reference for masked display')
    visa_expires_on = models.DateField(null=True, blank=True)
    sponsor_institution_ref = models.CharField(max_length=120, null=True, blank=True)
    document_ids = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'international_student_record'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Institutional information for an international student (visa-related records) — '


class LogbookEntry(CedaModel):
    """Anonymised clinical logbook entry (procedure/case, level of involvement, reflection) with supervisor verification"""

    ceda_entity = 'logbook_entry'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'placement_id': {'type': 'ref', 'ref': 'placement'}, 'procedure_code': {'type': 'code'}, 'involvement': {'type': 'enum', 'enum': 'involvement_level'}, 'reflection': {'type': 'text'}, 'occurred_on': {'type': 'date'}, 'supervisor_verified_by': {'type': 'str'}, 'verified_at': {'type': 'ts'}, 'clinical_minutes': {'type': 'minutes'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    placement = models.ForeignKey("sectors.Placement", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='placement_id', null=True, blank=True)
    procedure_code = models.CharField(max_length=40)
    involvement = models.CharField(max_length=32, choices=[('observed', 'Observed'), ('assisted', 'Assisted'), ('performed_supervised', 'Performed supervised'), ('performed_independent', 'Performed independent')])
    reflection = models.TextField(null=True, blank=True)
    occurred_on = models.DateField()
    supervisor_verified_by = models.CharField(max_length=200, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    clinical_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'logbook_entry'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Anonymised clinical logbook entry (procedure/case, level of involvement, reflect'


class OptionChoice(CedaModel):
    """Subject option or stream choice (combination rules, capacity, guidance against entry requirements)"""

    ceda_entity = 'option_choice'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'period_id': {'type': 'ref', 'ref': 'academic_period'}, 'stream': {'type': 'cl', 'code_list': 'stream'}, 'choices': {'type': 'json'}, 'rule_check': {'type': 'json'}, 'counsellor_override_by': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    period_id = cf.UUID7Field()
    stream = models.CharField(max_length=32, null=True, blank=True)
    choices = models.JSONField(help_text='Ranked subject choices')
    rule_check = models.JSONField(null=True, blank=True, help_text='Combination-rule result')
    counsellor_override_by = cf.UUID7Field(null=True, blank=True, help_text='Override of a guidance rule (recorded)')
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('in_review', 'In review'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled'), ('fulfilled', 'Fulfilled')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'option_choice'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Subject option or stream choice (combination rules, capacity, guidance against e'


class Placement(CedaModel):
    """Industry placement, apprenticeship or clinical rotation (matching, agreement, attendance, workplace assessment)"""

    ceda_entity = 'placement'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'placement_kind': {'type': 'enum', 'enum': 'placement_kind'}, 'employer_partner_id': {'type': 'ref', 'ref': 'employer_partner'}, 'clinical_site_id': {'type': 'ref', 'ref': 'clinical_site'}, 'supervisor_name': {'type': 'name', 'pii': True}, 'starts_on': {'type': 'date'}, 'ends_on': {'type': 'date'}, 'prerequisites_met': {'type': 'json'}, 'agreement_document_id': {'type': 'uuid'}, 'funding': {'type': 'json'}, 'attendance_confirmed_days': {'type': 'smallint'}, 'status': {'type': 'enum', 'enum': 'placement_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    placement_kind = models.CharField(max_length=32, choices=[('apprenticeship', 'Apprenticeship'), ('industry_placement', 'Industry placement'), ('siwes', 'Siwes'), ('clinical_rotation', 'Clinical rotation'), ('teaching_practice', 'Teaching practice')])
    employer_partner_id = cf.UUID7Field(null=True, blank=True)
    clinical_site_id = cf.UUID7Field(null=True, blank=True)
    supervisor_name = models.CharField(max_length=200, null=True, blank=True)
    starts_on = models.DateField()
    ends_on = models.DateField()
    prerequisites_met = models.JSONField(null=True, blank=True, help_text='Competencies, immunisation/occupational-health clearance')
    agreement_document_id = cf.UUID7Field(null=True, blank=True)
    funding = models.JSONField(null=True, blank=True, help_text='Employer funding')
    attendance_confirmed_days = models.SmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('agreed', 'Agreed'), ('active', 'Active'), ('completed', 'Completed'), ('terminated', 'Terminated')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'placement'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Industry placement, apprenticeship or clinical rotation (matching, agreement, at'


class ProfessionalBody(CedaModel):
    """Health-profession regulator and its registration rules for a programme family (MDCN, NMCN, PCN, MRTB, RRBN, MLSCN, CHPRBN)"""

    ceda_entity = 'professional_body'
    ceda_zones = ('registry',)
    ceda_domain = 'SEC'
    ceda_kind = 'reference'
    ceda_class = 'public'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CUR-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'name': {'type': 'title'}, 'cadre': {'type': 'cl', 'code_list': 'programme_family'}, 'indexing_rules': {'type': 'json'}, 'registration_rules': {'type': 'json'}, 'required_clinical_hours': {'type': 'smallint'}, 'export_format': {'type': 'str'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=16)
    name = models.CharField(max_length=300)
    cadre = models.CharField(max_length=32)
    indexing_rules = models.JSONField(null=True, blank=True)
    registration_rules = models.JSONField(null=True, blank=True)
    required_clinical_hours = models.SmallIntegerField(null=True, blank=True)
    export_format = models.CharField(max_length=80, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'professional_body'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Health-profession regulator and its registration rules for a programme family (M'


class RegistrationReadiness(CedaModel):
    """Readiness of a learner for professional registration or licensing examination (clinical hours, competencies)"""

    ceda_entity = 'registration_readiness'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'projection'
    ceda_class = 'confidential'
    ceda_history = 'snapshot'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'professional_body_id': {'type': 'ref', 'ref': 'professional_body'}, 'clinical_hours': {'type': 'dec'}, 'competencies_signed': {'type': 'smallint'}, 'is_ready': {'type': 'bool'}, 'as_of': {'type': 'date'}, 'exported_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    professional_body_id = cf.UUID7Field(null=True, blank=True)
    clinical_hours = models.DecimalField(max_digits=7, decimal_places=1)
    competencies_signed = models.SmallIntegerField()
    is_ready = models.BooleanField()
    as_of = models.DateField()
    exported_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'registration_readiness'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Readiness of a learner for professional registration or licensing examination (c'


class ResearchCandidature(CedaModel):
    """Research student candidature (supervision, milestones, progression reviews, thesis examination)"""

    ceda_entity = 'research_candidature'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's department"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'enrolment_id': {'type': 'ref', 'ref': 'enrolment'}, 'supervisor_staff_ids': {'type': 'json'}, 'thesis_title': {'type': 'title'}, 'milestones': {'type': 'json'}, 'examination': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'candidature_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    enrolment_id = cf.UUID7Field()
    supervisor_staff_ids = models.JSONField()
    thesis_title = models.CharField(max_length=300, null=True, blank=True)
    milestones = models.JSONField(null=True, blank=True)
    examination = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('active', 'Active'), ('suspended', 'Suspended'), ('under_examination', 'Under examination'), ('awarded', 'Awarded'), ('withdrawn', 'Withdrawn')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'research_candidature'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Research student candidature (supervision, milestones, progression reviews, thes'


class SkillsLabSession(CedaModel):
    """Skills laboratory or simulation session (equipment, facilitators, competency outcomes)"""

    ceda_entity = 'skills_lab_session'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-OPS-7'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'room_booking_id': {'type': 'ref', 'ref': 'room_booking'}, 'scenario': {'type': 'str'}, 'facilitator_staff_ids': {'type': 'json'}, 'equipment_asset_ids': {'type': 'json'}, 'participant_learner_ids': {'type': 'json'}, 'outcomes': {'type': 'json'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    room_booking = models.ForeignKey("timetable.RoomBooking", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='room_booking_id')
    scenario = models.CharField(max_length=300)
    facilitator_staff_ids = models.JSONField()
    equipment_asset_ids = models.JSONField(null=True, blank=True)
    participant_learner_ids = models.JSONField()
    outcomes = models.JSONField(null=True, blank=True, help_text='Competency outcomes recorded')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'skills_lab_session'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Skills laboratory or simulation session (equipment, facilitators, competency out'


class StudentFinanceApplication(CedaModel):
    """Student-finance guidance and loan or grant application (e.g. NELFUND) — no lender credentials stored"""

    ceda_entity = 'student_finance_application'
    ceda_zones = ('ops',)
    ceda_domain = 'SEC'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = "derived: the learner's institution"
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-LRN-PERM'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'learner_id': {'type': 'ref', 'ref': 'learner'}, 'scheme': {'type': 'cl', 'code_list': 'finance_scheme'}, 'amount_requested_minor': {'type': 'money'}, 'currency': {'type': 'currency'}, 'status': {'type': 'enum', 'enum': 'application_status'}, 'external_ref': {'type': 'code'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    learner_id = cf.UUID7Field()
    scheme = models.CharField(max_length=32)
    amount_requested_minor = models.BigIntegerField(null=True, blank=True, help_text='(minor units)')
    currency = models.CharField(max_length=3, null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('fee_pending', 'Fee pending'), ('desk_review', 'Desk review'), ('query_raised', 'Query raised'), ('inspection', 'Inspection'), ('decision', 'Decision'), ('approved', 'Approved'), ('refused', 'Refused'), ('deferred', 'Deferred'), ('withdrawn', 'Withdrawn'), ('appealed', 'Appealed')])
    external_ref = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'student_finance_application'
        app_label = 'sectors'
        base_manager_name = 'unscoped'
        verbose_name = 'Student-finance guidance and loan or grant application (e.g. NELFUND) — no lende'
