# INTG — Integration, data exchange, imports, webhooks, idempotency and data-subject requests

Integrations exchange data through APIs and events and never become a second copy of master data (Book 3 §27). API clients are bound to data-sharing agreements (purpose, datasets, legal basis, expiry); every exchange is authenticated, logged and traceable, and cross-border exchanges carry only agreed fields. Inbound webhooks (payment gateways, exam bodies, WhatsApp, state revenue) are signature-verified and processed idempotently; client POSTs that create or move money, issue certificates or enrol learners carry an Idempotency-Key retained 24 hours. Legacy imports are staged, validated, matched and reversible for 30 days (FR-ADM-12). Data-subject requests are handled within statutory deadlines (ADM-10).

Module (system of record): `integration` · default zone: **registry** · default retention: `RS-INTG`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`api_client`](#registry-api_client) | registry | config | internal | lifecycle | API client (partner, verifier, government system, LMS) with OAuth scopes, mTLS binding and rate limits |
| [`data_sharing_agreement`](#registry-data_sharing_agreement) | registry | config | internal | versioned | Data-sharing agreement (purpose, datasets, legal basis, parties, residency, expiry) |
| [`exchange_transfer`](#registry-exchange_transfer) | registry | event | confidential | append | Global Education Data Exchange transfer (learner records, transcripts, results, institution, funding, attendance, outcomes) |
| [`integration_connection`](#registry-integration_connection) | registry | config | internal | lifecycle | Configured integration (payment gateway, NIMC, exam body, LMS, SSO/SCIM, IFMIS, accounting, OCR engine, originality provider) |
| [`integration_connection`](#ops-integration_connection) | ops | config | internal | lifecycle | Configured integration (payment gateway, NIMC, exam body, LMS, SSO/SCIM, IFMIS, accounting, OCR engine, originality provider) |
| [`webhook_subscription`](#ops-webhook_subscription) | ops | config | internal | lifecycle | Outbound webhook subscription (tenant-configurable, HMAC-signed, retried with back-off for 24 h) |
| [`webhook_delivery`](#ops-webhook_delivery) | ops | queue | internal | lifecycle | Delivery attempt of an outbound webhook |
| [`inbound_webhook`](#registry-inbound_webhook) | registry | queue | confidential | lifecycle | Inbound webhook received (payment gateway, exam body, WhatsApp, state revenue) — signature verified, processed once |
| [`inbound_webhook`](#ops-inbound_webhook) | ops | queue | confidential | lifecycle | Inbound webhook received (payment gateway, exam body, WhatsApp, state revenue) — signature verified, processed once |
| [`idempotency_key`](#registry-idempotency_key) | registry | queue | internal | none | Client Idempotency-Key and the stored response (retained 24 hours; offline sync operations use the same table) |
| [`idempotency_key`](#ops-idempotency_key) | ops | queue | internal | none | Client Idempotency-Key and the stored response (retained 24 hours; offline sync operations use the same table) |
| [`import_job`](#registry-import_job) | registry | transaction | confidential | lifecycle | Legacy data import or migration batch (mapping, validation, matching, staged commit, 30-day rollback) |
| [`import_job`](#ops-import_job) | ops | transaction | confidential | lifecycle | Legacy data import or migration batch (mapping, validation, matching, staged commit, 30-day rollback) |
| [`import_row_issue`](#registry-import_row_issue) | registry | queue | confidential | lifecycle | Validation or matching issue on an import row |
| [`import_row_issue`](#ops-import_row_issue) | ops | queue | confidential | lifecycle | Validation or matching issue on an import row |
| [`privacy_request`](#registry-privacy_request) | registry | transaction | restricted | lifecycle | Data-subject request (access, rectification, erasure respecting legal holds, restriction, portability, objection) |

<a id="registry-api_client"></a>
## `api_client`

API client (partner, verifier, government system, LMS) with OAuth scopes, mTLS binding and rate limits

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-INTG` |
| Requirements | FR-ADM-06, FR-CER-07 |
| Pages | ADM-09, ADM-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `client_kind` | `VARCHAR(32)` | no |  | values: partner, bulk_verifier, government_system, lms, mobile_app, internal_service |
| `client_id` | `VARCHAR(64)` | no |  |  |
| `secret_hash` | `BINARY(32)` | yes |  | Client secret hash (or mTLS certificate thumbprint) |
| `certificate_thumbprint` | `BINARY(32)` | yes |  |  |
| `scopes` | `JSON` | no |  |  |
| `agreement_id` → `data_sharing_agreement` | `BINARY(16)` | yes |  |  |
| `rate_limit_per_minute` | `INT UNSIGNED` | no |  |  |
| `service_identity_id` → `service_identity` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, client_id)

<a id="registry-data_sharing_agreement"></a>
## `data_sharing_agreement`

Data-sharing agreement (purpose, datasets, legal basis, parties, residency, expiry)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-INTG` |
| Requirements | FR-ADM-06, FR-ADM-07 |
| Pages | ADM-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `counterparty` | `VARCHAR(300)` | no |  |  |
| `purpose` | `TEXT` | no |  |  |
| `datasets` | `JSON` | no |  | Agreed fields only |
| `legal_basis` | `VARCHAR(32)` | no |  | values: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests |
| `cross_border` | `BOOLEAN` | no |  |  |
| `expires_on` | `DATE` | no |  |  |
| `document_id` | `BINARY(16)` | yes |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-exchange_transfer"></a>
## `exchange_transfer`

Global Education Data Exchange transfer (learner records, transcripts, results, institution, funding, attendance, outcomes)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-INTG` |
| Requirements | FR-LRN-10, FR-LRN-16, FR-ADM-06 |
| Pages | ADM-09, LRN-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `agreement_id` → `data_sharing_agreement` | `BINARY(16)` | no |  |  |
| `direction` | `VARCHAR(32)` | no |  | values: outbound, inbound |
| `dataset` | `VARCHAR(32)` | no |  | values: learner_record, transcript, results, institution, staff, funding, attendance, outcomes |
| `subject_ref` | `BINARY(16)` | yes |  | Learner or institution |
| `payload_hash` | `BINARY(32)` | no |  |  |
| `payload_format` | `VARCHAR(32)` | no |  | OneRoster 1.2, Ed-Fi style, PESC transcript … |
| `counterpart_ref` | `VARCHAR(128)` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-integration_connection"></a>
## `integration_connection` (registry)

Configured integration (payment gateway, NIMC, exam body, LMS, SSO/SCIM, IFMIS, accounting, OCR engine, originality provider)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-INTG` |
| Requirements | FR-ADM-06, FR-PMT-101, FR-FIN-06 |
| Pages | ADM-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `integration_code` | `VARCHAR(40)` | no |  | paystack, flutterwave, remita, nimc, waec, moodle, entra, ifmis … |
| `adapter_version` | `VARCHAR(32)` | no |  |  |
| `settings` | `JSON` | no |  | Non-secret settings |
| `credentials_vault_ref` | `VARCHAR(255)` | no |  | Secrets in the vault only |
| `last_success_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, integration_code)

<a id="ops-integration_connection"></a>
## `integration_connection` (ops)

Configured integration (payment gateway, NIMC, exam body, LMS, SSO/SCIM, IFMIS, accounting, OCR engine, originality provider)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-INTG` |
| Requirements | FR-ADM-06, FR-PMT-101, FR-FIN-06 |
| Pages | ADM-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `integration_code` | `VARCHAR(40)` | no |  | paystack, flutterwave, remita, nimc, waec, moodle, entra, ifmis … |
| `adapter_version` | `VARCHAR(32)` | no |  |  |
| `settings` | `JSON` | no |  | Non-secret settings |
| `credentials_vault_ref` | `VARCHAR(255)` | no |  | Secrets in the vault only |
| `last_success_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, integration_code)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-webhook_subscription"></a>
## `webhook_subscription`

Outbound webhook subscription (tenant-configurable, HMAC-signed, retried with back-off for 24 h)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-ADM-06 |
| Pages | ADM-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `api_client_id` | `BINARY(16)` | no |  | Registry API client |
| `event_types` | `JSON` | no |  |  |
| `target_url` | `VARCHAR(2048)` | no |  |  |
| `signing_secret_vault_ref` | `VARCHAR(255)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-webhook_delivery"></a>
## `webhook_delivery`

Delivery attempt of an outbound webhook

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-ADM-06 |
| Pages | ADM-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `subscription_id` → `webhook_subscription` | `BINARY(16)` | no |  |  |
| `event_id` | `BINARY(16)` | no |  |  |
| `attempts` | `SMALLINT` | no |  |  |
| `next_attempt_at` | `DATETIME(6)` | yes |  |  |
| `last_status_code` | `SMALLINT` | yes |  |  |
| `delivered_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: queued, sent, delivered, read, failed, retrying, abandoned, processed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, subscription_id, event_id)

<a id="registry-inbound_webhook"></a>
## `inbound_webhook` (registry)

Inbound webhook received (payment gateway, exam body, WhatsApp, state revenue) — signature verified, processed once

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-PMT-02, FR-SUB-111, FR-COM-106 |
| Pages | PMT-03, SUB-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `source` | `VARCHAR(40)` | no |  |  |
| `external_event_id` | `VARCHAR(128)` | no |  | Provider event id — idempotency key |
| `signature_valid` | `BOOLEAN` | no |  |  |
| `payload` | `JSON` | no |  |  |
| `received_at` | `DATETIME(6)` | no |  |  |
| `processed_at` | `DATETIME(6)` | yes |  |  |
| `error` | `VARCHAR(1000)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: queued, sent, delivered, read, failed, retrying, abandoned, processed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, source, external_event_id)

<a id="ops-inbound_webhook"></a>
## `inbound_webhook` (ops)

Inbound webhook received (payment gateway, exam body, WhatsApp, state revenue) — signature verified, processed once

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-PMT-02, FR-SUB-111, FR-COM-106 |
| Pages | PMT-03, SUB-103 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `source` | `VARCHAR(40)` | no |  |  |
| `external_event_id` | `VARCHAR(128)` | no |  | Provider event id — idempotency key |
| `signature_valid` | `BOOLEAN` | no |  |  |
| `payload` | `JSON` | no |  |  |
| `received_at` | `DATETIME(6)` | no |  |  |
| `processed_at` | `DATETIME(6)` | yes |  |  |
| `error` | `VARCHAR(1000)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: queued, sent, delivered, read, failed, retrying, abandoned, processed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, source, external_event_id)

<a id="registry-idempotency_key"></a>
## `idempotency_key` (registry)

Client Idempotency-Key and the stored response (retained 24 hours; offline sync operations use the same table)

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-TRANSIENT` |
| Requirements | FR-ATT-03, FR-PMT-02 |
| Pages | PMT-03, ATT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `principal_id` | `BINARY(16)` | no |  |  |
| `idem_key` | `VARCHAR(128)` | no |  |  |
| `request_hash` | `BINARY(32)` | no |  |  |
| `response_status` | `SMALLINT` | no |  |  |
| `response_body` | `JSON` | yes |  |  |
| `expires_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, principal_id, idem_key)

<a id="ops-idempotency_key"></a>
## `idempotency_key` (ops)

Client Idempotency-Key and the stored response (retained 24 hours; offline sync operations use the same table)

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-TRANSIENT` |
| Requirements | FR-ATT-03, FR-PMT-02 |
| Pages | PMT-03, ATT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `principal_id` | `BINARY(16)` | no |  |  |
| `idem_key` | `VARCHAR(128)` | no |  |  |
| `request_hash` | `BINARY(32)` | no |  |  |
| `response_status` | `SMALLINT` | no |  |  |
| `response_body` | `JSON` | yes |  |  |
| `expires_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, principal_id, idem_key)

<a id="registry-import_job"></a>
## `import_job` (registry)

Legacy data import or migration batch (mapping, validation, matching, staged commit, 30-day rollback)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-ADM-12, FR-ASM-102, FR-ASM-103 |
| Pages | ADM-15 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `template` | `VARCHAR(32)` | no |  | values: learners, guardians, staff, classes, enrolments, marks, balances, assessments, curriculum |
| `source_document_id` | `BINARY(16)` | no |  |  |
| `mapping` | `JSON` | no |  |  |
| `rows_total` | `INT UNSIGNED` | no |  |  |
| `rows_valid` | `INT UNSIGNED` | no |  |  |
| `rows_matched` | `INT UNSIGNED` | no |  |  |
| `rows_committed` | `INT UNSIGNED` | no |  |  |
| `committed_at` | `DATETIME(6)` | yes |  |  |
| `rollback_until` | `DATETIME(6)` | yes |  |  |
| `rolled_back_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: uploaded, mapped, validating, validated, matching, staged, committed, rolled_back, failed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-import_job"></a>
## `import_job` (ops)

Legacy data import or migration batch (mapping, validation, matching, staged commit, 30-day rollback)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-ADM-12, FR-ASM-102, FR-ASM-103 |
| Pages | ADM-15 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `template` | `VARCHAR(32)` | no |  | values: learners, guardians, staff, classes, enrolments, marks, balances, assessments, curriculum |
| `source_document_id` | `BINARY(16)` | no |  |  |
| `mapping` | `JSON` | no |  |  |
| `rows_total` | `INT UNSIGNED` | no |  |  |
| `rows_valid` | `INT UNSIGNED` | no |  |  |
| `rows_matched` | `INT UNSIGNED` | no |  |  |
| `rows_committed` | `INT UNSIGNED` | no |  |  |
| `committed_at` | `DATETIME(6)` | yes |  |  |
| `rollback_until` | `DATETIME(6)` | yes |  |  |
| `rolled_back_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: uploaded, mapped, validating, validated, matching, staged, committed, rolled_back, failed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="registry-import_row_issue"></a>
## `import_row_issue` (registry)

Validation or matching issue on an import row

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-ADM-12 |
| Pages | ADM-15 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `job_id` → `import_job` | `BINARY(16)` | no |  |  |
| `row_no` | `INT UNSIGNED` | no |  |  |
| `level` | `VARCHAR(32)` | no |  | values: hard, soft, anomaly |
| `message` | `VARCHAR(1000)` | no |  |  |
| `error_code` | `VARCHAR(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-import_row_issue"></a>
## `import_row_issue` (ops)

Validation or matching issue on an import row

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-ADM-12 |
| Pages | ADM-15 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `job_id` → `import_job` | `BINARY(16)` | no |  |  |
| `row_no` | `INT UNSIGNED` | no |  |  |
| `level` | `VARCHAR(32)` | no |  | values: hard, soft, anomaly |
| `message` | `VARCHAR(1000)` | no |  |  |
| `error_code` | `VARCHAR(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-privacy_request"></a>
## `privacy_request`

Data-subject request (access, rectification, erasure respecting legal holds, restriction, portability, objection)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `integration` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-07, NFR-PRIV-03 |
| Pages | ADM-10 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `request_kind` | `VARCHAR(32)` | no |  | values: access, rectification, erasure, restriction, portability, objection |
| `subject_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `subject_id` | `BINARY(16)` | yes |  |  |
| `requester_name` | `VARCHAR(200)` | no |  |  |
| `identity_verified_at` | `DATETIME(6)` | yes |  |  |
| `received_at` | `DATETIME(6)` | no |  |  |
| `due_at` | `DATETIME(6)` | no |  |  |
| `outcome` | `JSON` | yes |  | Per-entity actions (export, redact, crypto-shred, refused with basis) |
| `export_document_id` | `BINARY(16)` | yes |  |  |
| `handled_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, in_review, approved, rejected, cancelled, fulfilled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

