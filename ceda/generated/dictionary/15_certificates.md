# CER — Certificate 360 and the state certificate registry — eligibility, issuance, signing, verification, reissue and anti-fraud

The state certificate registry is the single authoritative register of every certificate, transcript, approval certificate and badge credential issued in the state (FR-CER-101). Issuance passes the full eligibility chain, is approved by an authorised signatory, signed (RFC 8785 canonical JSON, SHA-256, ES256 with HSM-held keys) and published within 60 seconds to the registry and linked platforms. Every lifecycle change is an append-only certificate event. Reissue never creates a second valid original: the original is superseded at the moment of issue. Physical security stock is tracked by serial. Legacy awards are created from the digitised archive and marked "Verified from archive".

Module (system of record): `certificates` · default zone: **registry** · default retention: `RS-CERT-PERM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`certificate`](#registry-certificate) | registry | master | confidential | lifecycle | Certificate 360 — authoritative award record (status valid, suspended, revoked, superseded, corrected) |
| [`certificate_event`](#registry-certificate_event) | registry | event | confidential | append | Certificate lifecycle event — issue, correct, suspend, reinstate, revoke, reissue, supersede (append-only) |
| [`certificate_template`](#registry-certificate_template) | registry | config | internal | versioned | Certificate template (layout, fields, security-print profile) per credential kind and issuer |
| [`signatory`](#registry-signatory) | registry | master | internal | effective | Authorised signatory of an issuing authority (with specimen and authority period) |
| [`signing_key`](#registry-signing_key) | registry | config | public | lifecycle | Metadata of an HSM-held issuing key (the private key never leaves the HSM; public keys at the JWKS endpoint) |
| [`eligibility_run`](#registry-eligibility_run) | registry | transaction | confidential | lifecycle | Batch award-eligibility run for a cohort or series |
| [`eligibility_result`](#registry-eligibility_result) | registry | transaction | confidential | append | Eligibility-chain result for one learner (identity → institution → … → accreditation at award date → award approval) |
| [`verification`](#registry-verification) | registry | event | internal | append | Public or API certificate verification (minimum disclosure, rate-limited, visible to the holder) |
| [`registry_publication`](#registry-registry_publication) | registry | queue | internal | lifecycle | Publication of a certificate event to the state registry and linked platforms (≤ 60 s) and the Education Passport |
| [`security_stock`](#registry-security_stock) | registry | master | restricted | lifecycle | Security paper sheet by serial (received → issued to institution → printed / spoiled / destroyed) |
| [`print_job`](#registry-print_job) | registry | event | restricted | append | Print of a signed, approved certificate on registered stock by an authorised printer |
| [`certificate_delivery`](#registry-certificate_delivery) | registry | event | confidential | append | Collection in person or tracked courier delivery of a printed certificate, with recipient identity |
| [`legacy_award`](#registry-legacy_award) | registry | master | confidential | lifecycle | Legacy award record created from the digitised archive (marked "Verified from archive" with source pages) |
| [`fee_schedule`](#registry-fee_schedule) | registry | config | public | versioned | State fee schedule for services (certificate reissue by type, reason and urgency; certified copies; record copies) |
| [`reissue_case`](#registry-reissue_case) | registry | transaction | restricted | lifecycle | Certificate reissue, correction, certified copy or legacy digital copy request |
| [`identity_check`](#registry-identity_check) | registry | event | restricted | append | Identity-verification step for a reissue or record-request case (NIN, OTP, facial match with liveness, manual review) |
| [`forgery_report`](#registry-forgery_report) | registry | transaction | restricted | lifecycle | Suspected-forgery report from a verifier, with evidence image, routed to integrity investigators |

<a id="registry-certificate"></a>
## `certificate`

Certificate 360 — authoritative award record (status valid, suspended, revoked, superseded, corrected)  

scope_node_id is the issuing institution or authority. Status changes only through certificate_event; the row's status is the projection of its latest event. The canonical payload and its hash are immutable.

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `certificates` |
| Origin | appj |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-01, FR-CER-02, FR-CER-04, FR-CER-05, FR-CER-09, FR-CER-101, FR-CER-109, FR-CER-110, FR-PVT-107, FR-EXM-07 |
| Pages | CER-01, CER-03, CER-04, CER-05, PUB-02, HED-06 |
| Events | CERT.ISSUED, CERT.REVOKED, CERT.REISSUED, CERT.CORRECTED, CERT.SUSPENDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `certificate_number` | `VARCHAR(32)` | no |  | <country>-<authority>-<year>-<seq><check>; never reused (decision CD-08) |
| `verification_code` | `VARCHAR(16)` | no |  | Separate short code printed with the QR |
| `credential_kind` | `VARCHAR(32)` | no |  | values: certificate, transcript, testimonial, approval_certificate, badge, micro_credential, certified_copy |
| `learner_id` → `learner` | `BINARY(16)` | yes |  | Holder (NULL only for approval certificates) |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `qualification_id` → `qualification` | `BINARY(16)` | yes |  |  |
| `programme_id` → `programme` | `BINARY(16)` | yes |  |  |
| `curriculum_version_id` → `curriculum_version` | `BINARY(16)` | yes |  |  |
| `award_date` | `DATE` | no |  |  |
| `award_class` | `VARCHAR(40)` | yes |  | Grade, division or classification |
| `holder_name_on_award` | `VARCHAR(200)` | no |  | As printed |
| `eligibility_result_id` → `eligibility_result` | `BINARY(16)` | yes |  |  |
| `exception_id` → `policy_exception` | `BINARY(16)` | yes |  | Authorised exception recorded on the certificate |
| `template_id` → `certificate_template` | `BINARY(16)` | no |  |  |
| `signatory_id` → `signatory` | `BINARY(16)` | no |  |  |
| `payload` | `JSON` | no |  | RFC 8785 canonical JSON payload that was signed |
| `payload_hash` | `BINARY(32)` | no |  |  |
| `signature` | `VARBINARY(512)` | no |  | ES256 signature |
| `signing_key_id` → `signing_key` | `BINARY(16)` | no |  |  |
| `vc_document` | `JSON` | yes |  | W3C Verifiable Credential 2.0 / Open Badges 3.0 |
| `pdf_document_id` | `BINARY(16)` | yes |  | PDF/A with embedded signature (WORM bucket) |
| `supersedes_id` → `certificate` | `BINARY(16)` | yes |  | Original certificate superseded by this reissue/correction |
| `superseded_by` → `certificate` | `BINARY(16)` | yes |  |  |
| `legacy_award_id` → `legacy_award` | `BINARY(16)` | yes |  | Digital copy bound to a legacy award |
| `status` | `VARCHAR(32)` | no |  | values: valid, suspended, revoked, superseded, corrected |
| `status_changed_at` | `DATETIME(6)` | no |  |  |
| `award_key` | `VARCHAR(120)` | yes |  | One certificate per learner per qualification award while valid |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, certificate_number)
- Unique: (tenant_id, verification_code)
- Unique: (tenant_id, payload_hash)
- Unique: (tenant_id, award_key)
- Index: (tenant_id, learner_id)
- Index: (tenant_id, institution_id, award_date)

<a id="registry-certificate_event"></a>
## `certificate_event`

Certificate lifecycle event — issue, correct, suspend, reinstate, revoke, reissue, supersede (append-only)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `certificates` |
| Origin | appj |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-08, FR-CER-102, FR-CER-109 |
| Pages | CER-04, CER-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `certificate_id` → `certificate` | `BINARY(16)` | no |  |  |
| `event_kind` | `VARCHAR(32)` | no |  | values: issued, corrected, suspended, reinstated, revoked, reissued, superseded, certified_copy |
| `reason` | `TEXT` | no |  |  |
| `evidence_document_ids` | `JSON` | yes |  |  |
| `actor_user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `approver_user_id` → `app_user` | `BINARY(16)` | yes |  | Second approver for revocation and flagged cases |
| `workflow_instance_id` → `workflow_instance` | `BINARY(16)` | yes |  |  |
| `occurred_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Check `four_eyes`: `approver_user_id IS NULL OR approver_user_id <> actor_user_id`

<a id="registry-certificate_template"></a>
## `certificate_template`

Certificate template (layout, fields, security-print profile) per credential kind and issuer

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-04 |
| Pages | CER-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `code` | `VARCHAR(40)` | no |  |  |
| `credential_kind` | `VARCHAR(32)` | no |  | values: certificate, transcript, testimonial, approval_certificate, badge, micro_credential, certified_copy |
| `qualification_id` → `qualification` | `BINARY(16)` | yes |  |  |
| `layout` | `JSON` | no |  |  |
| `print_profile` | `JSON` | yes |  | Security paper features required |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, code, version)

<a id="registry-signatory"></a>
## `signatory`

Authorised signatory of an issuing authority (with specimen and authority period)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | effective |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-04 |
| Pages | CER-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `title_on_award` | `VARCHAR(300)` | no |  |  |
| `signature_image_document_id` | `BINARY(16)` | yes |  |  |
| `max_batch_without_second` | `INT UNSIGNED` | yes |  | Four-eyes threshold for batches |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-signing_key"></a>
## `signing_key`

Metadata of an HSM-held issuing key (the private key never leaves the HSM; public keys at the JWKS endpoint)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | lifecycle |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-04, NFR-SEC-104 |
| Pages | CER-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `kid` | `VARCHAR(64)` | no |  | e.g. abia-moe-2026-01 |
| `algorithm` | `VARCHAR(16)` | no |  |  |
| `public_jwk` | `JSON` | no |  |  |
| `hsm_key_ref` | `VARCHAR(255)` | no |  | Key handle in the HSM/KMS |
| `ceremony_document_id` | `BINARY(16)` | yes |  | Key ceremony record with ministry witnesses |
| `activated_at` | `DATETIME(6)` | no |  |  |
| `retired_at` | `DATETIME(6)` | yes |  | Retired keys still verify old signatures |
| `status` | `VARCHAR(32)` | no |  | values: pending, active, retired, compromised |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, kid)

<a id="registry-eligibility_run"></a>
## `eligibility_run`

Batch award-eligibility run for a cohort or series

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-01, FR-CER-03 |
| Pages | CER-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `qualification_id` → `qualification` | `BINARY(16)` | no |  |  |
| `cohort_filter` | `JSON` | no |  |  |
| `learners_total` | `INT UNSIGNED` | no |  |  |
| `learners_eligible` | `INT UNSIGNED` | no |  |  |
| `learners_blocked` | `INT UNSIGNED` | no |  |  |
| `requested_by` → `app_user` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, previewed, running, awaiting_approval, approved, issued, completed, failed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-eligibility_result"></a>
## `eligibility_result`

Eligibility-chain result for one learner (identity → institution → … → accreditation at award date → award approval)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | append |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-01, FR-CER-02 |
| Pages | CER-02, CER-03 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `run_id` → `eligibility_run` | `BINARY(16)` | yes |  |  |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `qualification_id` → `qualification` | `BINARY(16)` | no |  |  |
| `checks` | `JSON` | no |  | Ordered checks with pass/fail and evidence |
| `is_eligible` | `BOOLEAN` | no |  |  |
| `evaluated_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-verification"></a>
## `verification`

