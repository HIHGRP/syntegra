# ASM — Assessment, grading, moderation, targets, report cards, examinations, results, GPA and transcripts

Assessments traceable to curriculum objectives, configurable grading scales, markbooks with hard and soft validation, moderation, target grades, report cards (FR-ASM-01–07, 101–103), internal and external examinations with entries, sittings, seating and invigilation, immutable committed results, GPA/CGPA and classification, and signed transcripts (FR-EXM-01–08, 101–102). Results are permanent records (MFS §13.6). Exam-body results arriving by file or API are matched to Learner 360 before commit.

Module (system of record): `assessment` · default zone: **ops** · default retention: `RS-LRN-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`grading_scale`](#registry-grading_scale) | registry | config | public | versioned | Configurable grading scale (percentage, letter, grade points, GPA, pass/fail, competency levels, degree classes) |
| [`grade_band`](#registry-grade_band) | registry | config | public | versioned | Band of a grading scale (contiguous and non-overlapping) |
| [`assessment`](#ops-assessment) | ops | config | internal | lifecycle | Assessment 360 definition (formative, summative, coursework, practical, competency, CA test, examination) |
| [`markbook_column`](#ops-markbook_column) | ops | config | internal | none | Teacher marksheet column (yes/no, numeric, grade, date, comment) for offline spreadsheet round-trips |
| [`assessment_result`](#ops-assessment_result) | ops | transaction | confidential | lifecycle | Mark per learner per assessment (hard ≤ max mark; corrections after lock need head approval) |
| [`moderation_sample`](#ops-moderation_sample) | ops | transaction | confidential | lifecycle | Moderation sample with moderator mark and tolerance outcome |
| [`target_grade`](#ops-target_grade) | ops | transaction | confidential | effective | Target grade from prior attainment and tracking points, with RAG progress |
| [`external_assessment_import`](#ops-external_assessment_import) | ops | transaction | confidential | lifecycle | Historical or external assessment data import for longitudinal tracking and benchmarking |
| [`report_card_run`](#ops-report_card_run) | ops | transaction | internal | lifecycle | Report-card generation run (templates, completeness checks, publication to the parent portal) |
| [`report_card`](#ops-report_card) | ops | transaction | confidential | append | Published report card of a learner for a period (document stored to the learner record) |
| [`exam_series`](#ops-exam_series) | ops | config | internal | lifecycle | Examination 360 series (internal or external body, qualification, curriculum, programme) |
| [`exam_paper`](#ops-exam_paper) | ops | config | internal | none | Paper or component of a series (subject, duration, OSCE station) |
| [`exam_entry`](#ops-exam_entry) | ops | transaction | confidential | lifecycle | Candidate entry (eligibility checks, access arrangements, fees) |
| [`exam_sitting`](#ops-exam_sitting) | ops | transaction | internal | lifecycle | Sitting of a paper — room, desk layout, seat allocation and invigilators |
| [`exam_result`](#ops-exam_result) | ops | transaction | confidential | append | Result per candidate per paper (immutable once committed) |
| [`result_import`](#ops-result_import) | ops | transaction | confidential | lifecycle | Import of results from an exam body (file or API) with candidate matching and anomaly review |
| [`exam_anomaly`](#ops-exam_anomaly) | ops | queue | confidential | lifecycle | Statistical anomaly for human review (distribution shift, similarity cluster, improbable improvement) — never auto-penalised |
| [`grade_broadsheet`](#ops-grade_broadsheet) | ops | projection | confidential | snapshot | Grade broadsheet per class, subject and series (spreadsheet export) |
| [`academic_standing`](#ops-academic_standing) | ops | transaction | confidential | lifecycle | GPA/CGPA, credits, progression and classification per learner per period (borderline cases flagged) |
| [`transcript`](#ops-transcript) | ops | transaction | confidential | append | Digitally signed, verifiable transcript (registered in the certificate registry as a credential of kind transcript) |

<a id="registry-grading_scale"></a>
## `grading_scale`

Configurable grading scale (percentage, letter, grade points, GPA, pass/fail, competency levels, degree classes)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `assessment` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-ASM-03 |
| Pages | ASM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `scale_kind` | `VARCHAR(32)` | no |  | values: percentage, letter, grade_points, gpa, pass_fail, competency, degree_class |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

<a id="registry-grade_band"></a>
## `grade_band`

Band of a grading scale (contiguous and non-overlapping)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | none |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-ASM-03 |
| Pages | ASM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `grading_scale_id` → `grading_scale` | `BINARY(16)` | no |  |  |
| `label` | `VARCHAR(16)` | no |  | A1, B2, C4, Distinction, Level 3 |
| `min_score` | `DECIMAL(7,3)` | no |  |  |
| `max_score` | `DECIMAL(7,3)` | no |  |  |
| `grade_points` | `DECIMAL(4,2)` | yes |  |  |
| `is_pass` | `BOOLEAN` | no |  |  |
| `is_credit` | `BOOLEAN` | no |  | Counts as a credit (5 credits incl. English and Mathematics) |
| `sort_order` | `SMALLINT` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, grading_scale_id, label)

- Check `range`: `max_score >= min_score`

<a id="ops-assessment"></a>
## `assessment`

Assessment 360 definition (formative, summative, coursework, practical, competency, CA test, examination)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-01, FR-ASM-02, FR-CUR-111, FR-LMS-112 |
| Pages | ASM-02, ASM-01 |
| Events | ASM.ASSESSMENT_CREATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `class_subject_plan_id` → `class_subject_plan` | `BINARY(16)` | yes |  |  |
| `course_section_id` → `course_section` | `BINARY(16)` | yes |  |  |
| `assignment_id` → `assignment` | `BINARY(16)` | yes |  | LMS assignment that posts its marks here |
| `title` | `VARCHAR(300)` | no |  |  |
| `assessment_kind` | `VARCHAR(32)` | no |  | values: formative, summative, coursework, practical, competency, ca_test, examination, homework, quiz |
| `max_mark` | `DECIMAL(7,3)` | no |  |  |
| `weight` | `DECIMAL(6,3)` | no |  |  |
| `assessed_on` | `DATE` | yes |  |  |
| `grading_scale_id` → `grading_scale` | `BINARY(16)` | yes |  |  |
| `node_ids` | `JSON` | yes |  | Curriculum objectives assessed (G7) |
| `is_moderated` | `BOOLEAN` | no |  |  |
| `locked_at` | `DATETIME(6)` | yes |  | Results locked after approval |
| `status` | `VARCHAR(32)` | no |  | values: draft, open, marking, moderated, approved, locked |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `grading_scale_id` → `grading_scale` — declared soft
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-markbook_column"></a>
## `markbook_column`

Teacher marksheet column (yes/no, numeric, grade, date, comment) for offline spreadsheet round-trips

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | derived: the class-subject |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-103 |
| Pages | ASM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `class_subject_plan_id` → `class_subject_plan` | `BINARY(16)` | no |  |  |
| `assessment_id` → `assessment` | `BINARY(16)` | yes |  |  |
| `label` | `VARCHAR(80)` | no |  |  |
| `column_kind` | `VARCHAR(32)` | no |  | values: yes_no, numeric, grade, date, comment |
| `sort_order` | `SMALLINT` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-assessment_result"></a>
## `assessment_result`

Mark per learner per assessment (hard ≤ max mark; corrections after lock need head approval)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the assessment's class |
| Module | `assessment` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-02, FR-ASM-05, FR-LMS-112 |
| Pages | ASM-01, LRN-04 |
| Events | ASM.RESULTS_LOCKED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `assessment_id` → `assessment` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `score` | `DECIMAL(7,3)` | yes |  |  |
| `grade_label` | `VARCHAR(16)` | yes |  |  |
| `objective_results` | `JSON` | yes |  | Per curriculum objective (curriculum evidence) |
| `is_missing_work` | `BOOLEAN` | no |  |  |
| `access_arrangement` | `VARCHAR(200)` | yes |  | Applied adjustment (no need detail) |
| `comment` | `VARCHAR(1000)` | yes |  |  |
| `entered_by` | `BINARY(16)` | no |  |  |
| `corrected_after_lock` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, assessment_id, learner_id)
- Index: (tenant_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-moderation_sample"></a>
## `moderation_sample`

Moderation sample with moderator mark and tolerance outcome

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the assessment's class |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-04, FR-LMS-111 |
| Pages | ASM-05, LMS-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `assessment_id` → `assessment` | `BINARY(16)` | yes |  |  |
| `submission_mark_id` → `submission_mark` | `BINARY(16)` | yes |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `original_score` | `DECIMAL(7,3)` | no |  |  |
| `moderated_score` | `DECIMAL(7,3)` | yes |  |  |
| `moderator_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `within_tolerance` | `BOOLEAN` | yes |  |  |
| `note` | `VARCHAR(1000)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `moderator_staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-target_grade"></a>
## `target_grade`

