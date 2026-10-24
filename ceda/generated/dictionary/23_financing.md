# SUB — Programme financing — Student Digital Access Fee (SDAF) rates, census, payers, exemptions, demand, collection, remittance and reconciliation

Public institutions are financed by the SDAF, a per-student charge each term or semester by institution type, collected by the State Government into its designated revenue account and remitted in full to SDIN (MFS §20). The platform administers rates, the census-date billable count (one counting rule for public and private), payers (government only for public primary and JSS — UBE Act 2004 s.3), exemptions, demand notices, idempotent posting of state collections, remittances with ageing, and the dual-signed reconciliation statement. It never holds SDAF money. Rates, counts, notices, receipts, remittances and statements are append-only and audited end to end; segregation of duties is enforced in data (SDIN read-only on collections and remittances; recorder ≠ approver). Private subscriptions are in domain PLT.

Module (system of record): `financing` · default zone: **registry** · default retention: `RS-SDAF`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`sdaf_rate_card`](#registry-sdaf_rate_card) | registry | config | internal | versioned | Version of the state-approved SDAF rate card (propose → approve → publish) |
| [`sdaf_rate`](#registry-sdaf_rate) | registry | config | internal | append | Rate in a rate card for an institution type and level, per term or per semester (naira) |
| [`billing_period`](#registry-billing_period) | registry | config | internal | lifecycle | Term or semester billing period with census date (from each institution type's academic calendar) |
| [`sdaf_payer_rule`](#registry-sdaf_payer_rule) | registry | config | internal | versioned | Who pays the SDAF for an institution type and level (government only for public primary and JSS) |
| [`sdaf_exemption_category`](#registry-sdaf_exemption_category) | registry | config | internal | versioned | Exemption category (SEND, orphans and vulnerable children, IDPs, scholarship holders) with funding rule |
| [`sdaf_exemption`](#registry-sdaf_exemption) | registry | transaction | restricted | lifecycle | Approved SDAF exemption for a learner and period (learner stays in the headcount; reported separately) |
| [`census_snapshot`](#registry-census_snapshot) | registry | snapshot | confidential | versioned | Billable-learner count of an institution for a period (flags cleared, head-confirmed, frozen and hashed; amendments versioned) |
| [`census_learner`](#registry-census_learner) | registry | snapshot | confidential | append | Learner included or excluded in a census snapshot, with reason (append-only) |
| [`census_flag`](#registry-census_flag) | registry | queue | confidential | lifecycle | Ghost-learner flag before freezing (no attendance since period start, identity conflict, unexplained rise) — cleared or explained by the head |
| [`billing_period_billed`](#registry-billing_period_billed) | registry | link | confidential | append | Once-per-period billing guard — a learner is billed once per period across channels and institutions |
| [`sdaf_demand`](#registry-sdaf_demand) | registry | transaction | confidential | lifecycle | SDAF demand notice (consolidated to a government payer) or individual assessment (never at basic-education level) |
| [`sdaf_collection`](#registry-sdaf_collection) | registry | event | confidential | append | Payment into the state revenue account against a demand (posted idempotently from state notifications; append-only) |
| [`unmatched_collection`](#registry-unmatched_collection) | registry | queue | confidential | lifecycle | State collection notification not matched to a demand, or a held duplicate |
| [`remittance`](#registry-remittance) | registry | event | confidential | append | Remittance of collected SDAF from the State Government to SDIN, with advice (recorder ≠ approver; append-only) |
| [`remittance_allocation`](#registry-remittance_allocation) | registry | link | confidential | append | Allocation of a remittance to the collections it covers |
| [`reconciliation_statement`](#registry-reconciliation_statement) | registry | snapshot | confidential | lifecycle | Period statement — billed, exempted, collected, remitted, outstanding — with dual sign-off (state + SDIN), locked and hashed |
| [`reconciliation_line`](#registry-reconciliation_line) | registry | snapshot | confidential | append | Line of a reconciliation statement by institution (with logged disputes) |
| [`sdaf_public_summary`](#registry-sdaf_public_summary) | registry | snapshot | public | append | Optional aggregated public summary per term (no learner data) |

<a id="registry-sdaf_rate_card"></a>
## `sdaf_rate_card`

Version of the state-approved SDAF rate card (propose → approve → publish)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-102 |
| Pages | SUB-101 |
| Events | SUB.RATE_CARD_PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `version` | `INT UNSIGNED` | no |  |  |
| `proposed_by` → `app_user` | `BINARY(16)` | no |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  | Commissioner or State Executive Council |
| `approval_instrument` | `VARCHAR(200)` | yes |  | Approval reference (D25/D26) |
| `effective_from` | `DATE` | no |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, version)

- Check `four_eyes`: `approved_by IS NULL OR approved_by <> proposed_by`

<a id="registry-sdaf_rate"></a>
## `sdaf_rate`

Rate in a rate card for an institution type and level, per term or per semester (naira)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-102 |
| Pages | SUB-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `rate_card_id` → `sdaf_rate_card` | `BINARY(16)` | no |  |  |
| `institution_type` | `VARCHAR(32)` | no |  | code list `institution_category` |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `charge_period` | `VARCHAR(32)` | no |  | values: per_term, per_semester |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, rate_card_id, institution_type, education_level)

<a id="registry-billing_period"></a>
## `billing_period`

Term or semester billing period with census date (from each institution type's academic calendar)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-103, FR-SUB-126 |
| Pages | SUB-102, SUB-105 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `academic_period_id` → `academic_period` | `BINARY(16)` | no |  |  |
| `institution_types` | `JSON` | no |  | code list `institution_category` |
| `label` | `VARCHAR(40)` | no |  | e.g. 2026/27-T1-BASIC, 2026/27-S1-TERTIARY |
| `census_on` | `DATE` | no |  | Default end of week 3 (term) or week 4 (semester) |
| `confirmation_closes_on` | `DATE` | no |  |  |
| `collection_window_ends_on` | `DATE` | no |  |  |
| `remittance_due_on` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: planned, census_open, confirming, demand_issued, collecting, remitting, reconciled, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, label)

<a id="registry-sdaf_payer_rule"></a>
## `sdaf_payer_rule`

Who pays the SDAF for an institution type and level (government only for public primary and JSS)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-107 |
| Pages | SUB-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_type` | `VARCHAR(32)` | no |  | code list `institution_category` |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `is_basic_education` | `BOOLEAN` | no |  | Public primary or junior secondary |
| `payer` | `VARCHAR(32)` | no |  | values: government, parent_or_student, sponsor, scholarship, split |
| `split` | `JSON` | yes |  | Shares when payer = split |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, institution_type, education_level, version)

- Check `ube_act`: `NOT (is_basic_education AND payer <> 'government')`

<a id="registry-sdaf_exemption_category"></a>
## `sdaf_exemption_category`

Exemption category (SEND, orphans and vulnerable children, IDPs, scholarship holders) with funding rule

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `financing` |
| Origin | ceda |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-108 |
| Pages | SUB-106 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `funding_rule` | `VARCHAR(32)` | no |  | values: borne_by_state, waived |
| `evidence_required` | `VARCHAR(500)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

<a id="registry-sdaf_exemption"></a>
## `sdaf_exemption`

Approved SDAF exemption for a learner and period (learner stays in the headcount; reported separately)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-108 |
| Pages | SUB-106, SUB-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `billing_period_id` → `billing_period` | `BINARY(16)` | no |  |  |
| `category_id` → `sdaf_exemption_category` | `BINARY(16)` | no |  |  |
| `evidence_document_id` | `BINARY(16)` | no |  |  |
| `requested_by` → `app_user` | `BINARY(16)` | no |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, billing_period_id)

- Check `four_eyes`: `approved_by IS NULL OR approved_by <> requested_by`

<a id="registry-census_snapshot"></a>
## `census_snapshot`

Billable-learner count of an institution for a period (flags cleared, head-confirmed, frozen and hashed; amendments versioned)

| | |
|---|---|
| Zone | registry |
| Kind | snapshot |
| Classification | confidential |
| History | versioned |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-104, FR-SUB-105, FR-SUB-106, FR-SUB-118 |
| Pages | SUB-102 |
| Events | SUB.CENSUS_FROZEN |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `billing_period_id` → `billing_period` | `BINARY(16)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `enrolled` | `INT UNSIGNED` | no |  |  |
| `verified` | `INT UNSIGNED` | no |  |  |
| `excluded` | `INT UNSIGNED` | no |  |  |
| `exempted` | `INT UNSIGNED` | no |  |  |
| `billable` | `INT UNSIGNED` | no |  |  |
| `open_flags` | `INT UNSIGNED` | no |  | Count cannot be frozen while flags are open |
| `confirmed_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `confirmed_at` | `DATETIME(6)` | yes |  |  |
| `frozen_at` | `DATETIME(6)` | yes |  |  |
| `content_hash` | `BINARY(32)` | yes |  |  |
| `challenge` | `JSON` | yes |  | Evidence-based challenge and decision |
| `status` | `VARCHAR(32)` | no |  | values: draft, flags_open, awaiting_confirmation, confirmed, challenged, frozen, superseded |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, billing_period_id, version)

- Check `frozen_needs_clear`: `status <> 'frozen' OR (open_flags = 0 AND content_hash IS NOT NULL AND confirmed_by IS NOT NULL)`

<a id="registry-census_learner"></a>
## `census_learner`

Learner included or excluded in a census snapshot, with reason (append-only)

| | |
|---|---|
| Zone | registry |
| Kind | snapshot |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-104, FR-SUB-101 |
| Pages | SUB-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `snapshot_id` → `census_snapshot` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `inclusion` | `VARCHAR(32)` | no |  | values: billable, excluded, exempt |
| `reason` | `VARCHAR(32)` | yes |  | values: withdrawn_before_census, duplicate, unverified, other_institution_holds, exempt |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, snapshot_id, learner_id)

<a id="registry-census_flag"></a>
## `census_flag`

Ghost-learner flag before freezing (no attendance since period start, identity conflict, unexplained rise) — cleared or explained by the head

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `financing` |
| Origin | ceda |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-105 |
| Pages | SUB-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `snapshot_id` → `census_snapshot` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | yes |  |  |
| `flag_kind` | `VARCHAR(32)` | no |  | values: no_attendance_since_start, identity_conflict, unexplained_rise |
| `evidence` | `JSON` | no |  |  |
| `resolution` | `VARCHAR(32)` | yes |  | values: cleared, explained, removed_from_count |
| `explanation` | `VARCHAR(1000)` | yes |  |  |
| `resolved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-billing_period_billed"></a>
## `billing_period_billed`

Once-per-period billing guard — a learner is billed once per period across channels and institutions  

Insert of a second row for the same learner and period fails — the database-level guarantee of FR-SUB-101.

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `financing` |
| Origin | ceda |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-101, FR-SUB-104 |
| Pages | SUB-102, SUB-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `billing_period_id` → `billing_period` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `channel` | `VARCHAR(32)` | no |  | values: sdaf, direct_subscription |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `snapshot_id` → `census_snapshot` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, billing_period_id, learner_id)

<a id="registry-sdaf_demand"></a>
## `sdaf_demand`

SDAF demand notice (consolidated to a government payer) or individual assessment (never at basic-education level)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-109, FR-SUB-107 |
| Pages | SUB-103, SUB-109 |
| Events | SUB.DEMAND_ISSUED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `demand_number` | `VARCHAR(32)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `billing_period_id` → `billing_period` | `BINARY(16)` | no |  |  |
| `snapshot_id` → `census_snapshot` | `BINARY(16)` | no |  |  |
| `payer_kind` | `VARCHAR(32)` | no |  | values: government, parent_or_student, sponsor, scholarship, split |
| `payer_ref` | `BINARY(16)` | yes |  | Government payer, guardian, learner or sponsor |
| `learner_id` → `learner` | `BINARY(16)` | yes |  | Individual assessments only |
| `billable_count` | `INT UNSIGNED` | no |  |  |
| `waived_count` | `INT UNSIGNED` | no |  |  |
| `rate_id` → `sdaf_rate` | `BINARY(16)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (billable − waived) × rate (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `revenue_code` | `VARCHAR(40)` | no |  |  |
| `payment_reference` | `VARCHAR(64)` | no |  | Remita RRR or state e-revenue reference |
| `issued_at` | `DATETIME(6)` | no |  |  |
| `is_basic_education` | `BOOLEAN` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: issued, part_paid, paid, overdue, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, demand_number)
- Unique: (tenant_id, payment_reference)

- Check `ube_act`: `NOT (is_basic_education AND payer_kind <> 'government')`

<a id="registry-sdaf_collection"></a>
## `sdaf_collection`

Payment into the state revenue account against a demand (posted idempotently from state notifications; append-only)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-110, FR-SUB-111, FR-SUB-114 |
| Pages | SUB-103, SUB-109 |
| Events | SUB.COLLECTION_POSTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `demand_id` → `sdaf_demand` | `BINARY(16)` | no |  |  |
| `state_receipt_ref` | `VARCHAR(128)` | no |  | State e-receipt / collection-system id — idempotency key |
| `channel` | `VARCHAR(32)` | no |  | values: state_portal, remita, bank_branch, pos, ussd, bank_transfer |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `paid_at` | `DATETIME(6)` | no |  |  |
| `statement_matched_at` | `DATETIME(6)` | yes |  | Daily reconciliation against the state collection-account statement |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, state_receipt_ref)

<a id="registry-unmatched_collection"></a>
## `unmatched_collection`

State collection notification not matched to a demand, or a held duplicate

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `financing` |
| Origin | ceda |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-111 |
| Pages | SUB-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `state_receipt_ref` | `VARCHAR(128)` | no |  |  |
| `payload` | `JSON` | no |  |  |
| `reason` | `VARCHAR(32)` | no |  | values: no_reference, unknown_reference, amount_mismatch, duplicate |
| `resolved_demand_id` → `sdaf_demand` | `BINARY(16)` | yes |  |  |
| `resolved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-remittance"></a>
## `remittance`

Remittance of collected SDAF from the State Government to SDIN, with advice (recorder ≠ approver; append-only)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-112, FR-SUB-114 |
| Pages | SUB-104 |
| Events | SUB.REMITTANCE_RECORDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `billing_period_id` → `billing_period` | `BINARY(16)` | no |  |  |
| `advice_ref` | `VARCHAR(64)` | no |  |  |
| `bank_ref` | `VARCHAR(64)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `remitted_on` | `DATE` | no |  |  |
| `recorded_by` → `app_user` | `BINARY(16)` | no |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, advice_ref)

- Check `dual_control`: `approved_by <> recorded_by`

<a id="registry-remittance_allocation"></a>
## `remittance_allocation`

Allocation of a remittance to the collections it covers

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-112 |
| Pages | SUB-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `remittance_id` → `remittance` | `BINARY(16)` | no |  |  |
| `collection_id` → `sdaf_collection` | `BINARY(16)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, remittance_id, collection_id)

<a id="registry-reconciliation_statement"></a>
## `reconciliation_statement`

Period statement — billed, exempted, collected, remitted, outstanding — with dual sign-off (state + SDIN), locked and hashed  

Once both signatures exist no line changes; corrections go into the next statement.

| | |
|---|---|
| Zone | registry |
| Kind | snapshot |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `financing` |
| Origin | appj |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-113, FR-SUB-115, FR-SUB-125 |
| Pages | SUB-104, SUB-105 |
| Events | SUB.STATEMENT_SIGNED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `billing_period_id` → `billing_period` | `BINARY(16)` | no |  |  |
| `billed_minor` | `BIGINT` | no |  | (minor units) |
| `exempted_minor` | `BIGINT` | no |  | (minor units) |
| `collected_minor` | `BIGINT` | no |  | (minor units) |
| `remitted_minor` | `BIGINT` | no |  | (minor units) |
| `outstanding_minor` | `BIGINT` | no |  | (minor units) |
| `late_remittance_charge_minor` | `BIGINT` | no |  | (minor units) |
| `service_credits_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `state_signed_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `state_signed_at` | `DATETIME(6)` | yes |  |  |
| `operator_signed_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `operator_signed_at` | `DATETIME(6)` | yes |  |  |
| `content_hash` | `BINARY(32)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, state_signed, operator_signed, signed_locked, disputed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, billing_period_id)

- Check `dual_signature`: `operator_signed_by IS NULL OR state_signed_by IS NULL OR operator_signed_by <> state_signed_by`

<a id="registry-reconciliation_line"></a>
## `reconciliation_line`

Line of a reconciliation statement by institution (with logged disputes)

| | |
|---|---|
| Zone | registry |
| Kind | snapshot |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `financing` |
| Origin | ceda |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-113 |
| Pages | SUB-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `statement_id` → `reconciliation_statement` | `BINARY(16)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `billed_minor` | `BIGINT` | no |  | (minor units) |
| `exempted_minor` | `BIGINT` | no |  | (minor units) |
| `collected_minor` | `BIGINT` | no |  | (minor units) |
| `remitted_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `dispute` | `JSON` | yes |  | Dispute logged against the line |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, statement_id, institution_id)

<a id="registry-sdaf_public_summary"></a>
## `sdaf_public_summary`

Optional aggregated public summary per term (no learner data)

| | |
|---|---|
| Zone | registry |
| Kind | snapshot |
| Classification | public |
| History | append |
| Scope | owned |
| Module | `financing` |
| Origin | ceda |
| Retention | `RS-SDAF` |
| Requirements | FR-SUB-115 |
| Pages | SUB-105 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `billing_period_id` → `billing_period` | `BINARY(16)` | no |  |  |
| `published_at` | `DATETIME(6)` | no |  |  |
| `summary` | `JSON` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

