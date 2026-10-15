"""CR-006 pages, forms and API: budgets and imprest, funding and loans, facilities and the infrastructure overview."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tests.conftest import system_ctx, web_sign_in

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "Demo-password-2026"


def _sign_in(client: Any, username: str) -> None:
    client.post("/sign-out")
    client.handler.enforce_csrf_checks = False
    r = web_sign_in(client, {"username": username, "password": PASSWORD})
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


def _submit(client: Any, key: str, data: dict[str, str], expect: str) -> str:
    r = client.post(f"/forms/{key}", data)
    body = r.content.decode()
    errors = re.findall(r'class="(?:err|alert alert-error)"[^>]*>([^<]*)<', body)
    assert r.status_code == 200 and expect in body, (key, r.status_code, errors, body[-1500:])
    return body


def test_every_cr006_form_completes_its_task(world: Any, client: Any) -> None:
    """Each budget, imprest, funding and facilities form, filled in correctly, does what it says (by role)."""
    import datetime as dt

    from syntegra.core import context
    from syntegra.institutions.models import Institution
    from syntegra.platform.demo import abia

    abia.run(
        abia.Scale(
            schools_per_lga=1,
            pupils=12,
            lgas=1,
            absu_students=6,
            asceta_students=3,
            absu_staff=6,
            asceta_staff=2,
            days=1,
        ),
        log=lambda _m: None,
    )
    with context.use(system_ctx()):
        absu = Institution.objects.get(name="Abia State University, Uturu")
        officer = f"estate.{absu.institution_code.lower()}@abia.demo"
    later = (dt.date.today() + dt.timedelta(days=30)).isoformat()

    # budget: prepare (bursar) → approve (vice-chancellor) → commit → spend
    _sign_in(client, "bursar.absu@abia.demo")
    _submit(
        client,
        "budget-prepare",
        {
            "institution_id": str(absu.id),
            "fiscal_year": "2027",
            "lines_text": "REG | 22020301 | 1,000,000 | overhead | Stationery 2027",
        },
        "saved",
    )
    _sign_in(client, "vc.absu@abia.demo")
    form = _ok(client.get("/forms/budget-approve"))
    _submit(client, "budget-approve", {"target": _option(form, "target", "2027")}, "approved")
    _sign_in(client, "bursar.absu@abia.demo")
    form = _ok(client.get("/forms/budget-commit"))
    line = _option(form, "budget_line_id", "Stationery 2027")
    _submit(
        client,
        "budget-commit",
        {
            "budget_line_id": line,
            "amount_minor": "250,000",
            "source_kind": "purchase_order",
            "description": "LPO 7 printer paper",
        },
        "committed",
    )
    form = _ok(client.get("/forms/budget-spend"))
    _submit(
        client,
        "budget-spend",
        {"target": _option(form, "target", "LPO 7"), "amount_minor": "200,000", "final": "on"},
        "Spending recorded",
    )

    # imprest: request (bursar) → approve (vice-chancellor) → retire (bursar)
    form = _ok(client.get("/forms/imprest-request"))
    holder = re.search(r'name="holder_staff_id".*?<option value="([0-9a-f-]{36})"', form, re.S)
    assert holder
    _submit(
        client,
        "imprest-request",
        {
            "holder_staff_id": holder.group(1),
            "budget_line_id": line,
            "purpose": "Sports day first aid",
            "amount_minor": "50,000",
            "retire_by": later,
        },
        "requested",
    )
    _sign_in(client, "vc.absu@abia.demo")
    form = _ok(client.get("/forms/imprest-approve"))
    _submit(client, "imprest-approve", {"target": _option(form, "target", "Sports day"), "approve": "true"}, "issued")
    _sign_in(client, "bursar.absu@abia.demo")
    form = _ok(client.get("/forms/imprest-retire"))
    _submit(
        client,
        "imprest-retire",
        {
            "target": _option(form, "target", "Sports day"),
            "receipts_text": "RCT-1 | 30,000 | Mercy Pharmacy\nRCT-2 | 15,000 | Caterer",
            "amount_minor": "45,000",
            "refund_minor": "5,000",
        },
        "is now retired",
    )

    # funding: apply (bursar) → review (HR) → decide and sign (state) → disburse and repay (bursar)
    form = _ok(client.get("/forms/funding-apply"))
    staff = re.search(r'name="staff_id".*?<option value="([0-9a-f-]{36})"', form, re.S)
    assert staff
    _submit(
        client,
        "funding-apply",
        {
            "programme_id": _option(form, "programme_id", "Salary advance"),
            "applicant_kind": "staff",
            "institution_id": str(absu.id),
            "staff_id": staff.group(1),
            "amount_minor": "100,000",
            "purpose_detail": "Emergency medical bills for a dependant",
        },
        "submitted",
    )
    _sign_in(client, "hr.absu@abia.demo")
    form = _ok(client.get("/forms/funding-recommend"))
    target = _option(form, "target", "staff — ₦100,000.00")
    _submit(
        client,
        "funding-recommend",
        {"target": target, "recommendation": "Confirmed staff; recommended."},
        "recommended",
    )
    _sign_in(client, "director.planning@abia.gov.ng")
    _submit(
        client,
        "funding-decide",
        {"target": target, "approve": "true", "reason": "Within limits and affordable."},
        "approved",
    )
    _submit(client, "funding-sign", {"target": target, "gross_pay_minor": "450,000"}, "signed")
    _sign_in(client, "bursar.absu@abia.demo")
    form = _ok(client.get("/forms/funding-disburse"))
    agreement = _option(form, "target", "salary advance")
    _submit(
        client,
        "funding-disburse",
        {
            "target": agreement,
            "amount_minor": "100,000",
            "payee_kind": "beneficiary",
            "purpose": "Advance",
            "reference": "SA-0001",
        },
        "disbursed",
    )
    _submit(
        client,
        "funding-repay",
        {"target": agreement, "amount_minor": "10,000", "method": "payroll_deduction", "reference": "PR-0001"},
        "recorded",
    )
    assert "Repayment schedule" in _ok(client.get(f"/funding/agreements/{agreement}"))

    # facilities: site, building, room, equipment, maintenance plan and done, an action and a work order
    _sign_in(client, officer)
    inst = str(absu.id)
    _submit(
        client,
        "estate-site",
        {
            "institution_id": inst,
            "site_code": "ANNEX",
            "name": "Annex",
            "owner": "state_government",
            "title_document": "gazette",
            "fenced": "partly_fenced",
            "encroachment": "none",
            "area_sqm": "12000",
            "latitude": "5.83",
            "longitude": "7.33",
        },
        "registered",
    )
    _submit(client, "estate-building", {"institution_id": inst, "name": "Science block", "built_year": "1999"}, "added")
    form = _ok(client.get("/forms/estate-room"))
    _submit(
        client,
        "estate-room",
        {
            "building_id": _option(form, "building_id", "Science block"),
            "code": "S1",
            "room_type": "laboratory",
            "capacity": "40",
        },
        "added",
    )
    _submit(
        client,
        "estate-asset",
        {
            "institution_id": inst,
            "asset_tag": "INV-01",
            "name": "Solar inverter",
            "category": "solar_system",
            "next_service_on": later,
            "value_minor": "1,200,000",
        },
        "added",
    )
    form = _ok(client.get("/forms/estate-schedule"))
    _submit(
        client,
        "estate-schedule",
        {
            "facility": _option(form, "facility", "Equipment INV-01"),
            "task": "Inspect solar inverter",
            "task_kind": "solar_service",
            "frequency_days": "90",
            "next_due_on": later,
            "estimated_cost_minor": "30,000",
        },
        "Planned",
    )
    form = _ok(client.get("/forms/estate-done"))
    _submit(
        client,
        "estate-done",
        {
            "target": _option(form, "target", "Inspect solar inverter"),
            "cost_minor": "25,000",
            "note": "Terminals cleaned",
        },
        "Done",
    )
    form = _ok(client.get("/forms/estate-assess"))
    _submit(
        client,
        "estate-assess",
        {
            "facility": _option(form, "facility", "Room S1"),
            "condition_grade": "poor",
            "usability": "usable_major_repairs",
            "structural_risk": "moderate",
            "in_use": "on",
            "repair_estimate_minor": "400,000",
        },
        "Assessment recorded",
    )
    form = _ok(client.get("/forms/estate-action"))
    first = re.search(r'name="target".*?<option value="([0-9a-f-]{36})"', form, re.S)
    assert first
    _submit(client, "estate-work-order", {"target": first.group(1)}, "Work order raised")
    _submit(client, "estate-action", {"target": first.group(1), "status": "in_progress", "note": ""}, "in progress")
    assert "Science block" in _ok(client.get(f"/estate?institution_id={inst}"))
