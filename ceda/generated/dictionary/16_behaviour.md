# BEH — Behaviour, rewards, seating plans and influences, intelligence events, detentions, on-call and on-report

Versioned behaviour policies built on the state minimum framework, two-tap logging online or offline, badges, data-rich seating plans with board-safe display and logged printing, pairwise influence evidence (≥ 20 shared-lesson events, no protected characteristics), threshold rules ("intelligence events") with simulation and reversible firings, a detention ladder with parent notice and transport checks, on-call requests routed by the timetable rota and on-report cards (MFS §18.4–18.5, FR-BEH-01–04, 101–115). No rule, agent or AI applies a sanction above detention (§18.11).

Module (system of record): `success` · default zone: **ops** · default retention: `RS-BEH`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`behaviour_framework`](#registry-behaviour_framework) | registry | config | public | versioned | State minimum behaviour framework (required categories, maximum points, head-decision outcomes) |
| [`behaviour_policy`](#ops-behaviour_policy) | ops | config | internal | versioned | Versioned behaviour policy of an institution (immutable once published; never re-scores past events) |
| [`behaviour_type`](#ops-behaviour_type) | ops | config | internal | versioned | Positive or negative behaviour with icon, points, default outcome and use in reports/influences |
| [`behaviour_event`](#ops-behaviour_event) | ops | event | confidential | lifecycle | Behaviour log entry (two taps from register, class list, seating plan or app; online or offline) |
| [`reward_badge`](#ops-reward_badge) | ops | config | internal | lifecycle | Achievement badge awarded at a points threshold or by rule (recognition only; never a credential) |
| [`badge_award`](#ops-badge_award) | ops | event | confidential | append | Badge awarded to a learner |
| [`room_layout`](#ops-room_layout) | ops | config | internal | none | Reusable room desk layout for seating plans |
| [`seating_field_set`](#ops-seating_field_set) | ops | config | internal | none | Set of up to 16 learner data fields shown on seating plans for a class, subject or level |
| [`seating_plan`](#ops-seating_plan) | ops | transaction | confidential | lifecycle | Seating plan for a class in a room (drag-and-drop or strategy-generated) |
| [`seating_plan_print`](#ops-seating_plan_print) | ops | event | confidential | append | Logged, watermarked print of a seating plan for observers or inspectors |
| [`influence_score`](#ops-influence_score) | ops | projection | confidential | none | Pairwise influence between two learners from behaviour in shared lessons (adjacent vs apart; ≥ 20 events) |
| [`intel_rule`](#ops-intel_rule) | ops | config | internal | versioned | Threshold rule over behaviour, attendance, homework or wellbeing data with actions (simulated before activation) |
| [`intel_firing`](#ops-intel_firing) | ops | event | confidential | append | Each time an intelligence rule fires (append-only; staff may reverse its effects) |
| [`intel_firing_reversal`](#ops-intel_firing_reversal) | ops | event | confidential | append | Staff reversal of an intelligence-rule firing's effects |
| [`detention_type`](#ops-detention_type) | ops | config | internal | lifecycle | Detention level in the institution ladder (duration, default room and supervisor, escalation to next level) |
| [`detention`](#ops-detention) | ops | transaction | confidential | lifecycle | Detention session and attendance (Attended, Pending, Not attended, Escalated) |
| [`oncall_request`](#ops-oncall_request) | ops | transaction | confidential | lifecycle | On-call request raised from a classroom (routed to the rota; acknowledgement target 2 min; emergency reason) |
| [`on_report_card`](#ops-on_report_card) | ops | transaction | confidential | lifecycle | Learner on report for a period at tutor, head-of-year or senior-leadership level |
| [`on_report_target`](#ops-on_report_target) | ops | config | confidential | none | Personalised target on an on-report card |
| [`on_report_rating`](#ops-on_report_rating) | ops | event | confidential | append | Rating and comment for a target in one lesson, or a parent or learner comment (append-only) |

<a id="registry-behaviour_framework"></a>
## `behaviour_framework`

State minimum behaviour framework (required categories, maximum points, head-decision outcomes)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-106 |
| Pages | BEH-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `version` | `INT UNSIGNED` | no |  |  |
| `required_categories` | `JSON` | no |  |  |
| `max_points_per_event` | `SMALLINT` | no |  |  |
| `head_decision_outcomes` | `JSON` | no |  | Outcomes above detention |
| `after_school_detention_rule` | `JSON` | yes |  | Per-LGA permission and default parent notice (D21) |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `effective_from` | `DATE` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, version)

<a id="ops-behaviour_policy"></a>
## `behaviour_policy`

Versioned behaviour policy of an institution (immutable once published; never re-scores past events)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-106, FR-BEH-01 |
| Pages | BEH-101 |
| Events | BEH.POLICY_PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `framework_version` | `INT UNSIGNED` | no |  | State framework version it conforms to |
| `version` | `INT UNSIGNED` | no |  |  |
| `missing_homework_is_behaviour` | `BOOLEAN` | no |  |  |
| `effective_from` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, version)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-behaviour_type"></a>
## `behaviour_type`

Positive or negative behaviour with icon, points, default outcome and use in reports/influences

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | none |
| Module | `success` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-106 |
| Pages | BEH-101, BEH-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `policy_id` → `behaviour_policy` | `BINARY(16)` | no |  |  |
| `code` | `VARCHAR(32)` | no |  |  |
| `label` | `VARCHAR(300)` | no |  |  |
| `polarity` | `VARCHAR(32)` | no |  | values: positive, negative |
| `category` | `VARCHAR(32)` | no |  | bullying, violence, lateness, positive conduct … · code list `behaviour_category` |
| `points` | `SMALLINT` | no |  |  |
| `icon` | `VARCHAR(40)` | yes |  |  |
| `default_outcome` | `VARCHAR(32)` | yes |  | values: none, warning, detention, on_report, parent_contact, intervention, internal_exclusion, suspension, exclusion |
| `detention_type_id` → `detention_type` | `BINARY(16)` | yes |  |  |
| `counts_in_reports` | `BOOLEAN` | no |  |  |
| `counts_in_influences` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, policy_id, code)

<a id="ops-behaviour_event"></a>
## `behaviour_event`

Behaviour log entry (two taps from register, class list, seating plan or app; online or offline)  

Exclusions and suspensions are recorded as head decisions with reason and appeal route (outcome above detention).

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-01, FR-BEH-02, FR-BEH-03, FR-BEH-04, FR-BEH-107 |
| Pages | BEH-01, BEH-02, BEH-102 |
| Events | BEH.EVENT_RECORDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `behaviour_type_id` → `behaviour_type` | `BINARY(16)` | no |  |  |
| `points` | `SMALLINT` | no |  | Points of the policy version in force |
| `lesson_occurrence_id` → `lesson_occurrence` | `BINARY(16)` | yes |  |  |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `location` | `VARCHAR(120)` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `recorded_by_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `description` | `VARCHAR(2000)` | yes |  |  |
| `target_learner_ids` | `JSON` | yes |  | Targets of bullying (routes to the pastoral lead) |
| `outcome` | `VARCHAR(32)` | yes |  | values: none, warning, detention, on_report, parent_contact, intervention, internal_exclusion, suspension, exclusion |
| `decision_by` | `BINARY(16)` | yes |  | Head for outcomes above detention |
| `appeal_status` | `VARCHAR(32)` | yes |  | values: none, lodged, upheld, dismissed |
| `client_op_id` | `BINARY(16)` | yes |  | Offline idempotency key |
| `reversed_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, learner_id, occurred_at)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `recorded_by_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-reward_badge"></a>
## `reward_badge`

Achievement badge awarded at a points threshold or by rule (recognition only; never a credential)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-108 |
| Pages | BEH-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  |  |
| `label` | `VARCHAR(300)` | no |  |  |
| `rule` | `JSON` | no |  | Points threshold or rule |
| `image_ref` | `VARCHAR(1024)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-badge_award"></a>
## `badge_award`

Badge awarded to a learner

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-108, FR-OPS-05 |
| Pages | BEH-101, LRN-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `badge_id` → `reward_badge` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `awarded_at` | `DATETIME(6)` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | values: points_threshold, rule, staff_award, activity |
| `intel_firing_id` → `intel_firing` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-room_layout"></a>
## `room_layout`

Reusable room desk layout for seating plans

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-110 |
| Pages | BEH-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `room_id` → `room` | `BINARY(16)` | no |  |  |
| `name` | `VARCHAR(80)` | no |  |  |
| `desks` | `JSON` | no |  | Desk positions and labels |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-seating_field_set"></a>
## `seating_field_set`

Set of up to 16 learner data fields shown on seating plans for a class, subject or level

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-110, FR-BEH-102 |
| Pages | BEH-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(80)` | no |  |  |
| `applies_to` | `JSON` | no |  | Class, subject or level |
| `fields` | `JSON` | no |  | Up to 16 field codes (SEND, free meals/CCT, gifted, working and target grade RAG, attendance, home language) |
| `board_safe_fields` | `JSON` | no |  | Fields still shown in board-safe view (never sensitive ones) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `max_fields`: `JSON_LENGTH(`fields`) <= 16`

<a id="ops-seating_plan"></a>
## `seating_plan`

Seating plan for a class in a room (drag-and-drop or strategy-generated)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the class |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-101, FR-BEH-110 |
| Pages | BEH-102, ACA-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | yes |  |  |
| `room_layout_id` → `room_layout` | `BINARY(16)` | no |  |  |
| `field_set_id` → `seating_field_set` | `BINARY(16)` | yes |  |  |
| `strategy` | `VARCHAR(32)` | yes |  | values: manual, ability, mixed_ability, alphabetical, random, separate_negative_influences |
| `placements` | `JSON` | no |  | Learner → desk |
| `is_active` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `subject_id` → `subject` — cross-zone (ops → registry)

<a id="ops-seating_plan_print"></a>
## `seating_plan_print`

Logged, watermarked print of a seating plan for observers or inspectors

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-110 |
| Pages | BEH-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `seating_plan_id` → `seating_plan` | `BINARY(16)` | no |  |  |
| `printed_by` | `BINARY(16)` | no |  |  |
| `viewer_name` | `VARCHAR(200)` | no |  | Watermarked on the print |
| `printed_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-influence_score"></a>
## `influence_score`

Pairwise influence between two learners from behaviour in shared lessons (adjacent vs apart; ≥ 20 events)

| | |
|---|---|
| Zone | ops |
| Kind | projection |
| Classification | confidential |
| History | none |
| Scope | derived: the class; visible only to its teachers and pastoral staff |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-109 |
| Pages | BEH-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `learner_a_id` → `learner` | `BINARY(16)` | no |  |  |
| `learner_b_id` → `learner` | `BINARY(16)` | no |  |  |
| `shared_events` | `INT UNSIGNED` | no |  |  |
| `negative_adjacent` | `INT UNSIGNED` | no |  |  |
| `negative_apart` | `INT UNSIGNED` | no |  |  |
| `positive_adjacent` | `INT UNSIGNED` | no |  |  |
| `positive_apart` | `INT UNSIGNED` | no |  |  |
| `computed_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, class_group_id, learner_a_id, learner_b_id)

- Soft reference `learner_a_id` → `learner` — cross-zone (ops → registry)
- Soft reference `learner_b_id` → `learner` — cross-zone (ops → registry)

- Check `ordered_pair`: `learner_a_id < learner_b_id`

<a id="ops-intel_rule"></a>
## `intel_rule`

Threshold rule over behaviour, attendance, homework or wellbeing data with actions (simulated before activation)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-105, FR-BEH-115 |
| Pages | BEH-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `source_data` | `VARCHAR(32)` | no |  | values: behaviour, attendance, homework, wellbeing, mixed |
| `rule_expression` | `JSON` | no |  | e.g. 10 negative events in 7 days; 100 positive points |
| `actions` | `JSON` | no |  | notify, message_parent, detention, on_report, intervention, badge, dsl_alert |
| `is_positive_milestone` | `BOOLEAN` | no |  |  |
| `simulation_result` | `JSON` | yes |  | Learners who would have triggered in the last 30 days |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-intel_firing"></a>
## `intel_firing`

Each time an intelligence rule fires (append-only; staff may reverse its effects)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-115 |
| Pages | BEH-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `rule_id` → `intel_rule` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `evidence` | `JSON` | no |  |  |
| `actions_taken` | `JSON` | no |  |  |
| `agent_action_id` → `agent_action` | `BINARY(16)` | yes |  | Behaviour agent action |
| `fired_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `agent_action_id` → `agent_action` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

<a id="ops-intel_firing_reversal"></a>
## `intel_firing_reversal`

Staff reversal of an intelligence-rule firing's effects

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-115 |
| Pages | BEH-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `firing_id` → `intel_firing` | `BINARY(16)` | no |  |  |
| `reversed_by` | `BINARY(16)` | no |  |  |
| `reason` | `VARCHAR(500)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, firing_id)

<a id="ops-detention_type"></a>
## `detention_type`

Detention level in the institution ladder (duration, default room and supervisor, escalation to next level)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-BEH-104, FR-BEH-111 |
| Pages | BEH-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  | Lunchtime, Head of year, Senior leadership |
| `ladder_level` | `SMALLINT` | no |  |  |
| `duration_minutes` | `INT` | no |  |  |
| `default_room_id` → `room` | `BINARY(16)` | yes |  |  |
| `default_supervisor_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `is_after_school` | `BOOLEAN` | no |  |  |
| `parent_notice_hours` | `SMALLINT` | no |  |  |
| `next_level_id` → `detention_type` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `default_supervisor_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-detention"></a>
## `detention`

Detention session and attendance (Attended, Pending, Not attended, Escalated)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-104, FR-BEH-111 |
| Pages | BEH-104 |
| Events | BEH.DETENTION_SET |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `detention_type_id` → `detention_type` | `BINARY(16)` | no |  |  |
| `behaviour_event_id` → `behaviour_event` | `BINARY(16)` | yes |  |  |
| `intel_firing_id` → `intel_firing` | `BINARY(16)` | yes |  |  |
| `escalated_from_id` → `detention` | `BINARY(16)` | yes |  |  |
| `scheduled_at` | `DATETIME(6)` | no |  |  |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `supervisor_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `parent_notified_at` | `DATETIME(6)` | yes |  |  |
| `transport_checked` | `BOOLEAN` | no |  |  |
| `minutes_owed` | `INT` | no |  |  |
| `attendance` | `VARCHAR(32)` | no |  | values: pending, attended, not_attended, escalated, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `supervisor_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-oncall_request"></a>
## `oncall_request`

On-call request raised from a classroom (routed to the rota; acknowledgement target 2 min; emergency reason)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-BEH-113 |
| Pages | BEH-105 |
| Events | BEH.ONCALL_RAISED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `class_group_id` → `class_group` | `BINARY(16)` | yes |  |  |
| `raised_by_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `reason` | `VARCHAR(32)` | no |  | values: behaviour, medical, safeguarding, emergency, other |
| `learner_id` → `learner` | `BINARY(16)` | yes |  |  |
| `responder_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `raised_at` | `DATETIME(6)` | no |  |  |
| `acknowledged_at` | `DATETIME(6)` | yes |  |  |
| `escalated_at` | `DATETIME(6)` | yes |  |  |
| `resolved_at` | `DATETIME(6)` | yes |  |  |
| `outcome` | `VARCHAR(500)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: raised, acknowledged, escalated, resolved, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `raised_by_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `responder_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-on_report_card"></a>
## `on_report_card`

Learner on report for a period at tutor, head-of-year or senior-leadership level

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-112 |
| Pages | BEH-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `level` | `VARCHAR(32)` | no |  | values: tutor, head_of_year, senior_leadership |
| `owner_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `outcome` | `VARCHAR(1000)` | yes |  |  |
| `intervention_id` → `intervention` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, completed, ended_early |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `owner_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-on_report_target"></a>
## `on_report_target`

Personalised target on an on-report card

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-112 |
| Pages | BEH-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `card_id` → `on_report_card` | `BINARY(16)` | no |  |  |
| `target_text` | `VARCHAR(300)` | no |  |  |
| `sort_order` | `SMALLINT` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-on_report_rating"></a>
## `on_report_rating`

Rating and comment for a target in one lesson, or a parent or learner comment (append-only)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `success` |
| Origin | appj |
| Retention | `RS-BEH` |
| Requirements | FR-BEH-112 |
| Pages | BEH-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `card_id` → `on_report_card` | `BINARY(16)` | no |  |  |
| `target_id` → `on_report_target` | `BINARY(16)` | yes |  |  |
| `lesson_occurrence_id` → `lesson_occurrence` | `BINARY(16)` | yes |  |  |
| `author_kind` | `VARCHAR(32)` | no |  | values: teacher, owner, parent, learner, staff |
| `author_id` | `BINARY(16)` | no |  |  |
| `rating` | `SMALLINT` | yes |  |  |
| `comment` | `VARCHAR(1000)` | yes |  |  |
| `rated_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

