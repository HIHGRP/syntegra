# MDM — Master data management, identity matching and data quality

"One person, one record" (P4). Before any learner, guardian, staff member, institution, supplier, course or programme is created the matching engine runs (Book 3 §12): deterministic identifier matches, Fellegi–Sunter probabilistic scoring, probable matches routed to stewards (LRN-03, ADM-17), merges with survivorship, alias resolution and 90-day un-merge. External identifiers (NIN, exam candidate numbers, TRCN) are encrypted with HMAC lookup tokens and never used as keys. Data-quality rules and issues feed the Data Quality Index (§12.3) and the data quality command centre (CMD-16).

Module (system of record): `mdm` · default zone: **registry** · default retention: `RS-MDM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`external_identifier`](#registry-external_identifier) | registry | master | restricted | lifecycle | Authorised external identifier of a person (NIN, exam candidate number, UPN, TRCN number …) |
| [`identity_verification`](#registry-identity_verification) | registry | event | restricted | append | Identity verification attempt against a national source (NIMC NIN, TRCN, CAC) — result only, not the source data |
| [`match_review`](#registry-match_review) | registry | queue | restricted | lifecycle | Probable-duplicate pair awaiting or holding a steward decision |
| [`match_pair_decision`](#registry-match_pair_decision) | registry | event | internal | append | Remembered steward decision on a pair (suppresses re-raising; trains matching weights) |
| [`merge_journal`](#registry-merge_journal) | registry | event | restricted | append | Merge of two master records with survivorship and re-pointed references (un-merge within 90 days) |
| [`data_quality_rule`](#registry-data_quality_rule) | registry | config | internal | versioned | Data-quality rule feeding the DQI components (completeness, uniqueness, validity, timeliness, consistency, verification) |
| [`data_quality_issue`](#registry-data_quality_issue) | registry | queue | internal | lifecycle | Open data-quality issue on a record (validation failure, probable duplicate, stale dataset, conflict) |
| [`data_quality_issue`](#ops-data_quality_issue) | ops | queue | internal | lifecycle | Open data-quality issue on a record (validation failure, probable duplicate, stale dataset, conflict) |
| [`dataset_freshness`](#registry-dataset_freshness) | registry | projection | internal | none | Last data received per institution per dataset (stale institutions shown, not hidden) |

<a id="registry-external_identifier"></a>
## `external_identifier`

Authorised external identifier of a person (NIN, exam candidate number, UPN, TRCN number …)  

Never displayed unmasked; NIN never used as a primary key or sole matching key (Book 3 §8.3, §12.1). Identifiers of learners, guardians and staff share this table so matching can block on value_hmac.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `mdm` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-04, FR-FAM-01, FR-STF-02, FR-PVT-101, FR-FCL-14 |
| Pages | LRN-02, LRN-04, STF-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `person_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `person_id` | `BINARY(16)` | no |  | learner, guardian, staff or provider_person id (polymorphic) |
| `scheme` | `VARCHAR(32)` | no |  | NG-NIN, WAEC-CAND, NECO-CAND, JAMB-REG, TRCN, UPN, INST-ID … · code list `identifier_scheme` |
| `value_hmac` | `BINARY(32)` | no | restricted | HMAC-SHA-256 lookup of value |
| `value_enc` | `VARBINARY(1024)` | no | restricted | Envelope-encrypted value. Identifier value — envelope-encrypted per tenant and scheme |
| `value_last4` | `CHAR(4)` | yes | restricted | Last four characters of value for masked display |
| `value_national_hmac` | `BINARY(32)` | yes |  | National lookup token (federation key) — NIN only, for cross-state matching without exchanging the NIN (CR-002) |
| `issuer` | `VARCHAR(120)` | yes |  | Issuing body where not implied by the scheme |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `verified_via` | `VARCHAR(32)` | yes |  | values: nimc, registrar, exam_body, trcn, cac, manual |
| `status` | `VARCHAR(32)` | no |  | values: unverified, verified, mismatch, revoked |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, person_kind, person_id)
- Index: (tenant_id, scheme, value_hmac)
- Index: (tenant_id, scheme, value_national_hmac)

