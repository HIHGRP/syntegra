# PLT — Platform, tenancy and operator commercial records

The control plane of the SaaS service operated by Syntegra Digital Infrastructure Nigeria Ltd (SDIN): tenants and their residency, hostnames used to resolve the tenant at sign-in, feature flags, the operator's private-provider plan catalogue and subscription billing (MFS §20.7–20.8), service credits, the operator receivables ledger, Global Learner ID block allocation, and backup/DR evidence. The control plane never holds learner-level data (FR-ADM-01); SDAF money and records live in the state registry (domain SUB), never here.

Module (system of record): `platform` · default zone: **platform** · default retention: `RS-PLATFORM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`residency_region`](#platform-residency_region) | platform | reference | internal | lifecycle | Data-residency region (in-country hosting location for a group of tenants) |
| [`tenant`](#platform-tenant) | platform | master | internal | lifecycle | Tenant — data boundary, configuration and billing unit (global, country, state, network, private provider) |
| [`tenant_domain`](#platform-tenant_domain) | platform | config | internal | lifecycle | Hostname that resolves to a tenant at sign-in (tenant is never chosen from a list) |
| [`feature_flag`](#platform-feature_flag) | platform | config | internal | none | Feature flag per tenant and phase (continuous delivery, freeze windows) |
| [`platform_user`](#platform-platform_user) | platform | master | restricted | lifecycle | Operator staff account (PLAT role) — no learner-data access by default; break-glass only |
| [`glid_block`](#platform-glid_block) | platform | config | internal | append | Block of Global Learner ID serials leased to a state registry (national uniqueness without per-insert coordination) |
| [`subscription_plan`](#platform-subscription_plan) | platform | config | internal | versioned | Operator plan and price-list version for private providers (and the State Enterprise plan) |
| [`subscription`](#platform-subscription) | platform | transaction | internal | lifecycle | A tenant's subscription to a plan (private providers pay SDIN directly; state tenants are SDAF-financed) |
| [`subscription_quote`](#platform-subscription_quote) | platform | transaction | internal | lifecycle | Quote issued to a private provider before subscription acceptance |
| [`subscription_invoice`](#platform-subscription_invoice) | platform | transaction | internal | lifecycle | Invoice from the operator to a private provider (never edited after issue; credit notes for changes) |
| [`subscription_invoice_line`](#platform-subscription_invoice_line) | platform | transaction | internal | append | Line of an operator invoice (per campus for group invoices, proration, add-ons) |
| [`subscription_credit_note`](#platform-subscription_credit_note) | platform | transaction | internal | append | Credit note or refund against an operator invoice |
| [`subscription_payment`](#platform-subscription_payment) | platform | transaction | internal | append | Payment by a private provider directly to the operator |
| [`service_credit`](#platform-service_credit) | platform | transaction | internal | append | Service credit under the BOO service-level agreement |
| [`operator_receivable`](#platform-operator_receivable) | platform | transaction | internal | append | Operator receivables ledger line by channel (SDAF remittance, private subscription, other services) |
| [`backup_run`](#platform-backup_run) | platform | event | internal | append | Database backup or restore test (DR readiness evidence for provider staff) |
| [`exchange_peer`](#platform-exchange_peer) | platform | config | internal | lifecycle | National clearance network directory — one row per state registry (36 states and the FCT) |

<a id="platform-residency_region"></a>
## `residency_region`

Data-residency region (in-country hosting location for a group of tenants)

| | |
|---|---|
| Zone | platform |
| Kind | reference |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | NFR-PRIV-04 |
| Pages | ADM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `code` | `VARCHAR(32)` | no |  | Region code, e.g. ng-lagos, ng-abuja |
| `name` | `VARCHAR(300)` | no |  |  |
| `country` | `CHAR(2)` | no |  | Country whose law governs the data (NDPA 2023 for NG) |
| `primary_site` | `VARCHAR(120)` | no |  | Primary data centre |
| `secondary_site` | `VARCHAR(120)` | yes |  | ClusterSet replica site (second in-country data centre) |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (code)

<a id="platform-tenant"></a>
## `tenant`

Tenant — data boundary, configuration and billing unit (global, country, state, network, private provider)  

Tenants nest (country → state → private provider / network). Every row in the registry, ops, vault and records zones carries tenant_id. Public institutions are scope nodes inside the state tenant; each private provider is its own tenant registered in the state where it operates.

| | |
|---|---|
| Zone | platform |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | appj |
| Retention | `RS-PLATFORM` |
| Requirements | FR-ADM-01, FR-PVT-108 |
| Pages | ADM-01 |
| Events | PLT.TENANT_PROVISIONED, PLT.TENANT_STATUS_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `parent_id` → `tenant` | `BINARY(16)` | yes |  | Parent tenant (state for a private provider, country for a state) |
| `kind` | `VARCHAR(32)` | no |  | values: global, country, state, network, private_provider, institution, department |
| `code` | `VARCHAR(40)` | no |  | Stable tenant code, e.g. ng, ng-ab, pvt-ng-ab-000123 |
| `name` | `VARCHAR(300)` | no |  |  |
| `residency_region_id` → `residency_region` | `BINARY(16)` | no |  |  |
| `state_code` | `VARCHAR(6)` | yes |  | ISO 3166-2 state for state and private-provider tenants |
| `isolation` | `VARCHAR(32)` | no |  | Dedicated schema or pooled schema (MFS §16.3 layer 1) · values: dedicated_schema, pooled_schema |
| `ops_schema` | `VARCHAR(64)` | no |  | MySQL schema of the tenant's ops zone |
| `time_zone` | `VARCHAR(64)` | no |  | IANA time zone applied on display |
| `default_language` | `VARCHAR(35)` | no |  |  |
| `currency` | `CHAR(3)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: proposed, provisioning, active, suspended, closed |
| `activated_at` | `DATETIME(6)` | yes |  |  |
| `closed_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (code)

<a id="platform-tenant_domain"></a>
## `tenant_domain`

Hostname that resolves to a tenant at sign-in (tenant is never chosen from a list)

| | |
|---|---|
| Zone | platform |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-ADM-10 |
| Pages | AUT-01, ADM-13 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` → `tenant` | `BINARY(16)` | no |  |  |
| `hostname` | `VARCHAR(253)` | no |  | e.g. abia.syntegra.ng or portal.schoolname.ng |
| `is_primary` | `BOOLEAN` | no |  |  |
| `verified_at` | `DATETIME(6)` | yes |  | DNS ownership verified |
| `tls_certificate_ref` | `VARCHAR(200)` | yes |  | Certificate manager reference |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (hostname)

