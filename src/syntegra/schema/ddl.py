"""Apply CEDA-generated DDL to a zone database.

The CEDA DDL (ceda/generated/mysql) is the physical schema authority; Django models are ``managed = False``.
Schema evolution follows CEDA §17.4: each CEDA release ships a migration in this app whose operations
apply that release's expand/contract DDL to every zone alias.
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


def statements_for_zone(zone: str) -> list[str]:
    base = Path(settings.SYNTEGRA_CEDA_DDL_DIR)
    stmts: list[str] = []
    for name in ZONE_FILES[zone]:
        stmts.extend(split_sql((base / name).read_text(encoding="utf-8")))
    return stmts


def apply_ceda_ddl(apps, schema_editor) -> None:  # type: ignore[no-untyped-def]
    alias = schema_editor.connection.alias
    zone = zone_of_alias(alias)
    with schema_editor.connection.cursor() as cur:
        for stmt in statements_for_zone(zone):
            cur.execute(stmt)