Target grade from prior attainment and tracking points, with RAG progress

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | effective |
| Scope | derived: the learner's class |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-101, FR-ILP-101 |
| Pages | ASM-01, LRN-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | no |  |  |
| `target_label` | `VARCHAR(16)` | no |  |  |
| `method` | `VARCHAR(32)` | no |  | values: prior_attainment, tracking_points, manual |
| `working_at_label` | `VARCHAR(16)` | yes |  |  |
| `rag` | `VARCHAR(32)` | yes |  | values: red, amber, green |
| `gap_points` | `DECIMAL(6,2)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `subject_id` → `subject` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-external_assessment_import"></a>
## `external_assessment_import`

Historical or external assessment data import for longitudinal tracking and benchmarking

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-102 |
| Pages | ASM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `source` | `VARCHAR(200)` | no |  |  |
| `cohort_label` | `VARCHAR(60)` | yes |  |  |
| `rows_total` | `INT UNSIGNED` | no |  |  |
| `rows_matched` | `INT UNSIGNED` | no |  |  |
| `import_job_id` → `import_job` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: uploaded, mapped, validating, validated, matching, staged, committed, rolled_back, failed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-report_card_run"></a>
## `report_card_run`

Report-card generation run (templates, completeness checks, publication to the parent portal)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-06, FR-ASM-07 |
| Pages | ASM-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `template_code` | `VARCHAR(40)` | no |  |  |
| `class_group_ids` | `JSON` | no |  |  |
| `completeness` | `JSON` | yes |  | Missing marks and comments per class |
| `withholding_policy_id` → `policy_rule` | `BINARY(16)` | yes |  | Only an explicitly approved policy; never for SEND or safeguarding-flagged learners |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, previewed, running, awaiting_approval, approved, issued, completed, failed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)
- Soft reference `withholding_policy_id` → `policy_rule` — declared soft
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-report_card"></a>
## `report_card`

Published report card of a learner for a period (document stored to the learner record)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | append |
| Scope | derived: the learner's class |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-ASM-06, FR-LRN-102 |
| Pages | ASM-04, FAM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `run_id` → `report_card_run` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `document_id` | `BINARY(16)` | no |  | PDF in the records zone |
| `content_hash` | `BINARY(32)` | no |  |  |
| `released_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, run_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-exam_series"></a>
## `exam_series`