Public or API certificate verification (minimum disclosure, rate-limited, visible to the holder)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `certificates` |
| Origin | appj |
| Retention | `RS-VERIFY` |
| Partitioning | range_month on `verified_at` |
| Requirements | FR-CER-06, FR-CER-07, FR-CER-110, FR-CER-113 |
| Pages | PUB-01, PUB-02, CER-07 |
| Events | CERT.VERIFIED, CERT.VERIFY_FAILED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `certificate_id` → `certificate` | `BINARY(16)` | yes |  | NULL when no match |
| `queried_number` | `VARCHAR(40)` | no |  |  |
| `channel` | `VARCHAR(32)` | no |  | values: web_number, qr, secure_link, bulk_api, passport_share |
| `api_client_id` → `api_client` | `BINARY(16)` | yes |  | Bulk verifiers |
| `result` | `VARCHAR(32)` | no |  | values: valid, superseded, revoked, corrected, suspended, not_found, rate_limited |
| `ip_hash` | `BINARY(32)` | yes |  | Keyed hash of the client IP (abuse detection without storing the IP) |
| `verified_at` **PK** | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

- Index: (tenant_id, queried_number, verified_at)
- Index: (tenant_id, certificate_id)

- Soft reference `certificate_id` → `certificate` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)
- Soft reference `api_client_id` → `api_client` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

