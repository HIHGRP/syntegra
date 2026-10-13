# ATT — Attendance registers, absence reporting and follow-up, staff sign-in, visitors and evacuation roll call

Daily (AM/PM) and lesson registers with country attendance codes, offline capture with idempotent sync and documented conflict rules (FR-ATT-01–08, 101–106). The register header records who submitted what and when (register compliance, ATT-102); marks are partitioned by month because at state scale they are the largest operational table (≈ 26 million marks per school day for 5 million learners — CEDA §12). Parent-reported absences pre-fill registers; first-day contact and escalation are tracked; evacuation roll calls are built from live attendance, staff sign-in and the visitor log.

Module (system of record): `attendance` · default zone: **ops** · default retention: `RS-ATT`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`attendance_register`](#ops-attendance_register) | ops | transaction | internal | lifecycle | Register header — one daily (AM/PM) or lesson register for a class or section on a date |
| [`attendance_mark`](#ops-attendance_mark) | ops | transaction | confidential | none | Attendance mark per learner per register (partitioned by month; integrity checked nightly) |
| [`absence_report`](#ops-absence_report) | ops | transaction | confidential | lifecycle | Absence reported by a parent (app, WhatsApp, web, office) — acknowledged, accepted (pre-fills code) or queried |
| [`absence_contact`](#ops-absence_contact) | ops | event | confidential | append | First-day absence contact attempt and outcome (escalation and DSL alert for vulnerable learners not reached) |
| [`staff_attendance`](#ops-staff_attendance) | ops | event | confidential | append | Staff sign-in and sign-out (manual, kiosk or biometric device — templates never leave the device) |
| [`visitor_visit`](#ops-visitor_visit) | ops | event | confidential | lifecycle | Visitor log entry (included in evacuation roll calls) |
| [`evacuation_event`](#ops-evacuation_event) | ops | transaction | internal | lifecycle | Evacuation or drill (start, all-clear, timings as safe-schools inspection evidence) |
| [`evacuation_mark`](#ops-evacuation_mark) | ops | event | confidential | append | Roll-call mark for a person at an assembly point (learner, staff or visitor), captured offline |

<a id="ops-attendance_register"></a>
## `attendance_register`

Register header — one daily (AM/PM) or lesson register for a class or section on a date

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `attendance` |
| Origin | ceda |
| Retention | `RS-ATT` |
| Requirements | FR-ATT-01, FR-ATT-04, FR-ATT-104, FR-CMD-112, FR-ATT-106 |
| Pages | ATT-01, ATT-102, ATT-02 |
| Events | ATT.REGISTER_SUBMITTED, ATT.REGISTER_MISSING |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `register_kind` | `VARCHAR(32)` | no |  | values: am, pm, daily, lesson, activity, trip |
| `session_date` | `DATE` | no |  |  |
| `lesson_occurrence_id` → `lesson_occurrence` | `BINARY(16)` | yes |  | Lesson registers |
| `due_at` | `DATETIME(6)` | no |  | Deadline (missing-register nudge at +10 min, escalation at +30 min) |
| `taken_by_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `submitted_at` | `DATETIME(6)` | yes |  |  |
| `device_captured_at` | `DATETIME(6)` | yes |  | Offline capture time |
| `marks_count` | `SMALLINT` | yes |  |  |
| `release_to_parents_at` | `DATETIME(6)` | yes |  | Live or delayed sharing per institution setting |
| `status` | `VARCHAR(32)` | no |  | values: due, in_progress, submitted, late, missing, corrected |
| `lesson_key` | `BINARY(16)` | yes |  | lesson_occurrence_id, or all-zero for daily registers (uniqueness) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, class_group_id, register_kind, session_date, lesson_key)
- Index: (tenant_id, session_date, status)

- Soft reference `taken_by_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-attendance_mark"></a>
## `attendance_mark`

Attendance mark per learner per register (partitioned by month; integrity checked nightly)  

Offline conflict rule: the latest teacher mark wins; office overrides are audited (FR-ATT-03). Each mark carries the idempotency key of the client operation that wrote it.

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | none |
| Scope | derived: the register's class |
| Module | `attendance` |
| Origin | appj |
| Retention | `RS-ATT` |
| Partitioning | range_month on `session_date` |
| Requirements | FR-ATT-01, FR-ATT-02, FR-ATT-03, FR-ATT-05, FR-LMS-114 |
| Pages | ATT-01, ATT-02, LRN-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `register_id` → `attendance_register` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `session_date` **PK** | `DATE` | no |  |  |
| `code` | `VARCHAR(32)` | no |  | Present, Late, Absent (unauthorised), Medical, Excused, Approved activity, Not required · code list `attendance_code` |
| `minutes_late` | `SMALLINT` | yes |  |  |
| `reason_source` | `VARCHAR(32)` | yes |  | values: teacher, parent, office, system |
| `absence_report_id` → `absence_report` | `BINARY(16)` | yes |  |  |
| `recorded_by` | `BINARY(16)` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | teacher, office, kiosk, biometric_device, lms_live_class, parent_prefill · values: teacher, office, kiosk, biometric_device, lms_live_class, parent_prefill, import |
| `client_op_id` | `BINARY(16)` | yes |  | Offline idempotency key |
| `device_captured_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, register_id, learner_id, session_date)
- Index: (tenant_id, learner_id, session_date)

- Soft reference `register_id` → `attendance_register` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)
- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)
- Soft reference `absence_report_id` → `absence_report` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

<a id="ops-absence_report"></a>
## `absence_report`

Absence reported by a parent (app, WhatsApp, web, office) — acknowledged, accepted (pre-fills code) or queried

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `attendance` |
| Origin | appj |
| Retention | `RS-ATT` |
| Requirements | FR-ATT-103, FR-FAM-07, FR-FAM-08, FR-ATT-02, FR-COM-107 |
| Pages | ATT-103, FAM-03, COM-101 |
| Events | ATT.ABSENCE_REPORTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `reported_by_guardian_id` → `guardian` | `BINARY(16)` | yes |  |  |
| `channel` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `from_date` | `DATE` | no |  |  |
| `to_date` | `DATE` | no |  |  |
| `reason` | `VARCHAR(32)` | no |  | code list `absence_reason` |
| `message_text` | `VARCHAR(2000)` | yes |  |  |
| `attachment_document_id` | `BINARY(16)` | yes |  | Medical note |
| `proposed_code` | `VARCHAR(32)` | yes |  | code list `attendance_code` |
| `conversation_id` → `conversation` | `BINARY(16)` | yes |  |  |
| `handled_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: received, acknowledged, accepted, queried, rejected |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `reported_by_guardian_id` → `guardian` — cross-zone (ops → registry)

- Check `dates`: `to_date >= from_date`

<a id="ops-absence_contact"></a>
## `absence_contact`

First-day absence contact attempt and outcome (escalation and DSL alert for vulnerable learners not reached)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | derived: the learner's institution |
| Module | `attendance` |
| Origin | ceda |
| Retention | `RS-ATT` |
| Requirements | FR-ATT-06, FR-ATT-101 |
| Pages | ATT-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `session_date` | `DATE` | no |  |  |
| `contacted_guardian_id` → `guardian` | `BINARY(16)` | yes |  |  |
| `channel` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `message_id` → `message` | `BINARY(16)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | no |  | values: reached_reason_given, reached_no_reason, no_answer, message_sent, failed |
| `reason_given` | `VARCHAR(500)` | yes |  |  |
| `escalated_to` | `VARCHAR(32)` | yes |  | values: pastoral_lead, dsl, head, lga |
| `attempted_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `contacted_guardian_id` → `guardian` — cross-zone (ops → registry)
- Soft reference `message_id` → `message` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

<a id="ops-staff_attendance"></a>
## `staff_attendance`

Staff sign-in and sign-out (manual, kiosk or biometric device — templates never leave the device)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | owned |
| Module | `attendance` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Partitioning | range_month on `signed_on` |
| Requirements | FR-ATT-08, FR-ATT-105 |
| Pages | ATT-101, ATT-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `signed_on` **PK** | `DATE` | no |  |  |
| `direction` | `VARCHAR(32)` | no |  | values: in, out |
| `at` | `DATETIME(6)` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | values: teacher, office, kiosk, biometric_device, lms_live_class, parent_prefill, import |
| `device_ref` | `VARCHAR(64)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-visitor_visit"></a>
## `visitor_visit`

Visitor log entry (included in evacuation roll calls)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `attendance` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-ATT-102, FR-ATT-105 |
| Pages | ATT-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `visitor_name` | `VARCHAR(200)` | no |  |  |
| `organisation` | `VARCHAR(300)` | yes |  |  |
| `phone` | `VARCHAR(16)` | yes |  |  |
| `host_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `purpose` | `VARCHAR(300)` | yes |  |  |
| `badge_no` | `VARCHAR(20)` | yes |  |  |
| `arrived_at` | `DATETIME(6)` | no |  |  |
| `departed_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `host_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-evacuation_event"></a>
## `evacuation_event`

Evacuation or drill (start, all-clear, timings as safe-schools inspection evidence)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `attendance` |
| Origin | appj |
| Retention | `RS-ATT` |
| Requirements | FR-ATT-102, FR-ATT-105 |
| Pages | ATT-101 |
| Events | ATT.EVACUATION_STARTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `campus_id` → `campus` | `BINARY(16)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: fire, drill, lockdown, invacuation, other |
| `started_at` | `DATETIME(6)` | no |  |  |
| `all_clear_at` | `DATETIME(6)` | yes |  |  |
| `incident_lead_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `expected_count` | `INT UNSIGNED` | yes |  |  |
| `accounted_count` | `INT UNSIGNED` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: in_progress, all_clear, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `campus_id` → `campus` — cross-zone (ops → registry)
- Soft reference `incident_lead_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-evacuation_mark"></a>
## `evacuation_mark`

Roll-call mark for a person at an assembly point (learner, staff or visitor), captured offline

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `attendance` |
| Origin | appj |
| Retention | `RS-ATT` |
| Requirements | FR-ATT-105 |
| Pages | ATT-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `evacuation_event_id` → `evacuation_event` | `BINARY(16)` | no |  |  |
| `person_kind` | `VARCHAR(32)` | no |  | values: learner, staff, visitor |
| `person_id` | `BINARY(16)` | no |  |  |
| `assembly_point` | `VARCHAR(60)` | no |  |  |
| `marshal_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `state` | `VARCHAR(32)` | no |  | values: safe, missing, absent_today, left_site |
| `marked_at` | `DATETIME(6)` | no |  |  |
| `client_op_id` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, evacuation_event_id, person_kind, person_id, state)

- Soft reference `marshal_staff_id` → `staff` — cross-zone (ops → registry)

