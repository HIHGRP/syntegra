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
