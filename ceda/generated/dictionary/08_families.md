# FAM — Family 360, guardians, contacts, contact restrictions and consent

Guardians are person masters matched on phone, e-mail, NIN and name before creation (FR-FAM-01) and held in the state registry beside the learner. The learner–guardian relationship carries parental responsibility, contact priority, lives-with and effective dates; one guardian may belong to several households and one learner may have guardians in several (FR-FAM-03). Households as billing groups, organisation contacts and the consent record are operational (ops zone). Court orders and contact restriction detail are special category (vault); the registry carries only the restriction flag the messaging, collection and portal rules need (FR-FAM-04).

Module (system of record): `families` · default zone: **registry** · default retention: `RS-LRN-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`guardian`](#registry-guardian) | registry | master | confidential | lifecycle | Parent/Guardian 360 master |
| [`learner_guardian`](#registry-learner_guardian) | registry | link | confidential | effective | Relationship between a learner and a guardian (parental responsibility, priority, lives-with, restriction flag) |
| [`family`](#ops-family) | ops | master | confidential | lifecycle | Family 360 household and billing group (per operating tenant) |
| [`family_member`](#ops-family_member) | ops | link | confidential | effective | Membership of a learner or guardian in a household |
| [`organisation_contact`](#ops-organisation_contact) | ops | master | confidential | lifecycle | Organisation contact (other schools, doctors, suppliers, agencies) and additional learner contacts |
| [`contact_restriction`](#vault-contact_restriction) | vault | master | special | effective | Court order or contact restriction detail (no communications, collection or portal access to the restricted child) |
| [`consent_record`](#ops-consent_record) | ops | transaction | confidential | effective | Consent given or refused by a guardian (or learner of age) for a learner — the consent record |

<a id="registry-guardian"></a>
## `guardian`

Parent/Guardian 360 master

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: through the learners the guardian is linked to |
| Module | `families` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-FAM-01, FR-FAM-06 |
| Pages | FAM-01, FAM-02, FAM-03 |
| Events | FAM.GUARDIAN_CREATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `given_name` | `VARCHAR(200)` | no |  |  |
| `family_name` | `VARCHAR(200)` | no |  |  |
| `title` | `VARCHAR(30)` | yes |  |  |
| `name_phonetic` | `VARCHAR(120)` | no |  |  |
| `phone` | `VARCHAR(16)` | yes |  | E.164; inbound WhatsApp matching uses phone_hmac in channel contacts |
| `email` | `VARCHAR(254)` | yes |  |  |
| `preferred_language` | `VARCHAR(35)` | yes |  |  |
| `preferred_channel` | `VARCHAR(32)` | yes |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `address` | `JSON` | yes |  |  |
| `user_id` → `app_user` | `BINARY(16)` | yes |  | Parent portal account |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, merged, deceased |
| `merged_into` → `guardian` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, phone)

<a id="registry-learner_guardian"></a>
## `learner_guardian`

Relationship between a learner and a guardian (parental responsibility, priority, lives-with, restriction flag)

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | confidential |
| History | effective |
| Scope | derived: the learner |
| Module | `families` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-FAM-02, FR-FAM-04, FR-LRN-06, FR-EYR-101 |
| Pages | FAM-01, FAM-02, LRN-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `guardian_id` → `guardian` | `BINARY(16)` | no |  |  |
| `relationship` | `VARCHAR(32)` | no |  | code list `relationship` |
| `has_parental_responsibility` | `BOOLEAN` | no |  |  |
| `contact_priority` | `SMALLINT` | yes |  |  |
| `lives_with` | `BOOLEAN` | yes |  |  |
| `is_contact_restricted` | `BOOLEAN` | no |  | Detail held in the vault (contact_restriction) |
| `is_authorised_collector` | `BOOLEAN` | no |  |  |
| `is_payer` | `BOOLEAN` | no |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, guardian_id, valid_from)
- Index: (tenant_id, guardian_id)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-family"></a>
## `family`

Family 360 household and billing group (per operating tenant)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the institutions of its learners |
| Module | `families` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-FAM-03, FR-BIL-07 |
| Pages | FAM-01, BIL-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `name` | `VARCHAR(300)` | no |  |  |
| `primary_payer_guardian_id` → `guardian` | `BINARY(16)` | yes |  | Registry guardian (soft) |
| `billing_account_id` → `account` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `primary_payer_guardian_id` → `guardian` — cross-zone (ops → registry)

<a id="ops-family_member"></a>
## `family_member`

Membership of a learner or guardian in a household

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | confidential |
| History | effective |
| Scope | derived: the family |
| Module | `families` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-FAM-03 |
| Pages | FAM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `family_id` → `family` | `BINARY(16)` | no |  |  |
| `member_kind` | `VARCHAR(32)` | no |  | values: learner, guardian |
| `member_id` | `BINARY(16)` | no |  | learner or guardian id (registry) |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, family_id, member_kind, member_id, valid_from)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-organisation_contact"></a>
## `organisation_contact`

Organisation contact (other schools, doctors, suppliers, agencies) and additional learner contacts

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `families` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-FAM-101 |
| Pages | FAM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `kind` | `VARCHAR(32)` | no |  | values: school, doctor, supplier, agency, employer, other |
| `name` | `VARCHAR(300)` | no |  |  |
| `contact_person` | `VARCHAR(200)` | yes |  |  |
| `phone` | `VARCHAR(16)` | yes |  |  |
| `email` | `VARCHAR(254)` | yes |  |  |
| `address` | `JSON` | yes |  |  |
| `learner_id` → `learner` | `BINARY(16)` | yes |  | When the contact is linked to one learner (with relationship and priority) |
| `relationship` | `VARCHAR(80)` | yes |  |  |
| `priority` | `SMALLINT` | yes |  |  |
| `preferred_channel` | `VARCHAR(32)` | yes |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-contact_restriction"></a>
## `contact_restriction`

Court order or contact restriction detail (no communications, collection or portal access to the restricted child)

| | |
|---|---|
| Zone | vault |
| Kind | master |
| Classification | special |
| History | effective |
| Scope | derived: the learner; DSL and named users only |
| Module | `families` |
| Origin | ceda |
| Retention | `RS-SAF` |
| Requirements | FR-FAM-04, FR-COM-02 |
| Pages | FAM-01, SAF-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `guardian_id` → `guardian` | `BINARY(16)` | no |  |  |
| `restriction` | `VARCHAR(32)` | no |  | values: no_contact, no_collection, no_information, supervised_only |
| `order_reference` | `MEDIUMBLOB` | yes | special | Court order reference and terms |
| `document_id` | `BINARY(16)` | yes |  | Order copy (records zone, special category) |
| `recorded_by` | `BINARY(16)` | no |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `guardian_id` → `guardian` — cross-zone (vault → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-consent_record"></a>
## `consent_record`

Consent given or refused by a guardian (or learner of age) for a learner — the consent record  

Appendix J called this consent_response; CEDA keeps one consent record for all sources (consent request, form, admission, WhatsApp button). Withdrawal propagates immediately to messaging, photo sharing and trip lists.

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | effective |
| Scope | derived: the learner's institution |
| Module | `families` |
| Origin | appj (Appendix J `consent_response`) |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-FAM-05, FR-COM-120, FR-EYR-02, FR-OPS-06, FR-PTM-103 |
| Pages | FAM-04, COM-104, OPS-06 |
| Events | FAM.CONSENT_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `guardian_id` → `guardian` | `BINARY(16)` | yes |  | NULL when the learner gives consent themselves |
| `consent_type` | `VARCHAR(32)` | no |  | photography, trips, data_sharing, medical, biometrics, digital_services, video_recording … · code list `consent_type` |
| `consent_request_id` → `consent_request` | `BINARY(16)` | yes |  |  |
| `request_version` | `INT UNSIGNED` | yes |  | Version of the request answered |
| `decision` | `VARCHAR(32)` | no |  | values: given, refused, withdrawn |
| `legal_basis` | `VARCHAR(32)` | no |  | values: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests |
| `channel` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `comment` | `VARCHAR(1000)` | yes |  |  |
| `evidence` | `JSON` | yes |  | Wording shown, device, time |
| `expires_on` | `DATE` | yes |  |  |
| `withdrawn_at` | `DATETIME(6)` | yes |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, learner_id, consent_type)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `guardian_id` → `guardian` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

