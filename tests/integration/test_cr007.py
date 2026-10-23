"""CR-007: the school or office at sign-in, one session per account, administrators' sessions and access levels, and
document management for digitised paper records."""

from __future__ import annotations

import datetime as dt
import io
import re
import zipfile
from typing import Any

import pytest

from tests.conftest import make_user, system_ctx, user_ctx

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "correct-horse-battery"


def _pdf(title: str, lines: list[str]) -> bytes:
    from syntegra.platform.demo.abia import _pdf as pdf

    return pdf(title, lines)


def _sign_in(client: Any, user: Any) -> Any:
    return client.post("/sign-in", {"username": user.username, "password": PASSWORD})


def _confirm(client: Any) -> Any:
    page = client.get("/auth/context?next=/").content.decode()
    grant = re.search(r'name="grant_id" value="([0-9a-f-]{36})"', page)
    assert grant, page[-1500:]
    return client.post("/auth/context?next=/", {"grant_id": grant.group(1)})


def _session(user: Any) -> Any:
    from syntegra.core import context
    from syntegra.iam.models import UserSession

    with context.use(system_ctx()):
        return UserSession.objects.filter(user_id=user.id, revoked_at__isnull=True).order_by("-started_at").first()


# --------------------------------------------------------------------------- sign-in identity (FR-AUT-101)
def test_sign_in_shows_and_records_the_school_and_its_address(world: Any, client: Any) -> None:
    u, _g = make_user(world, "HEAD", world.institution.scope_node_id, "Principal")
    r = _sign_in(client, u)
    assert r.status_code == 302 and r["Location"].startswith("/auth/context")
    page = client.get(r["Location"]).content.decode()
    assert "Government Secondary School Aba" in page and "Aba, Aba South LGA" in page and "Level 4" in page
    # nothing else opens until the school is confirmed
    assert client.get("/").status_code == 302 and client.get("/")["Location"].startswith("/auth/context")
    assert _confirm(client).status_code == 302
    home = client.get("/").content.decode()
    assert 'id="affiliation-bar"' in home and "Government Secondary School Aba" in home and "Aba South LGA" in home
    s = _session(u)
    assert s.affiliation_name == "Government Secondary School Aba" and s.affiliation_confirmed_at is not None
    assert "Aba South LGA" in s.affiliation_address
    me = client.get("/api/v1/me").json()
    assert me["affiliation"]["name"] == "Government Secondary School Aba" and me["access_level"]["number"] == 4


def test_api_sign_in_returns_each_grants_school_or_office(world: Any, client: Any) -> None:
    u, g = make_user(world, "HEAD", world.institution.scope_node_id)
    r = client.post(
        "/api/v1/auth/sign-in", {"username": u.username, "password": PASSWORD}, content_type="application/json"
    )
    assert r.status_code == 201
    grant = r.json()["grants"][0]
    assert grant["affiliation"]["name"] == "Government Secondary School Aba" and grant["access_level"] == "restricted"
    tok = r.json()["token"]
    r = client.post(
        "/api/v1/auth/role", {"grant_id": str(g)}, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {tok}"
    )
    assert r.status_code == 200 and r.json()["affiliation"]["address"].startswith("Aba")


def test_wrong_password_reveals_nothing_about_the_school(world: Any, client: Any) -> None:
    u, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    r = client.post("/sign-in", {"username": u.username, "password": "wrong-password-123"})
    assert r.status_code == 401 and b"Government Secondary School Aba" not in r.content


# --------------------------------------------------------------------------- one session per account (FR-AUT-102)
def test_one_account_cannot_be_used_by_two_people_at_once(world: Any, client: Any) -> None:
    from django.test import Client

    from syntegra.core import context
    from syntegra.iam.models import UserSession

    u, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    _sign_in(client, u)
    _confirm(client)
    other = Client()
    r = _sign_in(other, u)
    assert r.status_code == 409 and b"already signed in on another device" in r.content
    r = other.post(
        "/api/v1/auth/sign-in", {"username": u.username, "password": PASSWORD}, content_type="application/json"
    )
    assert r.status_code == 409 and r.json()["code"] == "AUTH-SESSION-IN-USE"
    # the person using the account is told
    assert b'id="refused-banner"' in client.get("/").content
    # a session that has gone quiet is ended by the next sign-in — nobody is locked out for good
    with context.use(system_ctx()):
        s = UserSession.objects.get(pk=_session(u).id)
        UserSession.objects.filter(pk=s.id).update(last_seen_at=s.last_seen_at - dt.timedelta(minutes=20))
    assert _sign_in(other, u).status_code == 302
    r = client.get("/")
    assert r.status_code == 302 and "ended=replaced" in r["Location"]
    assert b"signed in on another device" in client.get(r["Location"]).content
    with context.use(system_ctx()):
        assert UserSession.objects.get(pk=s.id).ended_reason == "replaced"


def test_sign_out_frees_the_account_immediately(world: Any, client: Any) -> None:
    from django.test import Client

    u, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    _sign_in(client, u)
    _confirm(client)
    client.post("/sign-out")
    assert _sign_in(Client(), u).status_code == 302


