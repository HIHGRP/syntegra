# FCL — Fee-clearance due diligence — learner obligations register, clearance checks, admission decisions and disputes

Before a learner with a previous enrolment is admitted or transferred anywhere in the ecosystem, the receiving institution checks whether the learner owes fees or other dues to any other institution (change request CR-001). Each institution's ledger (ops zone, domain FIN) publishes outstanding obligations to this state-wide register as summaries backed by issued invoices; the register therefore spans public and private tenants without exposing ledgers. The check informs a human admission decision and notifies the creditor — it never refuses admission, delays the transfer of records or restricts attendance by itself (MFS principle P9; admission refusal is human-only). Learners entering public basic education, and learners the head identifies as SEND, safeguarding, in care or displaced, are always admitted. Families see every check and can dispute any claim; stale claims expire; SDAF arrears never appear here (state revenue only). Repeated transfers that leave unsettled obligations are flagged for state review — the abuse the register exists to stop — and creditors that publish unsupported claims are visible through upheld disputes.

Module (system of record): `clearance` · default zone: **registry** · default retention: `RS-FIN`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`learner_obligation`](#registry-learner_obligation) | registry | transaction | restricted | lifecycle | Outstanding obligation of a learner's payer to an institution (fees or other dues), published from the creditor's ledger |
| [`obligation_dispute`](#registry-obligation_dispute) | registry | transaction | restricted | lifecycle | Dispute of a published obligation by the family, the admitting institution or the creditor (resolved by LGA or state) |
| [`clearance_check`](#registry-clearance_check) | registry | event | restricted | append | Clearance check run for an incoming learner (purpose-bound, logged, visible to the family) |
| [`clearance_decision`](#registry-clearance_decision) | registry | event | restricted | append | Human admission decision recorded on a clearance check (or the automatic protection of a learner) |

<a id="registry-learner_obligation"></a>
## `learner_obligation`

Outstanding obligation of a learner's payer to an institution (fees or other dues), published from the creditor's ledger  

scope_node_id is the creditor institution's node. One open obligation per learner × creditor × kind; the amount is re-published from the ledger (never typed in) except for manual claims with evidence.

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `clearance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-FCL-01, FR-FCL-07 |
| Pages | FCL-02, FCL-01 |
| Events | FCL.OBLIGATION_PUBLISHED, FCL.OBLIGATION_SETTLED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `creditor_institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `creditor_tenant_id` | `BINARY(16)` | no |  | Operating tenant whose ledger holds the invoices |
| `obligation_kind` | `VARCHAR(32)` | no |  | values: tuition_fees, boarding, examination_fees, transport, meals, books_and_materials, uniform, development_levy, damaged_property, library, other_dues |
| `payer_kind` | `VARCHAR(32)` | no |  | values: learner, family, guardian, sponsor, funder, government, employer, institution |
| `periods` | `JSON` | yes |  | Billing periods covered, e.g. 2025/26-T2, 2025/26-T3 |
| `amount_outstanding_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `oldest_due_on` | `DATE` | no |  |  |
| `evidence` | `JSON` | no |  | Invoice numbers and content hashes, or document ids for manual claims |
| `evidence_hash` | `BINARY(32)` | no |  | SHA-256 of the canonical evidence |
| `source` | `VARCHAR(32)` | no |  | values: ledger, manual_with_evidence |
| `published_by` | `BINARY(16)` | no |  |  |
| `published_at` | `DATETIME(6)` | no |  |  |
| `reconfirm_by` | `DATE` | no |  | Expires if the creditor does not reconfirm (default 90 days) |
| `last_checked_at` | `DATETIME(6)` | yes |  |  |
| `settled_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: outstanding, payment_plan, disputed, settled, written_off, waived, expired, withdrawn |
| `open_key` | `VARCHAR(120)` | yes |  | learner:creditor:kind while open |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, open_key)
- Index: (tenant_id, learner_id, status)
- Index: (tenant_id, creditor_institution_id, status)
- Index: (tenant_id, reconfirm_by)

- Check `positive`: `amount_outstanding_minor > 0`

<a id="registry-obligation_dispute"></a>
## `obligation_dispute`

Dispute of a published obligation by the family, the admitting institution or the creditor (resolved by LGA or state)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `clearance` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-FCL-06 |
| Pages | FCL-03, FCL-02 |
| Events | FCL.DISPUTE_RAISED, FCL.DISPUTE_RESOLVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `obligation_id` → `learner_obligation` | `BINARY(16)` | no |  |  |
| `raised_by_kind` | `VARCHAR(32)` | no |  | values: guardian, learner, admitting_institution, creditor |
| `raised_by` | `BINARY(16)` | no |  |  |
| `grounds` | `VARCHAR(32)` | no |  | values: already_paid, amount_wrong, not_liable, waiver_granted, statute_barred, protected_learner, other |
| `statement` | `TEXT` | no |  |  |
| `evidence_document_ids` | `JSON` | yes |  |  |
| `due_by` | `DATE` | no |  | Resolution service level (default 10 school days) |
| `resolver_scope_id` → `scope_node` | `BINARY(16)` | no |  | LGA or state node that decides |
| `resolution` | `VARCHAR(32)` | yes |  | values: upheld, partly_upheld, rejected, withdrawn |
| `resolved_amount_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `resolved_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `resolved_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, obligation_id)
- Index: (tenant_id, resolver_scope_id, status)

<a id="registry-clearance_check"></a>
## `clearance_check`

Clearance check run for an incoming learner (purpose-bound, logged, visible to the family)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `clearance` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-FCL-02, FR-FCL-03, FR-FCL-08 |
| Pages | FCL-01, FCL-02 |
| Events | FCL.CHECK_PERFORMED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `requesting_institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `purpose` | `VARCHAR(32)` | no |  | values: admission, transfer, re_enrolment, enquiry_with_consent |
| `basis` | `VARCHAR(32)` | no |  | values: admission_due_diligence, guardian_consent |
| `admission_application_id` | `BINARY(16)` | yes |  | ops-zone admission application |
| `learner_transfer_id` → `learner_transfer` | `BINARY(16)` | yes |  |  |
| `requested_by` | `BINARY(16)` | no |  |  |
| `checked_at` | `DATETIME(6)` | no |  |  |
| `coverage` | `VARCHAR(32)` | no |  | values: state, national |
| `result` | `VARCHAR(32)` | no |  | values: clear, outstanding, disputed_only, protected |
| `obligations` | `JSON` | no |  | Snapshot: obligation id, creditor, kind, amount, oldest due date, status |
| `total_outstanding_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `pattern_flags` | `JSON` | yes |  | e.g. repeat_unsettled_transfers (count, window) |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, learner_id, checked_at)
- Index: (tenant_id, requesting_institution_id, checked_at)

<a id="registry-clearance_decision"></a>
## `clearance_decision`

Human admission decision recorded on a clearance check (or the automatic protection of a learner)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `clearance` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-FCL-04, FR-FCL-05 |
| Pages | FCL-01 |
| Events | FCL.DECISION_RECORDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `check_id` → `clearance_check` | `BINARY(16)` | no |  |  |
| `decision` | `VARCHAR(32)` | no |  | values: admit, admit_with_payment_plan, defer_pending_settlement, admit_protected |
| `protected_reason` | `VARCHAR(32)` | yes |  | values: public_basic_education, send, safeguarding, child_in_care, displaced, other_vulnerability |
| `reason` | `TEXT` | no |  |  |
| `payment_plan_ref` | `VARCHAR(64)` | yes |  |  |
| `decided_by` | `BINARY(16)` | no |  | app_user, or the system for automatic protection |
| `decided_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, check_id)

- Check `protection_reason`: `decision <> 'admit_protected' OR protected_reason IS NOT NULL`

