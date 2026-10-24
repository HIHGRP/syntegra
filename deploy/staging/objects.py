"""Staging rehearsal helpers (CR-008) run in the application image.

bucket   create the document bucket with object lock (write-once, compliance retention)
backup   mirror every object version to the backup volume with its SHA-256 (manifest.json)
verify   after the dumps are restored into a second MySQL: every table has the same row count as the live database,
         and every document master and searchable copy recorded in the restored database is in the object mirror
         with exactly the SHA-256 recorded at capture
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

BUCKET = os.environ.get("SYNTEGRA_S3_BUCKET", "syntegra-staging")
BACKUPS = Path(os.environ.get("STAGING_BACKUPS", "/backups"))
PREFIX = os.environ.get("SYNTEGRA_DB_PREFIX", "syn_stg")
ZONES = ("django", "platform", "registry", "ops", "vault", "records", "dw")


def s3() -> Any:
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=os.environ["SYNTEGRA_S3_ENDPOINT_URL"],
        region_name=os.environ.get("SYNTEGRA_S3_REGION", "us-east-1"),
        config=Config(s3={"addressing_style": "path"}, request_checksum_calculation="when_required"),
    )


def bucket() -> None:
    client = s3()
    try:
        client.create_bucket(Bucket=BUCKET, ObjectLockEnabledForBucket=True)
        print(f"created bucket {BUCKET} with object lock")
    except client.exceptions.BucketAlreadyOwnedByYou:
        print(f"bucket {BUCKET} exists")
    cfg = client.get_object_lock_configuration(Bucket=BUCKET)["ObjectLockConfiguration"]
    assert cfg.get("ObjectLockEnabled") == "Enabled", cfg
    print("object lock: enabled")


def backup() -> None:
    client = s3()
    out = BACKUPS / "objects"
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for page in client.get_paginator("list_object_versions").paginate(Bucket=BUCKET):
        for v in page.get("Versions", []):
            key, version = v["Key"], v["VersionId"]
            data = client.get_object(Bucket=BUCKET, Key=key, VersionId=version)["Body"].read()
            digest = hashlib.sha256(data).hexdigest()
            path = out / digest
            path.write_bytes(data)
            head = client.head_object(Bucket=BUCKET, Key=key, VersionId=version)
            until = head.get("ObjectLockRetainUntilDate")
            manifest.append(
                {
                    "key": key,
                    "version_id": version,
                    "sha256": digest,
                    "size": len(data),
                    "lock_mode": head.get("ObjectLockMode"),
                    "retain_until": until.isoformat() if until else None,
                }
            )
    (BACKUPS / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"mirrored {len(manifest)} object versions to {out}")
    unlocked = [m["key"] for m in manifest if m["lock_mode"] != "COMPLIANCE"]
    assert not unlocked, f"objects without compliance lock: {unlocked}"
    print("every object is under compliance lock")


def _connect(host: str, **kw: Any) -> Any:
    import MySQLdb

    return MySQLdb.connect(host=host, charset="utf8mb4", **kw)


def verify() -> None:
    live = _connect(
        os.environ.get("SYNTEGRA_DB_HOST", "db"),
        port=int(os.environ.get("SYNTEGRA_DB_PORT", "3306")),
        user=os.environ["SYNTEGRA_DB_USER"],
        password=os.environ["SYNTEGRA_DB_PASSWORD"],
        ssl={"ca": os.environ["SYNTEGRA_DB_SSL_CA"]},
        ssl_mode="VERIFY_IDENTITY",
    )
    restored = _connect(
        "db-restore",
        port=int(os.environ.get("STAGING_RESTORE_PORT", "3306")),
        user="root",
        password="restore-root-password",  # noqa: S106 — the throwaway restore server's
    )
    tables = rows = 0
    for zone in ZONES:
        schema = f"{PREFIX}_{zone}"
        with live.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'",
                [schema],
            )
            names = sorted(r[0] for r in cur.fetchall())
        for name in names:
            counts = []
            for conn in (live, restored):
                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM `{schema}`.`{name}`")
                    counts.append(int(cur.fetchone()[0]))
            assert counts[0] == counts[1], f"{schema}.{name}: live {counts[0]} rows, restored {counts[1]}"
            tables += 1
            rows += counts[0]
    print(f"restored database matches the live one: {tables} tables, {rows} rows")
    manifest = {m["sha256"]: m for m in json.loads((BACKUPS / "manifest.json").read_text())}
    with restored.cursor() as cur:
        cur.execute(
            f"SELECT reference_no, master_object_key, HEX(sha256) FROM `{PREFIX}_records`.document "
            "UNION ALL SELECT CONCAT('searchable copy of ', HEX(source_sha256)), object_key, HEX(sha256) "
            f"FROM `{PREFIX}_records`.document_rendition"
        )
        objects = cur.fetchall()
    assert objects, "no documents were recorded during the rehearsal"
    for name, key, recorded in objects:
        recorded = recorded.lower()
        entry = manifest.get(recorded)
        assert entry is not None, f"{name}: {key} is not in the object backup"
        assert entry["key"] == key, f"{name}: backed up as {entry['key']}, recorded as {key}"
        data = (BACKUPS / "objects" / recorded).read_bytes()
        assert hashlib.sha256(data).hexdigest() == recorded, f"{name}: the backed-up bytes do not match"
        print(f"  {name}: {key} ✓ sha256 {recorded[:16]}…")
    print(f"every recorded object is in the backup with its recorded hash: {len(objects)} objects")


if __name__ == "__main__":
    {"bucket": bucket, "backup": backup, "verify": verify}[sys.argv[1]]()
