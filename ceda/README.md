# CEDA — Syntegra Canonical Enterprise Data Architecture

The authoritative data blueprint for Syntegra, derived from **SYN-MFS-002 v2.4** (Master Functional
Specification). The Python application, APIs, UX/UI, intelligence engine, government dashboards, reporting
layer and hosting infrastructure are built from it.

- **Read first:** [`CEDA.md`](CEDA.md) — principles, decisions, zones, conventions, security, data flows,
  API/UI contracts, warehouse and semantic layer, dashboards, intelligence data, hosting and capacity,
  governance, and the corrections to MFS Appendix J.
- **The model (source of truth):** [`model/`](model/) — 481 entities in 33 domain files, types, enums,
  the Nigerian jurisdiction pack, events, metrics, retention, and change requests
  ([`model/change_requests/`](model/change_requests/) — CR-001: enterprise HRMS and fee-clearance due diligence).
- **Releases:** [`releases/`](releases/) — frozen DDL per release (1.1.0 baseline, 1.2.0 expand-only delta) for
  upgrading live databases in place.
- **Generated artefacts (never edit by hand):** [`generated/`](generated/)
  - [`mysql/`](generated/mysql/) — MySQL 9.7 LTS DDL per data zone, plus the code-list seed
  - [`dictionary/`](generated/dictionary/README.md) — data dictionary per domain
  - [`erd/`](generated/erd/) — Mermaid ERDs per domain
  - [`jsonschema/`](generated/jsonschema/), [`openapi/components.yaml`](generated/openapi/components.yaml) — canonical resource schemas
  - [`events/`](generated/events/catalog.md) — event catalogue, CloudEvents envelope and payload schemas
  - [`metrics/catalog.md`](generated/metrics/catalog.md) — semantic-layer metric catalogue
  - [`traceability/`](generated/traceability/) — page, requirement and Appendix J coverage

## At a glance

| | |
|---|---|
| Version | 1.2.0 (CR-001) |
| Entities / tables | 481 / 511 across 6 zones (platform, registry, ops, vault, records, warehouse) |
| Enforced foreign keys / append-only tables / partitioned tables | 660 / 95 / 21 |
| Enums / code lists / events / metrics / retention series | 335 / 51 / 149 / 59 / 32 |
| Coverage | 260/260 MFS pages + 13 CR-001 pages · 517/517 MFS + 23 CR-001 functional requirements · 174/174 Appendix J tables |

## Working with the model

```bash
python3 -m pip install pyyaml pytest

python3 ceda/tools/cedagen.py validate --warnings   # validate the model
python3 ceda/tools/cedagen.py generate              # regenerate ceda/generated/
python3 ceda/tools/cedagen.py check                 # fail if generated/ is stale
python3 ceda/tools/release.py delta 1.2.0           # derive a release's expand-only delta
python3 ceda/tools/release.py check --mysql         # replayed releases == current DDL, structurally (needs MYSQL_CMD)

# Load every zone into a MySQL 9.7 server and prove the database guarantees
docker run -d --name mysql97 -e MYSQL_ROOT_PASSWORD=ceda -p 3306:3306 mysql:9.7
MYSQL_CMD="docker exec -i mysql97 mysql -uroot -pceda" python3 ceda/tools/mysql_check.py

# All conformance tests (the MySQL test runs when MYSQL_CMD is set)
MYSQL_CMD="docker exec -i mysql97 mysql -uroot -pceda" python3 -m pytest ceda/tests -q
```

CI (`.github/workflows/ceda.yml`) runs the same steps against a `mysql:9.7` service on every change under `ceda/`.

To change the data model, follow CEDA.md §17.4: edit `model/`, regenerate, write the expand/contract
migration, run the tests, bump the CEDA version.
