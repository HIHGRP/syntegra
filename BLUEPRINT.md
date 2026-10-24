# Syntegra — Premium School Management Information System (SMIS) SaaS

**Technical Blueprint v1.0**
**Stack:** Python 3.12 · FastAPI · PostgreSQL · Redis · Celery · React · Kubernetes
**Date:** 2026-10-11

> **Precedence notice (13 Oct 2026).** This v1.0 blueprint predates SYN-MFS-002 v2.4 and the Canonical
> Enterprise Data Architecture. The binding stack is now Python 3.12 · Django 5.2 LTS · MySQL 9.7 LTS ·
> RHEL 10 (MFS §16), and all data modelling, physical schema, data placement, eventing, analytics and
> data-governance decisions are governed by [`ceda/CEDA.md`](ceda/CEDA.md) and the model in [`ceda/model/`](ceda/model/).
> Where this document conflicts with the MFS or CEDA (for example PostgreSQL, row-level security, the §5 data
> model, ClickHouse), the MFS and CEDA govern.

---

## 1. Vision & Positioning

Syntegra is a multi-tenant, premium-tier School Management Information System delivered as a SaaS platform. It targets K-12 schools, international schools, universities, and school groups (districts/MATs) that need a modern, auditable, extensible platform covering academics, operations, finance, communications, and compliance.

### Core differentiators
- **True multi-tenancy** with per-tenant data isolation and optional dedicated-schema or dedicated-DB deployments for enterprise clients.
- **API-first & extensible** — every feature exposed via REST + GraphQL; webhook + plug-in SDK for integrations.
- **AI-assisted workflows** — grading assistance, attendance anomaly detection, timetable generation, student risk scoring, parent-communication drafting.
- **Compliance-grade audit trail** — immutable event log, GDPR/FERPA/COPPA/KVKK ready, data residency per region.
- **Offline-capable** mobile apps for teachers/parents in low-connectivity regions.
- **White-label** for school groups and resellers.

---

## 2. Functional Scope (Modules)

| # | Module | Scope |
|---|--------|-------|
| 1 | **Identity & Access** | SSO (SAML, OIDC, Google, Microsoft), RBAC + ABAC, MFA, delegated admin |
| 2 | **Admissions & CRM** | Enquiry capture, applications, interviews, offers, enrolment, waitlist |
| 3 | **Student Information** | Profiles, guardians, medical, documents, lifecycle (joined→alumnus) |
| 4 | **Academics** | Programmes, year groups, classes, subjects, curriculum mapping |
| 5 | **Timetable & Scheduling** | Constraint-based generator, substitutions, room/resource booking |
| 6 | **Attendance** | Biometric/RFID/kiosk ingestion, period-level, absence workflows |
| 7 | **Gradebook & Assessments** | Rubrics, standards-based, weighted, formative/summative, moderation |
| 8 | **Report Cards & Transcripts** | Templated, locked publication, versioning, digital signatures |
| 9 | **Learning Management** | Assignments, submissions, plagiarism check, media library, LTI 1.3 |
| 10 | **Behaviour & Pastoral** | Incidents, merits/demerits, sanctions, safeguarding (CPOMS-style) |
| 11 | **Communications** | Email, SMS, push, in-app, parent portal, bulk + segmented |
| 12 | **Finance & Billing** | Fee structures, invoices, payment gateways, scholarships, dunning |
| 13 | **Payroll** | Teacher contracts, timesheets, deductions, statutory reports |
| 14 | **HR** | Staff records, leave, appraisals, CPD, recruitment |
| 15 | **Transport** | Routes, buses, GPS tracking, pickup/drop logs, parent live view |
| 16 | **Library** | Catalog, circulation, reservations, overdue, Z39.50/MARC import |
| 17 | **Inventory & Assets** | Textbooks, devices (1:1), consumables, maintenance tickets |
| 18 | **Health & Nurse** | Visits, medications, immunizations, allergies, incident reporting |
| 19 | **Analytics & BI** | Dashboards, early-warning, cohort analysis, custom reports |
| 20 | **Compliance & Audit** | Consent, DSR fulfilment, retention policies, export/erasure |

