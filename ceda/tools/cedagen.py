#!/usr/bin/env python3
"""cedagen — validator and generator for the Syntegra Canonical Enterprise Data Architecture.

The CEDA model (ceda/model/**/*.yaml) is the single source of truth for Syntegra's data.
This tool validates it and generates every derived artefact under ceda/generated/:

  mysql/        MySQL 9.7 DDL, one file per data zone
  dictionary/   data dictionary (Markdown), one file per domain
  erd/          Mermaid entity-relationship diagrams, one per domain
  jsonschema/   JSON Schema (2020-12) of every entity, one bundle per domain
  openapi/      OpenAPI 3.1 component schemas for the REST API
  events/       domain-event catalogue and CloudEvents envelope + payload schemas
  metrics/      semantic-layer metric catalogue
  traceability/ requirement, page and Appendix J coverage reports
  summary.json  counts used by the documentation

Usage:
  python3 ceda/tools/cedagen.py validate        # validate only (exit 1 on errors)
  python3 ceda/tools/cedagen.py generate        # validate, then (re)write ceda/generated/
  python3 ceda/tools/cedagen.py check           # validate and fail if generated/ is stale
"""
from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]          # .../ceda
MODEL = ROOT / "model"
SOURCES = ROOT / "sources"
GENERATED = ROOT / "generated"

ZONE_ORDER = ["platform", "registry", "ops", "vault", "records", "dw"]
ZONE_FILE = {"platform": "00_platform", "registry": "10_registry", "ops": "20_ops",
             "vault": "30_vault", "records": "40_records", "dw": "90_dw"}
CLASS_ORDER = ["public", "internal", "confidential", "restricted", "special"]
NO_INDEX_TYPES = {"text", "longtext", "json", "sealed", "secret", "cls"}
MAX_IDENT = 64

# ----------------------------------------------------------------------------- model classes


@dataclass
class Attr:
    name: str
    type: str
    args: list
    required: bool
    flags: set
    opts: dict
    doc: str
    entity: "Entity" = None

    @property
    def classification(self):
        for c in reversed(CLASS_ORDER):
            if c in self.flags:
                return c
        return None

    @property
    def ref_target(self):
        return self.args[0] if self.type == "ref" else None


@dataclass
class Column:
    name: str
    mysql: str
    nullable: bool
    default: str | None = None
    on_update: bool = False
    comment: str = ""
    attr: Attr | None = None
    standard: bool = False
    logical_type: str = ""
    generated: str | None = None


@dataclass
class Entity:
    name: str
    zone: str
    domain: "Domain"
    spec: dict
    attrs: list = field(default_factory=list)
    columns: list = field(default_factory=list)
    pk: list = field(default_factory=list)
    uniques: list = field(default_factory=list)
    indexes: list = field(default_factory=list)
    checks: list = field(default_factory=list)
    fks: list = field(default_factory=list)
    soft_refs: list = field(default_factory=list)
    replicated: bool = False

    def g(self, key, default=None):
        return self.spec.get(key, default)

    @property
    def title(self):
        return self.spec.get("title", "")

    @property
    def kind(self):
        return self.spec.get("kind")

    @property
    def history(self):
        return self.spec.get("history", "none")

    @property
    def classification(self):
        return self.spec.get("class")

    @property
    def partition(self):
        return self.spec.get("partition")

    @property
    def append_only(self):
        return self.history in ("append", "snapshot")

    @property
    def module(self):
        return self.spec.get("module", self.domain.module)

    @property
    def tenant(self):
        return bool(MODEL_META["zones"][self.zone]["tenant_column"])

    @property
    def key(self):
        return f"{self.zone}.{self.name}" if self.replicated else self.name

    def col(self, name):
        for c in self.columns:
            if c.name == name:
                return c
        return None


@dataclass
class Domain:
    file: Path
    name: str
    code: str
    title: str
    module: str
    zone: str
    summary: str
    retention: str | None
    entities: list = field(default_factory=list)


class Errors:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


MODEL_META: dict = {}

# ----------------------------------------------------------------------------- loading

ATTR_RE = re.compile(r"^\s*(?P<name>[a-z][a-z0-9_]*)\s*:\s*(?P<type>[a-z_]+)(?:\((?P<args>[^)]*)\))?(?P<req>!)?"
                     r"(?P<flags>[^|]*)(?:\|\s*(?P<doc>.*))?$")


