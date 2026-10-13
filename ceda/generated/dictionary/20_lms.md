# LMS — Online coursework — course spaces, content, assignments, submissions, marking, quizzes, live classes and digital skills

A course space for every class-subject and course section, created automatically from published class subject plans and approved course allocations, with units generated from the scheme of work and every item tagged to curriculum objectives (MFS §8, FR-LMS-101–127). Submissions get hashed, timestamped receipts, keep every version and record device and sync times for offline work; work is never auto-zeroed. Marks post to the markbook and objective results to curriculum evidence. Digital-skills levels for learners and teachers feed the Education Passport and the state dashboard. Binary content (files, recordings, H5P packages) is in object storage.

Module (system of record): `lms` · default zone: **ops** · default retention: `RS-LMS`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`course_space`](#ops-course_space) | ops | master | internal | lifecycle | LMS course space for a class-subject, course section or staff training course (auto-created; roster synced) |
| [`course_member`](#ops-course_member) | ops | link | confidential | effective | Roster membership of a course space (synced from enrolment, class membership, registration or allocation) |
| [`lms_unit`](#ops-lms_unit) | ops | config | internal | none | Unit (week or topic) of a course space generated from the scheme of work and tagged to objectives |
| [`lms_content`](#ops-lms_content) | ops | config | internal | none | Content item — note, file, video, audio, link, H5P interactive or state content-library item |
| [`content_library_item`](#registry-content_library_item) | registry | master | public | versioned | State content-library resource, curriculum-aligned, published by the state |
| [`assignment`](#ops-assignment) | ops | transaction | internal | lifecycle | Assignment — homework, coursework, CA test, quiz/CBT, practical, portfolio, peer review or digital-skills task |
| [`rubric`](#ops-rubric) | ops | config | internal | versioned | Marking rubric (criteria and levels; digital-skills rubrics map to the framework) |
| [`submission`](#ops-submission) | ops | transaction | confidential | append | Learner submission version (hashed, timestamped receipt; device and sync times; AI-use declaration) |
| [`submission_file`](#ops-submission_file) | ops | event | confidential | append | File in a submission (compressed on upload; up to 200 MB per submission, configurable) |
| [`submission_mark`](#ops-submission_mark) | ops | transaction | confidential | lifecycle | Mark and feedback for a submission (rubric, comments, annotations, audio feedback; auto-marked items) |
| [`extension`](#ops-extension) | ops | transaction | confidential | lifecycle | Individual extension with reason (no lateness flag before the extended date) |
| [`originality_report`](#ops-originality_report) | ops | event | confidential | append | Originality check result from the configured provider (shown to the teacher only; never an automatic penalty) |
| [`question`](#ops-question) | ops | master | internal | versioned | Question-bank item owned by a department or the state (with difficulty and discrimination statistics) |
| [`quiz_attempt`](#ops-quiz_attempt) | ops | transaction | confidential | lifecycle | Online quiz or CBT attempt (randomised items, timing incl. extra-time adjustment, secure-mode, IP and device log) |
| [`live_class`](#ops-live_class) | ops | transaction | internal | lifecycle | Scheduled live video class (attendance to the register; recording only with consent) |
| [`discussion_post`](#ops-discussion_post) | ops | event | confidential | lifecycle | Moderated discussion post (under-13s only in teacher-moderated threads; no private learner-to-learner messages) |
| [`homework_limit`](#ops-homework_limit) | ops | config | internal | effective | Nightly homework timetable and load limit for a class |
| [`digital_skill_level`](#ops-digital_skill_level) | ops | transaction | confidential | effective | Digital-skills level per person and strand (device use, information literacy, communication, content creation, safety, computational thinking) |
| [`ussd_session`](#ops-ussd_session) | ops | event | confidential | append | USSD/SMS feature-phone interaction (due dates, completion confirmation) |

<a id="ops-course_space"></a>
## `course_space`

LMS course space for a class-subject, course section or staff training course (auto-created; roster synced)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-101, FR-ACA-115, FR-STF-105, FR-HED-101 |
| Pages | LMS-101 |
| Events | LMS.SPACE_CREATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `space_kind` | `VARCHAR(32)` | no |  | values: class_subject, course_section, staff_training, programme, community |
| `class_subject_plan_id` → `class_subject_plan` | `BINARY(16)` | yes |  |  |
| `course_section_id` → `course_section` | `BINARY(16)` | yes |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `owner_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `external_lms` | `JSON` | yes |  | LTI 1.3 / OneRoster link where an external LMS is used |
| `storage_bytes` | `BIGINT` | no |  | 5 GB per institution per session included |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `owner_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-course_member"></a>
## `course_member`

Roster membership of a course space (synced from enrolment, class membership, registration or allocation)

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | confidential |
| History | effective |
| Scope | derived: the course space |
| Module | `lms` |
| Origin | ceda |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-101 |
| Pages | LMS-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `course_space_id` → `course_space` | `BINARY(16)` | no |  |  |
| `member_kind` | `VARCHAR(32)` | no |  | values: learner, staff |
| `member_id` | `BINARY(16)` | no |  | learner or staff id |
| `space_role` | `VARCHAR(32)` | no |  | values: owner, editor, observer, learner |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, course_space_id, member_kind, member_id, valid_from)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-lms_unit"></a>
## `lms_unit`

Unit (week or topic) of a course space generated from the scheme of work and tagged to objectives

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-102 |
| Pages | LMS-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `course_space_id` → `course_space` | `BINARY(16)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `sort_order` | `SMALLINT` | no |  |  |
| `node_ids` | `JSON` | yes |  |  |
| `scheme_week_id` → `scheme_week` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-lms_content"></a>
## `lms_content`

Content item — note, file, video, audio, link, H5P interactive or state content-library item

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-103, FR-LMS-117 |
| Pages | LMS-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `unit_id` → `lms_unit` | `BINARY(16)` | no |  |  |
| `content_kind` | `VARCHAR(32)` | no |  | values: note, file, video, audio, link, h5p, library_item, live_recording |
| `title` | `VARCHAR(300)` | no |  |  |
| `body` | `TEXT` | yes |  |  |
| `object_key` | `VARCHAR(1024)` | yes |  |  |
| `size_bytes` | `BIGINT` | yes |  | Data-cost estimate before download |
| `library_item_id` → `content_library_item` | `BINARY(16)` | yes |  |  |
| `node_ids` | `JSON` | yes |  |  |
| `is_offline_pack` | `BOOLEAN` | no |  | Included in the weekly offline download |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `library_item_id` → `content_library_item` — cross-zone (ops → registry)

<a id="registry-content_library_item"></a>
## `content_library_item`

State content-library resource, curriculum-aligned, published by the state

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `lms` |
| Origin | ceda |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-LMS-103, FR-OPS-107 |
| Pages | LMS-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `content_kind` | `VARCHAR(32)` | no |  | values: note, file, video, audio, link, h5p, library_item, live_recording |
| `object_key` | `VARCHAR(1024)` | yes |  |  |
| `node_refs` | `JSON` | no |  | Curriculum versions and objectives |
| `licence` | `VARCHAR(120)` | yes |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-assignment"></a>
## `assignment`

Assignment — homework, coursework, CA test, quiz/CBT, practical, portfolio, peer review or digital-skills task

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-104, FR-LMS-105, FR-LMS-106, FR-LMS-109, FR-LMS-121, FR-LMS-125, FR-LMS-127, FR-CUR-108 |
| Pages | LMS-102, LMS-107, LMS-109 |
| Events | LMS.ASSIGNMENT_PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `course_space_id` → `course_space` | `BINARY(16)` | no |  |  |
| `unit_id` → `lms_unit` | `BINARY(16)` | yes |  |  |
| `assignment_kind` | `VARCHAR(32)` | no |  | values: homework, coursework, ca_test, quiz_cbt, practical, portfolio, peer_review, digital_skills_task |
| `title` | `VARCHAR(300)` | no |  |  |
| `instructions` | `TEXT` | no |  |  |
| `node_ids` | `JSON` | yes |  | Objectives assessed |
| `max_mark` | `DECIMAL(7,3)` | yes |  |  |
| `rubric_id` → `rubric` | `BINARY(16)` | yes |  |  |
| `markbook_weight` | `DECIMAL(6,3)` | yes |  |  |
| `assessment_id` → `assessment` | `BINARY(16)` | yes |  | Markbook column fed on release |
| `opens_at` | `DATETIME(6)` | no |  |  |
| `due_at` | `DATETIME(6)` | no |  |  |
| `late_policy` | `VARCHAR(32)` | no |  | values: accept_flag, accept_with_penalty, close_at_due |
| `allow_resubmission` | `BOOLEAN` | no |  |  |
| `group_settings` | `JSON` | yes |  |  |
| `accessibility_options` | `JSON` | yes |  |  |
| `ai_policy` | `VARCHAR(32)` | no |  | values: not_allowed, allowed_with_acknowledgement, encouraged |
| `release_at` | `DATETIME(6)` | yes |  | Scheduled release of marks and feedback |
| `homework_reason` | `VARCHAR(300)` | yes |  | Reason given when the nightly homework limit is exceeded |
| `status` | `VARCHAR(32)` | no |  | values: draft, scheduled, published, closed, marked, released, archived |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, course_space_id, due_at)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-rubric"></a>
## `rubric`

Marking rubric (criteria and levels; digital-skills rubrics map to the framework)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-LMS-110 |
| Pages | LMS-104, LMS-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `criteria` | `JSON` | no |  | Criteria, levels, descriptors, points |
| `framework_ref` | `VARCHAR(60)` | yes |  | Digital-skills framework strand |
| `version` | `INT UNSIGNED` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-submission"></a>
## `submission`

Learner submission version (hashed, timestamped receipt; device and sync times; AI-use declaration)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | append |
| Scope | derived: the assignment's course space |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-107, FR-LMS-108, FR-LMS-116, FR-LMS-121, FR-LMS-119 |
| Pages | LMS-103, LMS-104, LMS-107 |
| Events | LMS.SUBMITTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `assignment_id` → `assignment` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `group_ref` | `VARCHAR(40)` | yes |  |  |
| `version_no` | `SMALLINT` | no |  |  |
| `is_draft` | `BOOLEAN` | no |  |  |
| `text_body` | `TEXT` | yes |  |  |
| `device_submitted_at` | `DATETIME(6)` | yes |  | Device clock (offline work) |
| `synced_at` | `DATETIME(6)` | no |  | Server receipt time |
| `is_late` | `BOOLEAN` | no |  | Teacher decides when device and sync times straddle the due time |
| `receipt_hash` | `BINARY(32)` | no |  |  |
| `ai_declaration` | `VARCHAR(32)` | no |  | values: none_used, used_acknowledged, not_declared |
| `source` | `VARCHAR(32)` | no |  | app, web, scan_split (QR cover sheet), ussd_confirmation · values: app, web, scan_split, ussd_confirmation, offline_sync |
| `client_op_id` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, receipt_hash)
- Unique: (tenant_id, assignment_id, learner_id, version_no)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-submission_file"></a>
## `submission_file`

File in a submission (compressed on upload; up to 200 MB per submission, configurable)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-107 |
| Pages | LMS-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `submission_id` → `submission` | `BINARY(16)` | no |  |  |
| `object_key` | `VARCHAR(1024)` | no |  |  |
| `mime_type` | `VARCHAR(127)` | no |  |  |
| `size_bytes` | `BIGINT` | no |  |  |
| `sha256` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-submission_mark"></a>
## `submission_mark`

Mark and feedback for a submission (rubric, comments, annotations, audio feedback; auto-marked items)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-110, FR-LMS-112, FR-LMS-124 |
| Pages | LMS-104, LMS-105 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `submission_id` → `submission` | `BINARY(16)` | no |  |  |
| `marker_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `score` | `DECIMAL(7,3)` | yes |  |  |
| `rubric_levels` | `JSON` | yes |  |  |
| `feedback` | `TEXT` | yes |  |  |
| `annotation_object_key` | `VARCHAR(1024)` | yes |  |  |
| `audio_feedback_object_key` | `VARCHAR(1024)` | yes |  |  |
| `objective_results` | `JSON` | yes |  |  |
| `is_auto_marked` | `BOOLEAN` | no |  |  |
| `released_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, submission_id)

- Soft reference `marker_staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-extension"></a>
## `extension`

Individual extension with reason (no lateness flag before the extended date)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-109 |
| Pages | LMS-104, LMS-107 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `assignment_id` → `assignment` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `new_due_at` | `DATETIME(6)` | no |  |  |
| `reason` | `VARCHAR(500)` | no |  |  |
| `granted_by` → `staff` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, assignment_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `granted_by` → `staff` — cross-zone (ops → registry)

<a id="ops-originality_report"></a>
## `originality_report`

Originality check result from the configured provider (shown to the teacher only; never an automatic penalty)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `lms` |
| Origin | ceda |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-120 |
| Pages | LMS-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `submission_id` → `submission` | `BINARY(16)` | no |  |  |
| `provider` | `VARCHAR(40)` | no |  |  |
| `similarity_pct` | `DECIMAL(6,3)` | yes |  |  |
| `report_ref` | `VARCHAR(500)` | yes |  |  |
| `checked_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-question"></a>
## `question`

Question-bank item owned by a department or the state (with difficulty and discrimination statistics)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-LMS-113 |
| Pages | LMS-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `bank_code` | `VARCHAR(40)` | no |  |  |
| `item_kind` | `VARCHAR(32)` | no |  | values: single_choice, multiple_choice, true_false, numeric, short_text, essay, matching |
| `stem` | `TEXT` | no |  |  |
| `options` | `JSON` | yes |  |  |
| `answer_key_enc` | `VARBINARY(1024)` | yes | restricted | Envelope-encrypted answer_key. Encrypted until the test closes |
| `node_ids` | `JSON` | yes |  |  |
| `difficulty` | `DECIMAL(7,6)` | yes |  |  |
| `discrimination` | `DECIMAL(5,3)` | yes |  |  |
| `qti_ref` | `VARCHAR(200)` | yes |  | QTI 3.0 identifier |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-quiz_attempt"></a>
## `quiz_attempt`

Online quiz or CBT attempt (randomised items, timing incl. extra-time adjustment, secure-mode, IP and device log)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the assignment's course space |
| Module | `lms` |
| Origin | ceda |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-113, FR-LMS-106 |
| Pages | LMS-106, LMS-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `assignment_id` → `assignment` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `item_order` | `JSON` | no |  |  |
| `responses` | `JSON` | yes |  |  |
| `time_allowed_minutes` | `INT` | no |  | Includes authorised extra time |
| `started_at` | `DATETIME(6)` | no |  |  |
| `submitted_at` | `DATETIME(6)` | yes |  |  |
| `device_log` | `JSON` | yes |  | Secure mode, IP, device |
| `auto_score` | `DECIMAL(7,3)` | yes |  |  |
| `invigilator_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `invigilator_staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-live_class"></a>
## `live_class`

Scheduled live video class (attendance to the register; recording only with consent)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `lms` |
| Origin | ceda |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-114, FR-ADM-101 |
| Pages | LMS-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `course_space_id` → `course_space` | `BINARY(16)` | no |  |  |
| `lesson_occurrence_id` → `lesson_occurrence` | `BINARY(16)` | yes |  |  |
| `starts_at` | `DATETIME(6)` | no |  |  |
| `provider_room_ref` | `VARCHAR(200)` | yes |  |  |
| `recording_object_key` | `VARCHAR(1024)` | yes |  |  |
| `recording_consent_complete` | `BOOLEAN` | no |  |  |
| `captions_object_key` | `VARCHAR(1024)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-discussion_post"></a>
## `discussion_post`

Moderated discussion post (under-13s only in teacher-moderated threads; no private learner-to-learner messages)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the course space |
| Module | `lms` |
| Origin | ceda |
| Retention | `RS-LMS` |
| Requirements | FR-LMS-115 |
| Pages | LMS-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `course_space_id` → `course_space` | `BINARY(16)` | no |  |  |
| `thread_ref` | `BINARY(16)` | no |  |  |
| `author_kind` | `VARCHAR(32)` | no |  | values: learner, staff |
| `author_id` | `BINARY(16)` | no |  |  |
| `body` | `TEXT` | no |  |  |
| `moderation` | `VARCHAR(32)` | no |  | values: visible, pending_moderation, hidden, removed |
| `posted_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-homework_limit"></a>
## `homework_limit`

Nightly homework timetable and load limit for a class

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | effective |
| Scope | none |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-LMS-127 |
| Pages | LMS-109 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `weekday` | `SMALLINT` | no |  |  |
| `max_items` | `SMALLINT` | no |  |  |
| `subject_slots` | `JSON` | yes |  | Subjects expected that night |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, class_group_id, weekday, valid_from)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-digital_skill_level"></a>
## `digital_skill_level`

Digital-skills level per person and strand (device use, information literacy, communication, content creation, safety, computational thinking)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | effective |
| Scope | derived: the person's institution |
| Module | `lms` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LMS-122, FR-LMS-123, FR-LMS-126 |
| Pages | LMS-108, LRN-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `person_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `person_id` | `BINARY(16)` | no |  |  |
| `strand` | `VARCHAR(32)` | no |  | code list `digital_strand` |
| `level` | `SMALLINT` | no |  |  |
| `evidence` | `JSON` | yes |  | LMS activity evidence |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, person_kind, person_id, strand, valid_from)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`
- Check `level_range`: `level BETWEEN 1 AND 5`

<a id="ops-ussd_session"></a>
## `ussd_session`

USSD/SMS feature-phone interaction (due dates, completion confirmation)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `lms` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-LMS-118 |
| Pages | LMS-107 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | yes |  |  |
| `msisdn_hmac` | `BINARY(32)` | no |  |  |
| `action` | `VARCHAR(32)` | no |  | values: list_due, confirm_completed, help |
| `assignment_id` → `assignment` | `BINARY(16)` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