---

## 3. Architecture

### 3.1 High-level

```
┌───────────────────────────────────────────────────────────────────────┐
│                     CDN / WAF (Cloudflare)                            │
└───────────────────────────────────────────────────────────────────────┘
                              │
┌───────────────────────────────────────────────────────────────────────┐
│  Edge: NGINX Ingress + mTLS + Rate limit + Tenant routing             │
└───────────────────────────────────────────────────────────────────────┘
                              │
┌──────────────┬──────────────┬──────────────┬──────────────────────────┐
│  Web (React) │ Mobile (RN)  │  Admin SPA   │  Public API / Webhooks   │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────────────────┘
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                              │
┌───────────────────────────────────────────────────────────────────────┐
│                   API Gateway (FastAPI + Starlette)                   │
│   • AuthN/Z middleware     • Tenant context     • Observability       │
└───────────────────────────────────────────────────────────────────────┘
                              │
┌────────────┬────────────┬────────────┬────────────┬───────────────────┐
│  Core svc  │  Finance   │  Comms     │  Analytics │  AI/ML Service    │
│ (modular)  │  Service   │  Service   │  Service   │  (FastAPI+Ray)    │
└────┬───────┴────┬───────┴────┬───────┴────┬───────┴────┬──────────────┘
     │            │            │            │            │
     ▼            ▼            ▼            ▼            ▼
┌───────────────────────────────────────────────────────────────────────┐
│   PostgreSQL (RLS)  ·  Redis  ·  Kafka/NATS  ·  S3  ·  ClickHouse     │
│   OpenSearch (search)  ·  Vault (secrets)  ·  Vector DB (pgvector)    │
└───────────────────────────────────────────────────────────────────────┘
                              │
┌───────────────────────────────────────────────────────────────────────┐
│         Workers (Celery/Arq)  ·  Schedulers (APScheduler)             │
└───────────────────────────────────────────────────────────────────────┘
```

### 3.2 Modular monolith → services

Phase 1 ships a **modular monolith** (one Python codebase, strict module boundaries, one deployable). Modules communicate via an internal event bus and typed interfaces. Phase 2 extracts hot/independent modules (Comms, Analytics, AI) into services as scale demands. This keeps early velocity high while leaving a clean extraction path.

### 3.3 Multi-tenancy strategy

Three isolation tiers, selectable per tenant:

| Tier | Model | DB | Use case |
|------|-------|----|----|
| **Shared** | Row-level security | 1 DB, `tenant_id` + Postgres RLS policies | Standard SMB schools |
| **Schema** | Schema-per-tenant | 1 DB, N schemas | Mid-market, moderate isolation |
| **Dedicated** | DB-per-tenant | N DBs, 1 cluster | Enterprise, data residency |

Tenant context is resolved from subdomain (`{slug}.syntegra.app`) or custom domain, injected into a `TenantContext` on every request, and bound to every DB session (`SET LOCAL app.current_tenant = ...`) so RLS policies apply automatically.

### 3.4 Service decomposition

- **core-api** — academics, students, staff, attendance, gradebook, timetable
- **finance-api** — billing, invoicing, payments, payroll
- **comms-api** — email/SMS/push, templating, delivery tracking
- **analytics-api** — materialized views, OLAP queries over ClickHouse
- **ai-api** — model serving, async inference jobs
- **integration-api** — webhooks, OAuth app platform, LTI, SIS imports
- **public-api** — rate-limited external API with token scopes

---

## 4. Technology Stack

