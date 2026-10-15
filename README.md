# Syntegra

Syntegra is a multi-tenant education management platform for Nigerian states. It covers institutions, learners,
attendance, curriculum coverage, certificates and State Digital Access Fee (SDAF) financing.

This repository holds two things:

- the **Canonical Enterprise Data Architecture (CEDA)** in [`ceda/`](ceda/), which is the authoritative data blueprint;
- the **Python application** in [`src/syntegra/`](src/syntegra/), which is built from that blueprint.

When documents disagree, the order of precedence is:

1. `ceda/CEDA.md` and `ceda/model/`
2. SYN-MFS-002 v2.4
3. `BLUEPRINT.md`

## Stack

The stack is the one the MFS binds in §16:

- Python 3.12
- Django 5.2 LTS with Django REST Framework 3.16
- MySQL 9.7 LTS
- Red Hat Enterprise Linux 10 (UBI 10 images)
- Valkey for cache and rate limits
- Celery for background jobs

## How the application is built from the CEDA

```
ceda/model/*.yaml ──cedagen.py──▶ ceda/generated/mysql/*.sql   (physical schema authority, applied by migrations)
                 └─gen_django.py─▶ src/syntegra/<module>/models.py (managed=False, one app per CEDA module)
                                   src/syntegra/core/catalog/ceda_catalog.json (events, metrics, enums, code lists, 260 pages)
```

- **Tables.** Every table comes from the CEDA DDL, applied per zone by the `schema` migrations. Django never generates
  DDL. CHECK constraints, generated columns, tenant-consistent foreign keys, partitions and append-only triggers all
  live in MySQL. Business rules are therefore enforced by the database as well as by Python.
- **Six data zones, one database alias each.** The zones are `platform`, `registry`, `ops`, `vault`, `records` and
  `dw`. In `single` tenancy mode (dev, test, pilots) each zone has one alias. In `schema` mode (production) each
  tenant gets its own schemas, and their aliases are registered on demand.
- **Generated models.** `ZoneRouter` uses each model's `ceda_zones` to pick its database. `TenantScopedManager` makes
  any query that has no tenant context fail.
- **Regenerating.** After changing the model, run `python ceda/tools/cedagen.py generate` and then
  `python ceda/tools/gen_django.py generate`. CI checks that both outputs are up to date.
- **Upgrading.** Each CEDA release is frozen in `ceda/releases/<version>/` and applied by one migration
  (`schema.0001_ceda_1_1_0`, `schema.0002_ceda_1_2_0`, …), so a live database is upgraded in place with an expand-only
  delta. `python ceda/tools/release.py check --mysql` proves that replaying the releases gives exactly the current DDL.

## Kernel (`syntegra.core`)

| Module | What it guarantees |
|---|---|
| `context` | Every request, job and command carries an immutable `Context`: tenant, state tenant, actor, role grant, scope subtree, clearance, purpose and correlation id. |
| `authz` | Checks permissions (`resource:action`, with wildcards), scope (subtree via `scope_closure`), clearance-based field trimming and purpose rules for restricted or special-category data. |
| `uow` | The command pipeline: permission check, then one transaction on the zone, then optimistic locking (`If-Match` ↔ `row_version`), change capture, outbox events and exactly **one** audit event per command. |
| `audit` | Hash-chained audit per zone, tenant and lane: `hash = SHA-256(prev ‖ JCS(event))`. Sensitive values are stored as hashes. `verify_chain` recomputes a chain. |
| `outbox` | Writes a transactional outbox entry that is checked against the CEDA event catalogue and shaped as a CloudEvents envelope. Dispatch happens in-process in dev and through Debezium in production. |
| `policy` | Versioned rules at scope nodes, inherited down the hierarchy. A rule marked mandatory-below can only be tightened at lower levels. Rules are written in a safe expression language with no attribute access and no arbitrary calls. |
| `workflow` | JSON state machines with guards, permissions, SLA-bound human tasks and an append-only transition log. |
| `crypto` | AES-GCM envelope encryption, HMAC lookup tokens, per-record sealing (crypto-shredding) and ES256 signing. All keys come from a `KeyProvider` (local in dev, HSM in prod). |
| `api` | Errors as problem+json (RFC 9457), UUIDv7 cursor pagination, ETags, `Idempotency-Key` replay backed by the `idempotency_key` table, and a generic read-only CEDA API. |

