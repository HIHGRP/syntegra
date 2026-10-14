# GOV — Governance hierarchy, configuration, reference data, policy and workflow

The ten-level governance hierarchy (global → country → state → LGA → network → institution → campus → unit → class/programme → learner) as effective-dated scope nodes with a closure table for subtree tests (MFS §2.3, §16.2), the layered configuration model (global core → country → state → network → institution → department, Book 3 §7), jurisdiction code lists, the Ministry policy and rule engine with exceptions (Book 3 §14) and the universal workflow engine (Book 3 §11). Every module uses these engines; none builds its own (MFS §4.2).

Module (system of record): `governance` · default zone: **registry** · default retention: `RS-CONFIG`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`scope_node`](#registry-scope_node) | registry | master | internal | effective | Governance hierarchy node (country, state, LGA, network, institution, campus, unit, class/programme) |
| [`scope_closure`](#registry-scope_closure) | registry | projection | internal | none | Ancestor/descendant pairs of the governance hierarchy for fast subtree tests |
| [`config_version`](#registry-config_version) | registry | config | internal | versioned | Versioned configuration document for a layer (country, state, network, institution, department) |
| [`jurisdiction_pack`](#registry-jurisdiction_pack) | registry | config | public | versioned | Versioned jurisdiction pack (statutory references, categories, timescales — e.g. Nigerian safeguarding pack) |
| [`code_list`](#registry-code_list) | registry | reference | public | none | Jurisdiction code list (education levels, attendance codes, ownership, sex, concern categories …) |
| [`code_value`](#registry-code_value) | registry | reference | public | effective | Value of a jurisdiction code list (effective-dated; never deleted) |
| [`translation`](#registry-translation) | registry | config | public | none | Platform or tenant translation and terminology override (UI strings, RTL languages) |
| [`policy_rule`](#registry-policy_rule) | registry | config | internal | versioned | Versioned rule at a governance level (Ministry policy engine) |
| [`policy_rule_test`](#registry-policy_rule_test) | registry | config | internal | none | Unit test of a rule version (given context → expected outcome) |
| [`policy_exception`](#registry-policy_exception) | registry | transaction | internal | lifecycle | Approved, time-boxed exception to a rule (never modifies the rule; evaluated at run time) |
| [`policy_conflict`](#registry-policy_conflict) | registry | event | internal | append | Detected conflict between a lower-level configuration and a higher mandatory rule |
| [`workflow_definition`](#registry-workflow_definition) | registry | config | internal | versioned | Versioned workflow definition (state machine, human steps, SLAs, escalations) |
| [`workflow_instance`](#registry-workflow_instance) | registry | transaction | internal | lifecycle | Running workflow on a subject record |
| [`workflow_instance`](#ops-workflow_instance) | ops | transaction | internal | lifecycle | Running workflow on a subject record |
| [`workflow_task`](#registry-workflow_task) | registry | queue | internal | lifecycle | Human task in a workflow (assignee resolved from role-at-scope, SLA, escalation) |
| [`workflow_task`](#ops-workflow_task) | ops | queue | internal | lifecycle | Human task in a workflow (assignee resolved from role-at-scope, SLA, escalation) |
| [`workflow_transition`](#registry-workflow_transition) | registry | event | internal | append | Transition of a workflow instance (append-only; mirrored in the audit trail) |
| [`workflow_transition`](#ops-workflow_transition) | ops | event | internal | append | Transition of a workflow instance (append-only; mirrored in the audit trail) |

<a id="registry-scope_node"></a>
## `scope_node`

Governance hierarchy node (country, state, LGA, network, institution, campus, unit, class/programme)  

Effective-dated so that LGA boundary changes keep history (MFS §4.4). The path column supports prefix queries; scope_closure answers "is record R inside grant G's subtree" with one indexed lookup.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | effective |
| Scope | none |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-CMD-02, FR-CMD-118, FR-INS-08 |
| Pages | CMD-07, AUT-03 |
| Events | GOV.SCOPE_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `parent_id` → `scope_node` | `BINARY(16)` | yes |  |  |
| `level` | `VARCHAR(32)` | no |  | values: global, country, state, authority, lga, network, institution, campus, faculty, department, programme, class, agency, formation |
| `code` | `VARCHAR(40)` | no |  | Official code, e.g. NG, NG-AB, AB-ABS, AB/SS/0412 |
| `name` | `VARCHAR(300)` | no |  |  |
| `path` | `VARCHAR(512)` | no |  | Materialised path of codes, e.g. NG.AB.ABS.0412 |
| `depth` | `SMALLINT` | no |  |  |
| `ref_kind` | `VARCHAR(32)` | yes |  | Entity the node represents · values: tenant, institution, campus, org_unit, class_group, course_section, programme, network, security_agency, agency_unit |
| `ref_id` | `BINARY(16)` | yes |  | Institution, campus, org unit, class group or course section id (soft) |
| `ownership` | `VARCHAR(32)` | yes |  | Denormalised for oversight filters (public/private) · code list `ownership` |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code, valid_from)
- Index: (tenant_id, path)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-scope_closure"></a>
## `scope_closure`

Ancestor/descendant pairs of the governance hierarchy for fast subtree tests  

Maintained by the governance module in the same transaction as scope_node changes (MFS §16.2).

| | |
|---|---|
| Zone | registry |
| Kind | projection |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-CMD-02 |
| Pages | CMD-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` **PK** | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `ancestor_id` **PK** → `scope_node` | `BINARY(16)` | no |  |  |
| `descendant_id` **PK** → `scope_node` | `BINARY(16)` | no |  |  |
| `depth` | `SMALLINT` | no |  | 0 = self |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, descendant_id, ancestor_id)

<a id="registry-config_version"></a>
## `config_version`

Versioned configuration document for a layer (country, state, network, institution, department)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-ADM-02, FR-ACA-02, FR-ADM-09 |
| Pages | ADM-02, ADM-03, ADM-12, ADM-13 |
| Events | GOV.CONFIG_PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `layer` | `VARCHAR(32)` | no |  | values: global, country, state, network, institution, department |
| `section` | `VARCHAR(40)` | no |  | e.g. levels, identifiers, calendar, branding, languages, messaging, health_index |
| `version` | `INT UNSIGNED` | no |  |  |
| `document` | `JSON` | no |  | Validated against the section's JSON Schema |
| `locked_keys` | `JSON` | yes |  | Keys marked mandatory_below by a higher layer (shown locked with source) |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `effective_from` | `DATE` | no |  |  |
| `published_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, section, version)

<a id="registry-jurisdiction_pack"></a>
## `jurisdiction_pack`

Versioned jurisdiction pack (statutory references, categories, timescales — e.g. Nigerian safeguarding pack)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | none |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-SAF-108, FR-SAF-105, FR-CUR-115 |
| Pages | ADM-02, SAF-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `code` | `VARCHAR(40)` | no |  | e.g. ng-core, ng-safeguarding, uk-kcsie, ib-dp |
| `version` | `INT UNSIGNED` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `country` | `CHAR(2)` | yes |  |  |
| `content` | `JSON` | no |  | Statutory references, categories, timescales, forms |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `effective_from` | `DATE` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code, version)

<a id="registry-code_list"></a>
## `code_list`

Jurisdiction code list (education levels, attendance codes, ownership, sex, concern categories …)

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | public |
| History | none |
| Scope | none |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-ACA-01, FR-ADM-02, FR-LRN-05 |
| Pages | ADM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `code` | `VARCHAR(48)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `pack` | `VARCHAR(40)` | no |  | Jurisdiction pack that seeds the list |
| `is_extensible` | `BOOLEAN` | no |  | Lower layers may add values (never remove) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code)

<a id="registry-code_value"></a>
## `code_value`

Value of a jurisdiction code list (effective-dated; never deleted)

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | public |
| History | effective |
| Scope | none |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-ACA-01 |
| Pages | ADM-02, ACA-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `code_list_id` → `code_list` | `BINARY(16)` | no |  |  |
| `code` | `VARCHAR(32)` | no |  |  |
| `label` | `VARCHAR(300)` | no |  |  |
| `labels_i18n` | `JSON` | yes |  | Translations keyed by BCP 47 tag |
| `parent_code` | `VARCHAR(32)` | yes |  | Hierarchical lists (level → stage) |
| `sort_order` | `SMALLINT` | no |  |  |
| `attributes` | `JSON` | yes |  | e.g. age band for a level, statutory flag for an attendance code |
| `owner_scope_id` → `scope_node` | `BINARY(16)` | yes |  | Layer that added the value (NULL = pack) |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code_list_id, code, valid_from)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-translation"></a>
## `translation`

Platform or tenant translation and terminology override (UI strings, RTL languages)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | none |
| Scope | none |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-ADM-09, NFR-I18N-01 |
| Pages | ADM-12 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `override_scope_id` → `scope_node` | `BINARY(16)` | yes |  | NULL = platform-wide |
| `lang` | `VARCHAR(35)` | no |  |  |
| `msg_key` | `VARCHAR(200)` | no |  |  |
| `text` | `TEXT` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, override_scope_id, lang, msg_key)

<a id="registry-policy_rule"></a>
## `policy_rule`

Versioned rule at a governance level (Ministry policy engine)  

Rule source is the safe expression language of Book 3 §14.1; publication is blocked while any rule test fails.

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-ADM-05, FR-CUR-06, FR-CUR-08, FR-BEH-105, FR-INSP-04 |
| Pages | ADM-06, CUR-05, CUR-08 |
| Events | GOV.POLICY_PUBLISHED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  | e.g. ATT-INST-02, ID-NG-01, G2 |
| `rule_domain` | `VARCHAR(32)` | no |  | values: attendance, curriculum, coverage, teacher_qualification, examination, progression, certification, accreditation, registration, alerting, billing, behaviour, safeguarding, financing, identity, messaging, agents |
| `title` | `VARCHAR(300)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `is_mandatory_below` | `BOOLEAN` | no |  | Lower levels may tighten, never relax |
| `expression` | `MEDIUMTEXT` | no |  | Rule DSL source |
| `parameters` | `JSON` | yes |  | Thresholds and weights |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `effective_from` | `DATE` | no |  |  |
| `effective_to` | `DATE` | yes |  |  |
| `authored_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, rule_key, version)

- Check `four_eyes`: `approved_by IS NULL OR authored_by IS NULL OR approved_by <> authored_by`

<a id="registry-policy_rule_test"></a>
## `policy_rule_test`

Unit test of a rule version (given context → expected outcome)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-ADM-05 |
| Pages | ADM-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `rule_id` → `policy_rule` | `BINARY(16)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `given_context` | `JSON` | no |  |  |
| `expected` | `JSON` | no |  |  |
| `last_result` | `VARCHAR(32)` | yes |  | values: pass, fail, error |
| `last_run_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-policy_exception"></a>
## `policy_exception`

Approved, time-boxed exception to a rule (never modifies the rule; evaluated at run time)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-CUR-105, FR-ACA-112, FR-ACA-02, FR-TIM-03 |
| Pages | CUR-08 |
| Events | GOV.EXCEPTION_APPROVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_id` → `policy_rule` | `BINARY(16)` | no |  |  |
| `subject_kind` | `VARCHAR(40)` | yes |  | Record the exception applies to (teaching_assignment, institution …) |
| `subject_id` | `BINARY(16)` | yes |  |  |
| `reason` | `TEXT` | no |  |  |
| `evidence_document_id` | `BINARY(16)` | yes |  | records zone (soft) |
| `requested_by` → `app_user` | `BINARY(16)` | no |  |  |
| `approved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `start_on` | `DATE` | no |  |  |
| `end_on` | `DATE` | no |  | ≤ 12 months after start |
| `review_on` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, approved, rejected, active, expired, renewed, revoked |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `window`: `end_on >= start_on AND end_on <= start_on + INTERVAL 12 MONTH`
- Check `four_eyes`: `approved_by IS NULL OR approved_by <> requested_by`

<a id="registry-policy_conflict"></a>
## `policy_conflict`

Detected conflict between a lower-level configuration and a higher mandatory rule

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | owned |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-CUR-06, FR-PVT-111 |
| Pages | CUR-08, ADM-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_id` → `policy_rule` | `BINARY(16)` | no |  |  |
| `attempted_by` → `app_user` | `BINARY(16)` | no |  |  |
| `config_section` | `VARCHAR(40)` | yes |  |  |
| `attempted_value` | `JSON` | no |  |  |
| `resolution` | `VARCHAR(32)` | no |  | values: cancelled, exception_requested, revised |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-workflow_definition"></a>
## `workflow_definition`

Versioned workflow definition (state machine, human steps, SLAs, escalations)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-ADM-05, FR-FRM-103, FR-PVT-106 |
| Pages | ADM-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `workflow_key` | `VARCHAR(60)` | no |  | admission, recruitment, safeguarding, procurement, curriculum_version, certificate_issue … |
| `version` | `INT UNSIGNED` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `definition` | `JSON` | no |  | States, transitions, guards, actions, human steps, timers |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, workflow_key, version)

<a id="registry-workflow_instance"></a>
## `workflow_instance` (registry)

Running workflow on a subject record

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-ADM-05 |
| Pages | HOM-03, INS-03 |
| Events | WF.STARTED, WF.COMPLETED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `definition_id` → `workflow_definition` | `BINARY(16)` | yes |  | Definition version the instance runs on (never changes) |
| `subject_kind` | `VARCHAR(40)` | no |  |  |
| `subject_id` | `BINARY(16)` | no |  |  |
| `state` | `VARCHAR(60)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: running, waiting, completed, cancelled, failed |
| `started_by` | `BINARY(16)` | yes |  | Actor (user or service identity) |
| `completed_at` | `DATETIME(6)` | yes |  |  |
| `context` | `JSON` | yes |  | Workflow variables (no special-category content) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, subject_kind, subject_id)

- Soft reference `definition_id` → `workflow_definition` — declared soft

<a id="ops-workflow_instance"></a>
## `workflow_instance` (ops)

Running workflow on a subject record

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-ADM-05 |
| Pages | HOM-03, INS-03 |
| Events | WF.STARTED, WF.COMPLETED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `definition_id` → `workflow_definition` | `BINARY(16)` | yes |  | Definition version the instance runs on (never changes) |
| `subject_kind` | `VARCHAR(40)` | no |  |  |
| `subject_id` | `BINARY(16)` | no |  |  |
| `state` | `VARCHAR(60)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: running, waiting, completed, cancelled, failed |
| `started_by` | `BINARY(16)` | yes |  | Actor (user or service identity) |
| `completed_at` | `DATETIME(6)` | yes |  |  |
| `context` | `JSON` | yes |  | Workflow variables (no special-category content) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, subject_kind, subject_id)

- Soft reference `definition_id` → `workflow_definition` — declared soft
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="registry-workflow_task"></a>
## `workflow_task` (registry)

Human task in a workflow (assignee resolved from role-at-scope, SLA, escalation)

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-COM-111 |
| Pages | HOM-03 |
| Events | WF.TASK_ASSIGNED, WF.TASK_COMPLETED, WF.TASK_ESCALATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `instance_id` → `workflow_instance` | `BINARY(16)` | no |  |  |
| `step_key` | `VARCHAR(60)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `assignee_role` | `VARCHAR(16)` | yes |  | Role code when assigned by role-at-scope |
| `assignee_scope_id` | `BINARY(16)` | yes |  | Scope of the role assignment |
| `assignee_user_id` | `BINARY(16)` | yes |  | Resolved user |
| `approval_type` | `VARCHAR(32)` | yes |  | values: single, any_of, all_of, sequential |
| `due_at` | `DATETIME(6)` | yes |  |  |
| `reminded_at` | `DATETIME(6)` | yes |  | 75% of SLA reminder |
| `escalated_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, claimed, completed, escalated, reassigned, cancelled |
| `decision` | `VARCHAR(40)` | yes |  |  |
| `decided_by` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `external_task_ref` | `VARCHAR(128)` | yes |  | Linked workspace-messaging task (Zenzap) for two-way sync |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, assignee_user_id, status)

<a id="ops-workflow_task"></a>
## `workflow_task` (ops)

Human task in a workflow (assignee resolved from role-at-scope, SLA, escalation)

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `governance` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-COM-111 |
| Pages | HOM-03 |
| Events | WF.TASK_ASSIGNED, WF.TASK_COMPLETED, WF.TASK_ESCALATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `instance_id` → `workflow_instance` | `BINARY(16)` | no |  |  |
| `step_key` | `VARCHAR(60)` | no |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `assignee_role` | `VARCHAR(16)` | yes |  | Role code when assigned by role-at-scope |
| `assignee_scope_id` | `BINARY(16)` | yes |  | Scope of the role assignment |
| `assignee_user_id` | `BINARY(16)` | yes |  | Resolved user |
| `approval_type` | `VARCHAR(32)` | yes |  | values: single, any_of, all_of, sequential |
| `due_at` | `DATETIME(6)` | yes |  |  |
| `reminded_at` | `DATETIME(6)` | yes |  | 75% of SLA reminder |
| `escalated_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, claimed, completed, escalated, reassigned, cancelled |
| `decision` | `VARCHAR(40)` | yes |  |  |
| `decided_by` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `external_task_ref` | `VARCHAR(128)` | yes |  | Linked workspace-messaging task (Zenzap) for two-way sync |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, assignee_user_id, status)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="registry-workflow_transition"></a>
## `workflow_transition` (registry)

Transition of a workflow instance (append-only; mirrored in the audit trail)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-ADM-05 |
| Pages | HOM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `instance_id` → `workflow_instance` | `BINARY(16)` | no |  |  |
| `from_state` | `VARCHAR(60)` | yes |  |  |
| `to_state` | `VARCHAR(60)` | no |  |  |
| `actor` | `BINARY(16)` | yes |  |  |
| `reason` | `TEXT` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-workflow_transition"></a>
## `workflow_transition` (ops)

Transition of a workflow instance (append-only; mirrored in the audit trail)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `governance` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-ADM-05 |
| Pages | HOM-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `instance_id` → `workflow_instance` | `BINARY(16)` | no |  |  |
| `from_state` | `VARCHAR(60)` | yes |  |  |
| `to_state` | `VARCHAR(60)` | no |  |  |
| `actor` | `BINARY(16)` | yes |  |  |
| `reason` | `TEXT` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