### 4.1 Backend
- **Language:** Python 3.12 (CPython; evaluate 3.13 free-threaded for CPU workers)
- **Web framework:** FastAPI (async-first, pydantic v2, OpenAPI)
- **ORM:** SQLAlchemy 2.x (async) + Alembic migrations
- **Validation/Schema:** Pydantic v2
- **Background jobs:** Celery (long-running, periodic) + Arq (lightweight async) + APScheduler
- **GraphQL:** Strawberry (co-located with REST where useful)
- **Auth:** Authlib (OIDC/SAML), python-jose (JWT), passlib/argon2
- **Testing:** pytest, pytest-asyncio, pytest-postgresql, hypothesis, schemathesis, locust
- **Code quality:** ruff, mypy (strict), black, bandit, pip-audit

### 4.2 Data
- **OLTP:** PostgreSQL 16 (RLS, partitioning, logical replication, pgvector, pg_cron)
- **Cache / sessions:** Redis 7 (with Sentinel/Cluster)
- **Search:** OpenSearch (student/staff/doc search, suggestions)
- **Events:** Kafka (or NATS JetStream for smaller deployments)
- **OLAP:** ClickHouse for analytics (CDC via Debezium → Kafka)
- **Object storage:** S3-compatible (AWS S3, MinIO on-prem)
- **Vector:** pgvector (RAG for AI assistants)
- **Secrets:** HashiCorp Vault

### 4.3 Frontend
- **Web:** React 19 + TypeScript, Vite, TanStack Query, Zustand, Tailwind, shadcn/ui
- **Mobile:** React Native (Expo) with offline-first (WatermelonDB) for teachers/parents
- **Design system:** Internal, Figma-synced, WCAG 2.2 AA

### 4.4 Infrastructure & DevOps
- **Containers:** Docker, distroless base images
- **Orchestration:** Kubernetes (EKS/GKE); Helm charts per service
- **IaC:** Terraform (AWS + Cloudflare); ArgoCD for GitOps
- **CI/CD:** GitHub Actions → container registry → ArgoCD sync
- **Observability:** OpenTelemetry → Grafana stack (Loki, Tempo, Mimir, Grafana)
- **Error tracking:** Sentry
- **Feature flags:** Unleash or OpenFeature
- **CDN/WAF:** Cloudflare

---

## 5. Core Data Model (abridged)

Representative tables with multi-tenancy fields. All tenant tables carry `tenant_id UUID NOT NULL` with an RLS policy.

