"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``records`` — Records and archives.
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



class CustodyEvent(CedaModel):
    """Chain-of-custody event of a box or volume (collected, transferred, received, scanned, returned, archived, destroyed) — append-only"""

    ceda_entity = 'custody_event'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'batch_id': {'type': 'ref', 'ref': 'digitisation_batch'}, 'event_kind': {'type': 'enum', 'enum': 'custody_event_kind'}, 'from_location': {'type': 'str'}, 'to_location': {'type': 'str'}, 'handled_by': {'type': 'uuid'}, 'transfer_note_document_id': {'type': 'uuid'}, 'occurred_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    batch = models.ForeignKey("records.DigitisationBatch", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='batch_id')
    event_kind = models.CharField(max_length=32, choices=[('collected', 'Collected'), ('in_transit', 'In transit'), ('received_at_hub', 'Received at hub'), ('scanned_on_site', 'Scanned on site'), ('returned', 'Returned'), ('archived', 'Archived'), ('destroyed', 'Destroyed'), ('exception', 'Exception')])
    from_location = models.CharField(max_length=120, null=True, blank=True)
    to_location = models.CharField(max_length=120)
    handled_by = cf.UUID7Field()
    transfer_note_document_id = cf.UUID7Field(null=True, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'custody_event'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Chain-of-custody event of a box or volume (collected, transferred, received, sca'


class DigitisationBatch(CedaModel):
    """Box/volume batch in the digitisation programme (barcode, priority, schedule, throughput, quality)"""

    ceda_entity = 'digitisation_batch'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'barcode': {'type': 'code'}, 'survey_id': {'type': 'ref', 'ref': 'digitisation_site_survey'}, 'record_series_id': {'type': 'ref', 'ref': 'record_series'}, 'classification': {'type': 'enum', 'enum': 'classification'}, 'assigned_operator_ids': {'type': 'json'}, 'pages_expected': {'type': 'int_u'}, 'pages_captured': {'type': 'int_u'}, 'hub': {'type': 'str'}, 'stage': {'type': 'enum', 'enum': 'pipeline_stage'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    barcode = models.CharField(max_length=40)
    survey = models.ForeignKey("records.DigitisationSiteSurvey", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='survey_id', null=True, blank=True)
    record_series = models.ForeignKey("records.RecordSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='record_series_id', null=True, blank=True)
    classification = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')], help_text='Special-category batches only to cleared operators')
    assigned_operator_ids = models.JSONField(null=True, blank=True, help_text='DIGO operators (batch-scoped access)')
    pages_expected = models.PositiveIntegerField(null=True, blank=True)
    pages_captured = models.PositiveIntegerField(default=0)
    hub = models.CharField(max_length=80, null=True, blank=True)
    stage = models.CharField(max_length=32, choices=[('surveyed', 'Surveyed'), ('collected', 'Collected'), ('prepared', 'Prepared'), ('captured', 'Captured'), ('cleaned', 'Cleaned'), ('recognised', 'Recognised'), ('extracted', 'Extracted'), ('qa', 'Qa'), ('linked', 'Linked'), ('ingested', 'Ingested'), ('disposed', 'Disposed')])
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
        db_table = 'digitisation_batch'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Box/volume batch in the digitisation programme (barcode, priority, schedule, thr'


class DigitisationSiteSurvey(CedaModel):
    """Survey of paper holdings per site (boxes, volumes, page estimates, cost and duration)"""

    ceda_entity = 'digitisation_site_survey'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'transaction'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'site_name': {'type': 'title'}, 'institution_id': {'type': 'uuid'}, 'boxes': {'type': 'int_u'}, 'volumes': {'type': 'int_u'}, 'estimated_pages': {'type': 'bigint'}, 'priority': {'type': 'smallint'}, 'surveyed_on': {'type': 'date'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    site_name = models.CharField(max_length=300)
    institution_id = cf.UUID7Field(null=True, blank=True)
    boxes = models.PositiveIntegerField()
    volumes = models.PositiveIntegerField()
    estimated_pages = models.BigIntegerField()
    priority = models.SmallIntegerField()
    surveyed_on = models.DateField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'digitisation_site_survey'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Survey of paper holdings per site (boxes, volumes, page estimates, cost and dura'


class Disposal(CedaModel):
    """Approved disposal of documents or originals with disposal/destruction certificate (refused while a legal hold applies)"""

    ceda_entity = 'disposal'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'record_series_id': {'type': 'ref', 'ref': 'record_series'}, 'proposal': {'type': 'json'}, 'approved_by': {'type': 'uuid'}, 'executed_at': {'type': 'ts'}, 'certificate_document_id': {'type': 'uuid'}, 'physical_disposition': {'type': 'enum', 'enum': 'physical_disposition'}, 'status': {'type': 'enum', 'enum': 'disposal_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    record_series = models.ForeignKey("records.RecordSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='record_series_id')
    proposal = models.JSONField(help_text='Documents or boxes proposed')
    approved_by = cf.UUID7Field(null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    certificate_document_id = cf.UUID7Field(null=True, blank=True)
    physical_disposition = models.CharField(max_length=32, choices=[('returned_to_site', 'Returned to site'), ('transferred_to_archive', 'Transferred to archive'), ('destroyed', 'Destroyed')], null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('proposed', 'Proposed'), ('approved', 'Approved'), ('refused_legal_hold', 'Refused legal hold'), ('executed', 'Executed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'disposal'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Approved disposal of documents or originals with disposal/destruction certificat'


class Document(CedaModel):
    """Stored document — born-digital or digitised (object-storage pointer, metadata, classification, retention, hash)"""

    ceda_entity = 'document'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'master'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'category_id': {'type': 'ref', 'ref': 'document_category'}, 'reference_no': {'type': 'code'}, 'title': {'type': 'title'}, 'description': {'type': 'str'}, 'source_reference': {'type': 'str'}, 'classification': {'type': 'enum', 'enum': 'classification'}, 'institution_id': {'type': 'uuid'}, 'lga_scope_id': {'type': 'uuid'}, 'date_from': {'type': 'date'}, 'date_to': {'type': 'date'}, 'session_label': {'type': 'code'}, 'level_or_class': {'type': 'str'}, 'subject_label': {'type': 'str'}, 'origin': {'type': 'enum', 'enum': 'document_origin'}, 'origin_module': {'type': 'code'}, 'batch_id': {'type': 'ref', 'ref': 'digitisation_batch'}, 'page_range': {'type': 'str'}, 'master_object_key': {'type': 'object_key'}, 'access_object_key': {'type': 'object_key'}, 'mime_type': {'type': 'mime'}, 'size_bytes': {'type': 'bigint'}, 'sha256': {'type': 'hash'}, 'captured_at': {'type': 'ts'}, 'qa_status': {'type': 'enum', 'enum': 'qa_status'}, 'ocr_text_ref': {'type': 'object_key'}, 'legal_hold_count': {'type': 'smallint'}, 'disposal_due_on': {'type': 'date'}, 'status': {'type': 'enum', 'enum': 'document_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    category = models.ForeignKey("records.DocumentCategory", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='category_id')
    reference_no = models.CharField(max_length=64, null=True, blank=True, help_text='Reference number, unique in the state: <institution code>/<category>/<year>/<sequence> (CR-007)')
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=2000, null=True, blank=True, help_text='What the document is and what it contains')
    source_reference = models.CharField(max_length=200, null=True, blank=True, help_text='Reference, file or box number written on the paper original')
    classification = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')])
    institution_id = cf.UUID7Field(null=True, blank=True, help_text='Registry institution (soft)')
    lga_scope_id = cf.UUID7Field(null=True, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    session_label = models.CharField(max_length=20, null=True, blank=True)
    level_or_class = models.CharField(max_length=80, null=True, blank=True)
    subject_label = models.CharField(max_length=120, null=True, blank=True)
    origin = models.CharField(max_length=32, choices=[('born_digital', 'Born digital'), ('digitised', 'Digitised'), ('uploaded', 'Uploaded'), ('generated', 'Generated')])
    origin_module = models.CharField(max_length=40, null=True, blank=True, help_text='Born-digital source module')
    batch = models.ForeignKey("records.DigitisationBatch", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='batch_id', null=True, blank=True)
    page_range = models.CharField(max_length=40, null=True, blank=True)
    master_object_key = models.CharField(max_length=1024, help_text='WORM bucket')
    access_object_key = models.CharField(max_length=1024, null=True, blank=True, help_text='Derived access copy (PDF/A-2b)')
    mime_type = models.CharField(max_length=127)
    size_bytes = models.BigIntegerField()
    sha256 = models.BinaryField()
    captured_at = models.DateTimeField()
    qa_status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('auto_accepted', 'Auto accepted'), ('needs_review', 'Needs review'), ('verified', 'Verified'), ('rejected', 'Rejected')])
    ocr_text_ref = models.CharField(max_length=1024, null=True, blank=True, help_text='Full text (never for special category)')
    legal_hold_count = models.SmallIntegerField(default=0)
    disposal_due_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('ingested', 'Ingested'), ('active', 'Active'), ('on_hold', 'On hold'), ('disposal_due', 'Disposal due'), ('disposed', 'Disposed')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'document'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Stored document — born-digital or digitised (object-storage pointer, metadata, c'


class DocumentCategory(CedaModel):
    """Document type/category with its own view, download and share permissions (on top of role and scope)"""

    ceda_entity = 'document_category'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-CONFIG'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'record_series_id': {'type': 'ref', 'ref': 'record_series'}, 'classification': {'type': 'enum', 'enum': 'classification'}, 'permissions': {'type': 'json'}, 'is_full_text_indexed': {'type': 'bool'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    record_series = models.ForeignKey("records.RecordSeries", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='record_series_id')
    classification = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')])
    permissions = models.JSONField(help_text='view, download, share by role')
    is_full_text_indexed = models.BooleanField(default=True, help_text='Always false for special category')
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'document_category'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Document type/category with its own view, download and share permissions (on top'


class DocumentIndex(CedaModel):
    """Full-text search entry of a document — title, keywords and extracted text (never for special category)"""

    ceda_entity = 'document_index'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'projection'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'document_id': {'type': 'ref', 'ref': 'document'}, 'institution_id': {'type': 'uuid'}, 'reference_no': {'type': 'code'}, 'title': {'type': 'title'}, 'keywords': {'type': 'str'}, 'body_text': {'type': 'longtext'}, 'text_source': {'type': 'enum', 'enum': 'text_source'}, 'char_count': {'type': 'int_u'}, 'indexed_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    document = models.ForeignKey("records.Document", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='document_id')
    institution_id = cf.UUID7Field(null=True, blank=True, help_text='Denormalised from the document for per-school search')
    reference_no = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=300)
    keywords = models.CharField(max_length=2000, null=True, blank=True, help_text='Category, school, session, class, subject, paper reference and description')
    body_text = models.TextField(null=True, blank=True, help_text='Extracted or transcribed text')
    text_source = models.CharField(max_length=32, choices=[('none', 'None'), ('pdf_text_layer', 'Pdf text layer'), ('text_file', 'Text file'), ('transcription', 'Transcription'), ('pdf_text_layer_and_transcription', 'Pdf text layer and transcription'), ('ocr', 'Ocr')], help_text='Where body_text came from')
    char_count = models.PositiveIntegerField(default=0)
    indexed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'document_index'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Full-text search entry of a document — title, keywords and extracted text (never'


class DocumentLink(CedaModel):
    """Link from a document to a person or record (learner, staff, guardian, institution, case …) — powers every 360 Documents tab"""

    ceda_entity = 'document_link'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'link'
    ceda_class = 'confidential'
    ceda_history = 'none'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'document_id': {'type': 'ref', 'ref': 'document'}, 'record_kind': {'type': 'code'}, 'record_id': {'type': 'uuid'}, 'link_basis': {'type': 'enum', 'enum': 'link_basis'}, 'confidence': {'type': 'ratio'}, 'confirmed_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    document = models.ForeignKey("records.Document", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='document_id')
    record_kind = models.CharField(max_length=40)
    record_id = cf.UUID7Field()
    link_basis = models.CharField(max_length=32, choices=[('explicit', 'Explicit'), ('matched', 'Matched'), ('extracted', 'Extracted'), ('inherited', 'Inherited')])
    confidence = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True, help_text='For links proposed by matching')
    confirmed_by = cf.UUID7Field(null=True, blank=True)
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'document_link'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Link from a document to a person or record (learner, staff, guardian, institutio'


class ExtractedField(CedaModel):
    """Field extracted from a page with confidence (names, DOB, admission numbers, grades, staff numbers) — double-keyed when key"""

    ceda_entity = 'extracted_field'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'page_id': {'type': 'ref', 'ref': 'scanned_page'}, 'row_no': {'type': 'smallint'}, 'field_name': {'type': 'code'}, 'value': {'type': 'str'}, 'confidence': {'type': 'ratio'}, 'is_key_field': {'type': 'bool'}, 'verified_value': {'type': 'str'}, 'verified_by': {'type': 'uuid'}, 'second_key_by': {'type': 'uuid'}, 'matched_record_kind': {'type': 'code'}, 'matched_record_id': {'type': 'uuid'}, 'status': {'type': 'enum', 'enum': 'qa_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    page = models.ForeignKey("records.ScannedPage", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='page_id')
    row_no = models.SmallIntegerField(null=True, blank=True, help_text='Register/broadsheet row')
    field_name = models.CharField(max_length=40)
    value = models.CharField(max_length=500, null=True, blank=True)
    confidence = models.DecimalField(max_digits=7, decimal_places=6)
    is_key_field = models.BooleanField(default=False)
    verified_value = models.CharField(max_length=500, null=True, blank=True)
    verified_by = cf.UUID7Field(null=True, blank=True)
    second_key_by = cf.UUID7Field(null=True, blank=True, help_text='Double-keying')
    matched_record_kind = models.CharField(max_length=40, null=True, blank=True)
    matched_record_id = cf.UUID7Field(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('auto_accepted', 'Auto accepted'), ('needs_review', 'Needs review'), ('verified', 'Verified'), ('rejected', 'Rejected')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'extracted_field'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Field extracted from a page with confidence (names, DOB, admission numbers, grad'


class LegalHold(CedaModel):
    """Legal hold suspending disposal for named people, institutions or series"""

    ceda_entity = 'legal_hold'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'title': {'type': 'title'}, 'subject_filter': {'type': 'json'}, 'reason': {'type': 'text'}, 'placed_by': {'type': 'uuid'}, 'released_at': {'type': 'ts'}, 'status': {'type': 'enum', 'enum': 'record_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    title = models.CharField(max_length=300)
    subject_filter = models.JSONField(help_text='People, institutions, series')
    reason = models.TextField()
    placed_by = cf.UUID7Field()
    released_at = models.DateTimeField(null=True, blank=True)
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
        db_table = 'legal_hold'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Legal hold suspending disposal for named people, institutions or series'


class QaSample(CedaModel):
    """Batch QA sample result against the accuracy target (≥ 99.5% key fields)"""

    ceda_entity = 'qa_sample'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'event'
    ceda_class = 'internal'
    ceda_history = 'append'
    ceda_scope = 'none'
    ceda_append_only = True
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'batch_id': {'type': 'ref', 'ref': 'digitisation_batch'}, 'sampled': {'type': 'int_u'}, 'errors': {'type': 'int_u'}, 'accuracy': {'type': 'pct'}, 'passed': {'type': 'bool'}, 'checked_by': {'type': 'uuid'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    batch = models.ForeignKey("records.DigitisationBatch", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='batch_id')
    sampled = models.PositiveIntegerField()
    errors = models.PositiveIntegerField()
    accuracy = models.DecimalField(max_digits=6, decimal_places=3)
    passed = models.BooleanField()
    checked_by = cf.UUID7Field()
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'qa_sample'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Batch QA sample result against the accuracy target (≥ 99.5% key fields)'


class RecordRequest(CedaModel):
    """Public request for copies of a person's own records (identity verification and configured fee)"""

    ceda_entity = 'record_request'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'requester_name': {'type': 'name', 'pii': True}, 'requester_phone': {'type': 'phone', 'pii': True}, 'person_kind': {'type': 'enum', 'enum': 'person_kind'}, 'person_id': {'type': 'uuid'}, 'identity_verified_at': {'type': 'ts'}, 'fee_reference': {'type': 'code'}, 'paid_at': {'type': 'ts'}, 'fulfilled_document_ids': {'type': 'json'}, 'status': {'type': 'enum', 'enum': 'request_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    requester_name = models.CharField(max_length=200)
    requester_phone = models.CharField(max_length=16, null=True, blank=True)
    person_kind = models.CharField(max_length=32, choices=[('learner', 'Learner'), ('guardian', 'Guardian'), ('staff', 'Staff'), ('provider_person', 'Provider person'), ('applicant', 'Applicant'), ('visitor', 'Visitor')], null=True, blank=True)
    person_id = cf.UUID7Field(null=True, blank=True)
    identity_verified_at = models.DateTimeField(null=True, blank=True)
    fee_reference = models.CharField(max_length=64, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    fulfilled_document_ids = models.JSONField(null=True, blank=True)
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
        db_table = 'record_request'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = "Public request for copies of a person's own records (identity verification and c"


class RecordSeries(CedaModel):
    """File-plan record series with owner, classification and retention rule"""

    ceda_entity = 'record_series'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'config'
    ceda_class = 'internal'
    ceda_history = 'versioned'
    ceda_scope = 'owned'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'scope_node_id': {'type': 'uuid', 'standard': True}, 'code': {'type': 'code'}, 'title': {'type': 'title'}, 'owner_role': {'type': 'code'}, 'classification': {'type': 'enum', 'enum': 'classification'}, 'retention_series': {'type': 'code'}, 'retention_rule': {'type': 'json'}, 'version': {'type': 'int_u'}, 'status': {'type': 'enum', 'enum': 'version_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    scope_node_id = cf.UUID7Field()
    code = models.CharField(max_length=32, help_text='File plan code')
    title = models.CharField(max_length=300)
    owner_role = models.CharField(max_length=16)
    classification = models.CharField(max_length=32, choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('restricted', 'Restricted'), ('special', 'Special')])
    retention_series = models.CharField(max_length=32, help_text='CEDA retention series (model/retention.yaml)')
    retention_rule = models.JSONField(help_text='Trigger, period, disposal action')
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
        db_table = 'record_series'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'File-plan record series with owner, classification and retention rule'


class Redaction(CedaModel):
    """Automatic redaction of third-party personal data before external release, with human review"""

    ceda_entity = 'redaction'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'transaction'
    ceda_class = 'confidential'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'document_id': {'type': 'ref', 'ref': 'document'}, 'regions': {'type': 'json'}, 'redacted_object_key': {'type': 'object_key'}, 'reviewed_by': {'type': 'uuid'}, 'released_at': {'type': 'ts'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    document = models.ForeignKey("records.Document", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='document_id')
    regions = models.JSONField(help_text='Page regions redacted')
    redacted_object_key = models.CharField(max_length=1024)
    reviewed_by = cf.UUID7Field(null=True, blank=True)
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
        db_table = 'redaction'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Automatic redaction of third-party personal data before external release, with h'


class ScannedPage(CedaModel):
    """Page image captured from a batch (master TIFF/JPEG 2000 hashed at capture; access copy derived)"""

    ceda_entity = 'scanned_page'
    ceda_zones = ('records',)
    ceda_domain = 'DOC'
    ceda_kind = 'transaction'
    ceda_class = 'restricted'
    ceda_history = 'lifecycle'
    ceda_scope = 'none'
    ceda_append_only = False
    ceda_partition = None
    ceda_retention = 'RS-DOC'
    ceda_fields = {'id': {'type': 'uuid', 'standard': True}, 'tenant_id': {'type': 'uuid', 'standard': True}, 'batch_id': {'type': 'ref', 'ref': 'digitisation_batch'}, 'document_id': {'type': 'ref', 'ref': 'document'}, 'sequence_no': {'type': 'int_u'}, 'master_object_key': {'type': 'object_key'}, 'access_object_key': {'type': 'object_key'}, 'dpi': {'type': 'smallint'}, 'sha256': {'type': 'hash'}, 'ocr_confidence': {'type': 'ratio'}, 'document_type_guess': {'type': 'code'}, 'captured_at': {'type': 'ts'}, 'qa_status': {'type': 'enum', 'enum': 'qa_status'}, 'created_at': {'type': 'ts', 'standard': True}, 'created_by': {'type': 'uuid', 'standard': True}, 'updated_at': {'type': 'ts', 'standard': True}, 'updated_by': {'type': 'uuid', 'standard': True}, 'row_version': {'type': 'int_u', 'standard': True}}

    id = cf.UUID7Field(primary_key=True, default=uuid7)
    tenant_id = cf.UUID7Field()
    batch = models.ForeignKey("records.DigitisationBatch", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='batch_id')
    document = models.ForeignKey("records.Document", on_delete=models.DO_NOTHING, db_constraint=False, related_name='+', db_column='document_id', null=True, blank=True)
    sequence_no = models.PositiveIntegerField()
    master_object_key = models.CharField(max_length=1024)
    access_object_key = models.CharField(max_length=1024, null=True, blank=True)
    dpi = models.SmallIntegerField()
    sha256 = models.BinaryField()
    ocr_confidence = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    document_type_guess = models.CharField(max_length=40, null=True, blank=True)
    captured_at = models.DateTimeField()
    qa_status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('auto_accepted', 'Auto accepted'), ('needs_review', 'Needs review'), ('verified', 'Verified'), ('rejected', 'Rejected')])
    created_at = models.DateTimeField(default=cf.utcnow)
    created_by = cf.UUID7Field(null=True, blank=True)
    updated_at = models.DateTimeField(default=cf.utcnow)
    updated_by = cf.UUID7Field(null=True, blank=True)
    row_version = models.PositiveIntegerField(default=1)

    objects = TenantScopedManager()
    unscoped = models.Manager()

    class Meta:
        managed = False
        db_table = 'scanned_page'
        app_label = 'records'
        base_manager_name = 'unscoped'
        verbose_name = 'Page image captured from a batch (master TIFF/JPEG 2000 hashed at capture; acces'
