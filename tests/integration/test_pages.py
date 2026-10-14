import re

import pytest

pytestmark = pytest.mark.django_db(databases="__all__")


def test_public_verify_page_and_sign_in_redirect(world, client) -> None:  # type: ignore[no-untyped-def]
    r = client.get("/verify?number=NG-ABMOE-2026-00000199")
    assert r.status_code == 200 and b"No certificate found" in r.content
    r = client.get("/")
    assert r.status_code == 302 and r["Location"].startswith("/sign-in")


def test_head_signs_in_takes_register_and_opens_learner_360(world, as_user, client) -> None:  # type: ignore[no-untyped-def]
    from tests.conftest import make_user
    from tests.integration.test_operations_flows import enrol_class

    cls, ids = enrol_class(world, as_user, n=3)
    u, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    client.handler.enforce_csrf_checks = False
    r = client.post("/sign-in", {"username": u.username, "password": "correct-horse-battery"})
    assert r.status_code == 302
    home = client.get("/")
    assert home.status_code == 200, home.content
    assert b"registers</h2>" in home.content and cls.name.encode() in home.content, home.content.decode()[-3000:]
    page = client.get(f"/registers/class/{cls.id}")
    assert page.status_code == 200 and b"Save register" in page.content
    form = {f"mark_{lid}": "P" for lid in ids}
    form[f"mark_{ids[0]}"] = "L"
    form[f"late_{ids[0]}"] = "10"

    form["row_version"] = re.search(rb'name="row_version" value="(\d+)"', page.content).group(1).decode()
    r = client.post(f"/registers/class/{cls.id}", form)
    assert r.status_code == 200 and (b"Register submitted" in r.content or b"Register late" in r.content)
    r = client.get(f"/learners/{ids[0]}")
    assert r.status_code == 200 and b"Attendance (90 days)" in r.content and b"100.0%" in r.content
    assert client.get("/pages?q=ATT-01").status_code == 200
    assert client.get("/coverage").status_code == 200


def test_clearance_desk_and_establishment_pages(world, as_user, client) -> None:  # type: ignore[no-untyped-def]
    from syntegra.core.tenancy import SEED_STATE_TENANT
    from syntegra.institutions import services as inst
    from tests.conftest import make_user
    from tests.integration.test_fee_clearance import enrol_at, owe

    with as_user("STA", world.state_scope):
        private = inst.register(
            inst.RegisterInstitution(
                name="Lighthouse Academy",
                category="secondary",
                ownership="private",
                lga_scope_id=world.lga_scope,
                address={},
                levels=["sss_1"],
                operating_tenant_id=SEED_STATE_TENANT,
            )
        )
    lrn = enrol_at(world, as_user, private, "Tobenna")
    owe(world, as_user, private, lrn, 75_000)
    u, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    client.handler.enforce_csrf_checks = False
    assert client.post("/sign-in", {"username": u.username, "password": "correct-horse-battery"}).status_code == 302
    r = client.post(
        "/admissions/clearance",
        {
            "glid": lrn.global_learner_id,
            "institution_id": str(world.institution.id),
            "education_level": "SSS1",
            "purpose": "transfer",
        },
    )
    assert r.status_code == 200 and b"Outstanding" in r.content and b"Lighthouse Academy" in r.content
    check_id = re.search(rb'name="check_id" value="([0-9a-f-]+)"', r.content).group(1).decode()
    r = client.post(
        "/admissions/clearance",
        {
            "check_id": check_id,
            "decision": "admit_with_payment_plan",
            "payment_plan_ref": "LH-PP-7",
            "reason": "Plan agreed with Lighthouse",
        },
    )
    assert r.status_code == 200 and b"Decision recorded" in r.content
    assert client.get("/hr/establishment").status_code == 200  # heads hold hr:view


def test_national_clearance_network_page(world, client) -> None:  # type: ignore[no-untyped-def]
    from tests.conftest import make_user

    u, _ = make_user(world, "STA", world.state_scope)
    client.handler.enforce_csrf_checks = False
    assert client.post("/sign-in", {"username": u.username, "password": "correct-horse-battery"}).status_code == 302
    r = client.get("/clearance/network")
    assert r.status_code == 200 and b"National clearance network" in r.content
    assert b"NG-FC" in r.content and b"1 / 37" in r.content and b"(this state)" in r.content
    h, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    client.post("/sign-out")
    client.post("/sign-in", {"username": h.username, "password": "correct-horse-battery"})
    assert client.get("/clearance/network").status_code == 403


def test_register_learner_page(world, client) -> None:  # type: ignore[no-untyped-def]
    from tests.conftest import make_user

    u, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    client.handler.enforce_csrf_checks = False
    client.post("/sign-in", {"username": u.username, "password": "correct-horse-battery"})
    r = client.get("/learners/new")
    assert r.status_code == 200 and b"Check and register" in r.content and b"Lagos State" in r.content
    form = {
        "institution_id": str(world.institution.id),
        "education_level": "jss_1",
        "given": "Ifeoma",
        "family": "Nwosu",
        "date_of_birth": "2014-02-11",
        "dob_precision": "day",
        "sex": "female",
        "nin": "70000000017",
        "nationality": "NG",
    }
    assert b"enter the date of birth" in client.post("/learners/new", {**form, "date_of_birth": ""}).content
    assert b"NIN has 11 digits" in client.post("/learners/new", {**form, "nin": "123"}).content
    r = client.post("/learners/new", form)
    assert r.status_code == 200 and b"Registered" in r.content and b"LRN-" in r.content
    r = client.post("/learners/new", form)  # the same child again: linked, never duplicated
    assert r.status_code == 200 and b"Learner already enrolled" in r.content and b"request a transfer" in r.content
