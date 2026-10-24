# INS — Institution 360, state institution register, licensing, inspection and compliance

The state institution register: every ECCDE centre, school, technical college, college of education, polytechnic, university and non-formal centre, public and private, held once as Institution 360 (MFS §7.1, FR-INS-01–12). Master fields change only through the registering authority's change request. Licences, accreditations and authorisations gate certificate issuance and exam entries. Inspections, findings, corrective actions, compliance requirements, onboarding readiness and the improvement loop live here so the state, LGA and inspectorate see one picture.

Module (system of record): `institutions` · default zone: **registry** · default retention: `RS-INS-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`institution`](#registry-institution) | registry | master | internal | lifecycle | Institution 360 master (public and private, every level) |
| [`institution_change_request`](#registry-institution_change_request) | registry | transaction | internal | lifecycle | Change request to an institution's master fields (name, registration number, ownership, category, address, coordinates) |
| [`campus`](#registry-campus) | registry | master | internal | lifecycle | Campus / site / branch of an institution |
| [`org_unit`](#registry-org_unit) | registry | master | internal | effective | Faculty / school / department / unit (effective-dated tree, cost centres and heads) |
| [`licence`](#registry-licence) | registry | master | internal | lifecycle | Licence, accreditation or authorisation (operating licence, exam centre, certificate issuer, programme accreditation) |
| [`inspection`](#registry-inspection) | registry | transaction | confidential | lifecycle | Inspection 360 — approval, routine, monitoring or follow-up inspection |
| [`inspection_programme`](#registry-inspection_programme) | registry | config | internal | lifecycle | Risk-based inspection programme for a period, for inspectorate approval |
| [`inspection_finding`](#registry-inspection_finding) | registry | transaction | confidential | lifecycle | Finding recorded during an inspection (with photos and GPS evidence) |
| [`corrective_action`](#registry-corrective_action) | registry | transaction | confidential | lifecycle | Corrective action plan item (from findings, approval conditions, compliance or curriculum alerts) |
| [`compliance_requirement`](#registry-compliance_requirement) | registry | config | internal | versioned | Compliance requirement inherited down the policy hierarchy (fire, health and safety, certifications with expiry) |
| [`compliance_status`](#registry-compliance_status) | registry | transaction | internal | lifecycle | Status of one compliance requirement at one institution (Compliant, Attention required, Overdue, Critical) |
| [`onboarding_check`](#registry-onboarding_check) | registry | transaction | internal | lifecycle | Onboarding readiness step of an institution (structure, staff, learners matched, curriculum adopted, first register, first results) |
| [`onboarding_target`](#registry-onboarding_target) | registry | config | internal | none | Onboarding target date and wave per LGA (state rollout in LGA waves) |
| [`unknown_institution_reference`](#registry-unknown_institution_reference) | registry | event | internal | append | Reference to an institution not on the register (transfer, exam entry, certificate) — alert to the regulator |
| [`institution_profile`](#registry-institution_profile) | registry | projection | internal | snapshot | Comparison context of an institution (level, ownership, location band, size, PTR, infrastructure band, share with additional needs) |
| [`health_index_policy`](#registry-health_index_policy) | registry | config | internal | versioned | Versioned health-index weights, targets and bands (decomposable score, P8) |
| [`facility_check`](#registry-facility_check) | registry | transaction | internal | lifecycle | Fire inspection, health and safety check or certification with expiry (compliance centre evidence) |

<a id="registry-institution"></a>
## `institution`

Institution 360 master (public and private, every level)  

scope_node_id is the institution's own node. The financing channel is derived from ownership (FR-SUB-101): public → SDAF, private → direct subscription; a change applies from the next billing period.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INS-01, FR-INS-03, FR-INS-04, FR-INS-09, FR-INS-10, FR-INS-12, FR-CMD-101, FR-SUB-101, FR-CMD-111, FR-PVT-116 |
| Pages | INS-01, INS-02, INS-03, CMD-06, CMD-101, PVT-104, HOM-05 |
| Events | INS.REGISTERED, INS.STATUS_CHANGED, INS.MERGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_code` | `VARCHAR(20)` | no |  | INS-<country>-NNNNNN |
| `gov_reg_no` | `VARCHAR(40)` | yes |  | Government registration number, e.g. AB/SS/0412 |
| `name` | `VARCHAR(300)` | no |  |  |
| `short_name` | `VARCHAR(80)` | yes |  |  |
| `category` | `VARCHAR(32)` | no |  | ECCDE, primary, JSS, SSS, technical college, college of education, polytechnic, university, nursing, non-formal … · code list `institution_category` |
| `ownership` | `VARCHAR(32)` | no |  | federal, state, lga, private, faith, community, ngo · code list `ownership` |
| `is_public` | `BOOLEAN` | no |  | Derived from ownership; drives the financing channel |
| `operating_tenant_id` | `BINARY(16)` | no |  | Tenant whose ops zone runs the institution (state for public; provider tenant for private) |
| `provider_id` → `provider` | `BINARY(16)` | yes |  | Private provider (proprietor organisation) |
| `network_scope_id` → `scope_node` | `BINARY(16)` | yes |  | Optional network layer |
| `lga_scope_id` → `scope_node` | `BINARY(16)` | no |  | LGA the institution belongs to |
| `levels` | `JSON` | no |  | Education levels offered · code list `education_level` |
| `day_boarding` | `VARCHAR(32)` | yes |  | values: day, boarding, mixed |
| `gender_intake` | `VARCHAR(32)` | yes |  | values: mixed, boys, girls |
| `address` | `JSON` | no |  | Structured address (street, town, LGA, state, postcode) |
| `location` | `POINT SRID 4326` | yes |  | WGS84; NOT NULL once surveyed (500 m / 5 km duplicate checks) |
| `location_class` | `VARCHAR(32)` | yes |  | urban, peri-urban, rural (comparison context) · values: urban, peri_urban, rural |
| `capacity` | `INT UNSIGNED` | yes |  |  |
| `head_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `website` | `VARCHAR(2048)` | yes |  |  |
| `phone` | `VARCHAR(16)` | yes |  |  |
| `email` | `VARCHAR(254)` | yes |  |  |
| `onboarding_status` | `VARCHAR(32)` | no |  | Not yet onboarded, Onboarding, Live, Suspended, Closed · values: not_onboarded, onboarding, live, suspended, closed |
| `regulatory_status` | `VARCHAR(32)` | no |  | approved, approved_with_conditions, regularising, suspended, closed, unregistered · values: approved, approved_with_conditions, regularising, suspended, closed, unregistered, public_owned |
| `status` | `VARCHAR(32)` | no |  | values: proposed, active, suspended, closed, merged |
| `merged_into` → `institution` | `BINARY(16)` | yes |  | Alias after amalgamation |
| `is_regularisation` | `BOOLEAN` | no |  | Existing unregistered institution brought into compliance |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_code)
- Unique: (tenant_id, gov_reg_no)
- Index: (tenant_id, lga_scope_id)
- Index: (tenant_id, ownership, category)
- Index: (tenant_id, name)

<a id="registry-institution_change_request"></a>
## `institution_change_request`

Change request to an institution's master fields (name, registration number, ownership, category, address, coordinates)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INS-04 |
| Pages | INS-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `field_changes` | `JSON` | no |  | [{field, from, to}] |
| `reason` | `TEXT` | no |  |  |
| `evidence_document_id` | `BINARY(16)` | yes |  |  |
| `requested_by` → `app_user` | `BINARY(16)` | no |  |  |
| `decided_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-campus"></a>
## `campus`

