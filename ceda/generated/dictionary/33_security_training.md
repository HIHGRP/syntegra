# STI — Education and training institutions of the security agencies — agency structures, ranks, courses, intakes

The Armed Forces (Defence Headquarters, Army, Navy, Air Force), the Nigeria Police Force and the paramilitary, law-enforcement, emergency and security services each run their own academies, staff and war colleges, depots and training schools (change request CR-004). Every agency is modelled individually: its organisational structure (headquarters, services, directorates, commands, training commands, formations, zones, state commands) is a tree of scope nodes and is the access hierarchy; its ranks are held in seniority order; each of its institutions has its own course catalogue (curriculum) of versioned courses broken into modules, run as intakes, with every trainee's outcome on the lifelong learner record. All of this lives in a national sector registry (tenant kind sector_registry, code ng-fse) isolated from the 37 state registries. CEDA holds education and training administration only — never operational, deployment, intelligence, weapons or tactical content.

Module (system of record): `security_training` · default zone: **registry** · default retention: `RS-LRN-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`security_agency`](#registry-security_agency) | registry | master | internal | lifecycle | Security agency (armed service, police, paramilitary, law-enforcement, emergency or security service) |
| [`agency_unit`](#registry-agency_unit) | registry | master | internal | lifecycle | Unit of an agency's own structure (headquarters, service, directorate, command, formation, state command) |
| [`agency_rank`](#registry-agency_rank) | registry | reference | public | versioned | Rank of an agency in seniority order (officer, warrant, non-commissioned, senior and junior staff, cadet, recruit) |
| [`security_institution`](#registry-security_institution) | registry | master | internal | lifecycle | Security-agency profile of an education or training institution (agency, owning command, type, access regime) |
| [`security_course`](#registry-security_course) | registry | master | internal | lifecycle | Course in an institution's catalogue — its curriculum (versioned; award, duration, entry, target ranks) |
| [`security_course_module`](#registry-security_course_module) | registry | config | internal | versioned | Module (syllabus heading) of a training course — area, contact hours, assessment |
| [`security_course_intake`](#registry-security_course_intake) | registry | transaction | internal | lifecycle | Intake (run) of a course, e.g. 77 Regular Course, with dates and capacity |
| [`trainee_record`](#registry-trainee_record) | registry | transaction | restricted | lifecycle | A trainee on an intake — rank at entry and outcome, on the lifelong learner record |

<a id="registry-security_agency"></a>
## `security_agency`

Security agency (armed service, police, paramilitary, law-enforcement, emergency or security service)  

scope_node_id is the agency's own node (level agency) under the sector registry's root.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-STI-01 |
| Pages | STI-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(16)` | no |  | e.g. NA, NN, NAF, DHQ, NPF, NSCDC, NCoS, NIS, NCS, FFS, FRSC, NDLEA, DSS, EFCC |
| `name` | `VARCHAR(300)` | no |  |  |
| `category` | `VARCHAR(32)` | no |  | values: armed_forces, police, paramilitary, law_enforcement, intelligence_security, emergency_service |
| `supervising_ministry` | `VARCHAR(200)` | yes |  | Ministry or office the agency reports to |
| `establishing_law` | `VARCHAR(300)` | yes |  | Act establishing the agency |
| `website` | `VARCHAR(2048)` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | verified by the agency, illustrative, or to be confirmed · values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code)

<a id="registry-agency_unit"></a>
## `agency_unit`

Unit of an agency's own structure (headquarters, service, directorate, command, formation, state command)  

scope_node_id is the unit's own node, a child of its parent unit's node (or of the agency's node).

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-STI-02, FR-STI-08 |
| Pages | STI-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `agency_id` → `security_agency` | `BINARY(16)` | no |  |  |
| `parent_unit_id` → `agency_unit` | `BINARY(16)` | yes |  |  |
| `unit_type` | `VARCHAR(32)` | no |  | values: headquarters, service, directorate, department, command, training_command, formation, zone, state_command, area_command, sector_command |
| `code` | `VARCHAR(40)` | no |  | Unique within the agency, e.g. TRADOC, NAVTRAC, ATC, LA-CMD |
| `name` | `VARCHAR(300)` | no |  |  |
| `headquarters_state` | `VARCHAR(6)` | yes |  | ISO 3166-2 state of the unit's headquarters |
| `headquarters_town` | `VARCHAR(120)` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, agency_id, code)
- Index: (tenant_id, parent_unit_id)

<a id="registry-agency_rank"></a>
## `agency_rank`

Rank of an agency in seniority order (officer, warrant, non-commissioned, senior and junior staff, cadet, recruit)

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | public |
| History | versioned |
| Scope | none |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-STI-03 |
| Pages | STI-01, STI-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `agency_id` → `security_agency` | `BINARY(16)` | no |  |  |
| `code` | `VARCHAR(24)` | no |  | e.g. LT, CAPT, ASP, CPL |
| `title` | `VARCHAR(80)` | no |  |  |
| `abbreviation` | `VARCHAR(16)` | yes |  |  |
| `rank_category` | `VARCHAR(32)` | no |  | values: commissioned_officer, warrant_officer, non_commissioned, other_rank, senior_staff, junior_staff, cadet, recruit |
| `seniority` | `SMALLINT` | no |  | 1 = most junior |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, agency_id, code)

<a id="registry-security_institution"></a>
## `security_institution`

Security-agency profile of an education or training institution (agency, owning command, type, access regime)  