<a id="platform-feature_flag"></a>
## `feature_flag`

Feature flag per tenant and phase (continuous delivery, freeze windows)

| | |
|---|---|
| Zone | platform |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-ADM-01 |
| Pages | ADM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` → `tenant` | `BINARY(16)` | yes |  | NULL = platform default |
| `flag_key` | `VARCHAR(80)` | no |  |  |
| `is_enabled` | `BOOLEAN` | no |  |  |
| `rollout_percent` | `SMALLINT` | yes |  | Progressive rollout share |
| `phase` | `VARCHAR(8)` | yes |  | Delivery phase gating the feature (P0–P7) |
| `reason` | `VARCHAR(300)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, flag_key)

<a id="platform-platform_user"></a>
## `platform_user`

Operator staff account (PLAT role) — no learner-data access by default; break-glass only

| | |
|---|---|
| Zone | platform |
| Kind | master |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-ADM-01, FR-ADM-13 |
| Pages | ADM-01, ADM-16 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `email` | `VARCHAR(254)` | no |  |  |
| `display_name` | `VARCHAR(200)` | no |  |  |
| `idp_subject` | `VARCHAR(255)` | no |  | Subject in Red Hat Identity Management / operator IdP (MFA enforced) |
| `is_break_glass_eligible` | `BOOLEAN` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: invited, active, locked, suspended, deactivated |
| `last_sign_in_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (email)
- Unique: (idp_subject)

<a id="platform-glid_block"></a>
## `glid_block`

Block of Global Learner ID serials leased to a state registry (national uniqueness without per-insert coordination)  

The national GLID allocator leases contiguous blocks (default 10,000 serials) to each state registry. A registry assigns serials from its open block, so Global Learner IDs are unique nationally and never reused, including after merge. Decision CD-07.

| | |
|---|---|
| Zone | platform |
| Kind | config |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-LRN-07 |
| Pages | ADM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` → `tenant` | `BINARY(16)` | no |  | State tenant that holds the lease |
| `first_serial` | `BIGINT` | no |  |  |
| `last_serial` | `BIGINT` | no |  |  |
| `leased_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (first_serial)

- Check `range`: `last_serial >= first_serial`

<a id="platform-subscription_plan"></a>
## `subscription_plan`

Operator plan and price-list version for private providers (and the State Enterprise plan)

| | |
|---|---|
| Zone | platform |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | none |
| Module | `platform` |
| Origin | appj |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-117, FR-ADM-11 |
| Pages | SUB-108, ADM-14 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `code` | `VARCHAR(40)` | no |  | Starter, Standard, Advanced, Tertiary, Group, State Enterprise |
| `version` | `INT UNSIGNED` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `tier` | `VARCHAR(32)` | no |  | values: starter, standard, advanced, tertiary, group, state_enterprise |
| `price_basis` | `VARCHAR(32)` | no |  | values: per_learner_term, per_learner_semester, flat_term, per_campus_term, sdaf |
| `unit_price_minor` | `BIGINT` | no |  | Price per unit of the price basis (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `modules` | `JSON` | no |  | Module codes included (INS, LRN, LMS …) |
| `limits` | `JSON` | yes |  | Learner, campus, storage and messaging limits |
| `add_ons` | `JSON` | yes |  | Digitisation, messaging bundles, storage — with prices |
| `vat_applicable` | `BOOLEAN` | no |  |  |
| `effective_from` | `DATE` | no |  |  |
| `effective_to` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `approved_by` → `platform_user` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (code, version)

<a id="platform-subscription"></a>
## `subscription`

A tenant's subscription to a plan (private providers pay SDIN directly; state tenants are SDAF-financed)

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | appj |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-101, FR-SUB-117, FR-SUB-121, FR-ADM-11 |
| Pages | ADM-14, SUB-107, SUB-108 |
| Events | SUB.SUBSCRIPTION_STATUS_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` → `tenant` | `BINARY(16)` | no |  |  |
| `plan_id` → `subscription_plan` | `BINARY(16)` | no |  |  |
| `financing_channel` | `VARCHAR(32)` | no |  | values: sdaf, direct_subscription |
| `status` | `VARCHAR(32)` | no |  | values: trial, active, grace, restricted, suspended, terminated |
| `starts_on` | `DATE` | no |  |  |
| `ends_on` | `DATE` | yes |  |  |
| `trial_ends_on` | `DATE` | yes |  |  |
| `grace_days` | `SMALLINT` | no |  |  |
| `restricted_since` | `DATETIME(6)` | yes |  | Administrative features restricted (never registers, teaching, results, certificates — P9) |
| `terms_version` | `VARCHAR(32)` | yes |  | Subscription terms accepted |
| `terms_accepted_at` | `DATETIME(6)` | yes |  |  |
| `terms_accepted_by_name` | `VARCHAR(200)` | yes |  |  |
| `billing_email` | `VARCHAR(254)` | yes |  |  |
| `payment_method` | `VARCHAR(32)` | yes |  | values: gateway, virtual_account, bank_transfer, direct_debit |
| `virtual_account_ref` | `VARCHAR(40)` | yes |  | Dedicated virtual account for transfers |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="platform-subscription_quote"></a>
## `subscription_quote`

