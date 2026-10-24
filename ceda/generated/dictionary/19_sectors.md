# SEC — Sector extensions — early years, post-16 and careers, TVET, higher education and medical/health education

Sector-specific records on the same Learner 360, enrolment and programme masters: early-years observations, milestones, daycare sessions, authorised collectors and care logs (FR-EYR-01–03, 101); option choices, career guidance, higher-education applications, student finance and destinations (FR-P16-01–03, 101–103); competencies, workplace assessment, apprenticeships, SIWES industrial training and Employer Partner 360 (FR-TVT-01–06, 101); accommodation, research candidature and ethics, graduation and alumni (FR-HED-01–07, 101); clinical rotations, anonymised logbooks, clinical hours, skills labs and regulator readiness (FR-MED-01–05, 101–103). Patient data is never stored (FR-MED-03, FR-MED-05).

Module (system of record): `sectors` · default zone: **ops** · default retention: `RS-LRN-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`development_milestone`](#registry-development_milestone) | registry | reference | public | versioned | Early-years development area and milestone framework |
| [`eyr_observation`](#ops-eyr_observation) | ops | event | confidential | lifecycle | Early-years observation (text, photo, video) against development areas and milestones, shared with parents |
| [`eyr_session_booking`](#ops-eyr_session_booking) | ops | transaction | confidential | lifecycle | Daycare-linked early-years session booking (staff-to-child ratio monitoring) |
| [`authorised_collector`](#ops-authorised_collector) | ops | master | confidential | effective | Person authorised to collect an early-years child (photo check at pick-up) |
| [`collection_record`](#ops-collection_record) | ops | event | confidential | append | Pick-up record with photo check against authorised collectors |
| [`care_log`](#vault-care_log) | vault | event | special | append | Early-years daily care log (meals, sleep, nappies, medication given) shared with parents |
| [`option_choice`](#ops-option_choice) | ops | transaction | confidential | lifecycle | Subject option or stream choice (combination rules, capacity, guidance against entry requirements) |
| [`guidance_session`](#ops-guidance_session) | ops | event | confidential | lifecycle | Career guidance session (counsellor, interests, aptitude, recommended stream, agreed next steps) |
| [`he_application`](#ops-he_application) | ops | transaction | confidential | lifecycle | Higher-education application tracked through an adapter (JAMB UTME/CAPS, UCAS-equivalent) — choices, references, offers |
| [`student_finance_application`](#ops-student_finance_application) | ops | transaction | restricted | lifecycle | Student-finance guidance and loan or grant application (e.g. NELFUND) — no lender credentials stored |
| [`destination_record`](#ops-destination_record) | ops | event | confidential | lifecycle | Post-education destination (further education, employment, apprenticeship, entrepreneurship, professional qualification) |
| [`competency_framework`](#registry-competency_framework) | registry | reference | public | versioned | Competency framework (NSQ, NABTEB trade syllabus, industry certification, clinical competencies, digital skills) |
| [`competency_record`](#ops-competency_record) | ops | transaction | confidential | lifecycle | Competency evidence and assessor sign-off (including approved workplace assessors and clinical supervisors) |
| [`employer_partner`](#registry-employer_partner) | registry | master | internal | lifecycle | Employer Partner 360 (placements, sponsorships, assessors, agreements, hiring outcomes) |
| [`placement`](#ops-placement) | ops | transaction | confidential | lifecycle | Industry placement, apprenticeship or clinical rotation (matching, agreement, attendance, workplace assessment) |
| [`industrial_training`](#ops-industrial_training) | ops | transaction | confidential | lifecycle | Industrial training / SIWES placement (letters, employer acceptance, logbook, visits, ITF forms, grading) |
| [`clinical_site`](#registry-clinical_site) | registry | master | internal | lifecycle | Hospital or clinical department hosting rotations (capacity, supervisors) |
| [`logbook_entry`](#ops-logbook_entry) | ops | transaction | confidential | lifecycle | Anonymised clinical logbook entry (procedure/case, level of involvement, reflection) with supervisor verification |
| [`professional_body`](#registry-professional_body) | registry | reference | public | lifecycle | Health-profession regulator and its registration rules for a programme family (MDCN, NMCN, PCN, MRTB, RRBN, MLSCN, CHPRBN) |
| [`registration_readiness`](#ops-registration_readiness) | ops | projection | confidential | snapshot | Readiness of a learner for professional registration or licensing examination (clinical hours, competencies) |
| [`skills_lab_session`](#ops-skills_lab_session) | ops | transaction | internal | lifecycle | Skills laboratory or simulation session (equipment, facilitators, competency outcomes) |
| [`international_student_record`](#ops-international_student_record) | ops | master | restricted | lifecycle | Institutional information for an international student (visa-related records) — restricted |
| [`accommodation_allocation`](#ops-accommodation_allocation) | ops | transaction | confidential | lifecycle | Hostel accommodation application and allocation (accessibility needs considered) |
| [`research_candidature`](#ops-research_candidature) | ops | transaction | confidential | lifecycle | Research student candidature (supervision, milestones, progression reviews, thesis examination) |
| [`ethics_application`](#ops-ethics_application) | ops | transaction | confidential | lifecycle | Research ethics application and decision |
| [`graduation_list`](#ops-graduation_list) | ops | transaction | confidential | lifecycle | Graduation list from classification and certificate eligibility; ceremony |
| [`alumnus`](#ops-alumnus) | ops | master | confidential | lifecycle | Alumni record (consented contact after graduation) |
| [`admission_enquiry`](#ops-admission_enquiry) | ops | transaction | confidential | lifecycle | Admissions enquiry, open-day or visit booking, waiting list position (website widget posts here) |
| [`admission_application`](#ops-admission_application) | ops | transaction | confidential | lifecycle | Admission application for a school place or tertiary programme (entry checks, O'Level verification, decisions, offers) |

<a id="registry-development_milestone"></a>
## `development_milestone`

Early-years development area and milestone framework

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-EYR-01 |
| Pages | EYR-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `area_code` | `VARCHAR(32)` | no |  |  |
| `milestone_code` | `VARCHAR(32)` | no |  |  |
| `statement` | `TEXT` | no |  |  |
| `age_band_months` | `VARCHAR(16)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, milestone_code, version)