def parse_attr(raw: str, errs: Errors, where: str) -> Attr | None:
    m = ATTR_RE.match(raw)
    if not m:
        errs.err(f"{where}: cannot parse attribute '{raw}'")
        return None
    args = [a.strip() for a in (m.group("args") or "").split(",") if a.strip()]
    flags, opts = set(), {}
    for tok in (m.group("flags") or "").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            opts[k] = v
        else:
            flags.add(tok)
    return Attr(m.group("name"), m.group("type"), args, bool(m.group("req")), flags, opts,
                (m.group("doc") or "").strip())


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class Model:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.errs = Errors()
        global MODEL_META
        self.meta = load_yaml(MODEL / "_meta.yaml")
        MODEL_META = self.meta
        self.types = load_yaml(MODEL / "types.yaml")["types"]
        self.enums = load_yaml(MODEL / "enums.yaml")["enums"]
        self.events = load_yaml(MODEL / "events.yaml")["events"]
        self.metrics = load_yaml(MODEL / "metrics.yaml")["metrics"]
        self.retention = {r["code"]: r for r in load_yaml(MODEL / "retention.yaml")["series"]}
        self.codelists = {}
        for p in sorted((MODEL / "reference").glob("*.yaml")):
            doc = load_yaml(p)
            for cl in doc.get("code_lists", []):
                self.codelists[cl["code"]] = dict(cl, pack=doc.get("pack"))
        self.trace = load_yaml(MODEL / "traceability.yaml")
        self.pages = {p["id"]: p for p in load_yaml(SOURCES / "mfs_pages.yaml")["pages"]}
        self.requirements = {r["id"]: r for r in load_yaml(SOURCES / "mfs_requirements.yaml")["requirements"]}
        self.appj = {t["table"]: t for t in load_yaml(SOURCES / "mfs_appj_tables.yaml")["tables"]}
        self.reserved = set((SOURCES / "mysql97_reserved_words.txt").read_text().split())
        self.domains: list[Domain] = []
        self.entities: dict[str, Entity] = {}         # key -> Entity (replicated entities keyed zone.name)
        self.by_name: dict[str, list[Entity]] = defaultdict(list)
        self._load_domains()
        self._build()

    # .................................................................. domains
    def _load_domains(self):
        for path in sorted((MODEL / "domains").glob("*.yaml")):
            doc = load_yaml(path)
            d = Domain(path, doc["domain"], doc["code"], doc["title"], doc.get("module", doc["domain"]),
                       doc.get("zone", "ops"), (doc.get("summary") or "").strip(), doc.get("retention"))
            self.domains.append(d)
            for name, spec in (doc.get("entities") or {}).items():
                spec = spec or {}
                zones = spec.get("zone", d.zone)
                zones = zones if isinstance(zones, list) else [zones]
                for z in zones:
                    e = Entity(name, z, d, spec, replicated=len(zones) > 1)
                    if e.key in self.entities:
                        self.errs.err(f"duplicate entity {e.key} ({path.name})")
                        continue
                    self.entities[e.key] = e
                    self.by_name[name].append(e)
                    d.entities.append(e)

    def resolve(self, name: str, zone: str | None = None) -> Entity | None:
        cands = self.by_name.get(name, [])
        if not cands:
            return None
        if zone:
            for c in cands:
                if c.zone == zone:
                    return c
        return cands[0]

    # .................................................................. build
    def _build(self):
        E = self.errs
        meta_std = self.meta["standard_columns"]
        for e in self.entities.values():
            where = f"{e.domain.file.name}:{e.name}"
            for raw in e.g("attrs", []) or []:
                a = parse_attr(raw, E, where)
                if a:
                    a.entity = e
                    e.attrs.append(a)
            dw = e.zone == "dw"
            custom_pk = e.g("pk")
            # id
            if not custom_pk and not dw:
                e.columns.append(self._std("id", meta_std))
            if e.tenant:
                e.columns.append(self._std("tenant_id", meta_std))
            scope = str(e.g("scope", "none"))
            if scope.startswith("owned"):
                c = self._std("scope_node_id", meta_std)
                c.nullable = scope.endswith("?")
                e.columns.append(c)
            for a in e.attrs:
                e.columns.extend(self._columns_for(a, where))
            if e.history == "effective":
                e.columns.append(self._std("valid_from", meta_std))
                e.columns.append(self._std("valid_to", meta_std))
                e.checks.append(("valid", "valid_to IS NULL OR valid_to >= valid_from"))
            if dw:
                e.columns.append(Column("loaded_at", "DATETIME(6)", False, "CURRENT_TIMESTAMP(6)",
                                        comment="Warehouse load time (UTC)", standard=True, logical_type="ts"))
                e.columns.append(Column("load_batch_id", "BIGINT", False, comment="ETL batch that wrote the row",
                                        standard=True, logical_type="bigint"))
            else:
                e.columns.append(self._std("created_at", meta_std))
                e.columns.append(self._std("created_by", meta_std))
                if not e.append_only:
                    for n in ("updated_at", "updated_by", "row_version"):
                        e.columns.append(self._std(n, meta_std))
            # keys
            part = e.partition
            if custom_pk:
                e.pk = list(custom_pk)
            else:
                e.pk = ["id"] + ([part["column"]] if part else [])
            for a in e.attrs:
                cols = self._attr_colnames(a)
                if "uq" in a.flags:
                    e.uniques.append(cols[:1])
                if "ix" in a.flags:
                    e.indexes.append(cols[:1])
            for u in e.g("uq", []) or []:
                e.uniques.append(list(u))
            for i in e.g("ix", []) or []:
                e.indexes.append(list(i))
            for name, expr in (e.g("checks") or {}).items():
                e.checks.append((name, expr))

    def _std(self, name, meta_std):
        s = meta_std[name]
        t = self.types[s["type"]]
        return Column(name, t["mysql"], s["nullable"], s.get("default"), s.get("on_update", False), s["doc"],
                      standard=True, logical_type=s["type"])

    def _attr_colnames(self, a: Attr):
        if a.type == "secret":
            names = [a.name + "_enc"]
            if "lookup" in a.flags:
                names.insert(0, a.name + "_hmac")
            if "mask4" in a.flags:
                names.append(a.name + "_last4")
            return names
        if a.type == "money":
            return [a.name + "_minor"]
        return [a.name]

    def _columns_for(self, a: Attr, where) -> list:
        E = self.errs
        t = self.types.get(a.type)
        if not t:
            E.err(f"{where}.{a.name}: unknown type '{a.type}'")
            return []
        args = a.args or t.get("default_args", [])
        if "args" in t and len(args) != len(t["args"]):
            E.err(f"{where}.{a.name}: type {a.type} needs args {t['args']}")
            return []
        mysql = t["mysql"]
        if a.type == "enum":
            if args[0] not in self.enums:
                E.err(f"{where}.{a.name}: unknown enum '{args[0]}'")
            else:
                longest = max(len(v) for v in self.enums[args[0]]["values"])
                if longest > 32:
                    E.err(f"enum {args[0]} has a value longer than 32 chars")
        elif a.type in ("cl", "cls"):
            if args[0] not in self.codelists:
                E.err(f"{where}.{a.name}: unknown code list '{args[0]}'")
        elif "{0}" in mysql:
            mysql = mysql.format(*args)
        nullable = not a.required
        comment = a.doc
        cols = []
        if a.type == "secret":
            if "lookup" in a.flags:
                cols.append(Column(a.name + "_hmac", "BINARY(32)", nullable, comment=f"HMAC-SHA-256 lookup of {a.name}",
                                   attr=a, logical_type="hmac"))
            cols.append(Column(a.name + "_enc", "VARBINARY(1024)", nullable, comment=f"Envelope-encrypted {a.name}. {comment}".strip(),
                               attr=a, logical_type="secret"))
            if "mask4" in a.flags:
                cols.append(Column(a.name + "_last4", "CHAR(4) CHARACTER SET ascii COLLATE ascii_bin", True,
                                   comment=f"Last four characters of {a.name} for masked display", attr=a, logical_type="code"))
            return cols
        name = a.name + ("_minor" if a.type == "money" else "")
        default = a.opts.get("default")
        if default is not None and a.type in ("str", "name", "title", "code", "enum", "cl", "lang", "country", "currency", "phone", "email", "semver", "mime"):
            default = "'" + default.replace("'", "''") + "'"
        if default is not None and a.type == "bool":
            default = {"true": "TRUE", "false": "FALSE"}.get(default.lower(), default)
        if a.type == "money":
            comment = (comment + " (minor units)").strip()
        gen = (a.entity.g("generated") or {}).get(a.name) if a.entity else None
        if gen:
            cols.append(Column(name, mysql, True, None, comment=comment, attr=a, logical_type=a.type, generated=gen))
            return cols
        cols.append(Column(name, mysql, nullable, default, comment=comment, attr=a, logical_type=a.type))
        return cols


# ----------------------------------------------------------------------------- validation


def ident_ok(name):
    return bool(re.fullmatch(r"[a-z][a-z0-9_]*", name)) and len(name) <= MAX_IDENT


def short(name: str, limit=MAX_IDENT) -> str:
    if len(name) <= limit:
        return name
    h = hashlib.sha1(name.encode()).hexdigest()[:8]
    return name[: limit - 9] + "_" + h


def mysql_key_bytes(col: Column) -> int:
    t = col.mysql.upper()
    m = re.match(r"(VAR)?CHAR\((\d+)\)", t)
    if m:
        n = int(m.group(2))
        return n * (1 if "ASCII" in t else 4) + (2 if m.group(1) else 0)
    m = re.match(r"(VAR)?BINARY\((\d+)\)", t)
    if m:
        return int(m.group(2)) + (2 if m.group(1) else 0)
    sizes = {"DATE": 3, "DATETIME(6)": 8, "TIME": 3, "BOOLEAN": 1, "INT": 4, "INT UNSIGNED": 4, "SMALLINT": 2,
             "BIGINT": 8}
    for k, v in sizes.items():
        if t.startswith(k):
            return v
    if t.startswith("DECIMAL"):
        return 9
    return 0


