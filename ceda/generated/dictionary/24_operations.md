# OPS — Operations — estate, rooms, assets, maintenance, safety incidents, capital plan, transport, clubs, trips, meals, library and learning resources

The physical institution (FR-OPS-01–08, 101–107): buildings and rooms with accessibility, ICT and condition (Infrastructure 360 feeding infrastructure indicators), the asset register with inspections and predictive maintenance, maintenance requests (critical safety risk → Priority 1 to head and LGA), facility safety incidents, the multi-year capital plan and campus plan archive, transport with driver checks and boarding records, clubs and events with fair allocation, trips with consent gating, meals reconciled against attendance for the school feeding programme, library loans and textbook issue with textbook-to-learner ratios.

Module (system of record): `operations` · default zone: **ops** · default retention: `RS-OPS-7`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`building`](#ops-building) | ops | master | internal | lifecycle | Building on a campus (condition, structural safety, water, power, toilets by sex) |
| [`room`](#ops-room) | ops | master | internal | lifecycle | Room or space — Infrastructure 360 (classroom, lab, workshop, hall, ICT suite, hostel room, skills lab) |
| [`asset`](#ops-asset) | ops | master | internal | lifecycle | Asset register entry (custodian, location, value, condition, service and safety-check dates) |
| [`asset_inspection`](#ops-asset_inspection) | ops | event | internal | append | Technician inspection of an asset (mobile, offline, checklist and photos) or stock-take record |
| [`maintenance_request`](#ops-maintenance_request) | ops | transaction | internal | lifecycle | Maintenance request with safety-risk rating (critical → Priority 1 to head and LGA); preventive work orders |
| [`facility_incident`](#ops-facility_incident) | ops | transaction | confidential | lifecycle | Facility safety incident (location, severity, photos, follow-up) |
| [`capital_plan_item`](#ops-capital_plan_item) | ops | transaction | internal | lifecycle | Multi-year capital plan item linked to asset and building condition (cost estimate and priority) |
| [`transport_route`](#ops-transport_route) | ops | config | internal | lifecycle | Transport route with stops |
| [`vehicle`](#ops-vehicle) | ops | master | internal | lifecycle | Vehicle (registration, capacity, roadworthiness and insurance expiry) |
| [`transport_allocation`](#ops-transport_allocation) | ops | link | confidential | effective | Learner allocated to a route and stop (detention transport check uses it) |
| [`boarding_record`](#ops-boarding_record) | ops | event | confidential | append | Boarding or alighting record on a route |
| [`activity`](#ops-activity) | ops | config | internal | lifecycle | Club, activity or event with eligibility, capacity, fees and achievements |
| [`activity_enrolment`](#ops-activity_enrolment) | ops | link | confidential | lifecycle | Learner preference, allocation, waiting list and attendance for an activity |
| [`trip`](#ops-trip) | ops | transaction | internal | lifecycle | Trip or visit (planning, risk assessment, approval, consent, payment, on-the-day register) |
| [`trip_participant`](#ops-trip_participant) | ops | link | confidential | lifecycle | Learner on a trip (blocked without consent) and on-the-day register |
| [`meal_service`](#ops-meal_service) | ops | event | internal | lifecycle | Meals served per day and session (school feeding programme numbers reconciled against attendance) |
| [`dietary_requirement`](#ops-dietary_requirement) | ops | master | confidential | effective | Learner dietary requirement (allergy detail is health data — kept as a coded flag here) |
| [`library_item`](#ops-library_item) | ops | master | public | lifecycle | Library catalogue item (or link to an external library system) |
| [`library_loan`](#ops-library_loan) | ops | transaction | confidential | lifecycle | Library loan |
| [`learning_resource`](#ops-learning_resource) | ops | master | internal | lifecycle | Textbook or learning material title held in stock (government-supplied or institution-bought) by subject and level |
| [`resource_issue`](#ops-resource_issue) | ops | event | confidential | lifecycle | Issue, return, loss and condition of a learning resource per learner or class |

<a id="ops-building"></a>
## `building`

Building on a campus (condition, structural safety, water, power, toilets by sex)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-01, FR-OPS-105 |
| Pages | OPS-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `campus_id` → `campus` | `BINARY(16)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `built_year` | `SMALLINT` | yes |  |  |
| `condition_grade` | `VARCHAR(32)` | yes |  | code list `condition_grade` |
| `facilities` | `JSON` | yes |  | Toilets by sex, water, power, accessibility |
| `plan_document_ids` | `JSON` | yes |  | Campus plan archive over time |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `campus_id` → `campus` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-room"></a>
## `room`

Room or space — Infrastructure 360 (classroom, lab, workshop, hall, ICT suite, hostel room, skills lab)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-01, FR-TIM-06, FR-TVT-02, FR-HED-03 |
| Pages | OPS-01, TIM-04, TVT-02, HED-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `campus_id` → `campus` | `BINARY(16)` | no |  |  |
| `building_id` → `building` | `BINARY(16)` | yes |  |  |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | yes |  |  |
| `room_type` | `VARCHAR(32)` | no |  | code list `room_type` |
| `capacity` | `SMALLINT` | no |  |  |
| `accessibility` | `JSON` | yes |  | step_free, hearing_loop … |
| `condition_grade` | `VARCHAR(32)` | yes |  | code list `condition_grade` |
| `ict` | `JSON` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, campus_id, code)

- Soft reference `campus_id` → `campus` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-asset"></a>
## `asset`

Asset register entry (custodian, location, value, condition, service and safety-check dates)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-02, FR-TVT-02, FR-OPS-102 |
| Pages | OPS-02, TVT-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `asset_tag` | `VARCHAR(40)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `category` | `VARCHAR(32)` | no |  | code list `asset_category` |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `custodian_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `acquired_on` | `DATE` | yes |  |  |
| `value_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `condition_grade` | `VARCHAR(32)` | yes |  | code list `condition_grade` |
| `next_service_on` | `DATE` | yes |  |  |
| `safety_check_due_on` | `DATE` | yes |  | Equipment past this date cannot be allocated (FR-TVT-02) |
| `predicted_failure_on` | `DATE` | yes |  | Predictive maintenance estimate |
| `status` | `VARCHAR(32)` | no |  | values: in_use, in_store, under_repair, condemned, disposed, lost |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, asset_tag)

- Soft reference `custodian_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-asset_inspection"></a>
## `asset_inspection`

Technician inspection of an asset (mobile, offline, checklist and photos) or stock-take record

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-106, FR-OPS-02 |
| Pages | OPS-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `asset_id` → `asset` | `BINARY(16)` | no |  |  |
| `inspected_by` | `BINARY(16)` | no |  |  |
| `checklist` | `JSON` | no |  |  |
| `photo_document_ids` | `JSON` | yes |  |  |
| `condition_grade` | `VARCHAR(32)` | no |  | code list `condition_grade` |
| `inspected_at` | `DATETIME(6)` | no |  |  |
| `client_op_id` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-maintenance_request"></a>
## `maintenance_request`

Maintenance request with safety-risk rating (critical → Priority 1 to head and LGA); preventive work orders

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-03, FR-OPS-102 |
| Pages | OPS-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `asset_id` → `asset` | `BINARY(16)` | yes |  |  |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `description` | `TEXT` | no |  |  |
| `risk` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `is_preventive` | `BOOLEAN` | no |  |  |
| `reported_by` | `BINARY(16)` | no |  |  |
| `assigned_to` | `BINARY(16)` | yes |  |  |
| `due_on` | `DATE` | yes |  |  |
| `completed_at` | `DATETIME(6)` | yes |  |  |
| `cost_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: reported, triaged, scheduled, in_progress, completed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-facility_incident"></a>
## `facility_incident`

Facility safety incident (location, severity, photos, follow-up)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-103 |
| Pages | OPS-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `room_id` → `room` | `BINARY(16)` | yes |  |  |
| `location_text` | `VARCHAR(200)` | yes |  |  |
| `severity` | `VARCHAR(32)` | no |  | values: critical, high, moderate, info |
| `description` | `TEXT` | no |  |  |
| `photo_document_ids` | `JSON` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `follow_up` | `TEXT` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-capital_plan_item"></a>
## `capital_plan_item`

Multi-year capital plan item linked to asset and building condition (cost estimate and priority)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-104 |
| Pages | OPS-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `building_id` → `building` | `BINARY(16)` | yes |  |  |
| `asset_id` → `asset` | `BINARY(16)` | yes |  |  |
| `title` | `VARCHAR(300)` | no |  |  |
| `planned_year` | `SMALLINT` | no |  |  |
| `estimate_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `priority` | `SMALLINT` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: reported, triaged, scheduled, in_progress, completed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-transport_route"></a>
## `transport_route`

Transport route with stops

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-04 |
| Pages | OPS-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `stops` | `JSON` | no |  | Ordered stops with times and coordinates |
| `vehicle_id` → `vehicle` | `BINARY(16)` | yes |  |  |
| `driver_staff_id` → `staff` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `driver_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-vehicle"></a>
## `vehicle`

Vehicle (registration, capacity, roadworthiness and insurance expiry)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-04 |
| Pages | OPS-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `registration` | `VARCHAR(16)` | no |  |  |
| `capacity` | `SMALLINT` | no |  |  |
| `roadworthy_until` | `DATE` | yes |  |  |
| `insured_until` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, registration)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-transport_allocation"></a>
## `transport_allocation`

Learner allocated to a route and stop (detention transport check uses it)

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | confidential |
| History | effective |
| Scope | none |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-04, FR-BEH-111 |
| Pages | OPS-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `route_id` → `transport_route` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `stop_code` | `VARCHAR(16)` | no |  |  |
| `direction` | `VARCHAR(32)` | no |  | values: to_school, from_school |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, route_id, learner_id, direction, valid_from)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-boarding_record"></a>
## `boarding_record`

Boarding or alighting record on a route

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Partitioning | range_month on `boarded_on` |
| Requirements | FR-OPS-04 |
| Pages | OPS-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `route_id` → `transport_route` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `boarded_on` **PK** | `DATE` | no |  |  |
| `event` | `VARCHAR(32)` | no |  | values: boarded, alighted, no_show |
| `at` | `DATETIME(6)` | no |  |  |
| `recorded_by` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Soft reference `route_id` → `transport_route` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)
- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-activity"></a>
## `activity`

Club, activity or event with eligibility, capacity, fees and achievements

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-05, FR-OPS-101 |
| Pages | OPS-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `name` | `VARCHAR(300)` | no |  |  |
| `activity_kind` | `VARCHAR(32)` | no |  | values: club, sport, event, trip_series, holiday_programme |
| `eligibility_rule` | `JSON` | yes |  |  |
| `capacity` | `SMALLINT` | yes |  |  |
| `fee_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `allocation_method` | `VARCHAR(32)` | no |  | values: first_come, preference_lottery, priority_rules |
| `period_id` → `academic_period` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `period_id` → `academic_period` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-activity_enrolment"></a>
## `activity_enrolment`

Learner preference, allocation, waiting list and attendance for an activity

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-05, FR-OPS-101 |
| Pages | OPS-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `activity_id` → `activity` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `preference_rank` | `SMALLINT` | yes |  |  |
| `allocation` | `VARCHAR(32)` | no |  | values: preferred, allocated, waitlisted, declined, withdrawn |
| `waiting_position` | `SMALLINT` | yes |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | yes |  |  |
| `sessions_attended` | `SMALLINT` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, activity_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-trip"></a>
## `trip`

Trip or visit (planning, risk assessment, approval, consent, payment, on-the-day register)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-06, FR-STF-106 |
| Pages | OPS-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `destination` | `VARCHAR(300)` | no |  |  |
| `departs_at` | `DATETIME(6)` | no |  |  |
| `returns_at` | `DATETIME(6)` | no |  |  |
| `leader_staff_id` → `staff` | `BINARY(16)` | no |  | Must hold valid safeguarding training when gating is on |
| `risk_assessment_document_id` | `BINARY(16)` | yes |  |  |
| `workflow_instance_id` → `workflow_instance` | `BINARY(16)` | yes |  |  |
| `charge_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: planning, awaiting_approval, approved, consent_collection, departed, returned, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `leader_staff_id` → `staff` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-trip_participant"></a>
## `trip_participant`

Learner on a trip (blocked without consent) and on-the-day register

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-06 |
| Pages | OPS-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `trip_id` → `trip` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `consent_record_id` → `consent_record` | `BINARY(16)` | yes |  |  |
| `invoice_id` → `invoice` | `BINARY(16)` | yes |  |  |
| `present_out` | `BOOLEAN` | yes |  |  |
| `present_return` | `BOOLEAN` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, trip_id, learner_id)

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

<a id="ops-meal_service"></a>
## `meal_service`

Meals served per day and session (school feeding programme numbers reconciled against attendance)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-07 |
| Pages | OPS-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `served_on` | `DATE` | no |  |  |
| `meal_session` | `VARCHAR(32)` | no |  | values: breakfast, lunch, snack, dinner |
| `programme` | `VARCHAR(32)` | yes |  | code list `feeding_programme` |
| `meals_served` | `INT UNSIGNED` | no |  |  |
| `learners_present` | `INT UNSIGNED` | yes |  | From attendance |
| `menu` | `JSON` | yes |  |  |
| `variance_note` | `VARCHAR(500)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, served_on, meal_session)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-dietary_requirement"></a>
## `dietary_requirement`

Learner dietary requirement (allergy detail is health data — kept as a coded flag here)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | effective |
| Scope | derived: the learner's institution |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-07 |
| Pages | OPS-07 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `requirement` | `VARCHAR(32)` | no |  | code list `dietary_code` |
| `is_allergy` | `BOOLEAN` | no |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="ops-library_item"></a>
## `library_item`

Library catalogue item (or link to an external library system)

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-08 |
| Pages | OPS-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `authors` | `VARCHAR(500)` | yes |  |  |
| `isbn` | `VARCHAR(17)` | yes |  |  |
| `copies` | `SMALLINT` | no |  |  |
| `external_ref` | `VARCHAR(200)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-library_loan"></a>
## `library_loan`

Library loan

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `operations` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-OPS-08 |
| Pages | OPS-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `library_item_id` → `library_item` | `BINARY(16)` | no |  |  |
| `borrower_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `borrower_id` | `BINARY(16)` | no |  |  |
| `loaned_on` | `DATE` | no |  |  |
| `due_on` | `DATE` | no |  |  |
| `returned_on` | `DATE` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="ops-learning_resource"></a>
## `learning_resource`

Textbook or learning material title held in stock (government-supplied or institution-bought) by subject and level

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `operations` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-107 |
| Pages | OPS-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `subject_id` → `subject` | `BINARY(16)` | no |  |  |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `source` | `VARCHAR(32)` | no |  | values: government_supplied, institution_bought, donated |
| `stock` | `INT UNSIGNED` | no |  |  |
| `content_library_item_id` → `content_library_item` | `BINARY(16)` | yes |  | Digital resource linked to objectives |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `subject_id` → `subject` — cross-zone (ops → registry)
- Soft reference `content_library_item_id` → `content_library_item` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-resource_issue"></a>
## `resource_issue`

Issue, return, loss and condition of a learning resource per learner or class

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `operations` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-OPS-107 |
| Pages | OPS-08 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `resource_id` → `learning_resource` | `BINARY(16)` | no |  |  |
| `learner_id` → `learner` | `BINARY(16)` | yes |  |  |
| `class_group_id` → `class_group` | `BINARY(16)` | yes |  |  |
| `quantity` | `SMALLINT` | no |  |  |
| `issued_on` | `DATE` | no |  |  |
| `returned_on` | `DATE` | yes |  |  |
| `outcome` | `VARCHAR(32)` | yes |  | values: returned, lost, damaged, retained |
| `condition_grade` | `VARCHAR(32)` | yes |  | code list `condition_grade` |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `learner_id` → `learner` — cross-zone (ops → registry)

