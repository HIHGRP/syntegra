# CUR — Curriculum 360, adoption, teaching chain evidence and zero-gap coverage assurance

Federal and state curricula captured as structured Curriculum 360 (subject → strand → theme → topic → objective/competency with hours, assessment and teacher-qualification requirements), versioned and immutable once published; state adaptations layered on federal versions; adoption resolved and stamped on every class (MFS §5.1, FR-CUR-01–15, 101–115). The teaching chain evidence — scheme of work, lesson delivery log — and the coverage engine's gap register (invariants G1–G12) live in the ops zone of the institution's tenant. Compliance scores are computed in the warehouse (metric CUR-COMPLIANCE).

Module (system of record): `curriculum` · default zone: **registry** · default retention: `RS-CUR-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`curriculum`](#registry-curriculum) | registry | master | public | lifecycle | Curriculum 360 master (national, state, international or institutional framework) |
| [`curriculum_version`](#registry-curriculum_version) | registry | config | public | versioned | Immutable published version of a curriculum (copy-on-write; author ≠ approver) |
| [`curriculum_node`](#registry-curriculum_node) | registry | config | public | versioned | Strand, theme, topic, learning objective or competency of a curriculum version |
| [`curriculum_adoption`](#registry-curriculum_adoption) | registry | link | internal | effective | Which curriculum version applies to which institution, level, cohort and period (resolved automatically) |
| [`scheme_of_work`](#ops-scheme_of_work) | ops | transaction | internal | versioned | Scheme of work for a teaching assignment — auto-drafted from curriculum hours and the calendar, edited by the teacher (G5, G10) |
| [`scheme_week`](#ops-scheme_week) | ops | link | internal | none | Week of a scheme of work with the curriculum objectives placed in it |
| [`delivery_log`](#ops-delivery_log) | ops | event | internal | append | Evidence that a lesson was delivered — objectives covered, learners present, note (G6) |
| [`coverage_gap`](#ops-coverage_gap) | ops | transaction | internal | lifecycle | Coverage gap — a breached teaching-chain invariant (G1–G12) with owner, severity, due date and escalation |
| [`gap_event`](#ops-gap_event) | ops | event | internal | append | History of a coverage gap (opened, reminded, escalated, fix proposed, closed) — append-only |

<a id="registry-curriculum"></a>
## `curriculum`

Curriculum 360 master (national, state, international or institutional framework)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `curriculum` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-01, FR-CUR-05, FR-CUR-101, FR-CUR-115 |
| Pages | CUR-01, CUR-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(48)` | no |  | e.g. NG-NERDC-MATH-JSS |
| `title` | `VARCHAR(300)` | no |  |  |
| `framework` | `VARCHAR(32)` | no |  | national, state, cambridge, ib, pearson, competency, institutional · code list `curriculum_framework` |
| `subject_id` → `subject` | `BINARY(16)` | yes |  |  |
| `levels` | `JSON` | no |  | code list `education_level` |
| `authority` | `VARCHAR(32)` | no |  | NERDC, State MoE, NBTE, NCCE, NUC … · code list `regulator` |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

<a id="registry-curriculum_version"></a>
## `curriculum_version`

Immutable published version of a curriculum (copy-on-write; author ≠ approver)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | none |
| Module | `curriculum` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-01, FR-CUR-03, FR-CUR-04, FR-CUR-10, FR-CUR-101 |
| Pages | CUR-02, CUR-03, CUR-04 |
| Events | CUR.APPROVED, CUR.PUBLISHED, CUR.WITHDRAWN |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `curriculum_id` → `curriculum` | `BINARY(16)` | no |  |  |
| `version_label` | `VARCHAR(32)` | no |  | e.g. 3.1 |
| `base_version_id` → `curriculum_version` | `BINARY(16)` | yes |  | Federal version a state adaptation layers on |
| `is_adaptation` | `BOOLEAN` | no |  |  |
| `language` | `VARCHAR(35)` | yes |  | Curriculum versions by language of instruction |
| `status` | `VARCHAR(32)` | no |  | values: draft, review, approved, published, superseded, withdrawn |
| `effective_from` | `DATE` | yes |  |  |
| `effective_to` | `DATE` | yes |  |  |
| `authored_by` → `app_user` | `BINARY(16)` | no |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `approval_reason` | `TEXT` | yes |  |  |
| `source_document_id` | `BINARY(16)` | yes |  | Digitised source (captured from paper; human approval before publication) |
| `content_hash` | `BINARY(32)` | yes |  | Hash of the node tree at publication |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, curriculum_id, version_label)