def validate(m: Model):
    E = m.errs
    enums_used, cls_used, events_used = set(), set(), set()
    pages_cov, reqs_cov = defaultdict(set), defaultdict(set)
    for code, en in m.enums.items():
        if not en.get("values"):
            E.err(f"enum {code} has no values")
    for d in m.domains:
        if d.zone not in ZONE_ORDER:
            E.err(f"{d.file.name}: unknown zone {d.zone}")
        if d.retention and d.retention not in m.retention:
            E.err(f"{d.file.name}: unknown retention series {d.retention}")
    for e in m.entities.values():
        w = f"{e.domain.file.name}:{e.name}"
        if e.zone not in ZONE_ORDER:
            E.err(f"{w}: unknown zone {e.zone}")
            continue
        if not ident_ok(e.name):
            E.err(f"{w}: invalid table name")
        if e.name in m.reserved:
            E.err(f"{w}: table name is a MySQL reserved word")
        for req in ("title", "kind", "class"):
            if not e.g(req):
                E.err(f"{w}: missing '{req}'")
        if e.kind and e.kind not in m.meta["kinds"] and e.zone != "dw":
            E.err(f"{w}: unknown kind {e.kind}")
        if e.history not in m.meta["history"]:
            E.err(f"{w}: unknown history {e.history}")
        if e.classification and e.classification not in CLASS_ORDER:
            E.err(f"{w}: unknown classification {e.classification}")
        if e.zone == "vault" and e.classification != "special" and not e.replicated:
            E.err(f"{w}: vault entities must be classified special")
        if e.classification == "special" and e.zone not in ("vault", "dw"):
            E.err(f"{w}: special-category entity must live in the vault zone")
        if e.g("origin") not in ("appj", "ceda"):
            E.err(f"{w}: origin must be appj or ceda")
        if e.g("origin") == "appj" and (e.g("appj_name") or e.name) not in m.appj:
            E.err(f"{w}: origin appj but no Appendix J table '{e.g('appj_name') or e.name}'")
        ret = e.g("retention", e.domain.retention)
        if e.zone != "dw" and not ret:
            E.err(f"{w}: no retention series (entity or domain)")
        if ret and ret not in m.retention:
            E.err(f"{w}: unknown retention series {ret}")
        scope = str(e.g("scope", "none"))
        if not (scope in ("none",) or scope.startswith("owned") or scope.startswith("derived")):
            E.err(f"{w}: scope must be none, owned, owned? or derived: <rule>")
        if e.zone in ("registry", "ops", "vault", "records") and e.kind in ("master", "transaction", "event", "link") \
                and scope == "none" and not e.g("scope_note"):
            E.warn(f"{w}: tenant data with scope none (add scope or scope_note)")
        names = set()
        for c in e.columns:
            if c.name in names:
                E.err(f"{w}: duplicate column {c.name}")
            names.add(c.name)
            if not ident_ok(c.name):
                E.err(f"{w}: invalid column name {c.name}")
            if c.name in m.reserved:
                E.err(f"{w}: column '{c.name}' is a MySQL reserved word")
        for a in e.attrs:
            if a.type == "enum" and a.args:
                enums_used.add(a.args[0])
            if a.type in ("cl", "cls") and a.args:
                cls_used.add(a.args[0])
            if a.type == "money" and not e.col("currency") and not any(x.name.endswith("currency") for x in e.columns):
                E.err(f"{w}.{a.name}: money attribute but entity has no currency column")
            if a.type == "ref":
                tgt = a.args[0] if a.args else None
                if tgt != "*" and not m.resolve(tgt, e.zone):
                    E.err(f"{w}.{a.name}: ref to unknown entity '{tgt}'")
                if not a.name.endswith("_id") and not a.name.endswith("_by") and not a.name.endswith("_to") \
                        and a.name not in ("merged_into", "superseded_by"):
                    E.warn(f"{w}.{a.name}: ref column should end with _id")
            if a.type in ("point",) and "ix" in a.flags and not a.required:
                E.err(f"{w}.{a.name}: spatial index needs NOT NULL")
            if a.classification == "special" and e.zone not in ("vault", "dw") and a.type != "sealed":
                E.err(f"{w}.{a.name}: special-category field outside the vault must be sealed")
            for f in a.flags:
                if f not in {"uq", "ix", "pii", "lookup", "mask4", "soft", "public", "internal", "confidential",
                             "restricted", "special", "immutable", "derived", "signed"}:
                    E.err(f"{w}.{a.name}: unknown flag {f}")
        if e.partition:
            p = e.partition
            if p.get("type") not in ("range_month", "range_day", "range_year"):
                E.err(f"{w}: unknown partition type")
            if not e.col(p.get("column", "")):
                E.err(f"{w}: partition column missing")
            elif e.col(p["column"]).nullable:
                E.err(f"{w}: partition column must be NOT NULL")
            for u in [e.pk] + e.uniques:
                if p.get("column") not in u:
                    E.err(f"{w}: unique key {u} must include partition column {p.get('column')}")
        for keyset in [e.pk] + e.uniques + e.indexes:
            total = 16 if (e.tenant and keyset is not e.pk) else 0
            for cn in keyset:
                c = e.col(cn)
                if not c:
                    E.err(f"{w}: key column {cn} not found")
                    continue
                if c.attr and c.attr.type in NO_INDEX_TYPES and not cn.endswith("_hmac"):
                    E.err(f"{w}: cannot index {cn} ({c.attr.type})")
                total += mysql_key_bytes(c)
            if total > 3072:
                E.err(f"{w}: index {keyset} is {total} bytes (> 3072)")
        row = sum(mysql_key_bytes(c) for c in e.columns if not re.match(r"(TEXT|MEDIUM|JSON|BLOB|LONG)", c.mysql.upper()))
        if row > 65535:
            E.err(f"{w}: row size {row} bytes exceeds 65535")
        for ev in e.g("events", []) or []:
            events_used.add(ev)
            if ev not in m.events:
                E.err(f"{w}: event {ev} not in events.yaml")
        for p in e.g("pages", []) or []:
            if p not in m.pages:
                E.err(f"{w}: unknown page {p}")
            pages_cov[p].add(e.name)
        for r in e.g("reqs", []) or []:
            if r not in m.requirements:
                E.err(f"{w}: unknown requirement {r}")
            reqs_cov[r].add(e.name)
        if e.zone == "dw":
            for s in e.g("sources", []) or []:
                if not m.resolve(s):
                    E.err(f"{w}: warehouse source {s} unknown")
    for code in m.enums:
        if code not in enums_used:
            E.warn(f"enum {code} is not used")
    # events
    for name, ev in m.events.items():
        if not re.fullmatch(r"[A-Z0-9]+\.[A-Z0-9_]+", name):
            E.err(f"event {name}: name must be DOMAIN.PAST_TENSE")
        agg = ev.get("aggregate")
        if not agg or not m.resolve(agg):
            E.err(f"event {name}: unknown aggregate {agg}")
        if ev.get("producer") not in {d.module for d in m.domains} | {e.module for e in m.entities.values()}:
            E.err(f"event {name}: unknown producer module {ev.get('producer')}")
        for f, t in (ev.get("payload") or {}).items():
            base = t.split("(")[0].rstrip("!")
            if base not in m.types:
                E.err(f"event {name}.{f}: unknown type {t}")
        if ev.get("class") in ("restricted", "special"):
            E.err(f"event {name}: event payloads may not be restricted/special (IDs only)")
    # metrics
    for mt in m.metrics:
        for s in mt.get("sources", []):
            if not m.resolve(s):
                E.err(f"metric {mt['id']}: unknown source {s}")
        for r in mt.get("reqs", []):
            if r not in m.requirements:
                E.err(f"metric {mt['id']}: unknown requirement {r}")
            reqs_cov[r].add("metric:" + mt["id"])
    # page coverage — every MFS page must be served by at least one entity or metric
    for mt in m.metrics:
        for p in mt.get("pages", []):
            if p not in m.pages:
                E.err(f"metric {mt['id']}: unknown page {p}")
            pages_cov[p].add("metric:" + mt["id"])
    for p in m.pages:
        if p not in pages_cov:
            E.err(f"page {p} ({m.pages[p]['title']}) is not served by any entity or metric")
    # requirement coverage — every FR must be mapped to data or declared behavioural
    behavioural = {x["id"]: x for x in (m.trace.get("behavioural_requirements") or [])}
    for r in behavioural:
        if r not in m.requirements:
            E.err(f"traceability: unknown requirement {r}")
        if not m.resolve(behavioural[r].get("uses", "")) and behavioural[r].get("uses"):
            E.err(f"traceability: {r} uses unknown entity {behavioural[r]['uses']}")
    for r, rec in m.requirements.items():
        if r.startswith("FR-") and r not in reqs_cov and r not in behavioural:
            E.err(f"requirement {r} is not mapped to an entity, metric or behavioural note")
    # Appendix J coverage
    mapped = {}
    for e in m.entities.values():
        if e.g("origin") == "appj":
            mapped[e.g("appj_name") or e.name] = e.name
    for t in m.appj:
        if t not in mapped and t not in (m.trace.get("appj_superseded") or {}):
            E.err(f"Appendix J table {t} is not mapped to a CEDA entity")
    m.coverage = dict(pages=pages_cov, reqs=reqs_cov, behavioural=behavioural, appj=mapped)
    return E


