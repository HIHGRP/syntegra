# PVT — Private education provider admission and regulation

One online door for private providers (MFS §10): proprietor account and identity, application with evidence against the state checklist, fees through Remita, desk review, approval inspection, four-eyes decision, digitally signed approval certificate, automatic tenant creation and onboarding, then renewals, conditions, monitoring, sanctions and learner protection on closure. The regulatory dataset that private institutions share with the state is defined by policy and delivered as projections (reg_* records) — the regulator never reads a private tenant's operational schema (MFS §16.3).

Module (system of record): `providers` · default zone: **registry** · default retention: `RS-INS-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`provider`](#registry-provider) | registry | master | confidential | lifecycle | Private education provider (proprietor organisation) — Provider 360 |
| [`provider_person`](#registry-provider_person) | registry | link | restricted | effective | Proprietor or director of a provider (identity verified by NIN) |
| [`provider_application`](#registry-provider_application) | registry | transaction | confidential | lifecycle | Application for approval (new, regularisation or renewal) of one or more proposed institutions |
| [`approval_checklist_item`](#registry-approval_checklist_item) | registry | config | public | versioned | State approval checklist item and minimum standard per level (policy data, not code) |
| [`application_evidence`](#registry-application_evidence) | registry | transaction | confidential | lifecycle | Evidence item against the approval checklist (pre-checked by document intelligence) |
| [`application_query`](#registry-application_query) | registry | transaction | confidential | lifecycle | Query sent back to the applicant during desk review, and the reply |
| [`regulatory_fee`](#registry-regulatory_fee) | registry | transaction | confidential | lifecycle | State regulatory fee (application, inspection, approval, renewal) — separate from the operator subscription |
| [`approval`](#registry-approval) | registry | master | public | lifecycle | Approval certificate of a private institution (signed, QR-verifiable, levels, capacity, conditions, expiry) |
| [`approval_condition`](#registry-approval_condition) | registry | transaction | confidential | lifecycle | Condition attached to an approval, tracked as a corrective action with evidence |
| [`sanction`](#registry-sanction) | registry | transaction | confidential | lifecycle | Sanction step on a private institution (warning → conditions → suspension of admissions → suspension → closure) with appeal |
| [`closure_case`](#registry-closure_case) | registry | transaction | confidential | lifecycle | Learner protection case when a private institution is suspended or closed (LGA tracks re-enrolment) |
| [`reg_dataset_definition`](#registry-reg_dataset_definition) | registry | config | internal | versioned | Regulatory dataset that private institutions share with the state (configured per country/state, MFS §10.5) |
| [`reg_snapshot`](#registry-reg_snapshot) | registry | snapshot | confidential | snapshot | Regulatory dataset delivery from a private institution (read-only to the regulator) |

<a id="registry-provider"></a>
## `provider`

Private education provider (proprietor organisation) — Provider 360

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `providers` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-101, FR-PVT-110, FR-PVT-102 |
| Pages | PVT-103, PVT-104 |
| Events | PVT.PROVIDER_REGISTERED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `legal_name` | `VARCHAR(300)` | no |  |  |
| `trading_name` | `VARCHAR(300)` | yes |  |  |
| `cac_number` | `VARCHAR(20)` | yes |  | Corporate Affairs Commission registration |
| `tin` | `VARCHAR(20)` | yes |  | Tax identification number |
| `provider_tenant_id` | `BINARY(16)` | yes |  | Private tenant created on first approval |
| `registered_address` | `JSON` | no |  |  |
| `phone` | `VARCHAR(16)` | yes |  |  |
| `email` | `VARCHAR(254)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: registered, applicant, approved, suspended, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, cac_number)

<a id="registry-provider_person"></a>
## `provider_person`