Examination 360 series (internal or external body, qualification, curriculum, programme)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-01, FR-EXM-05, FR-MED-102 |
| Pages | EXM-01, EXM-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `exam_body` | `VARCHAR(32)` | no |  | code list `exam_body` |
| `name` | `VARCHAR(300)` | no |  |  |
| `qualification_id` → `qualification` | `BINARY(16)` | yes |  |  |
| `programme_id` → `programme` | `BINARY(16)` | yes |  |  |
| `curriculum_version_id` → `curriculum_version` | `BINARY(16)` | yes |  |  |
| `entry_opens_on` | `DATE` | yes |  |  |
| `entry_closes_on` | `DATE` | yes |  |  |
| `results_release_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: setup, entries_open, entries_closed, sitting, results_import, results_approved, released, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `qualification_id` → `qualification` — declared soft
- Soft reference `programme_id` → `programme` — declared soft
- Soft reference `curriculum_version_id` → `curriculum_version` — declared soft
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-exam_paper"></a>
## `exam_paper`

Paper or component of a series (subject, duration, OSCE station)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | derived: the series |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-03, FR-MED-102 |
| Pages | EXM-03, MED-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `series_id` → `exam_series` | `BINARY(16)` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | yes |  |  |
| `paper_code` | `VARCHAR(20)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `duration_minutes` | `INT` | no |  |  |
| `is_osce_station` | `BOOLEAN` | no |  |  |
| `station_rubric` | `JSON` | yes |  | OSCE station design and scoring |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, series_id, paper_code)

- Soft reference `subject_id` → `subject` — declared soft

<a id="ops-exam_entry"></a>
## `exam_entry`

Candidate entry (eligibility checks, access arrangements, fees)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-02, FR-INS-07, FR-PVT-114 |
| Pages | EXM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `series_id` → `exam_series` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `candidate_number` | `VARCHAR(32)` | yes |  |  |
| `subjects` | `JSON` | no |  |  |
| `eligibility` | `JSON` | yes |  | Checks: enrolment, subjects studied, identity verified, attendance, institution authorisation |
| `access_arrangements` | `JSON` | yes |  | Authorised arrangements (no need detail) |
| `is_external_candidate` | `BOOLEAN` | no |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, eligible, blocked, entered, withdrawn, absent, resulted |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, series_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-exam_sitting"></a>
## `exam_sitting`

