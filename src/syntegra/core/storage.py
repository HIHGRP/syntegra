"""Object storage for binary masters (CEDA ``object_key``): write-once, content-addressed, hash-verified on read.

Production uses S3-compatible object storage with WORM (object-lock) buckets; this module is the single place that
reads and writes objects, so the backend can be swapped without touching the modules. The filesystem backend here
stores ``<root>/<key>`` with the key derived from the SHA-256 of the content — the same bytes are stored once — and
never overwrites a good object. Every read recomputes the hash and refuses a file that no longer matches (MFS §13.2).
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from syntegra.core.errors import DomainError

log = logging.getLogger(__name__)
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


def _write_temp(directory: Path, data: bytes) -> Path:
    """Write ``data`` to a new temporary file in ``directory`` and flush it to disk."""
    fd, name = tempfile.mkstemp(dir=directory, prefix=".incoming-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, 0o440)
    except BaseException:
        Path(name).unlink(missing_ok=True)
        raise
    return Path(name)


def put(data: bytes, *, prefix: str, ext: str) -> Stored:
    """Store ``data`` once under ``<prefix>/<aa>/<sha256>.<ext>``; storing the same bytes again is a no-op.

    The bytes are written to a temporary file and linked into place only once complete, so an object at its key is
    always whole: a crash or a full disk mid-write leaves no partial object, and a second upload of the same scan at
    the same moment finds either nothing or the finished file. An object at the key that does not match it (left
    by an earlier interrupted write) is replaced with these bytes — they are, by construction, its correct content.
    """
    digest = hashlib.sha256(data).digest()
    hexd = digest.hex()
    key = f"{prefix.strip('/').lower()}/{hexd[:2]}/{hexd}.{ext.lower().lstrip('.')}"
    path = _path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and _matches(path, digest):
        return Stored(key, digest, len(data), created=False)
    tmp = _write_temp(path.parent, data)
    try:
        try:
            os.link(tmp, path)  # fails if the object exists: never overwrites a good object
            created = True
        except FileExistsError:
            if _matches(path, digest):
                created = False
            else:
                log.warning("object %s did not match its key; replaced with the uploaded bytes", key)
                os.replace(tmp, path)
                created = True
    finally:
        tmp.unlink(missing_ok=True)
    return Stored(key, digest, len(data), created=created)


def _matches(path: Path, digest: bytes) -> bool:
    try:
        return hashlib.sha256(path.read_bytes()).digest() == digest
    except FileNotFoundError:
        return False


def get(key: str, expected_sha256: bytes) -> bytes:
    """The object's bytes, after checking them against the hash recorded at capture."""
    path = _path(key)
    if not path.exists():
        raise IntegrityFailure(key)
    data = path.read_bytes()
    if hashlib.sha256(data).digest() != bytes(expected_sha256):
        raise IntegrityFailure(key)
    return data
