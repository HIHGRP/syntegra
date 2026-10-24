"""CEDA conformance tests.

Run: python3 -m pytest ceda/tests -q
The MySQL test runs only when MYSQL_CMD is set (CI provides a MySQL 9.7 service).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CEDA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CEDA / "tools"))

import cedagen  # noqa: E402


@pytest.fixture(scope="module")
def model():
    m = cedagen.Model()
    errs = cedagen.validate(m)
    cedagen.plan_keys(m)
    return m, errs


def test_model_is_valid(model):
    _, errs = model
    assert errs.errors == [], "\n".join(errs.errors[:50])
    assert errs.warnings == [], "\n".join(errs.warnings[:50])


def test_generated_artefacts_are_current():
    assert cedagen.main(["check"]) == 0, "run: python3 ceda/tools/cedagen.py generate"


def test_every_page_is_served(model):
    m, _ = model
    mfs = [p for p in m.pages.values() if "change_request" not in p]
    cr = [p for p in m.pages.values() if p.get("change_request")]
    assert len(mfs) == 260  # every MFS page …
    assert {p["change_request"] for p in cr} <= set(m.change_requests)  # … plus pages added by approved change requests
    assert set(m.coverage["pages"]) == set(m.pages)


def test_every_functional_requirement_is_accounted_for(model):
    m, _ = model
    frs = {r for r in m.requirements if r.startswith("FR-")}
    assert len({r for r in frs if "change_request" not in m.requirements[r]}) == 517
    assert {m.requirements[r]["change_request"] for r in frs if "change_request" in m.requirements[r]} <= set(
        m.change_requests
    )
    unaccounted = frs - set(m.coverage["reqs"]) - set(m.coverage["behavioural"])
    assert not unaccounted, sorted(unaccounted)


def test_every_appendix_j_table_is_mapped(model):
    m, _ = model
    assert len(m.appj) == 174
    assert set(m.coverage["appj"]) == set(m.appj)


def test_special_category_only_in_vault(model):
    m, _ = model
    for e in m.entities.values():
        if e.classification == "special":
            assert e.zone in ("vault", "dw"), e.key
        for a in e.attrs:
            if a.classification == "special" and e.zone not in ("vault", "dw"):
                assert a.type == "sealed", f"{e.key}.{a.name}"


def test_no_vault_entity_feeds_the_warehouse_row_level(model):
    m, _ = model
    for e in m.entities.values():
        if e.zone != "dw" or e.kind == "aggregate":
            continue
        for s in e.g("sources", []):
            src = m.resolve(s)
            assert src.zone != "vault", f"{e.name} sources vault entity {s} at row level"


def test_append_only_tables_have_no_update_columns(model):
    m, _ = model
    for e in m.entities.values():
        if e.append_only:
            names = {c.name for c in e.columns}
            assert not names & {"updated_at", "updated_by", "row_version"}, e.key


def test_partitioned_tables_have_no_foreign_keys(model):
    m, _ = model
    partitioned = {e.key for e in m.entities.values() if e.partition}
    for e in m.entities.values():
        for _, tgt, _ in e.fks:
            assert e.key not in partitioned and tgt.key not in partitioned, (e.key, tgt.key)


def test_money_always_has_currency(model):
    m, _ = model
    for e in m.entities.values():
        if any(a.type == "money" for a in e.attrs):
            assert any(c.name.endswith("currency") for c in e.columns), e.key


def test_event_payloads_carry_no_personal_types(model):
    m, _ = model
    for name, ev in m.events.items():
        for f, t in (ev.get("payload") or {}).items():
            base = t.rstrip("!").split("(")[0]
            assert base not in ("name", "email", "phone", "text", "sealed", "secret"), f"{name}.{f}"


def test_summary_counts():
    s = json.loads((CEDA / "generated" / "summary.json").read_text())
    assert s["pages_covered"] == s["pages_total"] >= 260
    assert s["appj_tables_mapped"] == s["appj_tables_total"] == 174
    assert s["tables"] >= 174


@pytest.mark.skipif(not os.environ.get("MYSQL_CMD"), reason="MYSQL_CMD not set (needs a MySQL 9.7 server)")
def test_ddl_loads_and_guarantees_hold_in_mysql_97():
    r = subprocess.run([sys.executable, str(CEDA / "tools" / "mysql_check.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_releases_reproduce_the_current_ddl():
    """ceda/releases (baseline + expand-only deltas + manual expand scripts) replays to the current DDL."""
    import importlib

    release = importlib.import_module("release")
    assert release.cmd_check() == 0
    assert release.versions()[-1] == json.loads((CEDA / "generated" / "summary.json").read_text())["version"]


def test_change_requests_are_traceable(model):
    m, _ = model
    for cr_id, cr in m.change_requests.items():
        assert cr["status"] == "adopted", cr_id
        served = {e for r in cr["requirements"] for e in m.coverage["reqs"].get(r["id"], set())}
        assert served, f"{cr_id} has no realising entity"