Module boundaries are enforced by `import-linter`:

- the kernel imports no business module;
- `*/domain` packages are free of Django and DRF;
- education modules never read payment state;
- only safeguarding and success may touch vault models;
- fee clearance never imports the finance ledger or SDAF code: only published obligation summaries reach an
  admission decision.

## What is built

| Area | Service (`<module>/services.py`) | API (`/api/v1/…`) | Page |
|---|---|---|---|
| Sign-in and sessions | Argon2id; lockout after 5 failures in 10 min; sessions stored as SHA-256 only; TOTP MFA; idle timeout set by clearance | `auth/sign-in`, `auth/mfa`, `auth/role`, `auth/sign-out`, `me` | `/sign-in`, AUT-03 `/auth/context` (choose the role to work in; shown after sign-in when you hold several) |
| Institutions | Registration with duplicate detection (name similarity, distance, gov. registration number), scope node and closure | `institutions` | form `/forms/institution-register` |
| Learners | Fellegi–Sunter matching (auto-link ≥ 0.98, review 0.80–0.98), GLID from leased blocks, encrypted NIN with purpose-bound reveal, one active primary enrolment, transfer; guardians at registration — a minor needs one with parental responsibility (age of majority is the state policy `LRN-AGE-OF-MAJORITY`), guardians matched by NIN, phone or e-mail with agreeing names before creation, relationship, contact priority, lives-with, collector and payer flags; contact details withheld where contact is restricted | `learners`, `learners/{id}/transfer`, `learners/{id}/nin`, `learners/{id}/guardians` | LRN-02 `/learners/new`, LRN-04 `/learners/{id}` |
| Classes | Sessions, classes, memberships, subject plans, teacher-of-record assignments | `classes`, `classes/{id}/members` | forms `/forms/class-create`, `/forms/class-member` |
| Attendance | Registers, idempotent offline sync (`client_op_id`), audited corrections, rates with policy thresholds | `classes/{id}/registers`, `registers/{id}`, `learners/{id}/attendance` | ATT-01 `/registers/class/{id}` |
| Coverage | G2/G3 invariants; gaps deduplicated by the database; owner, due date in school days, escalation, events | `institutions/{id}/coverage/evaluate`, `coverage/gaps` | CUR-101 `/coverage` |
| Certificates | Minimal-disclosure payload, RFC 8785 + ES256 signature, public verification log, JWKS, four-eyes reissue with supersession | `certificates`, `certificates/{id}/reissue`, `reissue-cases/{id}/decision`, `public/verify`, `public/jwks.json` | PUB-01 `/verify` |
| SDAF financing | Census with a content hash, billing at most once per period across institutions, UBE payer rule, rate cards with four eyes, demands | `institutions/{id}/census`, `census/{id}/freeze`, `census/{id}/demand` | forms `/forms/census-take`, `census-freeze`, `census-demand` |
| HRMS (CR-001) | Establishment and vacancies; appointments with statutory retirement; posting orders that move role grants, end teaching and re-run coverage (G9→G2); leave with balances the database cannot over-book and cover hand-off (G8); promotions; employee relations with due process; separation that ends access everywhere; encrypted salary accounts with four-eyes; Nigerian payroll (NTA 2025 PAYE, pension, NHF) with two-person approval; state-wide integrity scan (shared accounts/BVNs, double employment, pay after exit, past retirement, no attendance, failed headcount) with human pay holds | `hr/positions`, `hr/institutions/{id}/establishment`, `hr/appointments`, `hr/postings`, `hr/leave`, `hr/promotions`, `hr/relations`, `hr/separations`, `hr/integrity/*`, `hr/payroll-runs` | HRM-01 `/hr/establishment` |
| Fee clearance (CR-001) | Obligations published from each institution's ledger (never SDAF); mandatory, purpose-bound check before transfer and re-admission across every public and private institution in the state; human admission decision — admit, payment plan, defer, protected — never a refusal and never blocking records or attendance (P9); UBE protection; disputes resolved by the LGA; debt-hopping flags; families see every check | `clearance/checks`, `clearance/checks/{id}/decision`, `clearance/obligations`, `clearance/obligations/{id}/disputes`, `clearance/disputes/{id}/resolution`, `learners/{id}/clearance-checks`; `X-Syntegra-Clearance-*` headers on transfer and registration | FCL-01 `/admissions/clearance` |
| National clearance network (CR-002) | Every check also asks the other 36 states and the FCT: a directory of all 37 registries; signed (ES256), expiring, single-use queries; matching by Global Learner ID, a national NIN token (never the NIN) or demographics; data returned only for a confident match; states not on the network or not answering are reported as coverage gaps and never block (P9); new arrivals checked before enrolment; both states log; families see checks from other states | `exchange/clearance` (state-to-state, signed messages), `exchange/keys` | FCL-04 `/clearance/network` |
| Security agencies' training (CR-004) | A national sector registry (`ng-fse`) for the education and training institutions of the Armed Forces, Police and paramilitary, law-enforcement, emergency and security services: each agency with its own structure (the access hierarchy), ranks, institutions and per-institution course catalogues with syllabus headings, intakes and trainee outcomes; administration only — never operational or tactical content; reference data illustrative until each agency confirms it | `security-training/agencies`, `…/agencies/{id}`, `…/institutions/{id}`, `…/courses/{id}`, `…/courses/{id}/intakes`, `…/intakes/{id}`, `…/intakes/{id}/trainees`, `…/trainees/{id}/outcome` | STI-01 `/security-training`, STI-02, STI-03, STI-04 |
| Federal institutions (CR-005) | A national sector registry (`ng-fed`) for the federal unity colleges (FGCs, FGGCs, King's and Queen's College, Federal Science and Technical Colleges) and federal special training institutions (colleges of education, agriculture, forestry, fisheries, co-operatives, statistics, surveying, aviation, maritime, petroleum, NTI) under their owning ministries and structures (FME zones and departments); official lists imported and validated row by row | `federal-institutions`, `federal-institutions/import` | FED-01 `/federal-institutions` |
| Education watchdogs (CR-005) | National directory of regulators, examination, admission, curriculum, teacher, funding and professional bodies (FME, NUC, NBTE, NCCE, UBEC, NERDC, TRCN, WAEC, NECO, NABTEB, NBAIS, JAMB, TETFund, NMCN …) with their dependencies; every institution in every registry gets its regulatory profile on registration (supervision, accreditation, curriculum, examination, admission, teachers, funding) with gaps reported | `regulators` (public), `institutions/{id}/regulation`, `regulation-links/{id}` | REG-01 `/regulators`, REG-02 `/institutions/{id}/regulation` |
| Institutional budgets and imprest (CR-006) | Cost centres, versioned budgets by cost centre, economic code and funding source approved by a second person; commitments before spending (refused beyond the available amount); spending, release, virements with a second approver; imprest issued by a second person and retired with receipts; budget execution | `finance/cost-centres`, `finance/budgets`, `finance/commitments`, `finance/virements`, `finance/imprest` | FIN-02 `/finance/performance`, ACC-01 `/finance/imprest` |
| Funding and loans (CR-006) | Programmes for institutions, staff and learners (NELFUND, TETFund, UBEC, scholarships, co-operative and salary-advance loans …); applications with eligibility shown, review and decision by different people, agreements with repayment schedules, the net-pay floor for payroll repayments, disbursements into budget lines, repayments oldest-first, daily arrears | `funding/programmes`, `funding/overview`, `funding/applications`, `funding/agreements/{id}`, `funding/mine` | FND-01 `/funding`, FND-02 `/funding/agreements/{id}` |
| Government property and facilities (CR-006) | Sites with title, fencing and encroachment; buildings, rooms, equipment; dated condition and usability assessments; preventive maintenance; proactive actions for the head with escalation to the LGA and ministry; work orders | `estate/sites`, `estate/buildings`, `estate/rooms`, `estate/assets`, `estate/assessments`, `estate/schedules`, `estate/actions`, `estate/institutions/{id}/workspace` | OPS-01 `/estate`, EST-01 `/estate/property`, EST-02 `/estate/actions` |
| Infrastructure warehouse (CR-006) | Nightly load of facility condition, maintenance, budgets and funding; roll-up every level of the hierarchy; the Commissioner's state-wide view with drill-down | `estate/infrastructure` | EST-03 `/estate/state` |
| Agency careers (CR-006) | Per rank, the courses required for promotion, appointment or command; per course, the units that sponsor, approve, deliver and hold quotas | — | STI-05 `/security-training/agencies/{id}/careers` |
| Examination sitting arrangements | Examination series and papers; whole classes entered with candidate numbers; seating across chosen halls with alternate or every desk, classes interleaved so neighbours are not classmates (the count of same-class neighbours is shown), front seats for access arrangements; halls assessed unsafe and halls already in use at that time are refused; invigilators at one per hall plus one per further 30 candidates; seat chart and seating list per hall. Role EXO (examinations officer); heads hold `exam:*`, teachers and the state `exam:view` | `exams/series`, `exams/series/{id}/papers`, `exams/series/{id}/entries`, `exams/series/{id}/sittings`, `exams/papers/{id}/sitting`, `exams/institutions/{id}/halls` | EXM-01 `/exams/series`, EXM-03 `/exams/series/{id}/sittings` |
| Classroom seating plans | Per class: choose a usable classroom (rooms assessed unsafe are refused), a layout (two-seater desks, single desks, tables of six) and a strategy — alphabetical, ability, mixed ability, seeded random, separate negative influences (pairs with 20+ shared events and more negative behaviour together than apart are kept apart; the count still sitting together is shown) or manual drag-and-drop / tap-to-swap. Learners with a seating or large-print adjustment always sit in the front row. Board-safe view (names only) and a watermarked print that is logged. Heads and teachers hold `seating:*` | — | BEH-102 `/classes/{id}/seating` |
| Sign-in identity and sessions (CR-007) | After the password, the school, college or office of each role grant is shown with its address — never typed — and the one confirmed is recorded on the session and shown under the menu on every page. One account, one session: a sign-in is refused while another session of the account is in use (15 minutes), the person using it is warned, quieter sessions end as `replaced`, and every session records why it ended. Administrators see and end sessions in their scope | `auth/sign-in` (grants with their school or office), `auth/role`, `me`, `auth/sessions`, `auth/sessions/{id}/end` | AUT-03 `/auth/context`, ADM-102 `/admin/sessions` |
| Document management (CR-007) | Digitised paper documents filed under each school with a reference number (`INS-NG-000129/ADM/1998/00001`); write-once storage with a SHA-256 checked on every read; one copy per scan; text from the PDF layer, OCR (Tesseract, when installed) and transcriptions indexed with a MySQL FULLTEXT key; search by words, reference, school, category and year; each school's complete register; viewer with an on-screen watermark; an editable Word copy made on demand (never stored). Ministry, boards, LGAs and records managers search every school in scope with `document:search`; restricted documents need a purpose; everything is audited | `documents`, `documents/categories`, `documents/{id}`, `documents/{id}/content`, `documents/{id}/word`, `institutions/{id}/documents` | DOC-104 `/documents`, DOC-105 `/documents/{id}`, DOC-107 `/documents/upload`, DOC-108 `/institutions/{id}/documents` |
| Access levels (CR-007) | Five levels over the classifications (1 Public, 2 Internal, 3 Confidential, 4 Restricted, 5 Special); each role has one; an administrator can lower one person's level for one role with a reason (never above the role or their own, never their own grant). Pages above the level are refused, their menu items hidden, fields trimmed and documents withheld | `access/levels`, `access/grants/{id}/level` | ADM-101 `/admin/access-levels` |
| School performance | Control room and school comparison for every school in scope: mean score, pass rate, attendance and a performance index ranked within primary, secondary and tertiary; best school and best student overall and per group; by-LGA charts | — | CMD-101 `/command/control-room`, CMD-102 `/command/compare` |
| Bulk roll import | A school's whole roll in one audited command (all or nothing, same validation as single registration, guardians for minors, duplicates checked); Global Learner IDs leased in national blocks | — | used by the demonstration loader |
| Metrics | Semantic layer (`ENR-COUNT`, `ATT-RATE`, `CUR-GAPS-OPEN`) limited to the caller's scope; small-number suppression set by policy | `metrics/{id}` | Home tiles |
| Forms | Every write action above also has a web form: 63 forms at `/forms`, listed by module for the role in use. Each form validates with the API's own serializer and calls the same service, so a page and the API accept and refuse exactly the same things; errors show beside the field they belong to, values are kept, and option lists only offer records in the user's scope (anything else is refused). Record pages link to the forms that act on them (end a regulatory link, accept a gap, add a trainee, record an outcome, transfer a learner, publish unpaid fees) | — | `/forms`, `/forms/{key}` |
| Any CEDA entity | Read-only, scoped and clearance-trimmed. Vault, warehouse and special-category data are excluded. | `ceda`, `ceda/{entity}`, `ceda/{entity}/{id}` | `/pages` (the 260-page catalogue with live and planned status) |

