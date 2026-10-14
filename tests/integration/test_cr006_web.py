"""CR-006 pages, forms and API: budgets and imprest, funding and loans, facilities and the infrastructure overview."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tests.conftest import system_ctx

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "Demo-password-2026"


def _sign_in(client: Any, username: str) -> None:
    client.post("/sign-out")
    client.handler.enforce_csrf_checks = False
    r = client.post("/sign-in", {"username": username, "password": PASSWORD})
    assert r.status_code == 302, r.content.decode()[-1500:]


def _ok(r: Any) -> str:
    body = r.content.decode()
    assert r.status_code == 200, body[-2500:]
    return body


def _option(page: str, field: str, text: str) -> str:
    """The value of the first option of ``field`` whose label contains ``text``."""
    block = re.search(rf'name="{field}".*?</select>', page, re.S)
    assert block, field
    m = re.search(rf'<option value="([^"]+)"[^>]*>[^<]*{re.escape(text)}', block.group(0))
    assert m, (field, text, block.group(0)[:1500])
    return m.group(1)


def test_budgets_funding_and_facilities_pages_forms_and_api(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.institutions.models import Institution
    from syntegra.platform.demo import abia

    abia.run(
        abia.Scale(
            schools_per_lga=1,
            pupils=12,
            lgas=2,
            absu_students=6,
            asceta_students=3,
            absu_staff=4,
            asceta_staff=2,
            days=2,
        ),
        log=lambda _m: None,
    )
    with context.use(system_ctx()):
        absu = Institution.objects.get(name="Abia State University, Uturu")

    # the bursar: budget against actual, imprest, funding, and a virement that someone else must approve
    _sign_in(client, "bursar.absu@abia.demo")
    home = _ok(client.get("/"))
    assert 'href="/finance/performance"' in home and 'href="/funding"' in home
    page = _ok(client.get(f"/finance/performance?institution_id={absu.id}&fiscal_year=2026"))
    assert "Maintenance of buildings" in page and "Rehabilitation of lecture theatres" in page
    page = _ok(client.get("/finance/imprest"))
    assert "Matriculation ceremony" in page and "Issued" in page
    page = _ok(client.get("/funding"))
    assert "Staff co-operative society loan" in page and "TETFund" in page
    agreement = re.search(r'href="/funding/agreements/([0-9a-f-]{36})"', page)
    assert agreement
    page = _ok(client.get(f"/funding/agreements/{agreement.group(1)}"))
    assert "Repayment schedule" in page or "Disbursements" in page

    form = _ok(client.get("/forms/budget-cost-centre"))
    r = client.post(
        "/forms/budget-cost-centre",
        {"institution_id": str(absu.id), "code": "SPORTS", "name": "Sports Council", "kind": "sports"},
    )
    assert "Cost centre SPORTS added" in _ok(r)
    form = _ok(client.get("/forms/budget-virement"))
    src = _option(form, "from_line_id", "Maintenance of buildings")
    dst = _option(form, "to_line_id", "Books and journals")
    r = client.post(
        "/forms/budget-virement",
        {"from_line_id": src, "to_line_id": dst, "amount_minor": "2,000,000", "reason": "Library e-journal renewal"},
    )
    assert "submitted for approval" in _ok(r)
    bad = client.post(
        "/forms/budget-prepare", {"institution_id": str(absu.id), "fiscal_year": "2027", "lines_text": "X | 1 | y"}
    )
    assert bad.status_code == 422 and "cost-centre codes" in bad.content.decode()

    # the vice-chancellor approves the virement (four eyes)
    _sign_in(client, "vc.absu@abia.demo")
    form = _ok(client.get("/forms/budget-virement-decision"))
    target = _option(form, "target", "Library e-journal")
    assert "Virement" in _ok(client.post("/forms/budget-virement-decision", {"target": target, "approve": "true"}))

    # the facilities officer: workspace, an assessment that raises an action, the action list
    with context.use(system_ctx()):
        officer = f"estate.{absu.institution_code.lower()}@abia.demo"
    _sign_in(client, officer)
    page = _ok(client.get(f"/estate?institution_id={absu.id}"))
    assert "Classroom block A" in page and "Do these first" in page
    form = _ok(client.get("/forms/estate-assess"))
    room = _option(form, "facility", "Room A1")
    r = client.post(
        "/forms/estate-assess",
        {"facility": room, "condition_grade": "unsafe", "usability": "unsafe_restricted", "structural_risk": "high",
         "in_use": "on", "learners_affected": "45", "repair_estimate_minor": "850,000"},
    )  # fmt: skip
    assert "Assessment recorded" in _ok(r)
    page = _ok(client.get("/estate/actions"))
    assert "Critical" in page or "High" in page

    # the Commissioner: the state infrastructure overview, the property register, funding across the state
    _sign_in(client, "commissioner.education@abia.gov.ng")
    page = _ok(client.get("/estate/state"))
    assert "Usable classrooms" in page and "Institutions needing attention first" in page
    assert "Abia State University" in _ok(client.get("/estate/property"))
    assert _ok(client.get("/funding"))
    assert client.get("/estate/state?scope_id=not-a-uuid").status_code == 422

    # the API: same services, same validation
    r = client.post(
        "/api/v1/auth/sign-in",
        {"username": "bursar.absu@abia.demo", "password": PASSWORD},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {r.json()['token']}"}
    r = client.get("/api/v1/finance/budgets?fiscal_year=2026", **auth)
    assert r.status_code == 200 and r.json()["totals"]["revised"] > 0
    r = client.post(
        "/api/v1/finance/cost-centres",
        {"institution_id": str(absu.id), "code": "X1", "name": "X", "kind": "not-a-kind"},
        content_type="application/json",
        **auth,
    )
    assert r.status_code in (400, 422) and "kind" in r.content.decode()
    assert client.get("/api/v1/funding/programmes?beneficiary_kind=staff", **auth).status_code == 200
    assert client.get("/api/v1/funding/overview", **auth).status_code == 200
    assert client.get("/api/v1/finance/imprest?status=bogus", **auth).status_code in (400, 422)
    r = client.get(f"/api/v1/estate/institutions/{absu.id}/workspace", **auth)
    assert r.status_code in (200, 403)  # a bursar may or may not hold estate:view
