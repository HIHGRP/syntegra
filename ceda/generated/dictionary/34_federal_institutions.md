# FED — Federal unity colleges and federal special training institutions — owning bodies, their structures, institutions

Federal institutions that are not state schools (change request CR-005): the Federal Government Colleges, Federal Government Girls' Colleges and Federal Science and Technical Colleges (the unity schools), and the federal special training institutions owned by ministries and parastatals — colleges of education, agriculture, forestry, fisheries, animal health and land resources; co-operative, statistics and surveying schools; aviation, maritime and petroleum training; policy and teacher-training institutes. They are held in a national sector registry (ng-fed, decision CD-23) under their owning body and that body's own structure, which is also the access hierarchy. Learners are registered on the single registration path; the institution master (domain INS) keeps name, location and levels.

Module (system of record): `federal_institutions` · default zone: **registry** · default retention: `RS-INS-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`federal_body`](#registry-federal_body) | registry | master | internal | lifecycle | Federal ministry, department, parastatal or commission that owns or supervises federal institutions |
| [`federal_body_unit`](#registry-federal_body_unit) | registry | master | internal | lifecycle | Unit of a federal body's own structure (department, directorate, division, geopolitical zone) |
| [`federal_institution`](#registry-federal_institution) | registry | master | internal | lifecycle | Federal profile of a unity college or federal special training institution |

<a id="registry-federal_body"></a>
## `federal_body`

Federal ministry, department, parastatal or commission that owns or supervises federal institutions  

scope_node_id is the body's own node (level agency) under the registry root.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `federal_institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-FED-01 |
| Pages | FED-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(16)` | no |  | e.g. FME, FMAFS, FMOH, FMAV, FMT |
| `name` | `VARCHAR(300)` | no |  |  |
| `category` | `VARCHAR(32)` | no |  | values: ministry, department, parastatal, commission, agency |
| `parent_body_id` → `federal_body` | `BINARY(16)` | yes |  | e.g. a parastatal's supervising ministry |
| `website` | `VARCHAR(2048)` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code)

<a id="registry-federal_body_unit"></a>
## `federal_body_unit`

Unit of a federal body's own structure (department, directorate, division, geopolitical zone)  

scope_node_id is the unit's own node (level formation), a child of its parent unit or of the body.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `federal_institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-FED-01, FR-FED-03 |
| Pages | FED-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `body_id` → `federal_body` | `BINARY(16)` | no |  |  |
| `parent_unit_id` → `federal_body_unit` | `BINARY(16)` | yes |  |  |
| `unit_type` | `VARCHAR(32)` | no |  | values: department, directorate, division, unit, zone |
| `code` | `VARCHAR(40)` | no |  | Unique within the body |
| `name` | `VARCHAR(300)` | no |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, body_id, code)
- Index: (tenant_id, parent_unit_id)

<a id="registry-federal_institution"></a>
## `federal_institution`

Federal profile of a unity college or federal special training institution  

scope_node_id is the institution's node, a child of its owning unit's node.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `federal_institutions` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-FED-02, FR-FED-03, FR-FED-04 |
| Pages | FED-01, REG-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `body_id` → `federal_body` | `BINARY(16)` | no |  |  |
| `unit_id` → `federal_body_unit` | `BINARY(16)` | no |  |  |
| `institution_type` | `VARCHAR(32)` | no |  | values: unity_college, unity_college_girls, unity_college_boys, science_technical_college, special_needs_college, college_of_education, college_of_education_technical, college_of_education_special, college_of_agriculture, college_of_forestry, college_of_fisheries, college_of_animal_health, college_of_land_resources, college_of_veterinary_laboratory, cooperative_college, school_of_statistics, school_of_surveying, aviation_college, maritime_academy, petroleum_training_institute, policy_institute, teacher_training_institute, other_special |
| `geopolitical_zone` | `VARCHAR(32)` | no |  | values: north_central, north_east, north_west, south_east, south_south, south_west |
| `gender_intake` | `VARCHAR(32)` | yes |  | values: mixed, boys, girls |
| `day_boarding` | `VARCHAR(32)` | yes |  | values: day, boarding, mixed |
| `admission_basis` | `VARCHAR(32)` | yes |  | e.g. national_common_entrance for unity colleges · values: national_common_entrance, utme, direct_entry, merit_and_quota, agency_recruitment, other |
| `established_year` | `SMALLINT` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, institution_id)
- Index: (tenant_id, body_id)
- Index: (tenant_id, unit_id)
- Index: (tenant_id, institution_type)

