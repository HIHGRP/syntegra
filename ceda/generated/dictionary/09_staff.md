# STF — Staff / Teacher 360, authorisations, HR, cover, recruitment, CPD, training and payroll

One record per staff member across posts and institutions (FR-STF-01). The staff identity, posts and teaching authorisations (qualifications, TRCN registration, subject-and-level authorisations, safer- recruitment checks) form the state teacher register in the registry zone, because the coverage engine (G2, G3, G9, G11), teacher deployment (STF-10) and private-institution regulation all need them. Day-to-day HR — absence and cover, recruitment, appraisal, CPD, statutory training and payroll — is operational (ops zone). Allegations about adults are in the vault (domain SAF).

Module (system of record): `people` · default zone: **registry** · default retention: `RS-STF-FILE`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`staff`](#registry-staff) | registry | master | confidential | lifecycle | Staff / Teacher 360 master (one person, many posts) |
| [`staff_post`](#registry-staff_post) | registry | link | confidential | effective | Post held by a staff member at an institution (employer, unit, title, grade, contract, FTE, line manager) |
| [`staff_qualification`](#registry-staff_qualification) | registry | master | confidential | lifecycle | Qualification, professional registration, teaching authorisation (subject × level) or check, with expiry and verification |
| [`professional_registration_check`](#registry-professional_registration_check) | registry | event | confidential | append | Verification of a professional registration with its register (TRCN, MDCN, NMCN …) |
| [`staff_absence`](#ops-staff_absence) | ops | transaction | confidential | lifecycle | Staff absence (triggers the cover process and G8 checks) |
| [`cover_assignment`](#ops-cover_assignment) | ops | transaction | internal | lifecycle | Cover for a lesson affected by staff absence (never auto-assigned unqualified; G8) |
| [`vacancy`](#ops-vacancy) | ops | transaction | internal | lifecycle | Vacancy in the recruitment workflow |
| [`job_application`](#ops-job_application) | ops | transaction | restricted | lifecycle | Application for a vacancy (blind scoring by default; references and checks before offer) |
| [`appraisal`](#ops-appraisal) | ops | transaction | restricted | lifecycle | Annual appraisal with objectives, evidence, ratings and development plan |
| [`cpd_record`](#ops-cpd_record) | ops | transaction | confidential | lifecycle | CPD and professional learning record (including LMS training and evidenced digital teaching practice) |
| [`training_course`](#ops-training_course) | ops | config | internal | versioned | Safeguarding or statutory training course (native LMS staff course space or SCORM/xAPI package) |
| [`training_completion`](#ops-training_completion) | ops | transaction | confidential | lifecycle | Completion of a training course by an adult (writes to Staff 360, CPD and the Education Passport) |
| [`staff_pulse_response`](#ops-staff_pulse_response) | ops | event | internal | append | Anonymous staff wellbeing pulse response (reported only in aggregate; no staff identifier stored) |
| [`payroll_tax_table`](#ops-payroll_tax_table) | ops | config | internal | versioned | Versioned payroll statutory table (PAYE, pension/PenCom, NHF) |
| [`payroll_run`](#ops-payroll_run) | ops | transaction | restricted | lifecycle | Pay run (two-person approval, bank file export, ledger posting) |
| [`payslip`](#ops-payslip) | ops | transaction | restricted | append | Payslip of one staff post in a pay run |

<a id="registry-staff"></a>
## `staff`

Staff / Teacher 360 master (one person, many posts)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: through the person's posts |
| Module | `people` |
| Origin | appj |
| Retention | `RS-STF-FILE` |
| Requirements | FR-STF-01, FR-ACA-113, FR-ACA-116, FR-DOC-108 |
| Pages | STF-01, STF-02, STF-03, STF-08, HOM-05 |
| Events | STF.CREATED, STF.LEFT |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_number` | `VARCHAR(20)` | no |  | STF-NNNN-NNNN with check digit |
| `given_name` | `VARCHAR(200)` | no |  |  |
| `middle_names` | `VARCHAR(200)` | yes |  |  |
| `family_name` | `VARCHAR(200)` | no |  |  |
| `name_phonetic` | `VARCHAR(120)` | no |  |  |
| `date_of_birth` | `DATE` | yes |  |  |
| `sex` | `VARCHAR(32)` | yes |  | code list `sex` |
| `phone` | `VARCHAR(16)` | yes |  |  |
| `email` | `VARCHAR(254)` | yes |  |  |
| `user_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `is_historic` | `BOOLEAN` | no |  | Created from a digitised personal file |
| `status` | `VARCHAR(32)` | no |  | values: onboarding, active, leaver, merged |
| `merged_into` → `staff` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, staff_number)

<a id="registry-staff_post"></a>
## `staff_post`

Post held by a staff member at an institution (employer, unit, title, grade, contract, FTE, line manager)  

Temporary posts (NYSC, volunteers) carry an end date and access expires automatically (MFS §4.4).

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | confidential |
| History | effective |
| Scope | owned |
| Module | `people` |
| Origin | appj |
| Retention | `RS-STF-FILE` |
| Requirements | FR-STF-01, FR-STF-11, FR-ACA-116, FR-CUR-109 |
| Pages | STF-02, STF-03, STF-10, ACA-102 |
| Events | STF.POST_STARTED, STF.POST_ENDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `org_unit_id` → `org_unit` | `BINARY(16)` | yes |  |  |
| `job_title` | `VARCHAR(300)` | no |  |  |
| `staff_category` | `VARCHAR(32)` | no |  | teaching, non_teaching, lecturer, graduate_assistant … · code list `staff_category` |
| `academic_rank` | `VARCHAR(32)` | yes |  | Professor, Senior Lecturer, Lecturer I … (load policy) · code list `academic_rank` |
| `grade_step` | `VARCHAR(20)` | yes |  |  |
| `contract` | `VARCHAR(32)` | no |  | values: permanent, fixed_term, part_time, adjunct, visiting, nysc, volunteer, graduate_assistant |
| `fte` | `DECIMAL(4,2)` | no |  |  |
| `employer_scope_id` → `scope_node` | `BINARY(16)` | yes |  | e.g. SUBEB, TESCOM, the private provider |
| `line_manager_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `is_temporary` | `BOOLEAN` | no |  |  |
| `leaving_reason` | `VARCHAR(32)` | yes |  | code list `leaving_reason` |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, staff_id)
- Index: (tenant_id, institution_id)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-staff_qualification"></a>
## `staff_qualification`

Qualification, professional registration, teaching authorisation (subject × level) or check, with expiry and verification

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the staff member |
| Module | `people` |
| Origin | appj |
| Retention | `RS-STF-FILE` |
| Requirements | FR-STF-02, FR-STF-04, FR-CUR-105, FR-ACA-113, FR-STF-102, FR-MED-103 |
| Pages | STF-02, STF-08, CUR-102, ACA-101 |
| Events | STF.AUTHORISATION_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: degree, certificate, registration, teaching_authorisation, specialism, check |
| `title` | `VARCHAR(300)` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | yes |  | For teaching authorisations |
| `subject_area_code` | `VARCHAR(40)` | yes |  | Tertiary specialism (subject area) |
| `levels` | `JSON` | yes |  | code list `education_level` |
| `issuer` | `VARCHAR(32)` | yes |  | TRCN, university, professional body · code list `regulator` |
| `reference` | `VARCHAR(64)` | yes |  |  |
| `issued_on` | `DATE` | yes |  |  |
| `expires_on` | `DATE` | yes |  |  |
| `verification` | `VARCHAR(32)` | no |  | values: unverified, pending, verified, failed, expired |
| `verified_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `document_id` | `BINARY(16)` | yes |  | Certificate scan (records zone) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, staff_id, kind)
- Index: (tenant_id, subject_id)
- Index: (tenant_id, expires_on)

<a id="registry-professional_registration_check"></a>
## `professional_registration_check`

Verification of a professional registration with its register (TRCN, MDCN, NMCN …)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-STF-02 |
| Pages | STF-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `qualification_id` → `staff_qualification` | `BINARY(16)` | no |  |  |
| `register` | `VARCHAR(32)` | no |  | code list `regulator` |
| `outcome` | `VARCHAR(32)` | no |  | values: match, partial_match, no_match, manual_review, error |
| `checked_at` | `DATETIME(6)` | no |  |  |
| `provider_ref` | `VARCHAR(128)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-staff_absence"></a>
## `staff_absence`

Staff absence (triggers the cover process and G8 checks)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-STF-06 |
| Pages | STF-06 |
| Events | STF.ABSENCE_RECORDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `staff_post_id` → `staff_post` | `BINARY(16)` | yes |  |  |
| `absence_type` | `VARCHAR(32)` | no |  | code list `absence_type` |
| `starts_at` | `DATETIME(6)` | no |  |  |
| `ends_at` | `DATETIME(6)` | no |  |  |
| `is_planned` | `BOOLEAN` | no |  |  |
| `reason_note` | `MEDIUMBLOB` | yes | special | Medical or personal detail (encrypted) |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, approved, rejected, recorded, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `staff_post_id` → `staff_post` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `window`: `ends_at > starts_at`

<a id="ops-cover_assignment"></a>
## `cover_assignment`

Cover for a lesson affected by staff absence (never auto-assigned unqualified; G8)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-TIM-05, FR-STF-06 |
| Pages | TIM-03, STF-06 |
| Events | TT.COVER_ASSIGNED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `absence_id` → `staff_absence` | `BINARY(16)` | no |  |  |
| `lesson_occurrence_id` → `lesson_occurrence` | `BINARY(16)` | no |  |  |
| `cover_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `is_qualified` | `BOOLEAN` | no |  |  |
| `rank_evidence` | `JSON` | yes |  | Qualified → free → lowest cover load → same department |
| `alternative` | `VARCHAR(32)` | yes |  | supervised_study_with_lms_work when no qualified cover · values: supervised_study_with_lms_work, merged_class, cancelled_lesson |
| `proposed_by` | `BINARY(16)` | yes |  | Cover Agent service identity or SLT user |
| `confirmed_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: proposed, booked, confirmed, declined, gap |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `cover_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-vacancy"></a>
## `vacancy`

Vacancy in the recruitment workflow

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-RECRUIT` |
| Requirements | FR-STF-05 |
| Pages | STF-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `org_unit_id` → `org_unit` | `BINARY(16)` | yes |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `subjects` | `JSON` | yes |  | Subjects and levels needed (links to coverage gaps) |
| `coverage_gap_id` → `coverage_gap` | `BINARY(16)` | yes |  | Gap that justified the vacancy |
| `closing_on` | `DATE` | yes |  |  |
| `workflow_instance_id` → `workflow_instance` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, open, closed, filled, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `org_unit_id` → `org_unit` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-job_application"></a>
## `job_application`

Application for a vacancy (blind scoring by default; references and checks before offer)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | derived: the vacancy |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-RECRUIT` |
| Requirements | FR-STF-05 |
| Pages | STF-05, STF-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `vacancy_id` → `vacancy` | `BINARY(16)` | no |  |  |
| `applicant_name` | `VARCHAR(200)` | no |  |  |
| `applicant_email` | `VARCHAR(254)` | no |  |  |
| `applicant_phone` | `VARCHAR(16)` | yes |  |  |
| `cv_document_id` | `BINARY(16)` | yes |  |  |
| `blind_score` | `DECIMAL(6,2)` | yes |  |  |
| `scores` | `JSON` | yes |  | Per criterion and panel member |
| `stage` | `VARCHAR(32)` | no |  | values: applied, shortlisted, interview, references, checks, offer, appointed, rejected, withdrawn |
| `staff_id` → `staff` | `BINARY(16)` | yes |  | Set on appointment (after identity matching) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-appraisal"></a>
## `appraisal`

Annual appraisal with objectives, evidence, ratings and development plan

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-STF-08 |
| Pages | STF-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `reviewer_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `cycle_label` | `VARCHAR(20)` | no |  | e.g. 2026/2027 |
| `objectives` | `JSON` | yes |  |  |
| `evidence` | `JSON` | yes |  |  |
| `rating` | `VARCHAR(32)` | yes |  | code list `appraisal_rating` |
| `development_plan` | `TEXT` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: planned, objectives_set, mid_year, final_review, signed_off |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, staff_id, cycle_label)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `reviewer_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-cpd_record"></a>
## `cpd_record`

CPD and professional learning record (including LMS training and evidenced digital teaching practice)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the staff member's posts |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-STF-07, FR-LMS-123, FR-LRN-101, FR-CUR-108 |
| Pages | STF-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `provider_name` | `VARCHAR(300)` | yes |  |  |
| `cpd_kind` | `VARCHAR(32)` | no |  | code list `cpd_kind` |
| `hours` | `DECIMAL(6,2)` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | yes |  | Route to a teaching authorisation |
| `completed_on` | `DATE` | no |  |  |
| `evidence_document_id` | `BINARY(16)` | yes |  |  |
| `source_kind` | `VARCHAR(40)` | yes |  | lms_course, digital_practice, external |
| `source_id` | `BINARY(16)` | yes |  |  |
| `expires_on` | `DATE` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `subject_id` → `subject` — cross-zone (ops → registry)

<a id="ops-training_course"></a>
## `training_course`

Safeguarding or statutory training course (native LMS staff course space or SCORM/xAPI package)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `people` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-STF-105, FR-STF-103 |
| Pages | STF-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `topic` | `VARCHAR(32)` | no |  | child protection, safe schools, first aid, fire safety, data protection, online safety, SEND awareness · code list `training_topic` |
| `course_space_id` → `course_space` | `BINARY(16)` | yes |  |  |
| `package_format` | `VARCHAR(32)` | yes |  | values: native_lms, scorm, xapi |
| `pass_mark` | `DECIMAL(6,3)` | yes |  |  |
| `renewal_months` | `SMALLINT` | yes |  |  |
| `required_for_roles` | `JSON` | yes |  | Role codes |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-training_completion"></a>
## `training_completion`

Completion of a training course by an adult (writes to Staff 360, CPD and the Education Passport)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the staff member's posts |
| Module | `people` |
| Origin | appj |
| Retention | `RS-STF-FILE` |
| Requirements | FR-STF-105, FR-STF-106, FR-STF-103 |
| Pages | STF-101 |
| Events | STF.TRAINING_COMPLETED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `course_id` → `training_course` | `BINARY(16)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `assigned_on` | `DATE` | no |  |  |
| `completed_on` | `DATE` | yes |  |  |
| `score` | `DECIMAL(6,3)` | yes |  |  |
| `passed` | `BOOLEAN` | yes |  |  |
| `certificate_document_id` | `BINARY(16)` | yes |  |  |
| `expires_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: assigned, in_progress, passed, failed, expired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, staff_id, course_id)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-staff_pulse_response"></a>
## `staff_pulse_response`

Anonymous staff wellbeing pulse response (reported only in aggregate; no staff identifier stored)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | owned |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-STF-104 |
| Pages | STF-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `survey_code` | `VARCHAR(40)` | no |  |  |
| `org_unit_id` → `org_unit` | `BINARY(16)` | yes |  |  |
| `answers` | `JSON` | no |  |  |
| `submitted_on` | `DATE` | no |  | Date only — no timestamp to resist re-identification |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `org_unit_id` → `org_unit` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-payroll_tax_table"></a>
## `payroll_tax_table`

Versioned payroll statutory table (PAYE, pension/PenCom, NHF)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | none |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-STF-09 |
| Pages | PAY-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `table_kind` | `VARCHAR(32)` | no |  | values: paye, pension, nhf, nhis, other |
| `version` | `INT UNSIGNED` | no |  |  |
| `bands` | `JSON` | no |  |  |
| `effective_from` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, table_kind, version)

<a id="ops-payroll_run"></a>
## `payroll_run`

Pay run (two-person approval, bank file export, ledger posting)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-STF-09 |
| Pages | PAY-01, PAY-02 |
| Events | PAY.RUN_APPROVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `employer_scope_id` → `scope_node` | `BINARY(16)` | no |  |  |
| `period_label` | `VARCHAR(7)` | no |  | YYYY-MM |
| `pay_date` | `DATE` | no |  |  |
| `gross_total_minor` | `BIGINT` | no |  | (minor units) |
| `net_total_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `prepared_by` | `BINARY(16)` | no |  |  |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `second_approver_id` | `BINARY(16)` | yes |  |  |
| `bank_file_document_id` | `BINARY(16)` | yes |  |  |
| `journal_id` → `journal` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, calculated, exceptions_review, approved, exported, posted, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, employer_scope_id, period_label)

- Soft reference `employer_scope_id` → `scope_node` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `two_person`: `second_approver_id IS NULL OR approved_by IS NULL OR second_approver_id <> approved_by`

<a id="ops-payslip"></a>
## `payslip`

Payslip of one staff post in a pay run

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `people` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-STF-09 |
| Pages | PAY-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `payroll_run_id` → `payroll_run` | `BINARY(16)` | no |  |  |
| `staff_post_id` → `staff_post` | `BINARY(16)` | no |  |  |
| `gross_minor` | `BIGINT` | no |  | (minor units) |
| `deductions_minor` | `BIGINT` | no |  | (minor units) |
| `net_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `line_items` | `JSON` | no |  | Earnings and deductions by code with tax table versions used |
| `bank_account_enc` | `VARBINARY(1024)` | yes | restricted | Envelope-encrypted bank_account. Payee bank account |
| `bank_account_last4` | `CHAR(4)` | yes | restricted | Last four characters of bank_account for masked display |
| `exception_flags` | `JSON` | yes |  | Exceptions reviewed before approval |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, payroll_run_id, staff_post_id)

- Soft reference `staff_post_id` → `staff_post` — cross-zone (ops → registry)

