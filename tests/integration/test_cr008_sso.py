"""Single sign-on by OpenID Connect (CR-003 FR-AUT-04–06, CR-008 FR-AUT-106), against an in-process identity provider
that signs real RS256 ID tokens and checks the PKCE verifier and client secret like a real one."""

from __future__ import annotations

import base64
import hashlib
import re
import time
import uuid
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from django.test import Client

from tests.conftest import api_sign_in, make_user, system_ctx, user_ctx

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "correct-horse-battery"
ISSUER = "https://id.abiastate.gov.ng"
CLIENT_ID = "syntegra-abia"
SECRET = "s3cret-from-the-provider"


class FakeIdP:
    """Discovery, keys, the authorization step and the token endpoint of an OpenID provider."""

    def __init__(self) -> None:
        from cryptography.hazmat.primitives.asymmetric import rsa

        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.kid = "key-2026"
        self.pending: dict[str, dict[str, Any]] = {}
        self.token_calls: list[dict[str, Any]] = []

    def jwks(self) -> dict[str, Any]:
        import json

        from jwt.algorithms import RSAAlgorithm

        jwk = json.loads(RSAAlgorithm.to_jwk(self.key.public_key()))
        return {"keys": [{**jwk, "kid": self.kid, "use": "sig", "alg": "RS256"}]}

    def get_json(self, url: str) -> dict[str, Any]:
        if url == f"{ISSUER}/.well-known/openid-configuration":
            return {
                "issuer": ISSUER,
                "authorization_endpoint": f"{ISSUER}/authorize",
                "token_endpoint": f"{ISSUER}/token",
                "jwks_uri": f"{ISSUER}/jwks",
                "code_challenge_methods_supported": ["S256"],
                "token_endpoint_auth_methods_supported": ["client_secret_basic"],
            }
        if url == f"{ISSUER}/jwks":
            return self.jwks()
        raise AssertionError(url)

    def authorize(self, url: str, **claims: Any) -> str:
        """The person signs in at the provider; returns the callback path the browser is sent back to."""
        q = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        assert url.startswith(f"{ISSUER}/authorize?") and q["client_id"] == CLIENT_ID and q["response_type"] == "code"
        assert q["code_challenge_method"] == "S256" and "openid" in q["scope"].split()
        code = uuid.uuid4().hex
        self.pending[code] = {"q": q, "claims": claims}
        return urlsplit(q["redirect_uri"]).path + "?" + urlencode({"code": code, "state": q["state"]})

    def post_form(self, url: str, data: dict[str, str], auth: tuple[str, str] | None = None) -> dict[str, Any]:
        import jwt

        from syntegra.iam.sso import SsoFailed

        assert url == f"{ISSUER}/token"
        self.token_calls.append({"data": data, "auth": auth})
        if auth != (CLIENT_ID, SECRET):
            raise SsoFailed("invalid_client")
        p = self.pending.pop(data["code"], None)
        if p is None:
            raise SsoFailed("invalid_grant")
        q, claims = p["q"], dict(p["claims"])
        challenge = base64.urlsafe_b64encode(hashlib.sha256(data["code_verifier"].encode()).digest()).rstrip(b"=")
        if challenge.decode() != q["code_challenge"] or data["redirect_uri"] != q["redirect_uri"]:
            raise SsoFailed("invalid_grant (PKCE)")
        now = int(time.time())
        body = {"iss": ISSUER, "aud": CLIENT_ID, "iat": now, "exp": now + 300, "nonce": q["nonce"], **claims}
        key = self.other if body.pop("_wrong_key", False) else self.key
        token = jwt.encode(body, key, algorithm="RS256", headers={"kid": self.kid})
        return {"access_token": "at", "token_type": "Bearer", "id_token": token}


@pytest.fixture
def idp(monkeypatch: Any) -> FakeIdP:
    from django.core.cache import cache

    from syntegra.iam import sso

    fake = FakeIdP()
    monkeypatch.setattr(sso, "_get_json", fake.get_json)
    monkeypatch.setattr(sso, "_post_form", fake.post_form)
    cache.clear()
    return fake


def _configure(world: Any, **over: Any) -> Any:
    from syntegra.core import context
    from syntegra.iam import sso

    with context.use(system_ctx()):
        admin_ctx = user_ctx(world.admin.id, world.users["STA"][1])
    args: dict[str, Any] = {
        "provider": "gov_sso",
        "label": "Sign in with Abia Government ID",
        "issuer": ISSUER,
        "client_id": CLIENT_ID,
        "client_secret": SECRET,
        "scopes": "openid email profile",
        "allowed_domains": ["abiastate.gov.ng"],
        "trust_idp_mfa": False,
        "sort_order": 1,
        "status": "active",
        **over,
    }
    with context.use(admin_ctx):
        return sso.save(admin_ctx, **args)