<a id="ops-eyr_observation"></a>
## `eyr_observation`

Early-years observation (text, photo, video) against development areas and milestones, shared with parents

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's class |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-EYR-01, FR-EYR-02, FR-EYR-03 |
| Pages | EYR-01, EYR-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `observed_by_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `observed_at` | `DATETIME(6)` | no |  |  |
| `milestone_codes` | `JSON` | yes |  |  |
| `note` | `TEXT` | yes |  |  |
| `media_document_ids` | `JSON` | yes |  | Shared only when every pictured child has photo consent |
| `pictured_learner_ids` | `JSON` | yes |  |  |
| `shared_with_parents_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `observed_by_staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-eyr_session_booking"></a>
## `eyr_session_booking`

Daycare-linked early-years session booking (staff-to-child ratio monitoring)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-EYR-101 |
| Pages | EYR-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `session_date` | `DATE` | no |  |  |
| `session_code` | `VARCHAR(16)` | no |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, confirmed, declined, cancelled, completed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, session_date, session_code)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-authorised_collector"></a>
## `authorised_collector`

Person authorised to collect an early-years child (photo check at pick-up)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | effective |
| Scope | derived: the learner |
| Module | `sectors` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-EYR-101, FR-FAM-04 |
| Pages | EYR-01, FAM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `guardian_id` → `guardian` | `BINARY(16)` | yes |  | When the collector is a guardian |
| `name` | `VARCHAR(200)` | no |  |  |
| `phone` | `VARCHAR(16)` | yes |  |  |
| `photo_document_id` | `BINARY(16)` | yes | restricted |  |
| `password_phrase_enc` | `VARBINARY(1024)` | yes | restricted | Envelope-encrypted password_phrase. Collection password |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `guardian_id` → `guardian` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-collection_record"></a>
## `collection_record`

Pick-up record with photo check against authorised collectors

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | derived: the learner |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-EYR-101 |
| Pages | EYR-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `collector_id` → `authorised_collector` | `BINARY(16)` | yes |  |  |
| `is_verified` | `BOOLEAN` | no |  |  |
| `staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `collected_at` | `DATETIME(6)` | no |  |  |
| `exception_note` | `VARCHAR(500)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `staff_id` → `staff` — cross-zone (ops → registry)

<a id="vault-care_log"></a>
## `care_log`

Early-years daily care log (meals, sleep, nappies, medication given) shared with parents

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-HEALTH` |
| Requirements | FR-EYR-03, FR-EYR-101 |
| Pages | EYR-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `log_kind` | `VARCHAR(32)` | no |  | values: meal, sleep, nappy, medication_given, incident, note |
| `detail` | `MEDIUMBLOB` | no | special |  |
| `recorded_by` | `BINARY(16)` | no |  |  |
| `recorded_at` | `DATETIME(6)` | no |  |  |
| `shared_with_parents_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-option_choice"></a>
## `option_choice`

Subject option or stream choice (combination rules, capacity, guidance against entry requirements)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-P16-01, FR-P16-103 |
| Pages | P16-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `stream` | `VARCHAR(32)` | yes |  | code list `stream` |
| `choices` | `JSON` | no |  | Ranked subject choices |
| `rule_check` | `JSON` | yes |  | Combination-rule result |
| `counsellor_override_by` | `BINARY(16)` | yes |  | Override of a guidance rule (recorded) |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, period_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)

<a id="ops-guidance_session"></a>
## `guidance_session`

Career guidance session (counsellor, interests, aptitude, recommended stream, agreed next steps)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-P16-103, FR-P16-102 |
| Pages | P16-01, P16-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `counsellor_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `held_on` | `DATE` | no |  |  |
| `topic` | `VARCHAR(32)` | no |  | code list `guidance_topic` |
| `interests` | `JSON` | yes |  |  |
| `aptitude` | `JSON` | yes |  |  |
| `recommended_stream` | `VARCHAR(32)` | yes |  | code list `stream` |
| `next_steps` | `TEXT` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `counsellor_staff_id` → `staff` — cross-zone (ops → registry)