```sql
-- Tenancy
CREATE TABLE tenant (
  id UUID PRIMARY KEY,
  slug CITEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  isolation_tier TEXT CHECK (isolation_tier IN ('shared','schema','dedicated')),
  region TEXT NOT NULL,
  plan_id UUID REFERENCES plan(id),
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Identity
CREATE TABLE user_account (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(id),
  email CITEXT NOT NULL,
  password_hash TEXT,
  mfa_secret TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  last_login_at TIMESTAMPTZ,
  UNIQUE (tenant_id, email)
);

CREATE TABLE role (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  name TEXT NOT NULL,
  permissions JSONB NOT NULL
);

-- Academic structure
CREATE TABLE academic_year (id UUID PK, tenant_id UUID, name TEXT, starts DATE, ends DATE);
CREATE TABLE campus       (id UUID PK, tenant_id UUID, name TEXT, address JSONB);
CREATE TABLE year_group   (id UUID PK, tenant_id UUID, academic_year_id UUID, label TEXT);
CREATE TABLE class_group  (id UUID PK, tenant_id UUID, year_group_id UUID, code TEXT, head_teacher_id UUID);
CREATE TABLE subject      (id UUID PK, tenant_id UUID, code TEXT, name TEXT);
CREATE TABLE course_offering (id UUID PK, tenant_id UUID, subject_id UUID, class_group_id UUID, teacher_id UUID);

-- People
CREATE TABLE student (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID REFERENCES user_account(id),
  admission_no TEXT NOT NULL,
  given_name TEXT NOT NULL,
  family_name TEXT NOT NULL,
  dob DATE,
  gender TEXT,
  current_class_id UUID REFERENCES class_group(id),
  status TEXT NOT NULL,
  joined_on DATE,
  UNIQUE (tenant_id, admission_no)
);

CREATE TABLE guardian (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID,
  given_name TEXT, family_name TEXT,
  phone TEXT, email CITEXT
);

CREATE TABLE guardian_student_link (
  guardian_id UUID, student_id UUID, relationship TEXT, is_primary BOOL,
  PRIMARY KEY (guardian_id, student_id)
);

CREATE TABLE staff (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID REFERENCES user_account(id),
  employee_no TEXT,
  given_name TEXT, family_name TEXT,
  role TEXT,     -- teacher, admin, nurse, etc.
  joined_on DATE
);

-- Attendance (partitioned by month)
CREATE TABLE attendance (
  id UUID,
  tenant_id UUID NOT NULL,
  student_id UUID NOT NULL,
  date DATE NOT NULL,
  period INT,
  status TEXT CHECK (status IN ('present','absent','late','excused')),
  marked_by UUID,
  source TEXT,   -- manual, kiosk, rfid, biometric
  recorded_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (id, date)
) PARTITION BY RANGE (date);

-- Gradebook
CREATE TABLE assessment (id UUID PK, tenant_id UUID, course_offering_id UUID, title TEXT, max_score NUMERIC, weight NUMERIC, type TEXT);
CREATE TABLE grade (
  id UUID PRIMARY KEY,
  tenant_id UUID,
  assessment_id UUID,
  student_id UUID,
  score NUMERIC,
  letter_grade TEXT,
  comments TEXT,
  moderated_by UUID,
  locked_at TIMESTAMPTZ
);

-- Finance
CREATE TABLE fee_structure (id UUID PK, tenant_id UUID, name TEXT, academic_year_id UUID);
CREATE TABLE fee_item      (id UUID PK, tenant_id UUID, fee_structure_id UUID, label TEXT, amount NUMERIC, currency TEXT, cadence TEXT);
CREATE TABLE invoice       (id UUID PK, tenant_id UUID, student_id UUID, number TEXT UNIQUE, issued_on DATE, due_on DATE, total NUMERIC, balance NUMERIC, status TEXT);
CREATE TABLE invoice_line  (id UUID PK, invoice_id UUID, fee_item_id UUID, qty NUMERIC, amount NUMERIC);
CREATE TABLE payment       (id UUID PK, tenant_id UUID, invoice_id UUID, amount NUMERIC, method TEXT, gateway_ref TEXT, received_on TIMESTAMPTZ);

-- Audit (append-only, hash-chained)
CREATE TABLE audit_event (
  id BIGSERIAL PRIMARY KEY,
  tenant_id UUID,
  actor_id UUID,
  entity TEXT, entity_id UUID,
  action TEXT,
  before JSONB, after JSONB,
  ip INET, user_agent TEXT,
  prev_hash BYTEA, hash BYTEA,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Row-Level Security example

```sql
ALTER TABLE student ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON student
  USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## 6. Project Layout