Proprietor or director of a provider (identity verified by NIN)

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | restricted |
| History | effective |
| Scope | none |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-101 |
| Pages | PVT-101, PVT-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `provider_id` → `provider` | `BINARY(16)` | no |  |  |
| `user_id` → `app_user` | `BINARY(16)` | yes |  | Account of the proprietor (PROP role) |
| `given_name` | `VARCHAR(200)` | no |  |  |
| `family_name` | `VARCHAR(200)` | no |  |  |
| `role` | `VARCHAR(32)` | no |  | values: proprietor, director, company_secretary, head_designate |
| `nin_verified` | `BOOLEAN` | no |  | External identifier held in external_identifier |
| `ownership_share` | `DECIMAL(6,3)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-provider_application"></a>
## `provider_application`

Application for approval (new, regularisation or renewal) of one or more proposed institutions

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `providers` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-101, FR-PVT-103, FR-PVT-106, FR-PVT-109, FR-PVT-113, FR-PVT-117 |
| Pages | PVT-101, PVT-102 |
| Events | ADM.APPLICATION_SUBMITTED, INS.APPLICATION_SUBMITTED, PVT.DECISION_MADE |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `provider_id` → `provider` | `BINARY(16)` | no |  |  |
| `application_number` | `VARCHAR(32)` | no |  |  |
| `kind` | `VARCHAR(32)` | no |  | values: new, regularisation, renewal, variation |
| `proposed_institution` | `JSON` | no |  | Name, levels, location, capacity, curricula, fee schedule, staffing plan |
| `proposed_location` | `POINT SRID 4326` | yes |  | Map pin (duplicate check within 500 m) |
| `institution_id` → `institution` | `BINARY(16)` | yes |  | Existing or created institution |
| `federal_approval` | `JSON` | yes |  | NUC / NBTE / NCCE / MDCN / NMCN evidence for tertiary and medical (FR-PVT-117) |
| `completeness` | `DECIMAL(6,3)` | yes |  | Share of checklist items evidenced |
| `submitted_at` | `DATETIME(6)` | yes |  |  |
| `desk_review_due_on` | `DATE` | yes |  | 10 working days |
| `inspection_due_on` | `DATE` | yes |  | 20 working days |
| `decision` | `VARCHAR(32)` | yes |  | values: approve, approve_with_conditions, defer, refuse |
| `decision_reasons` | `TEXT` | yes |  |  |
| `decided_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `second_approver_id` → `app_user` | `BINARY(16)` | yes |  | Four-eyes decision |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `appeal_route` | `VARCHAR(500)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, fee_pending, desk_review, query_raised, inspection, decision, approved, refused, deferred, withdrawn, appealed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, application_number)

- Check `four_eyes`: `second_approver_id IS NULL OR decided_by IS NULL OR second_approver_id <> decided_by`

<a id="registry-approval_checklist_item"></a>
## `approval_checklist_item`

State approval checklist item and minimum standard per level (policy data, not code)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-104 |
| Pages | PVT-101, PVT-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `item_key` | `VARCHAR(40)` | no |  |  |
| `area` | `VARCHAR(32)` | no |  | values: legal, premises, facilities, staffing, curriculum, safeguarding_safety, finance |
| `title` | `VARCHAR(300)` | no |  |  |
| `levels` | `JSON` | yes |  | code list `education_level` |
| `is_mandatory` | `BOOLEAN` | no |  |  |
| `minimum_standard` | `JSON` | yes |  | e.g. classroom size, toilets by sex, laboratories |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, item_key, version)

<a id="registry-application_evidence"></a>
## `application_evidence`

Evidence item against the approval checklist (pre-checked by document intelligence)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `providers` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-103 |
| Pages | PVT-101, PVT-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `application_id` → `provider_application` | `BINARY(16)` | no |  |  |
| `checklist_item_id` → `approval_checklist_item` | `BINARY(16)` | no |  |  |
| `document_id` | `BINARY(16)` | no |  | records zone |
| `ai_precheck` | `JSON` | yes |  | Document-intelligence pre-check result and confidence |
| `reviewer_status` | `VARCHAR(32)` | no |  | values: pending, accepted, queried, rejected |
| `reviewer_note` | `VARCHAR(1000)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, application_id, checklist_item_id, document_id)

<a id="registry-application_query"></a>
## `application_query`

Query sent back to the applicant during desk review, and the reply

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-106 |
| Pages | PVT-102, PVT-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `application_id` → `provider_application` | `BINARY(16)` | no |  |  |
| `question` | `TEXT` | no |  |  |
| `asked_by` → `app_user` | `BINARY(16)` | no |  |  |
| `reply` | `TEXT` | yes |  |  |
| `replied_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-regulatory_fee"></a>
## `regulatory_fee`

State regulatory fee (application, inspection, approval, renewal) — separate from the operator subscription

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-105, FR-SUB-122 |
| Pages | PVT-101, PVT-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `provider_id` → `provider` | `BINARY(16)` | no |  |  |
| `application_id` → `provider_application` | `BINARY(16)` | yes |  |  |
| `fee_kind` | `VARCHAR(32)` | no |  | values: application, inspection, approval, renewal, late_renewal |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `revenue_code` | `VARCHAR(40)` | no |  | State revenue code |
| `payment_reference` | `VARCHAR(64)` | yes |  | Remita RRR |
| `paid_at` | `DATETIME(6)` | yes |  |  |
| `receipt_number` | `VARCHAR(64)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: due, paid, waived, refunded |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-approval"></a>
## `approval`