# ----------------------------------------------------------------------------- DDL


def q(name):
    return f"`{name}`"


def sql_str(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def plan_keys(m: Model):
    """Decide foreign keys, soft references and supporting indexes for every entity."""
    referenced_tenant = set()
    for e in m.entities.values():
        e.fks, e.soft_refs = [], []
        for a in e.attrs:
            if a.type != "ref":
                continue
            tgt_name = a.args[0]
            col = a.name
            if tgt_name == "*":
                e.soft_refs.append((col, "*", "polymorphic reference"))
                continue
            tgt = m.resolve(tgt_name, e.zone)
            reason = None
            if "soft" in a.flags:
                reason = "declared soft"
            elif tgt.zone != e.zone:
                reason = f"cross-zone ({e.zone} → {tgt.zone})"
            elif e.partition or tgt.partition:
                reason = "partitioned table (InnoDB partitioned tables cannot hold foreign keys)"
            elif e.zone == "dw":
                reason = "warehouse (conformed by ETL)"
            elif tgt.g("pk"):
                reason = "target has a composite key"
            if reason:
                e.soft_refs.append((col, tgt.name, reason))
                continue
            if e.tenant and tgt.tenant:
                e.fks.append((["tenant_id", col], tgt, ["tenant_id", "id"]))
                referenced_tenant.add(tgt.key)
            else:
                e.fks.append(([col], tgt, ["id"]))
        # owning scope: enforced where the governance hierarchy lives (registry zone)
        if e.col("scope_node_id") and e.zone == "registry" and not e.partition and e.name != "scope_node":
            sn = m.resolve("scope_node", "registry")
            e.fks.append((["tenant_id", "scope_node_id"], sn, ["tenant_id", "id"]))
            referenced_tenant.add(sn.key)
        elif e.col("scope_node_id"):
            e.soft_refs.append(("scope_node_id", "scope_node", "owning scope (governance hierarchy is in the registry zone)" if e.zone != "registry" else "partitioned table"))
    for e in m.entities.values():
        e._extra_uniques = []
        if e.key in referenced_tenant:
            e._extra_uniques.append(["tenant_id", "id"])


def tenantise(e: Entity, cols: list) -> list:
    if e.tenant and cols and cols[0] != "tenant_id" and e.zone != "dw":
        return ["tenant_id"] + cols
    return list(cols)


def covered(existing: list, cols: list) -> bool:
    return any(ex[: len(cols)] == cols for ex in existing)


def partition_clause(e: Entity) -> str:
    p = e.partition
    col = p["column"]
    is_ts = e.col(col).mysql.startswith("DATETIME")
    start = _dt.date(2026, 9, 1)
    parts = []
    if p["type"] == "range_month":
        d = start
        for _ in range(12):
            nxt = (d.replace(day=28) + _dt.timedelta(days=4)).replace(day=1)
            parts.append((f"p{d:%Y%m}", nxt))
            d = nxt
    elif p["type"] == "range_day":
        d = _dt.date(2026, 10, 1)
        for _ in range(31):
            nxt = d + _dt.timedelta(days=1)
            parts.append((f"p{d:%Y%m%d}", nxt))
            d = nxt
    else:
        for y in range(2026, 2030):
            parts.append((f"p{y}", _dt.date(y + 1, 1, 1)))
    vals = []
    for pname, bound in parts:
        b = f"{bound:%Y-%m-%d}" + (" 00:00:00" if is_ts else "")
        vals.append(f"  PARTITION {pname} VALUES LESS THAN ('{b}')")
    vals.append("  PARTITION pmax VALUES LESS THAN (MAXVALUE)")
    return f"PARTITION BY RANGE COLUMNS ({q(col)}) (\n" + ",\n".join(vals) + "\n)"


def enum_check(m: Model, a: Attr, colname: str) -> str:
    vals = ", ".join(sql_str(v) for v in m.enums[a.args[0]]["values"])
    expr = f"{q(colname)} IN ({vals})"
    return expr if a.required else f"{q(colname)} IS NULL OR {expr}"


def unique_name(used: set, name: str) -> str:
    """Schema-wide unique constraint/trigger name (MySQL requires CHECK, FK and trigger names unique per schema)."""
    cand = short(name)
    if cand in used:
        cand = short(name[:50] + "_" + hashlib.sha1(name.encode()).hexdigest()[:6] + "x")
        i = 2
        while cand in used:
            cand = short(f"{name[:48]}_{i}")
            i += 1
    used.add(cand)
    return cand


def ddl_entity(m: Model, e: Entity, used: set | None = None) -> tuple[str, list, list]:
    used = used if used is not None else set()
    lines = []
    for c in e.columns:
        if c.generated:
            s = f"  {q(c.name)} {c.mysql} GENERATED ALWAYS AS ({c.generated}) STORED"
            if c.comment:
                s += f" COMMENT {sql_str(c.comment[:1024])}"
            lines.append(s)
            continue
        s = f"  {q(c.name)} {c.mysql}{'' if c.nullable else ' NOT NULL'}"
        if c.default is not None:
            s += f" DEFAULT {c.default}"
        if c.on_update:
            s += " ON UPDATE CURRENT_TIMESTAMP(6)"
        if c.comment:
            s += f" COMMENT {sql_str(c.comment[:1024])}"
        lines.append(s)
    lines.append(f"  PRIMARY KEY ({', '.join(q(c) for c in e.pk)})")
    keys_seen = [list(e.pk)]
    for u in e._extra_uniques:
        lines.append(f"  UNIQUE KEY {q(short('uq_' + e.name + '_' + '_'.join(u)))} ({', '.join(q(c) for c in u)})")
        keys_seen.append(u)
    for u in e.uniques:
        cols = tenantise(e, u)
        if e.g("global_unique") and u in (e.g("global_unique") or []):
            cols = list(u)
        lines.append(f"  UNIQUE KEY {q(short('uq_' + e.name + '_' + '_'.join(u)))} ({', '.join(q(c) for c in cols)})")
        keys_seen.append(cols)
    if e.col("scope_node_id") and e.tenant:
        ix = ["tenant_id", "scope_node_id"]
        if not covered(keys_seen, ix):
            lines.append(f"  KEY {q(short('ix_' + e.name + '_scope'))} ({', '.join(q(c) for c in ix)})")
            keys_seen.append(ix)
    for i in e.indexes:
        cols = tenantise(e, i)
        if covered(keys_seen, cols):
            continue
        col0 = e.col(i[0])
        if col0 and col0.mysql.startswith("POINT"):
            lines.append(f"  SPATIAL KEY {q(short('sx_' + e.name + '_' + i[0]))} ({q(i[0])})")
            continue
        lines.append(f"  KEY {q(short('ix_' + e.name + '_' + '_'.join(i)))} ({', '.join(q(c) for c in cols)})")
        keys_seen.append(cols)
    fk_stmts = []
    for cols, tgt, tcols in e.fks:
        if not covered(keys_seen, cols):
            lines.append(f"  KEY {q(short('ix_' + e.name + '_' + cols[-1]))} ({', '.join(q(c) for c in cols)})")
            keys_seen.append(cols)
        fk_stmts.append(
            f"ALTER TABLE {q(e.name)} ADD CONSTRAINT {q(unique_name(used, 'fk_' + e.name + '__' + cols[-1]))} FOREIGN KEY "
            f"({', '.join(q(c) for c in cols)}) REFERENCES {q(tgt.name)} ({', '.join(q(c) for c in tcols)});")
    if e.tenant and e.zone != "dw" and not covered(keys_seen, ["tenant_id"]):
        lines.append(f"  KEY {q(short('ix_' + e.name + '_tenant'))} ({q('tenant_id')})")
    checks = []
    for a in e.attrs:
        if a.type == "enum" and a.args and a.args[0] in m.enums:
            checks.append((a.name, enum_check(m, a, a.name)))
        if a.type in ("money",) and "signed" not in a.opts and a.opts.get("min") == "0":
            checks.append((a.name + "_min", f"{q(a.name + '_minor')} >= 0"))
    checks.extend(e.checks)
    for name, expr in checks:
        lines.append(f"  CONSTRAINT {q(unique_name(used, 'ck_' + e.name + '__' + name))} CHECK ({expr})")
    comment = f"[{e.domain.code}/{e.kind}/{e.classification}] {e.title}"
    ddl = f"CREATE TABLE {q(e.name)} (\n" + ",\n".join(lines) + \
          f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT={sql_str(comment[:2048])}"
    if e.partition:
        ddl += "\n" + partition_clause(e)
    ddl += ";"
    triggers = []
    if e.append_only:
        for op in ("UPDATE", "DELETE"):
            tn = unique_name(used, f"tr_{e.name}__no_{op.lower()}")
            triggers.append(
                f"CREATE TRIGGER {q(tn)} BEFORE {op} ON {q(e.name)} FOR EACH ROW "
                f"SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = {sql_str(f'{e.name} is append-only ({op} refused)')};")
    return ddl, fk_stmts, triggers


def gen_ddl(m: Model) -> dict:
    out = {}
    for zone in ZONE_ORDER:
        ents = [e for e in m.entities.values() if e.zone == zone]
        if not ents:
            continue
        z = m.meta["zones"][zone]
        hdr = [
            f"-- {m.meta['ceda']['id']} v{m.meta['ceda']['version']} — generated by ceda/tools/cedagen.py. DO NOT EDIT.",
            f"-- Zone: {zone} — {z['title']} (schema {z['schema']}, account {z['db_account']}).",
            f"-- {z['holds']}",
            f"-- Target: {m.meta['ceda']['database']}. Load into an empty schema; see ceda/CEDA.md §9.",
            f"-- Tables: {len(ents)}",
            "",
            "SET NAMES utf8mb4;",
            "SET time_zone = '+00:00';",
            "",
        ]
        body, fks, trg = [], [], []
        used: set = set()
        for d in m.domains:
            des = [e for e in d.entities if e.zone == zone]
            if not des:
                continue
            body.append(f"-- {'=' * 76}\n-- Domain {d.code} — {d.title}\n-- {'=' * 76}\n")
            for e in sorted(des, key=lambda x: x.name):
                ddl, f, t = ddl_entity(m, e, used)
                body.append(ddl + "\n")
                fks.extend(f)
                trg.extend(t)
        tail = []
        if fks:
            tail += ["", "-- " + "=" * 76, "-- Foreign keys (tenant-consistent: child (tenant_id, x_id) → parent (tenant_id, id))",
                     "-- " + "=" * 76] + fks
        if trg:
            tail += ["", "-- " + "=" * 76, "-- Append-only guards (second line of defence; the application account also lacks UPDATE/DELETE)",
                     "-- " + "=" * 76] + trg
        out[f"mysql/{ZONE_FILE[zone]}.sql"] = "\n".join(hdr + body + tail) + "\n"
    return out


# ----------------------------------------------------------------------------- documentation outputs


def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def entity_retention(e):
    return e.g("retention", e.domain.retention)


def gen_dictionary(m: Model) -> dict:
    out = {}
    idx = ["# CEDA data dictionary", "",
           f"Generated from the CEDA model ({m.meta['ceda']['id']} v{m.meta['ceda']['version']}). Do not edit by hand.", "",
           "| Domain | Code | Module (Django app) | Default zone | Entities |", "|---|---|---|---|---|"]
    for d in m.domains:
        fname = d.file.stem + ".md"
        idx.append(f"| [{d.title}]({fname}) | {d.code} | `{d.module}` | {d.zone} | {len(d.entities)} |")
        L = [f"# {d.code} — {d.title}", "", d.summary, "",
             f"Module (system of record): `{d.module}` · default zone: **{d.zone}** · default retention: "
             f"`{d.retention}`", "", "| Entity | Zone | Kind | Class | History | Title |", "|---|---|---|---|---|---|"]
        for e in d.entities:
            L.append(f"| [`{e.name}`](#{e.zone}-{e.name}) | {e.zone} | {e.kind} | {e.classification} | {e.history} | {md_escape(e.title)} |")
        L.append("")
        for e in d.entities:
            L.append(f'<a id="{e.zone}-{e.name}"></a>')
            L.append(f"## `{e.name}`" + (f" ({e.zone})" if e.replicated else ""))
            L.append("")
            L.append(md_escape(e.title) + ("  " if e.g("notes") else ""))
            if e.g("notes"):
                L.append("")
                L.append(" ".join(str(e.g("notes")).split()))
            L.append("")
            facts = [("Zone", e.zone), ("Kind", e.kind), ("Classification", e.classification),
                     ("History", e.history), ("Scope", e.g("scope", "none")), ("Module", f"`{e.module}`"),
                     ("Origin", e.g("origin") + (f" (Appendix J `{e.g('appj_name')}`)" if e.g("appj_name") else "")),
                     ("Retention", f"`{entity_retention(e)}`" if entity_retention(e) else "—")]
            if e.partition:
                facts.append(("Partitioning", f"{e.partition['type']} on `{e.partition['column']}`"))
            if e.g("reqs"):
                facts.append(("Requirements", ", ".join(e.g("reqs"))))
            if e.g("pages"):
                facts.append(("Pages", ", ".join(e.g("pages"))))
            if e.g("events"):
                facts.append(("Events", ", ".join(e.g("events"))))
            if e.g("sources"):
                facts.append(("Sources", ", ".join(f"`{s}`" for s in e.g("sources"))))
            L.append("| | |\n|---|---|")
            for k, v in facts:
                L.append(f"| {k} | {md_escape(str(v))} |")
            L.append("")
            L.append("| Column | MySQL type | Null | Class | Description |")
            L.append("|---|---|---|---|---|")
            for c in e.columns:
                cls = (c.attr.classification if c.attr else None) or ""
                ref = ""
                if c.attr and c.attr.type == "ref":
                    ref = f" → `{c.attr.args[0]}`"
                desc = c.comment
                if c.attr and c.attr.type == "enum" and c.attr.args[0] in m.enums:
                    desc = (desc + " · values: " + ", ".join(m.enums[c.attr.args[0]]["values"])).strip(" ·")
                if c.attr and c.attr.type in ("cl", "cls"):
                    desc = (desc + f" · code list `{c.attr.args[0]}`").strip(" ·")
                key = " **PK**" if c.name in e.pk else ""
                L.append(f"| `{c.name}`{key}{ref} | `{c.mysql.split(' COLLATE')[0].split(' CHARACTER')[0]}` | "
                         f"{'yes' if c.nullable else 'no'} | {cls} | {md_escape(desc)} |")
            if e.uniques or e.indexes:
                L.append("")
                for u in e.uniques:
                    L.append(f"- Unique: ({', '.join(tenantise(e, u))})")
                for i in e.indexes:
                    L.append(f"- Index: ({', '.join(tenantise(e, i))})")
            if e.soft_refs:
                L.append("")
                for col, tgt, why in e.soft_refs:
                    L.append(f"- Soft reference `{col}` → `{tgt}` — {why}")
            if e.checks:
                L.append("")
                for n, x in e.checks:
                    L.append(f"- Check `{n}`: `{x}`")
            L.append("")
        out[f"dictionary/{fname}"] = "\n".join(L) + "\n"
    out["dictionary/README.md"] = "\n".join(idx) + "\n"
    return out


def gen_erd(m: Model) -> dict:
    out = {}
    for d in m.domains:
        L = ["erDiagram"]
        names = {e.name for e in d.entities}
        stubs = set()
        rels = []
        for e in d.entities:
            for a in e.attrs:
                if a.type == "ref" and a.args[0] != "*":
                    tgt = a.args[0]
                    card = "||--o{" if not ("uq" in a.flags) else "||--o|"
                    rels.append(f'    {tgt} {card} {e.name} : "{a.name}"')
                    if tgt not in names:
                        stubs.add(tgt)
        for e in d.entities:
            L.append(f"    {e.name} {{")
            for c in e.columns:
                if c.standard and c.name not in ("id", "scope_node_id", "valid_from", "valid_to"):
                    continue
                t = re.sub(r"[^A-Za-z0-9]", "_", c.mysql.split(" ")[0])
                tag = " PK" if c.name in e.pk else (" FK" if c.attr and c.attr.type == "ref" else "")
                L.append(f"        {t} {c.name}{tag}")
            L.append("    }")
        for s in sorted(stubs):
            L.append(f"    {s} {{\n        BINARY_16 id PK\n    }}")
        L.extend(sorted(set(rels)))
        out[f"erd/{d.file.stem}.mmd"] = "\n".join(L) + "\n"
    return out


def json_type(m: Model, a: Attr | None, c: Column):
    if a is None:
        t = m.types.get(c.logical_type, {"json": {"type": "string"}})
        return dict(t["json"])
    t = m.types[a.type]
    js = json.loads(json.dumps(t["json"]))
    args = a.args or t.get("default_args", [])
    for k, v in list(js.items()):
        if isinstance(v, str) and "{0}" in v:
            v = v.format(*args)
            js[k] = int(v) if v.isdigit() else v
        if v == "{values}":
            js[k] = m.enums[args[0]]["values"]
    if a.type == "ref":
        js["x-ref"] = args[0]
    return js


def pascal(name):
    return "".join(p.capitalize() for p in name.split("_"))


def entity_schema(m: Model, e: Entity):
    props, required = OrderedDict(), []
    for c in e.columns:
        a = c.attr
        if a and a.type == "secret":
            if c.name != a.name + "_enc":
                continue
            js = json_type(m, a, c)
            js["description"] = a.doc or f"Encrypted {a.name}"
            js["x-classification"] = a.classification or "restricted"
            props[a.name] = js
            if a.required:
                required.append(a.name)
            continue
        js = json_type(m, a, c)
        if c.comment:
            js["description"] = c.comment
        if c.standard or c.generated:
            js["readOnly"] = True
        if a and a.classification:
            js["x-classification"] = a.classification
        if a and "pii" in a.flags:
            js["x-personal-data"] = True
        if c.nullable and not c.standard:
            js = {"anyOf": [js, {"type": "null"}]} if "anyOf" not in js else js
        props[c.name] = js
        if not c.nullable and not c.generated:
            required.append(c.name)
    return {
        "title": pascal(e.name), "description": e.title, "type": "object",
        "x-ceda": {"entity": e.name, "zone": e.zone, "domain": e.domain.code, "kind": e.kind,
                   "classification": e.classification, "history": e.history, "module": e.module},
        "properties": props, "required": required, "additionalProperties": False,
    }


def gen_schemas(m: Model) -> dict:
    out = {}
    components = OrderedDict()
    for d in m.domains:
        defs = OrderedDict()
        for e in d.entities:
            if e.zone == "dw":
                continue
            nm = pascal(e.name) + (pascal(e.zone) if e.replicated else "")
            s = entity_schema(m, e)
            defs[nm] = s
            components[nm] = s
        if defs:
            out[f"jsonschema/{d.file.stem}.schema.json"] = json.dumps({
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": f"https://schemas.syntegra.io/ceda/v1/{d.file.stem}.schema.json",
                "title": f"CEDA {d.code} — {d.title}", "$defs": defs}, indent=2, ensure_ascii=False) + "\n"
    out["openapi/components.yaml"] = yaml.safe_dump({
        "openapi": "3.1.0",
        "info": {"title": "Syntegra CEDA canonical component schemas", "version": m.meta["ceda"]["version"],
                 "description": "Generated from the CEDA model. API resources compose these schemas; fields marked "
                                "x-classification restricted/special are only serialised for callers whose grant "
                                "clearance covers them and who supplied X-Syntegra-Purpose."},
        "paths": {},
        "components": {"schemas": json.loads(json.dumps(components))}}, sort_keys=False, allow_unicode=True, width=120)
    return out


def gen_events(m: Model) -> dict:
    envelope = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://schemas.syntegra.io/ceda/v1/event-envelope.schema.json",
        "title": "Syntegra domain event envelope (CloudEvents 1.0 structured mode)",
        "type": "object",
        "required": ["specversion", "id", "source", "type", "time", "subject", "tenantid", "scopenodeid",
                     "actor", "schemaversion", "correlationid", "data"],
        "properties": {
            "specversion": {"const": "1.0"},
            "id": {"type": "string", "format": "uuid", "description": "UUID v7 of the outbox row"},
            "source": {"type": "string", "description": "/syntegra/{region}/{zone}/{module}"},
            "type": {"type": "string", "pattern": "^io\\.syntegra\\.[a-z0-9]+\\.[a-z0-9_]+\\.v[0-9]+$",
                     "description": "io.syntegra.<domain>.<event>.v<major>, e.g. io.syntegra.lrn.created.v1"},
            "time": {"type": "string", "format": "date-time"},
            "subject": {"type": "string", "description": "<aggregate>/<uuid>"},
            "datacontenttype": {"const": "application/json"},
            "tenantid": {"type": "string", "format": "uuid"},
            "scopenodeid": {"type": "string", "format": "uuid"},
            "actor": {"type": "string", "description": "user:<uuid> | agent:<uuid> for owner:<uuid> | system:<job>"},
            "schemaversion": {"type": "integer", "minimum": 1},
            "correlationid": {"type": "string"},
            "causationid": {"type": "string"},
            "classification": {"enum": ["public", "internal", "confidential"]},
            "data": {"type": "object"},
        },
        "additionalProperties": False,
    }
    payloads = OrderedDict()
    L = ["# CEDA domain event catalogue", "",
         "Generated from `ceda/model/events.yaml`. Events are named `<DOMAIN>.<PAST_TENSE_VERB>`, published through the "
         "transactional outbox of the producing zone, carried in the CloudEvents envelope "
         "(`envelope.schema.json`) and contain identifiers and minimal non-personal facts only (MFS Book 3 §16.2). "
         "Consumers fetch details through the API under their own permissions.", "",
         "| Event | Producer | Aggregate | Topic | Payload | Consumers | Trigger |", "|---|---|---|---|---|---|---|"]
    for name, ev in m.events.items():
        dom = name.split(".")[0].lower()
        topic = f"syn.{{region}}.{dom}.v{ev.get('version', 1)}"
        props, req = OrderedDict(), []
        for f, t in (ev.get("payload") or {}).items():
            base = t.rstrip("!")
            tname = base.split("(")[0]
            js = dict(m.types[tname]["json"])
            js = {k: v for k, v in js.items() if not (isinstance(v, str) and "{" in v)}
            if tname == "enum":
                arg = base[base.index("(") + 1:-1]
                if arg in m.enums:
                    js["enum"] = m.enums[arg]["values"]
            props[f] = js
            if t.endswith("!"):
                req.append(f)
        payloads[name] = {"type": "object", "description": ev.get("trigger", ""), "properties": props,
                          "required": req, "additionalProperties": False}
        pl = ", ".join(f"`{k}`" for k in (ev.get("payload") or {}))
        L.append(f"| `{name}` | `{ev['producer']}` | `{ev['aggregate']}` | `{topic}` | {pl} | "
                 f"{', '.join(ev.get('consumers', []))} | {md_escape(ev.get('trigger', ''))} |")
    out = {
        "events/envelope.schema.json": json.dumps(envelope, indent=2) + "\n",
        "events/payloads.schema.json": json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://schemas.syntegra.io/ceda/v1/event-payloads.schema.json",
            "title": "Syntegra domain event payloads", "$defs": payloads}, indent=2, ensure_ascii=False) + "\n",
        "events/catalog.md": "\n".join(L) + "\n",
    }
    return out