```
syntegra/
├── apps/
│   ├── api/                        # FastAPI app (modular monolith)
│   │   ├── syntegra/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── core/               # tenancy, auth, audit, events, db
│   │   │   ├── modules/
│   │   │   │   ├── identity/
│   │   │   │   ├── students/
│   │   │   │   ├── academics/
│   │   │   │   ├── attendance/
│   │   │   │   ├── gradebook/
│   │   │   │   ├── timetable/
│   │   │   │   ├── finance/
│   │   │   │   ├── comms/
│   │   │   │   ├── lms/
│   │   │   │   ├── behaviour/
│   │   │   │   ├── transport/
│   │   │   │   ├── library/
│   │   │   │   ├── health/
│   │   │   │   ├── hr/
│   │   │   │   ├── analytics/
│   │   │   │   └── integrations/
│   │   │   └── workers/
│   │   ├── migrations/             # Alembic
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── ai/                         # AI service (FastAPI + Ray Serve)
│   ├── analytics/                  # Analytics service
│   └── admin-console/              # Internal ops app
├── web/
│   ├── parent-portal/
│   ├── teacher-portal/
│   ├── student-portal/
│   └── admin-portal/
├── mobile/
│   └── syntegra-app/               # React Native (parent + teacher)
├── packages/
│   ├── ui/                         # Design system (React)
│   ├── sdk-python/                 # Public API SDK
│   └── sdk-js/
├── infra/
│   ├── terraform/
│   ├── helm/
│   └── argocd/
├── docs/
│   ├── architecture/
│   ├── runbooks/
│   └── adr/                        # Architecture Decision Records
└── .github/workflows/
```

### Module internal structure (every module follows this)
```
modules/<name>/
├── __init__.py
├── router.py           # FastAPI routes
├── schemas.py          # Pydantic DTOs
├── models.py           # SQLAlchemy models
├── service.py          # Business logic (pure where possible)
├── repository.py       # DB access
├── events.py           # Published / subscribed events
├── permissions.py
├── tasks.py            # Celery tasks
└── tests/
```

---

## 7. Cross-cutting concerns

### 7.1 Authentication & Authorization
- **Primary auth:** OIDC with short-lived access tokens (15m) + rotating refresh tokens (14d).
- **SSO:** SAML 2.0 and OIDC federated per tenant.
- **MFA:** TOTP + WebAuthn/passkeys; mandatory for admin roles.
- **RBAC + ABAC:** Role grants coarse perms (`student:read`); policies (Cedar or OPA) enforce fine-grained rules (e.g., teacher may read students only in classes they teach).
- **Child safety:** Students < 13 use guardian-approved accounts; data minimization defaults.

### 7.2 Audit & compliance
- Every write produces an immutable `audit_event` with hash chain (prev_hash → sha256 of row) for tamper evidence.
- Retention policies per entity, configurable per tenant with legal-hold overrides.
- Data Subject Request pipeline: export (JSON + PDF), rectification, erasure (hard delete vs. redaction depending on legal basis).

### 7.3 Observability
- OTel traces across HTTP, DB, Celery; tenant_id and user_id attached as span attributes.
- Structured JSON logs with correlation IDs.
- SLOs: p95 API latency < 300ms, 99.9% monthly availability for core modules, 99.95% for auth.
- Golden signals dashboards per module.

### 7.4 Caching
- Redis for session, rate limit, tenant-config, grade-aggregate caches.
- Cache keys namespaced by `tenant_id` with `cache:v1:<tenant>:<module>:...`.
- Invalidation driven by domain events on the bus.

### 7.5 Eventing
- Internal bus abstraction (Phase 1: Postgres LISTEN/NOTIFY + outbox; Phase 2: Kafka).
- Transactional outbox pattern for reliability.
- Event schema registry (Avro or JSON Schema with versioning).

### 7.6 File handling
- Signed URLs for upload/download (never through the API server).
- Virus scanning via ClamAV sidecar or an API like VirusTotal before marking files available.
- Image processing (yearbook photos, document previews) via async worker + S3 lifecycle rules.

### 7.7 Internationalization
- i18n with Babel + ICU message format; RTL support; locale per user.
- Timezone per campus; store UTC, convert at edges.
- Multi-currency with daily FX refresh for consolidated group reporting.

### 7.8 Rate limiting & abuse
- Token bucket per tenant/user/IP via Redis.
- WAF rules for login endpoints, API tokens; CAPTCHA on signup/password-reset.

---

## 8. AI & ML Capabilities

