"""CR-008 FR-ADM-203: a write through the API needs the access level of the web form that performs the same action,
so pages, forms and the API apply one rule."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

import pytest

from tests.conftest import api_sign_in, make_user, system_ctx, user_ctx

PASSWORD = "correct-horse-battery"
UNSAFE = ("post", "put", "patch", "delete")


def _api_writes() -> Iterator[tuple[str, str, Any]]:
    from django.urls import URLPattern, URLResolver, get_resolver

    def walk(patterns: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
        for p in patterns:
            if isinstance(p, URLResolver):
                yield from walk(p.url_patterns, prefix + str(p.pattern))
            elif isinstance(p, URLPattern):
                yield prefix + str(p.pattern), p.callback

    for route, cb in walk(get_resolver().url_patterns):
        cls = getattr(cb, "view_class", None) or getattr(cb, "cls", None)
        if cls is not None and route.startswith("api/"):
            for m in UNSAFE:
                if hasattr(cls, m):
                    yield route, m.upper(), cls


def _write_permissions(cls: Any, method: str) -> tuple[str, ...]:
    perm = cls.required_permission if hasattr(cls, "required_permission") else None
    if isinstance(perm, dict):
        perm = perm.get(method) or perm.get("*")
    return tuple(getattr(cls, "level_permissions", None) or ((perm,) if perm else ()))


def test_every_form_action_has_the_same_level_through_the_api() -> None:
    """Each permission a form writes with is level-checked on an API write, at the form's level."""
    from syntegra.core import access
    from syntegra.web import forms

    levels = access.write_levels()
    assert levels == forms.write_levels() and levels
    for f in forms.FORMS:
        for p in (f.permission,) if isinstance(f.permission, str) else f.permission:
            assert access.covers(levels[p], forms.level(f)), (f.key, p)
    covered = {p for route, method, cls in _api_writes() for p in _write_permissions(cls, method)}
    missing = sorted(set(levels) - covered)
    assert not missing, f"form actions with no level-checked API write: {missing}"


def test_api_writes_below_the_forms_level_are_refused() -> None:
    from rest_framework.test import APIRequestFactory

    from syntegra.core import access, context
    from syntegra.core.api.permissions import RequiresContext
    from syntegra.core.context import CLASS_ORDER, Context
    from syntegra.core.errors import Forbidden

    factory = APIRequestFactory()
    checked = 0
    for route, method, cls in _api_writes():
        for p in _write_permissions(cls, method):
            needed = access.write_level(p)
            if not needed or needed == "public":
                continue
            below = CLASS_ORDER[CLASS_ORDER.index(needed) - 1]
            request = factory.generic(method, "/" + route)
            for clearance, refused in ((below, True), (needed, False)):
                ctx = Context(
                    tenant_id=uuid.uuid4(),
                    state_tenant_id=uuid.uuid4(),
                    actor_kind="user",
                    actor_id=uuid.uuid4(),
                    grant_id=uuid.uuid4(),
                    clearance=clearance,
                    permissions=frozenset({p}),
                )
                with context.use(ctx):
                    if refused:
                        with pytest.raises(Forbidden) as exc:
                            RequiresContext().has_permission(request, cls())
                        assert exc.value.code == "AUTH-LEVEL", (route, method)
                    else:
                        assert RequiresContext().has_permission(request, cls()), (route, method)
            checked += 1
    assert checked >= 60


@pytest.mark.django_db(databases="__all__")
def test_a_capped_grant_is_refused_on_the_form_and_the_api_alike(world: Any, client: Any) -> None:
    from django.test import Client

    from syntegra.core import context
    from syntegra.iam import services as iam

    officer, g = make_user(world, "STA", world.state_scope, "HR Officer")
    with context.use(system_ctx()):
        admin_ctx = user_ctx(world.admin.id, world.users["STA"][1])
    with context.use(admin_ctx):
        iam.set_grant_cap(admin_ctx, g, "confidential", "Acting HR officer only")
    # the web form …
    web = Client()
    web.post("/sign-in", {"username": officer.username, "password": PASSWORD})
    web.post("/auth/context?next=/", {"grant_id": str(g)})
    r = web.post("/forms/hr-integrity-scan", {})
    assert r.status_code == 403 and b"Level 4" in r.content
    # … and the same action through the API (a second account: one session per account)
    officer2, g2 = make_user(world, "STA", world.state_scope, "HR Officer 2")
    with context.use(admin_ctx):
        iam.set_grant_cap(admin_ctx, g2, "confidential", "Acting HR officer only")
    tok = api_sign_in(Client(), officer2.username, PASSWORD)
    api = Client(HTTP_AUTHORIZATION=f"Bearer {tok}")
    r = api.post("/api/v1/hr/integrity/scan", {}, content_type="application/json")
    assert r.status_code == 403 and r.json()["code"] == "AUTH-LEVEL" and "Level 4" in r.json()["detail"]
    # reading stays a matter for the services' own checks; restoring the level lets the write through
    with context.use(admin_ctx):
        iam.set_grant_cap(admin_ctx, g2, None, "Back to full duties")
    assert api.post("/api/v1/hr/integrity/scan", {}, content_type="application/json").status_code in (200, 201)