def gen_metrics(m: Model) -> dict:
    L = ["# CEDA semantic-layer metric catalogue", "",
         "Generated from `ceda/model/metrics.yaml`. Every indicator shown on a dashboard, return, briefing or assistant "
         "answer is defined here exactly once (MFS §7.3, FR-RPT-02, FR-RPT-04). Aggregates leaving the institution "
         "scope apply small-number suppression (cells < 10, FR-CMD-108).", ""]
    groups = defaultdict(list)
    for mt in m.metrics:
        groups[mt.get("group", "Other")].append(mt)
    for g, items in groups.items():
        L += [f"## {g}", "", "| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |",
              "|---|---|---|---|---|---|---|---|"]
        for mt in items:
            L.append(f"| `{mt['id']}` | {md_escape(mt['name'])} | {md_escape(mt.get('formula', ''))} | "
                     f"{md_escape(mt.get('grain', ''))} | {mt.get('refresh', '')} | {mt.get('direction', '')} | "
                     f"{', '.join('`' + s + '`' for s in mt.get('sources', []))} | {', '.join(mt.get('pages', []))} |")
        L.append("")
    return {"metrics/catalog.md": "\n".join(L) + "\n"}


def gen_trace(m: Model) -> dict:
    cov = m.coverage
    out = {}
    # pages
    L = ["# Page → data traceability", "",
         "Every one of the 260 pages in SYN-MFS-002 v2.4 is served by at least one CEDA entity or metric. "
         "Generated; do not edit.", "",
         "| Page | Title | Module | Phase | CEDA entities and metrics | MFS master objects |", "|---|---|---|---|---|---|"]
    for pid in sorted(m.pages):
        p = m.pages[pid]
        ents = sorted(cov["pages"].get(pid, []))
        L.append(f"| {pid} | {md_escape(p.get('title', ''))} | {md_escape(p.get('module', ''))} | {p.get('phase', '')} | "
                 f"{', '.join('`' + x + '`' for x in ents)} | {md_escape(', '.join(p.get('objects', [])))} |")
    out["traceability/pages.md"] = "\n".join(L) + "\n"
    # requirements
    fr = [r for r in m.requirements if r.startswith("FR-")]
    data_mapped = [r for r in fr if r in cov["reqs"]]
    L = ["# Requirement → data traceability", "",
         f"{len(fr)} functional requirements in SYN-MFS-002 v2.4: {len(data_mapped)} are realised by CEDA entities "
         f"or metrics; {len(fr) - len(data_mapped)} are behavioural (UI, workflow or engine behaviour over data "
         "already modelled) and name the entity they operate on. Generated; do not edit.", "",
         "| Requirement | Priority | Phase | Realised by | Text |", "|---|---|---|---|---|"]
    for r in sorted(fr):
        rec = m.requirements[r]
        if r in cov["reqs"]:
            by = ", ".join("`" + x + "`" for x in sorted(cov["reqs"][r]))
        else:
            b = cov["behavioural"].get(r, {})
            by = f"behavioural — uses `{b.get('uses', '—')}`: {md_escape(b.get('note', ''))}"
        L.append(f"| {r} | {rec.get('priority', '')} | {rec.get('phase', '')} | {by} | {md_escape(rec.get('text', ''))[:220]} |")
    out["traceability/requirements.md"] = "\n".join(L) + "\n"
    # appendix J
    sup = m.trace.get("appj_superseded") or {}
    L = ["# MFS Appendix J → CEDA mapping", "",
         "Each of the 174 tables in SYN-MFS-002 v2.4 Book 3 Appendix J and the CEDA entity that re-specifies it. "
         "Generated; do not edit.", "",
         "| Appendix J table | Domain (MFS) | CEDA entity | CEDA zone | Note |", "|---|---|---|---|---|"]
    for t, rec in m.appj.items():
        ent = cov["appj"].get(t)
        if ent:
            e = m.resolve(ent)
            zones = ", ".join(sorted({x.zone for x in m.by_name[ent]}))
            note = "renamed" if ent != t else ""
            L.append(f"| `{t}` | {rec['domain']} | `{ent}` | {zones} | {note} |")
        else:
            L.append(f"| `{t}` | {rec['domain']} | — | — | superseded: {md_escape(sup.get(t, ''))} |")
    out["traceability/appj_mapping.md"] = "\n".join(L) + "\n"
    return out