| Capability | Technique | Data |
|---|---|---|
| Attendance anomaly detection | Isolation forest / Prophet | Attendance series per student |
| Early-warning / dropout risk | Gradient boosting (XGBoost) on tabular features | Grades, attendance, behaviour |
| Timetable generation | Constraint solver (OR-Tools CP-SAT) | Rooms, teachers, subjects, constraints |
| Grading assistance | LLM with rubric prompt + teacher-review loop | Rubric + submission |
| Parent message drafting | LLM template with tenant tone + guardrails | Student context + incident |
| Plagiarism detection | Embedding similarity (pgvector) + external API | Submissions corpus |
| Admissions scoring | Logistic regression / GBM | Applications + outcomes |
| Document OCR / extraction | Tesseract + layout LLM | Transcripts, forms |
| Semantic search (handbook, policies) | RAG over tenant docs | Uploaded policies, timetables |

AI service exposes a stable internal gRPC + REST interface. Model artifacts versioned in MLflow; staged rollout via feature flags. All AI outputs are **advisory** by default — teacher/admin confirmation required for any high-stakes action (grades, communications).

---

## 9. Integrations

- **SSO:** Google Workspace, Microsoft Entra, Apple School Manager
- **Comms:** Twilio (SMS/Voice), SendGrid (email), Firebase (push)
- **Payments:** Stripe, PayStack, Flutterwave, Razorpay, PayFast, iyzico, local bank gateways
- **Finance / Accounting:** QuickBooks, Xero, Sage
- **LMS / content:** LTI 1.3 for Khan Academy, IXL, Zoom, MS Teams
- **Government reporting:** Pluggable adapters (UK — DfE Census; US — state-specific; MOE adapters for GCC, EA)
- **Biometrics / hardware:** ZKTeco, Suprema, custom MQTT gateway
- **Transport:** GPS vendors (Teltonika, Queclink) via MQTT/HTTP

A generic **webhook + outbound-event** platform exposes tenant-configurable subscriptions. An **integration SDK** (Python + JS) lets partners build apps against the public API with OAuth 2.1 and scoped tokens.

---

## 10. Security Program

- **Threat model:** STRIDE per module, reviewed quarterly.
- **SAST/DAST:** CodeQL, Bandit, Semgrep in CI; OWASP ZAP nightly against staging.
- **Dependency scanning:** Dependabot + pip-audit + Trivy for images.
- **Secrets:** Vault + short-lived DB creds via Vault's database engine. No long-lived secrets in env.
- **Encryption:** TLS 1.3 everywhere; AES-256 at rest (RDS/S3); field-level encryption for medical records, safeguarding notes.
- **Backups:** PITR for Postgres (7-day), nightly snapshots to cold storage (90-day), quarterly restore drills.
- **Pen test:** Annual external pen test + bug bounty program.
- **Certifications roadmap:** SOC 2 Type II (Year 1), ISO 27001 (Year 2), ISO 27701, state-specific attestations (StateRAMP, iKeepSafe).

---

## 11. Compliance

- **GDPR (EU/UK)** — DPA, DPIA templates, data residency in EU region, DPO contact per tenant.
- **FERPA (US)** — directory information controls, consent workflows, parent/eligible-student access.
- **COPPA** — under-13 handling, parental consent capture.
- **KVKK (TR), POPIA (ZA), PDPA (SG/TH), LGPD (BR)** — regional configuration via a `compliance_profile` on each tenant.
- **Accessibility:** WCAG 2.2 AA for all portals; VPAT published.

---

## 12. Deployment & Environments

| Env | Purpose | Data |
|---|---|---|
| `dev` | Developer local via Docker Compose | Faker-seeded |
| `preview` | Per-PR ephemeral env (Argo + Vcluster) | Fresh seed |
| `staging` | Pre-prod, mirrors prod shape | Anonymized prod subset |
| `prod-eu` | EU tenants | Live |
| `prod-us` | US tenants | Live |
| `prod-apac` | APAC tenants | Live |

Each region is an independent Kubernetes cluster with its own data plane. A thin global control plane handles tenant provisioning, routing (via Cloudflare Workers), billing, and cross-region reporting.

