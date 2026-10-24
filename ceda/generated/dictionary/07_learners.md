# LRN — Learner 360, state enrolment register, transfer and Education Passport

One lifelong record per learner from early years to continuing education (FR-LRN-01–16), held in the state registry so that public and private institutions, the state, the SDAF census and the certificate registry all see the same person (decision CD-01). The state enrolment register records which institution holds each learner and when; it is the basis for transfers, child-missing-education referrals, the census date rule ("billed once, by the institution holding the enrolment") and state learner search. Class membership and everything operational live in the ops zone of the institution's tenant and refer back to learner_id and enrolment_id.

Module (system of record): `learners` · default zone: **registry** · default retention: `RS-LRN-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`learner`](#registry-learner) | registry | master | confidential | lifecycle | Learner 360 master — one row per person, lifelong |
| [`enrolment`](#registry-enrolment) | registry | transaction | confidential | lifecycle | State enrolment register — learner enrolled at an institution (and level, programme) for a period |
| [`learner_transfer`](#registry-learner_transfer) | registry | transaction | confidential | lifecycle | Transfer of a learner between institutions (within or across tenants and states), with DSL/SENCO handover acknowledgement |
| [`cme_referral`](#registry-cme_referral) | registry | transaction | confidential | lifecycle | Child-missing-education referral to the LGA attendance desk (compulsory-age leaver with unknown destination) |
| [`passport_entry`](#registry-passport_entry) | registry | projection | confidential | lifecycle | Education Passport entry — qualification, certificate, badge, competency, credit, CPD or digital-skills milestone |
| [`passport_share`](#registry-passport_share) | registry | transaction | confidential | lifecycle | Consented, time-limited, revocable share of a learner's Education Passport |
| [`passport_view`](#registry-passport_view) | registry | event | confidential | append | Verification log of a passport share (holder sees who verified) |
| [`external_exam_record`](#registry-external_exam_record) | registry | master | confidential | lifecycle | Verified external examination result linked to Learner 360 (WAEC, NECO, NABTEB, JAMB) — linked, never re-issued |
| [`historical_record_import`](#registry-historical_record_import) | registry | transaction | confidential | lifecycle | Authorised historical record received from a previous institution at enrolment (no re-supply by families) |

<a id="registry-learner"></a>
## `learner`

Learner 360 master — one row per person, lifelong  

Identity attributes only. National identifiers are in external_identifier; special-category detail is in the vault. A merged record keeps its row as an alias (status merged, merged_into set) so old references resolve. Historic learners created from digitised archives carry is_historic = true.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: visible through an enrolment at an institution inside the grant's subtree, or a purpose-bound state grant |
| Module | `learners` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-01, FR-LRN-03, FR-LRN-05, FR-LRN-06, FR-LRN-07, FR-LRN-12, FR-CMD-107, FR-DOC-108, FR-LRN-102 |
| Pages | LRN-01, LRN-02, LRN-04, CMD-101, PUB-03, HOM-05 |
| Events | LRN.CREATED, LRN.UPDATED, LRN.MERGED, LRN.VIEWED_SPECIAL |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `global_learner_id` | `CHAR(16)` | no |  | LRN-NNNN-NNNN-CC, assigned at creation from the state's leased block, never reused |
| `legal_given_name` | `VARCHAR(200)` | no |  |  |
| `legal_middle_names` | `VARCHAR(200)` | yes |  |  |
| `legal_family_name` | `VARCHAR(200)` | no |  |  |
| `preferred_name` | `VARCHAR(200)` | yes |  |  |
| `name_phonetic` | `VARCHAR(120)` | no |  | Double Metaphone keys + Nigerian name-variant keys for blocking |
| `date_of_birth` | `DATE` | no |  |  |
| `dob_precision` | `VARCHAR(32)` | no |  | Displaced and historic learners may have month or year only · values: day, month, year |
| `sex` | `VARCHAR(32)` | no |  | code list `sex` |
| `nationality` | `CHAR(2)` | yes |  |  |
| `state_of_origin` | `VARCHAR(6)` | yes |  |  |
| `home_languages` | `JSON` | yes |  | code list `language` |
| `photo_document_id` | `BINARY(16)` | yes | restricted | Records zone; restricted |
| `is_historic` | `BOOLEAN` | no |  | Created from a digitised archive (FR-DOC-108) |
| `is_minimal_documentation` | `BOOLEAN` | no |  | Temporary enrolment (IDP camps); identity matching reconciles later |
| `identity_verified_level` | `VARCHAR(32)` | no |  | values: unverified, document_seen, nin_verified, archive_verified |
| `status` | `VARCHAR(32)` | no |  | values: registered, active, left, deceased, merged |
| `merged_into` → `learner` | `BINARY(16)` | yes |  |  |
| `deceased_on` | `DATE` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, global_learner_id)
- Index: (tenant_id, legal_family_name, date_of_birth)
- Index: (tenant_id, name_phonetic)
- Index: (tenant_id, date_of_birth)

<a id="registry-enrolment"></a>
## `enrolment`

State enrolment register — learner enrolled at an institution (and level, programme) for a period  

scope_node_id = the institution's node. A learner has at most one active primary enrolment per period (dual registration is a second, non-primary enrolment). class_group_id refers to the ops zone (soft).

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `learners` |
| Origin | appj |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-08, FR-LRN-09, FR-LRN-11, FR-SUB-104, FR-PVT-114, FR-ACA-107 |
| Pages | LRN-07, LRN-09, LRN-05, ATT-01, SUB-102 |
| Events | ENR.STARTED, ENR.ENDED, LRN.LEFT |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `operating_tenant_id` | `BINARY(16)` | no |  | Tenant whose ops zone holds the operational record |
| `education_level` | `VARCHAR(32)` | no |  | code list `education_level` |
| `programme_id` → `programme` | `BINARY(16)` | yes |  |  |
| `class_group_id` → `class_group` | `BINARY(16)` | yes |  | Ops-zone class (arm) for the session |
| `cohort_label` | `VARCHAR(60)` | yes |  | Intake cohort, e.g. 2026/2027 ND1 |
| `is_primary` | `BOOLEAN` | no |  |  |
| `basis` | `VARCHAR(32)` | no |  | values: admission, transfer, promotion, re_enrolment, temporary, repeat |
| `start_on` | `DATE` | no |  |  |
| `end_on` | `DATE` | yes |  |  |
| `leaving_reason` | `VARCHAR(32)` | yes |  | code list `leaving_reason` |
| `destination` | `JSON` | yes |  | Destination institution, employment, unknown … |
| `is_over_capacity_approved` | `BOOLEAN` | no |  | Head approval recorded when capacity is exceeded |
| `status` | `VARCHAR(32)` | no |  | values: pending, active, completed, withdrawn, transferred, suspended |
| `active_primary_key` | `BINARY(16)` | yes |  | = learner_id when status active and is_primary, else NULL (one active primary enrolment) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, active_primary_key)
- Index: (tenant_id, learner_id, start_on)
- Index: (tenant_id, institution_id, status)

- Soft reference `class_group_id` → `class_group` — cross-zone (registry → ops)

- Check `dates`: `end_on IS NULL OR end_on >= start_on`

<a id="registry-learner_transfer"></a>
## `learner_transfer`

Transfer of a learner between institutions (within or across tenants and states), with DSL/SENCO handover acknowledgement

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `learners` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-10, FR-SAF-08, FR-LRN-16 |
| Pages | LRN-05 |
| Events | LRN.TRANSFERRED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `from_enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `to_institution_id` → `institution` | `BINARY(16)` | yes |  | NULL when leaving the state (exchange) |
| `to_enrolment_id` → `enrolment` | `BINARY(16)` | yes |  |  |
| `exchange_transfer_id` → `exchange_transfer` | `BINARY(16)` | yes |  | Cross-state or international records exchange |
| `requested_by` → `app_user` | `BINARY(16)` | no |  |  |
| `effective_on` | `DATE` | no |  |  |
| `records_package` | `JSON` | yes |  | Datasets transferred per policy |
| `dsl_handover_due_on` | `DATE` | yes |  |  |
| `dsl_acknowledged_at` | `DATETIME(6)` | yes |  | Safeguarding file acknowledged by receiving DSL |
| `senco_acknowledged_at` | `DATETIME(6)` | yes |  | SEND file acknowledged by receiving SENCO |
| `status` | `VARCHAR(32)` | no |  | values: requested, accepted, records_sent, handover_pending, completed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-cme_referral"></a>
## `cme_referral`

