"""Extract the page catalogue and requirement register from the MFS markdown.

Usage: python3 -I extract_mfs.py <mfs.md> <out_dir>
Writes mfs_pages.yaml and mfs_requirements.yaml.
"""
import re
import sys
from pathlib import Path

import yaml

src = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
out = Path(sys.argv[2])


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("\\|", "|").replace("\\<", "<").replace("\\>", ">")
    s = s.replace("\\[", "[").replace("\\]", "]").replace("\\_", "_").replace("\\*", "*").replace("\\-", "-")
    s = s.replace("**", "").replace("\\#", "#").replace("\\'", "'")
    return re.sub(r"\s+", " ", s).strip()


def cells(line: str):
    line = line.strip()
    if not line.startswith("|"):
        return None
    parts = re.split(r"(?<!\\)\|", line)[1:-1]
    return [clean(p) for p in parts]


def is_sep(c):
    return c and all(re.fullmatch(r":?-{2,}:?", x or "--") for x in c)


# ---------------------------------------------------------------- page inventory
inventory = {}
book2_start = next(i for i, l in enumerate(src) if l.startswith("# 24. Page inventory"))
for line in src[book2_start: book2_start + 220]:
    c = cells(line)
    if c and len(c) >= 7 and re.fullmatch(r"[A-Z0-9]{2,4}-\d{2,3}", c[0]):
        inventory[c[0]] = dict(id=c[0], title=c[1], module=c[2], pattern=c[3], route=c[4],
                               classification=c[5], phase="P" + c[6] if c[6].isdigit() else c[6])
apx_e = next(i for i, l in enumerate(src) if l.startswith("# Appendix E"))
for line in src[apx_e: apx_e + 90]:
    c = cells(line)
    if c and len(c) >= 6 and re.fullmatch(r"[A-Z0-9]{2,4}-\d{2,3}", c[0]):
        inventory[c[0]] = dict(id=c[0], title=c[1], module=c[2], pattern=c[3], roles=c[4], phase=c[5])

# ---------------------------------------------------------------- page specifications
head_re = re.compile(r"^###\s+(?:[\d.]+\s+)?([A-Z0-9]{2,4}-\d{2,3})\s+·\s+(.*)$")
starts = [(i, head_re.match(l)) for i, l in enumerate(src)]
starts = [(i, m) for i, m in starts if m]
for n, (i, m) in enumerate(starts):
    pid = m.group(1)
    end = starts[n + 1][0] if n + 1 < len(starts) else len(src)
    block = src[i:end]
    page = inventory.setdefault(pid, {"id": pid, "title": clean(m.group(2))})
    page["title"] = clean(m.group(2))
    section = None
    fields = []
    for line in block[1:]:
        if line.startswith("#### ") or line.startswith("**") and line.rstrip().endswith("**"):
            section = clean(line.lstrip("#").strip())
            continue
        if line.startswith("**Purpose.**"):
            page["purpose"] = clean(line.replace("**Purpose.**", ""))
            continue
        c = cells(line)
        if not c or is_sep(c):
            continue
        key = c[0].lower()
        if len(c) == 2:
            mapping = {
                "route": "route", "pattern": "pattern", "roles": "roles", "module": "module",
                "data classification": "classification", "phase": "phase", "source": "source",
                "master records / objects": "objects", "api calls": "api_calls",
                "events emitted": "events",
            }
            if key in mapping and c[1]:
                page[mapping[key]] = c[1]
        if section and section.lower().startswith("fields") and len(c) >= 4 and key not in ("field",):
            fields.append(dict(label=c[0], type=c[1], required=c[2].lower().startswith("y"),
                               rule=c[3] if c[3] not in ("—", "-") else None))
    if fields:
        page["fields"] = fields

for p in inventory.values():
    for k in ("api_calls", "events", "objects"):
        if k in p:
            vals = [v.strip() for v in re.split(r",\s*(?=(?:GET|POST|PUT|PATCH|DELETE|[A-Z][A-Za-z0-9 /&'’-]*|[A-Z]+\.[A-Z_]+))", p[k])]
            vals = [v for v in vals if v and v not in ("—", "-")]
            p[k] = vals
    if isinstance(p.get("roles"), str):
        p["roles"] = [r.strip() for r in re.split(r",\s*", p["roles"]) if r.strip()]

pages = sorted(inventory.values(), key=lambda p: p["id"])

# ---------------------------------------------------------------- requirements
req_re = re.compile(r"^(FR|NFR)-[A-Z0-9]+-\d{2,3}$")
reqs = {}
for idx, line in enumerate(src):
    c = cells(line)
    if not c or not req_re.match(c[0]):
        continue
    rid = c[0]
    rec = reqs.get(rid, {"id": rid})
    rec["text"] = c[1]
    rest = c[2:]
    for v in rest:
        if v in ("SHALL", "SHOULD", "MAY"):
            rec["priority"] = v
        elif re.fullmatch(r"P\d(?:[–-]P?\d)?(?: / P\d)?|Ongoing", v):
            rec["phase"] = v
    if rid.startswith("FR-"):
        rec["module"] = rid.split("-")[1]
    else:
        rec["area"] = rid.split("-")[1]
    reqs[rid] = rec

requirements = sorted(reqs.values(), key=lambda r: r["id"])

hdr = ("# Extracted from SYN-MFS-002 v2.4 (consolidated single volume) by ceda tooling.\n"
       "# Do not edit by hand; regenerate from the specification.\n")
(out / "mfs_pages.yaml").write_text(hdr + yaml.safe_dump({"pages": pages}, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
(out / "mfs_requirements.yaml").write_text(hdr + yaml.safe_dump({"requirements": requirements}, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
print(len(pages), "pages;", len(requirements), "requirements;",
      sum(1 for r in requirements if r["id"].startswith("FR-")), "FR")