<a id="registry-identity_verification"></a>
## `identity_verification`

Identity verification attempt against a national source (NIMC NIN, TRCN, CAC) — result only, not the source data

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `mdm` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-LRN-04, FR-CER-107, FR-PVT-101, FR-PVT-117 |
| Pages | LRN-02, CER-102, PVT-101 |
| Events | ID.NIN_VERIFIED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `person_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `person_id` | `BINARY(16)` | no |  |  |
| `scheme` | `VARCHAR(32)` | no |  | code list `identifier_scheme` |
| `channel` | `VARCHAR(32)` | no |  | values: nimc, registrar, exam_body, trcn, cac, manual |
| `requested_by` | `BINARY(16)` | no |  | User or service identity |
| `purpose_code` | `VARCHAR(40)` | no |  |  |
| `outcome` | `VARCHAR(32)` | no |  | values: match, partial_match, no_match, manual_review, error |
| `match_detail` | `JSON` | yes |  | Field-level agreement (name, DOB) — no source photo or address stored |
| `provider_ref` | `VARCHAR(128)` | yes |  | Gateway transaction reference |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-match_review"></a>
## `match_review`

Probable-duplicate pair awaiting or holding a steward decision

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `mdm` |
| Origin | appj |
| Retention | `RS-MDM` |
| Requirements | FR-LRN-02, FR-FAM-01, FR-INS-02, FR-PVT-102, FR-FIN-04, FR-DOC-108 |
| Pages | LRN-03, ADM-17, FAM-02, STF-03, INS-03 |
| Events | LRN.MATCH_REVIEWED, MDM.MATCH_DECIDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `entity_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, institution, provider, supplier, course, programme |
| `candidate_id` | `BINARY(16)` | no |  | Incoming or newer record |
| `existing_id` | `BINARY(16)` | no |  | Existing master record |
| `score` | `DECIMAL(7,6)` | no |  | 0.80–0.98 probable band; ≥ 0.98 auto-linked (still logged) |
| `evidence` | `JSON` | no |  | Field comparisons, blocking keys, model version |
| `source` | `VARCHAR(32)` | no |  | values: registration, import, transfer, digitisation, exam_import, application, nightly_scan |
| `assigned_to` → `app_user` | `BINARY(16)` | yes |  |  |
| `decision` | `VARCHAR(32)` | yes |  | values: same, different, unsure |
| `decision_reason` | `VARCHAR(500)` | yes |  |  |
| `decided_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, entity_kind, candidate_id, existing_id)

<a id="registry-match_pair_decision"></a>
## `match_pair_decision`

Remembered steward decision on a pair (suppresses re-raising; trains matching weights)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `mdm` |
| Origin | ceda |
| Retention | `RS-MDM` |
| Requirements | FR-LRN-02 |
| Pages | LRN-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `entity_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, institution, provider, supplier, course, programme |
| `record_a_id` | `BINARY(16)` | no |  |  |
| `record_b_id` | `BINARY(16)` | no |  |  |
| `decision` | `VARCHAR(32)` | no |  | values: same, different, unsure |
| `model_version` | `VARCHAR(32)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, entity_kind, record_a_id, record_b_id)

<a id="registry-merge_journal"></a>
## `merge_journal`

Merge of two master records with survivorship and re-pointed references (un-merge within 90 days)  

Merges of learners holding certificates or exam results need two approvers (Book 3 §12.2).

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `mdm` |
| Origin | ceda |
| Retention | `RS-MDM` |
| Requirements | FR-LRN-14, FR-INS-11 |
| Pages | LRN-08, ADM-17 |
| Events | MDM.MERGED, MDM.UNMERGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `entity_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, institution, provider, supplier, course, programme |
| `survivor_id` | `BINARY(16)` | no |  |  |
| `merged_id` | `BINARY(16)` | no |  | Becomes an alias that still resolves |
| `survivorship` | `JSON` | no |  | Field → chosen source and rule |
| `repointed` | `JSON` | no |  | Table → count of references re-pointed |
| `approved_by` → `app_user` | `BINARY(16)` | no |  |  |
| `second_approver_id` → `app_user` | `BINARY(16)` | yes |  | Required for records with certificates/results |
| `merged_at` | `DATETIME(6)` | no |  |  |
| `unmerge_deadline` | `DATE` | no |  |  |
| `unmerged_at` | `DATETIME(6)` | yes |  |  |
| `unmerged_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, entity_kind, merged_id)

- Check `four_eyes`: `second_approver_id IS NULL OR second_approver_id <> approved_by`

<a id="registry-data_quality_rule"></a>
## `data_quality_rule`

Data-quality rule feeding the DQI components (completeness, uniqueness, validity, timeliness, consistency, verification)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `mdm` |
| Origin | ceda |
| Retention | `RS-MDM` |
| Requirements | FR-CMD-104 |
| Pages | CMD-16, ADM-17 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `dimension` | `VARCHAR(32)` | no |  | values: completeness, uniqueness, validity, timeliness, consistency, verification |
| `entity` | `VARCHAR(64)` | no |  | CEDA entity checked |
| `expression` | `TEXT` | no |  | Rule DSL or SQL template over the semantic layer |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, rule_key, version)

<a id="registry-data_quality_issue"></a>
## `data_quality_issue` (registry)

Open data-quality issue on a record (validation failure, probable duplicate, stale dataset, conflict)

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `mdm` |
| Origin | ceda |
| Retention | `RS-MDM` |
| Requirements | FR-CMD-103, FR-CMD-104 |
| Pages | CMD-16, ADM-17, CMD-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `dimension` | `VARCHAR(32)` | no |  | values: completeness, uniqueness, validity, timeliness, consistency, verification |
| `record_kind` | `VARCHAR(64)` | no |  |  |
| `record_id` | `BINARY(16)` | yes |  |  |
| `detail` | `VARCHAR(1000)` | no |  |  |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `detected_at` | `DATETIME(6)` | no |  |  |
| `owner_user_id` | `BINARY(16)` | yes |  |  |
| `resolved_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, rule_key, status)