<a id="ops-he_application"></a>
## `he_application`

Higher-education application tracked through an adapter (JAMB UTME/CAPS, UCAS-equivalent) — choices, references, offers

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-P16-101, FR-P16-02 |
| Pages | P16-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `scheme` | `VARCHAR(32)` | no |  | code list `admission_scheme` |
| `choices` | `JSON` | no |  |  |
| `personal_statement_document_id` | `BINARY(16)` | yes |  |  |
| `reference_document_ids` | `JSON` | yes |  |  |
| `offer` | `JSON` | yes |  |  |
| `accepted_choice` | `VARCHAR(200)` | yes |  |  |
| `external_ref` | `VARCHAR(64)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, fee_pending, desk_review, query_raised, inspection, decision, approved, refused, deferred, withdrawn, appealed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-student_finance_application"></a>
## `student_finance_application`

Student-finance guidance and loan or grant application (e.g. NELFUND) — no lender credentials stored

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-P16-102 |
| Pages | P16-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `scheme` | `VARCHAR(32)` | no |  | code list `finance_scheme` |
| `amount_requested_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, fee_pending, desk_review, query_raised, inspection, decision, approved, refused, deferred, withdrawn, appealed |
| `external_ref` | `VARCHAR(64)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-destination_record"></a>
## `destination_record`

Post-education destination (further education, employment, apprenticeship, entrepreneurship, professional qualification)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's last institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-P16-03, FR-TVT-06 |
| Pages | P16-02, LRN-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | yes |  |  |
| `destination` | `VARCHAR(32)` | no |  | code list `destination_kind` |
| `detail` | `JSON` | yes |  |  |
| `recorded_on` | `DATE` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | values: learner, institution, survey, exchange |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)

<a id="registry-competency_framework"></a>
## `competency_framework`

Competency framework (NSQ, NABTEB trade syllabus, industry certification, clinical competencies, digital skills)

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-TVT-01, FR-LMS-122, FR-MED-02 |
| Pages | TVT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `framework_kind` | `VARCHAR(32)` | no |  | values: nsq, trade_syllabus, industry_certification, clinical, digital_skills, other |
| `units` | `JSON` | no |  | Units and elements with performance criteria |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

<a id="ops-competency_record"></a>
## `competency_record`

Competency evidence and assessor sign-off (including approved workplace assessors and clinical supervisors)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-TVT-01, FR-TVT-05, FR-MED-02, FR-MED-101 |
| Pages | TVT-01, MED-02, TVT-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `framework_id` → `competency_framework` | `BINARY(16)` | no |  |  |
| `unit_code` | `VARCHAR(40)` | no |  |  |
| `evidence_document_ids` | `JSON` | yes |  |  |
| `assessor_kind` | `VARCHAR(32)` | no |  | values: staff, workplace_assessor, clinical_supervisor |
| `assessor_ref` | `BINARY(16)` | no |  | Staff or employer contact |
| `level_achieved` | `VARCHAR(16)` | yes |  |  |
| `signed_off_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: in_progress, evidence_submitted, signed_off, not_yet_competent |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `framework_id` → `competency_framework` — cross-zone (ops → registry)

