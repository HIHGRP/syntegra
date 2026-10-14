#!/usr/bin/env python3
"""CEDA release management — frozen DDL per release and expand-only deltas (CEDA §17.4).

ceda/generated/mysql/ always holds the *current* full DDL. A database that already runs an earlier release
must not be rebuilt, so each release is kept under ceda/releases/<version>/:

  * the baseline release holds the full DDL of every zone (``kind: baseline``);
  * every later release holds only the statements that are new since the previous release (``kind: delta``):
    new tables, their triggers, and new code-list values. A change to an existing table cannot be derived
    automatically — the tool stops and asks for a hand-written expand/contract script in ``manual/``.

  python3 ceda/tools/release.py baseline 1.1.0 <git-ref>   # freeze the full DDL of a past release from git
  python3 ceda/tools/release.py delta 1.2.0                # derive the delta of the current model
  python3 ceda/tools/release.py check                      # replaying all releases == current generated DDL
  python3 ceda/tools/release.py check --mysql              # same, structurally, by loading both into MySQL
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "ceda" / "generated" / "mysql"
RELEASES = ROOT / "ceda" / "releases"
FILES = ["00_platform.sql", "10_registry.sql", "15_registry_seed_code_lists.sql", "20_ops.sql", "30_vault.sql",
         "40_records.sql", "90_dw.sql"]
SEED = "15_registry_seed_code_lists.sql"
ROW = re.compile(r"^\s*\(UUID_TO_BIN\(UUID\(\)\), @tenant, \(SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant "
                 r"AND `code` = '([^']+)'\), '((?:[^']|'')*)',")


def split_sql(script: str) -> list[str]:
    """Statements of a MySQL script (quotes, backticks and -- comments respected)."""
    out, buf, quote, i, n = [], [], None, 0, len(script)
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
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return out


def table_of(stmt: str) -> str | None:
    m = re.match(r"CREATE TABLE `([^`]+)`", stmt)
    return m.group(1) if m else None


def seed_rows(stmts: list[str]) -> dict[tuple[str, str], str]:
    rows = {}
    for s in stmts:
        if s.startswith("INSERT INTO `code_value`"):
            for line in s.splitlines()[1:]:
                m = ROW.match(line)
                if m:
                    rows[(m.group(1), m.group(2))] = line.strip().rstrip(",")
    return rows


def manifest(version: str) -> dict:
    return json.loads((RELEASES / version / "release.json").read_text())


def versions() -> list[str]:
    vs = [p.name for p in RELEASES.iterdir() if (p / "release.json").exists()] if RELEASES.exists() else []
    return sorted(vs, key=lambda v: tuple(int(x) for x in v.split(".")))


def release_files(version: str, f: str) -> list[Path]:
    """Scripts of one release for one DDL file, in apply order: hand-written expand script first, then the delta."""
    d = RELEASES / version
    out = [d / "manual" / f] if (d / "manual" / f).exists() else []
    return out + ([d / f] if (d / f).exists() else [])


def manual_tables(version: str | None = None) -> set[str]:
    """Existing tables altered by hand-written expand scripts (compared structurally, in MySQL)."""
    out: set[str] = set()
    for v in [version] if version else versions():
        md = RELEASES / v / "manual"
        for p in sorted(md.glob("*.sql")) if md.exists() else []:
            out |= set(re.findall(r"ALTER TABLE `([^`]+)`", p.read_text(encoding="utf-8")))
    return out


def _key(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def replay(before: str | None = None) -> dict[str, list[str]]:
    """Statements per file after applying every release in order (only releases earlier than ``before``)."""
    state: dict[str, list[str]] = {f: [] for f in FILES}
    for v in versions():
        if before is not None and _key(v) >= _key(before):
            continue
        for f in FILES:
            for p in release_files(v, f):
                state[f] += split_sql(p.read_text(encoding="utf-8"))
    return state


def cmd_baseline(version: str, ref: str) -> int:
    d = RELEASES / version
    d.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        text = subprocess.run(["git", "show", f"{ref}:ceda/generated/mysql/{f}"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout
        (d / f).write_text(text, encoding="utf-8")
    (d / "release.json").write_text(json.dumps({"version": version, "kind": "baseline", "git_ref": ref}, indent=2) + "\n")
    print(f"froze baseline {version} from {ref}")
    return 0


def cmd_delta(version: str) -> int:
    prev = replay(before=version)
    d = RELEASES / version
    d.mkdir(parents=True, exist_ok=True)
    problems = []
    covered = manual_tables(version)
    for f in FILES:
        cur = split_sql((CURRENT / f).read_text(encoding="utf-8"))
        old = prev[f]
        if f == SEED:
            old_rows, cur_rows = seed_rows(old), seed_rows(cur)
            new_lists = [s for s in cur if s.startswith("INSERT INTO `code_list`") and s not in old]
            added = [cur_rows[k] for k in cur_rows if k not in old_rows]
            body = new_lists[:]
            if added:
                body.append("INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, "
                            "`valid_from`) VALUES\n  " + ",\n  ".join(added))
            header = ["SET NAMES utf8mb4", "SET @tenant = UUID_TO_BIN('00000000-0000-7000-8000-000000000001')"]
            stmts = header + body if body else []
        else:
            old_set = set(old)
            old_tables = {table_of(s): s for s in old if table_of(s)}
            stmts = []
            for s in cur:
                if s in old_set:
                    continue
                t = table_of(s)
                if t and t in old_tables:
                    if t in covered:
                        continue
                    problems.append(f"{f}: table {t} changed — write an expand/contract script in {d / 'manual'}")
                    continue
                if s.startswith("SET "):
                    continue
                stmts.append(s)
            if stmts:
                stmts = ["SET NAMES utf8mb4", "SET time_zone = '+00:00'"] + stmts
        if stmts:
            (d / f).write_text(f"-- CEDA {version} delta for {f} — generated by ceda/tools/release.py. DO NOT EDIT.\n"
                               + ";\n\n".join(stmts) + ";\n", encoding="utf-8")
        elif (d / f).exists():
            (d / f).unlink()
    if problems:
        print("\n".join(problems))
        return 1
    (d / "release.json").write_text(json.dumps({"version": version, "kind": "delta"}, indent=2) + "\n")
    print(f"wrote delta {version}: " + ", ".join(p.name for p in sorted(d.glob("*.sql"))))
    return 0


def _norm(stmts: list[str], skip: set[str]) -> set[str]:
    return {s for s in stmts if not s.startswith(("SET ", "ALTER TABLE")) and table_of(s) not in skip}


def cmd_check() -> int:
    state = replay()
    ok = True
    for f in FILES:
        cur = split_sql((CURRENT / f).read_text(encoding="utf-8"))
        if f == SEED:
            same = seed_rows(cur).keys() == seed_rows(state[f]).keys()
        else:
            skip = manual_tables()
            same = _norm(cur, skip) == _norm(state[f], skip)
        if not same:
            ok = False
            print(f"{f}: replaying releases {versions()} does not reproduce the current DDL — run `release.py delta`")
    print("releases reproduce the current DDL" + (f" (structural check in MySQL for {sorted(manual_tables())})"
                                                   if manual_tables() else "") if ok else "release check failed")
    return 0 if ok else 1


ZONE_OF = {"00_platform.sql": "platform", "10_registry.sql": "registry", "15_registry_seed_code_lists.sql": "registry",
           "20_ops.sql": "ops", "30_vault.sql": "vault", "40_records.sql": "records", "90_dw.sql": "dw"}
SHAPE = """
SELECT 'col', TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, IFNULL(COLUMN_DEFAULT,'~'), EXTRA, IFNULL(GENERATION_EXPRESSION,'')
  FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()
