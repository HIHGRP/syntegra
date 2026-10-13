# TIM — Timetable, lesson occurrences, cover rota, duties and room bookings

Timetables built with hard constraints (clashes, capacity, accessibility, mandatory curriculum hours) and soft constraints, solved with CP-SAT and edited by hand (FR-TIM-01–07, 101–104). A published timetable version expands into recurring lessons; lesson occurrences are materialised on the day when something happens to them (register, cover, delivery log, on-report rating) so registers, cover (G8) and delivery evidence (G6) refer to one dated lesson. Duty and on-call rotas, room and resource bookings and external lettings are here.

Module (system of record): `timetable` · default zone: **ops** · default retention: `RS-OPS-7`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`timetable`](#ops-timetable) | ops | config | internal | versioned | Timetable version for an institution and session (one- or two-week cycles, structures per year group) |
| [`period_structure`](#ops-period_structure) | ops | config | internal | none | Bell schedule — named periods with times per day of the cycle and per year-group structure |
| [`timetable_lesson`](#ops-timetable_lesson) | ops | config | internal | none | Recurring scheduled lesson (class or section × subject × teacher × room × cycle slot) |
| [`lesson_occurrence`](#ops-lesson_occurrence) | ops | transaction | internal | lifecycle | Dated occurrence of a lesson, materialised when a register, cover, delivery log or rating refers to it |
| [`duty_rota`](#ops-duty_rota) | ops | config | internal | effective | Break, duty or on-call rota slot (fair distribution; on-call responders for BEH-105) |
| [`room_booking`](#ops-room_booking) | ops | transaction | internal | lifecycle | Booking of a room or shared resource (labs, halls, laptop trolleys) — recurring, approval rules, weekly limits |
| [`letting`](#ops-letting) | ops | transaction | internal | lifecycle | External letting of facilities with charges posted to finance |

<a id="ops-timetable"></a>
## `timetable`

Timetable version for an institution and session (one- or two-week cycles, structures per year group)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `timetable` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-TIM-01, FR-TIM-02, FR-TIM-03, FR-TIM-101, FR-TIM-07 |
| Pages | TIM-01, TIM-02 |
| Events | TT.PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `cycle_weeks` | `SMALLINT` | no |  |  |
| `sessions_per_day` | `SMALLINT` | no |  | Double-shift schools |
| `solver_run` | `JSON` | yes |  | Constraint set, objective value and unmet soft constraints |
| `unmet_requirements` | `JSON` | yes |  | Mandatory hours not met (publication blocked unless an exception exists) |
| `exception_id` → `policy_exception` | `BINARY(16)` | yes |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, period_id, version)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)
- Soft reference `exception_id` → `policy_exception` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-period_structure"></a>
## `period_structure`

Bell schedule — named periods with times per day of the cycle and per year-group structure

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | derived: the timetable |
| Module | `timetable` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-TIM-101 |
| Pages | TIM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `timetable_id` → `timetable` | `BINARY(16)` | no |  |  |
| `structure_code` | `VARCHAR(20)` | no |  | Year-group structure |
| `cycle_day` | `SMALLINT` | no |  |  |
| `period_code` | `VARCHAR(16)` | no |  |  |
| `starts_at` | `TIME` | no |  |  |
| `ends_at` | `TIME` | no |  |  |
| `is_teaching` | `BOOLEAN` | no |  | Breaks and registration periods are not teaching |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, timetable_id, structure_code, cycle_day, period_code)

<a id="ops-timetable_lesson"></a>
## `timetable_lesson`

Recurring scheduled lesson (class or section × subject × teacher × room × cycle slot)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | derived: the timetable |
| Module | `timetable` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-TIM-01, FR-TIM-04, FR-CUR-15 |
| Pages | TIM-01, TIM-02, ATT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `timetable_id` → `timetable` | `BINARY(16)` | no |  |  |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `class_subject_plan_id` → `class_subject_plan` | `BINARY(16)` | yes |  |  |
| `course_section_id` → `course_section` | `BINARY(16)` | yes |  |  |
| `subject_id` → `subject` | `BINARY(16)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `cycle_day` | `SMALLINT` | no |  |  |
| `period_code` | `VARCHAR(16)` | no |  |  |
| `duration_minutes` | `INT` | no |  |  |
| `lesson_kind` | `VARCHAR(32)` | no |  | lesson, lecture, tutorial, practical, live_class · values: lesson, lecture, tutorial, practical, live_class, registration |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, timetable_id, cycle_day, period_code)
- Index: (tenant_id, staff_id)
- Index: (tenant_id, class_group_id)

- Soft reference `subject_id` → `subject` — cross-zone (ops → registry)
- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-lesson_occurrence"></a>
## `lesson_occurrence`

Dated occurrence of a lesson, materialised when a register, cover, delivery log or rating refers to it

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `timetable` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-ATT-01, FR-TIM-04, FR-STF-06 |
| Pages | ATT-01, TIM-02, TIM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `timetable_lesson_id` → `timetable_lesson` | `BINARY(16)` | no |  |  |
| `occurs_on` | `DATE` | no |  |  |
| `starts_at` | `DATETIME(6)` | no |  |  |
| `ends_at` | `DATETIME(6)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  | Teacher actually responsible (cover changes it) |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `is_remote` | `BOOLEAN` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: scheduled, taught, covered, cancelled, remote |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, timetable_lesson_id, occurs_on)
- Index: (tenant_id, staff_id, occurs_on)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-duty_rota"></a>
## `duty_rota`

Break, duty or on-call rota slot (fair distribution; on-call responders for BEH-105)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | effective |
| Scope | owned |
| Module | `timetable` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-TIM-102, FR-BEH-113 |
| Pages | TIM-03, BEH-105 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `duty_kind` | `VARCHAR(32)` | no |  | values: break_duty, lunch_duty, gate_duty, on_call, bus_duty |
| `location` | `VARCHAR(120)` | yes |  |  |
| `cycle_day` | `SMALLINT` | no |  |  |
| `period_code` | `VARCHAR(16)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `backup_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `backup_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-room_booking"></a>
## `room_booking`

Booking of a room or shared resource (labs, halls, laptop trolleys) — recurring, approval rules, weekly limits

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `timetable` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-TIM-06, FR-TIM-103, FR-MED-101 |
| Pages | TIM-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `asset_id` → `asset` | `BINARY(16)` | yes |  | Shared resource |
| `booked_by` | `BINARY(16)` | no |  |  |
| `purpose` | `VARCHAR(300)` | no |  |  |
| `starts_at` | `DATETIME(6)` | no |  |  |
| `ends_at` | `DATETIME(6)` | no |  |  |
| `recurrence` | `JSON` | yes |  | RRULE for recurring bookings |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, confirmed, declined, cancelled, completed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, room_id, starts_at)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `window`: `ends_at > starts_at`

<a id="ops-letting"></a>
## `letting`

External letting of facilities with charges posted to finance

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `timetable` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-TIM-104 |
| Pages | TIM-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `room_booking_id` → `room_booking` | `BINARY(16)` | no |  |  |
| `hirer_name` | `VARCHAR(300)` | no |  |  |
| `hirer_contact` | `VARCHAR(200)` | yes |  |  |
| `charge_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, confirmed, declined, cancelled, completed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

