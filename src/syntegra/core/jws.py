"""Compact JWS (RFC 7515) with ES256 for inter-registry messages — signing keys come from the KeyProvider."""

from __future__ import annotations

import base64
import json
from typing import Any

from syntegra.core import crypto
from syntegra.core.canonical_json import canonicalize


class JWSError(ValueError):
    pass


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(claims: dict[str, Any], kid: str) -> str:
    header = b64url(canonicalize({"alg": "ES256", "kid": kid, "typ": "JWT"}))
    payload = b64url(canonicalize(claims))
    signing_input = f"{header}.{payload}".encode()
    return f"{header}.{payload}.{b64url(crypto.sign_es256(kid, signing_input))}"


def unverified_header(token: str) -> dict[str, Any]:
    try:
        return dict(json.loads(b64url_decode(token.split(".")[0])))
    except (ValueError, IndexError) as exc:
        raise JWSError("malformed token") from exc


def verify(token: str, jwk: dict[str, str]) -> dict[str, Any]:
    """Return the claims if the ES256 signature verifies against ``jwk``; raise ``JWSError`` otherwise."""
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError as exc:
        raise JWSError("malformed token") from exc
    header = unverified_header(token)
    if header.get("alg") != "ES256":
        raise JWSError("unsupported algorithm")
    if not crypto.verify_es256(jwk, f"{header_b64}.{payload_b64}".encode(), b64url_decode(sig_b64)):
        raise JWSError("bad signature")
    return dict(json.loads(b64url_decode(payload_b64)))