Campus / site / branch of an institution

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INS-08 |
| Pages | INS-06, INS-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `address` | `JSON` | yes |  |  |
| `location` | `POINT SRID 4326` | yes |  |  |
| `is_main` | `BOOLEAN` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-org_unit"></a>
## `org_unit`

Faculty / school / department / unit (effective-dated tree, cost centres and heads)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | effective |
| Scope | owned |
| Module | `institutions` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INS-08, FR-ACA-108 |
| Pages | INS-06, ACA-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `campus_id` → `campus` | `BINARY(16)` | yes |  |  |
| `parent_id` → `org_unit` | `BINARY(16)` | yes |  |  |
| `unit_type` | `VARCHAR(32)` | no |  | values: faculty, school, department, unit, centre, house, year_group |
| `code` | `VARCHAR(20)` | yes |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `head_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `acting_head_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `cost_centre` | `VARCHAR(32)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-licence"></a>
## `licence`

Licence, accreditation or authorisation (operating licence, exam centre, certificate issuer, programme accreditation)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INS-05, FR-INS-06, FR-INS-07, FR-PVT-117, FR-ACA-108 |
| Pages | INS-04, INS-02, ACA-102 |
| Events | INS.LICENCE_EXPIRED, INS.LICENCE_RENEWED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: operating_licence, private_approval, accreditation, exam_centre, certificate_issuer, programme_accreditation, federal_approval |
| `licence_number` | `VARCHAR(60)` | no |  |  |
| `issuing_body` | `VARCHAR(32)` | no |  | State MoE, NBTE, NCCE, NUC, MDCN, NMCN, WAEC (centre) … · code list `regulator` |
| `programme_id` → `programme` | `BINARY(16)` | yes |  | For programme accreditation |
| `scope_detail` | `JSON` | yes |  | Levels, programmes or subjects covered |
| `conditions` | `TEXT` | yes |  |  |
| `issued_on` | `DATE` | no |  |  |
| `expires_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | Expired automatically the day after expiry · values: valid, expiring, expired, suspended, revoked |
| `approval_id` → `approval` | `BINARY(16)` | yes |  | Private-provider approval that produced it |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, issuing_body, licence_number)
- Index: (tenant_id, institution_id, kind, status)
- Index: (tenant_id, expires_on)

