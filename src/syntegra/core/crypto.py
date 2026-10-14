"""Field encryption, lookup tokens, sealed text and signing (CEDA §8.1, MFS §16.2, NFR-SEC-104).

Key hierarchy: KEK in the HSM/KMIP key manager → per-tenant (and per-scheme) data keys → per-record keys
for sealed special-category text. The application only talks to a ``KeyProvider``; development and tests
use ``LocalKeyProvider`` (keys derived with HKDF from ``SYNTEGRA_MASTER_KEY``), production plugs in the
HSM-backed provider via ``SYNTEGRA_KEY_PROVIDER``. Private keys never leave the provider.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import uuid
from functools import lru_cache
from typing import Protocol

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from django.conf import settings
from django.utils.module_loading import import_string

_VERSION = 1
_P256_ORDER = int("FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551", 16)


class KeyProvider(Protocol):
    def data_key(self, purpose: str, tenant_id: uuid.UUID | None, version: int = 1) -> bytes: ...
    def hmac_key(self, purpose: str, tenant_id: uuid.UUID | None) -> bytes: ...
    def sign_es256(self, kid: str, message: bytes) -> bytes: ...
    def public_jwk(self, kid: str) -> dict[str, str]: ...


class LocalKeyProvider:
    """Development/test key provider. NOT for production: keys derive from a single configured secret."""

    def __init__(self, master: str) -> None:
        self._master = master.encode()

    def _derive(self, info: str, length: int = 32) -> bytes:
        return HKDF(algorithm=hashes.SHA256(), length=length, salt=b"syntegra-ceda", info=info.encode()).derive(
            self._master
        )

    def data_key(self, purpose: str, tenant_id: uuid.UUID | None, version: int = 1) -> bytes:
        return self._derive(f"dek:{purpose}:{tenant_id}:{version}")

    def hmac_key(self, purpose: str, tenant_id: uuid.UUID | None) -> bytes:
        return self._derive(f"hmac:{purpose}:{tenant_id}")

    def _signing_key(self, kid: str) -> ec.EllipticCurvePrivateKey:
        scalar = int.from_bytes(self._derive(f"es256:{kid}", 48), "big") % (_P256_ORDER - 1) + 1
        return ec.derive_private_key(scalar, ec.SECP256R1())

    def sign_es256(self, kid: str, message: bytes) -> bytes:
        der = self._signing_key(kid).sign(message, ec.ECDSA(hashes.SHA256()))
        r, s = decode_dss_signature(der)
        return r.to_bytes(32, "big") + s.to_bytes(32, "big")  # JOSE raw r||s

    def public_jwk(self, kid: str) -> dict[str, str]:
        nums = self._signing_key(kid).public_key().public_numbers()
        b64 = lambda i: base64.urlsafe_b64encode(i.to_bytes(32, "big")).rstrip(b"=").decode()  # noqa: E731
        return {
            "kty": "EC",
            "crv": "P-256",
            "x": b64(nums.x),
            "y": b64(nums.y),
            "kid": kid,
            "alg": "ES256",
            "use": "sig",
        }


@lru_cache(maxsize=1)
def provider() -> KeyProvider:
    cls = import_string(settings.SYNTEGRA_KEY_PROVIDER)
    return cls(settings.SYNTEGRA_MASTER_KEY)  # type: ignore[no-any-return]


# --------------------------------------------------------------------------- field encryption (type secret)


def encrypt(plaintext: str, *, purpose: str, tenant_id: uuid.UUID | None, aad: bytes = b"") -> bytes:
    """AES-256-GCM envelope: version(1) | key version(2) | nonce(12) | ciphertext+tag."""
    key = provider().data_key(purpose, tenant_id)
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), aad or purpose.encode())
    return struct.pack(">BH", _VERSION, 1) + nonce + ct


def decrypt(blob: bytes, *, purpose: str, tenant_id: uuid.UUID | None, aad: bytes = b"") -> str:
    ver, kver = struct.unpack(">BH", blob[:3])
    if ver != _VERSION:
        raise ValueError("unknown envelope version")
    key = provider().data_key(purpose, tenant_id, kver)
    return AESGCM(key).decrypt(blob[3:15], blob[15:], aad or purpose.encode()).decode()


def lookup_hmac(value: str, *, scheme: str, tenant_id: uuid.UUID | None) -> bytes:
    """Keyed lookup token (HMAC-SHA-256) for exact matching without decrypting (NIN, phone, e-mail)."""
    norm = "".join(value.split()).upper()
    return hmac.new(provider().hmac_key(f"lookup:{scheme}", tenant_id), norm.encode(), hashlib.sha256).digest()


def last4(value: str) -> str:
    v = "".join(value.split())
    return v[-4:]


# --------------------------------------------------------------------------- sealed special-category text


def seal(text: str, *, tenant_id: uuid.UUID | None, record_kind: str) -> bytes:
    """Encrypt with a fresh per-record key wrapped by the tenant's vault key.

    Layout: version(1) | wrap nonce(12) | wrapped key(48) | nonce(12) | ciphertext+tag. Erasure overwrites the
    blob (and therefore the only copy of the per-record key) — crypto-shredding (CEDA §8.3).
    """
    rec_key = AESGCM.generate_key(256)
    kek = provider().data_key("vault", tenant_id)
    wn, n = os.urandom(12), os.urandom(12)
    wrapped = AESGCM(kek).encrypt(wn, rec_key, record_kind.encode())
    ct = AESGCM(rec_key).encrypt(n, text.encode(), record_kind.encode())
    return bytes([_VERSION]) + wn + wrapped + n + ct


def unseal(blob: bytes, *, tenant_id: uuid.UUID | None, record_kind: str) -> str:
    if not blob or blob[0] != _VERSION:
        raise ValueError("sealed value unreadable (erased or unknown version)")
    wn, wrapped, n, ct = blob[1:13], blob[13:61], blob[61:73], blob[73:]
    rec_key = AESGCM(provider().data_key("vault", tenant_id)).decrypt(wn, wrapped, record_kind.encode())
    return AESGCM(rec_key).decrypt(n, ct, record_kind.encode()).decode()


# --------------------------------------------------------------------------- signatures


def sign_es256(kid: str, message: bytes) -> bytes:
    return provider().sign_es256(kid, message)


def verify_es256(jwk: dict[str, str], message: bytes, signature: bytes) -> bool:
    def b64d(s: str) -> int:
        return int.from_bytes(base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)), "big")

    pub = ec.EllipticCurvePublicNumbers(b64d(jwk["x"]), b64d(jwk["y"]), ec.SECP256R1()).public_key()
    der = encode_dss_signature(int.from_bytes(signature[:32], "big"), int.from_bytes(signature[32:], "big"))
    try:
        pub.verify(der, message, ec.ECDSA(hashes.SHA256()))
    except Exception:
        return False
    return True


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()