def gen_summary(m: Model) -> dict:
    ents = list(m.entities.values())
    s = {
        "ceda": m.meta["ceda"]["id"], "version": m.meta["ceda"]["version"],
        "domains": len(m.domains),
        "entities": len({e.name for e in ents}),
        "tables": len(ents),
        "tables_by_zone": {z: sum(1 for e in ents if e.zone == z) for z in ZONE_ORDER},
        "origin": {o: len({e.name for e in ents if e.g('origin') == o}) for o in ("appj", "ceda")},
        "columns": sum(len(e.columns) for e in ents),
        "foreign_keys": sum(len(e.fks) for e in ents),
        "soft_references": sum(len(e.soft_refs) for e in ents),
        "append_only_tables": sum(1 for e in ents if e.append_only),
        "partitioned_tables": sum(1 for e in ents if e.partition),
        "enums": len(m.enums), "code_lists": len(m.codelists), "events": len(m.events),
        "metrics": len(m.metrics), "retention_series": len(m.retention),
        "pages_covered": len(m.coverage["pages"]), "pages_total": len(m.pages),
        "fr_total": sum(1 for r in m.requirements if r.startswith("FR-")),
        "fr_data_mapped": sum(1 for r in m.requirements if r.startswith("FR-") and r in m.coverage["reqs"]),
        "appj_tables_mapped": len(m.coverage["appj"]), "appj_tables_total": len(m.appj),
    }
    return {"summary.json": json.dumps(s, indent=2) + "\n"}


