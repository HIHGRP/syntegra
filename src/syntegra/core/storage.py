"""Object storage for binary masters (CEDA ``object_key``): write-once, content-addressed, hash-verified on read.

This module is the single place that reads and writes objects. Keys derive from the SHA-256 of the content —
``<prefix>/<aa>/<sha256>.<ext>`` — so the same bytes are stored once, and every read recomputes the hash and
refuses an object that no longer matches (MFS §13.2).

Two stores (``SYNTEGRA_OBJECT_STORE``):

* ``s3`` — production and staging (CR-008, FR-DOC-301). S3-compatible object storage in a bucket created with object
  lock: each object is written once (a conditional write that fails if the key exists), with its SHA-256 checksum,
  under object lock in compliance mode until its retain-until date, so nobody — administrators included — can change
  or delete it before then.
* ``fs`` — development and tests only. Files under ``SYNTEGRA_OBJECT_STORE_DIR``, written to a temporary file and
  linked into place only when complete, never overwriting a good object.

The store an object was written to is recorded beside its key (``document.master_store``), so reads go to the right
place even after the default changes.
"""

from __future__ import annotations

import base64
import datetime as dt
import functools
import hashlib
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.conf import settings

from syntegra.core.errors import DomainError

log = logging.getLogger(__name__)
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9/_.-]{0,1000}$")
FS, S3 = "fs", "s3"


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
    store: str = FS
    lock_mode: str = "none"  # none, governance or compliance (CEDA object_lock_mode)
    retain_until: dt.date | None = None


def default_store() -> str:
    return str(getattr(settings, "SYNTEGRA_OBJECT_STORE", FS) or FS).lower()


def make_key(data: bytes, prefix: str, ext: str) -> tuple[str, bytes]:
    digest = hashlib.sha256(data).digest()
    hexd = digest.hex()
    key = f"{prefix.strip('/').lower()}/{hexd[:2]}/{hexd}.{ext.lower().lstrip('.')}"
    if not KEY_RE.match(key) or ".." in key or key.endswith("/"):
        raise ValueError(f"invalid object key {key!r}")
    return key, digest


def put(
    data: bytes,
    *,
    prefix: str,
    ext: str,
    retain_until: dt.date | None = None,
    content_type: str = "application/octet-stream",
) -> Stored:
    """Store ``data`` once in the default store; storing the same bytes again is a no-op. On S3 the object is locked
    until ``retain_until`` (compliance mode unless configured otherwise)."""
    key, digest = make_key(data, prefix, ext)
    if default_store() == S3:
        return _s3_put(key, digest, data, retain_until, content_type)
    return _fs_put(key, digest, data, retain_until)


def get(key: str, expected_sha256: bytes, store: str | None = None) -> bytes:
    """The object's bytes from the store it was written to, after checking them against the hash recorded at
    capture."""
    data = _s3_get(key) if (store or FS) == S3 else _fs_get(key)
    if data is None or hashlib.sha256(data).digest() != bytes(expected_sha256):
        raise IntegrityFailure(key)
    return data


def lock_status(key: str, store: str | None) -> dict[str, Any]:
    """What the store itself says about an object's lock — shown on the document page as evidence."""
    if (store or FS) != S3:
        return {"store": FS, "mode": "none", "retain_until": None}
    head = _s3().head_object(Bucket=_bucket(), Key=key, ChecksumMode="ENABLED")
    until = head.get("ObjectLockRetainUntilDate")
    return {
        "store": S3,
        "mode": str(head.get("ObjectLockMode") or "none").lower(),
        "retain_until": until.date() if until else None,
        "legal_hold": head.get("ObjectLockLegalHoldStatus") == "ON",
        "checksum_sha256": head.get("ChecksumSHA256"),
        "version_id": head.get("VersionId"),
    }


# --------------------------------------------------------------------------- filesystem (development and tests)
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


