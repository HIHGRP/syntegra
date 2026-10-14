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
| Sign-in and sessions | Argon2id; lockout after 5 failures in 10 min; sessions stored as SHA-256 only; TOTP MFA; idle timeout set by clearance | `auth/sign-in`, `auth/mfa`, `auth/role`, `auth/sign-out`, `me` | `/sign-in` |
| Institutions | Registration with duplicate detection (name similarity, distance, gov. registration number), scope node and closure | `institutions` | — |
| Learners | Fellegi–Sunter matching (auto-link ≥ 0.98, review 0.80–0.98), GLID from leased blocks, encrypted NIN with purpose-bound reveal, one active primary enrolment, transfer | `learners`, `learners/{id}/transfer`, `learners/{id}/nin` | LRN-04 `/learners/{id}` |
| Classes | Sessions, classes, memberships, subject plans, teacher-of-record assignments | `classes`, `classes/{id}/members` | — |
| Attendance | Registers, idempotent offline sync (`client_op_id`), audited corrections, rates with policy thresholds | `classes/{id}/registers`, `registers/{id}`, `learners/{id}/attendance` | ATT-01 `/registers/class/{id}` |
| Coverage | G2/G3 invariants; gaps deduplicated by the database; owner, due date in school days, escalation, events | `institutions/{id}/coverage/evaluate`, `coverage/gaps` | CUR-101 `/coverage` |
| Certificates | Minimal-disclosure payload, RFC 8785 + ES256 signature, public verification log, JWKS, four-eyes reissue with supersession | `certificates`, `certificates/{id}/reissue`, `reissue-cases/{id}/decision`, `public/verify`, `public/jwks.json` | PUB-01 `/verify` |
| SDAF financing | Census with a content hash, billing at most once per period across institutions, UBE payer rule, rate cards with four eyes, demands | `institutions/{id}/census`, `census/{id}/freeze`, `census/{id}/demand` | — |
| HRMS (CR-001) | Establishment and vacancies; appointments with statutory retirement; posting orders that move role grants, end teaching and re-run coverage (G9→G2); leave with balances the database cannot over-book and cover hand-off (G8); promotions; employee relations with due process; separation that ends access everywhere; encrypted salary accounts with four-eyes; Nigerian payroll (NTA 2025 PAYE, pension, NHF) with two-person approval; state-wide integrity scan (shared accounts/BVNs, double employment, pay after exit, past retirement, no attendance, failed headcount) with human pay holds | `hr/positions`, `hr/institutions/{id}/establishment`, `hr/appointments`, `hr/postings`, `hr/leave`, `hr/promotions`, `hr/relations`, `hr/separations`, `hr/integrity/*`, `hr/payroll-runs` | HRM-01 `/hr/establishment` |
| Fee clearance (CR-001) | Obligations published from each institution's ledger (never SDAF); mandatory, purpose-bound check before transfer and re-admission across every public and private institution in the state; human admission decision — admit, payment plan, defer, protected — never a refusal and never blocking records or attendance (P9); UBE protection; disputes resolved by the LGA; debt-hopping flags; families see every check | `clearance/checks`, `clearance/checks/{id}/decision`, `clearance/obligations`, `clearance/obligations/{id}/disputes`, `clearance/disputes/{id}/resolution`, `learners/{id}/clearance-checks`; `X-Syntegra-Clearance-*` headers on transfer and registration | FCL-01 `/admissions/clearance` |
| Metrics | Semantic layer (`ENR-COUNT`, `ATT-RATE`, `CUR-GAPS-OPEN`) limited to the caller's scope; small-number suppression set by policy | `metrics/{id}` | Home tiles |
| Any CEDA entity | Read-only, scoped and clearance-trimmed. Vault, warehouse and special-category data are excluded. | `ceda`, `ceda/{entity}`, `ceda/{entity}/{id}` | `/pages` (the 260-page catalogue with live and planned status) |

The models for all 511 tables exist and are tested against MySQL. Pages and services for the other MFS modules are
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
python manage.py runserver                # http://localhost:8000 (host → tenant through tenant_domain)
```

Configuration comes from environment variables:

- `SYNTEGRA_DB_HOST`, `SYNTEGRA_DB_USER`, `SYNTEGRA_DB_PASSWORD`, `SYNTEGRA_DB_PREFIX`;
- `SYNTEGRA_TENANCY` (`single` or `schema`);
- `SYNTEGRA_VALKEY_URL`;
- `SYNTEGRA_KEY_PROVIDER`;
- `SYNTEGRA_SECRET_KEY` (required in production).

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

- schema parity for all 511 tables in every zone;
- that tenant data cannot be queried without a context;
- tamper detection and append-only enforcement for the audit chain;
- learner matching, enrolment and transfer;
- scope isolation;
- purpose-bound NIN reveal;
- offline register replay and stale-ETag rejection;
- the G2 → G3 → closed gap lifecycle;
- certificate signing, verification and four-eyes reissue;
- the SDAF once-per-period guard and UBE demand;
- metric suppression;
- the server-rendered pages;
- fee clearance: decision required (never a refusal), deferral, payment plans, UBE protection, disputes and who may
  raise them, debt-hopping flags, ledger publication without SDAF, expiry, family view, re-admission and the API;
- HRMS: appointment and establishment, posting chain (grants, teaching, G2 gap as of the effective date), leave and
  cover, promotion, payroll with four-eyes and integrity holds, separation ending access.

## Layout

```
ceda/                 Canonical Enterprise Data Architecture (model, generators, generated artefacts, tests)
src/syntegra/core     kernel: context, authz, uow, audit, outbox, policy, workflow, crypto, tenancy, api
src/syntegra/<module> one Django app per CEDA module: models.py (generated), domain/ (pure rules), services.py, api.py, urls.py
src/syntegra/schema   migrations that apply the CEDA DDL to each zone
src/syntegra/web      page registry, server-rendered pages (Jinja2), design tokens
deploy/               Containerfile (UBI 10), compose stack (MySQL 9.7, Valkey)
tests/                unit (pure domain) and integration (MySQL) tests
```
