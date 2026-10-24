# FIN — Billing, payments, funding, ledger, budgets, procurement and suppliers

The global billing engine (bases, funding models, charge types, versioned rules, runs with preview and approval, learner ledgers, family statements, payment plans and ethical recovery — FR-BIL-01–10), payments and reconciliation (gateways, virtual accounts, idempotent webhooks, allocation, duplicate detection, bank statements, multi-currency — FR-PMT-01–07, 101), and finance (budgets, procurement with three-way match, Supplier 360, double-entry ledger with period close — FR-FIN-01–06). Money is BIGINT minor units with a currency on the row. Ledger entries are append-only (reverse, never edit). Unpaid fees never restrict registers, teaching, assessment, results or record transfer (P9).

Module (system of record): `finance` · default zone: **ops** · default retention: `RS-FIN`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`account`](#ops-account) | ops | master | restricted | lifecycle | Ledger account — learner, family, sponsor or funder account, and general-ledger accounts |
| [`charge_type`](#ops-charge_type) | ops | config | internal | lifecycle | Charge type (tuition, registration, exam, accommodation, transport, meals, uniform, books, ICT, lab, clinical, trips …) with GL account and tax treatment |
| [`billing_rule`](#ops-billing_rule) | ops | config | internal | versioned | Versioned, effective-dated billing rule (conditions, amount, priority, discount stacking); tested before publishing |
| [`billing_run`](#ops-billing_run) | ops | transaction | internal | lifecycle | Billing run with preview, exceptions, approval and issue (no duplicate invoice per learner per period) |
| [`invoice`](#ops-invoice) | ops | transaction | restricted | lifecycle | Invoice to a payer (immutable once issued; credit notes for changes) |
| [`invoice_line`](#ops-invoice_line) | ops | transaction | restricted | append | Invoice line (charge, rule version used, discount and funding applied) |
| [`credit_note`](#ops-credit_note) | ops | transaction | restricted | append | Credit note against an invoice |
| [`funding_source`](#ops-funding_source) | ops | master | internal | lifecycle | Scholarship, bursary, grant, sponsor, capitation, employer funding or loan (budget and per-learner caps) |
| [`funding_award`](#ops-funding_award) | ops | transaction | restricted | effective | Funding awarded to a learner (scholarship, bursary, capitation share) — never double counted |
| [`government_funding_receipt`](#ops-government_funding_receipt) | ops | transaction | internal | lifecycle | Capitation or government grant tranche received, reconciled against learners funded |
| [`payment_plan`](#ops-payment_plan) | ops | transaction | restricted | lifecycle | Payment plan and hardship assessment under the ethical recovery policy |
| [`recovery_policy`](#ops-recovery_policy) | ops | config | internal | versioned | Ethical recovery policy (reminder cadence, payment-plan offers); core education restrictions cannot be configured |
| [`payment`](#ops-payment) | ops | transaction | restricted | lifecycle | Incoming payment (gateway, virtual account, transfer, card, USSD, mobile money, cash, cheque, government, employer, scholarship) |
| [`payment_allocation`](#ops-payment_allocation) | ops | transaction | restricted | append | Allocation of a payment to an invoice (virtual account → reference → payer → heuristic suggestion) |
| [`ledger_entry`](#ops-ledger_entry) | ops | event | restricted | append | Double-entry posting (append-only; reverse, never edit; partitioned by month) |
| [`journal`](#ops-journal) | ops | transaction | restricted | lifecycle | Journal (balanced set of ledger entries) in a fiscal period |
| [`fiscal_period`](#ops-fiscal_period) | ops | config | internal | lifecycle | Fiscal period (open/closed); closed periods accept no postings |
| [`fx_rate`](#ops-fx_rate) | ops | reference | public | append | Exchange rate captured per source and day (local and reporting currency) |
| [`tax_rule`](#ops-tax_rule) | ops | config | public | versioned | Tax rule (VAT 7.5% where applicable, withholding) by charge type and jurisdiction |
| [`bank_statement_line`](#ops-bank_statement_line) | ops | transaction | restricted | lifecycle | Imported bank statement line (MT940/CSV/open banking) reconciled to payments and disbursements |
| [`budget`](#ops-budget) | ops | transaction | internal | versioned | Budget by cost centre and account linked to enrolment and staffing forecasts (approved via workflow) |
| [`supplier`](#ops-supplier) | ops | master | confidential | lifecycle | Supplier 360 master (duplicate detection; call-back verification and dual approval for bank-detail changes) |
| [`requisition`](#ops-requisition) | ops | transaction | internal | lifecycle | Purchase requisition (delegated approval limits; split-purchase detection) |
| [`purchase_order`](#ops-purchase_order) | ops | transaction | internal | lifecycle | Purchase order, goods receipt and three-way match to the supplier invoice |
| [`cost_centre`](#ops-cost_centre) | ops | master | internal | lifecycle | Cost centre of an institution (administration, department, boarding, feeding, estate, ICT, transport, project, welfare) with its budget holder |
| [`budget_line`](#ops-budget_line) | ops | transaction | internal | lifecycle | Approved budget line — cost centre × ledger account × economic code × funding source, with original, revised, committed and actual amounts |
| [`budget_commitment`](#ops-budget_commitment) | ops | transaction | internal | lifecycle | Commitment of a budget line by a requisition, purchase order, imprest, payroll or disbursement (released, spent or cancelled) |
| [`budget_virement`](#ops-budget_virement) | ops | transaction | internal | lifecycle | Virement — budget moved between two lines with a reason, approved by someone other than the requester |
| [`imprest`](#ops-imprest) | ops | transaction | confidential | lifecycle | Imprest — cash advance to a named holder against a budget line, to be retired with receipts by a due date |
| [`imprest_retirement`](#ops-imprest_retirement) | ops | event | confidential | append | Retirement of an imprest — receipts, amount accounted for and cash refunded |

<a id="ops-account"></a>
## `account`

Ledger account — learner, family, sponsor or funder account, and general-ledger accounts

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | appj |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-07, FR-FIN-05 |
| Pages | BIL-03, BIL-04, FIN-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `account_kind` | `VARCHAR(32)` | no |  | values: learner, family, sponsor, funder, general_ledger |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `holder_kind` | `VARCHAR(32)` | yes |  | values: learner, family, guardian, sponsor, funder, government, employer, institution |
| `holder_id` | `BINARY(16)` | yes |  | learner, family, sponsor or funder |
| `currency` | `CHAR(3)` | no |  |  |
| `gl_type` | `VARCHAR(32)` | yes |  | asset, liability, income, expense, equity (GL accounts) · values: asset, liability, income, expense, equity |
| `virtual_account_number` | `VARCHAR(20)` | yes |  | Per-family virtual account for transfers |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)
- Index: (tenant_id, holder_kind, holder_id)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-charge_type"></a>
## `charge_type`

Charge type (tuition, registration, exam, accommodation, transport, meals, uniform, books, ICT, lab, clinical, trips …) with GL account and tax treatment

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-BIL-03, FR-SUB-123 |
| Pages | BIL-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `income_account_id` → `account` | `BINARY(16)` | no |  |  |
| `tax_code` | `VARCHAR(16)` | yes |  |  |
| `is_digital_services_line` | `BOOLEAN` | no |  | Labelled pass-through line for private providers |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-billing_rule"></a>
## `billing_rule`

Versioned, effective-dated billing rule (conditions, amount, priority, discount stacking); tested before publishing

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `finance` |
| Origin | appj |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-01, FR-BIL-02, FR-BIL-04, FR-BIL-05, FR-BIL-08 |
| Pages | BIL-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `rule_key` | `VARCHAR(40)` | no |  |  |
| `charge_type_id` → `charge_type` | `BINARY(16)` | no |  |  |
| `billing_basis` | `VARCHAR(32)` | no |  | values: term, semester, annual, monthly, weekly, course, credit, module, session, hour, exam, registration, learner, family, service, subscription, pay_as_you_go |
| `conditions` | `JSON` | no |  | Institution, campus, programme, course, level, category, residency, scholarship, family … |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `priority` | `SMALLINT` | no |  |  |
| `discount_policy` | `JSON` | yes |  | Sibling/family discounts and stacking |
| `version` | `INT UNSIGNED` | no |  |  |
| `effective_from` | `DATE` | no |  |  |
| `effective_to` | `DATE` | yes |  |  |
| `test_results` | `JSON` | yes |  | Results against sample learners |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, rule_key, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-billing_run"></a>
## `billing_run`

Billing run with preview, exceptions, approval and issue (no duplicate invoice per learner per period)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-06 |
| Pages | BIL-02 |
| Events | BIL.RUN_ISSUED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `period_label` | `VARCHAR(20)` | no |  |  |
| `billing_basis` | `VARCHAR(32)` | no |  | values: term, semester, annual, monthly, weekly, course, credit, module, session, hour, exam, registration, learner, family, service, subscription, pay_as_you_go |
| `learners_in_scope` | `INT UNSIGNED` | no |  |  |
| `exceptions` | `JSON` | yes |  |  |
| `total_amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `issued_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, previewed, running, awaiting_approval, approved, issued, completed, failed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-invoice"></a>
## `invoice`

Invoice to a payer (immutable once issued; credit notes for changes)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | appj |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-06, FR-BIL-07, FR-FRM-104, FR-TIM-104, FR-OPS-101 |
| Pages | BIL-05, BIL-02, BIL-04 |
| Events | BIL.INVOICE_ISSUED, BIL.INVOICE_OVERDUE |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `invoice_number` | `VARCHAR(32)` | no |  |  |
| `billing_run_id` → `billing_run` | `BINARY(16)` | yes |  |  |
| `account_id` → `account` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | yes |  |  |
| `payer_kind` | `VARCHAR(32)` | no |  | values: learner, family, guardian, sponsor, funder, government, employer, institution |
| `payer_id` | `BINARY(16)` | no |  |  |
| `period_label` | `VARCHAR(20)` | yes |  |  |
| `issued_on` | `DATE` | no |  |  |
| `due_on` | `DATE` | no |  |  |
| `total_minor` | `BIGINT` | no |  | (minor units) |
| `balance_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `fx_rate_to_reporting` | `DECIMAL(18,8)` | yes |  | Rate captured per transaction |
| `content_hash` | `BINARY(32)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, issued, part_paid, paid, overdue, credited, void |
| `dedupe_key` | `VARCHAR(120)` | yes |  | learner:period:run — prevents duplicate invoices per learner per period |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, invoice_number)
- Unique: (tenant_id, dedupe_key)
- Index: (tenant_id, learner_id)
- Index: (tenant_id, due_on, status)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-invoice_line"></a>
## `invoice_line`

Invoice line (charge, rule version used, discount and funding applied)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-04, FR-BIL-09 |
| Pages | BIL-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `invoice_id` → `invoice` | `BINARY(16)` | no |  |  |
| `line_no` | `SMALLINT` | no |  |  |
| `charge_type_id` → `charge_type` | `BINARY(16)` | no |  |  |
| `billing_rule_id` → `billing_rule` | `BINARY(16)` | yes |  |  |
| `rule_version` | `INT UNSIGNED` | yes |  |  |
| `description` | `VARCHAR(300)` | no |  |  |
| `gross_minor` | `BIGINT` | no |  | (minor units) |
| `discount_minor` | `BIGINT` | no |  | (minor units) |
| `funded_minor` | `BIGINT` | no |  | Applied funding sources (no double funding) (minor units) |
| `net_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, invoice_id, line_no)

<a id="ops-credit_note"></a>
## `credit_note`

Credit note against an invoice

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-06 |
| Pages | BIL-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `invoice_id` → `invoice` | `BINARY(16)` | no |  |  |
| `credit_number` | `VARCHAR(32)` | no |  |  |
| `reason` | `VARCHAR(500)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `approved_by` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, credit_number)

<a id="ops-funding_source"></a>
## `funding_source`

Scholarship, bursary, grant, sponsor, capitation, employer funding or loan (budget and per-learner caps)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | appj |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-02, FR-BIL-09, FR-HED-06 |
| Pages | BIL-07, BIL-08, HED-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `funding_kind` | `VARCHAR(32)` | no |  | values: government, capitation, scholarship, bursary, grant, sponsorship, employer, loan, instalment |
| `funder_account_id` → `account` | `BINARY(16)` | yes |  |  |
| `budget_minor` | `BIGINT` | yes |  | (minor units) |
| `per_learner_cap_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `priority` | `SMALLINT` | no |  |  |
| `eligibility_rule` | `JSON` | yes |  |  |
| `valid_until` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-funding_award"></a>
## `funding_award`

Funding awarded to a learner (scholarship, bursary, capitation share) — never double counted

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | effective |
| Scope | derived: the learner's institution |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-HED-06, FR-BIL-09 |
| Pages | HED-07, BIL-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `funding_source_id` → `funding_source` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `awarded_by` | `BINARY(16)` | no |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-government_funding_receipt"></a>
## `government_funding_receipt`

Capitation or government grant tranche received, reconciled against learners funded

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-09 |
| Pages | BIL-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `funding_source_id` → `funding_source` | `BINARY(16)` | no |  |  |
| `tranche_label` | `VARCHAR(40)` | no |  |  |
| `amount_due_minor` | `BIGINT` | no |  | (minor units) |
| `amount_received_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `received_on` | `DATE` | yes |  |  |
| `learners_funded` | `INT UNSIGNED` | yes |  |  |
| `reconciliation` | `JSON` | yes |  | Government + student + scholarship + sponsor = total, no double counting |
| `status` | `VARCHAR(32)` | no |  | values: unmatched, matched, part_matched, disputed, reconciled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-payment_plan"></a>
## `payment_plan`

Payment plan and hardship assessment under the ethical recovery policy

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-BIL-10 |
| Pages | BIL-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `account_id` → `account` | `BINARY(16)` | no |  |  |
| `instalments` | `JSON` | no |  |  |
| `hardship_assessment` | `MEDIUMBLOB` | yes | special | Household circumstances (encrypted) |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, active, under_review, completed, closed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-recovery_policy"></a>
## `recovery_policy`

Ethical recovery policy (reminder cadence, payment-plan offers); core education restrictions cannot be configured

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-BIL-10, FR-ASM-07 |
| Pages | BIL-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `version` | `INT UNSIGNED` | no |  |  |
| `steps` | `JSON` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `no_core_restriction`: `JSON_SEARCH(`steps`, 'one', 'restrict_core_education') IS NULL`

<a id="ops-payment"></a>
## `payment`

Incoming payment (gateway, virtual account, transfer, card, USSD, mobile money, cash, cheque, government, employer, scholarship)  

Raw card data is never handled (hosted fields/redirect, PCI DSS SAQ-A). Receipts only after gateway confirmation.

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | appj |
| Retention | `RS-FIN` |
| Requirements | FR-PMT-01, FR-PMT-02, FR-PMT-03, FR-PMT-05, FR-PMT-07, FR-PMT-101 |
| Pages | PMT-01, PMT-03 |
| Events | PMT.RECEIVED, PMT.ALLOCATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `method` | `VARCHAR(32)` | no |  | values: bank_transfer, virtual_account, card, direct_debit, mobile_money, ussd, gateway, remita, cash, cheque, government, employer, scholarship |
| `gateway` | `VARCHAR(32)` | yes |  |  |
| `gateway_ref` | `VARCHAR(128)` | yes |  | Hard duplicate check |
| `payer_name` | `VARCHAR(200)` | yes |  |  |
| `payer_contact_hmac` | `BINARY(32)` | yes |  | Soft duplicate check (payer + amount within 10 minutes) |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `fx_rate_to_reporting` | `DECIMAL(18,8)` | yes |  |  |
| `received_at` | `DATETIME(6)` | no |  |  |
| `confirmed_at` | `DATETIME(6)` | yes |  |  |
| `receipt_number` | `VARCHAR(32)` | yes |  |  |
| `allocation_status` | `VARCHAR(32)` | no |  | values: unallocated, suggested, part_allocated, allocated |
| `possible_duplicate_of_id` → `payment` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: pending, confirmed, failed, refunded, held_duplicate |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, gateway_ref)
- Unique: (tenant_id, receipt_number)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-payment_allocation"></a>
## `payment_allocation`

Allocation of a payment to an invoice (virtual account → reference → payer → heuristic suggestion)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-PMT-04 |
| Pages | PMT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `payment_id` → `payment` | `BINARY(16)` | no |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `method` | `VARCHAR(32)` | no |  | values: virtual_account, reference, payer_contact, heuristic, manual |
| `confidence` | `DECIMAL(7,6)` | yes |  | Fee Agent allocates only ≥ 0.95; below that it suggests |
| `allocated_by` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-ledger_entry"></a>
## `ledger_entry`

Double-entry posting (append-only; reverse, never edit; partitioned by month)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `finance` |
| Origin | appj |
| Retention | `RS-FIN` |
| Partitioning | range_month on `posted_on` |
| Requirements | FR-FIN-05, FR-BIL-07, FR-STF-09 |
| Pages | BIL-03, FIN-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `journal_id` → `journal` | `BINARY(16)` | no |  |  |
| `account_id` → `account` | `BINARY(16)` | no |  |  |
| `posted_on` **PK** | `DATE` | no |  |  |
| `debit_minor` | `BIGINT` | no |  | (minor units) |
| `credit_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `source_kind` | `VARCHAR(40)` | no |  | invoice, payment, payroll_run, credit_note, journal |
| `source_id` | `BINARY(16)` | no |  |  |
| `rule_versions` | `JSON` | yes |  | Billing rule versions referenced |
| `reverses_id` | `BINARY(16)` | yes |  | Entry this one reverses |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, account_id, posted_on)

- Soft reference `journal_id` → `journal` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)
- Soft reference `account_id` → `account` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

- Check `one_side`: `(debit_minor = 0) <> (credit_minor = 0)`

<a id="ops-journal"></a>
## `journal`

Journal (balanced set of ledger entries) in a fiscal period

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-FIN-05, FR-FIN-06 |
| Pages | FIN-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `journal_number` | `VARCHAR(32)` | no |  |  |
| `fiscal_period_id` → `fiscal_period` | `BINARY(16)` | no |  |  |
| `description` | `VARCHAR(500)` | no |  |  |
| `posted_by` | `BINARY(16)` | no |  |  |
| `exported_at` | `DATETIME(6)` | yes |  | Exported to an external ERP/IFMIS where it is the ledger of record |
| `status` | `VARCHAR(32)` | no |  | values: draft, posted, reversed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, journal_number)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-fiscal_period"></a>
## `fiscal_period`

Fiscal period (open/closed); closed periods accept no postings

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-FIN-05 |
| Pages | FIN-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(10)` | no |  | YYYY-MM |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | no |  |  |
| `closed_at` | `DATETIME(6)` | yes |  |  |
| `closed_by` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-fx_rate"></a>
## `fx_rate`

Exchange rate captured per source and day (local and reporting currency)

| | |
|---|---|
| Zone | ops |
| Kind | reference |
| Classification | public |
| History | append |
| Scope | none |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-PMT-07 |
| Pages | FIN-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `rate_date` | `DATE` | no |  |  |
| `base_currency` | `CHAR(3)` | no |  |  |
| `quote_currency` | `CHAR(3)` | no |  |  |
| `rate` | `DECIMAL(18,8)` | no |  |  |
| `source` | `VARCHAR(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, rate_date, base_currency, quote_currency, source)

<a id="ops-tax_rule"></a>
## `tax_rule`

Tax rule (VAT 7.5% where applicable, withholding) by charge type and jurisdiction

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | none |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-PMT-07, FR-BIL-03 |
| Pages | FIN-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `tax_code` | `VARCHAR(16)` | no |  |  |
| `rate` | `DECIMAL(6,3)` | no |  |  |
| `applies_to` | `JSON` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `effective_from` | `DATE` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, tax_code, version)

<a id="ops-bank_statement_line"></a>
## `bank_statement_line`

Imported bank statement line (MT940/CSV/open banking) reconciled to payments and disbursements

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-PMT-06 |
| Pages | PMT-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `bank_account_ref` | `VARCHAR(40)` | no |  |  |
| `statement_date` | `DATE` | no |  |  |
| `value_date` | `DATE` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `narrative` | `VARCHAR(500)` | yes |  |  |
| `bank_ref` | `VARCHAR(64)` | no |  |  |
| `matched_kind` | `VARCHAR(40)` | yes |  |  |
| `matched_id` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: unmatched, matched, part_matched, disputed, reconciled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, bank_account_ref, bank_ref)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-budget"></a>
## `budget`

Budget by cost centre and account linked to enrolment and staffing forecasts (approved via workflow)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-FIN-01, FR-FIN-02 |
| Pages | FIN-01, FIN-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `fiscal_year` | `SMALLINT` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `line_items` | `JSON` | no |  | Cost centre × account × period amounts |
| `assumptions` | `JSON` | yes |  | Enrolment and staffing forecasts |
| `currency` | `CHAR(3)` | no |  |  |
| `variance_notes` | `JSON` | yes |  | Explanations and forecast outturn |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, fiscal_year, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-supplier"></a>
## `supplier`

Supplier 360 master (duplicate detection; call-back verification and dual approval for bank-detail changes)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | appj |
| Retention | `RS-FIN` |
| Requirements | FR-FIN-04 |
| Pages | FIN-04, FIN-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `cac_number` | `VARCHAR(20)` | yes |  |  |
| `tin` | `VARCHAR(20)` | yes |  |  |
| `contacts` | `JSON` | yes |  |  |
| `bank_account_enc` | `VARBINARY(1024)` | yes | restricted | Envelope-encrypted bank_account. |
| `bank_account_last4` | `CHAR(4)` | yes | restricted | Last four characters of bank_account for masked display |
| `bank_change_verified_by` | `BINARY(16)` | yes |  |  |
| `bank_change_approved_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `dual_control`: `bank_change_approved_by IS NULL OR bank_change_verified_by IS NULL OR bank_change_approved_by <> bank_change_verified_by`

<a id="ops-requisition"></a>
## `requisition`

Purchase requisition (delegated approval limits; split-purchase detection)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-FIN-03 |
| Pages | FIN-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `requisition_number` | `VARCHAR(32)` | no |  |  |
| `requested_by` | `BINARY(16)` | no |  |  |
| `cost_centre` | `VARCHAR(32)` | no |  |  |
| `line_items` | `JSON` | no |  |  |
| `total_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `split_purchase_flag` | `BOOLEAN` | no |  |  |
| `workflow_instance_id` → `workflow_instance` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, requisition_number)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-purchase_order"></a>
## `purchase_order`

Purchase order, goods receipt and three-way match to the supplier invoice

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-FIN-03 |
| Pages | FIN-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `po_number` | `VARCHAR(32)` | no |  |  |
| `requisition_id` → `requisition` | `BINARY(16)` | yes |  |  |
| `supplier_id` → `supplier` | `BINARY(16)` | no |  |  |
| `total_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `received_on` | `DATE` | yes |  |  |
| `supplier_invoice_ref` | `VARCHAR(64)` | yes |  |  |
| `match_status` | `VARCHAR(32)` | no |  | values: pending, matched, mismatch, override_approved |
| `paid_journal_id` → `journal` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, approved, issued, received, invoiced, paid, closed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, po_number)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-cost_centre"></a>
## `cost_centre`

Cost centre of an institution (administration, department, boarding, feeding, estate, ICT, transport, project, welfare) with its budget holder

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-ACC-01 |
| Pages | FIN-01, FIN-02, ACC-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `cost_centre_kind` | `VARCHAR(32)` | no |  | values: administration, academic_department, boarding, feeding, estate, ict, transport, health, library, sports, project, welfare, revenue_generating, other |
| `parent_id` → `cost_centre` | `BINARY(16)` | yes |  |  |
| `org_unit_id` → `org_unit` | `BINARY(16)` | yes |  | Department or unit the cost centre belongs to |
| `holder_staff_id` → `staff` | `BINARY(16)` | yes |  | Budget holder |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)
- Index: (tenant_id, institution_id)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `org_unit_id` → `org_unit` — cross-zone (ops → registry)
- Soft reference `holder_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-budget_line"></a>
## `budget_line`

Approved budget line — cost centre × ledger account × economic code × funding source, with original, revised, committed and actual amounts  

committed and actual are maintained by the commitment service under a row lock; available = revised − committed − actual is never negative (FR-ACC-03).

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-ACC-02, FR-ACC-03, FR-ACC-06 |
| Pages | FIN-01, FIN-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `budget_id` → `budget` | `BINARY(16)` | no |  |  |
| `cost_centre_id` → `cost_centre` | `BINARY(16)` | no |  |  |
| `account_id` → `account` | `BINARY(16)` | no |  |  |
| `economic_code` | `VARCHAR(16)` | no |  | Economic segment of the National Chart of Accounts, e.g. 22020101 |
| `funding_source_kind` | `VARCHAR(32)` | no |  | values: subvention, personnel_cost, overhead, capital_allocation, internally_generated_revenue, fees, grant, intervention, loan, donation, other |
| `funding_source_id` → `funding_source` | `BINARY(16)` | yes |  |  |
| `description` | `VARCHAR(300)` | yes |  |  |
| `original_minor` | `BIGINT` | no |  | (minor units) |
| `revised_minor` | `BIGINT` | no |  | (minor units) |
| `committed_minor` | `BIGINT` | no |  | (minor units) |
| `actual_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, budget_id, cost_centre_id, account_id, economic_code, funding_source_kind)
- Index: (tenant_id, cost_centre_id)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `within_budget`: `committed_minor >= 0 AND actual_minor >= 0 AND committed_minor + actual_minor <= revised_minor`

<a id="ops-budget_commitment"></a>
## `budget_commitment`

Commitment of a budget line by a requisition, purchase order, imprest, payroll or disbursement (released, spent or cancelled)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-ACC-03 |
| Pages | FIN-02 |
| Events | FIN.FUNDS_COMMITTED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `budget_line_id` → `budget_line` | `BINARY(16)` | no |  |  |
| `source_kind` | `VARCHAR(32)` | no |  | values: requisition, purchase_order, imprest, payroll, funding_disbursement, contract, manual |
| `source_id` | `BINARY(16)` | no |  |  |
| `description` | `VARCHAR(300)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `spent_minor` | `BIGINT` | no |  | (minor units) |
| `released_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `committed_on` | `DATE` | no |  |  |
| `committed_by` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, partly_spent, spent, released, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, budget_line_id, status)
- Index: (tenant_id, source_kind, source_id)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `settles`: `spent_minor + released_minor <= amount_minor`

<a id="ops-budget_virement"></a>
## `budget_virement`

Virement — budget moved between two lines with a reason, approved by someone other than the requester

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-ACC-04 |
| Pages | FIN-01, FIN-02 |
| Events | FIN.VIREMENT_APPROVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `virement_number` | `VARCHAR(32)` | no |  |  |
| `from_line_id` → `budget_line` | `BINARY(16)` | no |  |  |
| `to_line_id` → `budget_line` | `BINARY(16)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `reason` | `TEXT` | no |  |  |
| `requested_by` | `BINARY(16)` | no |  |  |
| `decided_by` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, virement_number)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `four_eyes`: `decided_by IS NULL OR decided_by <> requested_by`
- Check `two_lines`: `from_line_id <> to_line_id`

<a id="ops-imprest"></a>
## `imprest`

Imprest — cash advance to a named holder against a budget line, to be retired with receipts by a due date

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-ACC-05 |
| Pages | ACC-01 |
| Events | FIN.IMPREST_OVERDUE |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `imprest_number` | `VARCHAR(32)` | no |  |  |
| `holder_staff_id` → `staff` | `BINARY(16)` | no |  |  |
| `cost_centre_id` → `cost_centre` | `BINARY(16)` | no |  |  |
| `budget_line_id` → `budget_line` | `BINARY(16)` | no |  |  |
| `commitment_id` → `budget_commitment` | `BINARY(16)` | yes |  |  |
| `purpose` | `VARCHAR(300)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `retired_minor` | `BIGINT` | no |  | (minor units) |
| `refunded_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `requested_by` | `BINARY(16)` | no |  |  |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `issued_on` | `DATE` | yes |  |  |
| `retire_by` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: requested, approved, issued, partly_retired, retired, overdue, written_off, rejected, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, imprest_number)
- Index: (tenant_id, holder_staff_id, status)
- Index: (tenant_id, retire_by)

- Soft reference `holder_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `four_eyes`: `approved_by IS NULL OR approved_by <> requested_by`
- Check `retired_within`: `retired_minor + refunded_minor <= amount_minor`

<a id="ops-imprest_retirement"></a>
## `imprest_retirement`

Retirement of an imprest — receipts, amount accounted for and cash refunded

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `finance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-ACC-05 |
| Pages | ACC-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `imprest_id` → `imprest` | `BINARY(16)` | no |  |  |
| `receipts` | `JSON` | no |  | Receipt references, payees and amounts |
| `amount_minor` | `BIGINT` | no |  | Amount accounted for by receipts (minor units) |
| `refund_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `retired_on` | `DATE` | no |  |  |
| `verified_by` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

