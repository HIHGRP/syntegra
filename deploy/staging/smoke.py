"""Staging smoke test (CR-008): the production image, used as a person and an API client would, against MySQL over TLS,
object storage with compliance lock and the identity provider. Each step prints what it proved; any failure stops it.

TLS is ended in front of the application in production (the gateway sets X-Forwarded-Proto); this client plays that
part, so the production settings (HTTPS redirects, secure cookies, HSTS) run unchanged.
"""

# ruff: noqa: PT018, S603 — a script whose asserts are its checks; it runs this repository's manage.py

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import io
import json
import os
import re
import secrets
import struct
import subprocess
import sys
import time
import uuid
from http.client import HTTPConnection, HTTPResponse
from typing import Any
from urllib.parse import urlencode, urljoin, urlsplit

WEB = os.environ.get("STAGING_WEB", "http://web:8000")
ADMIN = os.environ.get("STAGING_ADMIN", "admin@abia.gov.ng")
ADMIN_PASSWORD = os.environ.get("SYNTEGRA_BOOTSTRAP_PASSWORD", "")
IDP_ISSUER = os.environ.get("STAGING_IDP_ISSUER", "http://idp:8080/realms/abia")
SSO_USER, SSO_PASSWORD = "sso.officer", "Staging-idp-password-2026"  # the staging realm's test user
TAG = "".join(secrets.choice("ACEFHKMNPRTWXY") for _ in range(6))  # letters OCR cannot confuse with digits


def ok(msg: str) -> None:
    print(f"  ✓ {msg}", flush=True)


class Response:
    def __init__(self, r: HTTPResponse) -> None:
        self.status = r.status
        self.headers = r.headers
        self.body = r.read()

    def json(self) -> Any:
        return json.loads(self.body)

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class Browser:
    """Cookies per host (Secure honoured by the gateway, not here), no automatic redirects."""

    def __init__(self) -> None:
        self.cookies: dict[str, dict[str, str]] = {}

    def request(
        self, method: str, url: str, body: bytes | None = None, headers: dict[str, str] | None = None
    ) -> Response:
        if url.startswith("https://web:8000"):  # the gateway: TLS ends here, the app is told so
            url = "http://web:8000" + url[len("https://web:8000") :]
        parts = urlsplit(url)
        host = parts.hostname or ""
        h = {"Host": parts.netloc, **(headers or {})}
        if parts.netloc == urlsplit(WEB).netloc:
            h.setdefault("X-Forwarded-Proto", "https")
        jar = self.cookies.setdefault(host, {})
        if jar:
            h["Cookie"] = "; ".join(f"{k}={v}" for k, v in jar.items())
        conn = HTTPConnection(parts.hostname, parts.port or 80, timeout=60)
        conn.request(method, parts.path + (f"?{parts.query}" if parts.query else ""), body=body, headers=h)
        r = Response(conn.getresponse())
        for raw in r.headers.get_all("Set-Cookie") or []:
            name, _, rest = raw.partition("=")
            value = rest.split(";", 1)[0]
            if "max-age=0" in raw.lower() or "expires=thu, 01 jan 1970" in raw.lower():
                jar.pop(name.strip(), None)
            else:
                jar[name.strip()] = value
        conn.close()
        return r

    def get(self, url: str, **kw: Any) -> Response:
        return self.request("GET", url, **kw)


