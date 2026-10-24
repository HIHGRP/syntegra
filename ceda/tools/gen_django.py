#!/usr/bin/env python3
"""gen_django — generate the Django ORM layer of the Syntegra application from the CEDA model.

The CEDA model is the single source of truth (ceda/model). This tool writes, for every Django app
(= CEDA module), a ``models.py`` whose classes map exactly onto the tables in ceda/generated/mysql:

  * ``managed = False`` — the schema is created from the CEDA DDL by the ``syntegra.schema`` migrations,
    never by Django's autodetector, so CHECKs, generated columns, tenant-consistent keys, partitions and
    triggers stay exactly as CEDA specifies;
  * one model per entity (replicated cross-cutting entities get one model used against each zone alias);
  * same-zone, non-partitioned references become ``ForeignKey(db_constraint=False)`` (MySQL enforces the
    real, tenant-consistent key); every other reference is a ``UUID7Field`` soft reference;
  * CEDA metadata (zone, classification, history, scope, field classifications, PII flags) is attached to
    each model class and drives routing, scoping, serialisation and trimming at run time.

It also writes runtime catalogues (events, metrics, enums, code lists) to ``syntegra/core/catalog/``.

Usage:  python3 ceda/tools/gen_django.py generate | check
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cedagen

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src" / "syntegra"
HEADER = '''"""GENERATED from the CEDA model by ceda/tools/gen_django.py — DO NOT EDIT.