def test_administrator_sees_and_ends_sessions_in_scope(world: Any, client: Any) -> None:
    from django.test import Client

    head, _g = make_user(world, "HEAD", world.institution.scope_node_id, "Head Teacher")
    hc = Client()
    _sign_in(hc, head)
    _confirm(hc)
    sta, _g2 = make_user(world, "STA", world.state_scope, "State Admin")
    _sign_in(client, sta)
    _confirm(client)
    page = client.get("/admin/sessions").content.decode()
    assert "Head Teacher" in page and "Government Secondary School Aba" in page and "in use" in page
    api = client.get("/api/v1/auth/sessions").json()
    sid = next(r["session_id"] for r in api["results"] if r["username"] == head.username)
    assert client.post("/admin/sessions", {"session_id": sid, "reason": "x"}).status_code == 422  # reason required
    r = client.post("/admin/sessions", {"session_id": sid, "reason": "Account shared between two staff"})
    assert r.status_code == 200 and b"The session was ended" in r.content
    r = hc.get("/")
    assert r.status_code == 302 and "ended=ended_by_administrator" in r["Location"]
    # a head cannot see the sessions page
    other, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    c3 = Client()
    _sign_in(c3, other)
    _confirm(c3)
    assert c3.get("/admin/sessions").status_code == 403


# --------------------------------------------------------------------------- access levels (FR-ADM-201/202)
def test_access_levels_are_listed_lowered_and_enforced(world: Any, client: Any) -> None:
    from django.test import Client

    head, g = make_user(world, "HEAD", world.institution.scope_node_id, "Capped Head")
    sta, _ = make_user(world, "STA", world.state_scope, "Access Admin")
    _sign_in(client, sta)
    _confirm(client)
    page = client.get("/admin/access-levels?q=Capped").content.decode()
    for label in ("Level 1 · Public", "Level 2 · Internal", "Level 3 · Confidential", "Level 4 · Restricted"):
        assert label in page
    assert "Capped Head" in page
    # cannot raise above the role's level, cannot change one's own role
    r = client.post("/admin/access-levels", {"grant_id": str(g), "cap": "special", "reason": "testing raise"})
    assert r.status_code in (403, 422)
    own = next(x for x in client.get("/api/v1/access/levels").json()["grants"] if x["username"] == sta.username)
    assert (
        client.post(
            "/admin/access-levels", {"grant_id": own["grant_id"], "cap": "internal", "reason": "my own role"}
        ).status_code
        == 403
    )
    r = client.post("/admin/access-levels", {"grant_id": str(g), "cap": "internal", "reason": "Clerical duties only"})
    assert r.status_code == 200 and b"The access level was changed" in r.content
    # the head now works at Level 2: documents (confidential) are refused and leave the menu
    hc = Client()
    _sign_in(hc, head)
    _confirm(hc)
    home = hc.get("/").content.decode()
    assert "Level 2 · Internal" in home and 'href="/documents"' not in home
    r = hc.get(f"/institutions/{world.institution.id}/documents")
    assert r.status_code == 403 and b"Level 3" in r.content
    # restoring the role's level through the API
    r = client.put(
        f"/api/v1/access/grants/{g}/level",
        {"level": "restricted", "reason": "Back to full duties"},
        content_type="application/json",
    )
    assert r.status_code == 204
    assert hc.get(f"/institutions/{world.institution.id}/documents").status_code == 200


# --------------------------------------------------------------------------- documents (FR-DOC-201–206)
def _upload(client: Any, institution: Any, cat: str, title: str, pdf: bytes, **extra: str) -> Any:
    from django.core.files.uploadedfile import SimpleUploadedFile

    data = {"institution": str(institution.id), "category": cat, "title": title, "date_from": "1998-09-14", **extra}
    data["files"] = [SimpleUploadedFile(f"{cat}.pdf", pdf, content_type="application/pdf")]
    return client.post("/documents/upload", data)