<a id="registry-registry_publication"></a>
## `registry_publication`

Publication of a certificate event to the state registry and linked platforms (≤ 60 s) and the Education Passport

| | |
|---|---|
| Zone | registry |
| Kind | queue |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `certificates` |
| Origin | appj |
| Retention | `RS-OPS-7` |
| Requirements | FR-CER-102 |
| Pages | CER-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `certificate_event_id` → `certificate_event` | `BINARY(16)` | no |  |  |
| `target` | `VARCHAR(32)` | no |  | values: state_registry, state_portal, national_service, education_passport |
| `attempts` | `SMALLINT` | no |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `last_error` | `VARCHAR(1000)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: queued, sent, delivered, read, failed, retrying, abandoned, processed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, certificate_event_id, target)

<a id="registry-security_stock"></a>
## `security_stock`

Security paper sheet by serial (received → issued to institution → printed / spoiled / destroyed)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `certificates` |
| Origin | appj |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-103, FR-CER-104, FR-CER-113 |
| Pages | CER-04, CMD-15 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `serial` | `VARCHAR(32)` | no |  |  |
| `batch_ref` | `VARCHAR(40)` | no |  |  |
| `holder_institution_id` → `institution` | `BINARY(16)` | yes |  |  |
| `certificate_id` → `certificate` | `BINARY(16)` | yes |  | Certificate printed on this sheet |
| `state` | `VARCHAR(32)` | no |  | values: received, issued_to_institution, printed, spoiled, destroyed, lost |
| `state_changed_at` | `DATETIME(6)` | no |  |  |
| `destruction_witness` | `VARCHAR(200)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, serial)

