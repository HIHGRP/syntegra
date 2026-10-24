"""The coat of arms of Abia State on sign-in, in the header, on the registration pages and against the state's
education bodies (static/img/emblems/NG-AB.png)."""

from __future__ import annotations

from typing import Any

import pytest

from tests.integration.test_cr006_web import _ok, _sign_in

pytestmark = pytest.mark.django_db(databases="__all__")


def test_coat_of_arms_on_official_pages(world: Any, client: Any) -> None:
    page = _ok(client.get("/sign-in"))
    assert 'class="sign-in-emblem"' in page and "/static/img/emblems/NG-AB.png" in page
    assert 'alt="Coat of arms of Abia State"' in page

    from syntegra.core import context
    from syntegra.platform.demo import abia

    with context.use(abia._sys()):
        state = abia._node(abia.STATE)
        abia._user("registrar.ministry@abia.gov.ng", "Schools registrar, Ministry of Education", "STA", state.id,
                   abia.Loaded(), "Abia State")  # fmt: skip
        abia._user("admissions.ministry@abia.gov.ng", "Admissions officer", "REG", state.id, abia.Loaded(),
                   "Abia State")  # fmt: skip
    _sign_in(client, "registrar.ministry@abia.gov.ng")
    form = _ok(client.get("/forms/institution-register"))
    assert 'id="state-heading"' in form and "Abia State Government" in form
    assert "Abia State Ministry of Education" in form
    other = _ok(client.get("/forms"))
    assert 'id="state-heading"' not in other  # only the registration pages carry the official heading
    _sign_in(client, "admissions.ministry@abia.gov.ng")
    learner = _ok(client.get("/learners/new"))
    assert 'id="state-heading"' in learner and 'class="emblem"' in learner


def test_no_emblem_for_a_state_without_one() -> None:
    from types import SimpleNamespace

    from syntegra.web.jinja import state_emblem

    assert state_emblem(SimpleNamespace(state_code="NG-AB")) == "/static/img/emblems/NG-AB.png"
    assert state_emblem(SimpleNamespace(state_code="NG-ZZ")) is None
    assert state_emblem(None) is None and state_emblem(SimpleNamespace(state_code=None)) is None
