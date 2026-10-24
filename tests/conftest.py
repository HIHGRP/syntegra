"""Test fixtures. Integration tests run on real MySQL 9.7 (MFS §16.7) — never SQLite.

Django creates ``test_<schema>`` for every zone alias and applies the CEDA DDL through the ``schema``
migrations; the seed tenant is provisioned once per session with ``platform.bootstrap``.
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import pytest

ALL = "__all__"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup: Any, django_db_blocker: Any) -> Iterator[None]:
    from syntegra.platform.bootstrap import bootstrap

    with django_db_blocker.unblock():
        bootstrap(admin_password="admin-password-123")
    return


@dataclass
class World:
    state_scope: uuid.UUID
    lga_scope: uuid.UUID
    lga2_scope: uuid.UUID
    admin: Any
    institution: Any = None
    institution2: Any = None
    period: Any = None
    users: dict[str, Any] = field(default_factory=dict)
    tokens: dict[str, str] = field(default_factory=dict)


def guardian(family: str = "Okafor", given: str = "Adaeze", **kw: Any) -> Any:
    """A parent with parental responsibility — every minor registered in the tests needs one (FR-LRN-06)."""
    from syntegra.families.services import GuardianInput

    kw.setdefault("phone", f"0803{abs(hash((given, family))) % 10_000_000:07d}")
    kw.setdefault("relationship", "mother")
    return GuardianInput(given=given, family=family, **kw)


def system_ctx() -> Any:
    from syntegra.core import context
    from syntegra.core.tenancy import SEED_STATE_TENANT

    return context.system(SEED_STATE_TENANT, SEED_STATE_TENANT)


def user_ctx(user_id: uuid.UUID, grant_id: uuid.UUID, **kw: Any) -> Any:
    from syntegra.core import authz
    from syntegra.core.context import Context
    from syntegra.core.tenancy import SEED_STATE_TENANT

    base = Context(
        tenant_id=SEED_STATE_TENANT, state_tenant_id=SEED_STATE_TENANT, actor_kind="user", actor_id=user_id, **kw
    )
    from syntegra.core import context

    with context.use(base):
        return authz.grant_context(base, grant_id)


@pytest.fixture
def world(db: Any, django_db_blocker: Any) -> World:
    from syntegra.core import context
    from syntegra.governance.models import ScopeNode
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions import services as inst

    sysctx = system_ctx()
    with context.use(sysctx):
        state = ScopeNode.objects.get(code="NG-AB")
        lga = ScopeNode.objects.get(code="AB-ABS")
        lga2 = ScopeNode.objects.get(code="AB-UMN")
        admin = AppUser.objects.get(username="admin@abia.gov.ng")
        w = World(state.id, lga.id, lga2.id, admin)
        w.users["STA"] = (admin, RoleGrant.objects.get(user_id=admin.id).id)
        admin_ctx = user_ctx(admin.id, w.users["STA"][1])
    with context.use(admin_ctx):
        w.institution = inst.register(
            inst.RegisterInstitution(
                name="Government Secondary School Aba",
                category="secondary",
                ownership="state",
                lga_scope_id=lga.id,
                address={"town": "Aba", "lga": "Aba South"},
                levels=["jss_1", "jss_2", "jss_3"],
                gov_reg_no="AB/SS/0412",
                location=(7.3667, 5.1066),
                capacity=1200,
            )
        )
        w.institution2 = inst.register(
            inst.RegisterInstitution(
                name="Umuahia Primary School",
                category="primary",
                ownership="state",
                lga_scope_id=lga2.id,
                address={"town": "Umuahia"},
                levels=["primary_4", "primary_5", "jss_1"],
                gov_reg_no="AB/PS/0099",
                location=(7.4896, 5.5320),
            )
        )
    with context.use(sysctx):
        from syntegra.academic import services as academic

        w.period = academic.create_session(
            w.state_scope, f"2026/2027-{uuid.uuid4().hex[:6]}", dt.date(2026, 9, 7), dt.date(2027, 7, 23)
        )
    return w


def make_user(w: World, role: str, scope_id: uuid.UUID, name: str | None = None) -> tuple[Any, uuid.UUID]:
    from syntegra.core import context
    from syntegra.iam import services as iam

    with context.use(system_ctx()):
        u = iam.create_user(
            system_ctx(),
            username=f"{(name or role).lower()}-{uuid.uuid4().hex[:8]}@test.ng",
            display_name=name or role,
            password="correct-horse-battery",
        )
        g = iam.grant_role(system_ctx(), user=u, role_code=role, scope_id=scope_id)
    return u, g.id


@pytest.fixture
def as_user(world: World) -> Any:
    """``with as_user("HEAD", scope) as ctx:`` — run service code as a fresh user holding ``role`` at ``scope``."""
    import contextlib

    from syntegra.core import context

    @contextlib.contextmanager
    def _as(role: str, scope_id: uuid.UUID, **kw: Any) -> Iterator[Any]:
        u, g = make_user(world, role, scope_id)
        ctx = user_ctx(u.id, g, **kw)
        with context.use(ctx):
            yield ctx

    return _as


@pytest.fixture
def api(world: World, client: Any) -> Any:
    """Return a function that signs a new user in with ``role`` at ``scope`` and yields an API caller."""

    def _api(role: str, scope_id: uuid.UUID) -> Any:
        u, _ = make_user(world, role, scope_id)
        r = client.post(
            "/api/v1/auth/sign-in",
            {"username": u.username, "password": "correct-horse-battery"},
            content_type="application/json",
        )
        assert r.status_code == 201, r.content
        token = r.json()["token"]
        confirm = client.post(  # confirm the school or office, as every API client must (FR-AUT-101)
            "/api/v1/auth/role",
            {"grant_id": r.json()["grants"][0]["grant_id"]},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert confirm.status_code == 200, confirm.content

        class Caller:
            user = u

            def __call__(self, method: str, path: str, body: Any = None, **headers: str) -> Any:
                h = {f"HTTP_{k.upper().replace('-', '_')}": v for k, v in headers.items()}
                fn = getattr(client, method.lower())
                kw: dict[str, Any] = {"HTTP_AUTHORIZATION": f"Bearer {token}", **h}
                if body is not None:
                    kw.update(data=body, content_type="application/json")
                return fn(path, **kw)

        return Caller()

    return _api


FSE_HOST = "fse.testserver"
FED_HOST = "fed.testserver"


@pytest.fixture(scope="session")
def fse(django_db_setup: Any, django_db_blocker: Any) -> Iterator[Any]:
    """Provision the Federal Security Education registry once and load the reference data (CR-004/CR-005)."""
    from syntegra.core import tenancy
    from syntegra.security_training import registry

    with django_db_blocker.unblock():
        p = registry.provision(hosts=[FSE_HOST])
        seeded = registry.seed_reference()
    tenancy.clear_caches()
    yield p, seeded
    tenancy.clear_caches()


@pytest.fixture(scope="session")
def fed(django_db_setup: Any, django_db_blocker: Any) -> Iterator[Any]:
    """Provision the Federal Institutions registry once and load the reference data (CR-005)."""
    from syntegra.core import tenancy
    from syntegra.federal_institutions import registry

    with django_db_blocker.unblock():
        p = registry.provision(hosts=[FED_HOST])
        seeded = registry.seed_reference()
    tenancy.clear_caches()
    yield p, seeded
    tenancy.clear_caches()


def web_sign_in(client: Any, data: dict[str, Any], **kw: Any) -> Any:
    """Sign in through the page and confirm the school or office shown after the password (CR-007, AUT-03).
    Returns the sign-in response, like ``client.post("/sign-in", ...)``."""
    import re

    r = client.post("/sign-in", data, **kw)
    if r.status_code == 302 and r["Location"].startswith("/auth/context"):
        page = client.get(r["Location"], **kw)
        m = re.search(r'name="grant_id" value="([0-9a-f-]{36})"', page.content.decode())
        if m:
            client.post(r["Location"], {"grant_id": m.group(1)}, **kw)
    return r


def api_sign_in(client: Any, username: str, password: str, **kw: Any) -> str:
    """Sign in through the API and confirm the first grant's school or office (FR-AUT-101); returns the token."""
    r = client.post(
        "/api/v1/auth/sign-in", {"username": username, "password": password}, content_type="application/json", **kw
    )
    assert r.status_code == 201, r.content
    token = str(r.json()["token"])
    confirm = client.post(
        "/api/v1/auth/role",
        {"grant_id": r.json()["grants"][0]["grant_id"]},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert confirm.status_code == 200, confirm.content
    return token
