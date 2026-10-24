# SEN — SEND and inclusion, gifted and talented, wellbeing, interventions and personal learning plans

Need detail, statutory plans, provision and therapy referrals are special category and live in the vault; teachers see only authorised adjustments, which live in the ops zone and feed timetabling, exam access arrangements, LMS assignments and class pages automatically (FR-SEN-01–07, 101–102). Wellbeing check-ins and concerns are vault records; keyword screening alerts the DSL but never labels a learner (FR-WEL-01–04, 101–103). Interventions record baseline, target and outcome for the closed loop. Personal learning plans are available to every learner (FR-ILP-101–104).

Module (system of record): `success` · default zone: **vault** · default retention: `RS-SEND`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`send_profile`](#vault-send_profile) | vault | master | special | lifecycle | SEND 360 support profile (need areas, support level, plan type, strengths, communication, learner voice) |
| [`send_need`](#vault-send_need) | vault | master | special | effective | Need area of a learner (coded; diagnosis detail encrypted) |
| [`support_plan`](#vault-support_plan) | vault | transaction | special | versioned | IEP/ISP or statutory plan (outcomes, provision, participants, review cycle; overdue reviews alerted) |
| [`support_plan_review`](#vault-support_plan_review) | vault | event | special | append | Review of a support plan |
| [`provision`](#vault-provision) | vault | config | special | lifecycle | Provision type offered (type, staff, hours, cost) for the provision map |
| [`provision_allocation`](#vault-provision_allocation) | vault | link | special | effective | Learner allocated to a provision, with impact measured |
| [`external_referral`](#vault-external_referral) | vault | transaction | special | lifecycle | Therapy or external-agency referral (speech, occupational, educational psychology, health) with consent and returned reports |
| [`adjustment`](#ops-adjustment) | ops | master | confidential | effective | Authorised reasonable adjustment — the teacher-visible layer (extra time, large print, read-aloud, seating, access arrangements) |
| [`gifted_register_entry`](#ops-gifted_register_entry) | ops | master | confidential | effective | Gifted and talented register entry with provision tracking |
| [`wellbeing_checkin`](#vault-wellbeing_checkin) | vault | event | special | append | Opt-in, age-appropriate wellbeing check-in or staff observation (five-point scale) |
| [`wellbeing_concern`](#vault-wellbeing_concern) | vault | transaction | special | lifecycle | Wellbeing concern reported by a learner, parent or staff member (routed to a pastoral lead; DSL alert on keywords) |
| [`intervention`](#ops-intervention) | ops | transaction | confidential | lifecycle | Intervention with baseline, target, learners, lead, review date and outcome (closed loop) |
| [`learning_plan_template`](#ops-learning_plan_template) | ops | config | internal | versioned | Reusable personal learning plan template (state or institution; catch-up, re-entry, gifted extension, exam readiness, TVET pathway) |
| [`learning_plan`](#ops-learning_plan) | ops | transaction | confidential | lifecycle | Personal learning plan for a learner (any learner, not only SEND) |
| [`learning_plan_goal`](#ops-learning_plan_goal) | ops | config | confidential | lifecycle | Goal in a learning plan linked to curriculum objectives and target grades |
| [`learning_plan_entry`](#ops-learning_plan_entry) | ops | event | confidential | append | Action, learner reflection, parent comment, evidence or review on a learning plan (append-only) |

<a id="vault-send_profile"></a>
## `send_profile`

SEND 360 support profile (need areas, support level, plan type, strengths, communication, learner voice)

| | |
|---|---|
| Zone | vault |
| Kind | master |
| Classification | special |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-01, FR-SEN-02, FR-SEN-03, FR-SEN-07 |
| Pages | SEN-01, SEN-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `support_level` | `VARCHAR(32)` | no |  | code list `send_support_level` |
| `plan_type` | `VARCHAR(32)` | yes |  | code list `send_plan_type` |
| `profile` | `MEDIUMBLOB` | no | special | Strengths, needs, preferences, communication, strategies, assistive technology, learner and parent voice |
| `senco_user_id` | `BINARY(16)` | yes |  |  |
| `review_due_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-send_need"></a>
## `send_need`

Need area of a learner (coded; diagnosis detail encrypted)

| | |
|---|---|
| Zone | vault |
| Kind | master |
| Classification | special |
| History | effective |
| Scope | none |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-01 |
| Pages | SEN-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `profile_id` → `send_profile` | `BINARY(16)` | no |  |  |
| `need_area` | `VARCHAR(32)` | no |  | code list `send_need_area` |
| `is_primary` | `BOOLEAN` | no |  |  |
| `detail` | `MEDIUMBLOB` | yes | special |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="vault-support_plan"></a>
## `support_plan`

IEP/ISP or statutory plan (outcomes, provision, participants, review cycle; overdue reviews alerted)

| | |
|---|---|
| Zone | vault |
| Kind | transaction |
| Classification | special |
| History | versioned |
| Scope | none |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-04 |
| Pages | SEN-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `profile_id` → `send_profile` | `BINARY(16)` | no |  |  |
| `plan_type` | `VARCHAR(32)` | no |  | code list `send_plan_type` |
| `version` | `INT UNSIGNED` | no |  |  |
| `outcomes` | `MEDIUMBLOB` | no | special |  |
| `participants` | `JSON` | yes |  |  |
| `review_cycle_months` | `SMALLINT` | no |  |  |
| `next_review_on` | `DATE` | no |  |  |
| `linked_learning_plan_id` | `BINARY(16)` | yes |  | Personal learning plan (ops) |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="vault-support_plan_review"></a>
## `support_plan_review`

Review of a support plan

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | none |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-04 |
| Pages | SEN-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `plan_id` → `support_plan` | `BINARY(16)` | no |  |  |
| `reviewed_on` | `DATE` | no |  |  |
| `notes` | `MEDIUMBLOB` | no | special |  |
| `attendees` | `JSON` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="vault-provision"></a>
## `provision`

Provision type offered (type, staff, hours, cost) for the provision map

| | |
|---|---|
| Zone | vault |
| Kind | config |
| Classification | special |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-05, FR-SEN-101 |
| Pages | SEN-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `provision_kind` | `VARCHAR(32)` | no |  | code list `provision_kind` |
| `staff_ids` | `JSON` | yes |  |  |
| `hours_per_week` | `DECIMAL(5,2)` | yes |  |  |
| `cost_per_term_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-provision_allocation"></a>
## `provision_allocation`

Learner allocated to a provision, with impact measured

| | |
|---|---|
| Zone | vault |
| Kind | link |
| Classification | special |
| History | effective |
| Scope | none |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-05 |
| Pages | SEN-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `provision_id` → `provision` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `impact` | `MEDIUMBLOB` | yes | special |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="vault-external_referral"></a>
## `external_referral`

Therapy or external-agency referral (speech, occupational, educational psychology, health) with consent and returned reports

| | |
|---|---|
| Zone | vault |
| Kind | transaction |
| Classification | special |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-102 |
| Pages | SEN-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `agency_kind` | `VARCHAR(32)` | no |  | code list `referral_agency` |
| `agency_name` | `VARCHAR(200)` | no |  |  |
| `consent_record_id` | `BINARY(16)` | no |  | Consent (ops) |
| `referred_on` | `DATE` | no |  |  |
| `report_document_id` | `BINARY(16)` | yes |  | Returned report stored in the support profile |
| `status` | `VARCHAR(32)` | no |  | values: drafted, sent, acknowledged, accepted, declined, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-adjustment"></a>
## `adjustment`

Authorised reasonable adjustment — the teacher-visible layer (extra time, large print, read-aloud, seating, access arrangements)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | effective |
| Scope | derived: the learner's classes |
| Module | `success` |
| Origin | appj |
| Retention | `RS-SEND` |
| Requirements | FR-SEN-03, FR-SEN-06, FR-LMS-106, FR-BEH-102 |
| Pages | SEN-02, ACA-05, LMS-102 |
| Events | SEN.ADJUSTMENT_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `adjustment_kind` | `VARCHAR(32)` | no |  | code list `adjustment_kind` |
| `parameters` | `JSON` | yes |  | e.g. extra_time_pct 25, font_scale 1.5 |
| `applies_to` | `JSON` | no |  | lessons, assessments, exams, lms, rooms |
| `authorised_by` | `BINARY(16)` | no |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-gifted_register_entry"></a>
## `gifted_register_entry`

Gifted and talented register entry with provision tracking

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | effective |
| Scope | derived: the learner's institution |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-SEN-101 |
| Pages | SEN-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `domain_area` | `VARCHAR(32)` | no |  | code list `gifted_domain` |
| `evidence` | `VARCHAR(1000)` | yes |  |  |
| `provision_note` | `VARCHAR(1000)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="vault-wellbeing_checkin"></a>
## `wellbeing_checkin`

Opt-in, age-appropriate wellbeing check-in or staff observation (five-point scale)

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | owned |
| Module | `success` |
| Origin | ceda |
| Retention | `RS-SEND` |
| Requirements | FR-WEL-01, FR-WEL-102 |
| Pages | WEL-01, WEL-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | values: learner, parent, staff |
| `score` | `SMALLINT` | no |  |  |
| `tracker_code` | `VARCHAR(32)` | yes |  |  |
| `note` | `MEDIUMBLOB` | yes | special |  |
| `checked_in_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `scale`: `score BETWEEN 1 AND 5`

<a id="vault-wellbeing_concern"></a>
## `wellbeing_concern`

Wellbeing concern reported by a learner, parent or staff member (routed to a pastoral lead; DSL alert on keywords)

| | |
|---|---|
| Zone | vault |
| Kind | transaction |
| Classification | special |
| History | lifecycle |
| Scope | owned |
| Module | `success` |
| Origin | appj |
| Retention | `RS-SEND` |
| Requirements | FR-WEL-101, FR-WEL-02, FR-WEL-103 |
| Pages | WEL-101, WEL-01 |
| Events | WEL.CONCERN_REPORTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `reported_by_kind` | `VARCHAR(32)` | no |  | values: learner, parent, staff |
| `reported_by_id` | `BINARY(16)` | yes |  |  |
| `concern_type` | `VARCHAR(32)` | no |  | exam pressure, anxiety, bullying, friendships, family, sleep, online safety, food, transport · code list `wellbeing_concern_type` |
| `body` | `MEDIUMBLOB` | no | special |  |
| `keyword_alert` | `BOOLEAN` | no |  | Safeguarding keywords detected; DSL alerted |
| `assigned_to` | `BINARY(16)` | yes |  |  |
| `respond_by` | `DATETIME(6)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-intervention"></a>
## `intervention`

Intervention with baseline, target, learners, lead, review date and outcome (closed loop)

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
| Requirements | FR-WEL-03, FR-INSP-05, FR-CMD-09, FR-WEL-103 |
| Pages | INT-01, INS-10, CMD-12 |
| Events | INT.INTERVENTION_CLOSED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `intervention_kind` | `VARCHAR(32)` | no |  | code list `intervention_kind` |
| `lead_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `learner_ids` | `JSON` | no |  | Participants (≤ a class; larger groups use cohorts) |
| `baseline` | `JSON` | no |  |  |
| `target` | `JSON` | no |  |  |
| `review_on` | `DATE` | no |  |  |
| `outcome` | `JSON` | yes |  |  |
| `effect_estimate` | `JSON` | yes |  | Outcome against target and counterfactual trend |
| `recommendation_id` → `recommendation` | `BINARY(16)` | yes |  |  |
| `cost_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: planned, active, review_due, closed_success, closed_partial, closed_no_effect, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `lead_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-learning_plan_template"></a>
## `learning_plan_template`

Reusable personal learning plan template (state or institution; catch-up, re-entry, gifted extension, exam readiness, TVET pathway)

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
| Requirements | FR-ILP-102 |
| Pages | ILP-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `content` | `JSON` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-learning_plan"></a>
## `learning_plan`

Personal learning plan for a learner (any learner, not only SEND)

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
| Requirements | FR-ILP-101, FR-ILP-104 |
| Pages | ILP-101, ILP-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `template_id` → `learning_plan_template` | `BINARY(16)` | yes |  |  |
| `template_version` | `INT UNSIGNED` | yes |  |  |
| `owner_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `next_review_on` | `DATE` | yes |  |  |
| `time_spent_minutes` | `INT` | yes |  |  |
| `cost_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, active, under_review, completed, closed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `owner_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-learning_plan_goal"></a>
## `learning_plan_goal`

Goal in a learning plan linked to curriculum objectives and target grades

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `success` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-ILP-101 |
| Pages | ILP-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `plan_id` → `learning_plan` | `BINARY(16)` | no |  |  |
| `goal_text` | `VARCHAR(1000)` | no |  |  |
| `node_ids` | `JSON` | yes |  | Curriculum objectives |
| `target_grade_id` → `target_grade` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: not_started, in_progress, achieved, partly_achieved, not_achieved, dropped |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-learning_plan_entry"></a>
## `learning_plan_entry`

Action, learner reflection, parent comment, evidence or review on a learning plan (append-only)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `success` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-ILP-101, FR-ILP-103, FR-ILP-104 |
| Pages | ILP-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `plan_id` → `learning_plan` | `BINARY(16)` | no |  |  |
| `goal_id` → `learning_plan_goal` | `BINARY(16)` | yes |  |  |
| `entry_kind` | `VARCHAR(32)` | no |  | values: action, learner_reflection, parent_comment, evidence, review, note |
| `author_kind` | `VARCHAR(32)` | no |  | values: teacher, owner, parent, learner, staff |
| `author_id` | `BINARY(16)` | no |  |  |
| `body` | `TEXT` | no |  |  |
| `evidence_ref` | `JSON` | yes |  | LMS submission or assessment result |
| `owner_staff_id` → `staff` | `BINARY(16)` | yes |  | Owner of an action |
| `due_on` | `DATE` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `owner_staff_id` → `staff` — cross-zone (ops → registry)

