"""CR-008 evidence-grade masters: write-once storage under object lock, searchable access copies beside the untouched
scan, and stamped releases entered in a register that can check a copy presented later (FR-DOC-301–305)."""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import re
from collections.abc import Iterator
from typing import Any

import pytest

from tests.conftest import make_user, system_ctx, user_ctx

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "correct-horse-battery"
BUCKET = "syntegra-test"


def _pdf(title: str, lines: list[str]) -> bytes:
    from syntegra.platform.demo.abia import _pdf as pdf

    return pdf(title, lines)


def _scan(lines: list[str]) -> bytes:
    """A PNG 'scan' at 200 dpi with no text layer, so that OCR has to read it."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("L", (1700, 120 + 110 * len(lines)), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=44)
    for i, line in enumerate(lines):
        draw.text((80, 60 + i * 110), line, fill=0, font=font)
    buf = io.BytesIO()
    img.save(buf, "PNG", dpi=(200, 200))
    return buf.getvalue()


def _text_of(pdf: bytes) -> str:
    from pypdf import PdfReader

    return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf)).pages)


def _sign_in(client: Any, user: Any) -> None:
    client.post("/sign-in", {"username": user.username, "password": PASSWORD})
    page = client.get("/auth/context?next=/").content.decode()
    grant = re.search(r'name="grant_id" value="([0-9a-f-]{36})"', page)
    assert grant, page[-1500:]
    client.post("/auth/context?next=/", {"grant_id": grant.group(1)})


def _upload(ctx: Any, institution: Any, name: str, data: bytes, cat: str = "ADM", title: str = "Register") -> Any:
    from syntegra.core import context
    from syntegra.records import services as rec

    with context.use(ctx):
        return rec.upload(
            ctx, institution_id=institution.id, category_code=cat, title=title, files=[rec.Upload(name, data)]
        )[0]


@pytest.fixture
def s3(settings: Any, monkeypatch: Any) -> Iterator[Any]:
    """An S3 bucket created with object lock (moto), as the default store."""
    import boto3
    from moto import mock_aws

    from syntegra.core import storage

    for k, val in {
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_DEFAULT_REGION": "us-east-1",
    }.items():
        monkeypatch.setenv(k, val)
    settings.SYNTEGRA_OBJECT_STORE = "s3"
    settings.SYNTEGRA_S3_BUCKET = BUCKET
    settings.SYNTEGRA_S3_ENDPOINT_URL = None
    storage._client.cache_clear()
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET, ObjectLockEnabledForBucket=True)
        yield client
    storage._client.cache_clear()


# --------------------------------------------------------------------------- write-once masters (FR-DOC-301)
def test_masters_are_written_once_under_compliance_lock(s3: Any) -> None:
    from botocore.exceptions import ClientError

    from syntegra.core import storage

    until = dt.date.today() + dt.timedelta(days=3650)
    data = b"%PDF-1.4 admission register 1987"
    first = storage.put(data, prefix="records/t", ext="pdf", retain_until=until, content_type="application/pdf")
    assert first.store == "s3" and first.created and first.lock_mode == "compliance" and first.retain_until == until
    status = storage.lock_status(first.key, "s3")
    assert status["mode"] == "compliance" and status["retain_until"] == until
    # the same bytes again: no second object, and the first is proved identical rather than overwritten
    again = storage.put(data, prefix="records/t", ext="pdf", retain_until=until)
    assert not again.created and again.key == first.key and again.lock_mode == "compliance"
    # a conditional write refuses to replace the object, whatever is sent
    with pytest.raises(ClientError):
        s3.put_object(Bucket=BUCKET, Key=first.key, Body=b"forged", IfNoneMatch="*")
    # nobody can delete the locked version, not even with the bypass header (compliance mode)
    version = status["version_id"]
    with pytest.raises(ClientError) as exc:
        s3.delete_object(Bucket=BUCKET, Key=first.key, VersionId=version, BypassGovernanceRetention=True)
    assert exc.value.response["Error"]["Code"] in ("AccessDenied", "InvalidRequest")
    assert storage.get(first.key, first.sha256, "s3") == data


def test_an_upload_records_where_its_master_is_kept_and_until_when(world: Any, s3: Any) -> None:
    from syntegra.records import evidence

    head, g = make_user(world, "HEAD", world.institution.scope_node_id)
    doc = _upload(user_ctx(head.id, g), world.institution, "adm.pdf", _pdf("ADMISSION REGISTER", ["1001 Ada"]))
    assert doc.master_store == "s3" and doc.master_lock_mode == "compliance"
    assert doc.master_retain_until == evidence.retain_until("ADM", doc.captured_at.date())
    head_obj = s3.head_object(Bucket=BUCKET, Key=doc.master_object_key)
    assert head_obj["ObjectLockMode"] == "COMPLIANCE"
    assert head_obj["ObjectLockRetainUntilDate"].date() == doc.master_retain_until


def test_retention_follows_the_file_plan() -> None:
    from syntegra.records import evidence
    from syntegra.records.services import CATEGORIES

    code, _t, _c, years = next(c for c in CATEGORIES if c[3] is not None)
    assert evidence.retain_until(code, dt.date(2024, 2, 29)) == dt.date(2024 + years, 2, 28 if years % 4 else 29)
    permanent = next(c[0] for c in CATEGORIES if c[3] is None)
    assert evidence.retain_until(permanent, dt.date(2026, 1, 1)).year == 2126


# --------------------------------------------------------------------------- searchable copy (FR-DOC-302)
def test_a_scan_gets_a_searchable_copy_and_the_master_is_untouched(world: Any, client: Any) -> None:
    from syntegra.core import context, storage
    from syntegra.records import evidence

    head, g = make_user(world, "HEAD", world.institution.scope_node_id)
    scan = _scan(["ADMISSION REGISTER 1987", "1001 Chukwuemeka Okafor born 1975"])
    doc = _upload(user_ctx(head.id, g), world.institution, "reg.png", scan)
    with context.use(system_ctx()):
        copy = evidence.searchable_copy(doc.id)
    assert copy is not None and copy.mime_type == "application/pdf" and copy.pages == 1
    assert bytes(copy.source_sha256) == bytes(doc.sha256) == hashlib.sha256(scan).digest()
    assert "Tesseract" in copy.generator or "tesseract" in copy.generator.lower()
    data = storage.get(copy.object_key, bytes(copy.sha256), copy.store)
    assert "Chukwuemeka Okafor" in _text_of(data)  # the words OCR read, selectable and searchable
    assert storage.get(doc.master_object_key, bytes(doc.sha256), doc.master_store) == scan  # master as captured

    _sign_in(client, head)
    page = client.get(f"/documents/{doc.id}").content.decode()
    assert 'id="evidence"' in page and copy.sha256.hex() in page and 'id="searchable-link"' in page
    r = client.get(f"/documents/{doc.id}/file?kind=searchable")
    assert r.status_code == 200 and r["Content-Type"] == "application/pdf"
    text = _text_of(r.content)
    assert "Chukwuemeka Okafor" in text and r["X-Syntegra-Release"] in text  # still searchable, and stamped


def test_a_pdf_with_its_own_text_needs_no_searchable_copy(world: Any) -> None:
    from syntegra.core import context
    from syntegra.records import evidence

    head, g = make_user(world, "HEAD", world.institution.scope_node_id)
    doc = _upload(user_ctx(head.id, g), world.institution, "a.pdf", _pdf("LOG BOOK", ["Visit by the inspector"]))
    with context.use(system_ctx()):
        assert evidence.searchable_copy(doc.id) is None


# --------------------------------------------------------------------------- stamped releases (FR-DOC-303/304)
def test_every_download_is_stamped_and_registered(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.records.models import DocumentRelease

    head, g = make_user(world, "HEAD", world.institution.scope_node_id, "Mrs Adaeze Nwosu")
    pdf = _pdf("ADMISSION REGISTER 1998", ["1001 Chidi Okafor born 1986"])
    doc = _upload(user_ctx(head.id, g), world.institution, "adm.pdf", pdf)
    _sign_in(client, head)
    one = client.get(f"/documents/{doc.id}/file")
    two = client.get(f"/documents/{doc.id}/file")
    code1, code2 = one["X-Syntegra-Release"], two["X-Syntegra-Release"]
    assert re.fullmatch(r"[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}", code1) and code1 != code2
    text = _text_of(one.content)
    assert "Chidi Okafor" in text and code1 in text and "Mrs Adaeze Nwosu" in text and doc.reference_no in text
    word = client.get(f"/documents/{doc.id}/word")
    assert word.status_code == 200 and re.search(
        r"-[A-Z2-9]{4}-[A-Z2-9]{4}-[A-Z2-9]{4}\.docx", word["Content-Disposition"]
    )
    with context.use(system_ctx()):
        rows = {r.release_code: r for r in DocumentRelease.objects.filter(document_id=doc.id)}
    assert set(rows) >= {code1, code2} and len(rows) == 3
    assert bytes(rows[code1].sha256) == hashlib.sha256(one.content).digest() and rows[code1].released_to == head.id
    assert {r.kind for r in rows.values()} == {"stamped_original", "word_copy"}
    assert rows[code1].reason == "Viewed on screen in Syntegra"  # shown in the viewer: stamped and registered too
    dl = client.get(f"/documents/{doc.id}/file?download=1")
    assert dl["Content-Disposition"].startswith("attachment") and "viewed on screen" not in _text_of(dl.content)


def test_the_register_checks_a_copy_presented_later(world: Any, client: Any) -> None:
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.test import Client

    head, g = make_user(world, "HEAD", world.institution.scope_node_id)
    pdf = _pdf("STAFF LIST", ["A. Teacher GL 08"])
    doc = _upload(user_ctx(head.id, g), world.institution, "s.pdf", pdf, cat="ADM")
    _sign_in(client, head)
    released = client.get(f"/documents/{doc.id}/file")
    code = released["X-Syntegra-Release"]
    # a head of school may download but not consult the register
    assert client.get("/records/releases").status_code == 403
    sta = Client()
    admin, _ag = make_user(world, "STA", world.state_scope, "State Records Officer")
    _sign_in(sta, admin)
    page = sta.get("/records/releases").content.decode()
    assert code in page and doc.reference_no in page
    r = sta.get(f"/records/releases?code={code.replace('-', '').lower()}")  # typed from paper, any case
    assert r.status_code == 200 and 'id="check-result"' in r.content.decode() and doc.reference_no in r.content.decode()

    def check(data: bytes) -> str:
        up = SimpleUploadedFile("copy.pdf", data, content_type="application/pdf")
        return sta.post("/records/releases", {"code": code, "file": up}).content.decode()

    assert 'id="match"' in check(released.content) and "Identical to the copy released" in check(released.content)
    assert 'id="mismatch"' in check(released.content.replace(b"Teacher", b"Tutor__"))
    assert "Identical to the master" in check(pdf)
    assert sta.get("/records/releases?code=AAAA-BBBB-CCCC").status_code == 404
    # the same through the API
    from tests.conftest import api_sign_in

    officer, _og = make_user(world, "STA", world.state_scope, "API Officer")  # one session per account
    tok = api_sign_in(Client(), officer.username, PASSWORD)
    api = Client(HTTP_AUTHORIZATION=f"Bearer {tok}")
    rows = api.get(f"/api/v1/records/releases?document={doc.id}").json()["results"]
    assert [x["code"] for x in rows] == [code]
    up = SimpleUploadedFile("copy.pdf", released.content, content_type="application/pdf")
    assert api.post(f"/api/v1/records/releases/{code}", {"file": up}).json()["presented_matches"] is True


def test_a_certified_true_copy_needs_the_permission_and_a_reason(world: Any, client: Any) -> None:
    from django.test import Client

    from syntegra.core import context
    from syntegra.records.models import DocumentRelease

    head, g = make_user(world, "HEAD", world.institution.scope_node_id)
    pdf = _pdf("ADMISSION REGISTER 1990", ["0901 Obinna Eze born 1978"])
    doc = _upload(user_ctx(head.id, g), world.institution, "a.pdf", pdf)
    _sign_in(client, head)
    assert 'id="certify"' not in client.get(f"/documents/{doc.id}").content.decode()
    assert client.post(f"/documents/{doc.id}/certified", {"reason": "Court order 12/2026"}).status_code == 403
    recm, _rg = make_user(world, "RECM", world.state_scope, "Records Manager")
    rc = Client()
    _sign_in(rc, recm)
    assert 'id="certify"' in rc.get(f"/documents/{doc.id}").content.decode()
    r = rc.post(f"/documents/{doc.id}/certified", {"reason": "court"})
    assert r.status_code == 422 and b"Give the reason" in r.content
    r = rc.post(f"/documents/{doc.id}/certified", {"reason": "High Court order FHC/ABJ/12/2026"})
    assert r.status_code == 200 and r.content == pdf and "certified" in r["Content-Disposition"]
    with context.use(system_ctx()):
        row = DocumentRelease.objects.get(release_code=r["X-Syntegra-Release"])
    assert row.kind == "certified_original" and row.reason == "High Court order FHC/ABJ/12/2026"
    assert bytes(row.sha256) == bytes(doc.sha256)
