"""CR-008 authenticator self-enrolment, enforced at sign-in for roles that need a second factor (FR-AUT-104/105), with
single-use recovery codes — on the pages and through the API."""

from __future__ import annotations

import re
import time
from typing import Any

import pytest
from django.test import Client

from tests.conftest import make_user, system_ctx

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "correct-horse-battery"


@pytest.fixture
def required(settings: Any) -> None:
    settings.SYNTEGRA_MFA_REQUIRED_CLEARANCE = "restricted"


def _totp(seed: str, ahead: int = 0) -> str:
    from syntegra.iam import services as iam

    return iam.totp(seed, time.time() + 30 * ahead)


def _sign_in(client: Any, user: Any, nxt: str = "/") -> Any:
    return client.post(f"/sign-in?next={nxt}", {"username": user.username, "password": PASSWORD})


def _confirm(client: Any) -> Any:
    page = client.get("/auth/context?next=/").content.decode()
    grant = re.search(r'name="grant_id" value="([0-9a-f-]{36})"', page)
    assert grant, page[-1500:]
    return client.post("/auth/context?next=/", {"grant_id": grant.group(1)})


def _enrol_on_page(client: Any, url: str) -> tuple[str, list[str], Any]:
    page = client.get(url)
    assert page.status_code == 200, page.content[-800:]
    html = page.content.decode()
    seed = re.search(r'<code class="hash" id="secret">([A-Z2-7 ]+)</code>', html).group(1).replace(" ", "")  # type: ignore[union-attr]
    factor = re.search(r'name="factor_id" value="([0-9a-f-]{36})"', html).group(1)  # type: ignore[union-attr]
    assert "<svg" in html and 'id="qr"' in html  # the QR code is drawn on the page itself
    bad = "000000" if _totp(seed) != "000000" else "111111"
    r = client.post(url, {"factor_id": factor, "code": bad})
    assert r.status_code == 422 and b"did not match" in r.content
    r = client.post(url, {"factor_id": factor, "code": _totp(seed)})
    assert r.status_code == 200
    codes = re.findall(r"<li><code>([A-Z2-9]{5}-[A-Z2-9]{5})</code></li>", r.content.decode())
    return seed, codes, r


def test_a_user_whose_roles_need_it_sets_up_an_authenticator_before_anything_opens(
    world: Any, client: Any, required: None
) -> None:
    head, _g = make_user(world, "HEAD", world.institution.scope_node_id)  # Level 4 · Restricted
    r = _sign_in(client, head, "/documents")
    assert r.status_code == 302 and r["Location"].startswith("/me/authenticator")
    for path in ("/", "/documents", "/auth/context", "/me"):
        assert client.get(path)["Location"].startswith("/me/authenticator"), path
    seed, codes, done = _enrol_on_page(client, r["Location"])
    assert 'id="enrolled"' in done.content.decode() and len(codes) == 10 and len(set(codes)) == 10
    nxt = re.search(r'href="([^"]+)" id="continue"', done.content.decode()).group(1)  # type: ignore[union-attr]
    assert nxt.startswith("/auth/context") and "documents" in nxt
    _confirm(client)
    assert client.get("/documents", follow=True).status_code == 200
    me = client.get("/me").content.decode()
    assert 'id="factors"' in me and "10 of 10 recovery codes left" in me
    # the next sign-in asks for the code, and a recovery code stands in for it once
    client.post("/sign-out")
    r = _sign_in(client, head)
    assert r["Location"].startswith("/auth/mfa")
    assert client.post("/auth/mfa", {"code": codes[0].lower()}).status_code == 302
    _confirm(client)
    assert "9 of 10 recovery codes left" in client.get("/me").content.decode()
    client.post("/sign-out")
    _sign_in(client, head)
    assert client.post("/auth/mfa", {"code": codes[0]}).status_code == 401  # spent
    assert client.post("/auth/mfa", {"code": _totp(seed, 1)}).status_code == 302


