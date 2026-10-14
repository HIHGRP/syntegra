"""Federal unity colleges and special training institutions (CR-005, FR-FED-01..04).

Reads are scoped by the caller's grant in the Federal Institutions registry: a grant at a body sees its institutions,
a grant at a zone of the unity colleges sees that zone's colleges, a grant at the registry root sees all.
"""

from __future__ import annotations

import csv
import io
from typing import Any

from syntegra.core import authz, uow
from syntegra.core.errors import HardValidation
from syntegra.federal_institutions import reference as ref
from syntegra.federal_institutions.models import FederalBody, FederalBodyUnit, FederalInstitution
from syntegra.institutions.models import Institution
from syntegra.regulation.models import InstitutionRegulation


def directory(
    *, body: str | None = None, zone: str | None = None, institution_type: str | None = None
) -> dict[str, Any]:
    """FED-01: federal institutions by owning body, with type, zone and the bodies each depends on."""
    authz.require("federal_institutions:view")
    profiles = FederalInstitution.objects.in_scope()
    if zone:
        profiles = profiles.filter(geopolitical_zone=zone)
    if institution_type:
        profiles = profiles.filter(institution_type__startswith=institution_type)
    profiles = list(profiles)
    bodies = {b.id: b for b in FederalBody.objects.all()}
    if body:
        profiles = [p for p in profiles if bodies[p.body_id].code == body]
    units = {u.id: u for u in FederalBodyUnit.objects.filter(id__in=[p.unit_id for p in profiles])}
    insts = {i.id: i for i in Institution.objects.filter(id__in=[p.institution_id for p in profiles])}
    links: dict[Any, list[str]] = {}
    for iid, code, rel in InstitutionRegulation.objects.filter(
        institution_id__in=list(insts), valid_to__isnull=True
    ).values_list("institution_id", "body_code", "relationship"):
        links.setdefault(iid, []).append(f"{code} ({rel.replace('_', ' ')})")
    rows = [
        {
            "institution_id": p.institution_id,
            "name": insts[p.institution_id].name,
            "body": bodies[p.body_id].code,
            "body_name": bodies[p.body_id].name,
            "unit": units[p.unit_id].name,
            "institution_type": p.institution_type,
            "zone": p.geopolitical_zone,
            "state": (insts[p.institution_id].address or {}).get("state"),
            "town": (insts[p.institution_id].address or {}).get("town"),
            "gender_intake": p.gender_intake,
            "admission_basis": p.admission_basis,
            "depends_on": sorted(links.get(p.institution_id, [])),
            "data_status": p.data_status,
        }
        for p in profiles
        if p.institution_id in insts
    ]
    rows.sort(key=lambda r: (r["body"], r["institution_type"], r["state"] or "", r["name"]))
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["institution_type"]] = counts.get(r["institution_type"], 0) + 1
    return {
        "institutions": rows,
        "by_type": counts,
        "bodies": sorted({(b.code, b.name) for b in bodies.values()}),
        "unconfirmed": sum(1 for r in rows if r["data_status"] != "verified"),
    }


# --------------------------------------------------------------------------- reference import (FR-FED-04)
COLUMNS = (
    "body",
    "unit",
    "code",
    "name",
    "short_name",
    "institution_type",
    "category",
    "state",
    "town",
    "levels",
    "gender_intake",
    "day_boarding",
    "admission_basis",
    "data_status",
)


def import_csv(text: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Create or correct federal institutions from the Federal Ministry's (or a body's) official list.

    One row per institution; ``levels`` is space-separated education_level codes. Each row is validated before
    anything is written; the whole file is applied in one command, so a bad row changes nothing.
    """
    from syntegra.federal_institutions.registry import Seeded, upsert_institution
    from syntegra.platform.states import BY_CODE

    authz.require("federal_institutions:import")
    reader = csv.DictReader(io.StringIO(text))
    missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise HardValidation("FED-IMPORT-COLUMNS", "Columns missing", ", ".join(missing))
    bodies = {b.code: b for b in FederalBody.objects.all()}
    units = {(u.body_id, u.code) for u in FederalBodyUnit.objects.all()}
    types = {c for c, _ in FederalInstitution._meta.get_field("institution_type").choices or []}
    specs, errors = [], []
    for i, row in enumerate(reader, start=2):
        body = bodies.get((row["body"] or "").strip().upper())
        problems = []
        if body is None:
            problems.append("unknown body")
        elif (body.id, row["unit"].strip()) not in units:
            problems.append("unknown unit for the body")
        if row["state"].strip() not in BY_CODE:
            problems.append("state must be an ISO code such as NG-LA")
        if row["institution_type"].strip() not in types:
            problems.append("unknown institution_type")
        if not row["code"].strip() or not row["name"].strip():
            problems.append("code and name are required")
        if problems:
            errors.append({"row": i, "code": row.get("code"), "problems": problems})
            continue
        specs.append(
            ref.Inst(
                body=body.code,  # type: ignore[union-attr]
                unit=row["unit"].strip(),
                code=row["code"].strip().upper(),
                name=row["name"].strip(),
                short_name=(row["short_name"] or row["code"]).strip(),
                institution_type=row["institution_type"].strip(),
                category=row["category"].strip(),
                state=row["state"].strip(),
                town=row["town"].strip(),
                levels=tuple(row["levels"].split()),
                gender=row["gender_intake"].strip() or None,
                boarding=row["day_boarding"].strip() or None,
                admission=row["admission_basis"].strip() or None,
                status=row["data_status"].strip() or "to_confirm",
            )
        )
    if errors or dry_run:
        return {"rows": len(specs) + len(errors), "valid": len(specs), "errors": errors, "applied": False}
    n = Seeded()
    with uow.command("registry", None, action="import", record_kind="federal_institution") as cmd:
        for spec in specs:
            upsert_institution(cmd, n, spec, source="import")
        cmd.note("imported", None, n.__dict__)
    return {
        "rows": len(specs),
        "valid": len(specs),
        "errors": [],
        "applied": True,
        "added": n.institutions,
        "updated": n.updated,
        "regulatory_links": n.regulatory_links,
    }


__all__ = ["COLUMNS", "directory", "import_csv"]