One profile per institution; the institution master (domain INS) keeps name, location, levels and status. scope_node_id is the institution's node, which is a child of its owning unit's node.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-STI-04, FR-STI-08 |
| Pages | STI-01, STI-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `agency_id` → `security_agency` | `BINARY(16)` | no |  |  |
| `unit_id` → `agency_unit` | `BINARY(16)` | no |  | Owning command, training command or directorate |
| `institution_type` | `VARCHAR(32)` | no |  | values: military_academy, police_academy, service_academy, defence_university, staff_college, war_college, defence_college, depot, training_school, specialist_school, training_college, technical_institute, health_sciences_school, strategic_institute |
| `access_regime` | `VARCHAR(32)` | no |  | content_not_held: CEDA holds administration only · values: standard, restricted, content_not_held |
| `accreditation` | `JSON` | yes |  | Academic regulators and affiliations, e.g. NUC, NBTE, affiliated university |
| `commandant_title` | `VARCHAR(80)` | yes |  | Commandant, Rector, Vice-Chancellor, Director, Principal |
| `established_year` | `SMALLINT` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id)
- Index: (tenant_id, agency_id)
- Index: (tenant_id, unit_id)

<a id="registry-security_course"></a>
## `security_course`

Course in an institution's catalogue — its curriculum (versioned; award, duration, entry, target ranks)  

scope_node_id is the institution's node. Degree-bearing courses also point to their academic programme.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-STI-05 |
| Pages | STI-02, STI-03 |
| Events | STI.COURSE_PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `agency_id` → `security_agency` | `BINARY(16)` | no |  |  |
| `code` | `VARCHAR(32)` | no |  | Unique within the institution |
| `title` | `VARCHAR(300)` | no |  |  |
| `category` | `VARCHAR(32)` | no |  | values: initial_officer, cadet_degree, recruit_basic, junior_leadership, promotion_career, specialist, command_and_staff, strategic_leadership, academic_programme, continuing_professional |
| `award` | `VARCHAR(32)` | no |  | values: degree, postgraduate, diploma, nce, certificate, staff_qualification, attendance |
| `award_title` | `VARCHAR(120)` | yes |  | e.g. B.Sc., psc, fdc, Certificate of Basic Training |
| `programme_id` → `programme` | `BINARY(16)` | yes |  | Academic programme for degree, diploma and NCE courses |
| `curriculum_id` → `curriculum` | `BINARY(16)` | yes |  | Curriculum 360 of the academic component, when held |
| `accrediting_body` | `VARCHAR(32)` | yes |  | code list `regulator` |
| `duration_weeks` | `SMALLINT` | yes |  |  |
| `entry_requirements` | `JSON` | yes |  | Entry qualifications, age limits, medical and other conditions (as published) |
| `target_ranks` | `JSON` | yes |  | Rank codes the course is for (e.g. officer cadets, CAPT–MAJ) |
| `description` | `TEXT` | yes |  |  |
| `version` | `VARCHAR(32)` | no |  |  |
| `content_held` | `BOOLEAN` | no |  | false: the agency does not release module detail (access regime) |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, code, version)
- Index: (tenant_id, agency_id, category)

<a id="registry-security_course_module"></a>
## `security_course_module`

Module (syllabus heading) of a training course — area, contact hours, assessment

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | none |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-CUR-PERM` |
| Requirements | FR-STI-06 |
| Pages | STI-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `course_id` → `security_course` | `BINARY(16)` | no |  |  |
| `sequence` | `SMALLINT` | no |  |  |
| `code` | `VARCHAR(32)` | no |  |  |
| `title` | `VARCHAR(200)` | no |  | Syllabus heading only — never operational or tactical content |
| `area` | `VARCHAR(32)` | no |  | values: academic, professional_core, leadership_ethics, law_human_rights, physical_fitness, field_practical, ict_cyber, health_first_aid, management_administration, community_relations, research |
| `contact_hours` | `SMALLINT` | yes |  |  |
| `assessment` | `VARCHAR(32)` | no |  | values: written, practical, continuous, project, oral, mixed, none |
| `is_mandatory` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, course_id, code)

<a id="registry-security_course_intake"></a>
## `security_course_intake`

Intake (run) of a course, e.g. 77 Regular Course, with dates and capacity  

scope_node_id is the institution's node.

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-STI-07 |
| Pages | STI-03, STI-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `course_id` → `security_course` | `BINARY(16)` | no |  |  |
| `intake_code` | `VARCHAR(40)` | no |  | e.g. RC77, SC-2026-1 |
| `name` | `VARCHAR(300)` | no |  |  |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | yes |  |  |
| `capacity` | `INT UNSIGNED` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: planned, in_progress, completed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, course_id, intake_code)

<a id="registry-trainee_record"></a>
## `trainee_record`

A trainee on an intake — rank at entry and outcome, on the lifelong learner record  

scope_node_id is the institution's node. Service numbers are external identifiers (scheme SVC-NO).

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `security_training` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-STI-07 |
| Pages | STI-04, LRN-04 |
| Events | STI.TRAINEE_OUTCOME_RECORDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `intake_id` → `security_course_intake` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | yes |  |  |
| `rank_at_entry_id` → `agency_rank` | `BINARY(16)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | no |  | values: in_training, passed, passed_out, commissioned, failed, relegated, withdrawn, discharged |
| `result` | `VARCHAR(120)` | yes |  | Grade, class of degree or order of merit, as awarded |
| `outcome_on` | `DATE` | yes |  |  |
| `outcome_reason` | `TEXT` | yes |  |  |
| `recorded_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, intake_id)
- Index: (tenant_id, intake_id, outcome)