<a id="registry-employer_partner"></a>
## `employer_partner`

Employer Partner 360 (placements, sponsorships, assessors, agreements, hiring outcomes)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-TVT-04, FR-TVT-03 |
| Pages | TVT-04, TVT-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `cac_number` | `VARCHAR(20)` | yes |  |  |
| `sector` | `VARCHAR(32)` | yes |  | code list `industry_sector` |
| `address` | `JSON` | yes |  |  |
| `contacts` | `JSON` | yes |  |  |
| `agreements` | `JSON` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-placement"></a>
## `placement`

Industry placement, apprenticeship or clinical rotation (matching, agreement, attendance, workplace assessment)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-TVT-03, FR-MED-01, FR-MED-05 |
| Pages | TVT-03, MED-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `placement_kind` | `VARCHAR(32)` | no |  | values: apprenticeship, industry_placement, siwes, clinical_rotation, teaching_practice |
| `employer_partner_id` → `employer_partner` | `BINARY(16)` | yes |  |  |
| `clinical_site_id` → `clinical_site` | `BINARY(16)` | yes |  |  |
| `supervisor_name` | `VARCHAR(200)` | yes |  |  |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `prerequisites_met` | `JSON` | yes |  | Competencies, immunisation/occupational-health clearance |
| `agreement_document_id` | `BINARY(16)` | yes |  |  |
| `funding` | `JSON` | yes |  | Employer funding |
| `attendance_confirmed_days` | `SMALLINT` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: proposed, agreed, active, completed, terminated |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `employer_partner_id` → `employer_partner` — declared soft
- Soft reference `clinical_site_id` → `clinical_site` — declared soft

<a id="ops-industrial_training"></a>
## `industrial_training`