Approval certificate of a private institution (signed, QR-verifiable, levels, capacity, conditions, expiry)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `providers` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-107, FR-PVT-113, FR-PVT-116 |
| Pages | PVT-103, PVT-104, PVT-105 |
| Events | PVT.APPROVAL_ISSUED, PVT.APPROVAL_RENEWED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `application_id` → `provider_application` | `BINARY(16)` | no |  |  |
| `approval_number` | `VARCHAR(40)` | no |  |  |
| `approved_levels` | `JSON` | no |  | code list `education_level` |
| `approved_capacity` | `INT UNSIGNED` | yes |  |  |
| `valid_from_on` | `DATE` | no |  |  |
| `expires_on` | `DATE` | no |  | Default 3 years |
| `certificate_id` → `certificate` | `BINARY(16)` | yes |  | Signed approval certificate in the certificate registry |
| `status` | `VARCHAR(32)` | no |  | values: active, expiring, expired, suspended, revoked, superseded |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, approval_number)

<a id="registry-approval_condition"></a>
## `approval_condition`

Condition attached to an approval, tracked as a corrective action with evidence

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `providers` |
| Origin | appj |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-112 |
| Pages | PVT-105 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `approval_id` → `approval` | `BINARY(16)` | no |  |  |
| `condition_text` | `TEXT` | no |  |  |
| `due_on` | `DATE` | no |  |  |
| `corrective_action_id` → `corrective_action` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, plan_submitted, plan_approved, in_progress, evidence_submitted, verified, overdue, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-sanction"></a>
## `sanction`

Sanction step on a private institution (warning → conditions → suspension of admissions → suspension → closure) with appeal

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-114 |
| Pages | PVT-103, PVT-105 |
| Events | PVT.SANCTION_APPLIED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `step` | `VARCHAR(32)` | no |  | values: warning, conditions, admissions_suspended, suspension, closure |
| `grounds` | `TEXT` | no |  |  |
| `evidence_document_ids` | `JSON` | no |  |  |
| `blocks_admissions` | `BOOLEAN` | no |  |  |
| `blocks_exam_entries` | `BOOLEAN` | no |  |  |
| `decided_by` → `app_user` | `BINARY(16)` | no |  |  |
| `effective_on` | `DATE` | no |  |  |
| `appeal_status` | `VARCHAR(32)` | yes |  | values: none, lodged, upheld, dismissed |
| `lifted_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: proposed, approved, in_effect, appealed, lifted, upheld |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-closure_case"></a>
## `closure_case`

Learner protection case when a private institution is suspended or closed (LGA tracks re-enrolment)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-115 |
| Pages | PVT-103, PVT-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `sanction_id` → `sanction` | `BINARY(16)` | yes |  |  |
| `learners_affected` | `INT UNSIGNED` | no |  |  |
| `learners_reenrolled` | `INT UNSIGNED` | no |  |  |
| `alternatives` | `JSON` | yes |  | Nearby approved institutions with places |
| `lga_officer_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-reg_dataset_definition"></a>
## `reg_dataset_definition`

Regulatory dataset that private institutions share with the state (configured per country/state, MFS §10.5)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-111, FR-INS-10, FR-CUR-114 |
| Pages | PVT-103, INS-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `dataset` | `VARCHAR(32)` | no |  | values: enrolment, attendance, staffing, curriculum_coverage, results, safety, fees, compliance, finance, registers |
| `fields` | `JSON` | no |  | Fields included |
| `frequency` | `VARCHAR(32)` | no |  | values: live, daily, weekly, termly, per_series, per_session, as_occurs |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, dataset, version)

<a id="registry-reg_snapshot"></a>
## `reg_snapshot`

Regulatory dataset delivery from a private institution (read-only to the regulator)  

Produced by the private tenant's ops zone through the governed exchange; the regulator reads only this.

| | |
|---|---|
| Zone | registry |
| Kind | snapshot |
| Classification | confidential |
| History | snapshot |
| Scope | owned |
| Module | `providers` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-PVT-111, FR-CUR-114 |
| Pages | PVT-103, CMD-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `dataset` | `VARCHAR(32)` | no |  | values: enrolment, attendance, staffing, curriculum_coverage, results, safety, fees, compliance, finance, registers |
| `definition_id` → `reg_dataset_definition` | `BINARY(16)` | no |  |  |
| `as_of` | `DATETIME(6)` | no |  |  |
| `payload` | `JSON` | no |  | Aggregates and permitted identities only |
| `payload_hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, institution_id, dataset, as_of)