Sitting of a paper — room, desk layout, seat allocation and invigilators

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-03, FR-EXM-101 |
| Pages | EXM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `paper_id` → `exam_paper` | `BINARY(16)` | no |  |  |
| `room_id` → `room` | `BINARY(16)` | no |  |  |
| `starts_at` | `DATETIME(6)` | no |  |  |
| `desk_layout` | `JSON` | no |  |  |
| `seat_allocations` | `JSON` | no |  | Candidate → desk label |
| `invigilator_staff_ids` | `JSON` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-exam_result"></a>
## `exam_result`

Result per candidate per paper (immutable once committed)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | append |
| Scope | derived: the entry |
| Module | `assessment` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-04, FR-EXM-102 |
| Pages | EXM-04, EXM-05, LRN-04 |
| Events | EXAM.RESULTS_COMMITTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `entry_id` → `exam_entry` | `BINARY(16)` | no |  |  |
| `paper_id` → `exam_paper` | `BINARY(16)` | no |  |  |
| `score` | `DECIMAL(7,3)` | yes |  |  |
| `grade_label` | `VARCHAR(16)` | no |  |  |
| `result_import_id` → `result_import` | `BINARY(16)` | yes |  |  |
| `committed_at` | `DATETIME(6)` | no |  |  |
| `committed_by` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, entry_id, paper_id)

<a id="ops-result_import"></a>
## `result_import`

Import of results from an exam body (file or API) with candidate matching and anomaly review

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-04, FR-EXM-08 |
| Pages | EXM-04, EXM-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `series_id` → `exam_series` | `BINARY(16)` | no |  |  |
| `source_document_id` | `BINARY(16)` | yes |  |  |
| `rows_total` | `INT UNSIGNED` | no |  |  |
| `rows_matched` | `INT UNSIGNED` | no |  |  |
| `rows_in_review` | `INT UNSIGNED` | no |  |  |
| `anomalies` | `JSON` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: uploaded, mapped, validating, validated, matching, staged, committed, rolled_back, failed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-exam_anomaly"></a>
## `exam_anomaly`

Statistical anomaly for human review (distribution shift, similarity cluster, improbable improvement) — never auto-penalised

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-08 |
| Pages | EXM-08, CMD-15 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `series_id` → `exam_series` | `BINARY(16)` | no |  |  |
| `anomaly_kind` | `VARCHAR(32)` | no |  | values: distribution_shift, similarity_cluster, improbable_improvement, timing, other |
| `evidence` | `JSON` | no |  |  |
| `affected_entry_ids` | `JSON` | yes |  |  |
| `assigned_to` | `BINARY(16)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | yes |  | values: no_issue, explained, action_taken, referred, confirmed |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-grade_broadsheet"></a>
## `grade_broadsheet`

Grade broadsheet per class, subject and series (spreadsheet export)

| | |
|---|---|
| Zone | ops |
| Kind | projection |
| Classification | confidential |
| History | snapshot |
| Scope | owned |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-102 |
| Pages | EXM-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `series_id` → `exam_series` | `BINARY(16)` | yes |  |  |
| `class_group_id` → `class_group` | `BINARY(16)` | no |  |  |
| `generated_at` | `DATETIME(6)` | no |  |  |
| `document_id` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-academic_standing"></a>
## `academic_standing`

GPA/CGPA, credits, progression and classification per learner per period (borderline cases flagged)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the enrolment's institution |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-06, FR-HED-05 |
| Pages | EXM-07, HED-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `credits_attempted` | `DECIMAL(6,1)` | no |  |  |
| `credits_earned` | `DECIMAL(6,1)` | no |  |  |
| `gpa` | `DECIMAL(4,2)` | yes |  |  |
| `cgpa` | `DECIMAL(4,2)` | yes |  |  |
| `progression` | `VARCHAR(32)` | yes |  | values: progress, progress_with_carryover, repeat, probation, withdraw, graduate |
| `classification` | `VARCHAR(32)` | yes |  | code list `degree_class` |
| `is_borderline` | `BOOLEAN` | no |  |  |
| `board_decision` | `VARCHAR(500)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, enrolment_id, period_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)

<a id="ops-transcript"></a>
## `transcript`

Digitally signed, verifiable transcript (registered in the certificate registry as a credential of kind transcript)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | append |
| Scope | derived: the learner |
| Module | `assessment` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EXM-07 |
| Pages | EXM-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `certificate_id` → `certificate` | `BINARY(16)` | yes |  | Registry record carrying number, hash and signature |
| `document_id` | `BINARY(16)` | no |  |  |
| `content_hash` | `BINARY(32)` | no |  |  |
| `issued_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)
- Soft reference `certificate_id` → `certificate` — cross-zone (ops → registry)

