# FND — Funding and loan platforms — capital for institutions, staff welfare and student support

Funding and loan platforms (change request CR-006): programmes offered by government agencies (TETFund, UBEC, the Nigerian Education Loan Fund, state scholarship boards), development partners, banks, co-operatives, employers, alumni and philanthropy, for institutions (capital works, equipment, ICT, research, operations), staff (welfare, housing, vehicle, salary advance) and learners (student loans, scholarships, bursaries). Applications are evaluated against the programme's eligibility rules and decided by two different people; agreements carry the terms and a generated repayment schedule; disbursements go to the institution, the beneficiary or a supplier; repayments (payroll deduction, direct debit, transfer, employer remittance) are allocated oldest instalment first. Loans never restrict a learner's education (P9) and payroll deductions never take net pay below the policy floor.

Module (system of record): `funding` · default zone: **ops** · default retention: `RS-FUND`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`funding_programme`](#ops-funding_programme) | ops | config | internal | lifecycle | Funding or loan programme — provider, beneficiary, purpose, instrument, terms and eligibility |
| [`funding_application`](#ops-funding_application) | ops | transaction | restricted | lifecycle | Application to a funding programme by or for an institution, a member of staff or a learner |
| [`funding_agreement`](#ops-funding_agreement) | ops | transaction | restricted | lifecycle | Funding agreement — principal, rate, tenor, moratorium, repayment basis, balances and arrears |
| [`funding_disbursement`](#ops-funding_disbursement) | ops | transaction | restricted | lifecycle | Disbursement of an agreement to the institution, the beneficiary, a supplier or a contractor |
| [`repayment_instalment`](#ops-repayment_instalment) | ops | transaction | restricted | lifecycle | Instalment of a repayment schedule — principal, interest, amount paid and status |
| [`funding_repayment`](#ops-funding_repayment) | ops | event | restricted | append | Repayment received (payroll deduction, direct debit, transfer, employer remittance) and its allocation to instalments |

<a id="ops-funding_programme"></a>
## `funding_programme`

Funding or loan programme — provider, beneficiary, purpose, instrument, terms and eligibility  

Programmes are seeded per registry from the national list (NELFUND student loans, TETFund and UBEC interventions …) and added by states and institutions (scholarship boards, staff co-operatives, bank facilities).

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `funding` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-FND-01 |
| Pages | FND-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(32)` | no |  |  |
| `name` | `VARCHAR(300)` | no |  |  |
| `provider_name` | `VARCHAR(200)` | no |  |  |
| `provider_kind` | `VARCHAR(32)` | no |  | values: federal_government_agency, state_government, local_government, development_partner, bank, microfinance, cooperative, employer, institution, alumni, philanthropy, other |
| `provider_body_code` | `VARCHAR(16)` | yes |  | Education body in the regulators' directory, e.g. TETFUND, UBEC, NELFUND |
| `beneficiary_kind` | `VARCHAR(32)` | no |  | values: institution, staff, learner |
| `purpose` | `VARCHAR(32)` | no |  | values: capital_works, equipment, ict, research, staff_development, operations, tuition_fees, upkeep, housing, vehicle, welfare_emergency, salary_advance, scholarship, bursary, special_needs, other |
| `instrument` | `VARCHAR(32)` | no |  | values: loan, grant, scholarship, bursary, intervention, matching_grant, salary_advance, bond, guarantee, in_kind |
| `interest_rate` | `DECIMAL(6,3)` | no |  | Annual nominal rate; 0 for interest-free loans and for grants |
| `tenor_months` | `SMALLINT` | yes |  |  |
| `moratorium_months` | `SMALLINT` | no |  |  |
| `repayment_basis` | `VARCHAR(32)` | no |  | values: none, fixed_instalment, annuity, income_contingent, payroll_deduction, bullet |
| `max_amount_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `eligibility` | `JSON` | yes |  | Rules: beneficiary levels, ownership, category, minimum service years, maximum income, matching contribution … |
| `terms` | `JSON` | yes |  | Further terms as published (e.g. repayment as a share of salary after national service) |
| `opens_on` | `DATE` | yes |  |  |
| `closes_on` | `DATE` | yes |  |  |
| `data_status` | `VARCHAR(32)` | no |  | values: verified, illustrative, to_confirm |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-funding_application"></a>
## `funding_application`

Application to a funding programme by or for an institution, a member of staff or a learner

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `funding` |
| Origin | ceda |
| Retention | `RS-FUND` |
| Requirements | FR-FND-02, FR-FND-07 |
| Pages | FND-01, FND-02 |
| Events | FND.APPLICATION_SUBMITTED, FND.APPLICATION_DECIDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `application_number` | `VARCHAR(32)` | no |  |  |
| `programme_id` → `funding_programme` | `BINARY(16)` | no |  |  |
| `applicant_kind` | `VARCHAR(32)` | no |  | values: institution, staff, learner |
| `applicant_id` | `BINARY(16)` | no |  | Institution, staff or learner id |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `amount_requested_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `purpose_detail` | `TEXT` | no |  |  |
| `capital_plan_item_id` → `capital_plan_item` | `BINARY(16)` | yes |  | What capital funding will pay for |
| `documents` | `JSON` | yes |  | Supporting document references |
| `eligibility` | `JSON` | yes |  | Each rule with its result, as evaluated at submission |
| `eligible` | `BOOLEAN` | yes |  |  |
| `submitted_by` | `BINARY(16)` | no |  |  |
| `submitted_at` | `DATETIME(6)` | yes |  |  |
| `recommended_by` | `BINARY(16)` | yes |  |  |
| `recommendation` | `TEXT` | yes |  |  |
| `decided_by` | `BINARY(16)` | yes |  |  |
| `decided_at` | `DATETIME(6)` | yes |  |  |
| `decision_reason` | `TEXT` | yes |  |  |
| `amount_approved_minor` | `BIGINT` | yes |  | (minor units) |
| `status` | `VARCHAR(32)` | no |  | values: draft, submitted, under_review, recommended, approved, declined, withdrawn, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, application_number)
- Index: (tenant_id, programme_id, status)
- Index: (tenant_id, applicant_kind, applicant_id)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `four_eyes`: `decided_by IS NULL OR recommended_by IS NULL OR decided_by <> recommended_by`

<a id="ops-funding_agreement"></a>
## `funding_agreement`

Funding agreement — principal, rate, tenor, moratorium, repayment basis, balances and arrears

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `funding` |
| Origin | ceda |
| Retention | `RS-FUND` |
| Requirements | FR-FND-03, FR-FND-05, FR-FND-06 |
| Pages | FND-01, FND-02 |
| Events | FND.AGREEMENT_SIGNED, FND.ARREARS_RAISED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `agreement_number` | `VARCHAR(32)` | no |  |  |
| `application_id` → `funding_application` | `BINARY(16)` | no |  |  |
| `programme_id` → `funding_programme` | `BINARY(16)` | no |  |  |
| `beneficiary_kind` | `VARCHAR(32)` | no |  | values: institution, staff, learner |
| `beneficiary_id` | `BINARY(16)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `instrument` | `VARCHAR(32)` | no |  | values: loan, grant, scholarship, bursary, intervention, matching_grant, salary_advance, bond, guarantee, in_kind |
| `principal_minor` | `BIGINT` | no |  | (minor units) |
| `interest_rate` | `DECIMAL(6,3)` | no |  |  |
| `tenor_months` | `SMALLINT` | yes |  |  |
| `moratorium_months` | `SMALLINT` | no |  |  |
| `repayment_basis` | `VARCHAR(32)` | no |  | values: none, fixed_instalment, annuity, income_contingent, payroll_deduction, bullet |
| `first_repayment_on` | `DATE` | yes |  |  |
| `disbursed_minor` | `BIGINT` | no |  | (minor units) |
| `repaid_minor` | `BIGINT` | no |  | (minor units) |
| `outstanding_minor` | `BIGINT` | no |  | (minor units) |
| `arrears_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `signed_on` | `DATE` | no |  |  |
| `signed_by` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: signed, disbursing, in_moratorium, repaying, in_arrears, settled, completed, written_off, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, agreement_number)
- Unique: (tenant_id, application_id)
- Index: (tenant_id, beneficiary_kind, beneficiary_id)
- Index: (tenant_id, programme_id, status)

- Soft reference `institution_id` → `institution` — cross-zone (ops → registry)
- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

- Check `disbursed_within`: `disbursed_minor <= principal_minor`

<a id="ops-funding_disbursement"></a>
## `funding_disbursement`

Disbursement of an agreement to the institution, the beneficiary, a supplier or a contractor

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `funding` |
| Origin | ceda |
| Retention | `RS-FUND` |
| Requirements | FR-FND-04, FR-FND-07 |
| Pages | FND-02 |
| Events | FND.DISBURSED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `agreement_id` → `funding_agreement` | `BINARY(16)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `payee_kind` | `VARCHAR(32)` | no |  | values: institution, beneficiary, supplier, contractor |
| `payee_reference` | `VARCHAR(120)` | yes |  | Institution account, beneficiary or supplier |
| `purpose` | `VARCHAR(200)` | no |  |  |
| `budget_line_id` → `budget_line` | `BINARY(16)` | yes |  | Receiving budget line for institutional funding |
| `capital_plan_item_id` → `capital_plan_item` | `BINARY(16)` | yes |  |  |
| `reference` | `VARCHAR(64)` | no |  |  |
| `disbursed_on` | `DATE` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: scheduled, paid, failed, reversed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, agreement_id, reference)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-repayment_instalment"></a>
## `repayment_instalment`

Instalment of a repayment schedule — principal, interest, amount paid and status

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `funding` |
| Origin | ceda |
| Retention | `RS-FUND` |
| Requirements | FR-FND-03, FR-FND-05 |
| Pages | FND-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `agreement_id` → `funding_agreement` | `BINARY(16)` | no |  |  |
| `sequence` | `SMALLINT` | no |  |  |
| `due_on` | `DATE` | no |  |  |
| `principal_minor` | `BIGINT` | no |  | (minor units) |
| `interest_minor` | `BIGINT` | no |  | (minor units) |
| `paid_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `paid_on` | `DATE` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: due, partly_paid, paid, overdue, waived |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, agreement_id, sequence)
- Index: (tenant_id, due_on, status)

- Check `paid_within`: `paid_minor <= principal_minor + interest_minor`

<a id="ops-funding_repayment"></a>
## `funding_repayment`

Repayment received (payroll deduction, direct debit, transfer, employer remittance) and its allocation to instalments

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `funding` |
| Origin | ceda |
| Retention | `RS-FUND` |
| Requirements | FR-FND-05, FR-FND-06 |
| Pages | FND-02 |
| Events | FND.REPAYMENT_RECEIVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `agreement_id` → `funding_agreement` | `BINARY(16)` | no |  |  |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `method` | `VARCHAR(32)` | no |  | values: payroll_deduction, direct_debit, bank_transfer, employer_remittance, cash, offset |
| `source_kind` | `VARCHAR(40)` | yes |  | payroll_run, bank_statement_line, remittance |
| `source_id` | `BINARY(16)` | yes |  |  |
| `reference` | `VARCHAR(64)` | no |  |  |
| `received_on` | `DATE` | no |  |  |
| `allocations` | `JSON` | no |  | Instalment sequence → amount |
| `recorded_by` | `BINARY(16)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Unique: (tenant_id, agreement_id, reference)