def gen_seed(m: Model) -> dict:
    """Reference-data seed for code lists (jurisdiction packs), loaded into the registry zone."""
    L = ["-- Jurisdiction code lists — generated from ceda/model/reference/*.yaml. DO NOT EDIT.",
         "-- Load after 10_registry.sql. tenant_id is the state tenant; replace @tenant before loading.",
         "SET NAMES utf8mb4;", "SET @tenant = UUID_TO_BIN('00000000-0000-7000-8000-000000000001');", ""]
    for code, cl in m.codelists.items():
        L.append(f"-- {code}: {cl.get('title', '')}")
        L.append("INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES "
                 f"(UUID_TO_BIN(UUID()), @tenant, {sql_str(code)}, {sql_str(cl.get('title', ''))}, "
                 f"{sql_str(cl.get('pack') or 'core')}, {'TRUE' if cl.get('extensible') else 'FALSE'});")
        vals = []
        for i, v in enumerate(cl.get("values", [])):
            if isinstance(v, str):
                v = {"code": v, "label": v.replace("_", " ").capitalize()}
            vals.append(f"(UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = {sql_str(code)}), "
                        f"{sql_str(str(v['code']))}, {sql_str(str(v['label']))}, {i + 1}, '2026-01-01')")
        if vals:
            L.append("INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES\n  "
                     + ",\n  ".join(vals) + ";")
        L.append("")
    return {"mysql/15_registry_seed_code_lists.sql": "\n".join(L) + "\n"}


