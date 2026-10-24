# HRM — Enterprise Human Resource Management Suite — establishment, employment, postings, leave, promotion, employee relations, separation, payroll elements and payroll integrity

The enterprise HRMS for every employer in the education ecosystem — State Ministry, SUBEB, TESCOM/PPSMB, tertiary institutions and private providers (change request CR-001). It extends the staff register of domain STF rather than duplicating it: one staff master and one staff_post per post remain in STF; HRMS adds the approved establishment (positions), salary structures and cadres, the employment record of each post, posting orders that move staff between institutions and employers, promotions, separations, bank accounts and state-wide payroll integrity in the registry (the state HR hub), because deployment, ghost-worker and double-employment detection must see every employer at once. Leave, employee relations and payroll elements are operational and live in the employer's ops zone; payroll runs and payslips stay in STF. Integration: postings and separations drive IAM grants (role grants follow the posting; access ends at separation), coverage rules G8/G9/G11, cover, staff attendance, finance journals and the semantic layer.

Module (system of record): `hr` · default zone: **registry** · default retention: `RS-STF-FILE`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`salary_structure`](#registry-salary_structure) | registry | config | internal | versioned | Versioned salary structure (CONPSS, CONTISS, CONUASS, CONTEDISS, state teacher scales, private scales) |
| [`salary_scale_point`](#registry-salary_scale_point) | registry | reference | internal | append | Grade level and step of a salary structure version with annual basic and standard allowances |
| [`cadre`](#registry-cadre) | registry | config | internal | lifecycle | Career cadre with progression and statutory retirement rule (e.g. Teacher, Education Officer, Principal, Lecturer) |
| [`position`](#registry-position) | registry | master | internal | lifecycle | Approved establishment position (one seat) at an institution, unit or office, with cadre, grade range and specialism |
| [`employment_record`](#registry-employment_record) | registry | master | confidential | lifecycle | Employment record of a staff post — appointment, confirmation, grade and step, position held and projected retirement |
| [`staff_posting`](#registry-staff_posting) | registry | transaction | confidential | lifecycle | Posting order — first posting, transfer, redeployment or secondment of a staff member between institutions and employers |
| [`promotion_case`](#registry-promotion_case) | registry | transaction | confidential | lifecycle | Promotion case of a staff member in a promotion exercise (eligibility, examination, board decision, effective date) |
| [`separation`](#registry-separation) | registry | transaction | confidential | lifecycle | Separation from a post (resignation, retirement, death, dismissal, end of contract, transfer of service) with exit clearance |
| [`staff_bank_account`](#registry-staff_bank_account) | registry | master | restricted | lifecycle | Staff salary bank account (encrypted; lookup token for duplicate detection; dual approval and call-back on change) |
| [`hr_integrity_flag`](#registry-hr_integrity_flag) | registry | queue | restricted | lifecycle | Payroll integrity flag across all employers in the state (ghost worker, double employment, pay after exit …) |
| [`headcount_exercise`](#registry-headcount_exercise) | registry | transaction | internal | lifecycle | Staff headcount (verification) exercise at an institution — in person, biometric or video |
| [`headcount_result`](#registry-headcount_result) | registry | event | confidential | append | Outcome for one staff member in a headcount exercise |
| [`leave_policy`](#ops-leave_policy) | ops | config | internal | versioned | Leave entitlement rule by leave type, cadre and grade-level band (versioned) |
| [`leave_balance`](#ops-leave_balance) | ops | projection | confidential | none | Leave balance per staff member, leave type and leave year (the database refuses over-booking) |
| [`leave_request`](#ops-leave_request) | ops | transaction | confidential | lifecycle | Leave request with approval; approval creates the staff absence that starts cover (G8) |
| [`employee_relations_case`](#ops-employee_relations_case) | ops | transaction | restricted | lifecycle | Employee relations case — query, disciplinary, grievance, appeal or petition with due-process steps and a human outcome |
| [`pay_element`](#ops-pay_element) | ops | config | internal | versioned | Payroll element — earning, allowance, statutory or voluntary deduction, loan repayment or employer contribution (versioned) |
| [`staff_pay_element`](#ops-staff_pay_element) | ops | link | restricted | effective | Recurring pay element of a staff post (allowance, voluntary deduction, loan with balance), effective-dated |

<a id="registry-salary_structure"></a>
## `salary_structure`

Versioned salary structure (CONPSS, CONTISS, CONUASS, CONTEDISS, state teacher scales, private scales)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-HRM-02 |
| Pages | HRM-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(20)` | no |  | e.g. CONPSS, CONTISS, AB-TSS |
| `title` | `VARCHAR(300)` | no |  |  |
| `employer_scope_id` → `scope_node` | `BINARY(16)` | yes |  | NULL = available to every employer in scope |
| `currency` | `CHAR(3)` | no |  |  |
| `effective_from` | `DATE` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `approval_instrument` | `VARCHAR(200)` | yes |  | Circular or board resolution |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

<a id="registry-salary_scale_point"></a>
## `salary_scale_point`

Grade level and step of a salary structure version with annual basic and standard allowances

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-HRM-02, FR-HRM-10 |
| Pages | HRM-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `structure_id` → `salary_structure` | `BINARY(16)` | no |  |  |
| `grade_level` | `SMALLINT` | no |  |  |
| `step` | `SMALLINT` | no |  |  |
| `annual_basic_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `allowances` | `JSON` | yes |  | Standard allowances by element code, as amount or % of basic (housing, transport, rural posting …) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, structure_id, grade_level, step)

- Check `positive`: `annual_basic_minor > 0 AND grade_level BETWEEN 1 AND 17 AND step BETWEEN 1 AND 15`

<a id="registry-cadre"></a>
## `cadre`

Career cadre with progression and statutory retirement rule (e.g. Teacher, Education Officer, Principal, Lecturer)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-HRM-01, FR-HRM-03, FR-HRM-07 |
| Pages | HRM-09, HRM-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(20)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `staff_category` | `VARCHAR(32)` | no |  | code list `staff_category` |
| `is_teaching` | `BOOLEAN` | no |  |  |
| `salary_structure_code` | `VARCHAR(20)` | no |  |  |
| `entry_grade_level` | `SMALLINT` | no |  |  |
| `max_grade_level` | `SMALLINT` | no |  |  |
| `years_per_promotion` | `SMALLINT` | no |  |  |
| `retirement_age` | `SMALLINT` | no |  | 65 for teachers (Harmonised Retirement Age for Teachers in Nigeria Act 2022), 60 otherwise |
| `max_years_service` | `SMALLINT` | no |  | 40 for teachers, 35 otherwise |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

- Check `grades`: `entry_grade_level <= max_grade_level`

<a id="registry-position"></a>
## `position`

Approved establishment position (one seat) at an institution, unit or office, with cadre, grade range and specialism  

A staff post fills a position through its employment record. Vacant positions with a subject specialism feed the vacancy workflow (STF vacancy) and the teacher demand–supply metric.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-HRM-01, FR-HRM-15 |
| Pages | HRM-01, HRM-10, HRM-03 |
| Events | HR.POSITION_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `position_code` | `VARCHAR(32)` | no |  | POS-<institution code>-NNNN |
| `institution_id` → `institution` | `BINARY(16)` | yes |  | NULL for ministry, board or LGA office positions |
| `org_unit_id` → `org_unit` | `BINARY(16)` | yes |  |  |
| `employer_scope_id` → `scope_node` | `BINARY(16)` | no |  | SUBEB, TESCOM, ministry, tertiary institution or private provider |
| `title` | `VARCHAR(300)` | no |  |  |
| `cadre_id` → `cadre` | `BINARY(16)` | no |  |  |
| `staff_category` | `VARCHAR(32)` | no |  | code list `staff_category` |
| `grade_level_min` | `SMALLINT` | no |  |  |
| `grade_level_max` | `SMALLINT` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | yes |  | Specialism for teaching positions |
| `education_levels` | `JSON` | yes |  | code list `education_level` |
| `funding` | `VARCHAR(32)` | no |  | values: funded, unfunded, donor_funded, privately_funded |
| `budget_line` | `VARCHAR(40)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: proposed, approved, frozen, abolished |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, position_code)
- Index: (tenant_id, institution_id, status)
- Index: (tenant_id, employer_scope_id)
- Index: (tenant_id, subject_id)

- Check `grades`: `grade_level_min <= grade_level_max`

<a id="registry-employment_record"></a>
## `employment_record`

Employment record of a staff post — appointment, confirmation, grade and step, position held and projected retirement

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-HRM-03, FR-HRM-07, FR-HRM-15 |
| Pages | HRM-02, HRM-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_post_id` → `staff_post` | `BINARY(16)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `position_id` → `position` | `BINARY(16)` | yes |  |  |
| `cadre_id` → `cadre` | `BINARY(16)` | no |  |  |
| `employer_scope_id` → `scope_node` | `BINARY(16)` | no |  |  |
| `appointment_type` | `VARCHAR(32)` | no |  | values: first_appointment, transfer_of_service, secondment, contract, nysc, volunteer, private_hire |
| `appointment_letter_ref` | `VARCHAR(64)` | yes |  |  |
| `first_appointment_on` | `DATE` | no |  | Date of first appointment into the service |
| `present_appointment_on` | `DATE` | no |  |  |
| `confirmation_due_on` | `DATE` | yes |  |  |
| `confirmed_on` | `DATE` | yes |  |  |
| `salary_structure_id` → `salary_structure` | `BINARY(16)` | no |  |  |
| `grade_level` | `SMALLINT` | no |  |  |
| `step` | `SMALLINT` | no |  |  |
| `last_promotion_on` | `DATE` | yes |  |  |
| `retirement_due_on` | `DATE` | yes |  | Earlier of retirement age and maximum years of service (cadre rule) |
| `retirement_basis` | `VARCHAR(32)` | yes |  | values: age, length_of_service, contract_end, none |
| `status` | `VARCHAR(32)` | no |  | values: probation, confirmed, suspended, seconded, separated |
| `seat_key` | `BINARY(16)` | yes |  | position_id while the post is active (one active holder per position) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, staff_post_id)
- Unique: (tenant_id, seat_key)
- Index: (tenant_id, staff_id)
- Index: (tenant_id, position_id)
- Index: (tenant_id, retirement_due_on)
- Index: (tenant_id, employer_scope_id, status)

<a id="registry-staff_posting"></a>
## `staff_posting`

Posting order — first posting, transfer, redeployment or secondment of a staff member between institutions and employers  

Effective postings end the old staff_post, create the new one in the receiving position, move the staff member's role grants to the new institution scope and re-run coverage (G9 before, G2/G3 after).

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-HRM-04 |
| Pages | HRM-03, HRM-02 |
| Events | HR.POSTING_APPROVED, HR.POSTING_EFFECTIVE |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `order_number` | `VARCHAR(40)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `from_staff_post_id` → `staff_post` | `BINARY(16)` | yes |  |  |
| `to_position_id` → `position` | `BINARY(16)` | no |  |  |
| `to_institution_id` → `institution` | `BINARY(16)` | yes |  |  |
| `posting_kind` | `VARCHAR(32)` | no |  | values: first_posting, transfer, redeployment, secondment, promotion_posting, rationalisation, on_request, disciplinary |
| `reason` | `TEXT` | no |  |  |
| `effective_on` | `DATE` | no |  |  |
| `coverage_impact` | `JSON` | yes |  | Class-subjects left without a teacher of record (G9) at the sending institution |
| `requested_by` → `app_user` | `BINARY(16)` | no |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `workflow_instance_id` → `workflow_instance` | `BINARY(16)` | yes |  |  |
| `new_staff_post_id` → `staff_post` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, approved, effective, rejected, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, order_number)
- Index: (tenant_id, staff_id, status)
- Index: (tenant_id, to_position_id)
- Index: (tenant_id, effective_on)

- Check `four_eyes`: `approved_by IS NULL OR approved_by <> requested_by`

<a id="registry-promotion_case"></a>
## `promotion_case`

Promotion case of a staff member in a promotion exercise (eligibility, examination, board decision, effective date)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-HRM-07 |
| Pages | HRM-05, HRM-02 |
| Events | HR.PROMOTION_DECIDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `employment_record_id` → `employment_record` | `BINARY(16)` | no |  |  |
| `exercise_label` | `VARCHAR(20)` | no |  | e.g. 2026-PROMO |
| `from_grade_level` | `SMALLINT` | no |  |  |
| `from_step` | `SMALLINT` | no |  |  |
| `to_grade_level` | `SMALLINT` | no |  |  |
| `to_step` | `SMALLINT` | no |  |  |
| `eligibility` | `JSON` | no |  | Years on grade, appraisal ratings, examination, discipline status — each with pass/fail |
| `exam_score` | `DECIMAL(6,3)` | yes |  |  |
| `board_decision` | `VARCHAR(32)` | yes |  | values: approved, not_approved, deferred |
| `decided_by` → `app_user` | `BINARY(16)` | yes |  | Human decision (board secretary) |
| `effective_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, staff_id, exercise_label)

- Check `upward`: `to_grade_level > from_grade_level OR (to_grade_level = from_grade_level AND to_step > from_step)`

<a id="registry-separation"></a>
## `separation`

Separation from a post (resignation, retirement, death, dismissal, end of contract, transfer of service) with exit clearance

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-HRM-09 |
| Pages | HRM-07, HRM-02 |
| Events | HR.SEPARATION_RECORDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `staff_post_id` → `staff_post` | `BINARY(16)` | no |  |  |
| `separation_kind` | `VARCHAR(32)` | no |  | values: resignation, retirement_statutory, retirement_voluntary, death, dismissal, termination, end_of_contract, transfer_of_service, abandonment |
| `notice_on` | `DATE` | yes |  |  |
| `effective_on` | `DATE` | no |  |  |
| `exit_checklist` | `JSON` | no |  | Handover of classes (G9), assets, ID card, final pay, pension notification, access removal |
| `pension_notified_on` | `DATE` | yes |  |  |
| `recorded_by` → `app_user` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, staff_id)
- Index: (tenant_id, effective_on)

<a id="registry-staff_bank_account"></a>
## `staff_bank_account`

Staff salary bank account (encrypted; lookup token for duplicate detection; dual approval and call-back on change)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-HRM-11, FR-HRM-12 |
| Pages | HRM-02, HRM-08 |
| Events | HR.BANK_ACCOUNT_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `bank_code` | `VARCHAR(10)` | no |  | CBN bank code |
| `account_number_hmac` | `BINARY(32)` | no | restricted | HMAC-SHA-256 lookup of account_number |
| `account_number_enc` | `VARBINARY(1024)` | no | restricted | Envelope-encrypted account_number. NUBAN — envelope-encrypted |
| `account_number_last4` | `CHAR(4)` | yes | restricted | Last four characters of account_number for masked display |
| `account_name` | `VARCHAR(200)` | no |  |  |
| `is_primary` | `BOOLEAN` | no |  |  |
| `verified_via` | `VARCHAR(32)` | yes |  | values: call_back, nibss_name_enquiry, document, none |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `requested_by` → `app_user` | `BINARY(16)` | no |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, staff_id)
- Index: (tenant_id, account_number_hmac)

- Check `four_eyes`: `approved_by IS NULL OR approved_by <> requested_by`

<a id="registry-hr_integrity_flag"></a>
## `hr_integrity_flag`

Payroll integrity flag across all employers in the state (ghost worker, double employment, pay after exit …)

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-HRM-12, FR-HRM-15 |
| Pages | HRM-08, HRM-10 |
| Events | HR.INTEGRITY_FLAG_RAISED, HR.PAYROLL_HOLD_DECIDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `employer_scope_id` → `scope_node` | `BINARY(16)` | yes |  |  |
| `flag_kind` | `VARCHAR(32)` | no |  | values: shared_bank_account, shared_bvn, concurrent_public_posts, paid_after_separation, past_retirement_date, no_attendance_30_days, failed_headcount, post_without_position, grade_outside_position |
| `evidence` | `JSON` | no |  | Matching records, dates and sources — never special-category data |
| `detected_at` | `DATETIME(6)` | no |  |  |
| `run_label` | `VARCHAR(40)` | yes |  |  |
| `payroll_hold` | `BOOLEAN` | no |  | Set only by a person (A1) |
| `decided_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `decision_reason` | `TEXT` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `open_key` | `VARCHAR(120)` | yes |  | kind:staff while open (one open flag per kind per staff member) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, open_key)
- Index: (tenant_id, employer_scope_id, status)
- Index: (tenant_id, flag_kind)

<a id="registry-headcount_exercise"></a>
## `headcount_exercise`

Staff headcount (verification) exercise at an institution — in person, biometric or video

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-HRM-13 |
| Pages | HRM-08 |
| Events | HR.HEADCOUNT_COMPLETED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `label` | `VARCHAR(40)` | no |  | e.g. 2026-Q4 |
| `method` | `VARCHAR(32)` | no |  | values: in_person, biometric, video |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `conducted_by` → `app_user` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, active, under_review, completed, closed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, label)

<a id="registry-headcount_result"></a>
## `headcount_result`

Outcome for one staff member in a headcount exercise

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-HRM-13, FR-HRM-12 |
| Pages | HRM-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `exercise_id` → `headcount_exercise` | `BINARY(16)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `staff_post_id` → `staff_post` | `BINARY(16)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | no |  | values: verified, absent_with_reason, absent_without_reason, not_on_nominal_roll, impersonation_suspected |
| `verified_at` | `DATETIME(6)` | no |  |  |
| `evidence` | `JSON` | yes |  | Biometric match score, document seen, witness |
| `verifier_id` → `app_user` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, exercise_id, staff_id)

<a id="ops-leave_policy"></a>
## `leave_policy`

Leave entitlement rule by leave type, cadre and grade-level band (versioned)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-HRM-05 |
| Pages | HRM-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `leave_type` | `VARCHAR(32)` | no |  | code list `absence_type` |
| `cadre_code` | `VARCHAR(20)` | yes |  | NULL = every cadre |
| `grade_level_min` | `SMALLINT` | no |  |  |
| `grade_level_max` | `SMALLINT` | no |  |  |
| `days_per_year` | `DECIMAL(6,1)` | no |  |  |
| `day_basis` | `VARCHAR(32)` | no |  | values: working_days, calendar_days |
| `carry_over_max` | `DECIMAL(6,1)` | no |  |  |
| `requires_document` | `BOOLEAN` | no |  |  |
| `is_paid` | `BOOLEAN` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-leave_balance"></a>
## `leave_balance`

Leave balance per staff member, leave type and leave year (the database refuses over-booking)

| | |
|---|---|
| Zone | ops |
| Kind | projection |
| Classification | confidential |
| History | none |
| Scope | none |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-HRM-05, FR-HRM-06, FR-HRM-15 |
| Pages | HRM-04, HRM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `leave_type` | `VARCHAR(32)` | no |  | code list `absence_type` |
| `leave_year` | `SMALLINT` | no |  |  |
| `entitled` | `DECIMAL(6,1)` | no |  |  |
| `carried_over` | `DECIMAL(6,1)` | no |  |  |
| `taken` | `DECIMAL(6,1)` | no |  |  |
| `pending` | `DECIMAL(6,1)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, staff_id, leave_type, leave_year)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)

- Check `within_entitlement`: `taken >= 0 AND pending >= 0 AND taken + pending <= entitled + carried_over`

<a id="ops-leave_request"></a>
## `leave_request`

Leave request with approval; approval creates the staff absence that starts cover (G8)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-HRM-06, FR-HRM-14 |
| Pages | HRM-04 |
| Events | HR.LEAVE_APPROVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `staff_post_id` → `staff_post` | `BINARY(16)` | yes |  |  |
| `leave_type` | `VARCHAR(32)` | no |  | code list `absence_type` |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `days` | `DECIMAL(6,1)` | no |  |  |
| `note` | `VARCHAR(500)` | yes |  | No medical detail — that goes to staff_absence.reason_note (sealed) |
| `requested_by` | `BINARY(16)` | no |  | app_user (registry) |
| `approver_id` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `relief_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `absence_id` → `staff_absence` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, approved, rejected, recorded, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, staff_id, starts_on)
- Index: (tenant_id, status)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `staff_post_id` → `staff_post` — cross-zone (ops → registry)
- Soft reference `relief_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `window`: `ends_on >= starts_on`
- Check `four_eyes`: `approver_id IS NULL OR approver_id <> requested_by`

<a id="ops-employee_relations_case"></a>
## `employee_relations_case`

Employee relations case — query, disciplinary, grievance, appeal or petition with due-process steps and a human outcome  

Allegations about adults that concern children stay in the vault (SAF allegation); this case holds a reference only.

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-STF-FILE` |
| Requirements | FR-HRM-08 |
| Pages | HRM-06, HRM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `case_number` | `VARCHAR(32)` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `case_kind` | `VARCHAR(32)` | no |  | values: query, disciplinary, grievance, appeal, petition |
| `summary` | `TEXT` | no |  | No special-category content |
| `vault_allegation_ref` | `BINARY(16)` | yes |  | Allegation in the vault (reference only) |
| `raised_by` | `BINARY(16)` | no |  |  |
| `raised_on` | `DATE` | no |  |  |
| `response_due_on` | `DATE` | yes |  |  |
| `steps` | `JSON` | no |  | Due-process timeline: query issued, response, panel, hearing, decision, appeal window |
| `outcome` | `VARCHAR(32)` | yes |  | values: no_case, advice, warning, severe_warning, suspension, interdiction, demotion, dismissal, retirement_in_public_interest, upheld, not_upheld |
| `outcome_decided_by` | `BINARY(16)` | yes |  | Human decision (A1) |
| `outcome_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, case_number)
- Index: (tenant_id, staff_id, status)

- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-pay_element"></a>
## `pay_element`

Payroll element — earning, allowance, statutory or voluntary deduction, loan repayment or employer contribution (versioned)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-HRM-10 |
| Pages | HRM-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(20)` | no |  | BASIC, HOUSING, TRANSPORT, RURAL, PAYE, PENSION_EE, PENSION_ER, NHF, UNION, COOP, LOAN … |
| `title` | `VARCHAR(300)` | no |  |  |
| `element_kind` | `VARCHAR(32)` | no |  | values: earning, allowance, statutory_deduction, voluntary_deduction, loan_repayment, employer_contribution |
| `calc_method` | `VARCHAR(32)` | no |  | values: fixed, pct_of_basic, pct_of_gross, pct_of_pensionable, table |
| `rate` | `DECIMAL(9,4)` | yes |  | Percentage or fixed rate per method |
| `table_kind` | `VARCHAR(32)` | yes |  | Statutory table used (PAYE, pension, NHF) · values: paye, pension, nhf, nhis, other |
| `is_taxable` | `BOOLEAN` | no |  |  |
| `is_pensionable` | `BOOLEAN` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-staff_pay_element"></a>
## `staff_pay_element`

Recurring pay element of a staff post (allowance, voluntary deduction, loan with balance), effective-dated

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | restricted |
| History | effective |
| Scope | none |
| Module | `hr` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-HRM-10 |
| Pages | HRM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_post_id` → `staff_post` | `BINARY(16)` | no |  |  |
| `element_code` | `VARCHAR(20)` | no |  |  |
| `amount_minor` | `BIGINT` | yes |  | Monthly amount for fixed elements (minor units) |
| `rate` | `DECIMAL(9,4)` | yes |  |  |
| `currency` | `CHAR(3)` | no |  |  |
| `loan_balance_minor` | `BIGINT` | yes |  | (minor units) |
| `reference` | `VARCHAR(64)` | yes |  |  |
| `approved_by` | `BINARY(16)` | no |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, staff_post_id)

- Soft reference `staff_post_id` → `staff_post` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