Quote issued to a private provider before subscription acceptance

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-117 |
| Pages | SUB-107, SUB-108 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` → `tenant` | `BINARY(16)` | yes |  | Set once the provider tenant exists |
| `provider_ref` | `BINARY(16)` | yes |  | Registry provider id (soft) before tenant creation |
| `plan_id` → `subscription_plan` | `BINARY(16)` | no |  |  |
| `learner_estimate` | `INT UNSIGNED` | no |  |  |
| `campus_count` | `SMALLINT` | yes |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `valid_until` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, sent, accepted, expired, withdrawn |
| `document_ref` | `BINARY(16)` | yes |  | Quote PDF (records zone) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="platform-subscription_invoice"></a>
## `subscription_invoice`

Invoice from the operator to a private provider (never edited after issue; credit notes for changes)

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | appj |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-118, FR-SUB-120 |
| Pages | SUB-107, SUB-108 |
| Events | SUB.INVOICE_ISSUED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `subscription_id` → `subscription` | `BINARY(16)` | no |  |  |
| `invoice_number` | `VARCHAR(32)` | no |  | SDIN-<year>-<seq> |
| `period_start` | `DATE` | no |  |  |
| `period_end` | `DATE` | no |  |  |
| `census_learners` | `INT UNSIGNED` | yes |  | From the census count used for SDAF (one counting rule) |
| `net_amount_minor` | `BIGINT` | no |  | (minor units) |
| `discount_amount_minor` | `BIGINT` | no |  | (minor units) |
| `vat_amount_minor` | `BIGINT` | no |  | (minor units) |
| `total_amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `issued_on` | `DATE` | no |  |  |
| `due_on` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, issued, part_paid, paid, overdue, credited, void |
| `content_hash` | `BINARY(32)` | no |  | SHA-256 of the canonical invoice at issue |
| `e_invoice_ref` | `VARCHAR(64)` | yes |  | National e-invoicing reference where required (D27) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (invoice_number)

