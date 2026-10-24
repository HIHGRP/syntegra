# RPT — Reporting, semantic layer registry, government returns, scheduled reports and lineage

Reports come from live master records, never re-keyed spreadsheets (FR-RPT-01–06, 101–102). Every metric is defined once in the semantic layer (ceda/model/metrics.yaml is the source; metric_definition is its published, tenant-tunable copy with targets). Report definitions, saved queries and schedules are governed by scope; government returns are generated, validated, reviewed, certified by the head and submitted, with corrections made in the source records. Lineage is generated from the model: every metric → warehouse facts → operational entities.

Module (system of record): `reporting` · default zone: **registry** · default retention: `RS-RPT`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`metric_definition`](#registry-metric_definition) | registry | config | public | versioned | Published semantic-layer metric (definition, formula, grain, source, owner, refresh, target, suppression) |
| [`report_definition`](#registry-report_definition) | registry | config | internal | versioned | Report in the library (standard, statutory or saved builder query) with permission trimming and suppression |
| [`report_schedule`](#registry-report_schedule) | registry | config | internal | lifecycle | Scheduled delivery of a report (recipients, formats, cadence) |
| [`report_export`](#ops-report_export) | ops | event | internal | append | Export of a permitted table, chart or report (Excel/CSV/PDF), logged; bulk exports of confidential data audited |
| [`return_definition`](#registry-return_definition) | registry | config | internal | versioned | Statutory return definition (UBEC census, capitation, exam-body, regulator exports) with validation rules |
| [`return_submission`](#registry-return_submission) | registry | transaction | internal | lifecycle | Return generated from live data, validated, reviewed, head-certified and submitted (Accepted / Queried) |

<a id="registry-metric_definition"></a>
## `metric_definition`

Published semantic-layer metric (definition, formula, grain, source, owner, refresh, target, suppression)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `reporting` |
| Origin | ceda |
| Retention | `RS-RPT` |
| Requirements | FR-RPT-02, FR-RPT-04, FR-CMD-10, FR-CMD-113, FR-CMD-114 |
| Pages | RPT-02, RPT-04, CMD-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `metric_code` | `VARCHAR(40)` | no |  | e.g. ATT-RATE, CUR-COVERAGE |
| `name` | `VARCHAR(300)` | no |  |  |
| `definition` | `JSON` | no |  | From metrics.yaml at the published CEDA version |
| `target` | `DECIMAL(12,4)` | yes |  |  |
| `direction` | `VARCHAR(32)` | no |  | values: higher_is_better, lower_is_better, target_band |
| `label_kind` | `VARCHAR(32)` | no |  | verified, calculated, estimated · values: verified, calculated, estimated |
| `is_equity_indicator` | `BOOLEAN` | no |  | Shown only where jurisdiction policy allows |
| `ceda_version` | `VARCHAR(32)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, metric_code, version)

<a id="registry-report_definition"></a>
## `report_definition`

Report in the library (standard, statutory or saved builder query) with permission trimming and suppression

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `reporting` |
| Origin | ceda |
| Retention | `RS-RPT` |
| Requirements | FR-RPT-01, FR-RPT-02, FR-RPT-102, FR-BEH-114, FR-SAF-106, FR-COM-117, FR-FRM-108 |
| Pages | RPT-01, RPT-02, SAF-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(48)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `report_kind` | `VARCHAR(32)` | no |  | values: standard, statutory, saved_query, board_report, inspection_pack |
| `query` | `JSON` | no |  | Metrics, dimensions, filters over the semantic layer |
| `min_cell_size` | `SMALLINT` | no |  |  |
| `owner_user_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

<a id="registry-report_schedule"></a>
## `report_schedule`

Scheduled delivery of a report (recipients, formats, cadence)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `reporting` |
| Origin | ceda |
| Retention | `RS-RPT` |
| Requirements | FR-RPT-05, FR-CMD-110, FR-SUB-126 |
| Pages | RPT-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `report_definition_id` → `report_definition` | `BINARY(16)` | no |  |  |
| `cron` | `VARCHAR(64)` | no |  |  |
| `recipients` | `JSON` | no |  |  |
| `format` | `VARCHAR(32)` | no |  | values: xlsx, csv, pdf, json |
| `last_run_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-report_export"></a>
## `report_export`

Export of a permitted table, chart or report (Excel/CSV/PDF), logged; bulk exports of confidential data audited

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `reporting` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-RPT-102, FR-RPT-101 |
| Pages | RPT-01, RPT-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `requested_by` | `BINARY(16)` | no |  |  |
| `source` | `VARCHAR(200)` | no |  | Page region, report code or BI connector |
| `format` | `VARCHAR(32)` | no |  | values: xlsx, csv, pdf, json |
| `row_count` | `INT UNSIGNED` | no |  |  |
| `object_key` | `VARCHAR(1024)` | yes |  | Expiring export object |
| `expires_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-return_definition"></a>
## `return_definition`

Statutory return definition (UBEC census, capitation, exam-body, regulator exports) with validation rules

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `reporting` |
| Origin | ceda |
| Retention | `RS-RPT` |
| Requirements | FR-RPT-03, FR-MED-04 |
| Pages | RPT-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `recipient` | `VARCHAR(200)` | no |  |  |
| `spec` | `JSON` | no |  | Datasets, metrics and validation |
| `calendar` | `JSON` | yes |  | Due dates |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

<a id="registry-return_submission"></a>
## `return_submission`

Return generated from live data, validated, reviewed, head-certified and submitted (Accepted / Queried)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `reporting` |
| Origin | ceda |
| Retention | `RS-RPT` |
| Requirements | FR-RPT-03 |
| Pages | RPT-03 |
| Events | RPT.RETURN_SUBMITTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `return_definition_id` → `return_definition` | `BINARY(16)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | yes |  |  |
| `period_label` | `VARCHAR(20)` | no |  |  |
| `generated_at` | `DATETIME(6)` | no |  |  |
| `anomalies` | `JSON` | yes |  | Explained anomalies (Returns Agent draft) |
| `certified_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `certified_at` | `DATETIME(6)` | yes |  |  |
| `submitted_at` | `DATETIME(6)` | yes |  |  |
| `content_hash` | `BINARY(32)` | yes |  |  |
| `recipient_ref` | `VARCHAR(64)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: generated, validated, institution_review, certified, submitted, accepted, queried |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

