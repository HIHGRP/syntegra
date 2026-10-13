# INT — Intelligence and automation — alerts, investigations, improvement, recommendations, early warning, model register, agents, assistant and planning

The intelligence engine's operational records (MFS §12, Book 3 §16, §28; FR-CMD-03–10, 101–119, FR-INT-01–06, 101, FR-AGT-101–115, FR-INSP-05–06, FR-WEL-04). Alerts carry what changed, why it matters, evidence, severity, recommended action, owner and due date; they deduplicate and escalate. Follow-the-Problem investigations run Problem → Evidence → Root cause → Intervention → Responsible person → Outcome. AI recommendations and early-warning flags always show finding, evidence, confidence and the human decision, and their outcomes close the loop. Models are registered with purpose, data, excluded features, fairness and oversight. Agents act under service identities with declared tools, limits, kill switch and 24-hour undo; every action is append-only and explained. Features and training sets live in the warehouse (zone dw), never in operational tables.

Module (system of record): `intelligence` · default zone: **ops** · default retention: `RS-INTEL`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`alert_rule`](#registry-alert_rule) | registry | config | internal | versioned | Alert rule (indicator, threshold, severity, owner role, due, escalation chain) — policy-engine backed |
| [`alert`](#registry-alert) | registry | transaction | internal | lifecycle | Alert instance (what changed, why it matters, evidence, severity, recommended action, owner, due date) — deduplicated and escalated |
| [`alert`](#ops-alert) | ops | transaction | internal | lifecycle | Alert instance (what changed, why it matters, evidence, severity, recommended action, owner, due date) — deduplicated and escalated |
| [`alert_event`](#registry-alert_event) | registry | event | internal | append | History of an alert (raised, acknowledged, escalated, snoozed, resolved) — append-only |
| [`alert_event`](#ops-alert_event) | ops | event | internal | append | History of an alert (raised, acknowledged, escalated, snoozed, resolved) — append-only |
| [`investigation`](#registry-investigation) | registry | transaction | confidential | lifecycle | Follow-the-Problem investigation (Problem → Evidence → Root cause → Intervention → Responsible person → Outcome) |
| [`investigation`](#ops-investigation) | ops | transaction | confidential | lifecycle | Follow-the-Problem investigation (Problem → Evidence → Root cause → Intervention → Responsible person → Outcome) |
| [`improvement_plan`](#ops-improvement_plan) | ops | transaction | confidential | lifecycle | Improvement workspace (problem, evidence, contributing indicators, actions, owner, review and outcome vs target and counterfactual) |
| [`recommendation`](#ops-recommendation) | ops | transaction | confidential | lifecycle | AI recommendation awaiting a human decision (finding, evidence, confidence, recommendation, decision, outcome) |
| [`risk_flag`](#ops-risk_flag) | ops | transaction | confidential | lifecycle | Learner early-warning flag (dropout, attendance, behaviour, academic decline, wellbeing, SEND support gap) with explanation |
| [`ai_model`](#platform-ai_model) | platform | master | internal | lifecycle | Model register entry (purpose, owner, data, excluded features, oversight level) — AIX-03 |
| [`ai_model_version`](#platform-ai_model_version) | platform | config | internal | versioned | Model version with metrics, fairness gaps, drift, approval and review date (MLflow-tracked) |
| [`model_deployment`](#registry-model_deployment) | registry | config | internal | effective | Approval of a model version for use in a state (state DPO and ministry sign-off) |
| [`agent_template`](#platform-agent_template) | platform | config | internal | versioned | Agent library template (16 shipped agents) — triggers, tools, maximum autonomy, limits |
| [`agent`](#registry-agent) | registry | config | internal | lifecycle | Configured automation agent (owner, service identity, level, scope, limits, approval, status) |
| [`agent`](#ops-agent) | ops | config | internal | lifecycle | Configured automation agent (owner, service identity, level, scope, limits, approval, status) |
| [`agent_action`](#registry-agent_action) | registry | event | internal | append | Action taken or proposed by an agent — trigger, evidence, rule, tool call, outcome, owner ("Agent X for Owner Y"); append-only |
| [`agent_action`](#ops-agent_action) | ops | event | internal | append | Action taken or proposed by an agent — trigger, evidence, rule, tool call, outcome, owner ("Agent X for Owner Y"); append-only |
| [`assistant_conversation`](#ops-assistant_conversation) | ops | transaction | confidential | lifecycle | Education assistant conversation (answers executed as the user; every figure cited) — never used for training |
| [`llm_call_log`](#ops-llm_call_log) | ops | event | confidential | append | LLM gateway call log (prompt and output, PII-minimised; 30-day retention; residency-aware) |
| [`document_extraction`](#records-document_extraction) | records | transaction | confidential | lifecycle | Document-intelligence extraction (forms, PDFs, certificates, transcripts, invoices) with per-field confidence and human validation |
| [`planning_scenario`](#registry-planning_scenario) | registry | transaction | internal | versioned | Planning scenario (assumptions, capacity, forecast, gap, cost, comparison; university places, skills demand, ICT) |
| [`resource_proposal`](#registry-resource_proposal) | registry | transaction | internal | lifecycle | Resource-imbalance proposal for human decision (never reallocated automatically) |
| [`practice_share`](#registry-practice_share) | registry | transaction | internal | lifecycle | What's working — successful practice, intervention or outstanding teacher recognition (teacher consent; never a public ranking) |

<a id="registry-alert_rule"></a>
## `alert_rule`

Alert rule (indicator, threshold, severity, owner role, due, escalation chain) — policy-engine backed

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-CMD-04, FR-CUR-12, FR-INS-06 |
| Pages | CMD-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `policy_rule_id` → `policy_rule` | `BINARY(16)` | yes |  |  |
| `metric_id` | `VARCHAR(40)` | yes |  | Semantic-layer metric |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `owner_role` | `VARCHAR(16)` | no |  |  |
| `due_days` | `SMALLINT` | no |  |  |
| `escalation` | `JSON` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, rule_key, version)

<a id="registry-alert"></a>
## `alert` (registry)

Alert instance (what changed, why it matters, evidence, severity, recommended action, owner, due date) — deduplicated and escalated

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | appj |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-04, FR-CMD-03, FR-CMD-115, FR-INS-06, FR-CUR-12, FR-CER-10, FR-CER-113, FR-OPS-03, FR-CMD-103 |
| Pages | CMD-09, CMD-10, HOM-01, CMD-15, CMD-101 |
| Events | ALERT.RAISED, ALERT.ESCALATED, ALERT.RESOLVED, ALERT.SNOOZED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `priority` | `VARCHAR(32)` | no |  | values: p1, p2, p3, information |
| `title` | `VARCHAR(300)` | no |  |  |
| `what_changed` | `TEXT` | no |  |  |
| `why_it_matters` | `TEXT` | no |  |  |
| `evidence` | `JSON` | no |  |  |
| `recommended_action` | `TEXT` | yes |  |  |
| `subject_kind` | `VARCHAR(40)` | no |  |  |
| `subject_id` | `BINARY(16)` | no |  |  |
| `owner_role` | `VARCHAR(16)` | no |  |  |
| `owner_user_id` | `BINARY(16)` | yes |  |  |
| `due_at` | `DATETIME(6)` | no |  |  |
| `dedupe_key` | `VARCHAR(160)` | no |  | rule:subject while open |
| `escalation_level` | `SMALLINT` | no |  |  |
| `snoozed_until` | `DATETIME(6)` | yes |  |  |
| `investigation_id` → `investigation` | `BINARY(16)` | yes |  |  |
| `resolved_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, acknowledged, in_progress, snoozed, escalated, resolved, dismissed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, dedupe_key, status)
- Index: (tenant_id, owner_user_id, status)
- Index: (tenant_id, due_at)

<a id="ops-alert"></a>
## `alert` (ops)

Alert instance (what changed, why it matters, evidence, severity, recommended action, owner, due date) — deduplicated and escalated

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | appj |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-04, FR-CMD-03, FR-CMD-115, FR-INS-06, FR-CUR-12, FR-CER-10, FR-CER-113, FR-OPS-03, FR-CMD-103 |
| Pages | CMD-09, CMD-10, HOM-01, CMD-15, CMD-101 |
| Events | ALERT.RAISED, ALERT.ESCALATED, ALERT.RESOLVED, ALERT.SNOOZED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `priority` | `VARCHAR(32)` | no |  | values: p1, p2, p3, information |
| `title` | `VARCHAR(300)` | no |  |  |
| `what_changed` | `TEXT` | no |  |  |
| `why_it_matters` | `TEXT` | no |  |  |
| `evidence` | `JSON` | no |  |  |
| `recommended_action` | `TEXT` | yes |  |  |
| `subject_kind` | `VARCHAR(40)` | no |  |  |
| `subject_id` | `BINARY(16)` | no |  |  |
| `owner_role` | `VARCHAR(16)` | no |  |  |
| `owner_user_id` | `BINARY(16)` | yes |  |  |
| `due_at` | `DATETIME(6)` | no |  |  |
| `dedupe_key` | `VARCHAR(160)` | no |  | rule:subject while open |
| `escalation_level` | `SMALLINT` | no |  |  |
| `snoozed_until` | `DATETIME(6)` | yes |  |  |
| `investigation_id` → `investigation` | `BINARY(16)` | yes |  |  |
| `resolved_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, acknowledged, in_progress, snoozed, escalated, resolved, dismissed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, dedupe_key, status)
- Index: (tenant_id, owner_user_id, status)
- Index: (tenant_id, due_at)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="registry-alert_event"></a>
## `alert_event` (registry)

History of an alert (raised, acknowledged, escalated, snoozed, resolved) — append-only

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-04 |
| Pages | CMD-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `alert_id` → `alert` | `BINARY(16)` | no |  |  |
| `event_kind` | `VARCHAR(32)` | no |  | values: raised, acknowledged, assigned, escalated, snoozed, commented, resolved, reopened |
| `actor` | `BINARY(16)` | yes |  |  |
| `note` | `VARCHAR(1000)` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-alert_event"></a>
## `alert_event` (ops)

History of an alert (raised, acknowledged, escalated, snoozed, resolved) — append-only

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-04 |
| Pages | CMD-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `alert_id` → `alert` | `BINARY(16)` | no |  |  |
| `event_kind` | `VARCHAR(32)` | no |  | values: raised, acknowledged, assigned, escalated, snoozed, commented, resolved, reopened |
| `actor` | `BINARY(16)` | yes |  |  |
| `note` | `VARCHAR(1000)` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-investigation"></a>
## `investigation` (registry)

Follow-the-Problem investigation (Problem → Evidence → Root cause → Intervention → Responsible person → Outcome)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-05, FR-CMD-118, FR-CMD-119 |
| Pages | CMD-08, CMD-104 |
| Events | INV.OPENED, INV.ACTION_ADDED, INV.CLOSED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `stage` | `VARCHAR(32)` | no |  | values: problem, evidence, root_cause, intervention, responsible_person, outcome |
| `problem` | `TEXT` | no |  |  |
| `evidence` | `JSON` | yes |  |  |
| `root_cause` | `TEXT` | yes |  |  |
| `intervention_ref` | `BINARY(16)` | yes |  | Intervention or corrective action |
| `responsible_user_id` | `BINARY(16)` | yes |  | Required before advancing to outcome |
| `due_on` | `DATE` | yes |  |  |
| `outcome` | `TEXT` | yes |  |  |
| `owner_user_id` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `responsible_before_outcome`: `stage <> 'outcome' OR (responsible_user_id IS NOT NULL AND due_on IS NOT NULL)`

<a id="ops-investigation"></a>
## `investigation` (ops)

Follow-the-Problem investigation (Problem → Evidence → Root cause → Intervention → Responsible person → Outcome)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-05, FR-CMD-118, FR-CMD-119 |
| Pages | CMD-08, CMD-104 |
| Events | INV.OPENED, INV.ACTION_ADDED, INV.CLOSED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `stage` | `VARCHAR(32)` | no |  | values: problem, evidence, root_cause, intervention, responsible_person, outcome |
| `problem` | `TEXT` | no |  |  |
| `evidence` | `JSON` | yes |  |  |
| `root_cause` | `TEXT` | yes |  |  |
| `intervention_ref` | `BINARY(16)` | yes |  | Intervention or corrective action |
| `responsible_user_id` | `BINARY(16)` | yes |  | Required before advancing to outcome |
| `due_on` | `DATE` | yes |  |  |
| `outcome` | `TEXT` | yes |  |  |
| `owner_user_id` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `responsible_before_outcome`: `stage <> 'outcome' OR (responsible_user_id IS NOT NULL AND due_on IS NOT NULL)`

<a id="ops-improvement_plan"></a>
## `improvement_plan`

Improvement workspace (problem, evidence, contributing indicators, actions, owner, review and outcome vs target and counterfactual)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-INSP-05, FR-INSP-06 |
| Pages | INS-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` | `BINARY(16)` | no |  | Registry institution |
| `problem` | `TEXT` | no |  |  |
| `contributing_indicators` | `JSON` | yes |  |  |
| `actions` | `JSON` | no |  |  |
| `owner_user_id` | `BINARY(16)` | no |  |  |
| `review_on` | `DATE` | no |  |  |
| `target` | `JSON` | no |  |  |
| `outcome` | `JSON` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, active, under_review, completed, closed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-recommendation"></a>
## `recommendation`

AI recommendation awaiting a human decision (finding, evidence, confidence, recommendation, decision, outcome)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | appj |
| Retention | `RS-INTEL` |
| Requirements | FR-INT-02, FR-CMD-07, FR-CMD-117 |
| Pages | AIX-01, CMD-13 |
| Events | AI.RECOMMENDATION_DECIDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `model_version_id` | `BINARY(16)` | no |  | Platform model version (soft) |
| `kind` | `VARCHAR(32)` | no |  | values: intervention, cover, fee_match, resource_reallocation, curriculum_fix, data_fix, seating, recognition |
| `subject_kind` | `VARCHAR(40)` | no |  |  |
| `subject_id` | `BINARY(16)` | no |  |  |
| `finding` | `TEXT` | no |  |  |
| `evidence` | `JSON` | no |  | Top factors (SHAP) and source records |
| `confidence` | `DECIMAL(7,6)` | no |  |  |
| `recommendation` | `TEXT` | no |  |  |
| `decision` | `VARCHAR(32)` | yes |  | values: accepted, modified, dismissed |
| `decision_reason` | `VARCHAR(1000)` | yes |  | Required for dismissals |
| `decided_by` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `outcome` | `JSON` | yes |  | Closed-loop outcome |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-risk_flag"></a>
## `risk_flag`

Learner early-warning flag (dropout, attendance, behaviour, academic decline, wellbeing, SEND support gap) with explanation

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner's institution |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-WEL-04 |
| Pages | INT-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `flag_kind` | `VARCHAR(32)` | no |  | values: dropout, attendance, behaviour, academic_decline, wellbeing, send_support_gap |
| `probability` | `DECIMAL(7,6)` | no |  | Calibrated |
| `explanation` | `JSON` | no |  | Factors; protected characteristics excluded |
| `model_version_id` | `BINARY(16)` | no |  |  |
| `scored_on` | `DATE` | no |  |  |
| `recommendation_id` → `recommendation` | `BINARY(16)` | yes |  |  |
| `dismissed_reason` | `VARCHAR(500)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: new, reviewed, actioned, dismissed, expired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, learner_id, flag_kind)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="platform-ai_model"></a>
## `ai_model`

Model register entry (purpose, owner, data, excluded features, oversight level) — AIX-03

| | |
|---|---|
| Zone | platform |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-INT-04, FR-AGT-115, FR-INT-06 |
| Pages | AIX-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `code` | `VARCHAR(40)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `purpose` | `TEXT` | no |  |  |
| `owner` | `VARCHAR(200)` | no |  |  |
| `training_data` | `TEXT` | no |  |  |
| `excluded_features` | `JSON` | no |  | Protected characteristics excluded from learner-risk features |
| `oversight_level` | `VARCHAR(32)` | no |  | values: advisory, human_in_loop, human_on_loop |
| `dpia_document_ref` | `VARCHAR(200)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (code)

<a id="platform-ai_model_version"></a>
## `ai_model_version`

Model version with metrics, fairness gaps, drift, approval and review date (MLflow-tracked)

| | |
|---|---|
| Zone | platform |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-INT-04 |
| Pages | AIX-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `model_id` → `ai_model` | `BINARY(16)` | no |  |  |
| `version_label` | `VARCHAR(32)` | no |  |  |
| `artifact_uri` | `VARCHAR(500)` | no |  |  |
| `metrics` | `JSON` | no |  |  |
| `fairness` | `JSON` | no |  |  |
| `drift` | `JSON` | yes |  |  |
| `approved_by` → `platform_user` | `BINARY(16)` | yes |  |  |
| `review_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (model_id, version_label)

<a id="registry-model_deployment"></a>
## `model_deployment`

Approval of a model version for use in a state (state DPO and ministry sign-off)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | effective |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-INT-04, FR-INT-06 |
| Pages | AIX-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `model_version_id` | `BINARY(16)` | no |  | Platform model version (soft) |
| `approved_by` → `app_user` | `BINARY(16)` | no |  |  |
| `conditions` | `TEXT` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="platform-agent_template"></a>
## `agent_template`

Agent library template (16 shipped agents) — triggers, tools, maximum autonomy, limits

| | |
|---|---|
| Zone | platform |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-AGT-105, FR-AGT-103 |
| Pages | AGT-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `code` | `VARCHAR(40)` | no |  | register_agent, coverage_agent, fee_agent … |
| `name` | `VARCHAR(300)` | no |  |  |
| `watches` | `TEXT` | no |  |  |
| `tools` | `JSON` | no |  | Declared typed commands |
| `max_level` | `VARCHAR(32)` | no |  | values: a0, a1, a2, a3 |
| `human_only_actions` | `JSON` | no |  | Hard-wired consequential decisions (cannot exceed A1) |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (code, version)

<a id="registry-agent"></a>
## `agent` (registry)

Configured automation agent (owner, service identity, level, scope, limits, approval, status)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | appj |
| Retention | `RS-INTEL` |
| Requirements | FR-AGT-101, FR-AGT-102, FR-AGT-106, FR-AGT-107, FR-AGT-111, FR-AGT-112, FR-AGT-110 |
| Pages | AGT-102, AGT-103 |
| Events | AGT.PAUSED, AGT.LEVEL_LOWERED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `template_code` | `VARCHAR(40)` | no |  |  |
| `template_version` | `INT UNSIGNED` | no |  |  |
| `service_identity_id` | `BINARY(16)` | no |  | Registry service identity |
| `owner_user_id` | `BINARY(16)` | no |  |  |
| `level` | `VARCHAR(32)` | no |  | values: a0, a1, a2, a3 |
| `state_max_level` | `VARCHAR(32)` | no |  | Institutions may only lower · values: a0, a1, a2, a3 |
| `triggers` | `JSON` | no |  |  |
| `limits` | `JSON` | no |  | Messages, cost, records touched per day |
| `sandbox_result` | `JSON` | yes |  | Simulation against last month's data |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `head_approved_by` | `BINARY(16)` | yes |  | Required for A2 and above |
| `next_reapproval_on` | `DATE` | yes |  | Quarterly |
| `error_rate` | `DECIMAL(7,6)` | yes |  |  |
| `paused_at` | `DATETIME(6)` | yes |  |  |
| `paused_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, sandbox, awaiting_approval, active, paused, level_lowered, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-agent"></a>
## `agent` (ops)

Configured automation agent (owner, service identity, level, scope, limits, approval, status)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | appj |
| Retention | `RS-INTEL` |
| Requirements | FR-AGT-101, FR-AGT-102, FR-AGT-106, FR-AGT-107, FR-AGT-111, FR-AGT-112, FR-AGT-110 |
| Pages | AGT-102, AGT-103 |
| Events | AGT.PAUSED, AGT.LEVEL_LOWERED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `template_code` | `VARCHAR(40)` | no |  |  |
| `template_version` | `INT UNSIGNED` | no |  |  |
| `service_identity_id` | `BINARY(16)` | no |  | Registry service identity |
| `owner_user_id` | `BINARY(16)` | no |  |  |
| `level` | `VARCHAR(32)` | no |  | values: a0, a1, a2, a3 |
| `state_max_level` | `VARCHAR(32)` | no |  | Institutions may only lower · values: a0, a1, a2, a3 |
| `triggers` | `JSON` | no |  |  |
| `limits` | `JSON` | no |  | Messages, cost, records touched per day |
| `sandbox_result` | `JSON` | yes |  | Simulation against last month's data |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `head_approved_by` | `BINARY(16)` | yes |  | Required for A2 and above |
| `next_reapproval_on` | `DATE` | yes |  | Quarterly |
| `error_rate` | `DECIMAL(7,6)` | yes |  |  |
| `paused_at` | `DATETIME(6)` | yes |  |  |
| `paused_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, sandbox, awaiting_approval, active, paused, level_lowered, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="registry-agent_action"></a>
## `agent_action` (registry)

Action taken or proposed by an agent — trigger, evidence, rule, tool call, outcome, owner ("Agent X for Owner Y"); append-only

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `intelligence` |
| Origin | appj |
| Retention | `RS-AUDIT` |
| Partitioning | range_month on `occurred_at` |
| Requirements | FR-AGT-104, FR-AGT-108, FR-AGT-109, FR-AGT-113, FR-AGT-114 |
| Pages | AGT-104, AGT-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `agent_id` → `agent` | `BINARY(16)` | no |  |  |
| `owner_user_id` | `BINARY(16)` | no |  |  |
| `trigger_detail` | `JSON` | no |  |  |
| `evidence` | `JSON` | no |  |  |
| `rule_applied` | `VARCHAR(200)` | yes |  |  |
| `tool` | `VARCHAR(64)` | no |  |  |
| `parameters` | `JSON` | no |  | Typed, validated parameters (retrieved text is never executed) |
| `level` | `VARCHAR(32)` | no |  | values: a0, a1, a2, a3 |
| `outcome` | `VARCHAR(32)` | no |  | values: proposed, executed, held_paused, refused_policy, failed, undone |
| `explanation` | `TEXT` | no |  |  |
| `undo_until` | `DATETIME(6)` | yes |  | 24-hour undo for reversible A2 actions |
| `undone_action_id` | `BINARY(16)` | yes |  | Undo record for a previous action |
| `occurred_at` **PK** | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `agent_id` → `agent` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

<a id="ops-agent_action"></a>
## `agent_action` (ops)

Action taken or proposed by an agent — trigger, evidence, rule, tool call, outcome, owner ("Agent X for Owner Y"); append-only

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `intelligence` |
| Origin | appj |
| Retention | `RS-AUDIT` |
| Partitioning | range_month on `occurred_at` |
| Requirements | FR-AGT-104, FR-AGT-108, FR-AGT-109, FR-AGT-113, FR-AGT-114 |
| Pages | AGT-104, AGT-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `agent_id` → `agent` | `BINARY(16)` | no |  |  |
| `owner_user_id` | `BINARY(16)` | no |  |  |
| `trigger_detail` | `JSON` | no |  |  |
| `evidence` | `JSON` | no |  |  |
| `rule_applied` | `VARCHAR(200)` | yes |  |  |
| `tool` | `VARCHAR(64)` | no |  |  |
| `parameters` | `JSON` | no |  | Typed, validated parameters (retrieved text is never executed) |
| `level` | `VARCHAR(32)` | no |  | values: a0, a1, a2, a3 |
| `outcome` | `VARCHAR(32)` | no |  | values: proposed, executed, held_paused, refused_policy, failed, undone |
| `explanation` | `TEXT` | no |  |  |
| `undo_until` | `DATETIME(6)` | yes |  | 24-hour undo for reversible A2 actions |
| `undone_action_id` | `BINARY(16)` | yes |  | Undo record for a previous action |
| `occurred_at` **PK** | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `agent_id` → `agent` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

<a id="ops-assistant_conversation"></a>
## `assistant_conversation`

Education assistant conversation (answers executed as the user; every figure cited) — never used for training

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-AI-LOG` |
| Requirements | FR-INT-01, FR-INT-06 |
| Pages | HOM-06 |
| Events | AI.QUERY |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `user_id` | `BINARY(16)` | no |  |  |
| `title` | `VARCHAR(200)` | yes |  |  |
| `messages` | `JSON` | no |  | Turns with citations (records, time window, record count, DQI) |
| `expires_at` | `DATETIME(6)` | no |  | 30-day retention |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-llm_call_log"></a>
## `llm_call_log`

LLM gateway call log (prompt and output, PII-minimised; 30-day retention; residency-aware)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-AI-LOG` |
| Partitioning | range_day on `called_at` |
| Requirements | FR-INT-06, NFR-SEC-101 |
| Pages | AIX-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `caller_kind` | `VARCHAR(32)` | no |  | values: assistant, agent, document_intelligence, other |
| `caller_id` | `BINARY(16)` | no |  |  |
| `model` | `VARCHAR(80)` | no |  |  |
| `region` | `VARCHAR(32)` | no |  |  |
| `prompt_ref` | `VARCHAR(1024)` | no |  | Encrypted object, deleted after 30 days |
| `output_ref` | `VARCHAR(1024)` | yes |  |  |
| `tokens_in` | `INT UNSIGNED` | no |  |  |
| `tokens_out` | `INT UNSIGNED` | no |  |  |
| `called_at` **PK** | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="records-document_extraction"></a>
## `document_extraction`

Document-intelligence extraction (forms, PDFs, certificates, transcripts, invoices) with per-field confidence and human validation

| | |
|---|---|
| Zone | records |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-DOC` |
| Requirements | FR-INT-03, FR-INT-101, FR-PVT-106 |
| Pages | AIX-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `document_id` → `document` | `BINARY(16)` | no |  |  |
| `schema_code` | `VARCHAR(40)` | no |  |  |
| `fields` | `JSON` | no |  | Field → value, confidence |
| `findings` | `JSON` | yes |  | Missing, duplicate, contradictory, expired documents; key dates with reminders |
| `validated_by` | `BINARY(16)` | yes |  | Consequential fields validated by a person |
| `validated_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: pending, auto_accepted, needs_review, verified, rejected |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-planning_scenario"></a>
## `planning_scenario`

Planning scenario (assumptions, capacity, forecast, gap, cost, comparison; university places, skills demand, ICT)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-CMD-08, FR-CMD-116, FR-CUR-112, FR-STF-10 |
| Pages | CMD-14, STF-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `assumptions` | `JSON` | no |  |  |
| `outputs` | `JSON` | yes |  | Forecasts with Monte Carlo intervals |
| `compared_with_ids` | `JSON` | yes |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-resource_proposal"></a>
## `resource_proposal`

Resource-imbalance proposal for human decision (never reallocated automatically)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-07 |
| Pages | CMD-13 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `imbalance_kind` | `VARCHAR(32)` | no |  | values: teachers, classrooms, textbooks, ict, funding |
| `evidence` | `JSON` | no |  |  |
| `proposal` | `TEXT` | no |  |  |
| `decided_by` | `BINARY(16)` | yes |  |  |
| `decision` | `VARCHAR(32)` | yes |  | values: accepted, modified, dismissed |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-practice_share"></a>
## `practice_share`

What's working — successful practice, intervention or outstanding teacher recognition (teacher consent; never a public ranking)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `intelligence` |
| Origin | ceda |
| Retention | `RS-INTEL` |
| Requirements | FR-CMD-09, FR-CMD-117 |
| Pages | CMD-12 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `evidence` | `JSON` | no |  |  |
| `subject_kind` | `VARCHAR(40)` | no |  |  |
| `subject_id` | `BINARY(16)` | no |  |  |
| `consent_given_at` | `DATETIME(6)` | yes |  | Teacher consent before sharing |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