<a id="platform-subscription_invoice_line"></a>
## `subscription_invoice_line`

Line of an operator invoice (per campus for group invoices, proration, add-ons)

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-118 |
| Pages | SUB-107 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `invoice_id` → `subscription_invoice` | `BINARY(16)` | no |  |  |
| `line_no` | `SMALLINT` | no |  |  |
| `description` | `VARCHAR(300)` | no |  |  |
| `campus_ref` | `BINARY(16)` | yes |  | Registry campus id for group breakdowns (soft) |
| `quantity` | `DECIMAL(12,3)` | no |  |  |
| `unit_price_minor` | `BIGINT` | no |  | (minor units) |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `is_proration` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (invoice_id, line_no)

<a id="platform-subscription_credit_note"></a>
## `subscription_credit_note`

Credit note or refund against an operator invoice

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-118 |
| Pages | SUB-108 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `invoice_id` → `subscription_invoice` | `BINARY(16)` | no |  |  |
| `credit_number` | `VARCHAR(32)` | no |  |  |
| `reason` | `VARCHAR(500)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `is_refund` | `BOOLEAN` | no |  |  |
| `approved_by` → `platform_user` | `BINARY(16)` | no |  | SDIN finance approval |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (credit_number)

<a id="platform-subscription_payment"></a>
## `subscription_payment`

Payment by a private provider directly to the operator

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `platform` |
| Origin | appj |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-119 |
| Pages | SUB-107, SUB-108 |
| Events | SUB.PAYMENT_RECEIVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `invoice_id` → `subscription_invoice` | `BINARY(16)` | no |  |  |
| `method` | `VARCHAR(32)` | no |  | values: gateway, virtual_account, bank_transfer, direct_debit |
| `gateway` | `VARCHAR(32)` | yes |  | paystack, flutterwave, bank |
| `gateway_ref` | `VARCHAR(128)` | no |  | Idempotency: one row per gateway transaction |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `received_at` | `DATETIME(6)` | no |  |  |
| `receipt_number` | `VARCHAR(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (gateway_ref)
- Unique: (receipt_number)

<a id="platform-service_credit"></a>
## `service_credit`

Service credit under the BOO service-level agreement

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-125 |
| Pages | SUB-104, SUB-108 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` → `tenant` | `BINARY(16)` | no |  |  |
| `period_start` | `DATE` | no |  |  |
| `period_end` | `DATE` | no |  |  |
| `sla_metric` | `VARCHAR(40)` | no |  | availability_gov_tier, support_p1_response … |
| `target` | `DECIMAL(9,4)` | no |  |  |
| `measured` | `DECIMAL(9,4)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `applied_to_kind` | `VARCHAR(32)` | no |  | values: reconciliation_statement, subscription_invoice |
| `applied_to_id` | `BINARY(16)` | yes |  | Reconciliation statement (registry) or subscription invoice |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="platform-operator_receivable"></a>
## `operator_receivable`

Operator receivables ledger line by channel (SDAF remittance, private subscription, other services)

| | |
|---|---|
| Zone | platform |
| Kind | transaction |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-SUB-124 |
| Pages | SUB-108 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `channel` | `VARCHAR(32)` | no |  | values: sdaf_remittance, private_subscription, other_service |
| `tenant_id` → `tenant` | `BINARY(16)` | no |  |  |
| `source_kind` | `VARCHAR(40)` | no |  | remittance, subscription_invoice, digitisation_order … |
| `source_id` | `BINARY(16)` | no |  | Source record (soft; may be in the state registry) |
| `revenue_period` | `VARCHAR(7)` | no |  | YYYY-MM recognition period |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `recognised_on` | `DATE` | no |  |  |
| `exported_at` | `DATETIME(6)` | yes |  | Exported to SDIN accounting through the adapter |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (channel, revenue_period)

<a id="platform-backup_run"></a>
## `backup_run`

Database backup or restore test (DR readiness evidence for provider staff)

| | |
|---|---|
| Zone | platform |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-OPS-LOG` |
| Requirements | FR-ADM-13, NFR-AVAIL-03, NFR-PLAT-105 |
| Pages | ADM-16 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `residency_region_id` → `residency_region` | `BINARY(16)` | no |  |  |
| `store` | `VARCHAR(40)` | no |  | mysql-ops, mysql-registry, objectstore, opensearch … |
| `kind` | `VARCHAR(32)` | no |  | values: full_backup, incremental_backup, binlog_stream, tenant_restore_test, site_failover_test |
| `started_at` | `DATETIME(6)` | no |  |  |
| `finished_at` | `DATETIME(6)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | no |  | values: succeeded, failed, partial |
| `size_bytes` | `BIGINT` | yes |  |  |
| `rpo_seconds` | `INT` | yes |  | Measured recovery point for failover tests |
| `rto_seconds` | `INT` | yes |  | Measured recovery time for failover tests |
| `report_ref` | `BINARY(16)` | yes |  | Published test report document |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="platform-exchange_peer"></a>
## `exchange_peer`

National clearance network directory — one row per state registry (36 states and the FCT)

| | |
|---|---|
| Zone | platform |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `platform` |
| Origin | ceda |
| Retention | `RS-PLATFORM` |
| Requirements | FR-FCL-10, FR-FCL-11 |
| Pages | FCL-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `state_code` | `VARCHAR(6)` | no |  | ISO 3166-2:NG, e.g. NG-LA |
| `state_name` | `VARCHAR(300)` | no |  |  |
| `tenant_id` → `tenant` | `BINARY(16)` | yes |  | State tenant once provisioned on this platform |
| `hosting` | `VARCHAR(32)` | no |  | values: co_hosted, remote |
| `endpoint_url` | `VARCHAR(2048)` | yes |  | Remote peers: base URL of the state's exchange API |
| `kid` | `VARCHAR(64)` | yes |  | Key id of the state's exchange signing key |
| `public_jwk` | `JSON` | yes |  | Verification key (EC P-256) |
| `agreement_ref` | `VARCHAR(64)` | yes |  | National clearance data-sharing agreement reference |
| `status` | `VARCHAR(32)` | no |  | values: not_on_network, onboarding, active, suspended |
| `onboarded_at` | `DATETIME(6)` | yes |  |  |
| `last_seen_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (state_code)

