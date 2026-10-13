# DW — Analytics warehouse — conformed dimensions, facts, aggregates, live KPI read model and feature store

A separate MySQL 9.7 analytics cluster per state fed by CDC (Debezium → Kafka → loaders) so analytical queries never run on the operational primary (NFR-PLAT-110, FR-RPT-06). Layers: raw (CDC landing, not modelled here) → conformed core (the dimensions and facts below, Kimball style, SCD type 2 where history matters) → aggregates (agg_*) and the live KPI read model → semantic layer (metrics.yaml). Learner and staff keys are pseudonymised with a keyed HMAC at load; re-identification happens only through the operational API under the user's permissions. The vault is never replicated: safeguarding, SEND and wellbeing appear only as governed counts. Surrogate keys are BIGINT; every table carries tenant_id (the state), loaded_at and load_batch_id.

Module (system of record): `analytics` · default zone: **dw** · default retention: `None`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`dim_date`](#dw-dim_date) | dw | dimension | public | none | Calendar date dimension |
| [`dim_scope`](#dw-dim_scope) | dw | dimension | internal | none | Governance scope dimension (SCD2) — country, state, LGA, network, institution, campus, unit, class |
| [`dim_scope_closure`](#dw-dim_scope_closure) | dw | dimension | internal | none | Scope ancestor/descendant pairs in the warehouse (permission trimming and roll-up) |
| [`dim_institution`](#dw-dim_institution) | dw | dimension | internal | none | Institution dimension (SCD2) with comparison context (P7) |
| [`dim_learner`](#dw-dim_learner) | dw | dimension | confidential | none | Pseudonymised learner dimension (SCD2) — no names, no identifiers |
| [`dim_staff`](#dw-dim_staff) | dw | dimension | confidential | none | Pseudonymised staff dimension (SCD2) |
| [`dim_subject`](#dw-dim_subject) | dw | dimension | public | none | Subject dimension |
| [`dim_curriculum_node`](#dw-dim_curriculum_node) | dw | dimension | public | none | Curriculum objective dimension (version-aware) |
| [`dim_class`](#dw-dim_class) | dw | dimension | internal | none | Class (arm/set/section) dimension per session |
| [`dim_period`](#dw-dim_period) | dw | dimension | public | none | Academic and billing period dimension (session, term, semester, billing period) |
| [`fact_enrolment_census`](#dw-fact_enrolment_census) | dw | fact | confidential | none | Enrolment at the census date per learner and period (billable, exempt) — grain learner × period |
| [`agg_enrolment_daily`](#dw-agg_enrolment_daily) | dw | aggregate | internal | none | Daily enrolment counts by institution, level and sex |
| [`fact_attendance`](#dw-fact_attendance) | dw | fact | confidential | none | Attendance mark fact (pseudonymised learner) — grain learner × register (partitioned by month) |
| [`agg_attendance_daily`](#dw-agg_attendance_daily) | dw | aggregate | internal | none | Daily attendance aggregate by institution and class (live tiles refreshed ≤ 15 min in school hours) |
| [`agg_learner_attendance_term`](#dw-agg_learner_attendance_term) | dw | aggregate | confidential | none | Learner attendance rate per term (persistent < 90% and severe < 50% absence) |
| [`fact_staff_presence`](#dw-fact_staff_presence) | dw | fact | confidential | none | Staff presence per day (sign-in or register-derived) |
| [`fact_class_subject_coverage`](#dw-fact_class_subject_coverage) | dw | fact | internal | none | Daily coverage snapshot per class-subject — teacher of record, qualified, hours required vs scheduled vs delivered |
| [`fact_coverage_gap`](#dw-fact_coverage_gap) | dw | fact | internal | none | Coverage gap fact (opened, closed, age, severity, rule) |
| [`fact_curriculum_delivery`](#dw-fact_curriculum_delivery) | dw | fact | internal | none | Lesson delivery fact per objective |
| [`fact_assessment_result`](#dw-fact_assessment_result) | dw | fact | confidential | none | Assessment result fact (score %, objective results) |
| [`fact_exam_result`](#dw-fact_exam_result) | dw | fact | confidential | none | Examination result fact (internal and external series; credits and passes) |
| [`fact_behaviour`](#dw-fact_behaviour) | dw | fact | confidential | none | Behaviour event fact |
| [`agg_wellbeing_safeguarding_count`](#dw-agg_wellbeing_safeguarding_count) | dw | aggregate | internal | none | Governed daily counts of safeguarding concerns, SEND provision and wellbeing concerns (counts only; produced inside the vault) |
| [`fact_lms_activity`](#dw-fact_lms_activity) | dw | fact | internal | none | LMS activity fact per assignment (set, submitted, on time, late, missing, marked) |
| [`fact_digital_skill`](#dw-fact_digital_skill) | dw | fact | confidential | none | Digital-skills level snapshot per person and strand |
| [`fact_message`](#dw-fact_message) | dw | fact | internal | none | Messaging fact (volumes, delivery, read, cost by channel) |
| [`fact_finance`](#dw-fact_finance) | dw | fact | internal | none | Finance fact (invoiced, collected, outstanding by charge type; budget vs actual) |
| [`fact_sdaf`](#dw-fact_sdaf) | dw | fact | internal | none | SDAF fact per institution and billing period (billed, exempted, collected, remitted, outstanding) |
| [`fact_certificate_event`](#dw-fact_certificate_event) | dw | fact | internal | none | Certificate lifecycle and verification fact |
| [`fact_digitisation`](#dw-fact_digitisation) | dw | fact | internal | none | Digitisation throughput and quality fact per batch and day |
| [`fact_data_quality`](#dw-fact_data_quality) | dw | fact | internal | none | Data Quality Index components per institution per day (DQI = 0.30C + 0.20U + 0.20V + 0.15T + 0.10K + 0.05Ve) |
| [`fact_health_index`](#dw-fact_health_index) | dw | fact | internal | none | Institution health index per day with decomposed indicator scores and weights (P8) |
| [`fact_compliance_score`](#dw-fact_compliance_score) | dw | fact | internal | none | Curriculum compliance per institution per day with components (subject coverage 20, hours 25, objectives 25, assessment 15, qualified staff 15) |
| [`fact_infrastructure`](#dw-fact_infrastructure) | dw | fact | internal | none | Infrastructure snapshot per institution per term (classrooms per learner, toilets, water, power, ICT, condition) |
| [`fact_alert`](#dw-fact_alert) | dw | fact | internal | none | Alert fact (raised, acknowledged, escalated, resolved; age) |
| [`agg_metric`](#dw-agg_metric) | dw | aggregate | internal | none | Generic metric aggregate served by the semantic layer (value, numerator, denominator, suppression) per scope and period |
| [`live_kpi`](#dw-live_kpi) | dw | aggregate | internal | none | Live KPI read model (attendance today, registers, staff presence) refreshed by stream aggregation ≤ 5 min |
| [`feature_learner_weekly`](#dw-feature_learner_weekly) | dw | feature | confidential | none | Point-in-time learner feature set for early-warning models (no protected characteristics) |

<a id="dw-dim_date"></a>
## `dim_date`

Calendar date dimension

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | public |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `academic_period`, `calendar_event` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  | YYYYMMDD |
| `calendar_date` | `DATE` | no |  |  |
| `day_of_week` | `SMALLINT` | no |  |  |
| `iso_week` | `SMALLINT` | no |  |  |
| `month_no` | `SMALLINT` | no |  |  |
| `year_no` | `SMALLINT` | no |  |  |
| `is_weekend` | `BOOLEAN` | no |  |  |
| `state_session_label` | `VARCHAR(20)` | yes |  |  |
| `state_term_label` | `VARCHAR(20)` | yes |  |  |
| `is_state_school_day` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-dim_scope"></a>
## `dim_scope`

Governance scope dimension (SCD2) — country, state, LGA, network, institution, campus, unit, class

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `scope_node` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_key` **PK** | `BIGINT` | no |  |  |
| `scope_node_id` | `BINARY(16)` | no |  |  |
| `level` | `VARCHAR(32)` | no |  | values: global, country, state, authority, lga, network, institution, campus, faculty, department, programme, class |
| `code` | `VARCHAR(40)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `path` | `VARCHAR(512)` | no |  |  |
| `state_code` | `VARCHAR(6)` | yes |  |  |
| `lga_code` | `VARCHAR(40)` | yes |  |  |
| `ownership` | `VARCHAR(32)` | yes |  | code list `ownership` |
| `row_valid_from` | `DATE` | no |  |  |
| `row_valid_to` | `DATE` | yes |  |  |
| `is_current` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

- Index: (scope_node_id, is_current)
- Index: (path)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="dw-dim_scope_closure"></a>
## `dim_scope_closure`

Scope ancestor/descendant pairs in the warehouse (permission trimming and roll-up)

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `scope_closure` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `ancestor_key` **PK** | `BIGINT` | no |  |  |
| `descendant_key` **PK** | `BIGINT` | no |  |  |
| `depth` | `SMALLINT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

- Index: (descendant_key)

<a id="dw-dim_institution"></a>
## `dim_institution`

Institution dimension (SCD2) with comparison context (P7)

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `institution`, `institution_profile` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `institution_id` | `BINARY(16)` | no |  |  |
| `scope_key` | `BIGINT` | no |  |  |
| `lga_scope_key` | `BIGINT` | no |  |  |
| `institution_code` | `VARCHAR(20)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `category` | `VARCHAR(32)` | no |  | code list `institution_category` |
| `ownership` | `VARCHAR(32)` | no |  | code list `ownership` |
| `is_public` | `BOOLEAN` | no |  |  |
| `location_class` | `VARCHAR(32)` | yes |  | values: urban, peri_urban, rural |
| `comparison_group` | `VARCHAR(60)` | yes |  |  |
| `onboarding_status` | `VARCHAR(32)` | no |  | values: not_onboarded, onboarding, live, suspended, closed |
| `row_valid_from` | `DATE` | no |  |  |
| `row_valid_to` | `DATE` | yes |  |  |
| `is_current` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

- Index: (institution_id, is_current)
- Index: (lga_scope_key)

<a id="dw-dim_learner"></a>
## `dim_learner`

Pseudonymised learner dimension (SCD2) — no names, no identifiers

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `learner` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_key` **PK** | `BIGINT` | no |  |  |
| `learner_pseudo` | `BINARY(32)` | no |  | Keyed HMAC of learner_id (key held outside the warehouse) |
| `birth_year` | `SMALLINT` | yes |  |  |
| `sex` | `VARCHAR(32)` | yes |  | code list `sex` |
| `is_historic` | `BOOLEAN` | no |  |  |
| `row_valid_from` | `DATE` | no |  |  |
| `row_valid_to` | `DATE` | yes |  |  |
| `is_current` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

- Index: (learner_pseudo, is_current)

<a id="dw-dim_staff"></a>
## `dim_staff`

Pseudonymised staff dimension (SCD2)

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `staff`, `staff_post`, `staff_qualification` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_key` **PK** | `BIGINT` | no |  |  |
| `staff_pseudo` | `BINARY(32)` | no |  |  |
| `sex` | `VARCHAR(32)` | yes |  | code list `sex` |
| `staff_category` | `VARCHAR(32)` | yes |  | code list `staff_category` |
| `academic_rank` | `VARCHAR(32)` | yes |  | code list `academic_rank` |
| `is_qualified_teacher` | `BOOLEAN` | yes |  |  |
| `is_trcn_registered` | `BOOLEAN` | yes |  |  |
| `row_valid_from` | `DATE` | no |  |  |
| `row_valid_to` | `DATE` | yes |  |  |
| `is_current` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-dim_subject"></a>
## `dim_subject`

Subject dimension

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | public |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `subject` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `subject_key` **PK** | `BIGINT` | no |  |  |
| `subject_id` | `BINARY(16)` | no |  |  |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `subject_group` | `VARCHAR(32)` | yes |  | code list `subject_group` |
| `is_mandatory_core` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-dim_curriculum_node"></a>
## `dim_curriculum_node`

Curriculum objective dimension (version-aware)

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | public |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `curriculum_node`, `curriculum_version`, `curriculum` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `node_key` **PK** | `BIGINT` | no |  |  |
| `node_id` | `BINARY(16)` | no |  |  |
| `curriculum_code` | `VARCHAR(48)` | no |  |  |
| `version_label` | `VARCHAR(32)` | no |  |  |
| `node_code` | `VARCHAR(48)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: subject, strand, theme, topic, objective, competency |
| `requirement` | `VARCHAR(32)` | no |  | values: mandatory, optional, recommended, restricted |
| `subject_key` | `BIGINT` | yes |  |  |
| `min_hours` | `DECIMAL(6,1)` | yes |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-dim_class"></a>
## `dim_class`

Class (arm/set/section) dimension per session

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `class_group`, `course_section` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_key` **PK** | `BIGINT` | no |  |  |
| `class_group_id` | `BINARY(16)` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `stream` | `VARCHAR(32)` | yes |  | code list `stream` |
| `session_label` | `VARCHAR(20)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-dim_period"></a>
## `dim_period`

Academic and billing period dimension (session, term, semester, billing period)

| | |
|---|---|
| Zone | dw |
| Kind | dimension |
| Classification | public |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `academic_period`, `billing_period` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `period_key` **PK** | `BIGINT` | no |  |  |
| `period_id` | `BINARY(16)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: session, term, semester, half_term, billing_period |
| `label` | `VARCHAR(40)` | no |  |  |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_enrolment_census"></a>
## `fact_enrolment_census`

Enrolment at the census date per learner and period (billable, exempt) — grain learner × period

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `census_learner`, `census_snapshot`, `sdaf_exemption`, `enrolment` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `period_key` **PK** | `BIGINT` | no |  |  |
| `learner_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `is_billable` | `BOOLEAN` | no |  |  |
| `is_exempt` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-agg_enrolment_daily"></a>
## `agg_enrolment_daily`

Daily enrolment counts by institution, level and sex

| | |
|---|---|
| Zone | dw |
| Kind | aggregate |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `enrolment`, `learner` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `education_level` **PK** | `VARCHAR(32)` | no |  | code list `education_level` |
| `sex` **PK** | `VARCHAR(32)` | no |  | code list `sex` |
| `enrolled` | `INT UNSIGNED` | no |  |  |
| `new_entrants` | `INT UNSIGNED` | no |  |  |
| `leavers` | `INT UNSIGNED` | no |  |  |
| `dropouts` | `INT UNSIGNED` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_attendance"></a>
## `fact_attendance`

Attendance mark fact (pseudonymised learner) — grain learner × register (partitioned by month)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `attendance_mark`, `attendance_register` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `register_id` **PK** | `BINARY(16)` | no |  |  |
| `learner_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `class_key` | `BIGINT` | no |  |  |
| `register_kind` | `VARCHAR(32)` | no |  | values: am, pm, daily, lesson, activity, trip |
| `code` | `VARCHAR(32)` | no |  | code list `attendance_code` |
| `is_present` | `BOOLEAN` | no |  |  |
| `is_late` | `BOOLEAN` | no |  |  |
| `is_authorised_absence` | `BOOLEAN` | no |  |  |
| `minutes_late` | `SMALLINT` | yes |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-agg_attendance_daily"></a>
## `agg_attendance_daily`

Daily attendance aggregate by institution and class (live tiles refreshed ≤ 15 min in school hours)

| | |
|---|---|
| Zone | dw |
| Kind | aggregate |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `attendance_mark`, `attendance_register` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `class_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `possible_sessions` | `INT UNSIGNED` | no |  |  |
| `present_sessions` | `INT UNSIGNED` | no |  |  |
| `late_sessions` | `INT UNSIGNED` | no |  |  |
| `authorised_absences` | `INT UNSIGNED` | no |  |  |
| `unauthorised_absences` | `INT UNSIGNED` | no |  |  |
| `registers_due` | `SMALLINT` | no |  |  |
| `registers_on_time` | `SMALLINT` | no |  |  |
| `registers_missing` | `SMALLINT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-agg_learner_attendance_term"></a>
## `agg_learner_attendance_term`

Learner attendance rate per term (persistent < 90% and severe < 50% absence)

| | |
|---|---|
| Zone | dw |
| Kind | aggregate |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `attendance_mark` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `period_key` **PK** | `BIGINT` | no |  |  |
| `learner_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `possible_sessions` | `INT UNSIGNED` | no |  |  |
| `present_sessions` | `INT UNSIGNED` | no |  |  |
| `attendance_rate` | `DECIMAL(6,3)` | no |  |  |
| `is_persistent_absence` | `BOOLEAN` | no |  |  |
| `is_severe_absence` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_staff_presence"></a>
## `fact_staff_presence`

Staff presence per day (sign-in or register-derived)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `staff_attendance`, `staff_absence` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `staff_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `is_expected` | `BOOLEAN` | no |  |  |
| `is_present` | `BOOLEAN` | no |  |  |
| `absence_type` | `VARCHAR(32)` | yes |  | code list `absence_type` |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_class_subject_coverage"></a>
## `fact_class_subject_coverage`

Daily coverage snapshot per class-subject — teacher of record, qualified, hours required vs scheduled vs delivered

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `class_subject_plan`, `teaching_assignment`, `staff_qualification`, `timetable_lesson`, `delivery_log`, `coverage_gap` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `class_key` **PK** | `BIGINT` | no |  |  |
| `subject_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `is_mandatory` | `BOOLEAN` | no |  |  |
| `has_teacher_of_record` | `BOOLEAN` | no |  |  |
| `is_teacher_qualified` | `BOOLEAN` | no |  |  |
| `required_hours_to_date` | `DECIMAL(7,1)` | no |  |  |
| `scheduled_hours_to_date` | `DECIMAL(7,1)` | no |  |  |
| `delivered_hours_to_date` | `DECIMAL(7,1)` | no |  |  |
| `objectives_due` | `SMALLINT` | no |  |  |
| `objectives_delivered` | `SMALLINT` | no |  |  |
| `objectives_assessed_due` | `SMALLINT` | no |  |  |
| `objectives_assessed` | `SMALLINT` | no |  |  |
| `open_gaps` | `SMALLINT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_coverage_gap"></a>
## `fact_coverage_gap`

Coverage gap fact (opened, closed, age, severity, rule)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `coverage_gap`, `gap_event` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `gap_id` **PK** | `BINARY(16)` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `class_key` | `BIGINT` | yes |  |  |
| `subject_key` | `BIGINT` | yes |  |  |
| `rule` | `VARCHAR(32)` | no |  | values: g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12 |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `opened_date_key` | `INT` | no |  |  |
| `closed_date_key` | `INT` | yes |  |  |
| `escalation_level` | `SMALLINT` | no |  |  |
| `learners_affected` | `SMALLINT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_curriculum_delivery"></a>
## `fact_curriculum_delivery`

Lesson delivery fact per objective

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `delivery_log` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `delivery_id` **PK** | `BINARY(16)` | no |  |  |
| `node_key` **PK** | `BIGINT` | no |  |  |
| `date_key` | `INT` | no |  |  |
| `class_key` | `BIGINT` | no |  |  |
| `staff_key` | `BIGINT` | no |  |  |
| `delivered_minutes` | `INT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_assessment_result"></a>
## `fact_assessment_result`

Assessment result fact (score %, objective results)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `assessment_result`, `assessment`, `submission_mark` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `assessment_id` **PK** | `BINARY(16)` | no |  |  |
| `learner_key` **PK** | `BIGINT` | no |  |  |
| `date_key` | `INT` | no |  |  |
| `class_key` | `BIGINT` | no |  |  |
| `subject_key` | `BIGINT` | no |  |  |
| `assessment_kind` | `VARCHAR(32)` | no |  | values: formative, summative, coursework, practical, competency, ca_test, examination, homework, quiz |
| `score_pct` | `DECIMAL(6,3)` | yes |  |  |
| `is_missing_work` | `BOOLEAN` | no |  |  |
| `target_gap_points` | `DECIMAL(6,2)` | yes |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_exam_result"></a>
## `fact_exam_result`

Examination result fact (internal and external series; credits and passes)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `exam_result`, `exam_entry`, `exam_series`, `external_exam_record` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `series_id` **PK** | `BINARY(16)` | no |  |  |
| `learner_key` **PK** | `BIGINT` | no |  |  |
| `subject_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `exam_body` | `VARCHAR(32)` | no |  | code list `exam_body` |
| `exam_year` | `SMALLINT` | no |  |  |
| `grade_label` | `VARCHAR(16)` | no |  |  |
| `is_pass` | `BOOLEAN` | no |  |  |
| `is_credit` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_behaviour"></a>
## `fact_behaviour`

Behaviour event fact

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `behaviour_event`, `behaviour_type`, `detention` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `behaviour_event_id` **PK** | `BINARY(16)` | no |  |  |
| `date_key` | `INT` | no |  |  |
| `learner_key` | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `class_key` | `BIGINT` | yes |  |  |
| `polarity` | `VARCHAR(32)` | no |  | values: positive, negative |
| `category` | `VARCHAR(32)` | no |  | code list `behaviour_category` |
| `points` | `SMALLINT` | no |  |  |
| `outcome` | `VARCHAR(32)` | yes |  | values: none, warning, detention, on_report, parent_contact, intervention, internal_exclusion, suspension, exclusion |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-agg_wellbeing_safeguarding_count"></a>
## `agg_wellbeing_safeguarding_count`

Governed daily counts of safeguarding concerns, SEND provision and wellbeing concerns (counts only; produced inside the vault)  

Computed by a job running inside the vault zone that emits counts only; no row-level vault data ever leaves the vault.

| | |
|---|---|
| Zone | dw |
| Kind | aggregate |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `safeguarding_concern`, `send_profile`, `wellbeing_concern`, `community_report` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `measure` **PK** | `VARCHAR(40)` | no |  | safeguarding_concerns, send_register, send_provision_covered, wellbeing_concerns |
| `category` **PK** | `VARCHAR(40)` | no |  | Concern category or '*' |
| `count_value` | `INT UNSIGNED` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_lms_activity"></a>
## `fact_lms_activity`

LMS activity fact per assignment (set, submitted, on time, late, missing, marked)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `assignment`, `submission`, `submission_mark`, `course_space` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `assignment_id` **PK** | `BINARY(16)` | no |  |  |
| `date_key` | `INT` | no |  | Due date |
| `institution_key` | `BIGINT` | no |  |  |
| `class_key` | `BIGINT` | yes |  |  |
| `staff_key` | `BIGINT` | no |  |  |
| `assignment_kind` | `VARCHAR(32)` | no |  | values: homework, coursework, ca_test, quiz_cbt, practical, portfolio, peer_review, digital_skills_task |
| `learners_expected` | `SMALLINT` | no |  |  |
| `submitted` | `SMALLINT` | no |  |  |
| `on_time` | `SMALLINT` | no |  |  |
| `late` | `SMALLINT` | no |  |  |
| `missing` | `SMALLINT` | no |  |  |
| `marked` | `SMALLINT` | no |  |  |
| `returned_online` | `SMALLINT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_digital_skill"></a>
## `fact_digital_skill`

Digital-skills level snapshot per person and strand

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `digital_skill_level` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `person_pseudo` **PK** | `BINARY(32)` | no |  |  |
| `person_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `institution_key` | `BIGINT` | no |  |  |
| `strand` **PK** | `VARCHAR(32)` | no |  | code list `digital_strand` |
| `level` | `SMALLINT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_message"></a>
## `fact_message`

Messaging fact (volumes, delivery, read, cost by channel)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `message`, `broadcast_campaign` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `message_id` **PK** | `BINARY(16)` | no |  |  |
| `date_key` | `INT` | no |  |  |
| `institution_key` | `BIGINT` | yes |  |  |
| `channel` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `direction` | `VARCHAR(32)` | no |  | values: outbound, inbound |
| `is_delivered` | `BOOLEAN` | no |  |  |
| `is_read` | `BOOLEAN` | no |  |  |
| `response_minutes` | `INT` | yes |  |  |
| `cost_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_finance"></a>
## `fact_finance`

Finance fact (invoiced, collected, outstanding by charge type; budget vs actual)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `invoice`, `invoice_line`, `payment`, `ledger_entry`, `budget` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `charge_type_code` **PK** | `VARCHAR(32)` | no |  |  |
| `measure` **PK** | `VARCHAR(24)` | no |  | invoiced, collected, outstanding, budget, actual |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_sdaf"></a>
## `fact_sdaf`

SDAF fact per institution and billing period (billed, exempted, collected, remitted, outstanding)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `sdaf_demand`, `sdaf_collection`, `remittance_allocation`, `census_snapshot`, `reconciliation_line` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `period_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `billable_learners` | `INT UNSIGNED` | no |  |  |
| `exempt_learners` | `INT UNSIGNED` | no |  |  |
| `billed_minor` | `BIGINT` | no |  | (minor units) |
| `exempted_minor` | `BIGINT` | no |  | (minor units) |
| `collected_minor` | `BIGINT` | no |  | (minor units) |
| `remitted_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_certificate_event"></a>
## `fact_certificate_event`

Certificate lifecycle and verification fact

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `certificate_event`, `certificate`, `verification`, `reissue_case` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `event_id` **PK** | `BINARY(16)` | no |  |  |
| `date_key` | `INT` | no |  |  |
| `institution_key` | `BIGINT` | yes |  |  |
| `event_kind` | `VARCHAR(24)` | no |  | issued, revoked, reissued, corrected, verified_ok, verified_failed, reissue_requested |
| `credential_kind` | `VARCHAR(32)` | yes |  | values: certificate, transcript, testimonial, approval_certificate, badge, micro_credential, certified_copy |
| `channel` | `VARCHAR(24)` | yes |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_digitisation"></a>
## `fact_digitisation`

Digitisation throughput and quality fact per batch and day

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `digitisation_batch`, `scanned_page`, `extracted_field`, `qa_sample`, `custody_event` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `batch_id` **PK** | `BINARY(16)` | no |  |  |
| `hub` | `VARCHAR(80)` | yes |  |  |
| `lga_scope_key` | `BIGINT` | yes |  |  |
| `pages_captured` | `INT UNSIGNED` | no |  |  |
| `pages_indexed` | `INT UNSIGNED` | no |  |  |
| `key_field_accuracy` | `DECIMAL(6,3)` | yes |  |  |
| `hours_scan_to_searchable` | `DECIMAL(7,1)` | yes |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_data_quality"></a>
## `fact_data_quality`

Data Quality Index components per institution per day (DQI = 0.30C + 0.20U + 0.20V + 0.15T + 0.10K + 0.05Ve)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `data_quality_issue`, `data_quality_rule`, `dataset_freshness`, `match_review` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `completeness` | `DECIMAL(7,6)` | no |  |  |
| `uniqueness` | `DECIMAL(7,6)` | no |  |  |
| `validity` | `DECIMAL(7,6)` | no |  |  |
| `timeliness` | `DECIMAL(7,6)` | no |  |  |
| `consistency` | `DECIMAL(7,6)` | no |  |  |
| `verification` | `DECIMAL(7,6)` | no |  |  |
| `dqi` | `DECIMAL(7,3)` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_health_index"></a>
## `fact_health_index`

Institution health index per day with decomposed indicator scores and weights (P8)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `health_index_policy`, `institution` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `indicator` **PK** | `VARCHAR(40)` | no |  | attendance, progress, exam_outcomes, retention, dropout … or 'index' |
| `raw_value` | `DECIMAL(12,4)` | yes |  |  |
| `normalised_score` | `DECIMAL(7,3)` | yes |  |  |
| `weight` | `DECIMAL(6,4)` | yes |  |  |
| `policy_version` | `INT UNSIGNED` | no |  |  |
| `is_partial` | `BOOLEAN` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_compliance_score"></a>
## `fact_compliance_score`

Curriculum compliance per institution per day with components (subject coverage 20, hours 25, objectives 25, assessment 15, qualified staff 15)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `class_subject_plan`, `delivery_log`, `assessment`, `teaching_assignment`, `curriculum_adoption` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `date_key` **PK** | `INT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `component` **PK** | `VARCHAR(32)` | no |  | subject_coverage, teaching_hours, objectives, assessment, qualified_staff, total |
| `score` | `DECIMAL(7,3)` | no |  |  |
| `weight` | `DECIMAL(6,4)` | no |  |  |
| `band` | `VARCHAR(24)` | yes |  | compliant, partial, non_compliant, not_assessed |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_infrastructure"></a>
## `fact_infrastructure`

Infrastructure snapshot per institution per term (classrooms per learner, toilets, water, power, ICT, condition)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `room`, `building`, `asset` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `period_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` **PK** | `BIGINT` | no |  |  |
| `classrooms` | `SMALLINT` | no |  |  |
| `learners_per_classroom` | `DECIMAL(6,2)` | yes |  |  |
| `toilets` | `SMALLINT` | yes |  |  |
| `has_water` | `BOOLEAN` | yes |  |  |
| `has_power` | `BOOLEAN` | yes |  |  |
| `ict_devices` | `INT UNSIGNED` | yes |  |  |
| `condition_score` | `DECIMAL(7,3)` | yes |  |  |
| `textbook_ratio` | `JSON` | yes |  | Subject × level → textbooks per learner |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-fact_alert"></a>
## `fact_alert`

Alert fact (raised, acknowledged, escalated, resolved; age)

| | |
|---|---|
| Zone | dw |
| Kind | fact |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `alert`, `alert_event` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `alert_id` **PK** | `BINARY(16)` | no |  |  |
| `scope_key` | `BIGINT` | no |  |  |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `raised_date_key` | `INT` | no |  |  |
| `resolved_date_key` | `INT` | yes |  |  |
| `escalations` | `SMALLINT` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-agg_metric"></a>
## `agg_metric`

Generic metric aggregate served by the semantic layer (value, numerator, denominator, suppression) per scope and period

| | |
|---|---|
| Zone | dw |
| Kind | aggregate |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `scope_node` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `metric_code` **PK** | `VARCHAR(40)` | no |  |  |
| `scope_key` **PK** | `BIGINT` | no |  |  |
| `grain` **PK** | `VARCHAR(16)` | no |  | day, week, term, session, year |
| `period_label` **PK** | `VARCHAR(20)` | no |  |  |
| `dims_hash` **PK** | `BINARY(32)` | no |  | Hash of the dimension filter (sex, level, ownership …) |
| `dims` | `JSON` | no |  |  |
| `value` | `DECIMAL(18,6)` | yes |  |  |
| `numerator` | `DECIMAL(18,6)` | yes |  |  |
| `denominator` | `DECIMAL(18,6)` | yes |  |  |
| `is_suppressed` | `BOOLEAN` | no |  | Cells < 10 outside the institution scope |
| `label_kind` | `VARCHAR(32)` | no |  | values: verified, calculated, estimated |
| `computed_at` | `DATETIME(6)` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-live_kpi"></a>
## `live_kpi`

Live KPI read model (attendance today, registers, staff presence) refreshed by stream aggregation ≤ 5 min

| | |
|---|---|
| Zone | dw |
| Kind | aggregate |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `attendance_register`, `attendance_mark`, `staff_attendance` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `metric_code` **PK** | `VARCHAR(40)` | no |  |  |
| `scope_key` **PK** | `BIGINT` | no |  |  |
| `as_of_date` **PK** | `DATE` | no |  |  |
| `value` | `DECIMAL(18,6)` | yes |  |  |
| `numerator` | `DECIMAL(18,6)` | yes |  |  |
| `denominator` | `DECIMAL(18,6)` | yes |  |  |
| `is_suppressed` | `BOOLEAN` | no |  |  |
| `refreshed_at` | `DATETIME(6)` | no |  |  |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

<a id="dw-feature_learner_weekly"></a>
## `feature_learner_weekly`

Point-in-time learner feature set for early-warning models (no protected characteristics)

| | |
|---|---|
| Zone | dw |
| Kind | feature |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `analytics` |
| Origin | ceda |
| Retention | — |
| Sources | `attendance_mark`, `assessment_result`, `behaviour_event`, `submission`, `enrolment` |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `week_start_key` **PK** | `INT` | no |  |  |
| `learner_key` **PK** | `BIGINT` | no |  |  |
| `institution_key` | `BIGINT` | no |  |  |
| `attendance_rate_4w` | `DECIMAL(7,6)` | yes |  |  |
| `attendance_trend` | `DECIMAL(8,5)` | yes |  |  |
| `attainment_trend` | `DECIMAL(8,5)` | yes |  |  |
| `negative_behaviour_4w` | `SMALLINT` | yes |  |  |
| `missing_work_4w` | `SMALLINT` | yes |  |  |
| `transitions` | `SMALLINT` | yes |  | Moves between institutions |
| `label_dropout_next_term` | `BOOLEAN` | yes |  | Training label, filled retrospectively |
| `loaded_at` | `DATETIME(6)` | no |  | Warehouse load time (UTC) |
| `load_batch_id` | `BIGINT` | no |  | ETL batch that wrote the row |

