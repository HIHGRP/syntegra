"""Education watchdogs and every institution's regulatory profile (CR-005, FR-REG-01..04).

The directory of bodies and their dependencies is national (platform zone). An institution's links live in its own
registry: ``apply_rules`` derives them from the institution's category, ownership and levels (``reference.profile``)
when the institution is registered or seeded; ``set_link`` and ``end_link`` adjust one institution; ``profile``
shows the links with the gaps that remain (FR-REG-04).
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections import defaultdict
from typing import Any

from django.db import transaction

from syntegra.core import authz, context, uow
from syntegra.core.errors import HardValidation, NotFound
from syntegra.institutions.models import Institution
from syntegra.regulation import reference as ref
from syntegra.regulation.models import BodyDependency, InstitutionRegulation, RegulatoryBody

PLATFORM = "platform"
# security agencies → supervising ministry in the directory
AGENCY_MINISTRY = {
    "DHQ": "FMOD",
    "NA": "FMOD",
    "NN": "FMOD",
    "NAF": "FMOD",
    "NPF": "FMPA",
    "NSCDC": "FMI",
    "NCOS": "FMI",
    "NIS": "FMI",
    "FFS": "FMI",
    "NCS": "FMF",
}


# --------------------------------------------------------------------------- national directory
def seed_directory() -> tuple[int, int]:
    """Load or complete the bodies and their dependencies (idempotent). Returns (bodies, dependencies) added."""
    nb = nd = 0
    with transaction.atomic(using=PLATFORM):
        have = {b.code: b for b in RegulatoryBody.objects.using(PLATFORM).all()}
        for b in [*ref.BODIES, *(x for bodies_ in ref.STATE_BODIES.values() for x in bodies_)]:
            if b.code not in have:
                have[b.code] = RegulatoryBody(
                    code=b.code,
                    name=b.name,
                    body_type=b.body_type,
                    statutory_basis=b.statutory_basis,
                    jurisdiction=b.jurisdiction,
                    levels=list(b.levels) or None,
                    functions=b.functions,
                    data_status=b.status,
                    status="active",
                )
                have[b.code].save(using=PLATFORM)
                nb += 1
        deps = set(BodyDependency.objects.using(PLATFORM).values_list("from_body_id", "to_body_id", "dependency_type"))
        for frm, to, kind, note, status in [*ref.DEPENDENCIES, *ref.STATE_DEPENDENCIES]:
            key = (have[frm].id, have[to].id, kind)
            if key not in deps:
                BodyDependency(
                    from_body_id=key[0], to_body_id=key[1], dependency_type=kind, note=note, data_status=status
                ).save(using=PLATFORM)
                deps.add(key)
                nd += 1
    return nb, nd


def bodies() -> dict[str, RegulatoryBody]:
    return {b.code: b for b in RegulatoryBody.objects.using(PLATFORM).filter(status="active")}


def directory() -> dict[str, Any]:
    """REG-01 (public): bodies by type with what each depends on and who depends on it."""
    by_id = {b.id: b for b in RegulatoryBody.objects.using(PLATFORM).filter(status="active").order_by("name")}
    deps = list(BodyDependency.objects.using(PLATFORM).all())
    rows = []
    for b in by_id.values():
        rows.append(
            {
                "id": b.id,
                "code": b.code,
                "name": b.name,
                "body_type": b.body_type,
                "jurisdiction": b.jurisdiction,
                "statutory_basis": b.statutory_basis,
                "functions": b.functions,
                "levels": b.levels or [],
                "data_status": b.data_status,
                "depends_on": [
                    {"type": d.dependency_type, "code": by_id[d.to_body_id].code, "note": d.note}
                    for d in deps
                    if d.from_body_id == b.id and d.to_body_id in by_id
                ],
                "depended_on_by": [
                    {"type": d.dependency_type, "code": by_id[d.from_body_id].code}
                    for d in deps
                    if d.to_body_id == b.id and d.from_body_id in by_id
                ],
            }
        )
    types: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        types.setdefault(r["body_type"], []).append(r)
    return {"bodies": rows, "by_type": types, "dependencies": len(deps)}


# --------------------------------------------------------------------------- institution profiles
def _merge(links: list[ref.Link]) -> list[ref.Link]:
    """One link per body × relationship (the unique key), with what it covers combined."""
    merged: dict[tuple[str, str], ref.Link] = {}
    for link in links:
        key = (link.body, link.relationship)
        if key in merged:
            m = merged[key]
            merged[key] = ref.Link(
                m.body,
                m.relationship,
                f"{m.covers}; {link.covers}",
                tuple(dict.fromkeys(m.levels + link.levels)),
                m.mandatory or link.mandatory,
            )
        else:
            merged[key] = link
    return list(merged.values())


def apply_rules(
    cmd: uow.Command,
    inst: Institution,
    *,
    owner_ministry: str | None = None,
    accreditation: tuple[str, ...] | list[str] = (),
    unity_college: bool = False,
    technical: bool = False,
    data_status: str = "illustrative",
) -> int:
    """Create the rule-derived links an institution does not have yet (inside the caller's command)."""
    directory_ = bodies()
    if not directory_:
        return 0  # directory not loaded on this platform yet
    links = _expected(
        cmd,
        inst,
        owner_ministry=owner_ministry,
        accreditation=accreditation,
        unity_college=unity_college,
        technical=technical,
    )
    have = set(
        InstitutionRegulation.unscoped.using(cmd.alias)
        .filter(tenant_id=cmd.ctx.state_tenant_id, institution_id=inst.id, valid_to__isnull=True)
        .values_list("body_code", "relationship")
    )
    n = 0
    for link in links:
        body = directory_.get(link.body)
        if body is None or (link.body, link.relationship) in have:
            continue
        row = cmd.add(
            InstitutionRegulation(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                regulatory_body_id=body.id,
                body_code=body.code,
                relationship=link.relationship,
                covers=link.covers[:200],
                levels=list(link.levels) or None,
                is_mandatory=link.mandatory,
                source="rule",
                data_status=data_status,
                valid_from=dt.date.today(),
            )
        )
        cmd.emit(
            "REG.PROFILE_CHANGED",
            aggregate_id=row.id,
            aggregate_kind="institution_regulation",
            scope_node_id=inst.scope_node_id,
            payload={"institution_id": inst.id, "body_code": body.code, "relationship": link.relationship},
        )
        n += 1
    return n


def _expected(
    cmd: uow.Command,
    inst: Institution,
    *,
    owner_ministry: str | None = None,
    accreditation: tuple[str, ...] | list[str] = (),
    unity_college: bool = False,
    technical: bool = False,
) -> list[ref.Link]:
    """The rule-derived links an institution should have, localised to its state's own bodies."""
    from syntegra.core.tenancy import tenant_code_for

    code = tenant_code_for(cmd.ctx.state_tenant_id)
    return _merge(
        ref.localise(
            ref.profile(
                category=inst.category,
                ownership=inst.ownership,
                levels=list(inst.levels or []),
                owner_ministry=owner_ministry,
                accreditation=accreditation,
                unity_college=unity_college,
                technical=technical or inst.category == "technical_college",
            ),
            code.upper() if code else None,
            inst.category,
            inst.ownership,
        )
    )


def _visible(institution_id: uuid.UUID) -> Institution:
    inst: Institution | None = Institution.objects.in_scope().filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    return inst


def profile(institution_id: uuid.UUID, on: dt.date | None = None) -> dict[str, Any]:
    """REG-02: every body the institution depends on, with the gaps that remain."""
    authz.require("institution:view")
    inst = _visible(institution_id)
    on = on or dt.date.today()
    rows = list(
        InstitutionRegulation.objects.filter(institution_id=inst.id, valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .order_by("relationship", "body_code")
    )
    names = {b.code: b for b in bodies().values()}
    links = [
        {
            "id": r.id,
            "body_code": r.body_code,
            "body_name": names[r.body_code].name if r.body_code in names else r.body_code,
            "body_type": names[r.body_code].body_type if r.body_code in names else None,
            "relationship": r.relationship,
            "covers": r.covers,
            "levels": r.levels or [],
            "is_mandatory": r.is_mandatory,
            "source": r.source,
            "data_status": r.data_status,
            "valid_from": r.valid_from,
        }
        for r in rows
    ]
    return {
        "institution_id": inst.id,
        "name": inst.name,
        "category": inst.category,
        "ownership": inst.ownership,
        "levels": list(inst.levels or []),
        "links": links,
        "gaps": ref.gaps(
            [(r["body_code"], r["relationship"]) for r in links], category=inst.category, levels=list(inst.levels or [])
        ),
    }


def set_link(
    institution_id: uuid.UUID,
    body_code: str,
    relationship: str,
    *,
    covers: str,
    levels: list[str] | None = None,
    reason: str,
) -> InstitutionRegulation:
    """Add a link for one institution (e.g. a professional council for a nursing programme)."""
    inst = _visible(institution_id)
    body = bodies().get(body_code.upper())
    if body is None:
        raise HardValidation("REG-BODY", "Unknown education body", body_code)
    with uow.command(
        "registry", "regulation:manage", action="set_link", record_kind="institution_regulation", reason=reason
    ) as cmd:
        current = (
            InstitutionRegulation.unscoped.using(cmd.alias)
            .filter(
                tenant_id=cmd.ctx.state_tenant_id,
                institution_id=inst.id,
                body_code=body.code,
                relationship=relationship,
                valid_to__isnull=True,
            )
            .first()
        )
        if current is not None:
            return cmd.update(current, covers=covers[:200], levels=levels or None, source="institution")
        row = cmd.add(
            InstitutionRegulation(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                regulatory_body_id=body.id,
                body_code=body.code,
                relationship=relationship,
                covers=covers[:200],
                levels=levels or None,
                is_mandatory=True,
                source="institution",
                data_status="illustrative",
                valid_from=dt.date.today(),
            )
        )
        cmd.emit(
            "REG.PROFILE_CHANGED",
            aggregate_id=row.id,
            scope_node_id=inst.scope_node_id,
            payload={"institution_id": inst.id, "body_code": body.code, "relationship": relationship},
        )
        return row


def end_link(link_id: uuid.UUID, *, reason: str) -> InstitutionRegulation:
    with uow.command(
        "registry", "regulation:manage", action="end_link", record_kind="institution_regulation", reason=reason
    ) as cmd:
        row = cmd.lock(InstitutionRegulation, link_id)
        cmd.update(row, valid_to=dt.date.today())
        cmd.emit(
            "REG.PROFILE_CHANGED",
            aggregate_id=row.id,
            scope_node_id=row.scope_node_id,
            payload={
                "institution_id": row.institution_id,
                "body_code": row.body_code,
                "relationship": row.relationship,
            },
        )
        return row


# --------------------------------------------------------------------------- every institution in every registry
def _extras(inst: Institution) -> dict[str, Any]:
    """Owner ministry, accreditation and type flags from the sector profiles (security or federal)."""
    from syntegra.federal_institutions.models import FederalBody, FederalInstitution
    from syntegra.security_training.models import SecurityAgency, SecurityInstitution

    sec = SecurityInstitution.objects.filter(institution_id=inst.id).first()
    if sec is not None:
        agency = SecurityAgency.objects.get(pk=sec.agency_id)
        return {"owner_ministry": AGENCY_MINISTRY.get(agency.code), "accreditation": tuple(sec.accreditation or ())}
    fed = FederalInstitution.objects.filter(institution_id=inst.id).first()
    if fed is not None:
        body = FederalBody.objects.get(pk=fed.body_id)
        while body.code not in bodies() and body.parent_body_id:  # a parastatal: its supervising ministry
            body = FederalBody.objects.get(pk=body.parent_body_id)
        return {
            "owner_ministry": body.code if body.code in bodies() else None,
            "unity_college": fed.institution_type.startswith("unity_college")
            or fed.institution_type == "science_technical_college",
            "technical": fed.institution_type == "science_technical_college",
        }
    return {"owner_ministry": "FME" if inst.ownership == "federal" else None}


def apply_registry() -> int:
    """Apply the rules to every institution of the current registry (call inside its system context)."""
    insts = list(Institution.objects.all())
    if not insts:
        return 0
    n = 0
    with uow.command("registry", None, action="apply_rules", record_kind="institution_regulation") as cmd:
        for inst in insts:
            n += apply_rules(cmd, inst, **_extras(inst))
        cmd.note("links_added", None, n)
        if not n:
            cmd.audited = False
    return n


def apply_all() -> dict[str, int]:
    """Every registry on this platform: the 37 states and the sector registries."""
    from syntegra.platform.models import Tenant

    out = {}
    for t in Tenant.objects.using(PLATFORM).filter(kind__in=("state", "sector_registry"), status="active"):
        with context.use(context.system(t.id, t.id, correlation_id="regulation-apply")):
            out[t.code] = apply_registry()
    return out


def localise_registry() -> dict[str, int]:
    """Move the current registry's rule-derived links from the generic state bodies to the state's own bodies
    (after a state's bodies are added to the directory). Ends the generic links; adds the state's. A rule link
    whose levels have changed since it was made (e.g. a board now also covers the senior classes) is replaced."""
    from syntegra.core.tenancy import tenant_code_for

    ctx = context.require()
    code = (tenant_code_for(ctx.state_tenant_id) or "").upper()
    generic = set(ref.STATE_EQUIVALENTS.get(code, {})) | (
        {"STATE_MOE"} if code in ref.STATE_TERTIARY_MINISTRY else set()
    )
    n = {"ended": 0, "added": 0}
    if not generic:
        return n
    with uow.command("registry", None, action="localise", record_kind="institution_regulation") as cmd:
        for row in InstitutionRegulation.objects.filter(source="rule", valid_to__isnull=True, body_code__in=generic):
            cmd.update(row, valid_to=dt.date.today())
            n["ended"] += 1
        current: dict[uuid.UUID, list[InstitutionRegulation]] = defaultdict(list)
        for row in InstitutionRegulation.objects.filter(source="rule", valid_to__isnull=True).exclude(
            body_code__in=generic
        ):
            current[row.institution_id].append(row)
        for inst in Institution.objects.exclude(status__in=("closed", "merged")):
            extras = _extras(inst)
            # a rule link whose levels have changed (e.g. the board now also covers the senior classes) is replaced
            expected = {(x.body, x.relationship): x for x in _expected(cmd, inst, **extras)}
            for row in current.get(inst.id, []):
                want = expected.get((row.body_code, row.relationship))
                if want is None or list(want.levels) == list(row.levels or []):
                    continue
                if row.valid_from == dt.date.today():  # started today: correct it rather than end it the same day
                    cmd.update(row, levels=list(want.levels) or None, covers=want.covers[:200])
                    n["updated"] = n.get("updated", 0) + 1
                else:
                    cmd.update(row, valid_to=dt.date.today())
                    n["ended"] += 1
            n["added"] += apply_rules(cmd, inst, **extras)
        if not (n["ended"] or n["added"] or n.get("updated")):
            cmd.audited = False
    return n