def _fs_put(key: str, digest: bytes, data: bytes, retain_until: dt.date | None) -> Stored:
    """The bytes are written to a temporary file and linked into place only once complete, so an object at its key
    is always whole: a crash or a full disk mid-write leaves no partial object, and a second upload of the same scan
    at the same moment finds either nothing or the finished file. An object at the key that does not match it (left
    by an earlier interrupted write) is replaced with these bytes — they are, by construction, its correct content."""
    path = _path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and _matches(path, digest):
        return Stored(key, digest, len(data), False, FS, "none", retain_until)
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
    return Stored(key, digest, len(data), created, FS, "none", retain_until)


def _matches(path: Path, digest: bytes) -> bool:
    try:
        return hashlib.sha256(path.read_bytes()).digest() == digest
    except FileNotFoundError:
        return False


def _fs_get(key: str) -> bytes | None:
    path = _path(key)
    return path.read_bytes() if path.exists() else None


# --------------------------------------------------------------------------- S3 with object lock (production)
def _bucket() -> str:
    bucket = getattr(settings, "SYNTEGRA_S3_BUCKET", "")
    if not bucket:
        raise DomainError("STORE-CONFIG", "Object storage is not configured", "Set SYNTEGRA_S3_BUCKET.", 500)
    return str(bucket)


@functools.cache
def _client(endpoint: str | None, region: str, path_style: bool) -> Any:
    import boto3
    from botocore.config import Config

    cfg = Config(
        retries={"max_attempts": 5, "mode": "standard"},
        s3={"addressing_style": "path" if path_style else "auto"},
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
    )
    return boto3.client("s3", endpoint_url=endpoint or None, region_name=region, config=cfg)


def _s3() -> Any:
    return _client(
        getattr(settings, "SYNTEGRA_S3_ENDPOINT_URL", None) or None,
        str(getattr(settings, "SYNTEGRA_S3_REGION", "us-east-1")),
        bool(getattr(settings, "SYNTEGRA_S3_PATH_STYLE", False)),
    )


def _lock_mode() -> str:
    mode = str(getattr(settings, "SYNTEGRA_S3_LOCK_MODE", "COMPLIANCE")).upper()
    return mode if mode in ("COMPLIANCE", "GOVERNANCE") else "COMPLIANCE"


def _s3_put(key: str, digest: bytes, data: bytes, retain_until: dt.date | None, content_type: str) -> Stored:
    from botocore.exceptions import ClientError

    s3, bucket = _s3(), _bucket()
    checksum = base64.b64encode(digest).decode()
    args: dict[str, Any] = {
        "Bucket": bucket,
        "Key": key,
        "Body": data,
        "ContentType": content_type,
        "ChecksumAlgorithm": "SHA256",
        "ChecksumSHA256": checksum,  # the store refuses bytes that arrive different from what was hashed here
        "IfNoneMatch": "*",  # write once: refused if an object already has this key
        "Metadata": {"sha256": digest.hex()},
    }
    mode = "none"
    if retain_until is not None:
        mode = _lock_mode()
        args["ObjectLockMode"] = mode
        args["ObjectLockRetainUntilDate"] = dt.datetime.combine(retain_until, dt.time(), tzinfo=dt.UTC)
    try:
        s3.put_object(**args)
        return Stored(key, digest, len(data), True, S3, mode.lower(), retain_until)
    except ClientError:
        # Refused because the key exists — AWS answers 412 to the conditional write; some S3-compatible stores
        # instead refuse to overwrite a locked object. Either way nothing was overwritten. Anything else is a real
        # failure: re-raise it unless an object is in fact there.
        existing = _s3_get(key)
        if existing is None:
            raise
    # the key exists: the same bytes were stored before (keys are content hashes) — prove it, never overwrite
    if existing is None or hashlib.sha256(existing).digest() != digest:
        raise IntegrityFailure(key)
    status_now = lock_status(key, S3)
    return Stored(key, digest, len(data), False, S3, str(status_now["mode"]), status_now["retain_until"])


def _s3_get(key: str) -> bytes | None:
    from botocore.exceptions import ClientError

    try:
        obj = _s3().get_object(Bucket=_bucket(), Key=key)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") in ("NoSuchKey", "404"):
            return None
        raise
    return bytes(obj["Body"].read())