<a id="registry-inspection"></a>
## `inspection`

Inspection 360 — approval, routine, monitoring or follow-up inspection

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INSP-01, FR-INSP-02, FR-INSP-06, FR-CUR-14, FR-PVT-106, FR-INSP-101 |
| Pages | INS-07, INS-08, PVT-102 |
| Events | INSP.REPORT_APPROVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: approval, routine, monitoring, follow_up, thematic, renewal |
| `programme_id` → `inspection_programme` | `BINARY(16)` | yes |  |  |
| `provider_application_id` → `provider_application` | `BINARY(16)` | yes |  | Approval inspection |
| `scheduled_on` | `DATE` | no |  |  |
| `lead_inspector_id` → `staff` | `BINARY(16)` | yes |  |  |
| `risk_score` | `DECIMAL(7,3)` | yes |  |  |
| `briefing` | `JSON` | yes |  | Briefing pack snapshot (coverage, gaps, data, history, complaints) |
| `overall_judgement` | `VARCHAR(32)` | yes |  | code list `inspection_judgement` |
| `report_document_id` | `BINARY(16)` | yes |  |  |
| `visited_location` | `POINT SRID 4326` | yes |  | GPS captured on site |
| `status` | `VARCHAR(32)` | no |  | values: planned, scheduled, in_progress, report_draft, report_approved, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-inspection_programme"></a>
## `inspection_programme`

Risk-based inspection programme for a period, for inspectorate approval

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INSP-01 |
| Pages | INS-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `period_start` | `DATE` | no |  |  |
| `period_end` | `DATE` | no |  |  |
| `method` | `JSON` | yes |  | Weights: health index, compliance, alerts, time since last inspection |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-inspection_finding"></a>
## `inspection_finding`

Finding recorded during an inspection (with photos and GPS evidence)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `institutions` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INSP-03 |
| Pages | INS-08 |
| Events | INSP.FINDING_RECORDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `inspection_id` → `inspection` | `BINARY(16)` | no |  |  |
| `area` | `VARCHAR(32)` | no |  | code list `inspection_area` |
| `judgement` | `VARCHAR(32)` | no |  | code list `inspection_judgement` |
| `evidence` | `TEXT` | no |  |  |
| `evidence_document_ids` | `JSON` | yes |  |  |
| `requires_action` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-corrective_action"></a>
## `corrective_action`

Corrective action plan item (from findings, approval conditions, compliance or curriculum alerts)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INSP-03, FR-INSP-06, FR-CUR-12, FR-PVT-112 |
| Pages | INS-11, PVT-105 |
| Events | INSP.ACTION_VERIFIED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `source_kind` | `VARCHAR(32)` | no |  | values: inspection_finding, approval_condition, compliance, curriculum_alert, alert, intervention_workflow |
| `source_id` | `BINARY(16)` | no |  |  |
| `description` | `TEXT` | no |  |  |
| `owner_user_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `due_on` | `DATE` | no |  |  |
| `evidence_document_ids` | `JSON` | yes |  |  |
| `verified_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, plan_submitted, plan_approved, in_progress, evidence_submitted, verified, overdue, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-compliance_requirement"></a>
## `compliance_requirement`

Compliance requirement inherited down the policy hierarchy (fire, health and safety, certifications with expiry)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INSP-04, FR-INSP-101 |
| Pages | INS-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `requirement_key` | `VARCHAR(40)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `category` | `VARCHAR(32)` | no |  | values: fire, health_safety, structural, food_hygiene, transport, statutory_certification, data_protection, safeguarding |
| `applies_to` | `JSON` | no |  | Institution categories, levels, ownership |
| `evidence_required` | `TEXT` | yes |  |  |
| `renewal_months` | `SMALLINT` | yes |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, requirement_key, version)

<a id="registry-compliance_status"></a>
## `compliance_status`

Status of one compliance requirement at one institution (Compliant, Attention required, Overdue, Critical)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INSP-04, FR-INSP-101 |
| Pages | INS-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `requirement_id` → `compliance_requirement` | `BINARY(16)` | no |  |  |
| `evidence_document_id` | `BINARY(16)` | yes |  |  |
| `certified_on` | `DATE` | yes |  |  |
| `expires_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: compliant, attention_required, overdue, critical |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, requirement_id)