def _person(world: Any, role: str = "HEAD", local: str | None = None) -> tuple[Any, uuid.UUID]:
    from syntegra.core import context
    from syntegra.iam import services as iam

    email = f"{local or uuid.uuid4().hex[:8]}@abiastate.gov.ng"
    with context.use(system_ctx()):
        u = iam.create_user(system_ctx(), username=email, display_name="Mrs Ngozi Eze", password=PASSWORD)
        g = iam.grant_role(system_ctx(), user=u, role_code=role, scope_id=world.institution.scope_node_id)
    return u, g.id


def _sso(client: Any, idp: FakeIdP, nxt: str = "/", **claims: Any) -> Any:
    r = client.get(f"/auth/sso/gov_sso/start?next={nxt}")
    assert r.status_code == 302, r.content[-600:]
    return client.get(idp.authorize(r["Location"], **claims))


def _claims(user: Any, **over: Any) -> dict[str, Any]:
    return {"sub": f"gov-{user.id}", "email": user.username, "email_verified": True, **over}


def _confirm(client: Any) -> Any:
    page = client.get("/auth/context?next=/").content.decode()
    grant = re.search(r'name="grant_id" value="([0-9a-f-]{36})"', page)
    assert grant, page[-1500:]
    return client.post("/auth/context?next=/", {"grant_id": grant.group(1)})


def test_an_administrator_configures_a_provider_and_its_button_appears(world: Any, client: Any, idp: FakeIdP) -> None:
    from syntegra.core import context
    from syntegra.iam.models import IdentityProviderConfig

    assert b'id="sso"' not in client.get("/sign-in").content
    admin, _g = make_user(world, "STA", world.state_scope, "State Administrator")
    client.post("/sign-in", {"username": admin.username, "password": PASSWORD})
    _confirm(client)
    page = client.get("/admin/sign-in-providers")
    assert page.status_code == 200 and b"auth/sso/" in page.content
    form = {
        "provider": "gov_sso",
        "label": "Sign in with Abia Government ID",
        "issuer": ISSUER,
        "client_id": CLIENT_ID,
        "client_secret": SECRET,
        "scopes": "openid email",
        "allowed_domains": "abiastate.gov.ng, absu.edu.ng",
        "status": "active",
        "sort_order": "1",
    }
    r = client.post("/admin/sign-in-providers", {**form, "issuer": "http://id.abiastate.gov.ng"})
    assert r.status_code == 422 and b"https" in r.content
    r = client.post("/admin/sign-in-providers", form)
    assert r.status_code == 200 and b'id="providers-done"' in r.content and SECRET.encode() not in r.content
    with context.use(system_ctx()):
        row = IdentityProviderConfig.objects.get(provider="gov_sso")
    assert row.allowed_domains == ["abiastate.gov.ng", "absu.edu.ng"] and SECRET.encode() not in bytes(
        row.client_secret_enc
    )
    r = client.post("/admin/sign-in-providers", {"action": "check", "id": str(row.id)})
    assert r.status_code == 200 and b'id="checked"' in r.content and b"1 published" in r.content
    client.post("/sign-out")
    page = client.get("/sign-in").content.decode()
    assert 'id="sso-gov_sso"' in page and "Sign in with Abia Government ID" in page
    # a head of school cannot open the page
    head, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    other = Client()
    other.post("/sign-in", {"username": head.username, "password": PASSWORD})
    _confirm(other)
    assert other.get("/admin/sign-in-providers").status_code == 403


def test_sso_links_an_existing_account_and_then_the_password_no_longer_opens_it(
    world: Any, client: Any, idp: FakeIdP
) -> None:
    from syntegra.core import context
    from syntegra.iam.models import AppUser, UserSession

    _configure(world)
    user, _g = _person(world)
    r = _sso(client, idp, "/documents", **_claims(user))
    assert r.status_code == 302 and r["Location"].startswith("/auth/context") and "documents" in r["Location"]
    call = idp.token_calls[-1]
    assert call["auth"] == (CLIENT_ID, SECRET) and len(call["data"]["code_verifier"]) >= 43
    _confirm(client)
    assert client.get("/").status_code == 200
    with context.use(system_ctx()):
        u = AppUser.objects.get(pk=user.id)
        s = UserSession.objects.filter(user_id=user.id, revoked_at__isnull=True).get()
    assert (u.idp, u.idp_subject) == ("gov_sso", f"gov-{user.id}") and s.auth_method == "sso:gov_sso"
    # later sign-ins match the provider's subject, even if the e-mail changes there
    client.post("/sign-out")
    r = _sso(client, idp, **_claims(user, email="n.eze@abiastate.gov.ng"))
    assert r.status_code == 302 and r["Location"].startswith("/auth/context")
    client.post("/sign-out")
    # the password no longer opens a linked account
    r = client.post("/sign-in", {"username": user.username, "password": PASSWORD})
    assert r.status_code == 401 and b"organisation" in r.content