<a id="registry-print_job"></a>
## `print_job`

Print of a signed, approved certificate on registered stock by an authorised printer

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-104 |
| Pages | CER-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `certificate_id` → `certificate` | `BINARY(16)` | no |  |  |
| `stock_id` → `security_stock` | `BINARY(16)` | no |  |  |
| `printer_ref` | `VARCHAR(64)` | no |  |  |
| `printed_by` → `app_user` | `BINARY(16)` | no |  |  |
| `outcome` | `VARCHAR(32)` | no |  | values: printed, spoiled, refused |
| `printed_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-certificate_delivery"></a>
## `certificate_delivery`

Collection in person or tracked courier delivery of a printed certificate, with recipient identity

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | none |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-111 |
| Pages | CER-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `certificate_id` → `certificate` | `BINARY(16)` | no |  |  |
| `method` | `VARCHAR(32)` | no |  | values: collection_in_person, tracked_courier, digital_only |
| `recipient_name` | `VARCHAR(200)` | no |  |  |
| `recipient_id_checked` | `VARCHAR(120)` | yes |  | Document type checked (no number stored) |
| `courier_tracking` | `VARCHAR(64)` | yes |  |  |
| `delivered_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-legacy_award"></a>
## `legacy_award`

Legacy award record created from the digitised archive (marked "Verified from archive" with source pages)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-105 |
| Pages | CER-101, DOC-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `learner_id` → `learner` | `BINARY(16)` | no |  |  |
| `institution_id` → `institution` | `BINARY(16)` | no |  |  |
| `qualification_label` | `VARCHAR(300)` | no |  |  |
| `award_year` | `SMALLINT` | no |  |  |
| `original_number` | `VARCHAR(40)` | yes |  |  |
| `source_document_id` | `BINARY(16)` | no |  | Digitised register, broadsheet or counterfoil page |
| `verified_by` → `app_user` | `BINARY(16)` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-fee_schedule"></a>
## `fee_schedule`

State fee schedule for services (certificate reissue by type, reason and urgency; certified copies; record copies)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | public |
| History | versioned |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-FIN` |
| Requirements | FR-CER-108, FR-DOC-114, FR-PVT-104 |
| Pages | CER-101, PUB-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `service` | `VARCHAR(32)` | no |  | values: certificate_reissue, certified_copy, legacy_digital_copy, record_copy, transcript |
| `variant` | `VARCHAR(40)` | no |  | Certificate type / reason / urgency key |
| `amount_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `revenue_code` | `VARCHAR(40)` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, service, variant, version)