- Check `four_eyes`: `approved_by IS NULL OR approved_by <> authored_by`

<a id="registry-curriculum_node"></a>
## `curriculum_node`

Strand, theme, topic, learning objective or competency of a curriculum version

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | none |
| Module | `curriculum` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-02, FR-CUR-08 |
| Pages | CUR-02, CUR-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `version_id` → `curriculum_version` | `BINARY(16)` | no |  |  |
| `parent_id` → `curriculum_node` | `BINARY(16)` | yes |  |  |
| `node_code` | `VARCHAR(48)` | no |  | Unique within the version |
| `kind` | `VARCHAR(32)` | no |  | values: subject, strand, theme, topic, objective, competency |
| `statement` | `TEXT` | no |  |  |
| `requirement` | `VARCHAR(32)` | no |  | mandatory, optional, recommended, restricted · values: mandatory, optional, recommended, restricted |
| `is_state_addition` | `BOOLEAN` | no |  |  |
| `min_hours` | `DECIMAL(6,1)` | yes |  |  |
| `is_assessment_required` | `BOOLEAN` | no |  |  |
| `teacher_requirements` | `JSON` | yes |  | Required qualification and specialism |
| `resource_requirements` | `JSON` | yes |  |  |
| `term_hint` | `SMALLINT` | yes |  | Suggested term for scheme-of-work drafting |
| `sort_key` | `INT` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, version_id, node_code)

<a id="registry-curriculum_adoption"></a>
## `curriculum_adoption`

Which curriculum version applies to which institution, level, cohort and period (resolved automatically)

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | internal |
| History | effective |
| Scope | owned |
| Module | `curriculum` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-07, FR-CUR-102, FR-CUR-103, FR-CUR-114 |
| Pages | CUR-06, CUR-101, ACA-101 |
| Events | CUR.ADOPTION_RESOLVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `version_id` → `curriculum_version` | `BINARY(16)` | no |  |  |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `cohort_start_year` | `SMALLINT` | yes |  |  |
| `is_additional` | `BOOLEAN` | no |  | Approved institution addition (Cambridge, IB, faith studies) |
| `resolved_by` | `VARCHAR(32)` | no |  | values: automatic, state_adaptation, institution_addition, exception |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, institution_id, education_level)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-scheme_of_work"></a>
## `scheme_of_work`

Scheme of work for a teaching assignment — auto-drafted from curriculum hours and the calendar, edited by the teacher (G5, G10)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | versioned |
| Scope | derived: the class |
| Module | `curriculum` |
| Origin | appj (Appendix J `lesson_plan`) |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-110, FR-LMS-102 |
| Pages | CUR-09, LMS-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_subject_plan_id` → `class_subject_plan` | `BINARY(16)` | yes |  |  |
| `course_section_id` → `course_section` | `BINARY(16)` | yes |  |  |
| `teaching_assignment_id` → `teaching_assignment` | `BINARY(16)` | no |  |  |
| `curriculum_version_id` → `curriculum_version` | `BINARY(16)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `is_auto_drafted` | `BOOLEAN` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `curriculum_version_id` → `curriculum_version` — cross-zone (ops → registry)

<a id="ops-scheme_week"></a>
## `scheme_week`

