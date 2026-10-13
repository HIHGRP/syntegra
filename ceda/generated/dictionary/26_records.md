# DOC — Records and archives — document store, file plan, retention, legal holds, disposal and the digitisation pipeline

One records system for born-digital and digitised paper (MFS §13, FR-DOC-101–118). Every document has Dublin Core-based metadata extended for education, a classification inherited from its document type, a record series (file plan) with retention, and links to the people and institutions it concerns. Binary content lives in S3-compatible object storage: masters in WORM buckets, hashed at capture and verified on every read; access copies are derived. The digitisation pipeline tracks boxes and volumes under chain of custody through capture, clean-up, OCR/HTR, classification, field extraction with confidence, human QA and linking to master records. Special-category documents are restricted to cleared operators and named users throughout, and are never full-text indexed.

Module (system of record): `records` · default zone: **records** · default retention: `RS-DOC`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`record_series`](#records-record_series) | records | config | internal | versioned | File-plan record series with owner, classification and retention rule |
| [`document_category`](#records-document_category) | records | config | internal | lifecycle | Document type/category with its own view, download and share permissions (on top of role and scope) |
| [`document`](#records-document) | records | master | confidential | lifecycle | Stored document — born-digital or digitised (object-storage pointer, metadata, classification, retention, hash) |
| [`document_link`](#records-document_link) | records | link | confidential | none | Link from a document to a person or record (learner, staff, guardian, institution, case …) — powers every 360 Documents tab |
| [`legal_hold`](#records-legal_hold) | records | transaction | restricted | lifecycle | Legal hold suspending disposal for named people, institutions or series |
| [`disposal`](#records-disposal) | records | event | internal | lifecycle | Approved disposal of documents or originals with disposal/destruction certificate (refused while a legal hold applies) |
| [`redaction`](#records-redaction) | records | transaction | confidential | lifecycle | Automatic redaction of third-party personal data before external release, with human review |
| [`record_request`](#records-record_request) | records | transaction | restricted | lifecycle | Public request for copies of a person's own records (identity verification and configured fee) |
| [`digitisation_site_survey`](#records-digitisation_site_survey) | records | transaction | internal | lifecycle | Survey of paper holdings per site (boxes, volumes, page estimates, cost and duration) |
| [`digitisation_batch`](#records-digitisation_batch) | records | transaction | restricted | lifecycle | Box/volume batch in the digitisation programme (barcode, priority, schedule, throughput, quality) |
| [`custody_event`](#records-custody_event) | records | event | internal | append | Chain-of-custody event of a box or volume (collected, transferred, received, scanned, returned, archived, destroyed) — append-only |
| [`scanned_page`](#records-scanned_page) | records | transaction | restricted | lifecycle | Page image captured from a batch (master TIFF/JPEG 2000 hashed at capture; access copy derived) |
| [`extracted_field`](#records-extracted_field) | records | transaction | restricted | lifecycle | Field extracted from a page with confidence (names, DOB, admission numbers, grades, staff numbers) — double-keyed when key |
| [`qa_sample`](#records-qa_sample) | records | event | internal | append | Batch QA sample result against the accuracy target (≥ 99.5% key fields) |

<a id="records-record_series"></a>
## `record_series`

File-plan record series with owner, classification and retention rule

| | |
|---|---|
| Zone | records |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-115, FR-ADM-07 |
| Pages | DOC-106, ADM-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  | File plan code |
| `title` | `VARCHAR(300)` | no |  |  |
| `owner_role` | `VARCHAR(16)` | no |  |  |
| `classification` | `VARCHAR(32)` | no |  | values: public, internal, confidential, restricted, special |
| `retention_series` | `VARCHAR(32)` | no |  | CEDA retention series (model/retention.yaml) |
| `retention_rule` | `JSON` | no |  | Trigger, period, disposal action |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-document_category"></a>
## `document_category`

Document type/category with its own view, download and share permissions (on top of role and scope)

| | |
|---|---|
| Zone | records |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `records` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-DOC-106, FR-DOC-117 |
| Pages | DOC-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `record_series_id` → `record_series` | `BINARY(16)` | no |  |  |
| `classification` | `VARCHAR(32)` | no |  | values: public, internal, confidential, restricted, special |
| `permissions` | `JSON` | no |  | view, download, share by role |
| `is_full_text_indexed` | `BOOLEAN` | no |  | Always false for special category |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-document"></a>
## `document`

Stored document — born-digital or digitised (object-storage pointer, metadata, classification, retention, hash)  

Metadata (MFS §13.4): title, type, institution, LGA, date or range, people referenced, session, class/level, subject, record series, classification, retention rule, source (box, volume, pages, batch) or origin module, capture date, hash and QA status. Downloads and prints are watermarked with the viewer's name and time.

| | |
|---|---|
| Zone | records |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-103, FR-DOC-109, FR-DOC-110, FR-DOC-111, FR-DOC-112, FR-DOC-116, FR-INT-03, FR-INT-101 |
| Pages | DOC-105, DOC-104, AIX-02, HOM-05 |
| Events | DOC.INGESTED, DOC.LINKED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `category_id` → `document_category` | `BINARY(16)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `classification` | `VARCHAR(32)` | no |  | values: public, internal, confidential, restricted, special |
| `institution_id` | `BINARY(16)` | yes |  | Registry institution (soft) |
| `lga_scope_id` | `BINARY(16)` | yes |  |  |
| `date_from` | `DATE` | yes |  |  |
| `date_to` | `DATE` | yes |  |  |
| `session_label` | `VARCHAR(20)` | yes |  |  |
| `level_or_class` | `VARCHAR(80)` | yes |  |  |
| `subject_label` | `VARCHAR(120)` | yes |  |  |
| `origin` | `VARCHAR(32)` | no |  | values: born_digital, digitised, uploaded, generated |
| `origin_module` | `VARCHAR(40)` | yes |  | Born-digital source module |
| `batch_id` → `digitisation_batch` | `BINARY(16)` | yes |  |  |
| `page_range` | `VARCHAR(40)` | yes |  |  |
| `master_object_key` | `VARCHAR(1024)` | no |  | WORM bucket |
| `access_object_key` | `VARCHAR(1024)` | yes |  | Derived access copy (PDF/A-2b) |
| `mime_type` | `VARCHAR(127)` | no |  |  |
| `size_bytes` | `BIGINT` | no |  |  |
| `sha256` | `BINARY(32)` | no |  |  |
| `captured_at` | `DATETIME(6)` | no |  |  |
| `qa_status` | `VARCHAR(32)` | no |  | values: pending, auto_accepted, needs_review, verified, rejected |
| `ocr_text_ref` | `VARCHAR(1024)` | yes |  | Full text (never for special category) |
| `legal_hold_count` | `SMALLINT` | no |  |  |
| `disposal_due_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: ingested, active, on_hold, disposal_due, disposed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, category_id)
- Index: (tenant_id, disposal_due_on)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-document_link"></a>
## `document_link`

Link from a document to a person or record (learner, staff, guardian, institution, case …) — powers every 360 Documents tab

| | |
|---|---|
| Zone | records |
| Kind | link |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `records` |
| Origin | ceda |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-108, FR-DOC-111, FR-DOC-116, FR-FRM-105 |
| Pages | DOC-105, LRN-04, STF-02, INS-02 |
| Events | DOC.LINKED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `document_id` → `document` | `BINARY(16)` | no |  |  |
| `record_kind` | `VARCHAR(40)` | no |  |  |
| `record_id` | `BINARY(16)` | no |  |  |
| `link_basis` | `VARCHAR(32)` | no |  | values: explicit, matched, extracted, inherited |
| `confidence` | `DECIMAL(7,6)` | yes |  | For links proposed by matching |
| `confirmed_by` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, document_id, record_kind, record_id)
- Index: (tenant_id, record_kind, record_id)

<a id="records-legal_hold"></a>
## `legal_hold`

Legal hold suspending disposal for named people, institutions or series

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-115, FR-ADM-07 |
| Pages | DOC-106, ADM-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `subject_filter` | `JSON` | no |  | People, institutions, series |
| `reason` | `TEXT` | no |  |  |
| `placed_by` | `BINARY(16)` | no |  |  |
| `released_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-disposal"></a>
## `disposal`

Approved disposal of documents or originals with disposal/destruction certificate (refused while a legal hold applies)

| | |
|---|---|
| Zone | records |
| Kind | event |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-115 |
| Pages | DOC-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `record_series_id` → `record_series` | `BINARY(16)` | no |  |  |
| `proposal` | `JSON` | no |  | Documents or boxes proposed |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `executed_at` | `DATETIME(6)` | yes |  |  |
| `certificate_document_id` | `BINARY(16)` | yes |  |  |
| `physical_disposition` | `VARCHAR(32)` | yes |  | values: returned_to_site, transferred_to_archive, destroyed |
| `status` | `VARCHAR(32)` | no |  | values: proposed, approved, refused_legal_hold, executed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-redaction"></a>
## `redaction`

Automatic redaction of third-party personal data before external release, with human review

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `records` |
| Origin | ceda |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-113 |
| Pages | DOC-105 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `document_id` → `document` | `BINARY(16)` | no |  |  |
| `regions` | `JSON` | no |  | Page regions redacted |
| `redacted_object_key` | `VARCHAR(1024)` | no |  |  |
| `reviewed_by` | `BINARY(16)` | yes |  |  |
| `released_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="records-record_request"></a>
## `record_request`

Public request for copies of a person's own records (identity verification and configured fee)

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `records` |
| Origin | ceda |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-114 |
| Pages | DOC-104, PUB-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `requester_name` | `VARCHAR(200)` | no |  |  |
| `requester_phone` | `VARCHAR(16)` | yes |  |  |
| `person_kind` | `VARCHAR(32)` | yes |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `person_id` | `BINARY(16)` | yes |  |  |
| `identity_verified_at` | `DATETIME(6)` | yes |  |  |
| `fee_reference` | `VARCHAR(64)` | yes |  |  |
| `paid_at` | `DATETIME(6)` | yes |  |  |
| `fulfilled_document_ids` | `JSON` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-digitisation_site_survey"></a>
## `digitisation_site_survey`

Survey of paper holdings per site (boxes, volumes, page estimates, cost and duration)

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `records` |
| Origin | ceda |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-101 |
| Pages | DOC-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `site_name` | `VARCHAR(300)` | no |  |  |
| `institution_id` | `BINARY(16)` | yes |  |  |
| `boxes` | `INT UNSIGNED` | no |  |  |
| `volumes` | `INT UNSIGNED` | no |  |  |
| `estimated_pages` | `BIGINT` | no |  |  |
| `priority` | `SMALLINT` | no |  |  |
| `surveyed_on` | `DATE` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-digitisation_batch"></a>
## `digitisation_batch`

Box/volume batch in the digitisation programme (barcode, priority, schedule, throughput, quality)

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-101, FR-DOC-102, FR-DOC-118 |
| Pages | DOC-101, DOC-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `barcode` | `VARCHAR(40)` | no |  |  |
| `survey_id` → `digitisation_site_survey` | `BINARY(16)` | yes |  |  |
| `record_series_id` → `record_series` | `BINARY(16)` | yes |  |  |
| `classification` | `VARCHAR(32)` | no |  | Special-category batches only to cleared operators · values: public, internal, confidential, restricted, special |
| `assigned_operator_ids` | `JSON` | yes |  | DIGO operators (batch-scoped access) |
| `pages_expected` | `INT UNSIGNED` | yes |  |  |
| `pages_captured` | `INT UNSIGNED` | no |  |  |
| `hub` | `VARCHAR(80)` | yes |  |  |
| `stage` | `VARCHAR(32)` | no |  | values: surveyed, collected, prepared, captured, cleaned, recognised, extracted, qa, linked, ingested, disposed |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, barcode)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="records-custody_event"></a>
## `custody_event`

Chain-of-custody event of a box or volume (collected, transferred, received, scanned, returned, archived, destroyed) — append-only

| | |
|---|---|
| Zone | records |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-102 |
| Pages | DOC-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `batch_id` → `digitisation_batch` | `BINARY(16)` | no |  |  |
| `event_kind` | `VARCHAR(32)` | no |  | values: collected, in_transit, received_at_hub, scanned_on_site, returned, archived, destroyed, exception |
| `from_location` | `VARCHAR(120)` | yes |  |  |
| `to_location` | `VARCHAR(120)` | no |  |  |
| `handled_by` | `BINARY(16)` | no |  |  |
| `transfer_note_document_id` | `BINARY(16)` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="records-scanned_page"></a>
## `scanned_page`

Page image captured from a batch (master TIFF/JPEG 2000 hashed at capture; access copy derived)

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-103, FR-DOC-104, FR-DOC-105, FR-LMS-119 |
| Pages | DOC-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `batch_id` → `digitisation_batch` | `BINARY(16)` | no |  |  |
| `document_id` → `document` | `BINARY(16)` | yes |  |  |
| `sequence_no` | `INT UNSIGNED` | no |  |  |
| `master_object_key` | `VARCHAR(1024)` | no |  |  |
| `access_object_key` | `VARCHAR(1024)` | yes |  |  |
| `dpi` | `SMALLINT` | no |  |  |
| `sha256` | `BINARY(32)` | no |  |  |
| `ocr_confidence` | `DECIMAL(7,6)` | yes |  |  |
| `document_type_guess` | `VARCHAR(40)` | yes |  |  |
| `captured_at` | `DATETIME(6)` | no |  |  |
| `qa_status` | `VARCHAR(32)` | no |  | values: pending, auto_accepted, needs_review, verified, rejected |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, batch_id, sequence_no)

<a id="records-extracted_field"></a>
## `extracted_field`

Field extracted from a page with confidence (names, DOB, admission numbers, grades, staff numbers) — double-keyed when key

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `records` |
| Origin | appj |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-106, FR-DOC-107, FR-DOC-108, FR-INT-03 |
| Pages | DOC-103, AIX-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `page_id` → `scanned_page` | `BINARY(16)` | no |  |  |
| `row_no` | `SMALLINT` | yes |  | Register/broadsheet row |
| `field_name` | `VARCHAR(40)` | no |  |  |
| `value` | `VARCHAR(500)` | yes |  |  |
| `confidence` | `DECIMAL(7,6)` | no |  |  |
| `is_key_field` | `BOOLEAN` | no |  |  |
| `verified_value` | `VARCHAR(500)` | yes |  |  |
| `verified_by` | `BINARY(16)` | yes |  |  |
| `second_key_by` | `BINARY(16)` | yes |  | Double-keying |
| `matched_record_kind` | `VARCHAR(40)` | yes |  |  |
| `matched_record_id` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: pending, auto_accepted, needs_review, verified, rejected |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, page_id, row_no)

<a id="records-qa_sample"></a>
## `qa_sample`

Batch QA sample result against the accuracy target (≥ 99.5% key fields)

| | |
|---|---|
| Zone | records |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `records` |
| Origin | ceda |
| Retention | `RS-DOC` |
| Requirements | FR-DOC-107 |
| Pages | DOC-103, DOC-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `batch_id` → `digitisation_batch` | `BINARY(16)` | no |  |  |
| `sampled` | `INT UNSIGNED` | no |  |  |
| `errors` | `INT UNSIGNED` | no |  |  |
| `accuracy` | `DECIMAL(6,3)` | no |  |  |
| `passed` | `BOOLEAN` | no |  |  |
| `checked_by` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