<a id="registry-reissue_case"></a>
## `reissue_case`

Certificate reissue, correction, certified copy or legacy digital copy request

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `certificates` |
| Origin | appj |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-106, FR-CER-107, FR-CER-108, FR-CER-109 |
| Pages | PUB-101, CER-101, CER-102 |
| Events | CER.REISSUE_REQUESTED, CER.REISSUE_DECIDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `case_number` | `VARCHAR(32)` | no |  |  |
| `certificate_id` → `certificate` | `BINARY(16)` | yes |  | Located award (or legacy_award_id) |
| `legacy_award_id` → `legacy_award` | `BINARY(16)` | yes |  |  |
| `applicant_user_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `applicant_name` | `VARCHAR(200)` | no |  |  |
| `applicant_phone` | `VARCHAR(16)` | no |  |  |
| `reason` | `VARCHAR(32)` | no |  | values: lost_or_stolen, damaged, change_of_name, issuer_error, certified_copy, legacy_digital_copy |
| `urgency` | `VARCHAR(32)` | no |  | values: standard, express |
| `evidence_document_ids` | `JSON` | no |  |  |
| `fee_schedule_id` → `fee_schedule` | `BINARY(16)` | yes |  |  |
| `amount_due_minor` | `BIGINT` | no |  | (minor units) |
| `currency` | `CHAR(3)` | no |  |  |
| `payment_reference` | `VARCHAR(64)` | yes |  | Remita RRR |
| `paid_at` | `DATETIME(6)` | yes |  | No payment, no processing |
| `waiver_approved_by` → `app_user` | `BINARY(16)` | yes |  | Audited waiver (e.g. issuer error) |
| `integrity_flag` | `BOOLEAN` | no |  |  |
| `reviewer_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `second_approver_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `new_certificate_id` → `certificate` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: submitted, identity_check, archive_search, awaiting_payment, in_review, approved, issued, delivered, rejected, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, case_number)

- Check `four_eyes`: `second_approver_id IS NULL OR reviewer_id IS NULL OR second_approver_id <> reviewer_id`

<a id="registry-identity_check"></a>
## `identity_check`

Identity-verification step for a reissue or record-request case (NIN, OTP, facial match with liveness, manual review)

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | restricted |
| History | append |
| Scope | none |
| Module | `certificates` |
| Origin | appj |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-107, NFR-PRIV-102 |
| Pages | CER-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `reissue_case_id` → `reissue_case` | `BINARY(16)` | no |  |  |
| `method` | `VARCHAR(32)` | no |  | values: nin_check, otp, facial_match, document_review, manual_review |
| `outcome` | `VARCHAR(32)` | no |  | A mismatch routes to manual review, never auto-rejects · values: match, partial_match, no_match, manual_review, error |
| `consent_captured` | `BOOLEAN` | no |  | Explicit consent for facial match; template discarded after the check |
| `detail` | `JSON` | yes |  |  |
| `checked_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-forgery_report"></a>
## `forgery_report`

Suspected-forgery report from a verifier, with evidence image, routed to integrity investigators

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | owned |
| Module | `certificates` |
| Origin | ceda |
| Retention | `RS-CERT-PERM` |
| Requirements | FR-CER-112, FR-CER-10 |
| Pages | CER-07, CMD-15 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `queried_number` | `VARCHAR(40)` | no |  |  |
| `certificate_id` → `certificate` | `BINARY(16)` | yes |  |  |
| `reporter_org` | `VARCHAR(300)` | yes |  |  |
| `reporter_contact` | `VARCHAR(200)` | yes |  |  |
| `evidence_document_id` | `BINARY(16)` | yes |  |  |
| `investigator_id` → `app_user` | `BINARY(16)` | yes |  |  |
| `outcome` | `VARCHAR(32)` | yes |  | values: no_issue, explained, action_taken, referred, confirmed |
| `status` | `VARCHAR(32)` | no |  | values: open, in_progress, on_hold, closed, transferred |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

