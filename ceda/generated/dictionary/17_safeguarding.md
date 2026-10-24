# SAF — Safeguarding — concerns, cases, chronologies, referrals, secure sharing, allegations about adults and community reporting

Special-category data in the vault zone: its own schema, database account and key; excluded from search, CDC to the warehouse, AI training and every external messaging channel (MFS §2.2, §9.4, §18.9, FR-SAF-01–09, 101–108). Any staff member can record a concern and then sees only a receipt; the DSL and named users see cases; every view, export and print is audited. Allegations, low-level concerns and self-referrals about adults are a separate restricted area that bypasses the head when the head is the subject. Community reports are anonymous by default and store no IP or device data. Area dashboards show counts only, with groups under 10 suppressed.

Module (system of record): `safeguarding` · default zone: **vault** · default retention: `RS-SAF`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`safeguarding_concern`](#vault-safeguarding_concern) | vault | event | special | append | Concern recorded by any adult (the reporter sees only a receipt afterwards) |
| [`safeguarding_case`](#vault-safeguarding_case) | vault | master | special | lifecycle | Safeguarding 360 case (risk assessment, actions, referrals, meetings, reviews, closure with sign-off) |
| [`safeguarding_entry`](#vault-safeguarding_entry) | vault | event | special | append | Chronology entry — concern, action, decision, agency contact, meeting, review (encrypted text, append-only) |
| [`safeguarding_referral`](#vault-safeguarding_referral) | vault | transaction | special | lifecycle | External referral (police, social welfare, health, NGO) with outcome |
| [`case_access_grant`](#vault-case_access_grant) | vault | link | special | effective | Named need-to-know access to a case (DSL deputies and explicitly granted users) |
| [`case_access_log`](#vault-case_access_log) | vault | event | special | append | Every view, export and print of a vault record (shown as the access log on the case) |
| [`case_share`](#vault-case_share) | vault | transaction | special | lifecycle | Time-limited, watermarked share of selected chronology entries or a case bundle with a named professional |
| [`staff_case`](#vault-staff_case) | vault | master | special | lifecycle | Allegation, low-level concern or self-referral about an adult (restricted area; head, LGA designated officer, named HR) |
| [`staff_case_entry`](#vault-staff_case_entry) | vault | event | special | append | Chronology entry, decision or document on a staff case (hashed, tamper-evident, append-only) |
| [`reporting_form`](#ops-reporting_form) | ops | config | internal | versioned | Community reporting form (branding, fields, languages; published by link, QR poster, website embed, WhatsApp keyword) |
| [`community_report`](#vault-community_report) | vault | transaction | special | lifecycle | Report received through a community form — anonymous by default; no IP or device data; reply by one-time code |
| [`community_report_reply`](#vault-community_report_reply) | vault | event | special | append | Two-way message on an anonymous community report |

<a id="vault-safeguarding_concern"></a>
## `safeguarding_concern`

Concern recorded by any adult (the reporter sees only a receipt afterwards)

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | owned |
| Module | `safeguarding` |
| Origin | ceda |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-01, FR-SAF-02, FR-SAF-04, FR-WEL-02, FR-WEL-101 |
| Pages | SAF-01, SAF-02 |
| Events | SAF.CONCERN_RAISED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `case_id` → `safeguarding_case` | `BINARY(16)` | yes |  | Linked on triage |
| `category` | `VARCHAR(32)` | no |  | From the jurisdiction pack (Nigerian default) · code list `concern_category` |
| `reported_by` | `BINARY(16)` | no |  |  |
| `source` | `VARCHAR(32)` | no |  | values: staff, learner, parent, community_report, wellbeing_keyword, agency |
| `body` | `MEDIUMBLOB` | no | special | What was seen or heard (encrypted, per-record key) |
| `body_map` | `JSON` | yes |  | Body-map annotations (no free text) |
| `occurred_at` | `DATETIME(6)` | yes |  |  |
| `receipt_code` | `VARCHAR(16)` | no |  | Shown to the reporter |
| `community_report_id` → `community_report` | `BINARY(16)` | yes |  |  |
| `wellbeing_concern_id` → `wellbeing_concern` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, receipt_code)

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-safeguarding_case"></a>
## `safeguarding_case`

Safeguarding 360 case (risk assessment, actions, referrals, meetings, reviews, closure with sign-off)  

The case reference (SG-<year>-<seq>) contains no learner data. AI may summarise for the DSL; it never sets risk or outcome.

| | |
|---|---|
| Zone | vault |
| Kind | master |
| Classification | special |
| History | lifecycle |
| Scope | owned |
| Module | `safeguarding` |
| Origin | appj |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-03, FR-SAF-05, FR-SAF-06, FR-SAF-08, FR-SAF-09 |
| Pages | SAF-02, SAF-03 |
| Events | SAF.CASE_UPDATED, SAF.CASE_VIEWED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `case_reference` | `VARCHAR(20)` | no |  | SG-YYYY-NNNN |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `dsl_user_id` | `BINARY(16)` | no |  |  |
| `risk_level` | `VARCHAR(32)` | yes |  | Set by the DSL only · code list `risk_level` |
| `opened_at` | `DATETIME(6)` | no |  |  |
| `review_due_on` | `DATE` | yes |  |  |
| `closure_reason` | `MEDIUMBLOB` | yes | special |  |
| `closed_at` | `DATETIME(6)` | yes |  |  |
| `closed_signed_by` | `BINARY(16)` | yes |  |  |
| `transferred_to_institution_id` | `BINARY(16)` | yes |  | DSL-to-DSL transfer |
| `transfer_acknowledged_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, case_reference)

- Soft reference `learner_id` → `learner` — cross-zone (vault → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-safeguarding_entry"></a>
## `safeguarding_entry`

Chronology entry — concern, action, decision, agency contact, meeting, review (encrypted text, append-only)

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | none |
| Module | `safeguarding` |
| Origin | appj |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-03, FR-SAF-05 |
| Pages | SAF-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `case_id` → `safeguarding_case` | `BINARY(16)` | no |  |  |
| `entry_kind` | `VARCHAR(32)` | no |  | values: concern, action, decision, agency_contact, meeting, review, note, document |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `author_user_id` | `BINARY(16)` | no |  |  |
| `body` | `MEDIUMBLOB` | no | special |  |
| `source_ref` | `JSON` | yes |  | Linked concern, attendance or behaviour record the DSL may see |
| `document_ids` | `JSON` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="vault-safeguarding_referral"></a>
## `safeguarding_referral`

External referral (police, social welfare, health, NGO) with outcome

| | |
|---|---|
| Zone | vault |
| Kind | transaction |
| Classification | special |
| History | lifecycle |
| Scope | none |
| Module | `safeguarding` |
| Origin | ceda |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-05 |
| Pages | SAF-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `case_id` → `safeguarding_case` | `BINARY(16)` | no |  |  |
| `agency` | `VARCHAR(200)` | no |  |  |
| `agency_contact` | `MEDIUMBLOB` | yes | special |  |
| `referred_at` | `DATETIME(6)` | no |  |  |
| `legal_basis` | `VARCHAR(32)` | no |  | values: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests |
| `outcome` | `MEDIUMBLOB` | yes | special |  |
| `status` | `VARCHAR(32)` | no |  | values: drafted, sent, acknowledged, accepted, declined, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="vault-case_access_grant"></a>
## `case_access_grant`

Named need-to-know access to a case (DSL deputies and explicitly granted users)

| | |
|---|---|
| Zone | vault |
| Kind | link |
| Classification | special |
| History | effective |
| Scope | none |
| Module | `safeguarding` |
| Origin | ceda |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-06 |
| Pages | SAF-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `case_kind` | `VARCHAR(32)` | no |  | values: safeguarding_case, staff_case, community_report, send_profile |
| `case_id` | `BINARY(16)` | no |  |  |
| `user_id` | `BINARY(16)` | no |  |  |
| `granted_by` | `BINARY(16)` | no |  |  |
| `reason` | `VARCHAR(500)` | no |  |  |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, case_kind, case_id, user_id, valid_from)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="vault-case_access_log"></a>
## `case_access_log`

Every view, export and print of a vault record (shown as the access log on the case)

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | none |
| Module | `safeguarding` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Partitioning | range_month on `accessed_at` |
| Requirements | FR-SAF-06, FR-LRN-13 |
| Pages | SAF-03, SAF-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `case_kind` | `VARCHAR(32)` | no |  | values: safeguarding_case, staff_case, community_report, send_profile |
| `case_id` | `BINARY(16)` | no |  |  |
| `user_id` | `BINARY(16)` | no |  |  |
| `access` | `VARCHAR(32)` | no |  | values: view, export, print, share |
| `purpose_code` | `VARCHAR(40)` | no |  |  |
| `accessed_at` **PK** | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="vault-case_share"></a>
## `case_share`

Time-limited, watermarked share of selected chronology entries or a case bundle with a named professional

| | |
|---|---|
| Zone | vault |
| Kind | transaction |
| Classification | special |
| History | lifecycle |
| Scope | none |
| Module | `safeguarding` |
| Origin | ceda |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-107 |
| Pages | SAF-03, SAF-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `case_id` → `safeguarding_case` | `BINARY(16)` | no |  |  |
| `recipient_name` | `MEDIUMBLOB` | no | special |  |
| `recipient_email_hmac` | `BINARY(32)` | no |  |  |
| `purpose` | `VARCHAR(300)` | no |  |  |
| `legal_basis` | `VARCHAR(32)` | no |  | values: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests |
| `entry_ids` | `JSON` | no |  |  |
| `bundle_hash` | `BINARY(32)` | no |  |  |
| `token_hash` | `BINARY(32)` | no |  |  |
| `expires_at` | `DATETIME(6)` | no |  |  |
| `revoked_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, token_hash)

<a id="vault-staff_case"></a>
## `staff_case`

Allegation, low-level concern or self-referral about an adult (restricted area; head, LGA designated officer, named HR)  

An allegation about the head is routed to the LGA or state and hidden from the head (scope_node_id = LGA node).

| | |
|---|---|
| Zone | vault |
| Kind | master |
| Classification | special |
| History | lifecycle |
| Scope | owned |
| Module | `safeguarding` |
| Origin | appj |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-102, FR-SAF-103, FR-SAF-07 |
| Pages | SAF-101 |
| Events | SAF.STAFF_CASE_OPENED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `case_reference` | `VARCHAR(20)` | no |  | SC-YYYY-NNNN |
| `subject_staff_id` | `BINARY(16)` | no |  | Staff member concerned (registry) |
| `case_kind` | `VARCHAR(32)` | no |  | values: allegation, low_level_concern, self_referral |
| `is_about_head` | `BOOLEAN` | no |  |  |
| `designated_officer_user_id` | `BINARY(16)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | yes |  | substantiated, unsubstantiated, unfounded, false, malicious · values: substantiated, unsubstantiated, unfounded, false, malicious |
| `trcn_referral_at` | `DATETIME(6)` | yes |  |  |
| `police_informed_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, case_reference)
- Index: (tenant_id, subject_staff_id)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-staff_case_entry"></a>
## `staff_case_entry`

Chronology entry, decision or document on a staff case (hashed, tamper-evident, append-only)

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | none |
| Module | `safeguarding` |
| Origin | appj |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-102 |
| Pages | SAF-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `staff_case_id` → `staff_case` | `BINARY(16)` | no |  |  |
| `entry_kind` | `VARCHAR(32)` | no |  | values: concern, action, decision, agency_contact, meeting, review, note, document |
| `author_user_id` | `BINARY(16)` | no |  |  |
| `body` | `MEDIUMBLOB` | no | special |  |
| `document_ids` | `JSON` | yes |  |  |
| `content_hash` | `BINARY(32)` | no |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-reporting_form"></a>
## `reporting_form`

Community reporting form (branding, fields, languages; published by link, QR poster, website embed, WhatsApp keyword)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `safeguarding` |
| Origin | appj |
| Retention | `RS-CONFIG` |
| Requirements | FR-SAF-101, FR-SAF-104 |
| Pages | SAF-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `fields` | `JSON` | no |  |  |
| `languages` | `JSON` | no |  | code list `language` |
| `branding` | `JSON` | yes |  |  |
| `public_slug` | `VARCHAR(64)` | no |  |  |
| `whatsapp_keyword` | `VARCHAR(32)` | yes |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, public_slug)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-community_report"></a>
## `community_report`

Report received through a community form — anonymous by default; no IP or device data; reply by one-time code

| | |
|---|---|
| Zone | vault |
| Kind | transaction |
| Classification | special |
| History | lifecycle |
| Scope | owned |
| Module | `safeguarding` |
| Origin | appj |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-101, FR-SAF-104 |
| Pages | SAF-102, SAF-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `form_id` → `reporting_form` | `BINARY(16)` | yes |  |  |
| `form_version` | `INT UNSIGNED` | no |  |  |
| `answers` | `MEDIUMBLOB` | no | special | Field-level encrypted answers |
| `reporter_identity` | `MEDIUMBLOB` | yes | special | Only when the reporter volunteers it |
| `reply_code_hash` | `BINARY(32)` | no |  | One-time code for anonymous two-way replies |
| `received_at` | `DATETIME(6)` | no |  |  |
| `triaged_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, resolved, dismissed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `form_id` → `reporting_form` — declared soft
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="vault-community_report_reply"></a>
## `community_report_reply`

Two-way message on an anonymous community report

| | |
|---|---|
| Zone | vault |
| Kind | event |
| Classification | special |
| History | append |
| Scope | none |
| Module | `safeguarding` |
| Origin | ceda |
| Retention | `RS-SAF` |
| Requirements | FR-SAF-104 |
| Pages | SAF-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `report_id` → `community_report` | `BINARY(16)` | no |  |  |
| `direction` | `VARCHAR(32)` | no |  | values: outbound, inbound |
| `body` | `MEDIUMBLOB` | no | special |  |
| `author_user_id` | `BINARY(16)` | yes |  | Staff author (NULL for the reporter) |
| `sent_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