def generate_all(m: Model) -> dict:
    plan_keys(m)
    files = {}
    for fn in (gen_ddl, gen_seed, gen_dictionary, gen_erd, gen_schemas, gen_events, gen_metrics, gen_trace, gen_summary):
        files.update(fn(m))
    return files


def write_tree(files: dict, root: Path):
    if root.exists():
        shutil.rmtree(root)
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["validate", "generate", "check"])
    ap.add_argument("--warnings", action="store_true", help="print warnings")
    args = ap.parse_args(argv)
    m = Model()
    errs = validate(m)
    if args.warnings or errs.errors:
        for w in errs.warnings:
            print("warning:", w)
    for e in errs.errors:
        print("error:", e)
    if errs.errors:
        print(f"{len(errs.errors)} error(s), {len(errs.warnings)} warning(s)")
        return 1
    files = generate_all(m)
    if args.command == "validate":
        print(f"CEDA model valid: {len(m.domains)} domains, {len(m.entities)} tables, "
              f"{len(m.events)} events, {len(m.metrics)} metrics ({len(errs.warnings)} warnings)")
        return 0
    if args.command == "generate":
        write_tree(files, GENERATED)
        print(f"generated {len(files)} files under {GENERATED.relative_to(ROOT.parent)}")
        return 0
    # check
    stale = []
    existing = {str(p.relative_to(GENERATED)): p for p in GENERATED.rglob("*") if p.is_file()} if GENERATED.exists() else {}
    for rel, content in files.items():
        p = existing.pop(rel, None)
        if p is None or p.read_text(encoding="utf-8") != content:
            stale.append(rel)
    stale.extend(f"{rel} (orphan)" for rel in existing)
    if stale:
        print("generated artefacts are stale; run: python3 ceda/tools/cedagen.py generate")
        for s in stale[:50]:
            print("  ", s)
        return 1
    print("generated artefacts are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