def api(token: str | None = None, extra: dict[str, str] | None = None) -> dict[str, str]:
    h = {"Accept": "application/json", "X-Forwarded-Proto": "https"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return {**h, **(extra or {})}


def post_json(b: Browser, path: str, data: Any, token: str | None = None) -> Response:
    return b.request("POST", WEB + path, json.dumps(data).encode(), {**api(token), "Content-Type": "application/json"})


def multipart(fields: dict[str, str], files: list[tuple[str, str, bytes, str]]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    out = io.BytesIO()
    for k, v in fields.items():
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for field, name, data, mime in files:
        out.write(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n".encode()
        )
        out.write(data + b"\r\n")
    out.write(f"--{boundary}--\r\n".encode())
    return out.getvalue(), f"multipart/form-data; boundary={boundary}"


def totp(seed: str, at: float | None = None) -> str:
    key = base64.b32decode(seed + "=" * (-len(seed) % 8), casefold=True)
    counter = int((at or time.time()) // 30)
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    off = mac[-1] & 0x0F
    return str((struct.unpack(">I", mac[off : off + 4])[0] & 0x7FFFFFFF) % 1_000_000).zfill(6)


def scan(lines: list[str]) -> bytes:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("L", (1700, 120 + 110 * len(lines)), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=44)
    for i, line in enumerate(lines):
        draw.text((80, 60 + i * 110), line, fill=0, font=font)
    buf = io.BytesIO()
    img.save(buf, "PNG", dpi=(200, 200))
    return buf.getvalue()


def pdf_text(data: bytes) -> str:
    from pypdf import PdfReader

    return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)


def wait_for(url: str, what: str, seconds: int = 240) -> None:
    deadline = time.time() + seconds
    while True:
        try:
            if Browser().get(url).status < 500:
                ok(f"{what} is up")
                return
        except OSError:
            pass
        if time.time() > deadline:
            sys.exit(f"{what} did not come up at {url}")
        time.sleep(3)


def main() -> None:
    b = Browser()
    print("Staging rehearsal", TAG)
    wait_for(f"{WEB}/healthz", "the application")
    wait_for(f"{IDP_ISSUER}/.well-known/openid-configuration", "the identity provider")
    r = b.get(f"{WEB}/healthz", headers={"X-Forwarded-Proto": "http"})
    assert r.status == 301 and r.headers["Location"].startswith("https://"), (r.status, r.headers)
    ok("plain http is redirected to https (production settings in force)")

    # ---------------------------------------------------------------- sign-in with the second factor enforced
    r = post_json(b, "/api/v1/auth/sign-in", {"username": ADMIN, "password": ADMIN_PASSWORD})
    assert r.status == 201, r.text
    signed = r.json()
    token, grant = signed["token"], signed["grants"][0]["grant_id"]
    assert signed["mfa_setup_required"] is True, signed
    r = b.get(f"{WEB}/api/v1/documents/categories", headers=api(token))
    assert r.status == 403 and "/api/v1/me/mfa/totp" in r.text, r.text
    ok("the state administrator must set up an authenticator before any data opens")
    r = post_json(b, "/api/v1/me/mfa/totp", {}, token)
    assert r.status == 201, r.text
    enrol = r.json()
    r = post_json(b, f"/api/v1/me/mfa/totp/{enrol['factor_id']}/confirm", {"code": totp(enrol["secret"])}, token)
    assert r.status == 200 and len(r.json()["recovery_codes"]) == 10, r.text
    ok("authenticator enrolled with its first code; ten recovery codes issued")
    assert post_json(b, "/api/v1/auth/role", {"grant_id": grant}, token).status == 200
    ok("school or office confirmed; the role applies")

    # ---------------------------------------------------------------- documents: OCR, search, lock, releases
    seed = subprocess.run(
        [sys.executable, "manage.py", "syntegra_staging_seed"], check=True, capture_output=True, text=True
    )
    fixtures = json.loads(seed.stdout.strip().splitlines()[-1])
    words = ["ADMISSION REGISTER 1987", f"1001 Chukwuemeka Okafor {TAG}", "1002 Ngozi Eze born 1976"]
    body, ctype = multipart(
        {"institution_id": fixtures["institution_id"], "category": "ADM", "title": f"Admission register {TAG}"},
        [("files", "register.png", scan(words), "image/png")],
    )
    r = b.request("POST", f"{WEB}/api/v1/documents", body, {**api(token), "Content-Type": ctype})
    assert r.status == 201, r.text
    doc = r.json()["documents"][0]
    ok(f"scan uploaded: {doc['reference_no']}")
    detail = b.get(f"{WEB}/api/v1/documents/{doc['id']}", headers=api(token)).json()
    assert detail["master"]["store"] == "s3" and detail["master"]["lock_mode"] == "compliance", detail["master"]
    assert detail["searchable"], detail
    ok(f"master in object storage under compliance lock until {detail['master']['retain_until']}")
    hits = b.get(f"{WEB}/api/v1/documents?q={TAG}", headers=api(token)).json()
    assert [h["id"] for h in hits["rows"]] == [doc["id"]], hits
    ok("found by full-text search on a word OCR read from the scan")
    r = b.get(f"{WEB}/api/v1/documents/{doc['id']}/content", headers=api(token))
    code = r.headers["X-Syntegra-Release"]
    assert r.status == 200 and code in pdf_text(r.body), r.status
    stamped = r.body
    ok(f"download is a stamped copy carrying release code {code}")
    r = b.get(f"{WEB}/api/v1/documents/{doc['id']}/content?kind=searchable", headers=api(token))
    assert r.status == 200 and f"Okafor {TAG}" in pdf_text(r.body).replace("\n", " "), pdf_text(r.body)[:400]
    ok("searchable copy: the OCR words are selectable over the page image")
    altered = bytearray(stamped)
    altered[len(altered) // 2] ^= 0x01  # one bit changed anywhere is a different copy
    for data, field in ((stamped, "presented_matches"), (bytes(altered), None)):
        body, ctype = multipart({}, [("file", "copy.pdf", data, "application/pdf")])
        result = b.request(
            "POST", f"{WEB}/api/v1/records/releases/{code}", body, {**api(token), "Content-Type": ctype}
        ).json()
        assert result["presented_matches"] is (field is not None), result
    ok("the release register tells the released copy from an altered one")

    # ---------------------------------------------------------------- the store refuses changes (WORM)
    from botocore.exceptions import ClientError

    sys.path.insert(0, "/staging")
    import objects

    s3 = objects.s3()
    keys = [o["Key"] for o in s3.list_objects_v2(Bucket=objects.BUCKET, Prefix="records/").get("Contents", [])]
    assert keys, "no objects stored"
    for key in keys:
        head = s3.head_object(Bucket=objects.BUCKET, Key=key)
        assert head["ObjectLockMode"] == "COMPLIANCE", head
        for attempt in (
            lambda k=key: s3.put_object(Bucket=objects.BUCKET, Key=k, Body=b"forged"),
            lambda k=key, v=head["VersionId"]: s3.delete_object(Bucket=objects.BUCKET, Key=k, VersionId=v),
        ):
            try:
                attempt()
            except ClientError:
                continue
            raise AssertionError(f"the store allowed a change to {key}")
    ok(f"{len(keys)} stored objects: overwrite and delete refused by the store itself")

    # ---------------------------------------------------------------- single sign-on with the state's provider
    r = post_json(
        b,
        "/api/v1/admin/sign-in-providers",
        {
            "provider": "gov_sso",
            "label": "Sign in with Abia Government ID",
            "issuer": IDP_ISSUER,
            "client_id": "syntegra-staging",
            "client_secret": "staging-client-secret",
            "allowed_domains": ["abiastate.gov.ng"],
        },
        token,
    )
    assert r.status == 201, r.text
    provider = r.json()
    r = post_json(b, f"/api/v1/admin/sign-in-providers/{provider['id']}/check", {}, token)
    assert r.status == 200 and r.json()["key_count"] >= 1, r.text
    ok("provider configured; its discovery document and signing keys were read")
    person = Browser()
    page = person.get(f"{WEB}/sign-in")
    assert 'id="sso-gov_sso"' in page.text, page.status
    r = person.get(f"{WEB}/auth/sso/gov_sso/start?next=/")
    assert r.status == 302 and r.headers["Location"].startswith(f"{IDP_ISSUER}/protocol/openid-connect/auth")
    assert "code_challenge_method=S256" in r.headers["Location"]
    login = person.get(r.headers["Location"])
    action = re.search(r'<form[^>]+id="kc-form-login"[^>]+action="([^"]+)"', login.text)
    assert action, login.text[:600]
    r = person.request(
        "POST",
        urljoin(IDP_ISSUER, html.unescape(action.group(1))),
        urlencode({"username": SSO_USER, "password": SSO_PASSWORD}).encode(),
        {"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status == 302 and "/auth/sso/gov_sso/callback" in r.headers["Location"], (r.status, r.text[:400])
    r = person.get(r.headers["Location"])
    assert r.status == 302 and r.headers["Location"].startswith("/auth/context"), (r.status, r.text[-600:])
    me = person.get(f"{WEB}/api/v1/me", headers={"Accept": "application/json"}).json()
    assert me["username"] == fixtures["sso_user"], me
    ok(f"signed in through the identity provider as {me['username']} (PKCE, verified ID token)")
    print("Staging smoke test passed")


if __name__ == "__main__":
    main()
