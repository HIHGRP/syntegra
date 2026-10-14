"""Apply CEDA-generated DDL to a zone database.

The CEDA DDL is the physical schema authority; Django models are ``managed = False``. Schema evolution
follows CEDA §17.4: ``ceda/releases/<version>/`` holds the full DDL of the baseline release and an
expand-only delta (plus any hand-written expand script in ``manual/``) for each later release; every release
has one migration in this app that applies it to each zone alias. ``ceda/tools/release.py check --mysql``
proves that replaying the releases reproduces the current generated DDL.
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings

from syntegra.core.zones import zone_of_alias

ZONE_FILES = {
    "platform": ["00_platform.sql"],
    "registry": ["10_registry.sql", "15_registry_seed_code_lists.sql"],
    "ops": ["20_ops.sql"],
    "vault": ["30_vault.sql"],
    "records": ["40_records.sql"],
    "dw": ["90_dw.sql"],
}


def split_sql(script: str) -> list[str]:
    """Split a MySQL script into statements, respecting quotes, backticks and ``--`` comments."""
    out: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    i, n = 0, len(script)
    while i < n:
        ch = script[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and quote == "'" and i + 1 < n:
                buf.append(script[i + 1])
                i += 2
                continue
            if ch == quote:
                if quote == "'" and i + 1 < n and script[i + 1] == "'":
                    buf.append("'")
                    i += 2
                    continue
                quote = None
        elif ch in ("'", "`", '"'):
            quote = ch
            buf.append(ch)
        elif ch == "-" and script.startswith("--", i):
            j = script.find("\n", i)
            i = n if j < 0 else j
            continue
        elif ch == ";":
            stmt = "".join(buf).strip()
            if stmt:
                out.append(stmt)
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def release_dir(version: str) -> Path:
    return Path(settings.SYNTEGRA_CEDA_RELEASES_DIR) / version


def statements_for_zone(zone: str, version: str) -> list[str]:
    """Statements of one CEDA release for a zone: the hand-written expand script first, then the release file."""
    d = release_dir(version)
    stmts: list[str] = []
    for name in ZONE_FILES[zone]:
        for path in (d / "manual" / name, d / name):
            if path.exists():
                stmts.extend(split_sql(path.read_text(encoding="utf-8")))
    return stmts


def apply_release(version: str):  # type: ignore[no-untyped-def]
    """RunPython operation applying CEDA release ``version`` to whichever zone alias is being migrated."""

    def apply(apps, schema_editor) -> None:  # type: ignore[no-untyped-def]
        zone = zone_of_alias(schema_editor.connection.alias)
        with schema_editor.connection.cursor() as cur:
            for stmt in statements_for_zone(zone, version):
                cur.execute(stmt)

    return apply