<a id="registry-onboarding_check"></a>
## `onboarding_check`

Onboarding readiness step of an institution (structure, staff, learners matched, curriculum adopted, first register, first results)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-CMD-102, FR-PVT-108 |
| Pages | CMD-103, ADM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `step` | `VARCHAR(32)` | no |  | values: structure_set_up, staff_loaded, learners_loaded, learners_matched, curriculum_adopted, first_register, first_results, live |
| `target_on` | `DATE` | yes |  |  |
| `completed_at` | `DATETIME(6)` | yes |  |  |
| `blocking_reason` | `VARCHAR(500)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: not_started, in_progress, done, blocked, not_applicable |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, step)

<a id="registry-onboarding_target"></a>
## `onboarding_target`

Onboarding target date and wave per LGA (state rollout in LGA waves)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-CMD-102 |
| Pages | CMD-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `lga_scope_id` → `scope_node` | `BINARY(16)` | no |  |  |
| `wave` | `SMALLINT` | no |  |  |
| `target_live_on` | `DATE` | no |  |  |
| `readiness_gate` | `JSON` | yes |  | Gate criteria for the wave |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, lga_scope_id)

<a id="registry-unknown_institution_reference"></a>
## `unknown_institution_reference`

Reference to an institution not on the register (transfer, exam entry, certificate) — alert to the regulator

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-CMD-103 |
| Pages | CMD-103, PVT-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `source_kind` | `VARCHAR(32)` | no |  | values: transfer, exam_entry, certificate, digitisation, application |
| `source_id` | `BINARY(16)` | no |  |  |
| `reported_name` | `VARCHAR(300)` | no |  |  |
| `reported_address` | `VARCHAR(500)` | yes |  |  |
| `lga_scope_id` → `scope_node` | `BINARY(16)` | yes |  |  |
| `alert_id` | `BINARY(16)` | yes |  | Alert raised to the regulator |
| `resolved_institution_id` → `institution` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-institution_profile"></a>
## `institution_profile`

Comparison context of an institution (level, ownership, location band, size, PTR, infrastructure band, share with additional needs)

| | |
|---|---|
| Zone | registry |
| Kind | projection |
| Classification | internal |
| History | snapshot |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-CMD-06, FR-CMD-109 |
| Pages | CMD-102, CMD-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `as_of` | `DATE` | no |  |  |
| `comparison_group` | `VARCHAR(60)` | no |  | Group within which ranking is allowed |
| `enrolment_band` | `VARCHAR(16)` | yes |  |  |
| `ptr_band` | `VARCHAR(16)` | yes |  |  |
| `infrastructure_band` | `VARCHAR(16)` | yes |  |  |
| `additional_needs_share` | `DECIMAL(6,3)` | yes |  |  |
| `context` | `JSON` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, institution_id, as_of)

<a id="registry-health_index_policy"></a>
## `health_index_policy`

Versioned health-index weights, targets and bands (decomposable score, P8)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-CMD-01 |
| Pages | INS-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `version` | `INT UNSIGNED` | no |  |  |
| `weights` | `JSON` | no |  | Indicator → weight (attendance, progress, exam outcomes … resource utilisation) |
| `targets` | `JSON` | no |  | Indicator → normalisation target |
| `bands` | `JSON` | no |  | strong ≥ 80, adequate 65–79, concern 50–64, critical < 50 |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `effective_from` | `DATE` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, version)

<a id="registry-facility_check"></a>
## `facility_check`

Fire inspection, health and safety check or certification with expiry (compliance centre evidence)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-INSP-101 |
| Pages | INS-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `campus_id` → `campus` | `BINARY(16)` | yes |  |  |
| `check_kind` | `VARCHAR(32)` | no |  | code list `facility_check_kind` |
| `performed_on` | `DATE` | no |  |  |
| `performed_by` | `VARCHAR(200)` | yes |  |  |
| `result` | `VARCHAR(32)` | no |  | values: pass, pass_with_actions, fail |
| `certificate_document_id` | `BINARY(16)` | yes |  |  |
| `expires_on` | `DATE` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

