"""Fixes from the code review of CR-007 (PR #1): sign-in, sessions, access levels, offices and documents."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tests.conftest import make_user, system_ctx, user_ctx

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "correct-horse-battery"


def _sign_in(client: Any, user: Any, nxt: str | None = None) -> Any:
    url = "/sign-in" + (f"?next={nxt}" if nxt else "")
    return client.post(url, {"username": user.username, "password": PASSWORD})


def _confirm(client: Any) -> Any:
    page = client.get("/auth/context?next=/").content.decode()
    grant = re.search(r'name="grant_id" value="([0-9a-f-]{36})"', page)
    assert grant, page[-1500:]
    return client.post("/auth/context?next=/", {"grant_id": grant.group(1)})


def _update_grant(grant_id: Any, **changes: Any) -> None:
    from syntegra.core import context
    from syntegra.iam.models import RoleGrant

    with context.use(system_ctx()):
        RoleGrant.objects.filter(pk=grant_id).update(**changes)


# --------------------------------------------------------------------------- sign-in and sessions
def test_return_address_after_sign_in_stays_on_this_site() -> None:
    from syntegra.web.views import _safe_next

    for bad in ("//evil.example", "/\\evil.example", "/\\/evil.example", "/\tevil", "https://evil.example", "", None):
        assert _safe_next(bad) == "/", bad
    assert _safe_next("/documents?q=x") == "/documents?q=x"


def test_sign_in_page_shows_the_level_after_an_administrators_cap(world: Any, client: Any) -> None:
    u, g = make_user(world, "HEAD", world.institution.scope_node_id)
    _update_grant(g, clearance_cap="internal")
    r = _sign_in(client, u)
    page = client.get(r["Location"]).content.decode()
    assert "Level 2" in page and "Level 4" not in page
    _confirm(client)
    me = client.get("/api/v1/me").json()
    assert me["grants"][0]["access_level"] == "internal" and me["access_level"]["number"] == 2


def test_a_role_that_ends_mid_session_sends_the_person_back_to_choose(world: Any, client: Any) -> None:
    import datetime as dt

    u, g = make_user(world, "HEAD", world.institution.scope_node_id)
    _sign_in(client, u)
    _confirm(client)
    assert client.get("/").status_code == 200
    today = dt.date.today()  # e.g. moved by a posting: the old grant ended yesterday
    _update_grant(g, status="inactive", valid_from=today - dt.timedelta(days=30), valid_to=today - dt.timedelta(days=1))
    r = client.get("/")
    assert r.status_code == 302 and r["Location"].startswith("/auth/context")
    page = client.get(r["Location"])
    assert page.status_code == 200 and b"You have no active roles" in page.content
    assert client.post("/sign-out").status_code == 302  # signing out still works
    assert _sign_in(client, u).status_code == 302  # and nobody is locked out by the stale session


def test_select_grant_refuses_a_role_out_of_date(world: Any, client: Any) -> None:
    import datetime as dt

    u, g = make_user(world, "HEAD", world.institution.scope_node_id)
    tok = client.post(
        "/api/v1/auth/sign-in", {"username": u.username, "password": PASSWORD}, content_type="application/json"
    ).json()["token"]
    today = dt.date.today()
    _update_grant(g, valid_from=today - dt.timedelta(days=30), valid_to=today - dt.timedelta(days=1))
    r = client.post(
        "/api/v1/auth/role", {"grant_id": str(g)}, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {tok}"
    )
    assert r.status_code == 403


def test_signing_in_again_from_the_same_browser_is_not_refused(world: Any, client: Any) -> None:
    from django.test import Client

    u, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    _sign_in(client, u)
    _confirm(client)
    # the same browser (its own cookie) signs in again: the old session is replaced, not "another device"
    assert _sign_in(client, u).status_code == 302
    _confirm(client)
    assert client.get("/").status_code == 200
    # another device is still refused while this one is in use
    assert _sign_in(Client(), u).status_code == 409


def test_a_sign_in_abandoned_before_confirmation_does_not_block(world: Any, client: Any) -> None:
    from django.test import Client

    u, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    assert _sign_in(client, u).status_code == 302  # stopped at the confirmation page
    other = Client()
    assert _sign_in(other, u).status_code == 302
    _confirm(other)
    assert other.get("/").status_code == 200


def test_api_clients_confirm_the_school_or_office_too(world: Any, client: Any) -> None:
    u, g = make_user(world, "HEAD", world.institution.scope_node_id)
    r = client.post(
        "/api/v1/auth/sign-in", {"username": u.username, "password": PASSWORD}, content_type="application/json"
    )
    assert r.json()["confirm_required"] is True
    auth = {"HTTP_AUTHORIZATION": f"Bearer {r.json()['token']}"}
    r = client.get("/api/v1/documents/categories", **auth)
    assert r.status_code == 403 and "auth/role" in r.content.decode()
    client.post("/api/v1/auth/role", {"grant_id": str(g)}, content_type="application/json", **auth)
    assert client.get("/api/v1/documents/categories", **auth).status_code == 200


# --------------------------------------------------------------------------- second factor (AUT-02)
def _enrol(user: Any) -> str:
    from syntegra.core import context
    from syntegra.iam import services as iam

    with context.use(system_ctx()):
        return iam.enrol_totp(user)


def test_authenticator_code_page_completes_the_web_sign_in(world: Any, client: Any) -> None:
    from syntegra.iam import services as iam

    u, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    seed = _enrol(u)
    r = _sign_in(client, u, "/documents")
    assert r.status_code == 302 and r["Location"].startswith("/auth/mfa")
    # nothing opens before the code — not even the confirmation page
    assert client.get("/").status_code == 302 and client.get("/")["Location"].startswith("/auth/mfa")
    assert client.get("/auth/context")["Location"].startswith("/auth/mfa")
    page = client.get(r["Location"])
    assert page.status_code == 200 and b'name="code"' in page.content
    bad = "000000" if iam.totp(seed) != "000000" else "111111"
    assert client.post(r["Location"], {"code": bad}).status_code == 401
    ok = client.post(r["Location"], {"code": iam.totp(seed)})
    assert ok.status_code == 302 and ok["Location"].startswith("/auth/context")
    assert "documents" in ok["Location"]
    _confirm(client)
    assert client.get("/").status_code == 200


def test_authenticator_codes_are_used_once_and_wrong_codes_lock_the_account(world: Any, client: Any) -> None:
    from syntegra.core.errors import DomainError
    from syntegra.iam import services as iam

    u, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    seed = _enrol(u)
    _sign_in(client, u)
    code = iam.totp(seed)
    assert client.post("/auth/mfa", {"code": code}).status_code == 302
    client.post("/sign-out")
    _sign_in(client, u)
    assert client.post("/auth/mfa", {"code": code}).status_code == 401  # the same code again: refused
    for _ in range(4):
        client.post("/auth/mfa", {"code": "999999" if code != "999999" else "888888"})
    r = client.post("/auth/mfa", {"code": iam.totp(seed, __import__("time").time() + 30)})
    assert r.status_code == 401 and b"locked" in r.content
    with pytest.raises(DomainError) as exc:
        iam.verify_mfa("not-a-session", code)
    assert exc.value.code == "AUTH-SESSION"


# --------------------------------------------------------------------------- access levels
def test_forms_need_the_access_level_of_their_page(world: Any, client: Any) -> None:
    u, g = make_user(world, "STA", world.state_scope)
    _sign_in(client, u)
    _confirm(client)
    assert client.get("/forms/funding-decide").status_code == 200
    _update_grant(g, clearance_cap="internal")
    r = client.get("/forms/funding-decide")
    assert r.status_code == 403 and b"needs Level 3" in r.content
    assert b"funding-decide" not in client.get("/forms").content
    assert client.post("/forms/funding-decide", {}).status_code == 403


def test_restoring_a_grant_cannot_lift_it_above_the_administrator(world: Any, as_user: Any) -> None:
    from syntegra.core.errors import Forbidden
    from syntegra.iam import services as iam

    _target, g = make_user(world, "PLAT", world.state_scope)  # role level 5, special
    _update_grant(g, clearance_cap="confidential")
    with as_user("STA", world.state_scope) as sta:  # level 4, restricted
        for cap in (None, "special"):
            with pytest.raises(Forbidden) as exc:
                iam.set_grant_cap(sta, g, cap, "restore the full level")
            assert exc.value.code == "ACCESS-ABOVE-OWN"
        iam.set_grant_cap(sta, g, "internal", "clerical duties only")  # lowering further is fine


def test_grant_search_and_holder_counts_run_over_every_grant(world: Any, as_user: Any) -> None:
    from syntegra.iam import services as iam

    names = [make_user(world, "TCH", world.institution.scope_node_id, f"Searchable{i}") for i in range(3)]
    with as_user("STA", world.state_scope) as sta:
        everything = iam.access_overview(sta, limit=1)
        assert len(everything["grants"]) == 1 and everything["total"] > 3  # one page, the full total
        tch = next(r for r in everything["roles"] if r["code"] == "TCH")
        assert tch["holders"] >= 3
        found = iam.access_overview(sta, q=names[2][0].username)
        assert [r["username"] for r in found["grants"]] == [names[2][0].username] and found["total"] == 1
        second = iam.access_overview(sta, q="searchable", offset=1, limit=1)
        assert second["total"] == 3 and len(second["grants"]) == 1


# --------------------------------------------------------------------------- offices shown at sign-in
def test_administrators_record_office_addresses_and_who_works_there(world: Any, client: Any) -> None:
    from django.test import Client

    from syntegra.core import context
    from syntegra.governance.models import ScopeNode

    official, g = make_user(world, "LGA", world.state_scope)  # state-wide scope, works in the LGA office
    admin, _ = make_user(world, "STA", world.state_scope)
    _sign_in(client, admin)
    _confirm(client)
    page = client.get("/admin/access-levels").content.decode()
    assert 'id="offices"' in page
    with context.use(system_ctx()):
        lga = ScopeNode.objects.get(pk=world.lga_scope)
    r = client.post(
        "/admin/access-levels",
        {
            "action": "address",
            "node_id": str(lga.id),
            "office": "Aba South Local Government Education Authority",
            "street": "12 Ehi Road",
            "town": "Aba",
            "lga": "Aba South",
            "state": "Abia",
            "reason": "office address confirmed",
        },
    )
    assert r.status_code == 200 and b"office address was saved" in r.content
    r = client.post(
        "/admin/access-levels",
        {"action": "office", "grant_id": str(g), "office_id": str(lga.id), "reason": "works at the LGA office"},
    )
    assert r.status_code == 200 and b"office was changed" in r.content
    other = Client()
    page = other.get(_sign_in(other, official)["Location"])
    text = page.content.decode()
    assert "Aba South Local Government Education Authority" in text and "12 Ehi Road, Aba" in text


def test_grant_role_records_the_office(world: Any) -> None:
    from syntegra.core import context
    from syntegra.iam import services as iam

    with context.use(system_ctx()):
        u = iam.create_user(system_ctx(), username="office.test@test.ng", display_name="Officer", password=PASSWORD)
        g = iam.grant_role(
            system_ctx(), user=u, role_code="LGA", scope_id=world.state_scope, office_scope_id=world.lga_scope
        )
        assert g.office_scope_id == world.lga_scope
        assert iam.user_grants(u)[0]["affiliation"]["scope_id"] == str(world.lga_scope)


# --------------------------------------------------------------------------- documents
def _upload(ctx: Any, inst: Any, data: bytes, category: str = "STF", **kw: Any) -> Any:
    from syntegra.core import context
    from syntegra.records import services as rec

    with context.use(ctx):
        return rec.upload(
            ctx,
            institution_id=inst.id,
            category_code=category,
            title=kw.pop("title", "Staff file"),
            files=[rec.Upload("f.txt", data)],
            **kw,
        )[0]


def _sta(world: Any) -> Any:
    u, g = make_user(world, "STA", world.state_scope)
    return user_ctx(u.id, g)


def test_duplicate_message_does_not_reveal_documents_the_uploader_cannot_open(world: Any) -> None:
    from syntegra.core import context
    from syntegra.core.errors import HardValidation

    _upload(_sta(world), world.institution2, b"Staff file of Mr Okon, disciplinary hearing 2019.", title="Okon file")
    u, g = make_user(world, "HEAD", world.institution.scope_node_id)
    head = user_ctx(u.id, g)
    with context.use(head), pytest.raises(HardValidation) as exc:
        _upload(head, world.institution, b"Staff file of Mr Okon, disciplinary hearing 2019.")
    assert "Okon file" not in exc.value.detail and "/STF/" not in exc.value.detail
    assert "already stored" in exc.value.detail


def test_a_taken_reference_number_is_skipped(world: Any, monkeypatch: Any) -> None:
    from syntegra.records import services as rec

    sta = _sta(world)
    first = _upload(sta, world.institution, b"Minutes of the PTA, March.", category="MIN", title="PTA minutes")
    real = rec._next_reference
    calls: list[str] = []

    def stale(alias: str, tenant_id: Any, prefix: str) -> str:  # another upload read the same last number
        calls.append(prefix)
        return str(first.reference_no) if len(calls) == 1 else real(alias, tenant_id, prefix)

    monkeypatch.setattr(rec, "_next_reference", stale)
    second = _upload(sta, world.institution, b"Minutes of the PTA, April.", category="MIN", title="PTA minutes 2")
    assert len(calls) == 2 and second.reference_no != first.reference_no
    assert int(second.reference_no.rsplit("/", 1)[1]) == int(first.reference_no.rsplit("/", 1)[1]) + 1


def test_restricted_documents_are_listed_only_for_a_declared_purpose(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.records import services as rec

    sta = _sta(world)
    _upload(sta, world.institution, b"Staff file of Mrs Eze.", title="Eze staff file")
    _upload(sta, world.institution, b"Admission register page.", category="ADM", title="Admission register")
    with context.use(sta):
        reg = rec.register(sta, world.institution.id)
        titles = {r["title"] for _, rows in reg["groups"] for r in rows}
        assert "Admission register" in titles and "Eze staff file" not in titles
        assert reg["restricted_hidden"] == 1 and reg["restricted_left_out"]
        reg = rec.register(sta, world.institution.id, purpose="records_retrieval")
        titles = {r["title"] for _, rows in reg["groups"] for r in rows}
        assert "Eze staff file" in titles and reg["restricted_hidden"] == 0
        found = rec.search(sta, institution_id=world.institution.id, category_code="STF")
        assert found["total"] == 0 and found["restricted_left_out"]
        found = rec.search(sta, institution_id=world.institution.id, category_code="STF", purpose="records_retrieval")
        assert found["total"] == 1
    u, _g = make_user(world, "STA", world.state_scope)
    _sign_in(client, u)
    _confirm(client)
    page = client.get(f"/institutions/{world.institution.id}/documents").content.decode()
    assert 'id="restricted-note"' in page and "Eze staff file" not in page and 'id="purpose"' in page
    page = client.get(f"/institutions/{world.institution.id}/documents?purpose=records_retrieval").content.decode()
    assert "Eze staff file" in page and "purpose=records_retrieval" in page


def test_object_store_never_keeps_a_partial_object(settings: Any, tmp_path: Any, monkeypatch: Any) -> None:
    import hashlib
    import os

    from syntegra.core import storage

    settings.SYNTEGRA_OBJECT_STORE_DIR = tmp_path
    data = b"%PDF-1.4 scanned admission register" * 100
    hexd = hashlib.sha256(data).hexdigest()
    path = tmp_path / "records" / hexd[:2] / f"{hexd}.pdf"

    def full_disk(fd: int) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(os, "fsync", full_disk)
    with pytest.raises(OSError, match="No space left"):
        storage.put(data, prefix="records", ext="pdf")
    assert not path.exists() and not list(path.parent.glob(".incoming-*"))  # nothing half-written is left
    monkeypatch.undo()
    s = storage.put(data, prefix="records", ext="pdf")
    assert s.created and storage.get(s.key, s.sha256) == data
    assert not storage.put(data, prefix="records", ext="pdf").created  # stored once
    # an object damaged by an older interrupted write is repaired by the next upload of the same scan
    os.chmod(path, 0o640)
    path.write_bytes(data[:10])
    with pytest.raises(storage.IntegrityFailure):
        storage.get(s.key, s.sha256)
    assert storage.put(data, prefix="records", ext="pdf").created
    assert storage.get(s.key, s.sha256) == data
