# ACA — Academic structure — calendars, subjects, programmes, qualifications, classes, departments and courses

Schools are level → class (arm) → subject → teacher; post-secondary institutions are faculty → department → subject area → course → section → lecturer (MFS §6). Masters shared across the state — calendars, Subject 360, programmes, qualifications, departments, subject areas and the course catalogue with benchmark mappings — sit in the registry. The session-specific operational structure — Class 360, class subject plans, sets, teaching assignments, course sections, allocations and course registration — sits in the ops zone. Every assignment and allocation is effective-dated so past results always show who taught them (FR-ACA-118).

Module (system of record): `academic` · default zone: **registry** · default retention: `RS-LRN-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`academic_period`](#registry-academic_period) | registry | master | internal | lifecycle | Session, term, semester or half-term of a calendar (state calendar inherited by institutions) |
| [`calendar_event`](#registry-calendar_event) | registry | transaction | internal | lifecycle | Closure, holiday, exam window or event on a calendar (school closures recalculate compliance with an automatic exception) |
| [`subject`](#registry-subject) | registry | master | public | lifecycle | Subject 360 master (country master list plus institution courses) |
| [`stream_combination_rule`](#registry-stream_combination_rule) | registry | config | public | versioned | Stream subject-combination rule (WAEC, NECO, NABTEB, JAMB) for SSS classes and option choices |
| [`qualification`](#registry-qualification) | registry | master | public | lifecycle | Qualification 360 (FSLC, BECE, SSC, NTC, NCE, ND, HND, B.Sc. …) with award rules |
| [`programme`](#registry-programme) | registry | master | public | lifecycle | Programme 360 (qualification-bearing programmes, national or institutional) |
| [`programme_component`](#registry-programme_component) | registry | link | public | effective | Course or module within a programme (credits, core/elective, prerequisites — cycle-checked) |
| [`department`](#registry-department) | registry | master | internal | lifecycle | Department 360 — academic department of a post-secondary institution |
| [`subject_area`](#registry-subject_area) | registry | master | public | lifecycle | Discipline area of a department mapped to the national benchmark (NUC CCMAS, NBTE, NCCE) |
| [`course`](#registry-course) | registry | master | public | lifecycle | Course 360 catalogue entry owned by a department (code, units, level, semester, prerequisites, benchmark) |
| [`class_group`](#ops-class_group) | ops | master | internal | lifecycle | Class 360 — class (arm), set, cohort or course section for a period |
| [`class_membership`](#ops-class_membership) | ops | link | confidential | effective | Learner membership of a class, set or grouping (exactly one class arm per session; sets in addition) |
| [`class_subject_plan`](#ops-class_subject_plan) | ops | config | internal | effective | Subject offered to a class — periods per week, room type, curriculum version, language of instruction |
| [`teaching_assignment`](#ops-teaching_assignment) | ops | link | internal | effective | Teacher of record or co-teacher for a class-subject or lecturer for a course section (effective-dated) |
| [`course_section`](#ops-course_section) | ops | master | internal | lifecycle | Course offering section per semester (lecturer of record, co-lecturers, TAs, LMS space, assessment components) |
| [`course_registration`](#ops-course_registration) | ops | transaction | confidential | lifecycle | Student semester course registration (unit limits, prerequisites, carry-overs, clashes, adviser approval) |

<a id="registry-academic_period"></a>
## `academic_period`

Session, term, semester or half-term of a calendar (state calendar inherited by institutions)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-02, FR-ACA-06, FR-SUB-103 |
| Pages | ACA-01, SUB-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `parent_id` → `academic_period` | `BINARY(16)` | yes |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: session, term, semester, half_term, billing_period |
| `name` | `VARCHAR(300)` | no |  |  |
| `institution_types` | `JSON` | yes |  | Calendars differ by institution type · code list `institution_category` |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `teaching_days` | `SMALLINT` | yes |  | After closures |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `dates`: `ends_on >= starts_on`

<a id="registry-calendar_event"></a>
## `calendar_event`

Closure, holiday, exam window or event on a calendar (school closures recalculate compliance with an automatic exception)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-02 |
| Pages | ACA-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: holiday, closure, exam_window, event, inset_day, mid_term_break |
| `title` | `VARCHAR(300)` | no |  |  |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `reduces_teaching_days` | `BOOLEAN` | no |  |  |
| `is_remote_mode` | `BOOLEAN` | no |  | Closure switches classes to LMS remote mode |
| `exception_id` → `policy_exception` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-subject"></a>
## `subject`

Subject 360 master (country master list plus institution courses)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-03, FR-CUR-115 |
| Pages | ACA-03, CUR-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `levels` | `JSON` | yes |  | code list `education_level` |
| `subject_group` | `VARCHAR(32)` | yes |  | Core, science, arts, commercial, technical, vocational, language · code list `subject_group` |
| `is_mandatory_core` | `BOOLEAN` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

<a id="registry-stream_combination_rule"></a>
## `stream_combination_rule`

Stream subject-combination rule (WAEC, NECO, NABTEB, JAMB) for SSS classes and option choices

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `academic` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-103, FR-P16-01, FR-EXM-01 |
| Pages | ACA-101, P16-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `stream` | `VARCHAR(32)` | no |  | code list `stream` |
| `exam_body` | `VARCHAR(32)` | yes |  | code list `exam_body` |
| `rule` | `JSON` | no |  | Required, either-of and maximum subject sets |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-qualification"></a>
## `qualification`

Qualification 360 (FSLC, BECE, SSC, NTC, NCE, ND, HND, B.Sc. …) with award rules

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-CER-01, FR-ACA-04 |
| Pages | ACA-04, CER-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `awarding_body` | `VARCHAR(32)` | no |  | code list `regulator` |
| `framework_level` | `VARCHAR(16)` | yes |  |  |
| `award_rules` | `JSON` | no |  | Evaluated by the eligibility engine |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

<a id="registry-programme"></a>
## `programme`

Programme 360 (qualification-bearing programmes, national or institutional)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-04, FR-ACA-108, FR-HED-101, FR-BIL-08, FR-MED-103 |
| Pages | ACA-04, ACA-102, EXM-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | yes |  | NULL for national programmes |
| `department_id` → `department` | `BINARY(16)` | yes |  |  |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `qualification_id` → `qualification` | `BINARY(16)` | yes |  |  |
| `delivery_mode` | `VARCHAR(32)` | no |  | values: on_campus, distance, online, blended, continuing |
| `programme_family` | `VARCHAR(32)` | yes |  | Health-profession family (medicine, nursing, pharmacy …) · code list `programme_family` |
| `professional_body_id` → `professional_body` | `BINARY(16)` | yes |  |  |
| `duration_terms` | `SMALLINT` | yes |  |  |
| `rules` | `JSON` | no |  | Credits, CGPA, progression, classification scheme |
| `accreditation_status` | `VARCHAR(32)` | yes |  | values: full, interim, denied, expired, not_required |
| `accreditation_expires_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