def test_documents_are_filed_under_the_school_with_references_and_a_word_copy(world: Any, client: Any) -> None:
    head, _g = make_user(world, "HEAD", world.institution.scope_node_id, "Records Head")
    _sign_in(client, head)
    _confirm(client)
    assert 'href="/documents"' in client.get("/").content.decode()  # Documents is in the main menu
    pdf = _pdf("ADMISSION REGISTER 1998", ["1001 Chidi Okafor born 1986", "1002 Ada Nwosu born 1986"])
    r = _upload(client, world.institution, "ADM", "Admission register 1998", pdf, transcription="Okafor Nwosu")
    assert r.status_code == 302 and f"/institutions/{world.institution.id}/documents" in r["Location"]
    reg = client.get(r["Location"]).content.decode()
    ref = re.search(r"(INS-[A-Z]{2}-\d{6}/ADM/1998/00001)", reg)
    assert ref and "Admission registers" in reg and 'class="row-new"' in reg
    # the same scan is stored once
    r = _upload(client, world.institution, "ADM", "Admission register again", pdf)
    assert r.status_code == 422 and b"already stored as" in r.content
    # a second document of the same kind and year gets the next number
    r = _upload(client, world.institution, "ADM", "Admission register 1998 vol 2", _pdf("VOL 2", ["1003 Emeka Obi"]))
    assert r.status_code == 302
    assert ref.group(1)[:-5] + "00002" in client.get(r["Location"]).content.decode()
    # find by reference number (no full-text needed) and open it
    found = client.get(f"/documents?institution={world.institution.id}&q={ref.group(1)}").content.decode()
    doc_id = re.search(r'href="/documents/([0-9a-f-]{36})"', found).group(1)  # type: ignore[union-attr]
    page = client.get(f"/documents/{doc_id}").content.decode()
    assert "Government Secondary School Aba" in page and "watermark-overlay" in page
    assert "from the PDF&#39;s text layer" in page
    # the download is a stamped copy entered in the release register (CR-008); the master is never served as is
    scan = client.get(f"/documents/{doc_id}/file")
    assert scan.status_code == 200 and scan["Content-Type"] == "application/pdf"
    assert scan.content.startswith(b"%PDF") and scan.content != pdf and scan["X-Syntegra-Release"]
    word = client.get(f"/documents/{doc_id}/word")
    assert word.status_code == 200 and word["Content-Disposition"].endswith('.docx"')
    xml = zipfile.ZipFile(io.BytesIO(word.content)).read("word/document.xml").decode()
    assert "Chidi Okafor" in xml and ref.group(1) in xml and "Government Secondary School Aba" in xml
    # the same through the API
    api = client.get(f"/api/v1/institutions/{world.institution.id}/documents").json()
    assert api["total"] == 2 and api["groups"][0]["category"] == "Admission registers"
    assert client.get(f"/api/v1/documents/{doc_id}").json()["reference_no"] == ref.group(1)


def test_document_access_follows_scope_level_and_purpose(world: Any, client: Any) -> None:
    from django.test import Client

    from syntegra.core import context
    from syntegra.records import services as rec

    head, g = make_user(world, "HEAD", world.institution.scope_node_id, "Head A")
    with context.use(user_ctx(head.id, g)):
        ctx = user_ctx(head.id, g)
        staff = rec.upload(
            ctx,
            institution_id=world.institution.id,
            category_code="STF",
            title="Staff nominal roll 2024",
            files=[rec.Upload("stf.pdf", _pdf("NOMINAL ROLL", ["1. A. Teacher GL 08"]))],
        )[0]
    assert staff.classification == "restricted" and staff.reference_no.endswith(
        "/STF/" + str(dt.date.today().year) + "/00001"
    )
    _sign_in(client, head)
    _confirm(client)
    r = client.get(f"/documents/{staff.id}")
    assert r.status_code == 428 and b"Why do you need this document" in r.content  # restricted: purpose first
    r = client.get(f"/documents/{staff.id}?purpose=records_retrieval")
    assert r.status_code == 200 and b"Staff nominal roll 2024" in r.content
    assert client.get(f"/api/v1/documents/{staff.id}").status_code == 428
    r = client.get(f"/api/v1/documents/{staff.id}", HTTP_X_SYNTEGRA_PURPOSE="records_retrieval")
    assert r.status_code == 200
    # a head of another school sees nothing of it, and cannot search across schools
    other, _ = make_user(world, "HEAD", world.institution2.scope_node_id, "Head B")
    c2 = Client()
    _sign_in(c2, other)
    _confirm(c2)
    assert c2.get(f"/documents/{staff.id}?purpose=records_retrieval").status_code == 404
    assert c2.get(f"/institutions/{world.institution.id}/documents").status_code == 403
    assert c2.get("/api/v1/documents?q=nominal").status_code == 403
    # a stored file that no longer matches its hash is withheld
    from pathlib import Path

    from django.conf import settings

    path = Path(settings.SYNTEGRA_OBJECT_STORE_DIR) / staff.master_object_key
    path.chmod(0o640)
    path.write_bytes(b"%PDF-1.4 tampered")
    r = client.get(f"/documents/{staff.id}/file?purpose=records_retrieval")
    assert r.status_code == 500 and b"integrity" in r.content.lower()


def test_uploads_are_checked(world: Any, client: Any) -> None:
    from django.core.files.uploadedfile import SimpleUploadedFile

    head, _g = make_user(world, "HEAD", world.institution.scope_node_id)
    _sign_in(client, head)
    _confirm(client)
    r = client.post(
        "/documents/upload",
        {
            "institution": str(world.institution.id),
            "category": "ADM",
            "title": "Not a scan",
            "files": [SimpleUploadedFile("x.pdf", b"MZ\x90\x00 executable", content_type="application/pdf")],
        },
    )
    assert r.status_code == 422 and b"Not a PDF, JPEG, PNG, TIFF or text file" in r.content
    r = _upload(client, world.institution2, "ADM", "Someone else's school", _pdf("X", ["y"]))
    assert r.status_code == 422 or r.status_code == 403
    r = _upload(client, world.institution, "ADM", "Lowered", _pdf("Z", ["z"]), classification="internal")
    assert r.status_code == 422 and b"can be raised, not lowered" in r.content