Child-missing-education referral to the LGA attendance desk (compulsory-age leaver with unknown destination)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `learners` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-11, FR-PVT-115 |
| Pages | LRN-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `lga_scope_id` → `scope_node` | `BINARY(16)` | no |  |  |
| `reason` | `VARCHAR(500)` | no |  |  |
| `assigned_to` → `app_user` | `BINARY(16)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | yes |  | values: located_enrolled, located_not_enrolled, moved_out_of_state, not_located, deceased |
| `closed_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-passport_entry"></a>
## `passport_entry`

Education Passport entry — qualification, certificate, badge, competency, credit, CPD or digital-skills milestone

| | |
|---|---|
| Zone | registry |
| Kind | projection |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the holder (learner) and their authorised viewers |
| Module | `learners` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-15, FR-TVT-05, FR-LRN-101, FR-P16-103, FR-LMS-122 |
| Pages | LRN-06, TVT-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `entry_kind` | `VARCHAR(32)` | no |  | values: qualification, certificate, transcript, badge, competency, credit, cpd, digital_skill, guidance |
| `source_kind` | `VARCHAR(40)` | no |  |  |
| `source_id` | `BINARY(16)` | no |  | Certificate, badge award, competency record, training completion … (soft) |
| `title` | `VARCHAR(300)` | no |  |  |
| `issuer_name` | `VARCHAR(300)` | yes |  |  |
| `awarded_on` | `DATE` | yes |  |  |
| `credential` | `JSON` | yes |  | Open Badges 3.0 / W3C VC 2.0 document when issued |
| `is_verified` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, learner_id, source_kind, source_id)