<a id="registry-programme_component"></a>
## `programme_component`

Course or module within a programme (credits, core/elective, prerequisites — cycle-checked)

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | public |
| History | effective |
| Scope | derived: the programme |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-04 |
| Pages | ACA-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `programme_id` → `programme` | `BINARY(16)` | no |  |  |
| `course_id` → `course` | `BINARY(16)` | no |  |  |
| `programme_level` | `VARCHAR(16)` | yes |  | 100L, ND1, Year 2 |
| `semester_no` | `SMALLINT` | yes |  |  |
| `credits` | `DECIMAL(4,1)` | no |  |  |
| `is_core` | `BOOLEAN` | no |  |  |
| `prerequisite_course_ids` | `JSON` | yes |  | Cycle-checked on save |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, programme_id, course_id, valid_from)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-department"></a>
## `department`

Department 360 — academic department of a post-secondary institution

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-108, FR-ACA-114 |
| Pages | ACA-102, ACA-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `org_unit_id` → `org_unit` | `BINARY(16)` | no |  | The department's node in the organisation structure |
| `faculty_org_unit_id` → `org_unit` | `BINARY(16)` | yes |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `hod_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `acting_hod_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `load_policy` | `JSON` | yes |  | Maximum contact hours per rank |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-subject_area"></a>
## `subject_area`

