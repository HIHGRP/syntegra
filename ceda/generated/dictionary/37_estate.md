# EST — Government property register, facility condition and usability, preventive maintenance and proactive actions

Every government property an institution occupies (change request CR-006): the land (site) with owner, title, area, boundary, fencing and encroachment; the buildings, rooms and equipment already held in operations (OPS); dated condition and usability assessments of each; planned preventive maintenance; and proactive actions the platform proposes to the head of institution — unsafe facilities in use, assessments overdue, maintenance due, deteriorating condition, equipment past its safety check — escalated to the LGA and the ministry when not acted on. The warehouse (DW) loads all of it for the state-wide infrastructure view of the Commissioner for Education.

Module (system of record): `estate` · default zone: **ops** · default retention: `RS-INS-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`property_site`](#ops-property_site) | ops | master | internal | lifecycle | Government property site (land) used by an institution — owner, title, area, boundary, fencing, encroachment, valuation |
| [`facility_assessment`](#ops-facility_assessment) | ops | event | internal | append | Dated condition and usability assessment of a site, building, room or item of equipment |
| [`maintenance_schedule`](#ops-maintenance_schedule) | ops | config | internal | lifecycle | Planned preventive maintenance task for a site, building, room or item of equipment (frequency, next due, responsible person) |
| [`facility_action`](#ops-facility_action) | ops | transaction | internal | lifecycle | Proactive action proposed to the head of institution, with owner, due date and escalation to the LGA and ministry |

<a id="ops-property_site"></a>
## `property_site`

Government property site (land) used by an institution — owner, title, area, boundary, fencing, encroachment, valuation

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `estate` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-EST-01 |
| Pages | EST-01, OPS-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `site_code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `campus_id` → `campus` | `BINARY(16)` | yes |  |  |
| `owner` | `VARCHAR(32)` | no |  | values: federal_government, state_government, local_government, community, mission_or_faith, private, leased |
| `title_document` | `VARCHAR(32)` | no |  | values: certificate_of_occupancy, right_of_occupancy, gazette, deed_of_assignment, deed_of_gift, survey_plan_only, customary, lease, none_or_unknown |
| `title_reference` | `VARCHAR(64)` | yes |  | C of O, gazette or survey plan number |
| `area_sqm` | `DECIMAL(14,2)` | yes |  |  |
| `location` | `POINT SRID 4326` | yes |  |  |
| `boundary` | `JSON` | yes |  | GeoJSON polygon of the surveyed boundary |
| `fenced` | `VARCHAR(32)` | no |  | values: fully_fenced, partly_fenced, not_fenced, unknown |
| `encroachment` | `VARCHAR(32)` | no |  | values: none, suspected, confirmed, in_dispute, resolved, unknown |
| `acquired_on` | `DATE` | yes |  |  |
| `valuation_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `valued_on` | `DATE` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, site_code)
- Index: (tenant_id, institution_id)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `campus_id` → `campus` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-facility_assessment"></a>
## `facility_assessment`

Dated condition and usability assessment of a site, building, room or item of equipment

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | owned |
| Module | `estate` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-EST-02 |
| Pages | EST-01, EST-02, OPS-01 |
| Events | EST.FACILITY_ASSESSED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `subject_kind` | `VARCHAR(32)` | no |  | values: site, building, room, asset |
| `subject_id` | `BINARY(16)` | no |  |  |
| `assessed_on` | `DATE` | no |  |  |
| `assessor_kind` | `VARCHAR(32)` | no |  | values: head_of_institution, estate_officer, engineer, quality_inspector, lga_officer, contractor, community |
| `assessed_by` | `BINARY(16)` | no |  |  |
| `condition_grade` | `VARCHAR(32)` | no |  | code list `condition_grade` |
| `usability` | `VARCHAR(32)` | no |  | values: fully_usable, usable_minor_repairs, usable_major_repairs, unsafe_restricted, unusable, condemned |
| `structural_risk` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `defects` | `JSON` | yes |  | Element (roof, walls, floor, doors, windows, wiring, plumbing …), defect and severity |
| `utilities` | `JSON` | yes |  | Water, power, sanitation and internet working at the time |
| `in_use` | `BOOLEAN` | no |  | Whether the facility is being used at the time of assessment |
| `learners_affected` | `INT UNSIGNED` | yes |  |  |
| `repair_estimate_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `photo_document_ids` | `JSON` | yes |  |  |
| `next_due_on` | `DATE` | yes |  | When it should be assessed again |
| `client_op_id` | `BINARY(16)` | yes |  | Offline capture (idempotent) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, subject_kind, subject_id, assessed_on)
- Index: (tenant_id, institution_id, assessed_on)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-maintenance_schedule"></a>
## `maintenance_schedule`

Planned preventive maintenance task for a site, building, room or item of equipment (frequency, next due, responsible person)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `estate` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-EST-03 |
| Pages | EST-02, OPS-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `subject_kind` | `VARCHAR(32)` | no |  | values: site, building, room, asset |
| `subject_id` | `BINARY(16)` | no |  |  |
| `task` | `VARCHAR(200)` | no |  |  |
| `task_kind` | `VARCHAR(32)` | no |  | values: inspection, servicing, statutory_test, cleaning, pest_control, roofing, plumbing, electrical, painting, generator_service, solar_service, borehole_service, fire_safety, replacement, other |
| `frequency_days` | `SMALLINT` | no |  |  |
| `last_done_on` | `DATE` | yes |  |  |
| `next_due_on` | `DATE` | no |  |  |
| `responsible_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `estimated_cost_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, institution_id, next_due_on)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `responsible_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-facility_action"></a>
## `facility_action`

Proactive action proposed to the head of institution, with owner, due date and escalation to the LGA and ministry  

One open action per rule and subject (dedupe_key); closed actions are kept. The platform proposes and escalates; the head decides what to do (FR-EST-04).

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `estate` |
| Origin | ceda |
| Retention | `RS-INS-PERM` |
| Requirements | FR-EST-04, FR-EST-05 |
| Pages | EST-02, EST-03 |
| Events | EST.ACTION_RAISED, EST.ACTION_ESCALATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `rule` | `VARCHAR(32)` | no |  | values: unsafe_in_use, assessment_overdue, never_assessed, maintenance_due, maintenance_overdue, condition_deteriorated, safety_check_overdue, predicted_failure, encroachment, no_title |
| `subject_kind` | `VARCHAR(32)` | no |  | values: site, building, room, asset |
| `subject_id` | `BINARY(16)` | no |  |  |
| `dedupe_key` | `VARCHAR(120)` | no |  | rule:subject while open; suffixed with the action id when closed |
| `title` | `VARCHAR(200)` | no |  |  |
| `detail` | `TEXT` | yes |  |  |
| `priority` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `owner_role` | `VARCHAR(16)` | no |  |  |
| `due_on` | `DATE` | no |  |  |
| `escalation_level` | `SMALLINT` | no |  | 0 institution, 1 LGA, 2 ministry |
| `escalated_at` | `DATETIME(6)` | yes |  |  |
| `maintenance_request_id` → `maintenance_request` | `BINARY(16)` | yes |  |  |
| `resolved_by` | `BINARY(16)` | yes |  |  |
| `resolved_at` | `DATETIME(6)` | yes |  |  |
| `resolution` | `TEXT` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, acknowledged, in_progress, done, dismissed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, dedupe_key)
- Index: (tenant_id, institution_id, status)
- Index: (tenant_id, status, due_on)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