### Release process
1. Trunk-based development; short-lived branches; PR with required reviews + CI green.
2. Merge → container built → signed (cosign) → pushed to registry.
3. ArgoCD syncs to staging; smoke tests run.
4. Progressive rollout to prod (Argo Rollouts, 5% → 25% → 100%) with automated rollback on error-budget burn.
5. Database migrations are **expand/contract**: forward-compatible, double-write where needed, no destructive change in a single release.

---

## 13. Billing & Plans

- **Plans:** Starter, Growth, Scale, Enterprise. Per-student/month pricing with module add-ons (Transport, Payroll, AI pack).
- **Metering:** usage events (students enrolled, SMS sent, AI inference tokens) emitted to the billing pipeline; Stripe Metered Billing or Chargebee for invoicing.
- **Trial:** 30-day with up to 50 students; auto-expiry with 60-day read-only grace.
- **Discounts:** multi-school/group discounts, non-profit tier, annual pre-pay.

---

## 14. Quality & Testing

- **Unit tests:** per module, > 80% coverage target on service/repository.
- **Integration:** real Postgres + Redis via Testcontainers.
- **Contract tests:** Pact between api ↔ frontend; Schemathesis for OpenAPI fuzzing.
- **E2E:** Playwright against staging; nightly across top-10 user journeys.
- **Load:** Locust scenarios for critical reads (gradebook open, timetable fetch), targets published.
- **Chaos:** monthly game days (DB failover, Redis loss, zone outage).
- **Data integrity:** daily reconciliation jobs comparing OLTP ↔ OLAP for key metrics.

---

## 15. Roadmap

### Phase 0 — Foundations (M0-M2)
- Repo bootstrap, CI/CD, infra skeleton (Terraform, EKS, ArgoCD).
- Tenancy framework, auth (OIDC + SSO), audit log, event bus, API skeleton.
- Design system v1, admin console shell.

### Phase 1 — MVP (M3-M6)
- Identity, Students, Guardians, Staff.
- Academics (year groups, classes, subjects, offerings).
- Attendance (manual + kiosk).
- Gradebook (basic weighted, no rubrics).
- Communications (email + in-app).
- Parent portal, teacher portal (web).
- Finance basics (fee structures, invoices, Stripe + one local gateway).
- Pilot with 3 schools (one per region).

### Phase 2 — Core (M7-M12)
- Timetable (OR-Tools), substitutions.
- Full Gradebook (rubrics, standards-based, moderation, report cards).
- LMS basics (assignments, submissions), LTI 1.3.
- Behaviour & pastoral, safeguarding workflow.
- Transport (routes, GPS, parent live view).
- Mobile apps (parent, teacher) with offline cache.
- Analytics v1 (dashboards).
- SOC 2 Type I prep.

### Phase 3 — Premium (M13-M18)
- AI pack (early warning, grading assist, drafting).
- Advanced finance (payroll, multi-currency, group consolidation).
- Library, Inventory, Health, HR.
- Integration platform (public API GA, SDKs, app marketplace).
- Government reporting adapters for 3 initial markets.
- SOC 2 Type II.

### Phase 4 — Scale (M19-M24)
- Service extraction (Comms, Analytics, AI).
- Dedicated-tier offering, data-residency expansion.
- White-label and reseller program.
- ISO 27001.

---

## 16. Team & Delivery

- **Engineering pods** aligned to modules; each pod owns code + tests + runbooks + on-call.
- **Platform pod** owns tenancy, infra, security, DX.
- **Design pod** owns the system; product-managed roadmap per module.
- **DevRel + Partnerships** once Phase 3 integration platform ships.
- **On-call:** follow-the-sun once APAC region is live; PagerDuty + runbooks.

---

