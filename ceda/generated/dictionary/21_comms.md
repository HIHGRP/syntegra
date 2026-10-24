# COM — Communication — messaging gateway, WhatsApp and Zenzap, templates, conversations, broadcasts, notifications, announcements and consent requests

One messaging gateway with channel adapters (WhatsApp Business Platform, Zenzap-type workspaces, SMS, USSD, e-mail, push, voice) routing each message to the cheapest compliant channel, preferring open service windows and enforcing spend caps and quiet hours (MFS §9, FR-COM-01–05, 101–120). Every inbound and outbound message is stored against the recipient record with delivery, read and failure status. External channels never carry special-category content. Phone numbers are stored hashed for lookup and encrypted at rest (NFR-SEC-102).

Module (system of record): `comms` · default zone: **ops** · default retention: `RS-COMMS`

| Entity | Zone | Kind | Class | History | Title |
|---|---|---|---|---|---|
| [`message_channel`](#ops-message_channel) | ops | config | internal | lifecycle | Connected channel (WhatsApp number, Zenzap workspace, SMS sender ID, e-mail domain, push app) held by the tenant |
| [`message_template`](#ops-message_template) | ops | config | internal | versioned | Approved message template (Meta category, multilingual variants, approval status, version) |
| [`channel_contact`](#ops-channel_contact) | ops | master | confidential | lifecycle | Contact endpoint of a person on a channel (phone or address) with HMAC lookup for inbound matching |
| [`channel_opt_in`](#ops-channel_opt_in) | ops | event | confidential | append | Opt-in / opt-out per contact and channel with evidence (STOP honoured immediately) |
| [`conversation`](#ops-conversation) | ops | transaction | confidential | lifecycle | Two-way conversation thread (WhatsApp inbox, workspace thread linked to a record, web chat) |
| [`message`](#ops-message) | ops | transaction | confidential | lifecycle | Message sent or received on any channel (delivery, read, failure status; stored against the recipient record) |
| [`broadcast_campaign`](#ops-broadcast_campaign) | ops | transaction | internal | lifecycle | Broadcast campaign (audience rules, scheduling, language variants, throttling, cost estimate, results) |
| [`notification_rule`](#ops-notification_rule) | ops | config | internal | versioned | Rule turning domain events into notifications (recipients, channel policy, digest, quiet hours, escalation) |
| [`notification`](#ops-notification) | ops | transaction | internal | lifecycle | In-app notification to a user (permission-trimmed; may fan out to external channels) |
| [`staff_announcement`](#ops-staff_announcement) | ops | transaction | internal | lifecycle | Announcement to staff or parents with relationship-based audience (timetabled teachers, heads of year, tutors), receipts and expiry |
| [`announcement_recipient`](#ops-announcement_recipient) | ops | link | internal | none | Delivery, read and acknowledgement per announcement recipient |
| [`consent_request`](#ops-consent_request) | ops | transaction | internal | versioned | Request for parental consent (trip, photographs, event, data sharing) — versioned, reminders only to pending parents |
| [`mail_merge_job`](#ops-mail_merge_job) | ops | transaction | confidential | lifecycle | Mail-merge run producing letters, labels or badges (every letter stored to the recipient record) |
| [`workspace_channel`](#ops-workspace_channel) | ops | config | internal | lifecycle | Workspace-messaging channel provisioned from the hierarchy and staff posts (state, LGA, institution, department, year group) |

<a id="ops-message_channel"></a>
## `message_channel`

Connected channel (WhatsApp number, Zenzap workspace, SMS sender ID, e-mail domain, push app) held by the tenant

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-102, FR-COM-103, FR-COM-109 |
| Pages | COM-102 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `channel` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `provider` | `VARCHAR(40)` | no |  | meta_cloud_api, bsp_name, zenzap, teams, slack, smpp_aggregator … |
| `display_name` | `VARCHAR(300)` | no |  |  |
| `address` | `VARCHAR(128)` | no |  | E.164 number, sender id, workspace id |
| `credentials_vault_ref` | `VARCHAR(255)` | no |  | Token stored in the vault; never in the database |
| `monthly_spend_cap_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `quiet_hours` | `JSON` | yes |  | Default 20:00–07:00 local |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-message_template"></a>
## `message_template`

Approved message template (Meta category, multilingual variants, approval status, version)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-03, FR-COM-104, FR-COM-101 |
| Pages | COM-102, COM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `channel_id` → `message_channel` | `BINARY(16)` | yes |  |  |
| `template_key` | `VARCHAR(64)` | no |  |  |
| `category` | `VARCHAR(32)` | no |  | values: utility, authentication, marketing, service, internal |
| `variants` | `JSON` | no |  | Language → body with merge fields |
| `provider_template_ref` | `VARCHAR(128)` | yes |  |  |
| `approval_status` | `VARCHAR(32)` | no |  | values: draft, submitted, approved, rejected, paused, retired |
| `version` | `INT UNSIGNED` | no |  |  |
| `is_mail_merge` | `BOOLEAN` | no |  | Word-compatible letter/label/badge template |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, scope_node_id, template_key, version)

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-channel_contact"></a>
## `channel_contact`

Contact endpoint of a person on a channel (phone or address) with HMAC lookup for inbound matching

| | |
|---|---|
| Zone | ops |
| Kind | master |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the person's institutions |
| Module | `comms` |
| Origin | ceda |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-106, NFR-SEC-102 |
| Pages | COM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `person_kind` | `VARCHAR(32)` | no |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `person_id` | `BINARY(16)` | no |  |  |
| `channel` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `endpoint_hmac` | `BINARY(32)` | no |  | HMAC-SHA-256 lookup of endpoint |
| `endpoint_enc` | `VARBINARY(1024)` | no |  | Envelope-encrypted endpoint. E.164 phone, e-mail or device token |
| `endpoint_last4` | `CHAR(4)` | yes |  | Last four characters of endpoint for masked display |
| `is_verified` | `BOOLEAN` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, channel, endpoint_hmac)

<a id="ops-channel_opt_in"></a>
## `channel_opt_in`

Opt-in / opt-out per contact and channel with evidence (STOP honoured immediately)

| | |
|---|---|
| Zone | ops |
| Kind | event |
| Classification | confidential |
| History | append |
| Scope | derived: the person |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-108 |
| Pages | COM-102, COM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `contact_id` → `channel_contact` | `BINARY(16)` | no |  |  |
| `decision` | `VARCHAR(32)` | no |  | values: opt_in, opt_out |
| `category` | `VARCHAR(32)` | yes |  | values: utility, authentication, marketing, service, internal |
| `wording` | `VARCHAR(1000)` | no |  | Wording shown at opt-in |
| `source` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `decided_at` | `DATETIME(6)` | no |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |

<a id="ops-conversation"></a>
## `conversation`

Two-way conversation thread (WhatsApp inbox, workspace thread linked to a record, web chat)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-106, FR-COM-110, FR-COM-118, FR-AGT-114 |
| Pages | COM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `channel_id` → `message_channel` | `BINARY(16)` | no |  |  |
| `contact_id` → `channel_contact` | `BINARY(16)` | yes |  |  |
| `external_thread_ref` | `VARCHAR(128)` | yes |  |  |
| `linked_record_kind` | `VARCHAR(40)` | yes |  | alert, coverage_gap, corrective_action, inspection, reissue_case |
| `linked_record_id` | `BINARY(16)` | yes |  |  |
| `assigned_office` | `VARCHAR(32)` | yes |  | values: class_teacher, bursary, admissions, pastoral, attendance, helpdesk, head |
| `assigned_user_id` | `BINARY(16)` | yes |  |  |
| `service_window_ends_at` | `DATETIME(6)` | yes |  | WhatsApp 24-hour customer-service window |
| `sla_due_at` | `DATETIME(6)` | yes |  |  |
| `is_bot_handled` | `BOOLEAN` | no |  | Parent Concierge Agent; hand-over offered |
| `status` | `VARCHAR(32)` | no |  | values: open, pending, resolved, closed |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-message"></a>
## `message`

Message sent or received on any channel (delivery, read, failure status; stored against the recipient record)  

Classification-aware content rules block special-category content on external channels (they carry only "You have a new item — sign in to view"). Restricted guardians are excluded automatically.

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | derived: the recipient's institution |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-COMMS` |
| Partitioning | range_month on `created_on` |
| Requirements | FR-COM-01, FR-COM-02, FR-COM-04, FR-COM-105, FR-COM-112, FR-COM-113, FR-COM-114, FR-COM-115, FR-COM-117, FR-ATT-101, FR-DOC-116 |
| Pages | COM-01, COM-02, COM-101, HOM-02 |
| Events | COM.MESSAGE_SENT, COM.MESSAGE_RECEIVED |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `created_on` **PK** | `DATE` | no |  | Partition key (UTC date of creation) |
| `conversation_id` → `conversation` | `BINARY(16)` | yes |  |  |
| `campaign_id` → `broadcast_campaign` | `BINARY(16)` | yes |  |  |
| `notification_id` → `notification` | `BINARY(16)` | yes |  |  |
| `direction` | `VARCHAR(32)` | no |  | values: outbound, inbound |
| `channel` | `VARCHAR(32)` | no |  | values: in_app, push, sms, whatsapp, email, voice, ussd, workspace, web, post |
| `recipient_kind` | `VARCHAR(32)` | yes |  | values: learner, guardian, staff, provider_person, applicant, visitor |
| `recipient_id` | `BINARY(16)` | yes |  |  |
| `about_learner_id` → `learner` | `BINARY(16)` | yes |  |  |
| `template_id` → `message_template` | `BINARY(16)` | yes |  |  |
| `language` | `VARCHAR(35)` | yes |  |  |
| `body` | `TEXT` | yes |  | Rendered content (never special-category on external channels) |
| `priority` | `VARCHAR(32)` | no |  | values: p1, high, normal, low |
| `estimated_cost_minor` | `BIGINT` | yes |  | (minor units) |
| `actual_cost_minor` | `BIGINT` | yes |  | (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `provider_message_ref` | `VARCHAR(128)` | yes |  |  |
| `delivery_status` | `VARCHAR(32)` | no |  | values: queued, sent, delivered, read, failed, retrying, abandoned, processed |
| `delivered_at` | `DATETIME(6)` | yes |  |  |
| `read_at` | `DATETIME(6)` | yes |  |  |
| `failure_reason` | `VARCHAR(300)` | yes |  |  |
| `sent_by` | `BINARY(16)` | yes |  | User or agent service identity |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, recipient_kind, recipient_id)
- Index: (tenant_id, provider_message_ref)

- Soft reference `conversation_id` → `conversation` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)
- Soft reference `campaign_id` → `broadcast_campaign` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)
- Soft reference `notification_id` → `notification` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)
- Soft reference `about_learner_id` → `learner` — cross-zone (ops → registry)
- Soft reference `template_id` → `message_template` — partitioned table (InnoDB partitioned tables cannot hold foreign keys)

<a id="ops-broadcast_campaign"></a>
## `broadcast_campaign`

Broadcast campaign (audience rules, scheduling, language variants, throttling, cost estimate, results)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `comms` |
| Origin | ceda |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-116, FR-COM-01, FR-COM-03 |
| Pages | COM-103, COM-01 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `audience_rule` | `JSON` | no |  |  |
| `template_id` → `message_template` | `BINARY(16)` | no |  |  |
| `scheduled_at` | `DATETIME(6)` | yes |  |  |
| `throttle_per_second` | `SMALLINT` | yes |  |  |
| `recipients_estimated` | `INT UNSIGNED` | yes |  |  |
| `cost_estimate_minor` | `BIGINT` | yes |  | Counts only template messages outside open service windows (minor units) |
| `currency` | `CHAR(3)` | yes |  |  |
| `results` | `JSON` | yes |  |  |
| `approved_by` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, awaiting_approval, scheduled, sending, completed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-notification_rule"></a>
## `notification_rule`

Rule turning domain events into notifications (recipients, channel policy, digest, quiet hours, escalation)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `comms` |
| Origin | ceda |
| Retention | `RS-CONFIG` |
| Requirements | FR-COM-05 |
| Pages | ADM-18 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `event_type` | `VARCHAR(64)` | no |  |  |
| `recipient_rule` | `JSON` | no |  |  |
| `channel_policy` | `JSON` | no |  |  |
| `is_digest` | `BOOLEAN` | no |  |  |
| `bypass_quiet_hours` | `BOOLEAN` | no |  | Priority 1 and DSL safeguarding only |
| `version` | `INT UNSIGNED` | no |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-notification"></a>
## `notification`

In-app notification to a user (permission-trimmed; may fan out to external channels)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | none |
| Module | `comms` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Partitioning | range_month on `created_on` |
| Requirements | FR-COM-05, FR-CMD-03 |
| Pages | HOM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `created_on` **PK** | `DATE` | no |  |  |
| `user_id` | `BINARY(16)` | no |  |  |
| `rule_id` → `notification_rule` | `BINARY(16)` | yes |  |  |
| `event_id` | `BINARY(16)` | yes |  | Source domain event |
| `title` | `VARCHAR(300)` | no |  |  |
| `body` | `VARCHAR(1000)` | yes |  | Never special-category content |
| `link` | `VARCHAR(500)` | yes |  |  |
| `priority` | `VARCHAR(32)` | no |  | values: p1, high, normal, low |
| `read_at` | `DATETIME(6)` | yes |  |  |
| `acknowledged_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Index: (tenant_id, user_id, read_at)

- Soft reference `rule_id` → `notification_rule` — declared soft

<a id="ops-staff_announcement"></a>
## `staff_announcement`

Announcement to staff or parents with relationship-based audience (timetabled teachers, heads of year, tutors), receipts and expiry

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-119 |
| Pages | COM-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `title` | `VARCHAR(300)` | no |  |  |
| `body` | `TEXT` | no |  |  |
| `audience_rule` | `JSON` | no |  | e.g. timetabled_teachers_of(learner) |
| `requires_acknowledgement` | `BOOLEAN` | no |  |  |
| `expires_at` | `DATETIME(6)` | yes |  |  |
| `published_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-announcement_recipient"></a>
## `announcement_recipient`

Delivery, read and acknowledgement per announcement recipient

| | |
|---|---|
| Zone | ops |
| Kind | link |
| Classification | internal |
| History | none |
| Scope | none |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-OPS-3` |
| Requirements | FR-COM-119 |
| Pages | COM-104 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `announcement_id` → `staff_announcement` | `BINARY(16)` | no |  |  |
| `user_id` | `BINARY(16)` | no |  |  |
| `delivered_at` | `DATETIME(6)` | yes |  |  |
| `read_at` | `DATETIME(6)` | yes |  |  |
| `acknowledged_at` | `DATETIME(6)` | yes |  |  |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Unique: (tenant_id, announcement_id, user_id)

<a id="ops-consent_request"></a>
## `consent_request`

Request for parental consent (trip, photographs, event, data sharing) — versioned, reminders only to pending parents

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | internal |
| History | versioned |
| Scope | owned |
| Module | `comms` |
| Origin | appj |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-120, FR-OPS-06 |
| Pages | COM-104, OPS-06 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `consent_type` | `VARCHAR(32)` | no |  | code list `consent_type` |
| `title` | `VARCHAR(300)` | no |  |  |
| `body` | `TEXT` | no |  |  |
| `version` | `INT UNSIGNED` | no |  |  |
| `learner_ids` | `JSON` | no |  | Learners covered |
| `respond_by` | `DATETIME(6)` | yes |  |  |
| `trip_id` → `trip` | `BINARY(16)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, in_review, approved, published, superseded, retired, withdrawn |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-mail_merge_job"></a>
## `mail_merge_job`

Mail-merge run producing letters, labels or badges (every letter stored to the recipient record)

| | |
|---|---|
| Zone | ops |
| Kind | transaction |
| Classification | confidential |
| History | lifecycle |
| Scope | owned |
| Module | `comms` |
| Origin | ceda |
| Retention | `RS-OPS-3` |
| Requirements | FR-COM-101 |
| Pages | COM-02 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `template_id` → `message_template` | `BINARY(16)` | no |  |  |
| `recipient_rule` | `JSON` | no |  |  |
| `output` | `VARCHAR(32)` | no |  | values: letters_pdf, labels, badges, email |
| `documents_created` | `INT UNSIGNED` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: draft, previewed, running, awaiting_approval, approved, issued, completed, failed, cancelled |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

<a id="ops-workspace_channel"></a>
## `workspace_channel`

Workspace-messaging channel provisioned from the hierarchy and staff posts (state, LGA, institution, department, year group)

| | |
|---|---|
| Zone | ops |
| Kind | config |
| Classification | internal |
| History | lifecycle |
| Scope | owned |
| Module | `comms` |
| Origin | ceda |
| Retention | `RS-COMMS` |
| Requirements | FR-COM-109, FR-COM-110, FR-COM-111 |
| Pages | COM-102, COM-101 |

| Column | MySQL type | Null | Class | Description |
|---|---|---|---|---|
| `id` **PK** | `BINARY(16)` | no |  | Primary key: UUID v7 (time-ordered) stored as BINARY(16) without byte swap |
| `tenant_id` | `BINARY(16)` | no |  | Owning tenant (zones with tenant_column = true) |
| `scope_node_id` | `BINARY(16)` | no |  | Owning governance scope node (entities with scope: owned); subtree visibility through scope_closure |
| `channel_id` → `message_channel` | `BINARY(16)` | no |  |  |
| `external_channel_ref` | `VARCHAR(128)` | no |  |  |
| `audience` | `VARCHAR(32)` | no |  | values: state_heads, lga_heads, all_staff, department, year_group, committee |
| `membership_rule` | `JSON` | no |  | Derived from grants and posts; removed automatically on leaving |
| `last_synced_at` | `DATETIME(6)` | yes |  |  |
| `status` | `VARCHAR(32)` | no |  | values: active, inactive, retired |
| `created_at` | `DATETIME(6)` | no |  | UTC time the row was written |
| `created_by` | `BINARY(16)` | yes |  | Actor: app_user.id or service_identity.id (agents, integrations) |
| `updated_at` | `DATETIME(6)` | no |  | UTC time of last change (mutable entities only) |
| `updated_by` | `BINARY(16)` | yes |  | Actor of last change (mutable entities only) |
| `row_version` | `INT UNSIGNED` | no |  | Optimistic-lock counter; exposed as the API ETag (mutable entities only) |

- Soft reference `scope_node_id` → `scope_node` — owning scope (governance hierarchy is in the registry zone)