Industrial training / SIWES placement (letters, employer acceptance, logbook, visits, ITF forms, grading)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-TVT-101 |
| Pages | TVT-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `placement_id` → `placement` | `BINARY(16)` | no |  |  |
| `itf_reference` | `VARCHAR(40)` | yes |  |  |
| `logbook_document_id` | `BINARY(16)` | yes |  |  |
| `supervisor_visits` | `JSON` | yes |  |  |
| `grade` | `VARCHAR(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: proposed, agreed, active, completed, terminated |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-clinical_site"></a>
## `clinical_site`

Hospital or clinical department hosting rotations (capacity, supervisors)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-MED-01 |
| Pages | MED-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `department` | `VARCHAR(120)` | yes |  |  |
| `capacity` | `SMALLINT` | yes |  |  |
| `fhir_endpoint` | `VARCHAR(2048)` | yes |  | Placement attendance confirmation only (Practitioner/Encounter references) |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-logbook_entry"></a>
## `logbook_entry`

Anonymised clinical logbook entry (procedure/case, level of involvement, reflection) with supervisor verification  

Save is blocked when text matches patient-identifier patterns (name lists, hospital-number formats).

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-MED-02, FR-MED-03 |
| Pages | MED-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `placement_id` → `placement` | `BINARY(16)` | yes |  |  |
| `procedure_code` | `VARCHAR(40)` | no |  |  |
| `involvement` | `VARCHAR(32)` | no |  | values: observed, assisted, performed_supervised, performed_independent |
| `reflection` | `TEXT` | yes |  |  |
| `occurred_on` | `DATE` | no |  |  |
| `supervisor_verified_by` | `VARCHAR(200)` | yes |  |  |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `clinical_minutes` | `INT` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="registry-professional_body"></a>
## `professional_body`

Health-profession regulator and its registration rules for a programme family (MDCN, NMCN, PCN, MRTB, RRBN, MLSCN, CHPRBN)

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | appj |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-MED-103, FR-MED-04 |
| Pages | MED-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(16)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `cadre` | `VARCHAR(32)` | no |  | code list `programme_family` |
| `indexing_rules` | `JSON` | yes |  |  |
| `registration_rules` | `JSON` | yes |  |  |
| `required_clinical_hours` | `SMALLINT` | yes |  |  |
| `export_format` | `VARCHAR(80)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

<a id="ops-registration_readiness"></a>
## `registration_readiness`

Readiness of a learner for professional registration or licensing examination (clinical hours, competencies)

| | |
|---|---|
| Zone | ops |
| Kind | projection |
| Classification | confidential |
| History | snapshot |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-MED-04, FR-MED-102, FR-MED-103 |
| Pages | MED-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `professional_body_id` → `professional_body` | `BINARY(16)` | yes |  |  |
| `clinical_hours` | `DECIMAL(7,1)` | no |  |  |
| `competencies_signed` | `SMALLINT` | no |  |  |
| `is_ready` | `BOOLEAN` | no |  |  |
| `as_of` | `DATE` | no |  |  |
| `exported_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `professional_body_id` → `professional_body` — declared soft

<a id="ops-skills_lab_session"></a>
## `skills_lab_session`

Skills laboratory or simulation session (equipment, facilitators, competency outcomes)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-MED-101 |
| Pages | MED-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `room_booking_id` → `room_booking` | `BINARY(16)` | no |  |  |
| `scenario` | `VARCHAR(300)` | no |  |  |
| `facilitator_staff_ids` | `JSON` | no |  |  |
| `equipment_asset_ids` | `JSON` | yes |  |  |
| `participant_learner_ids` | `JSON` | no |  |  |
| `outcomes` | `JSON` | yes |  | Competency outcomes recorded |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-international_student_record"></a>
## `international_student_record`

Institutional information for an international student (visa-related records) — restricted

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | restricted |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-HED-07 |
| Pages | HED-01, LRN-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `nationality` | `CHAR(2)` | no |  |  |
| `visa_reference_enc` | `VARBINARY(1024)` | yes | restricted | Envelope-encrypted visa_reference. |
| `visa_reference_last4` | `CHAR(4)` | yes | restricted | Last four characters of visa_reference for masked display |
| `visa_expires_on` | `DATE` | yes |  |  |
| `sponsor_institution_ref` | `VARCHAR(120)` | yes |  |  |
| `document_ids` | `JSON` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-accommodation_allocation"></a>
## `accommodation_allocation`

Hostel accommodation application and allocation (accessibility needs considered)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-HED-03 |
| Pages | HED-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `bed_label` | `VARCHAR(16)` | yes |  |  |
| `has_accessibility_need` | `BOOLEAN` | no |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, proposed, approved, published, applied, allocated, waitlisted, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, period_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-research_candidature"></a>
## `research_candidature`

Research student candidature (supervision, milestones, progression reviews, thesis examination)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's department |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-HED-04 |
| Pages | HED-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `supervisor_staff_ids` | `JSON` | no |  |  |
| `thesis_title` | `VARCHAR(300)` | yes |  |  |
| `milestones` | `JSON` | yes |  |  |
| `examination` | `JSON` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, suspended, under_examination, awarded, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `enrolment_id` → `enrolment` — cross-zone (ops → registry)

<a id="ops-ethics_application"></a>
## `ethics_application`

Research ethics application and decision

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the candidature |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-HED-04 |
| Pages | HED-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `candidature_id` → `research_candidature` | `BINARY(16)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `document_id` | `BINARY(16)` | no |  |  |
| `decision` | `VARCHAR(32)` | yes |  | values: approve, approve_with_conditions, defer, refuse |
| `decided_on` | `DATE` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-graduation_list"></a>
## `graduation_list`

