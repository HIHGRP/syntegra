"""Object storage for binary masters (CEDA ``object_key``): write-once, content-addressed, hash-verified on read.

Production uses S3-compatible object storage with WORM (object-lock) buckets; this module is the single place that
reads and writes objects, so the backend can be swapped without touching the modules. The filesystem backend here
stores ``<root>/<key>`` with the key derived from the SHA-256 of the content — the same bytes are stored once — and
never overwrites an object. Every read recomputes the hash and refuses a file that no longer matches (MFS §13.2).
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from syntegra.core.errors import DomainError

KEY_RE = re.compile(r"^[a-z0-9][a-z0-9/_.-]{0,1000}$")


class IntegrityFailure(DomainError):
    def __init__(self, key: str):
        super().__init__(
            "STORE-INTEGRITY",
            "The stored file failed its integrity check",
            f"Object {key} no longer matches the hash recorded at capture. It has been withheld; tell the records "
            "manager.",
            500,
        )


@dataclass(frozen=True)
class Stored:
    key: str
    sha256: bytes
    size: int
    created: bool  # False when identical content was already stored (no extra space used)


def _root() -> Path:
    root = Path(getattr(settings, "SYNTEGRA_OBJECT_STORE_DIR", settings.REPO_DIR / "var" / "objects"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _path(key: str) -> Path:
    if not KEY_RE.match(key) or ".." in key or key.endswith("/"):
        raise ValueError(f"invalid object key {key!r}")
    return _root() / key


def put(data: bytes, *, prefix: str, ext: str) -> Stored:
    """Store ``data`` once under ``<prefix>/<aa>/<sha256>.<ext>``; storing the same bytes again is a no-op."""
    digest = hashlib.sha256(data).digest()
    hexd = digest.hex()
    key = f"{prefix.strip('/').lower()}/{hexd[:2]}/{hexd}.{ext.lower().lstrip('.')}"
    path = _path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o440)
    except FileExistsError:
        if hashlib.sha256(path.read_bytes()).digest() != digest:
            raise IntegrityFailure(key) from None
        return Stored(key, digest, len(data), created=False)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return Stored(key, digest, len(data), created=True)


def get(key: str, expected_sha256: bytes) -> bytes:
    """The object's bytes, after checking them against the hash recorded at capture."""
    path = _path(key)
    if not path.exists():
        raise IntegrityFailure(key)
    data = path.read_bytes()
    if hashlib.sha256(data).digest() != bytes(expected_sha256):
        raise IntegrityFailure(key)
    return data