UNION ALL SELECT 'idx', TABLE_NAME, INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX), NON_UNIQUE, '', '', ''
  FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = DATABASE() GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE
UNION ALL SELECT 'chk', cc.CONSTRAINT_NAME, cc.CHECK_CLAUSE, '', '', '', '', ''
  FROM information_schema.CHECK_CONSTRAINTS cc WHERE cc.CONSTRAINT_SCHEMA = DATABASE()
UNION ALL SELECT 'fk', TABLE_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, '', '', '', ''
  FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = DATABASE()
UNION ALL SELECT 'trg', TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, '', '', '', ''
  FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE()
ORDER BY 1, 2, 3"""


def _mysql(sql: str, db: str | None = None) -> str:
    import os
    import shlex

    cmd = shlex.split(os.environ.get("MYSQL_CMD", "mysql -h127.0.0.1 -uroot -pceda")) + ["--batch", "--skip-column-names"]
    p = subprocess.run(cmd + ([db] if db else []), input=sql, capture_output=True, text=True)
    err = "\n".join(x for x in p.stderr.splitlines() if "Using a password" not in x)
    if p.returncode:
        raise SystemExit(f"MySQL error ({db}): {err}")
    return p.stdout


def cmd_check_mysql() -> int:
    """Load (a) every release in order and (b) the current DDL into scratch schemas; compare their shape."""
    ok = True
    for zone in ("platform", "registry", "ops", "vault", "records", "dw"):
        files = [f for f in FILES if ZONE_OF[f] == zone]
        a, b = f"ceda_rel_{zone}", f"ceda_cur_{zone}"
        _mysql(f"DROP DATABASE IF EXISTS {a}; CREATE DATABASE {a}; DROP DATABASE IF EXISTS {b}; CREATE DATABASE {b};")
        for v in versions():
            for f in files:
                for p in release_files(v, f):
                    _mysql(p.read_text(encoding="utf-8"), a)
        for f in files:
            _mysql((CURRENT / f).read_text(encoding="utf-8"), b)
        sa, sb = _mysql(SHAPE, a), _mysql(SHAPE, b)
        rows_a = _mysql("SELECT code_list_id IS NOT NULL, COUNT(*) FROM code_value GROUP BY 1", a) if zone == "registry" else ""
        rows_b = _mysql("SELECT code_list_id IS NOT NULL, COUNT(*) FROM code_value GROUP BY 1", b) if zone == "registry" else ""
        same = sa == sb and rows_a == rows_b
        ok &= same
        print(f"{zone}: {'identical' if same else 'DIFFERENT'} ({len(sb.splitlines())} schema facts)")
        if not same:
            import difflib

            print("\n".join(list(difflib.unified_diff(sa.splitlines(), sb.splitlines(), "releases", "current",
                                                       lineterm=""))[:40]))
        _mysql(f"DROP DATABASE {a}; DROP DATABASE {b};")
    print("replayed releases are structurally identical to the current DDL" if ok else "structural check failed")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["baseline"] and len(a) == 3:
        sys.exit(cmd_baseline(a[1], a[2]))
    if a[:1] == ["delta"] and len(a) == 2:
        sys.exit(cmd_delta(a[1]))
    if a[:1] == ["check"]:
        sys.exit(cmd_check_mysql() if "--mysql" in a else cmd_check())
    print(__doc__)
    sys.exit(2)