Week of a scheme of work with the curriculum objectives placed in it

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | internal |
| History | none |
| Scope | derived: the scheme |
| Module | `curriculum` |
| Origin | ceda |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-110 |
| Pages | CUR-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scheme_id` → `scheme_of_work` | `BINARY(16)` | no |  |  |
| `week_no` | `SMALLINT` | no |  |  |
| `week_starts_on` | `DATE` | no |  |  |
| `node_ids` | `JSON` | no |  | Curriculum objectives planned for the week |
| `planned_minutes` | `INT` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scheme_id, week_no)

<a id="ops-delivery_log"></a>
## `delivery_log`

Evidence that a lesson was delivered — objectives covered, learners present, note (G6)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | owned |
| Module | `curriculum` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-111, FR-CUR-09 |
| Pages | CUR-09, ACA-05 |
| Events | CUR.LESSON_DELIVERED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `lesson_occurrence_id` → `lesson_occurrence` | `BINARY(16)` | no |  |  |
| `teaching_assignment_id` → `teaching_assignment` | `BINARY(16)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `node_ids` | `JSON` | no |  | Objectives covered |
| `delivered_minutes` | `INT` | no |  |  |
| `is_as_planned` | `BOOLEAN` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | class_page, staff_app, lms_lesson · values: class_page, staff_app, lms_lesson, import |
| `learners_present` | `SMALLINT` | yes |  |  |
| `note` | `VARCHAR(1000)` | yes |  |  |
| `delivered_on` | `DATE` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-coverage_gap"></a>
## `coverage_gap`

Coverage gap — a breached teaching-chain invariant (G1–G12) with owner, severity, due date and escalation  

Deduplicated — one open gap per class-subject (or section) per rule. Only people close gaps.

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `curriculum` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-106, FR-CUR-107, FR-CUR-108, FR-CUR-113, FR-CUR-109, FR-ACA-112, FR-CUR-11 |
| Pages | CUR-103, CUR-101, CUR-102 |
| Events | CUR.GAP_OPENED, CUR.GAP_ESCALATED, CUR.GAP_CLOSED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule` | `VARCHAR(32)` | no |  | values: g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12 |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `class_subject_plan_id` → `class_subject_plan` | `BINARY(16)` | yes |  |  |
| `course_section_id` → `course_section` | `BINARY(16)` | yes |  |  |
| `teaching_assignment_id` → `teaching_assignment` | `BINARY(16)` | yes |  |  |
| `learners_affected` | `SMALLINT` | no |  |  |
| `owner_role` | `VARCHAR(16)` | no |  |  |
| `owner_user_id` | `BINARY(16)` | yes |  |  |
| `due_on` | `DATE` | no |  |  |
| `escalation_level` | `SMALLINT` | no |  |  |
| `escalated_to_scope_id` | `BINARY(16)` | yes |  |  |
| `suggested_fixes` | `JSON` | yes |  | Ranked qualified teachers with spare load, LGA deployment, remote teaching |
| `accepted_by_head` | `BOOLEAN` | no |  | Gap accepted (e.g. leaver handover) |
| `opened_at` | `DATETIME(6)` | no |  |  |
| `closed_at` | `DATETIME(6)` | yes |  |  |
| `closed_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, escalated, accepted, closed |
| `open_key` | `VARCHAR(120)` | yes |  | rule:target while open; NULL when closed (one open gap per target per rule) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, open_key)
- Index: (tenant_id, institution_id, status)
- Index: (tenant_id, due_on)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-gap_event"></a>
## `gap_event`

History of a coverage gap (opened, reminded, escalated, fix proposed, closed) — append-only

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `curriculum` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-CUR-107 |
| Pages | CUR-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `gap_id` → `coverage_gap` | `BINARY(16)` | no |  |  |
| `event_kind` | `VARCHAR(32)` | no |  | values: opened, updated, reminded, fix_proposed, escalated, accepted, closed, reopened |
| `actor` | `BINARY(16)` | yes |  | User or agent service identity |
| `detail` | `JSON` | yes |  |  |
| `linked_thread_ref` | `VARCHAR(128)` | yes |  | Workspace-messaging thread (FR-COM-110) |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