Graduation list from classification and certificate eligibility; ceremony

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-HED-05 |
| Pages | HED-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `ceremony_on` | `DATE` | yes |  |  |
| `learner_ids` | `JSON` | no |  |  |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-alumnus"></a>
## `alumnus`

Alumni record (consented contact after graduation)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-HED-05 |
| Pages | HED-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `graduated_on` | `DATE` | no |  |  |
| `contact_consent` | `BOOLEAN` | no |  |  |
| `contact_email` | `VARCHAR(254)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-admission_enquiry"></a>
## `admission_enquiry`

Admissions enquiry, open-day or visit booking, waiting list position (website widget posts here)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-RECRUIT` |
| Requirements | FR-FAM-102, FR-FAM-103 |
| Pages | HED-01, PUB-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `contact_name` | `VARCHAR(200)` | no |  |  |
| `contact_phone` | `VARCHAR(16)` | yes |  |  |
| `contact_email` | `VARCHAR(254)` | yes |  |  |
| `child_name` | `VARCHAR(200)` | yes |  |  |
| `intended_level` | `VARCHAR(32)` | yes |  | code list `education_level` |
| `source` | `VARCHAR(32)` | no |  | values: website_widget, walk_in, phone, whatsapp, open_day, referral |
| `visit_at` | `DATETIME(6)` | yes |  |  |
| `waiting_list_position` | `INT UNSIGNED` | yes |  |  |
| `application_id` → `admission_application` | `BINARY(16)` | yes |  | Conversion to an application |
| `status` | `VARCHAR(32)` | no |  | values: new, contacted, visit_booked, applied, waitlisted, enrolled, lost |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-admission_application"></a>
## `admission_application`

Admission application for a school place or tertiary programme (entry checks, O'Level verification, decisions, offers)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `sectors` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-HED-01, FR-FAM-102, FR-FAM-103 |
| Pages | HED-01, HED-02, PUB-03 |
| Events | ADM.APPLICATION_RECEIVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `programme_id` → `programme` | `BINARY(16)` | yes |  |  |
| `education_level` | `VARCHAR(32)` | yes |  | code list `education_level` |
| `learner_id` → `learner` | `BINARY(16)` | yes |  | Matched or created at offer acceptance |
| `applicant_name` | `VARCHAR(200)` | no |  |  |
| `applicant_dob` | `DATE` | yes |  |  |
| `applicant_email` | `VARCHAR(254)` | yes |  |  |
| `applicant_phone` | `VARCHAR(16)` | yes |  |  |
| `channel` | `VARCHAR(32)` | no |  | values: online, office, agent, exam_body_adapter, import |
| `answers` | `JSON` | no |  |  |
| `olevel_verification` | `JSON` | yes |  | Via Certificate 360 or exam-body adapters |
| `decision` | `VARCHAR(32)` | yes |  | values: offer, conditional_offer, waitlist, refuse |
| `decided_by` | `BINARY(16)` | yes |  | Admission refusal is human-only |
| `offer_expires_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, reviewing, assessment, decided, offer_accepted, enrolled, declined, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `programme_id` → `programme` — cross-zone (ops → registry)
- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