Discipline area of a department mapped to the national benchmark (NUC CCMAS, NBTE, NCCE)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | derived: the department |
| Module | `academic` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-108, FR-ACA-109 |
| Pages | ACA-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `department_id` → `department` | `BINARY(16)` | no |  |  |
| `code` | `VARCHAR(40)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `benchmark` | `VARCHAR(32)` | no |  | code list `benchmark_framework` |
| `benchmark_area_code` | `VARCHAR(40)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, department_id, code)

<a id="registry-course"></a>
## `course`

Course 360 catalogue entry owned by a department (code, units, level, semester, prerequisites, benchmark)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-108, FR-ACA-109, FR-ACA-03 |
| Pages | ACA-102, ACA-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `department_id` → `department` | `BINARY(16)` | no |  |  |
| `subject_area_id` → `subject_area` | `BINARY(16)` | yes |  |  |
| `subject_id` → `subject` | `BINARY(16)` | yes |  |  |
| `code` | `VARCHAR(20)` | no |  | e.g. COM 214, GST 111 |
| `title` | `VARCHAR(300)` | no |  |  |
| `units` | `DECIMAL(4,1)` | no |  |  |
| `course_level` | `VARCHAR(16)` | no |  |  |
| `semester_no` | `SMALLINT` | yes |  |  |
| `is_service_course` | `BOOLEAN` | no |  | Taught to other departments (GST) |
| `is_compulsory` | `BOOLEAN` | no |  |  |
| `benchmark_ref` | `VARCHAR(60)` | yes |  |  |
| `outline_document_id` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, department_id, code)

<a id="ops-class_group"></a>
## `class_group`

Class 360 — class (arm), set, cohort or course section for a period  

scope_node_id is the class node (level 9). A class cannot be activated for a session without an adopted curriculum for every mandatory subject of its level (FR-CUR-103).

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-101, FR-ACA-104, FR-ACA-107, FR-ACA-117, FR-CUR-102, FR-CUR-103, FR-ACA-02 |
| Pages | ACA-02, ACA-05, ACA-101 |
| Events | ACA.CLASS_ACTIVATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `campus_id` → `campus` | `BINARY(16)` | yes |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  | Session |
| `kind` | `VARCHAR(32)` | no |  | values: arm, set, cohort, course_section, group |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `name` | `VARCHAR(300)` | no |  | Primary 4B, JSS 1 Gold, SS 2 Science A |
| `stream` | `VARCHAR(32)` | yes |  | code list `stream` |
| `programme_id` → `programme` | `BINARY(16)` | yes |  |  |
| `parent_class_id` → `class_group` | `BINARY(16)` | yes |  | Sets and cross-class groupings link to parent classes |
| `form_teacher_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `capacity` | `SMALLINT` | no |  | Room capacity and state policy (default 40 primary, 45 secondary) |
| `language_of_instruction` | `VARCHAR(35)` | yes |  |  |
| `session_shift` | `VARCHAR(32)` | yes |  | Double-shift schools · values: morning, afternoon, evening, single |
| `rolled_from_id` → `class_group` | `BINARY(16)` | yes |  | Academic Year Rollover Wizard |
| `status` | `VARCHAR(32)` | no |  | values: draft, active, closed, archived |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, period_id, name)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `campus_id` → `campus` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)
- Soft reference `programme_id` → `programme` — cross-zone (ops → registry)
- Soft reference `form_teacher_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-class_membership"></a>
## `class_membership`