## 17. Key Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Data breach | Field-level encryption, RLS, least-privilege IAM, pen testing, bug bounty |
| Multi-tenant data leak via query bug | RLS as last-line defense; mandatory tenant_id in every query via linter |
| Vendor lock-in (cloud) | S3-compatible storage, open protocols; infra via Terraform; stateful stores all open-source |
| Grade/finance data corruption | Append-only audit, PITR, reconciliation jobs, feature flags for new write paths |
| AI hallucination affecting students | Human-in-the-loop, confidence thresholds, feature flags, auditable prompts |
| Regulatory change per region | Compliance profile abstraction; small, isolated adapters |
| On-prem / sovereign requirements | Dedicated tier with Helm-chart deployable + customer-managed keys |

---

## 18. Appendices

### A. ADR topics to write first
1. ADR-001: Modular monolith vs. microservices from day one
2. ADR-002: Tenancy isolation tiers and RLS as default
3. ADR-003: Event bus — Postgres outbox then Kafka
4. ADR-004: SQLAlchemy async + Alembic as the data access standard
5. ADR-005: Authorization engine — OPA/Cedar
6. ADR-006: OpenTelemetry everywhere
7. ADR-007: AI service boundary and feature-flag gating

### B. Example API endpoint design

```
GET  /v1/students?class_id=…&page=…
POST /v1/students
GET  /v1/students/{id}
PATCH /v1/students/{id}
POST /v1/attendance:bulk
GET  /v1/gradebook/offerings/{id}/grades
POST /v1/invoices:issue
POST /v1/payments
```

All endpoints:
- Require `Authorization: Bearer <jwt>` and resolve tenant from JWT `tid` claim (verified against subdomain).
- Return `X-Request-Id` and populate OpenTelemetry trace.
- Support `If-Match` / `ETag` for optimistic concurrency on mutable resources.
- Paginate with cursor-based pagination for large collections.

### C. Example FastAPI skeleton

```python
# apps/api/syntegra/main.py
from fastapi import FastAPI
from syntegra.core.tenancy import TenancyMiddleware
from syntegra.core.auth import AuthMiddleware
from syntegra.core.observability import setup_otel
from syntegra.modules import students, attendance, gradebook, finance, comms

def create_app() -> FastAPI:
    app = FastAPI(title="Syntegra API", version="1.0.0")
    setup_otel(app)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(TenancyMiddleware)
    for module in (students, attendance, gradebook, finance, comms):
        app.include_router(module.router, prefix="/v1")
    return app

app = create_app()
```

```python
# apps/api/syntegra/core/tenancy.py
from contextvars import ContextVar
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

current_tenant: ContextVar[str | None] = ContextVar("current_tenant", default=None)

class TenancyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant = request.state.auth.tenant_id  # set by AuthMiddleware
        token = current_tenant.set(tenant)
        try:
            response = await call_next(request)
        finally:
            current_tenant.reset(token)
        return response
```

```python
# apps/api/syntegra/core/db.py
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text
from syntegra.core.tenancy import current_tenant

engine = create_async_engine(settings.database_url, pool_size=20)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with SessionLocal() as session:
        tenant = current_tenant.get()
        if tenant:
            await session.execute(text("SET LOCAL app.current_tenant = :t"), {"t": tenant})
        yield session
```

### D. Suggested first sprint checklist

1. Repo scaffold with the layout in §6, pyproject with ruff/mypy/pytest wired.
2. `tenant`, `user_account`, `role` tables + Alembic baseline + RLS helper.
3. OIDC login (Google + Microsoft) + session issuance + MFA scaffold.
4. `TenancyMiddleware`, `AuthMiddleware`, structured logging, OTel setup.
5. CI: lint, type-check, test, build, scan, publish image.
6. One real module end-to-end (`students`): model, migration, service, router, tests, Playwright happy path.
7. ArgoCD app deploying to a dev cluster.
8. Admin console shell with tenant provisioning.

---

**End of blueprint v1.0 — iterate per ADR as decisions are made.**
