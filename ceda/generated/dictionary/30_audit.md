# AUD — Audit trail, chain anchors and the transactional outbox

Every consequential write — and every view of special-category records, reveal of restricted fields, bulk export and assistant query — produces an audit event in the same transaction and the same zone as the change (Book 3 §15). Each zone keeps its own hash chain per tenant (hash = SHA-256(prev_hash ‖ canonical(event))); a daily anchor is written to write-once storage and the chain is verified nightly. Special-category values appear in field_changes only as hashes with a pointer to the vault history. Domain events are written to the zone's outbox in the same transaction and published by Debezium (outbox event router) to Kafka; outbox rows are purged seven days after publication.

Module (system of record): `core` · default zone: **ops** · default retention: `RS-AUDIT`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`audit_event`](#platform-audit_event) | platform | event | restricted | append | Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day) |
| [`audit_event`](#registry-audit_event) | registry | event | restricted | append | Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day) |
| [`audit_event`](#ops-audit_event) | ops | event | restricted | append | Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day) |
| [`audit_event`](#vault-audit_event) | vault | event | restricted | append | Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day) |
| [`audit_event`](#records-audit_event) | records | event | restricted | append | Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day) |
| [`audit_chain_head`](#platform-audit_chain_head) | platform | projection | internal | none | Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain |
| [`audit_chain_head`](#registry-audit_chain_head) | registry | projection | internal | none | Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain |
| [`audit_chain_head`](#ops-audit_chain_head) | ops | projection | internal | none | Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain |
| [`audit_chain_head`](#vault-audit_chain_head) | vault | projection | internal | none | Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain |
| [`audit_chain_head`](#records-audit_chain_head) | records | projection | internal | none | Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain |
| [`audit_anchor`](#platform-audit_anchor) | platform | event | internal | append | Daily anchor of an audit chain written to write-once storage, and the nightly verification result |
| [`audit_anchor`](#registry-audit_anchor) | registry | event | internal | append | Daily anchor of an audit chain written to write-once storage, and the nightly verification result |
| [`audit_anchor`](#ops-audit_anchor) | ops | event | internal | append | Daily anchor of an audit chain written to write-once storage, and the nightly verification result |
| [`audit_anchor`](#vault-audit_anchor) | vault | event | internal | append | Daily anchor of an audit chain written to write-once storage, and the nightly verification result |
| [`audit_anchor`](#records-audit_anchor) | records | event | internal | append | Daily anchor of an audit chain written to write-once storage, and the nightly verification result |
| [`outbox_event`](#platform-outbox_event) | platform | queue | internal | none | Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication) |
| [`outbox_event`](#registry-outbox_event) | registry | queue | internal | none | Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication) |
| [`outbox_event`](#ops-outbox_event) | ops | queue | internal | none | Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication) |
| [`outbox_event`](#vault-outbox_event) | vault | queue | internal | none | Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication) |
| [`outbox_event`](#records-outbox_event) | records | queue | internal | none | Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication) |

<a id="platform-audit_event"></a>
## `audit_event` (platform)

Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day)

| | |
|---|---|
| Zone | platform |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-AUDIT` |
| Partitioning | range_day on `occurred_at` |
| Requirements | FR-ADM-08, FR-LRN-13, FR-SAF-06, FR-AGT-109, FR-CMD-107, FR-SUB-114 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `chain_id` **PK** | `BINARY(16)` | no |  | Tenant id (or the platform chain id in the platform zone) |
| `chain_seq` **PK** | `BIGINT` | no |  | Monotonic sequence within the chain |
| `occurred_at` **PK** | `DATETIME(6)` | no |  |  |
| `event_id` | `BINARY(16)` | no |  | UUID v7 of the event |
| `actor_kind` | `VARCHAR(32)` | no |  | values: user, agent, api_client, system, platform_operator |
| `actor_id` | `BINARY(16)` | yes |  |  |
| `on_behalf_of_user_id` | `BINARY(16)` | yes |  | Agent X acting for Owner Y |
| `actor_grant_id` | `BINARY(16)` | yes |  | Active role-at-scope |
| `scope_node_id_at` | `BINARY(16)` | yes |  | Scope of the record at the time |
| `action` | `VARCHAR(80)` | no |  | e.g. learner.update, learner.nin.reveal, safeguarding_case.view, export.bulk |
| `record_kind` | `VARCHAR(64)` | no |  |  |
| `record_id` | `BINARY(16)` | yes |  |  |
| `field_changes` | `JSON` | yes |  | [{field, from, to}] — special-category values as hashes |
| `reason` | `VARCHAR(1000)` | yes |  |  |
| `purpose_code` | `VARCHAR(40)` | yes |  | Required for restricted/special access |
| `approval_ref` | `BINARY(16)` | yes |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `ip` | `VARBINARY(16)` | yes |  |  |
| `user_agent` | `VARCHAR(400)` | yes |  |  |
| `prev_hash` | `BINARY(32)` | no |  |  |
| `hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (record_kind, record_id)
- Index: (actor_id, occurred_at)

<a id="registry-audit_event"></a>
## `audit_event` (registry)

Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-AUDIT` |
| Partitioning | range_day on `occurred_at` |
| Requirements | FR-ADM-08, FR-LRN-13, FR-SAF-06, FR-AGT-109, FR-CMD-107, FR-SUB-114 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  | Tenant id (or the platform chain id in the platform zone) |
| `chain_seq` **PK** | `BIGINT` | no |  | Monotonic sequence within the chain |
| `occurred_at` **PK** | `DATETIME(6)` | no |  |  |
| `event_id` | `BINARY(16)` | no |  | UUID v7 of the event |
| `actor_kind` | `VARCHAR(32)` | no |  | values: user, agent, api_client, system, platform_operator |
| `actor_id` | `BINARY(16)` | yes |  |  |
| `on_behalf_of_user_id` | `BINARY(16)` | yes |  | Agent X acting for Owner Y |
| `actor_grant_id` | `BINARY(16)` | yes |  | Active role-at-scope |
| `scope_node_id_at` | `BINARY(16)` | yes |  | Scope of the record at the time |
| `action` | `VARCHAR(80)` | no |  | e.g. learner.update, learner.nin.reveal, safeguarding_case.view, export.bulk |
| `record_kind` | `VARCHAR(64)` | no |  |  |
| `record_id` | `BINARY(16)` | yes |  |  |
| `field_changes` | `JSON` | yes |  | [{field, from, to}] — special-category values as hashes |
| `reason` | `VARCHAR(1000)` | yes |  |  |
| `purpose_code` | `VARCHAR(40)` | yes |  | Required for restricted/special access |
| `approval_ref` | `BINARY(16)` | yes |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `ip` | `VARBINARY(16)` | yes |  |  |
| `user_agent` | `VARCHAR(400)` | yes |  |  |
| `prev_hash` | `BINARY(32)` | no |  |  |
| `hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, record_kind, record_id)
- Index: (tenant_id, actor_id, occurred_at)

<a id="ops-audit_event"></a>
## `audit_event` (ops)

Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-AUDIT` |
| Partitioning | range_day on `occurred_at` |
| Requirements | FR-ADM-08, FR-LRN-13, FR-SAF-06, FR-AGT-109, FR-CMD-107, FR-SUB-114 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  | Tenant id (or the platform chain id in the platform zone) |
| `chain_seq` **PK** | `BIGINT` | no |  | Monotonic sequence within the chain |
| `occurred_at` **PK** | `DATETIME(6)` | no |  |  |
| `event_id` | `BINARY(16)` | no |  | UUID v7 of the event |
| `actor_kind` | `VARCHAR(32)` | no |  | values: user, agent, api_client, system, platform_operator |
| `actor_id` | `BINARY(16)` | yes |  |  |
| `on_behalf_of_user_id` | `BINARY(16)` | yes |  | Agent X acting for Owner Y |
| `actor_grant_id` | `BINARY(16)` | yes |  | Active role-at-scope |
| `scope_node_id_at` | `BINARY(16)` | yes |  | Scope of the record at the time |
| `action` | `VARCHAR(80)` | no |  | e.g. learner.update, learner.nin.reveal, safeguarding_case.view, export.bulk |
| `record_kind` | `VARCHAR(64)` | no |  |  |
| `record_id` | `BINARY(16)` | yes |  |  |
| `field_changes` | `JSON` | yes |  | [{field, from, to}] — special-category values as hashes |
| `reason` | `VARCHAR(1000)` | yes |  |  |
| `purpose_code` | `VARCHAR(40)` | yes |  | Required for restricted/special access |
| `approval_ref` | `BINARY(16)` | yes |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `ip` | `VARBINARY(16)` | yes |  |  |
| `user_agent` | `VARCHAR(400)` | yes |  |  |
| `prev_hash` | `BINARY(32)` | no |  |  |
| `hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, record_kind, record_id)
- Index: (tenant_id, actor_id, occurred_at)

<a id="vault-audit_event"></a>
## `audit_event` (vault)

Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day)

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-AUDIT` |
| Partitioning | range_day on `occurred_at` |
| Requirements | FR-ADM-08, FR-LRN-13, FR-SAF-06, FR-AGT-109, FR-CMD-107, FR-SUB-114 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  | Tenant id (or the platform chain id in the platform zone) |
| `chain_seq` **PK** | `BIGINT` | no |  | Monotonic sequence within the chain |
| `occurred_at` **PK** | `DATETIME(6)` | no |  |  |
| `event_id` | `BINARY(16)` | no |  | UUID v7 of the event |
| `actor_kind` | `VARCHAR(32)` | no |  | values: user, agent, api_client, system, platform_operator |
| `actor_id` | `BINARY(16)` | yes |  |  |
| `on_behalf_of_user_id` | `BINARY(16)` | yes |  | Agent X acting for Owner Y |
| `actor_grant_id` | `BINARY(16)` | yes |  | Active role-at-scope |
| `scope_node_id_at` | `BINARY(16)` | yes |  | Scope of the record at the time |
| `action` | `VARCHAR(80)` | no |  | e.g. learner.update, learner.nin.reveal, safeguarding_case.view, export.bulk |
| `record_kind` | `VARCHAR(64)` | no |  |  |
| `record_id` | `BINARY(16)` | yes |  |  |
| `field_changes` | `JSON` | yes |  | [{field, from, to}] — special-category values as hashes |
| `reason` | `VARCHAR(1000)` | yes |  |  |
| `purpose_code` | `VARCHAR(40)` | yes |  | Required for restricted/special access |
| `approval_ref` | `BINARY(16)` | yes |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `ip` | `VARBINARY(16)` | yes |  |  |
| `user_agent` | `VARCHAR(400)` | yes |  |  |
| `prev_hash` | `BINARY(32)` | no |  |  |
| `hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, record_kind, record_id)
- Index: (tenant_id, actor_id, occurred_at)

<a id="records-audit_event"></a>
## `audit_event` (records)

Tamper-evident audit event (append-only, hash-chained per tenant and zone, partitioned by day)

| | |
|---|---|
| Zone | records |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-AUDIT` |
| Partitioning | range_day on `occurred_at` |
| Requirements | FR-ADM-08, FR-LRN-13, FR-SAF-06, FR-AGT-109, FR-CMD-107, FR-SUB-114 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  | Tenant id (or the platform chain id in the platform zone) |
| `chain_seq` **PK** | `BIGINT` | no |  | Monotonic sequence within the chain |
| `occurred_at` **PK** | `DATETIME(6)` | no |  |  |
| `event_id` | `BINARY(16)` | no |  | UUID v7 of the event |
| `actor_kind` | `VARCHAR(32)` | no |  | values: user, agent, api_client, system, platform_operator |
| `actor_id` | `BINARY(16)` | yes |  |  |
| `on_behalf_of_user_id` | `BINARY(16)` | yes |  | Agent X acting for Owner Y |
| `actor_grant_id` | `BINARY(16)` | yes |  | Active role-at-scope |
| `scope_node_id_at` | `BINARY(16)` | yes |  | Scope of the record at the time |
| `action` | `VARCHAR(80)` | no |  | e.g. learner.update, learner.nin.reveal, safeguarding_case.view, export.bulk |
| `record_kind` | `VARCHAR(64)` | no |  |  |
| `record_id` | `BINARY(16)` | yes |  |  |
| `field_changes` | `JSON` | yes |  | [{field, from, to}] — special-category values as hashes |
| `reason` | `VARCHAR(1000)` | yes |  |  |
| `purpose_code` | `VARCHAR(40)` | yes |  | Required for restricted/special access |
| `approval_ref` | `BINARY(16)` | yes |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `ip` | `VARBINARY(16)` | yes |  |  |
| `user_agent` | `VARCHAR(400)` | yes |  |  |
| `prev_hash` | `BINARY(32)` | no |  |  |
| `hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, record_kind, record_id)
- Index: (tenant_id, actor_id, occurred_at)

<a id="platform-audit_chain_head"></a>
## `audit_chain_head` (platform)

Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain  

Chains are split into lanes (chain_id = UUID5(tenant_id, "lane-<n>"), default 16 lanes per tenant and zone) so concurrent writers at the 07:30–09:30 register peak do not serialise on a single row; each lane is an independent hash chain anchored daily and verified nightly (CD-12).

| | |
|---|---|
| Zone | platform |
| Kind | projection |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `chain_id` **PK** | `BINARY(16)` | no |  |  |
| `lane` | `SMALLINT` | no |  |  |
| `last_seq` | `BIGINT` | no |  |  |
| `last_hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-audit_chain_head"></a>
## `audit_chain_head` (registry)

Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain  

Chains are split into lanes (chain_id = UUID5(tenant_id, "lane-<n>"), default 16 lanes per tenant and zone) so concurrent writers at the 07:30–09:30 register peak do not serialise on a single row; each lane is an independent hash chain anchored daily and verified nightly (CD-12).

| | |
|---|---|
| Zone | registry |
| Kind | projection |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  |  |
| `lane` | `SMALLINT` | no |  |  |
| `last_seq` | `BIGINT` | no |  |  |
| `last_hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-audit_chain_head"></a>
## `audit_chain_head` (ops)

Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain  

Chains are split into lanes (chain_id = UUID5(tenant_id, "lane-<n>"), default 16 lanes per tenant and zone) so concurrent writers at the 07:30–09:30 register peak do not serialise on a single row; each lane is an independent hash chain anchored daily and verified nightly (CD-12).

| | |
|---|---|
| Zone | ops |
| Kind | projection |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  |  |
| `lane` | `SMALLINT` | no |  |  |
| `last_seq` | `BIGINT` | no |  |  |
| `last_hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="vault-audit_chain_head"></a>
## `audit_chain_head` (vault)

Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain  

Chains are split into lanes (chain_id = UUID5(tenant_id, "lane-<n>"), default 16 lanes per tenant and zone) so concurrent writers at the 07:30–09:30 register peak do not serialise on a single row; each lane is an independent hash chain anchored daily and verified nightly (CD-12).

| | |
|---|---|
| Zone | vault |
| Kind | projection |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  |  |
| `lane` | `SMALLINT` | no |  |  |
| `last_seq` | `BIGINT` | no |  |  |
| `last_hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="records-audit_chain_head"></a>
## `audit_chain_head` (records)

Head of an audit hash chain (last sequence and hash), locked FOR UPDATE by each writer to sequence the chain  

Chains are split into lanes (chain_id = UUID5(tenant_id, "lane-<n>"), default 16 lanes per tenant and zone) so concurrent writers at the 07:30–09:30 register peak do not serialise on a single row; each lane is an independent hash chain anchored daily and verified nightly (CD-12).

| | |
|---|---|
| Zone | records |
| Kind | projection |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` **PK** | `BINARY(16)` | no |  |  |
| `lane` | `SMALLINT` | no |  |  |
| `last_seq` | `BIGINT` | no |  |  |
| `last_hash` | `BINARY(32)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="platform-audit_anchor"></a>
## `audit_anchor` (platform)

Daily anchor of an audit chain written to write-once storage, and the nightly verification result

| | |
|---|---|
| Zone | platform |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `chain_id` | `BINARY(16)` | no |  |  |
| `anchor_date` | `DATE` | no |  |  |
| `last_chain_seq` | `BIGINT` | no |  |  |
| `anchor_hash` | `BINARY(32)` | no |  |  |
| `worm_object_key` | `VARCHAR(1024)` | no |  |  |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `verification_ok` | `BOOLEAN` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (chain_id, anchor_date)

<a id="registry-audit_anchor"></a>
## `audit_anchor` (registry)

Daily anchor of an audit chain written to write-once storage, and the nightly verification result

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` | `BINARY(16)` | no |  |  |
| `anchor_date` | `DATE` | no |  |  |
| `last_chain_seq` | `BIGINT` | no |  |  |
| `anchor_hash` | `BINARY(32)` | no |  |  |
| `worm_object_key` | `VARCHAR(1024)` | no |  |  |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `verification_ok` | `BOOLEAN` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, chain_id, anchor_date)

<a id="ops-audit_anchor"></a>
## `audit_anchor` (ops)

Daily anchor of an audit chain written to write-once storage, and the nightly verification result

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` | `BINARY(16)` | no |  |  |
| `anchor_date` | `DATE` | no |  |  |
| `last_chain_seq` | `BIGINT` | no |  |  |
| `anchor_hash` | `BINARY(32)` | no |  |  |
| `worm_object_key` | `VARCHAR(1024)` | no |  |  |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `verification_ok` | `BOOLEAN` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, chain_id, anchor_date)

<a id="vault-audit_anchor"></a>
## `audit_anchor` (vault)

Daily anchor of an audit chain written to write-once storage, and the nightly verification result

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` | `BINARY(16)` | no |  |  |
| `anchor_date` | `DATE` | no |  |  |
| `last_chain_seq` | `BIGINT` | no |  |  |
| `anchor_hash` | `BINARY(32)` | no |  |  |
| `worm_object_key` | `VARCHAR(1024)` | no |  |  |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `verification_ok` | `BOOLEAN` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, chain_id, anchor_date)

<a id="records-audit_anchor"></a>
## `audit_anchor` (records)

Daily anchor of an audit chain written to write-once storage, and the nightly verification result

| | |
|---|---|
| Zone | records |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `core` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-08 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `chain_id` | `BINARY(16)` | no |  |  |
| `anchor_date` | `DATE` | no |  |  |
| `last_chain_seq` | `BIGINT` | no |  |  |
| `anchor_hash` | `BINARY(32)` | no |  |  |
| `worm_object_key` | `VARCHAR(1024)` | no |  |  |
| `verified_at` | `DATETIME(6)` | yes |  |  |
| `verification_ok` | `BOOLEAN` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, chain_id, anchor_date)

<a id="platform-outbox_event"></a>
## `outbox_event` (platform)

Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication)

| | |
|---|---|
| Zone | platform |
| Kind | queue |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-OUTBOX` |
| Partitioning | range_day on `created_on` |
| Requirements | FR-ADM-05, FR-CER-102, FR-COM-05 |
| Pages | ADM-18, ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `created_on` **PK** | `DATE` | no |  |  |
| `event_type` | `VARCHAR(80)` | no |  | e.g. LRN.CREATED |
| `schema_version` | `SMALLINT` | no |  |  |
| `aggregate_kind` | `VARCHAR(64)` | no |  |  |
| `aggregate_id` | `BINARY(16)` | no |  |  |
| `scope_node_id_at` | `BINARY(16)` | yes |  |  |
| `actor` | `VARCHAR(120)` | no |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `payload` | `JSON` | no |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (published_at)

<a id="registry-outbox_event"></a>
## `outbox_event` (registry)

Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication)

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-OUTBOX` |
| Partitioning | range_day on `created_on` |
| Requirements | FR-ADM-05, FR-CER-102, FR-COM-05 |
| Pages | ADM-18, ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `created_on` **PK** | `DATE` | no |  |  |
| `event_type` | `VARCHAR(80)` | no |  | e.g. LRN.CREATED |
| `schema_version` | `SMALLINT` | no |  |  |
| `aggregate_kind` | `VARCHAR(64)` | no |  |  |
| `aggregate_id` | `BINARY(16)` | no |  |  |
| `scope_node_id_at` | `BINARY(16)` | yes |  |  |
| `actor` | `VARCHAR(120)` | no |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `payload` | `JSON` | no |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, published_at)

<a id="ops-outbox_event"></a>
## `outbox_event` (ops)

Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication)

| | |
|---|---|
| Zone | ops |
| Kind | queue |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-OUTBOX` |
| Partitioning | range_day on `created_on` |
| Requirements | FR-ADM-05, FR-CER-102, FR-COM-05 |
| Pages | ADM-18, ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `created_on` **PK** | `DATE` | no |  |  |
| `event_type` | `VARCHAR(80)` | no |  | e.g. LRN.CREATED |
| `schema_version` | `SMALLINT` | no |  |  |
| `aggregate_kind` | `VARCHAR(64)` | no |  |  |
| `aggregate_id` | `BINARY(16)` | no |  |  |
| `scope_node_id_at` | `BINARY(16)` | yes |  |  |
| `actor` | `VARCHAR(120)` | no |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `payload` | `JSON` | no |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, published_at)

<a id="vault-outbox_event"></a>
## `outbox_event` (vault)

Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication)

| | |
|---|---|
| Zone | vault |
| Kind | queue |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-OUTBOX` |
| Partitioning | range_day on `created_on` |
| Requirements | FR-ADM-05, FR-CER-102, FR-COM-05 |
| Pages | ADM-18, ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `created_on` **PK** | `DATE` | no |  |  |
| `event_type` | `VARCHAR(80)` | no |  | e.g. LRN.CREATED |
| `schema_version` | `SMALLINT` | no |  |  |
| `aggregate_kind` | `VARCHAR(64)` | no |  |  |
| `aggregate_id` | `BINARY(16)` | no |  |  |
| `scope_node_id_at` | `BINARY(16)` | yes |  |  |
| `actor` | `VARCHAR(120)` | no |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `payload` | `JSON` | no |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, published_at)

<a id="records-outbox_event"></a>
## `outbox_event` (records)

Transactional outbox of domain events (written with the change; published by CDC; purged 7 days after publication)

| | |
|---|---|
| Zone | records |
| Kind | queue |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `core` |
| Origin | appj |
| Retention | `RS-OUTBOX` |
| Partitioning | range_day on `created_on` |
| Requirements | FR-ADM-05, FR-CER-102, FR-COM-05 |
| Pages | ADM-18, ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `created_on` **PK** | `DATE` | no |  |  |
| `event_type` | `VARCHAR(80)` | no |  | e.g. LRN.CREATED |
| `schema_version` | `SMALLINT` | no |  |  |
| `aggregate_kind` | `VARCHAR(64)` | no |  |  |
| `aggregate_id` | `BINARY(16)` | no |  |  |
| `scope_node_id_at` | `BINARY(16)` | yes |  |  |
| `actor` | `VARCHAR(120)` | no |  |  |
| `correlation_id` | `VARCHAR(64)` | yes |  |  |
| `payload` | `JSON` | no |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, published_at)