Learner membership of a class, set or grouping (exactly one class arm per session; sets in addition)

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | confidential |
| History | effective |
| Scope | derived: the class |
| Module | `academic` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-101, FR-ACA-104 |
| Pages | ACA-05, ATT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `is_arm` | `BOOLEAN` | no |  | True for the learner's single class arm |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, class_group_id, learner_id, valid_from)
- Index: (tenant_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-class_subject_plan"></a>
## `class_subject_plan`

Subject offered to a class — periods per week, room type, curriculum version, language of instruction

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | effective |
| Scope | derived: the class |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-102, FR-ACA-103, FR-ACA-105, FR-ACA-106, FR-CUR-102, FR-ACA-115 |
| Pages | ACA-101, CUR-102 |
| Events | ACA.SUBJECT_PLAN_PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | no |  |  |
| `is_mandatory` | `BOOLEAN` | no |  | Pre-filled mandatory subjects cannot be removed |
| `periods_per_week` | `SMALLINT` | no |  |  |
| `required_hours` | `DECIMAL(6,1)` | yes |  | From the adopted curriculum |
| `room_type` | `VARCHAR(32)` | yes |  | code list `room_type` |
| `curriculum_version_id` → `curriculum_version` | `BINARY(16)` | yes |  | Resolved and stored for history |
| `language_of_instruction` | `VARCHAR(35)` | yes |  |  |
| `copied_from_id` → `class_subject_plan` | `BINARY(16)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, class_group_id, subject_id, valid_from)

- Soft reference `subject_id` → `subject` — cross-zone (ops → registry)
- Soft reference `curriculum_version_id` → `curriculum_version` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-teaching_assignment"></a>
## `teaching_assignment`

Teacher of record or co-teacher for a class-subject or lecturer for a course section (effective-dated)  

Exactly one teacher of record per class-subject or section at a time (G2); unauthorised assignments need a time-boxed exception (G3).

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | internal |
| History | effective |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-CUR-104, FR-CUR-105, FR-CUR-109, FR-ACA-105, FR-ACA-111, FR-ACA-116, FR-ACA-118, FR-STF-04 |
| Pages | CUR-102, ACA-101, ACA-103 |
| Events | CUR.ASSIGNMENT_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `class_subject_plan_id` → `class_subject_plan` | `BINARY(16)` | yes |  | School |
| `course_section_id` → `course_section` | `BINARY(16)` | yes |  | Tertiary |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `staff_post_id` → `staff_post` | `BINARY(16)` | no |  |  |
| `role` | `VARCHAR(32)` | no |  | values: teacher_of_record, co_teacher, teaching_assistant, specialist |
| `authorisation_id` → `staff_qualification` | `BINARY(16)` | yes |  | Authorisation that satisfied G3 |
| `exception_id` → `policy_exception` | `BINARY(16)` | yes |  | Time-boxed exception when unauthorised |
| `justification` | `VARCHAR(500)` | yes |  | Out-of-specialism or overload reason (HOD) |
| `weekly_periods` | `DECIMAL(5,2)` | yes |  |  |
| `of_record_key` | `BINARY(16)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, of_record_key)
- Index: (tenant_id, staff_id)
- Index: (tenant_id, class_subject_plan_id)
- Index: (tenant_id, course_section_id)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `staff_post_id` → `staff_post` — cross-zone (ops → registry)
- Soft reference `authorisation_id` → `staff_qualification` — cross-zone (ops → registry)
- Soft reference `exception_id` → `policy_exception` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`
- Check `target`: `(class_subject_plan_id IS NULL) <> (course_section_id IS NULL)`

<a id="ops-course_section"></a>
## `course_section`

Course offering section per semester (lecturer of record, co-lecturers, TAs, LMS space, assessment components)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `academic` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ACA-110, FR-ACA-112, FR-ACA-111 |
| Pages | ACA-103, HED-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `course_id` → `course` | `BINARY(16)` | no |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  | Semester |
| `section_code` | `VARCHAR(8)` | no |  |  |
| `capacity` | `SMALLINT` | yes |  |  |
| `consuming_department_ids` | `JSON` | yes |  | Service courses visible to consuming departments |
| `assessment_scheme` | `JSON` | yes |  | CA and exam components |
| `external_examiner` | `JSON` | yes |  | External examiners and moderators (FR-ACA-114) |
| `allocation_status` | `VARCHAR(32)` | no |  | HOD approval publishes to timetables and the LMS · values: draft, proposed, approved, published, applied, allocated, waitlisted, cancelled |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, course_id, period_id, section_code)

- Soft reference `course_id` → `course` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-course_registration"></a>
## `course_registration`

Student semester course registration (unit limits, prerequisites, carry-overs, clashes, adviser approval)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the course section |
| Module | `academic` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-HED-02, FR-ACA-112 |
| Pages | HED-03 |
| Events | ACA.COURSE_REGISTERED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `course_section_id` → `course_section` | `BINARY(16)` | no |  |  |
| `is_carry_over` | `BOOLEAN` | no |  |  |
| `units` | `DECIMAL(4,1)` | no |  |  |
| `adviser_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `approved_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, adviser_approved, registered, dropped |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, course_section_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)
- Soft reference `adviser_staff_id` → `staff` — cross-zone (ops → registry)

