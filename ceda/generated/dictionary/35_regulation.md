# REG — Education watchdogs, regulators and examination bodies — their dependencies and every institution's regulatory profile

A national directory of the bodies Nigerian education depends on (change request CR-005): the Federal Ministry of Education, regulators and accreditors (NUC, NBTE, NCCE, UBEC), curriculum (NERDC), examination (WAEC, NECO, NABTEB, NBAIS), admission (JAMB), teacher registration (TRCN), funding (TETFund) and professional councils (NMCN, MDCN, PCN, MLSCN, COREN …), with the dependencies between them. The directory lives in the platform zone (one copy, national). Each institution's regulatory profile — which body supervises, accredits or licenses it, sets its curriculum, examines its learners, admits its graduates, registers its teachers, regulates its professions and funds it — lives in the registry of the institution (state, federal or security sector registry).

Module (system of record): `regulation` · default zone: **platform** · default retention: `RS-INS-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`regulatory_body`](#platform-regulatory_body) | platform | reference | public | lifecycle | Education watchdog — ministry, regulator, examination, admission, curriculum, teacher, funding or professional body |
| [`body_dependency`](#platform-body_dependency) | platform | reference | public | lifecycle | Dependency between two watchdogs (supervised by, recognises the results of, accredits with, funded by, member of) |
| [`institution_regulation`](#registry-institution_regulation) | registry | link | internal | effective | Link from an institution to a watchdog it depends on — relationship, what it covers, effective dates |

<a id="platform-regulatory_body"></a>
## `regulatory_body`

Education watchdog — ministry, regulator, examination, admission, curriculum, teacher, funding or professional body

| | |
|---|---|
| Zone | platform |
| Kind | reference |
| Classification | public |
| History | lifecycle |
| Scope | none |
| Module | `regulation` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-REG-01 |
| Pages | REG-01, REG-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `code` | `VARCHAR(16)` | no |  | Matches the regulator code list where one exists, e.g. NUC, WAEC, JAMB |
| `name` | `VARCHAR(300)` | no |  |  |
| `body_type` | `VARCHAR(32)` | no |  | values: ministry, regulator_accreditor, examination_body, admissions_body, curriculum_authority, teacher_regulator, professional_council, funding_agency, sector_regulator, training_institute |
| `statutory_basis` | `VARCHAR(300)` | yes |  | Establishing law |
| `jurisdiction` | `VARCHAR(32)` | no |  | values: federal, regional, state |
| `levels` | `JSON` | yes |  | Education levels the body covers (education_level codes) |
| `functions` | `TEXT` | yes |  | What the body does for institutions |
| `website` | `VARCHAR(2048)` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (code)

<a id="platform-body_dependency"></a>
## `body_dependency`

Dependency between two watchdogs (supervised by, recognises the results of, accredits with, funded by, member of)

| | |
|---|---|
| Zone | platform |
| Kind | reference |
| Classification | public |
| History | lifecycle |
| Scope | none |
| Module | `regulation` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-REG-02 |
| Pages | REG-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `from_body_id` → `regulatory_body` | `BINARY(16)` | no |  |  |
| `to_body_id` → `regulatory_body` | `BINARY(16)` | no |  |  |
| `dependency_type` | `VARCHAR(32)` | no |  | values: supervised_by, recognises_results_of, accredits_with, funded_by, member_of |
| `note` | `VARCHAR(300)` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (from_body_id, to_body_id, dependency_type)

<a id="registry-institution_regulation"></a>
## `institution_regulation`

Link from an institution to a watchdog it depends on — relationship, what it covers, effective dates  

scope_node_id is the institution's node. regulatory_body_id refers to the national directory in the platform zone (soft reference across zones). source records whether the link came from the rules or was set for the institution.

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | internal |
| History | effective |
| Scope | owned |
| Module | `regulation` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-REG-03, FR-REG-04 |
| Pages | REG-02 |
| Events | REG.PROFILE_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `regulatory_body_id` | `BINARY(16)` | no |  | Soft reference to regulatory_body (platform zone) |
| `body_code` | `VARCHAR(16)` | no |  | Denormalised code of the body, e.g. NECO |
| `relationship` | `VARCHAR(32)` | no |  | values: supervision, accreditation, licensing, curriculum, examination, admission, teacher_registration, professional_regulation, funding, affiliation |
| `covers` | `VARCHAR(200)` | yes |  | e.g. BECE and SSCE, UTME admissions, ND/HND programmes, teacher registration |
| `levels` | `JSON` | yes |  | Education levels the link applies to |
| `is_mandatory` | `BOOLEAN` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | values: rule, institution, import |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id, body_code, relationship, valid_from)
- Index: (tenant_id, body_code, relationship)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