The models for all 552 tables exist and are tested against MySQL. Pages and services for the other MFS modules are
**planned**, and are listed by phase at `/pages`.

## API conventions (Book 3 §26)

- **Errors** are returned as `application/problem+json` with a stable `code` and a `correlation_id`.
- **Validation levels:**
  - hard failures return 422;
  - soft warnings return 409 with `override_allowed`. Repeat the request with `X-Syntegra-Override-Reason` (at least
    10 characters); the reason is audited.
- **Concurrency:** send `If-Match: W/"<row_version>"`. A stale version returns 412.
- **Retries:** send `Idempotency-Key`. The response is replayed for 24 hours. Reusing a key with a different body is
  refused.
- **Purpose:** restricted reads need `X-Syntegra-Purpose: <purpose_code>`. The purpose must be allowed for the role,
  and it is written to the audit event.
- **Pagination:** `?cursor=…&limit=…` (UUIDv7 keyset). The response is `{"data": [...], "page": {"next_cursor": …}}`.

## Running locally

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"                   # needs libmysqlclient headers + pkg-config
podman compose -f deploy/compose.yaml up -d db valkey   # or: docker compose …
python manage.py migrate --database=default
for z in platform registry ops vault records dw; do python manage.py migrate --database=$z; done
python manage.py syntegra_bootstrap       # Abia State seed tenant, hierarchy, roles, policies, HR defaults; prints admin password
python manage.py syntegra_state NG-LA     # provision another state on this platform (or --all: 36 states and the FCT)
python manage.py syntegra_exchange directory   # national clearance network; also onboard | suspend | backfill
python manage.py syntegra_security_registry --admin you@example.ng   # Federal Security Education registry + reference data
python manage.py syntegra_federal_registry --admin you@example.ng    # Federal Institutions registry + reference data
python manage.py syntegra_federal_registry import list.csv --dry-run  # validate an official list (template: ceda/templates/)
python manage.py syntegra_regulation      # watchdog directory + regulatory profile of every institution in every registry
python manage.py runserver                # http://localhost:8000 (host → tenant through tenant_domain)
```

### The Abia demonstration state

```bash
python manage.py syntegra_demo_abia       # DEBUG only: ministries, ASUBEB, 170 schools × 500 pupils, ABSU, ASCETA, 150 staff,
                                          # marks, attendance, facilities, budgets, funding; then the warehouse load