<a id="registry-passport_share"></a>
## `passport_share`

Consented, time-limited, revocable share of a learner's Education Passport

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the holder |
| Module | `learners` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-15 |
| Pages | LRN-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `recipient_name` | `VARCHAR(300)` | no |  |  |
| `recipient_email` | `VARCHAR(254)` | yes |  |  |
| `entries` | `JSON` | no |  | Passport entries included |
| `token_hash` | `BINARY(32)` | no |  |  |
| `expires_at` | `DATETIME(6)` | no |  |  |
| `revoked_at` | `DATETIME(6)` | yes |  |  |
| `view_count` | `INT UNSIGNED` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, token_hash)

<a id="registry-passport_view"></a>
## `passport_view`

Verification log of a passport share (holder sees who verified)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `learners` |
| Origin | ceda |
| Retention | `RS-VERIFY` |
| Requirements | FR-LRN-15 |
| Pages | LRN-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `share_id` → `passport_share` | `BINARY(16)` | no |  |  |
| `viewed_at` | `DATETIME(6)` | no |  |  |
| `ip_country` | `CHAR(2)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-external_exam_record"></a>
## `external_exam_record`

Verified external examination result linked to Learner 360 (WAEC, NECO, NABTEB, JAMB) — linked, never re-issued

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the learner |
| Module | `learners` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-CER-114, FR-HED-01, FR-P16-101 |
| Pages | HED-02, CER-03, LRN-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `exam_body` | `VARCHAR(32)` | no |  | code list `exam_body` |
| `exam_year` | `SMALLINT` | no |  |  |
| `candidate_number_hmac` | `BINARY(32)` | yes |  | Lookup token of the candidate number |
| `results` | `JSON` | no |  | Subject → grade, as verified |
| `verified_at` | `DATETIME(6)` | no |  |  |
| `verification_ref` | `VARCHAR(128)` | no |  |  |
| `holder_consents_display` | `BOOLEAN` | no |  | Shown on verification results only with consent |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-historical_record_import"></a>
## `historical_record_import`

Authorised historical record received from a previous institution at enrolment (no re-supply by families)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `learners` |
| Origin | ceda |
| Retention | `RS-LRN-PERM` |
| Requirements | FR-LRN-16 |
| Pages | LRN-07, LRN-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `enrolment_id` → `enrolment` | `BINARY(16)` | no |  |  |
| `source_institution_id` → `institution` | `BINARY(16)` | yes |  |  |
| `source_system` | `VARCHAR(120)` | yes |  |  |
| `datasets` | `JSON` | no |  | Results, attendance summary, SEND/safeguarding handover flags |
| `received_at` | `DATETIME(6)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: uploaded, mapped, validating, validated, matching, staged, committed, rolled_back, failed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

