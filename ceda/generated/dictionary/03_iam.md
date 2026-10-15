# IAM — Identity, access, permissions and service identities

Sign-in identities, sessions and MFA factors; roles as permission templates granted at a scope (role × scope × clearance × purpose, Book 3 §10); access reviews, break-glass and the service identities under which automation agents and integrations act ("Agent X acting for Owner Y", MFS §2.1, §12.3). Accounts live in the state registry so one person signs in once per state and picks a role-at-scope grant across public and private institutions (AUT-03, decision CD-03).

Module (system of record): `iam` · default zone: **registry** · default retention: `RS-IAM`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`app_user`](#registry-app_user) | registry | master | confidential | lifecycle | Sign-in identity (a person may also be a learner, guardian or staff member) — Administrator 360 root |
| [`mfa_factor`](#registry-mfa_factor) | registry | master | restricted | lifecycle | Multi-factor authentication factor (TOTP, FIDO2 passkey, SMS/e-mail OTP fallback) |
| [`user_session`](#registry-user_session) | registry | transaction | confidential | lifecycle | Server-side session (idle timeout 30 min for restricted/special roles, 8 h otherwise) |
| [`credential_reset`](#registry-credential_reset) | registry | transaction | confidential | lifecycle | Password-reset or magic-link token (hashed, single use, short expiry; generic responses) |
| [`identity_provider_config`](#registry-identity_provider_config) | registry | config | restricted | lifecycle | Federated sign-in provider of a state (OpenID Connect — government IdP, Microsoft Entra ID, Google Workspace) |
| [`role`](#registry-role) | registry | config | internal | lifecycle | Role template (41 built-in roles plus REV, ACG, OPF; built-ins cloneable, never editable) |
| [`role_permission`](#registry-role_permission) | registry | config | internal | none | Permission granted by a role (resource:action with optional ABAC condition) |
| [`role_grant`](#registry-role_grant) | registry | link | internal | effective | Role granted to a user at a scope (role-at-scope), with clearance cap and access review date |
| [`access_review`](#registry-access_review) | registry | event | internal | append | Periodic access review decision on a grant |
| [`break_glass_grant`](#registry-break_glass_grant) | registry | transaction | restricted | lifecycle | Time-boxed elevated emergency access (DPO and data owner notified; reviewed within 24 h) |
| [`service_identity`](#registry-service_identity) | registry | master | internal | lifecycle | Non-human principal — automation agent, integration client or system job — bound to a human owner's grant |
| [`purpose_code`](#registry-purpose_code) | registry | reference | public | none | Purpose recorded when restricted fields are revealed or special-category records opened |
| [`user_pin`](#registry-user_pin) | registry | config | internal | none | Pinned page, record or saved view of a user (navigation v2) |

<a id="registry-app_user"></a>
## `app_user`

Sign-in identity (a person may also be a learner, guardian or staff member) — Administrator 360 root

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | appj |
| Retention | `RS-IAM` |
| Requirements | FR-ADM-03, FR-STF-11, FR-CMD-119, FR-AUT-05, FR-AUT-06 |
| Pages | AUT-01, AUT-03, ADM-04, HOM-04, CMD-104 |
| Events | IAM.USER_CREATED, IAM.USER_DEACTIVATED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `username` | `VARCHAR(254)` | no |  | Sign-in name (e-mail or issued username) |
| `display_name` | `VARCHAR(200)` | no |  |  |
| `phone` | `VARCHAR(16)` | yes |  | E.164; used for OTP and magic links |
| `person_kind` | `VARCHAR(32)` | yes |  | Linked master record type · values: learner, guardian, staff, provider_person, applicant, visitor |
| `person_id` | `BINARY(16)` | yes |  | learner, guardian or staff id (registry) |
| `idp` | `VARCHAR(32)` | no |  | values: local, gov_sso, entra, google, magic_link, otp |
| `idp_subject` | `VARCHAR(255)` | yes |  | Subject at the federated IdP |
| `password_hash` | `VARCHAR(255)` | yes |  | Argon2id (local accounts only) |
| `status` | `VARCHAR(32)` | no |  | values: invited, active, locked, suspended, deactivated |
| `locked_until` | `DATETIME(6)` | yes |  | Lockout after 5 failures in 10 minutes |
| `failed_attempts` | `SMALLINT` | no |  |  |
| `last_sign_in_at` | `DATETIME(6)` | yes |  |  |
| `preferences` | `JSON` | yes |  | Language, text size, theme, density, digest, briefing horizons |
| `deactivated_at` | `DATETIME(6)` | yes |  | Automatic from the HR leaving date |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, username)
- Unique: (tenant_id, idp, idp_subject)
- Index: (tenant_id, person_kind, person_id)

<a id="registry-mfa_factor"></a>
## `mfa_factor`

Multi-factor authentication factor (TOTP, FIDO2 passkey, SMS/e-mail OTP fallback)

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-IAM` |
| Requirements | FR-ADM-03, FR-AUT-01, FR-AUT-02, FR-AUT-03 |
| Pages | AUT-02, HOM-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `factor_type` | `VARCHAR(32)` | no |  | values: totp, passkey, sms_otp, email_otp |
| `label` | `VARCHAR(80)` | yes |  |  |
| `secret_enc` | `VARBINARY(1024)` | yes | restricted | Envelope-encrypted secret. TOTP seed or WebAuthn credential (public key and id) |
| `credential_id` | `VARCHAR(255)` | yes |  | WebAuthn credential id |
| `last_used_at` | `DATETIME(6)` | yes |  |  |
| `last_step` | `BIGINT` | yes |  | TOTP time step of the last accepted code — a code is never accepted twice (FR-AUT-03) |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-user_session"></a>
## `user_session`

Server-side session (idle timeout 30 min for restricted/special roles, 8 h otherwise)  

One account, one session (CR-007): a sign-in is refused while another session of the account is in use (last_seen_at within the in-use window); quieter sessions are ended with ended_reason = replaced. The school or office is copied from the confirmed grant's scope node — institution name and address for an institution node, otherwise the node's office address — so the session keeps what the user saw even if the address changes later.

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-SESSION` |
| Requirements | FR-ADM-03, FR-AUT-05, FR-AUT-07, FR-AUT-101, FR-AUT-102, FR-AUT-103 |
| Pages | AUT-01, AUT-03, HOM-04, ADM-102 |
| Events | AUTH.SIGNED_IN, AUTH.FAILED, AUTH.LOCKED, AUTH.MFA_PASSED, AUTH.MFA_FAILED, AUTH.CONCURRENT_REFUSED, AUTH.SESSION_ENDED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `session_hash` | `BINARY(32)` | no |  | SHA-256 of the session token |
| `active_grant_id` → `role_grant` | `BINARY(16)` | yes |  | Role-at-scope chosen in AUT-03 |
| `device_label` | `VARCHAR(120)` | yes |  |  |
| `is_trusted_device` | `BOOLEAN` | no |  | Trusted for 30 days |
| `ip` | `VARBINARY(16)` | yes |  |  |
| `user_agent` | `VARCHAR(400)` | yes |  |  |
| `mfa_at` | `DATETIME(6)` | yes |  |  |
| `auth_method` | `VARCHAR(40)` | yes |  | password, password+totp, password+recovery, sso:<provider>, sso:<provider>+idp_mfa |
| `started_at` | `DATETIME(6)` | no |  |  |
| `last_seen_at` | `DATETIME(6)` | no |  |  |
| `expires_at` | `DATETIME(6)` | no |  |  |
| `revoked_at` | `DATETIME(6)` | yes |  |  |
| `ended_reason` | `VARCHAR(32)` | yes |  | Why the session ended (CR-007) · values: signed_out, idle_timeout, expired, replaced, ended_by_administrator, account_inactive |
| `affiliation_scope_id` | `BINARY(16)` | yes |  | Scope node of the school or office the user signed in for (soft; CR-007) |
| `affiliation_name` | `VARCHAR(300)` | yes |  | School or office name as shown at sign-in |
| `affiliation_address` | `VARCHAR(500)` | yes |  | School or office address as shown at sign-in |
| `affiliation_confirmed_at` | `DATETIME(6)` | yes |  | When the user confirmed the school or office after the password |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, session_hash)

<a id="registry-credential_reset"></a>
## `credential_reset`

Password-reset or magic-link token (hashed, single use, short expiry; generic responses)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-SESSION` |
| Requirements | FR-ADM-03, FR-AUT-02 |
| Pages | AUT-04, AUT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `purpose` | `VARCHAR(32)` | no |  | values: password_reset, magic_link, mfa_recovery |
| `token_hash` | `BINARY(32)` | no |  |  |
| `requested_ip` | `VARBINARY(16)` | yes |  |  |
| `expires_at` | `DATETIME(6)` | no |  |  |
| `used_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, token_hash)

<a id="registry-identity_provider_config"></a>
## `identity_provider_config`

Federated sign-in provider of a state (OpenID Connect — government IdP, Microsoft Entra ID, Google Workspace)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-IAM` |
| Requirements | FR-AUT-04, FR-AUT-05, FR-AUT-06 |
| Pages | AUT-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `provider` | `VARCHAR(32)` | no |  | values: local, gov_sso, entra, google, magic_link, otp |
| `label` | `VARCHAR(80)` | no |  | Button text, e.g. Sign in with Abia Government ID |
| `issuer` | `VARCHAR(2048)` | no |  | OIDC issuer; discovery document at {issuer}/.well-known/openid-configuration |
| `client_id` | `VARCHAR(255)` | no |  |  |
| `client_secret_enc` | `VARBINARY(1024)` | yes | restricted | Envelope-encrypted client_secret. Confidential-client secret (envelope-encrypted) |
| `scopes` | `VARCHAR(200)` | no |  | Space-separated, always including openid and email |
| `allowed_domains` | `JSON` | no |  | E-mail domains whose verified addresses may sign in through this provider |
| `trust_idp_mfa` | `BOOLEAN` | no |  | Accept the provider's MFA (amr/acr) as the second factor |
| `sort_order` | `SMALLINT` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, provider)

<a id="registry-role"></a>
## `role`

Role template (41 built-in roles plus REV, ACG, OPF; built-ins cloneable, never editable)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | appj |
| Retention | `RS-IAM` |
| Requirements | FR-ADM-04, FR-ADM-201 |
| Pages | ADM-05, ADM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `code` | `VARCHAR(16)` | no |  | TCH, DSL, STA, PROP, REV … |
| `name` | `VARCHAR(300)` | no |  |  |
| `clearance` | `VARCHAR(32)` | no |  | Highest classification the role normally receives — its access level (1 public … 5 special, CR-007) · values: public, internal, confidential, restricted, special |
| `is_builtin` | `BOOLEAN` | no |  |  |
| `cloned_from_id` → `role` | `BINARY(16)` | yes |  |  |
| `created_by_clearance` | `VARCHAR(32)` | yes |  | Custom role may never exceed its creator's clearance · values: public, internal, confidential, restricted, special |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code)

<a id="registry-role_permission"></a>
## `role_permission`

Permission granted by a role (resource:action with optional ABAC condition)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `iam` |
| Origin | appj |
| Retention | `RS-IAM` |
| Requirements | FR-ADM-04 |
| Pages | ADM-05 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `role_id` → `role` | `BINARY(16)` | no |  |  |
| `permission` | `VARCHAR(80)` | no |  | resource:action, e.g. learner:view, learner.nin:reveal, certificate:issue |
| `abac_condition` | `JSON` | yes |  | own_classes, own_children, assigned_cases, assigned_inspections, own_placements |
| `field_scope` | `JSON` | yes |  | Restricted/special fields this permission reveals |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, role_id, permission)

<a id="registry-role_grant"></a>
## `role_grant`

Role granted to a user at a scope (role-at-scope), with clearance cap and access review date

| | |
|---|---|
| Zone | registry |
| Kind | link |
| Classification | internal |
| History | effective |
| Scope | none |
| Module | `iam` |
| Origin | appj |
| Retention | `RS-IAM` |
| Requirements | FR-ADM-03, FR-CMD-119, FR-STF-106, FR-STF-03, FR-ADM-202, FR-AUT-101 |
| Pages | ADM-04, AUT-03, CMD-104, ADM-101 |
| Events | IAM.GRANT_CHANGED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `role_id` → `role` | `BINARY(16)` | no |  |  |
| `scope_id` → `scope_node` | `BINARY(16)` | no |  |  |
| `clearance_cap` | `VARCHAR(32)` | yes |  | Narrows the role clearance for this grant · values: public, internal, confidential, restricted, special |
| `granted_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `review_due_on` | `DATE` | yes |  | Access review |
| `delegation_of_id` → `role_grant` | `BINARY(16)` | yes |  | Delegated from another grant (Administrator 360 delegations) |
| `supervised_until` | `DATE` | yes |  | Time-limited supervised exception approved by the head while mandatory checks are pending (FR-STF-03) |
| `office_scope_id` | `BINARY(16)` | yes |  | School or office the holder works in when it differs from the grant's scope — e.g. a ministry official with state-wide scope works in the Ministry of Education (soft; CR-007) |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `valid_from` | `DATE` | no |  | Effective from (inclusive) — history: effective |
| `valid_to` | `DATE` | yes |  | Effective to (inclusive); NULL = open-ended — history: effective |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, user_id, status)

- Check `valid`: `valid_to IS NULL OR valid_to >= valid_from`

<a id="registry-access_review"></a>
## `access_review`

Periodic access review decision on a grant

| | |
|---|---|
| Zone | registry |
| Kind | event |
| Classification | internal |
| History | append |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-IAM` |
| Requirements | FR-ADM-03 |
| Pages | ADM-04 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `grant_id` → `role_grant` | `BINARY(16)` | no |  |  |
| `reviewer_id` → `app_user` | `BINARY(16)` | no |  |  |
| `decision` | `VARCHAR(32)` | no |  | values: keep, reduce, revoke, escalate |
| `reason` | `VARCHAR(500)` | yes |  |  |
| `reviewed_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="registry-break_glass_grant"></a>
## `break_glass_grant`

Time-boxed elevated emergency access (DPO and data owner notified; reviewed within 24 h)

| | |
|---|---|
| Zone | registry |
| Kind | transaction |
| Classification | restricted |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-AUDIT` |
| Requirements | FR-ADM-07 |
| Pages | ADM-11 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `scope_id` → `scope_node` | `BINARY(16)` | no |  |  |
| `reason` | `TEXT` | no |  |  |
| `starts_at` | `DATETIME(6)` | no |  |  |
| `ends_at` | `DATETIME(6)` | no |  |  |
| `dpo_notified_at` | `DATETIME(6)` | yes |  |  |
| `reviewed_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `reviewed_at` | `DATETIME(6)` | yes |  |  |
| `review_outcome` | `VARCHAR(32)` | yes |  | values: keep, reduce, revoke, escalate |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Check `window`: `ends_at > starts_at`

<a id="registry-service_identity"></a>
## `service_identity`

Non-human principal — automation agent, integration client or system job — bound to a human owner's grant  

An agent can never exceed its owner's grant and is further narrowed to its declared tools (MFS §12.3).

| | |
|---|---|
| Zone | registry |
| Kind | master |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-IAM` |
| Requirements | FR-AGT-101, NFR-SEC-101 |
| Pages | AGT-102, ADM-09 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `kind` | `VARCHAR(32)` | no |  | values: agent, api_client, integration, system_job |
| `name` | `VARCHAR(300)` | no |  |  |
| `owner_user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `owner_grant_id` → `role_grant` | `BINARY(16)` | no |  | Grant the identity acts under |
| `allowed_tools` | `JSON` | yes |  | Declared typed commands (agents) or API scopes (clients) |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `paused_at` | `DATETIME(6)` | yes |  | Kill switch |
| `paused_by` → `app_user` | `BINARY(16)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

<a id="registry-purpose_code"></a>
## `purpose_code`

Purpose recorded when restricted fields are revealed or special-category records opened

| | |
|---|---|
| Zone | registry |
| Kind | reference |
| Classification | public |
| History | none |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-IAM` |
| Requirements | FR-CMD-107, FR-LRN-13 |
| Pages | LRN-04, CMD-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `code` | `VARCHAR(40)` | no |  | registration, safeguarding, investigation, transfer_query, exam_integrity, child_missing_education … |
| `label` | `VARCHAR(300)` | no |  |  |
| `requires_reason_text` | `BOOLEAN` | no |  |  |
| `allowed_roles` | `JSON` | yes |  | Role codes permitted to use the purpose |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, code)

<a id="registry-user_pin"></a>
## `user_pin`

Pinned page, record or saved view of a user (navigation v2)

| | |
|---|---|
| Zone | registry |
| Kind | config |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `iam` |
| Origin | ceda |
| Retention | `RS-SESSION` |
| Requirements | FR-CMD-115 |
| Pages | HOM-04, HOM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `user_id` → `app_user` | `BINARY(16)` | no |  |  |
| `target_kind` | `VARCHAR(32)` | no |  | values: page, record, saved_view |
| `target_ref` | `VARCHAR(300)` | no |  | Page id, record reference or saved-view id |
| `label` | `VARCHAR(120)` | yes |  |  |
| `sort_order` | `SMALLINT` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