python manage.py syntegra_demo_abia --schools-per-lga 1 --pupils 40   # a quick, smaller state
```

It prints the demonstration accounts (password `Demo-password-2026`, development only), e.g.
`commissioner.education@abia.gov.ng` for the control room. The **End-User Guide** — every task step by step with
annotated screenshots — is §30 of [`ceda/CEDA.md`](ceda/CEDA.md#30-end-user-guide).

Configuration comes from environment variables:

- `SYNTEGRA_DB_HOST`, `SYNTEGRA_DB_USER`, `SYNTEGRA_DB_PASSWORD`, `SYNTEGRA_DB_PREFIX`;
- `SYNTEGRA_TENANCY` (`single` or `schema`);
- `SYNTEGRA_VALKEY_URL`;
- `SYNTEGRA_KEY_PROVIDER`;
- `SYNTEGRA_SECRET_KEY` (required in production);
- `SYNTEGRA_SESSION_IN_USE_MINUTES` (default 15) — how long after its last activity a session blocks a second sign-in;
- `SYNTEGRA_OBJECT_STORE_DIR` and `SYNTEGRA_DOCUMENT_MAX_BYTES` (default 25 MB) — where document scans are kept
  (S3-compatible WORM buckets in production).

Scanned images and image-only PDFs are read for search when **Tesseract OCR** and `pdftoppm` are installed (Ubuntu:
`apt install tesseract-ocr poppler-utils`; RHEL 10: from EPEL). Without them, PDFs with a text layer and the
transcription typed at upload are indexed, and everything else is found by its details.

To build the image, run `podman build -f deploy/Containerfile .`. The image is based on UBI 10 Python 3.12 and runs
gunicorn as a non-root user.

## Tests and quality gates

```bash
python -m pytest tests                    # unit + integration on real MySQL 9.7 (all six zones), never SQLite
ruff check src tests && ruff format --check src tests
mypy                                      # strict on syntegra.core and every */domain package
PYTHONPATH=src lint-imports               # module boundaries
python ceda/tools/gen_django.py check     # models match the CEDA model
python -m pytest ceda/tests               # CEDA conformance (needs MYSQL_CMD)
python ceda/tools/release.py check --mysql # releases replay to the current DDL (needs MYSQL_CMD)
```

The integration tests cover:

- schema parity for all 528 tables in every zone;
- that tenant data cannot be queried without a context;
- tamper detection and append-only enforcement for the audit chain;
- learner matching, enrolment and transfer; guardians at registration (minors need parental responsibility, age
  of majority from policy, guardians matched not duplicated, contact restriction);
- scope isolation;
- purpose-bound NIN reveal;
- offline register replay and stale-ETag rejection;
- the G2 → G3 → closed gap lifecycle;
- certificate signing, verification and four-eyes reissue;
- the SDAF once-per-period guard and UBE demand;
- metric suppression;
- the server-rendered pages;
- the forms: every form renders for a role that may use it and is refused to one that may not; an empty
  submission is a 422, never a 500; institution registration, classes and members by Global Learner ID,
  publishing, disputing and resolving unpaid fees (amounts in naira stored in kobo), HR positions, postings with a
  second approver, leave and its approval, relations cases, integrity scan, payroll validation, regulatory links,
  the official-list upload, and security-training intakes, trainees and outcomes; the workspace chooser (no open
  redirect); and pages that now return 422 or 404 instead of 500 for malformed dates and identifiers;
- request validation: malformed or missing fields and identifiers return a 422 problem on every API endpoint;
- fee clearance: decision required (never a refusal), deferral, payment plans, UBE protection, disputes and who may
  raise them, debt-hopping flags, ledger publication without SDAF, expiry, family view, re-admission and the API;
- HRMS: appointment and establishment, posting chain (grants, teaching, G2 gap as of the effective date), leave and
  cover, promotion, payroll with four-eyes and integrity holds, separation ending access;
- national clearance: a Lagos debt found on admission in Abia (by NIN token and by demographics), no data for a
  possible match, refusal of replayed, expired, forged and unknown-state messages, a remote state over HTTPS, an
  unreachable state recorded without blocking, the family view, the network page, and complete 37-of-37 coverage
  with every state provisioned;
- security agencies' training: every agency with its own structure, ranks, institutions and course catalogue; access
  following the agency structure (police cannot open an army institution; a training command sees only its schools);
  state registries cannot see the sector registry; intakes, trainees and outcomes; syllabus headings only; the pages;
- federal institutions and watchdogs: the directory and its dependencies; every institution's regulatory profile
  (state schools on registration, unity colleges, tertiary, technical, nursing, security institutions) and its gaps;
  zone-level access to unity colleges; the official-list import (validation, additions, corrections); the pages.

## Layout

```
ceda/                 Canonical Enterprise Data Architecture (model, generators, generated artefacts, tests)
src/syntegra/core     kernel: context, authz, uow, audit, outbox, policy, workflow, crypto, tenancy, api
src/syntegra/<module> one Django app per CEDA module: models.py (generated), domain/ (pure rules), services.py, api.py, urls.py
src/syntegra/schema   migrations that apply the CEDA DDL to each zone
src/syntegra/web      page registry, server-rendered pages (Jinja2), forms (forms.py, choices.py), design tokens
deploy/               Containerfile (UBI 10), compose stack (MySQL 9.7, Valkey)
tests/                unit (pure domain) and integration (MySQL) tests
```
