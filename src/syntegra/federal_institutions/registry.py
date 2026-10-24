"""The Federal Institutions registry (CR-005, decision CD-23): federal unity colleges and special training institutions.

``provision`` creates the sector registry ``ng-fed``; ``seed_reference`` loads the owning bodies, their structures and
the institutions (each with its regulatory profile); ``upsert_institution`` is shared with the reference import.

Scope hierarchy::

    NG ── NG-FED ── <body> (agency) ── <unit> (formation, nested) ── <institution>
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from syntegra.core import context, uow
from syntegra.core.ids import format_institution_code
from syntegra.federal_institutions import reference as ref
from syntegra.platform import sector
from syntegra.platform.states import BY_CODE, ZONES

CODE = "NG-FED"
NAME = "Federal Institutions Registry"
DEFAULT_HOSTS = ["fed.syntegra.ng"]


def system_context() -> context.Context:
    return sector.system_context(CODE)


def provision(
    *, admin_username: str | None = None, admin_password: str | None = None, hosts: list[str] | None = None
) -> sector.Provisioned:
    return sector.provision(
        CODE,
        NAME,
        hosts=hosts or DEFAULT_HOSTS,
        admin_role="FADM",
        admin_username=admin_username,
        admin_password=admin_password,
    )


@dataclass
class Seeded:
    bodies: int = 0
    units: int = 0
    institutions: int = 0
    updated: int = 0
    regulatory_links: int = 0


def seed_reference() -> Seeded:
    with context.use(system_context()):
        n = Seeded()
        with uow.command("registry", None, action="seed_reference", record_kind="federal_body") as cmd:
            _seed_bodies(cmd, n)
            for spec in ref.INSTITUTIONS:
                upsert_institution(cmd, n, spec, source="rule")
            cmd.note("seeded", None, n.__dict__)
        return n


def _seed_bodies(cmd: uow.Command, n: Seeded) -> None:
    from syntegra.federal_institutions.models import FederalBody, FederalBodyUnit
    from syntegra.governance import services as gov
    from syntegra.governance.models import ScopeNode

    root = ScopeNode.objects.get(code=CODE)
    bodies = {b.code: b for b in FederalBody.objects.all()}
    for b in ref.BODIES:
        if b.code in bodies:
            continue
        parent = bodies.get(b.parent) if b.parent else None
        parent_node = ScopeNode.objects.get(pk=parent.scope_node_id) if parent else root
        level = "formation" if parent else "agency"
        node = gov.add_node(cmd, parent=parent_node, level=level, code=f"FED.{b.code}", name=b.name)
        bodies[b.code] = cmd.add(
            FederalBody(
                scope_node_id=node.id,
                code=b.code,
                name=b.name,
                category=b.category,
                parent_body_id=parent.id if parent else None,
                data_status=b.status,
                status="active",
            )
        )
        n.bodies += 1
    have = {(u.body_id, u.code): u for u in FederalBodyUnit.objects.all()}
    for u in ref.UNITS:
        body = bodies[u.body]
        if (body.id, u.code) in have:
            continue
        parent = have.get((body.id, u.parent)) if u.parent else None
        parent_node = ScopeNode.objects.get(pk=(parent or body).scope_node_id)
        node = gov.add_node(cmd, parent=parent_node, level="formation", code=f"FED.{u.body}.{u.code}", name=u.name)
        have[(body.id, u.code)] = cmd.add(
            FederalBodyUnit(
                scope_node_id=node.id,
                body_id=body.id,
                parent_unit_id=parent.id if parent else None,
                unit_type=u.unit_type,
                code=u.code,
                name=u.name,
                data_status=u.status,
                status="active",
            )
        )
        n.units += 1


def upsert_institution(cmd: uow.Command, n: Any, spec: ref.Inst, *, source: str) -> Any:
    """Create or update one federal institution (and its regulatory profile). Used by the seed and the import."""
    from syntegra.federal_institutions.models import FederalBody, FederalBodyUnit, FederalInstitution
    from syntegra.governance import services as gov
    from syntegra.governance.models import ScopeNode
    from syntegra.institutions.models import Institution
    from syntegra.regulation import services as regulation

    body = FederalBody.objects.get(code=spec.body)
    unit = FederalBodyUnit.objects.get(body_id=body.id, code=spec.unit)
    code = f"FED.{spec.body}.{spec.code}"
    existing = ScopeNode.objects.filter(code=code).first()
    prof = FederalInstitution.objects.filter(scope_node_id=existing.id).first() if existing else None
    if prof is not None:
        inst = Institution.objects.get(pk=prof.institution_id)
        changes = {
            k: v
            for k, v in (("name", spec.name), ("category", spec.category), ("levels", list(spec.levels)))
            if getattr(inst, k) != v
        }
        if changes:
            cmd.update(inst, **changes)
            n.updated += 1
        if prof.data_status != spec.status and spec.status:
            cmd.update(prof, data_status=spec.status)
        return prof
    states = sector.location_nodes()
    node = gov.add_node(
        cmd,
        parent=ScopeNode.objects.get(pk=unit.scope_node_id),
        level="institution",
        code=code,
        name=spec.name,
        ref_kind="institution",
        ownership="federal",
    )
    inst = cmd.add(
        Institution(
            scope_node_id=node.id,
            institution_code=format_institution_code("NG", Institution.unscoped.using(cmd.alias).count() + 1),
            name=spec.name,
            short_name=spec.short_name,
            category=spec.category,
            ownership="federal",
            is_public=True,
            operating_tenant_id=cmd.ctx.state_tenant_id,
            lga_scope_id=states[spec.state].id,  # state-level location until the LGA is confirmed
            levels=list(spec.levels),
            day_boarding=spec.boarding,
            gender_intake=spec.gender,
            address={"town": spec.town, "state": BY_CODE[spec.state][0]},
            onboarding_status="not_onboarded",
            regulatory_status="approved",
            status="active",
        )
    )
    ScopeNode.objects.filter(pk=node.id).update(ref_id=inst.id)
    prof = cmd.add(
        FederalInstitution(
            scope_node_id=node.id,
            institution_id=inst.id,
            body_id=body.id,
            unit_id=unit.id,
            institution_type=spec.institution_type,
            geopolitical_zone=ZONES[spec.state],
            gender_intake=spec.gender,
            day_boarding=spec.boarding,
            admission_basis=spec.admission,
            data_status=spec.status,
        )
    )
    n.institutions += 1
    from syntegra.regulation.services import _extras

    n.regulatory_links += regulation.apply_rules(cmd, inst, data_status=spec.status, **_extras(inst))
    extra = ref.SECTOR_REGULATORS.get(spec.code)
    if extra:
        body_ = regulation.bodies().get(extra[0])
        if body_ is not None:
            import datetime as dt

            from syntegra.regulation.models import InstitutionRegulation

            cmd.add(
                InstitutionRegulation(
                    scope_node_id=node.id,
                    institution_id=inst.id,
                    regulatory_body_id=body_.id,
                    body_code=body_.code,
                    relationship=extra[1],
                    covers=extra[2],
                    is_mandatory=True,
                    source=source,
                    data_status=spec.status,
                    valid_from=dt.date.today(),
                )
            )
            n.regulatory_links += 1
    return prof