Module ``{module}`` — {titles}.
Tables are created from ceda/generated/mysql (``managed = False``); put behaviour in the module's
domain/ and services/ packages, never here.
"""
# ruff: noqa
from __future__ import annotations

from django.db import models

from syntegra.core import fields as cf
from syntegra.core.ids import uuid7
from syntegra.core.managers import TenantScopedManager
from syntegra.core.models_base import CedaModel
'''

SIMPLE = {
    "name": ("models.CharField", {"max_length": 200}),
    "title": ("models.CharField", {"max_length": 300}),
    "email": ("models.CharField", {"max_length": 254}),
    "phone": ("models.CharField", {"max_length": 16}),
    "url": ("models.CharField", {"max_length": 2048}),
    "lang": ("models.CharField", {"max_length": 35}),
    "country": ("models.CharField", {"max_length": 2}),
    "subdivision": ("models.CharField", {"max_length": 6}),
    "currency": ("models.CharField", {"max_length": 3}),
    "glid": ("models.CharField", {"max_length": 16}),
    "object_key": ("models.CharField", {"max_length": 1024}),
    "mime": ("models.CharField", {"max_length": 127}),
    "semver": ("models.CharField", {"max_length": 32}),
    "path": ("models.CharField", {"max_length": 512}),
    "text": ("models.TextField", {}),
    "longtext": ("models.TextField", {}),
    "date": ("models.DateField", {}),
    "ts": ("models.DateTimeField", {}),
    "time": ("models.TimeField", {}),
    "bool": ("models.BooleanField", {}),
    "int": ("models.IntegerField", {}),
    "int_u": ("models.PositiveIntegerField", {}),
    "smallint": ("models.SmallIntegerField", {}),
    "bigint": ("models.BigIntegerField", {}),
    "money": ("models.BigIntegerField", {}),
    "minutes": ("models.IntegerField", {}),
    "pct": ("models.DecimalField", {"max_digits": 6, "decimal_places": 3}),
    "ratio": ("models.DecimalField", {"max_digits": 7, "decimal_places": 6}),
    "score": ("models.DecimalField", {"max_digits": 7, "decimal_places": 3}),
    "json": ("models.JSONField", {}),
    "cls": ("models.JSONField", {}),
    "hash": ("models.BinaryField", {}),
    "hmac": ("models.BinaryField", {}),
    "sealed": ("models.BinaryField", {}),
    "secret": ("models.BinaryField", {}),
    "uuid": ("cf.UUID7Field", {}),
    "ip": ("cf.PackedIPField", {}),
    "point": ("cf.PointField", {}),
}


def pascal(name: str) -> str:
    return "".join(p.capitalize() for p in name.split("_"))


def pyrepr(v):
    return repr(v)


def kw(d: dict) -> str:
    return ", ".join(f"{k}={pyrepr(v) if not isinstance(v, Raw) else v.s}" for k, v in d.items())


class Raw:
    def __init__(self, s):
        self.s = s


def _pages() -> list[dict]:
    """MFS page catalogue (ceda/sources/mfs_pages.yaml) reduced to what the page registry needs."""
    src = yaml.safe_load((REPO / "ceda" / "sources" / "mfs_pages.yaml").read_text(encoding="utf-8"))["pages"]
    for cr_path in sorted((REPO / "ceda" / "model" / "change_requests").glob("CR-*.yaml")):
        cr = yaml.safe_load(cr_path.read_text(encoding="utf-8"))
        src += [dict(pg, change_request=cr["id"]) for pg in cr.get("pages", [])]
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "module": p["module"],
            "pattern": p.get("pattern"),
            "route": p.get("route"),
            "classification": (p.get("classification") or "Internal").lower(),
            "phase": p.get("phase"),
            "roles": [str(r).split(" ", 1)[0] for r in p.get("roles") or []],
            "purpose": p.get("purpose"),
            "change_request": p.get("change_request"),
        }
        for p in src
    ]


# Relation names that would shadow django.db.models.Model attributes stay plain UUID columns.
DJANGO_MODEL_ATTRS = {
    "check",
    "clean",
    "save",
    "delete",
    "objects",
    "pk",
    "full_clean",
    "validate_unique",
    "refresh_from_db",
    "serializable_value",
    "prepare_database_save",
    "unscoped",
}


def field_for(m: cedagen.Model, e: cedagen.Entity, c: cedagen.Column, fk_cols: dict, names: set) -> tuple[str, str]:
    """Return (python attribute name, field constructor source)."""
    a = c.attr
    opts: dict = {}
    if c.nullable:
        opts["null"] = True
        opts["blank"] = True
    # standard columns
    if c.standard:
        if c.name == "id":
            if e.g("pk") or e.partition:  # composite primary key declared on the model
                return "id", "cf.UUID7Field(default=uuid7)"
            return "id", "cf.UUID7Field(primary_key=True, default=uuid7)"
        if c.name in ("tenant_id", "scope_node_id", "created_by", "updated_by"):
            return c.name, f"cf.UUID7Field({kw(opts)})"
        if c.name == "created_at":
            return c.name, "models.DateTimeField(default=cf.utcnow)"
        if c.name == "updated_at":
            return c.name, "models.DateTimeField(default=cf.utcnow)"
        if c.name == "row_version":
            return c.name, "models.PositiveIntegerField(default=1)"
        if c.name in ("valid_from", "valid_to"):
            return c.name, f"models.DateField({kw(opts)})"
        if c.name == "loaded_at":
            return c.name, "models.DateTimeField(default=cf.utcnow)"
        if c.name == "load_batch_id":
            return c.name, "models.BigIntegerField()"
    if c.name in fk_cols:
        tgt = fk_cols[c.name]
        fname = c.name[:-3] if c.name.endswith("_id") else c.name
        if fname not in DJANGO_MODEL_ATTRS and (fname not in names or fname == c.name):
            ref = f'"{tgt.module}.{pascal(tgt.name)}"'
            o = {
                "on_delete": Raw("models.DO_NOTHING"),
                "db_constraint": False,
                "related_name": "+",
                "db_column": c.name,
                **opts,
            }
            return fname, f"models.ForeignKey({ref}, {kw(o)})"
    lt = c.logical_type
    if lt in ("enum",):
        vals = m.enums[a.args[0]]["values"]
        o = {"max_length": 32, "choices": Raw(repr([(v, v.replace("_", " ").capitalize()) for v in vals])), **opts}
        cls = "models.CharField"
    elif lt in ("cl",):
        cls, o = "models.CharField", {"max_length": 32, **opts}
    elif lt in ("code",):
        n = int((a.args or [32])[0]) if a and a.type == "code" else 4 if c.name.endswith("_last4") else 32
        cls, o = "models.CharField", {"max_length": n, **opts}
    elif lt == "str":
        cls, o = "models.CharField", {"max_length": int(a.args[0]), **opts}
    elif lt == "dec":
        cls, o = "models.DecimalField", {"max_digits": int(a.args[0]), "decimal_places": int(a.args[1]), **opts}
    elif lt == "ref":
        cls, o = "cf.UUID7Field", dict(opts)
    elif lt == "bytes":
        cls, o = "models.BinaryField", dict(opts)
    elif lt in SIMPLE:
        cls, base = SIMPLE[lt]
        o = {**base, **opts}
    else:
        raise SystemExit(f"no Django mapping for {e.name}.{c.name} ({lt})")
    if a and "default" in a.opts and not c.generated:
        d = a.opts["default"]
        if lt == "bool":
            o["default"] = d.lower() == "true"
        elif lt in ("int", "int_u", "smallint", "bigint", "money", "minutes"):
            o["default"] = int(d)
        else:
            o["default"] = d
    if c.comment:
        o["help_text"] = c.comment[:300]
    if c.generated:
        o.pop("default", None)
        o["null"] = True
        o["editable"] = False
        return c.name, f"cf.generated({cls}({kw(o)}))"
    return c.name, f"{cls}({kw(o)})"


def ceda_meta(m: cedagen.Model, e: cedagen.Entity, zones: list[str]) -> list[str]:
    fields = {}
    for c in e.columns:
        a = c.attr
        info = {"type": c.logical_type}
        if a is not None:
            if a.classification:
                info["class"] = a.classification
            if "pii" in a.flags:
                info["pii"] = True
            if a.type == "ref":
                info["ref"] = a.args[0]
            if a.type == "secret":
                info["secret_of"] = a.name
            if a.type == "enum":
                info["enum"] = a.args[0]
            if a.type in ("cl", "cls"):
                info["code_list"] = a.args[0]
        if c.generated:
            info["generated"] = True
        if c.standard:
            info["standard"] = True
        fields[c.name] = info
    scope = str(e.g("scope", "none"))
    lines = [
        f"    ceda_entity = {e.name!r}",
        f"    ceda_zones = {tuple(zones)!r}",
        f"    ceda_domain = {e.domain.code!r}",
        f"    ceda_kind = {e.kind!r}",
        f"    ceda_class = {e.classification!r}",
        f"    ceda_history = {e.history!r}",
        f"    ceda_scope = {scope!r}",
        f"    ceda_append_only = {e.append_only!r}",
        f"    ceda_partition = {e.partition!r}",
        f"    ceda_retention = {e.g('retention', e.domain.retention)!r}",
        f"    ceda_fields = {fields!r}",
    ]
    return lines


def build(m: cedagen.Model) -> dict[str, str]:
    cedagen.plan_keys(m)
    by_module: dict[str, list] = defaultdict(list)
    seen = set()
    titles = defaultdict(set)
    for d in m.domains:
        for e in d.entities:
            if e.name in seen:
                continue
            seen.add(e.name)
            zones = [x.zone for x in m.by_name[e.name]]
            by_module[e.module].append((e, zones))
            titles[e.module].add(d.title.split(" — ")[0])
    out = {}
    for module, ents in sorted(by_module.items()):
        src = [HEADER.format(module=module, titles="; ".join(sorted(titles[module])))]
        for e, zones in sorted(ents, key=lambda x: x[0].name):
            fk_cols = {}
            for cols, tgt, _ in e.fks:
                col = cols[-1]
                if col == "scope_node_id":
                    continue
                fk_cols[col] = tgt
            colnames = {c.name for c in e.columns}
            src.append("")
            src.append("")
            src.append(f"class {pascal(e.name)}(CedaModel):")
            src.append(f'    """{e.title.replace(chr(34), chr(39))}"""')
            src.append("")
            src.extend(ceda_meta(m, e, zones))
            src.append("")
            used = set()
            single_pk = e.g("pk")[0] if e.g("pk") and len(e.g("pk")) == 1 else None
            for c in e.columns:
                name, ctor = field_for(m, e, c, fk_cols, colnames - {c.name})
                if c.name == single_pk:
                    ctor = ctor[:-1] + (", " if not ctor.endswith("()") else "") + "primary_key=True)"
                if name in used:
                    raise SystemExit(f"duplicate field name {e.name}.{name}")
                used.add(name)
                src.append(f"    {name} = {ctor}")
            if e.g("pk") and len(e.g("pk")) > 1:
                src.append(f"    pk = models.CompositePrimaryKey({', '.join(repr(x) for x in e.g('pk'))})")
            elif e.partition:
                src.append(f"    pk = models.CompositePrimaryKey('id', {e.partition['column']!r})")
            src.append("")
            tenant = m.meta["zones"][zones[0]]["tenant_column"]
            if tenant:
                src.append("    objects = TenantScopedManager()")
                src.append("    unscoped = models.Manager()")
            else:
                src.append("    objects = models.Manager()")
                src.append("    unscoped = models.Manager()")
            src.append("")
            src.append("    class Meta:")
            src.append("        managed = False")
            src.append(f"        db_table = {e.name!r}")
            src.append(f"        app_label = {module!r}")
            src.append("        base_manager_name = 'unscoped'")
            src.append(f"        verbose_name = {e.title[:80]!r}")
        out[f"{module}/models.py"] = "\n".join(src) + "\n"
    # runtime catalogues
    catalog = {
        "events": m.events,
        "metrics": m.metrics,
        "enums": {k: v["values"] for k, v in m.enums.items()},
        "code_lists": {
            k: [x if isinstance(x, str) else x["code"] for x in v.get("values", [])] for k, v in m.codelists.items()
        },
        "retention": m.retention,
        "zones": {
            k: {kk: vv for kk, vv in v.items() if kk in ("title", "schema", "tenant_column")}
            for k, v in m.meta["zones"].items()
        },
        "ceda": m.meta["ceda"],
        "pages": _pages(),
    }
    out["core/catalog/ceda_catalog.json"] = (
        json.dumps(catalog, indent=1, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    )
    return out


def main(argv=None) -> int:
    cmd = (argv or sys.argv[1:] or ["generate"])[0]
    m = cedagen.Model()
    errs = cedagen.validate(m)
    if errs.errors:
        print("CEDA model invalid; run cedagen validate")
        return 1
    files = build(m)
    stale = []
    for rel, content in files.items():
        p = SRC / rel
        if cmd == "generate":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        elif not p.exists() or p.read_text(encoding="utf-8") != content:
            stale.append(rel)
    if cmd == "check":
        if stale:
            print("Django models are stale; run: python3 ceda/tools/gen_django.py generate")
            print("\n".join("  " + s for s in stale))
            return 1
        print("Django models are up to date")
        return 0
    print(f"generated {len(files)} files under src/syntegra")
    return 0


if __name__ == "__main__":
    sys.exit(main())