@pytest.mark.parametrize(
    ("claims", "message"),
    [
        ({"email_verified": False}, b"verified e-mail"),
        ({"email": "ngozi@gmail.com"}, b"gmail.com cannot sign in"),
        ({"email": "nobody@abiastate.gov.ng"}, b"no Syntegra account"),
        ({"_wrong_key": True}, b"not valid"),
        ({"aud": "another-app"}, b"not valid"),
        ({"exp": int(time.time()) - 3600}, b"not valid"),
        ({"nonce": "replayed"}, b"nonce"),
    ],
)
def test_sso_refuses_what_it_cannot_trust(
    world: Any, client: Any, idp: FakeIdP, claims: dict[str, Any], message: bytes
) -> None:
    _configure(world)
    user, _g = _person(world)
    r = _sso(client, idp, **_claims(user, **claims))
    assert r.status_code == 401 and message in r.content, r.content[-1200:]
    assert client.get("/")["Location"].startswith("/sign-in")  # no session


def test_the_state_and_the_browser_must_match(world: Any, client: Any, idp: FakeIdP) -> None:
    _configure(world)
    user, _g = _person(world)
    r = client.get("/auth/sso/gov_sso/start")
    back = idp.authorize(r["Location"], **_claims(user))
    stranger = Client()  # the callback opened in another browser: no signed cookie
    assert stranger.get(back).status_code == 401
    forged = re.sub(r"state=[^&]+", "state=forged", back)
    assert client.get(forged).status_code == 401
    assert client.get("/auth/sso/entra/start").status_code == 404  # not configured


def test_the_providers_mfa_counts_only_when_trusted(world: Any, client: Any, idp: FakeIdP, settings: Any) -> None:
    from syntegra.core import context
    from syntegra.iam.models import UserSession

    settings.SYNTEGRA_MFA_REQUIRED_CLEARANCE = "restricted"
    _configure(world)
    user, _g = _person(world)  # a head of school: Level 4 needs a second factor
    r = _sso(client, idp, **_claims(user, amr=["pwd", "mfa"]))
    assert r["Location"].startswith("/me/authenticator")  # not trusted: set up the local authenticator
    client.post("/sign-out")
    _configure(world, trust_idp_mfa=True, client_secret=None)  # the stored secret is kept
    r = _sso(client, idp, **_claims(user, amr=["pwd", "mfa"]))
    assert r["Location"].startswith("/auth/context")
    with context.use(system_ctx()):
        s = UserSession.objects.filter(user_id=user.id, revoked_at__isnull=True).get()
    assert s.auth_method == "sso:gov_sso+idp_mfa" and s.mfa_at is not None
    client.post("/sign-out")
    r = _sso(client, idp, **_claims(user, amr=["pwd"]))  # trusted provider, but no MFA this time
    assert r["Location"].startswith("/me/authenticator")


def test_providers_through_the_api(world: Any, idp: FakeIdP) -> None:
    admin, _g = make_user(world, "STA", world.state_scope, "API Administrator")
    api = Client(HTTP_AUTHORIZATION=f"Bearer {api_sign_in(Client(), admin.username, PASSWORD)}")
    body = {
        "provider": "entra",
        "label": "Sign in with Microsoft",
        "issuer": "https://login.microsoftonline.com/abia/v2.0",
        "client_id": "abc",
        "client_secret": "xyz",
        "allowed_domains": ["abiastate.gov.ng"],
    }
    r = api.post("/api/v1/admin/sign-in-providers", body, content_type="application/json")
    assert r.status_code == 201 and r.json()["has_secret"] is True and "xyz" not in r.content.decode()
    assert [p["provider"] for p in api.get("/api/v1/admin/sign-in-providers").json()["results"]] == ["entra"]
    public = Client().get("/api/v1/auth/sso/providers").json()["providers"]
    assert public == [{"provider": "entra", "label": "Sign in with Microsoft", "start": "/auth/sso/entra/start"}]
    head, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    other = Client(HTTP_AUTHORIZATION=f"Bearer {api_sign_in(Client(), head.username, PASSWORD)}")
    assert other.get("/api/v1/admin/sign-in-providers").status_code == 403
