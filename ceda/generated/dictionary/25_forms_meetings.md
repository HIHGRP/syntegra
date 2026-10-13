# FRM — Forms and Daybook engine and parents' meetings

The no-code forms builder (Daybook forms) with versioned definitions, per-form security, multi-stage workflow, optional cost and Pay Now step, and automatic filing to the learner, staff or family Daybook timeline (FR-FRM-101–108). Parents' meetings across days with in-person, video and hybrid slots, clash prevention, travel gaps, interpreters, consent-only recording and attendance notes (FR-PTM-101–106).

Module (system of record): `forms` · default zone: **ops** · default retention: `RS-OPS-7`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`form_definition`](#ops-form_definition) | ops | config | internal | versioned | Form template (versioned; text, number, date, choice, signature, upload, body-map, cost and table fields) |
| [`form_response`](#ops-form_response) | ops | transaction | confidential | lifecycle | Submitted form (keeps the version it was submitted on; filed to the Daybook timeline) |
| [`meeting_event`](#ops-meeting_event) | ops | config | internal | lifecycle | Parents' meeting event across one or more days (in-person, video and hybrid slots per teacher) |
| [`meeting_booking`](#ops-meeting_booking) | ops | transaction | confidential | lifecycle | Booked slot for a parent with a teacher (clash prevention; interpreter; attendance and notes to the learner timeline) |

<a id="ops-form_definition"></a>
## `form_definition`

Form template (versioned; text, number, date, choice, signature, upload, body-map, cost and table fields)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `forms` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-FRM-101, FR-FRM-102, FR-FRM-104, FR-FRM-106, FR-FRM-107 |
| Pages | FRM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `field_schema` | `JSON` | no |  | Fields, mandatory and conditional rules |
| `raised_by_roles` | `JSON` | no |  | Staff, learners, parents, on behalf |
| `confidentiality` | `VARCHAR(32)` | no |  | values: public, internal, confidential, restricted, special |
| `workflow_definition_id` → `workflow_definition` | `BINARY(16)` | yes |  |  |
| `cost_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `requires_payment_before_continue` | `BOOLEAN` | no |  |  |
| `files_to` | `VARCHAR(32)` | no |  | values: learner, staff, family, institution |
| `is_template_library` | `BOOLEAN` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

- Soft reference `workflow_definition_id` → `workflow_definition` — declared soft
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-form_response"></a>
## `form_response`

Submitted form (keeps the version it was submitted on; filed to the Daybook timeline)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `forms` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-FRM-102, FR-FRM-103, FR-FRM-105, FR-FRM-107, FR-FRM-108 |
| Pages | FRM-102 |
| Events | FRM.SUBMITTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `form_id` → `form_definition` | `BINARY(16)` | yes |  |  |
| `form_version` | `INT UNSIGNED` | no |  |  |
| `subject_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `subject_id` | `BINARY(16)` | no |  |  |
| `submitted_by` | `BINARY(16)` | no |  |  |
| `on_behalf_of` | `BINARY(16)` | yes |  |  |
| `answers` | `JSON` | no |  |  |
| `attachment_document_ids` | `JSON` | yes |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | yes |  |  |
| `workflow_instance_id` → `workflow_instance` | `BINARY(16)` | yes |  |  |
| `submitted_at` | `DATETIME(6)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_workflow, awaiting_payment, approved, rejected, filed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, subject_kind, subject_id)

- Soft reference `form_id` → `form_definition` — declared soft
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-meeting_event"></a>
## `meeting_event`

Parents' meeting event across one or more days (in-person, video and hybrid slots per teacher)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `forms` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-PTM-101, FR-PTM-104 |
| Pages | PTM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `class_group_ids` | `JSON` | no |  |  |
| `days` | `JSON` | no |  | Dates and session windows |
| `slot_minutes` | `SMALLINT` | no |  |  |
| `travel_gap_minutes` | `SMALLINT` | no |  |  |
| `modes` | `JSON` | no |  | in_person, video, hybrid |
| `booking_opens_at` | `DATETIME(6)` | no |  |  |
| `booking_closes_at` | `DATETIME(6)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-meeting_booking"></a>
## `meeting_booking`

Booked slot for a parent with a teacher (clash prevention; interpreter; attendance and notes to the learner timeline)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `forms` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-PTM-102, FR-PTM-103, FR-PTM-105, FR-PTM-106 |
| Pages | PTM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `meeting_event_id` → `meeting_event` | `BINARY(16)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `guardian_id` → `guardian` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `starts_at` | `DATETIME(6)` | no |  |  |
| `mode` | `VARCHAR(32)` | no |  | values: in_person, video, hybrid |
| `interpreter_language` | `VARCHAR(35)` | yes |  |  |
| `video_room_ref` | `VARCHAR(200)` | yes |  |  |
| `recording_consent_all` | `BOOLEAN` | no |  |  |
| `attended` | `BOOLEAN` | yes |  |  |
| `note` | `VARCHAR(1000)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, confirmed, declined, cancelled, completed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, meeting_event_id, staff_id, starts_at)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `guardian_id` → `guardian` — cross-zone (ops → registry)
- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