<a id="ops-data_quality_issue"></a>
## `data_quality_issue` (ops)

Open data-quality issue on a record (validation failure, probable duplicate, stale dataset, conflict)

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `mdm` |
| Origin | ceda |
| Retention | `RS-MDM` |
| Requirements | FR-CMD-103, FR-CMD-104 |
| Pages | CMD-16, ADM-17, CMD-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `dimension` | `VARCHAR(32)` | no |  | values: completeness, uniqueness, validity, timeliness, consistency, verification |
| `record_kind` | `VARCHAR(64)` | no |  |  |
| `record_id` | `BINARY(16)` | yes |  |  |
| `detail` | `VARCHAR(1000)` | no |  |  |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `detected_at` | `DATETIME(6)` | no |  |  |
| `owner_user_id` | `BINARY(16)` | yes |  |  |
| `resolved_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, rule_key, status)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="registry-dataset_freshness"></a>
## `dataset_freshness`

Last data received per institution per dataset (stale institutions shown, not hidden)

| | |
|---|---|
| Zone | registry |
| Kind | projection |
| Classification | internal |
| History | none |
| Scope | owned |
| Module | `mdm` |
| Origin | ceda |
| Retention | `RS-MDM` |
| Requirements | FR-CMD-104 |
| Pages | CMD-101, CMD-103, CMD-16 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `dataset` | `VARCHAR(32)` | no |  | values: enrolment, attendance, staffing, curriculum_coverage, results, safety, fees, compliance, finance, registers |
| `last_received_at` | `DATETIME(6)` | yes |  |  |
| `expected_interval_hours` | `SMALLINT` | no |  |  |
| `is_stale` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, dataset)