def test_roles_below_the_threshold_are_not_made_to_enrol(world: Any, client: Any, required: None) -> None:
    teacher, _g = make_user(world, "TCH", world.institution.scope_node_id)  # Level 3 · Confidential
    r = _sign_in(client, teacher)
    assert r["Location"].startswith("/auth/context")
    _confirm(client)
    assert client.get("/").status_code == 200
    # but anyone may add an authenticator, and is then asked for it
    _seed, codes, _done = _enrol_on_page(client, "/me/authenticator")
    assert len(codes) == 10
    client.post("/sign-out")
    assert _sign_in(client, teacher)["Location"].startswith("/auth/mfa")


def test_removing_and_adding_factors_needs_the_second_factor_and_keeps_the_last(
    world: Any, client: Any, settings: Any
) -> None:
    from syntegra.core import context
    from syntegra.iam.models import MfaFactor, MfaRecoveryCode

    head, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    _sign_in(client, head)
    _confirm(client)
    seed, old_codes, _ = _enrol_on_page(client, "/me/authenticator")
    with context.use(system_ctx()):
        factor = MfaFactor.objects.get(user_id=head.id, status="active")
    # a session that has not passed the code cannot add or remove a factor
    client.post("/sign-out")
    _sign_in(client, head)
    other = client
    assert other.get("/me/authenticator")["Location"].startswith("/auth/mfa")
    assert other.post(f"/me/authenticator/{factor.id}/remove")["Location"].startswith("/auth/mfa")
    other.post("/auth/mfa", {"code": _totp(seed, 1)})
    _confirm(other)
    # new recovery codes replace the old ones
    r = other.post("/me/recovery-codes")
    new_codes = re.findall(r"<li><code>([A-Z2-9]{5}-[A-Z2-9]{5})</code></li>", r.content.decode())
    assert len(new_codes) == 10 and not set(new_codes) & set(old_codes)
    # the last authenticator of an account whose roles need one stays
    settings.SYNTEGRA_MFA_REQUIRED_CLEARANCE = "restricted"
    r = other.post(f"/me/authenticator/{factor.id}/remove")
    assert r.status_code == 422 and b"Add your new authenticator app first" in r.content
    settings.SYNTEGRA_MFA_REQUIRED_CLEARANCE = ""
    r = other.post(f"/me/authenticator/{factor.id}/remove")
    assert r.status_code == 302 and r["Location"] == "/me?removed=1"
    with context.use(system_ctx()):
        assert not MfaFactor.objects.filter(user_id=head.id, status="active").exists()
        assert not MfaRecoveryCode.objects.filter(user_id=head.id, status="active").exists()


def test_the_api_enrols_and_enforces_in_the_same_way(world: Any, client: Any, required: None) -> None:
    head, g = make_user(world, "HEAD", world.institution.scope_node_id)
    r = client.post(
        "/api/v1/auth/sign-in", {"username": head.username, "password": PASSWORD}, content_type="application/json"
    )
    assert r.status_code == 201 and r.json()["mfa_setup_required"] is True and r.json()["mfa_required"] is False
    api = Client(HTTP_AUTHORIZATION=f"Bearer {r.json()['token']}")
    api.post("/api/v1/auth/role", {"grant_id": str(g)}, content_type="application/json")
    r = api.get("/api/v1/documents/categories")
    assert r.status_code == 403 and "/api/v1/me/mfa/totp" in r.content.decode()
    assert api.get("/api/v1/me/mfa").json()["required"] is True
    r = api.post("/api/v1/me/mfa/totp", {}, content_type="application/json")
    assert r.status_code == 201 and r.json()["otpauth_uri"].startswith("otpauth://totp/Syntegra")
    seed, fid = r.json()["secret"], r.json()["factor_id"]
    bad = "000000" if _totp(seed) != "000000" else "111111"
    assert (
        api.post(f"/api/v1/me/mfa/totp/{fid}/confirm", {"code": bad}, content_type="application/json").status_code
        == 422
    )
    r = api.post(f"/api/v1/me/mfa/totp/{fid}/confirm", {"code": _totp(seed)}, content_type="application/json")
    assert r.status_code == 200 and len(r.json()["recovery_codes"]) == 10
    assert api.get("/api/v1/documents/categories").status_code == 200
    status = api.get("/api/v1/me/mfa").json()
    assert status["passed"] is True and len(status["factors"]) == 1 and status["recovery_codes_left"] == 10
