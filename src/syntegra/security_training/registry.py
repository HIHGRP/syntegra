"""The Federal Security Education registry (CR-004): a national sector registry beside the 37 state registries.

``provision`` creates the registry tenant (kind ``sector_registry``, code ``ng-fse``), its scope hierarchy root, roles,
purposes and policies, and optionally its first administrator. ``seed_reference`` loads every agency individually —
its structure as scope nodes (agency → headquarters → commands, training commands, formations, state commands), its
ranks, its institutions and each institution's own course catalogue with modules. Both are idempotent.

Scope hierarchy::

    NG (country)
    ├── NG-FSE (authority: the registry)
    │   └── <agency> (agency) ── <unit> (formation, nested) ── <institution> (institution)
    └── NG-KD, NG-LA … (state: location references for institutions; nothing is granted there)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from syntegra.core import context, uow
from syntegra.core.ids import format_institution_code
from syntegra.core.tenancy import state_tenant_id
from syntegra.platform import sector
from syntegra.platform.states import BY_CODE, STATES
from syntegra.security_training import curricula
from syntegra.security_training import reference as ref

CODE = "NG-FSE"
NAME = "Federal Security Education Registry"
DEFAULT_HOSTS = ["fse.syntegra.ng"]


def tenant_id() -> uuid.UUID:
    return state_tenant_id(CODE)


def system_context() -> context.Context:
    return sector.system_context(CODE)


Provisioned = sector.Provisioned


def provision(
    *, admin_username: str | None = None, admin_password: str | None = None, hosts: list[str] | None = None
) -> sector.Provisioned:
    """Create the registry tenant, scope root and configuration; grant SADM at the root to the administrator."""
    return sector.provision(
        CODE,
        NAME,
        hosts=hosts or DEFAULT_HOSTS,
        admin_role="SADM",
        admin_username=admin_username,
        admin_password=admin_password,
    )


# --------------------------------------------------------------------------- reference data
@dataclass
class Seeded:
    agencies: int = 0
    units: int = 0
    ranks: int = 0
    institutions: int = 0
    courses: int = 0
    modules: int = 0
    agency_modules: int = 0
    course_units: int = 0
    career_requirements: int = 0


def seed_reference() -> Seeded:
    """Load (or complete) the agencies, structures, ranks, institutions and course catalogues. Idempotent."""
    with context.use(system_context()):
        n = Seeded()
        with uow.command("registry", None, action="seed_reference", record_kind="security_agency") as cmd:
            _seed(cmd, n)
            cmd.note("seeded", None, n.__dict__)
        return n


def _seed(cmd: uow.Command, n: Seeded) -> None:
    from syntegra.governance import services as gov
    from syntegra.governance.models import ScopeNode
    from syntegra.security_training.models import AgencyRank, AgencyUnit, SecurityAgency

    root = ScopeNode.objects.get(code=CODE)
    states = sector.location_nodes()
    for a in ref.AGENCIES:
        agency = SecurityAgency.objects.filter(code=a.code).first()
        if agency is None:
            node = gov.add_node(cmd, parent=root, level="agency", code=a.code, name=a.name, ref_kind="security_agency")
            agency = cmd.add(
                SecurityAgency(
                    scope_node_id=node.id,
                    code=a.code,
                    name=a.name,
                    category=a.category,
                    supervising_ministry=a.ministry,
                    establishing_law=a.law,
                    data_status=a.status,
                    status="active",
                )
            )
            ScopeNode.objects.filter(pk=node.id).update(ref_id=agency.id)
            n.agencies += 1
        units = {u.code: u for u in AgencyUnit.objects.filter(agency_id=agency.id)}
        nodes = {u.code: u.scope_node_id for u in units.values()}
        specs = list(ref.UNITS.get(a.code, []))
        if a.code in ref.STATE_COMMANDS:
            parent, unit_type, pattern = ref.STATE_COMMANDS[a.code]
            for code, state_name, _cap in STATES:
                label = state_name.replace(" State", "") if code != "NG-FC" else "FCT"
                specs.append(ref.Unit(f"{code[3:]}-CMD", pattern.format(state=label), unit_type, parent, code, None))
        for u in specs:
            if u.code in units:
                continue
            parent_unit = units.get(u.parent) if u.parent else None
            parent_node = (
                ScopeNode.objects.get(pk=nodes[u.parent])
                if u.parent
                else ScopeNode.objects.get(pk=agency.scope_node_id)
            )
            node = gov.add_node(
                cmd,
                parent=parent_node,
                level="formation",
                code=f"{a.code}.{u.code}",
                name=u.name,
                ref_kind="agency_unit",
            )
            unit = cmd.add(
                AgencyUnit(
                    scope_node_id=node.id,
                    agency_id=agency.id,
                    parent_unit_id=parent_unit.id if parent_unit else None,
                    unit_type=u.unit_type,
                    code=u.code,
                    name=u.name,
                    headquarters_state=u.state,
                    headquarters_town=u.town,
                    data_status=u.status,
                    status="active",
                )
            )
            ScopeNode.objects.filter(pk=node.id).update(ref_id=unit.id)
            units[u.code], nodes[u.code] = unit, node.id
            n.units += 1
        have = set(AgencyRank.objects.filter(agency_id=agency.id).values_list("code", flat=True))
        ranks = ref.RANKS.get(a.code) or curricula.MORE_RANKS.get(a.code, [])
        for i, (rcode, title, abbr, cat) in enumerate(ranks, start=1):
            if rcode not in have:
                cmd.add(
                    AgencyRank(
                        agency_id=agency.id,
                        code=rcode,
                        title=title,
                        abbreviation=abbr,
                        rank_category=cat,
                        seniority=i,
                        data_status=ref.RANK_STATUS.get(a.code, ref.C),  # CR-006 additions: to_confirm
                    )
                )
                n.ranks += 1
    for spec, courses in ref.INSTITUTIONS:
        _seed_institution(cmd, n, spec, courses, states)
    seed_curricula(cmd, n)


def seed_curricula(cmd: uow.Command, n: Seeded) -> None:
    """CR-006: agency-specific syllabus headings, the units of each course and each rank's course requirements.

    Idempotent and additive, so registries seeded before CR-006 are completed in place."""
    from syntegra.security_training.models import (
        AgencyRank,
        AgencyUnit,
        SecurityAgency,
        SecurityCareerRequirement,
        SecurityCourse,
        SecurityCourseModule,
        SecurityCourseUnit,
        SecurityInstitution,
    )

    agencies = {a.id: a for a in SecurityAgency.objects.all()}
    by_code = {a.code: a for a in agencies.values()}
    units = {(u.agency_id, u.code): u for u in AgencyUnit.objects.all()}
    owning = dict(SecurityInstitution.objects.values_list("institution_id", "unit_id"))
    unit_code = {u.id: u.code for u in units.values()}
    have_units = set(SecurityCourseUnit.objects.values_list("course_id", "unit_id", "role"))
    for course in SecurityCourse.objects.filter(status="published"):
        agency = agencies[course.agency_id]
        if course.content_held:
            mods = list(SecurityCourseModule.objects.filter(course_id=course.id))
            codes, seq = {m.code for m in mods}, max((m.sequence for m in mods), default=0)
            for mcode, title, area, assessment, _cats in curricula.modules_for(agency.code, course.category):
                if mcode in codes:
                    continue
                seq += 1
                cmd.add(
                    SecurityCourseModule(
                        course_id=course.id,
                        sequence=seq,
                        code=mcode,
                        title=title,
                        area=area,
                        assessment=assessment,
                        is_mandatory=True,
                    )
                )
                n.agency_modules += 1
        delivering = unit_code.get(owning.get(course.institution_id))
        for acode, ucode, role in curricula.course_units(agency.code, delivering or "", course.category):
            unit = units.get((by_code[acode].id, ucode)) if acode in by_code else None
            if unit is None or (course.id, unit.id, role) in have_units:
                continue
            cmd.add(SecurityCourseUnit(course_id=course.id, unit_id=unit.id, role=role, data_status=curricula.C))
            have_units.add((course.id, unit.id, role))
            n.course_units += 1
    have_reqs = set(
        SecurityCareerRequirement.objects.values_list("agency_id", "rank_id", "requirement_kind", "course_code")
    )
    for acode, reqs in curricula.CAREER.items():
        agency = by_code.get(acode)
        if agency is None:
            continue
        ranks = {r.code: r for r in AgencyRank.objects.filter(agency_id=agency.id)}
        for rcode, kind, course_code, category, mandatory in reqs:
            rank = ranks.get(rcode)
            if rank is None or (agency.id, rank.id, kind, course_code) in have_reqs:
                continue
            cmd.add(
                SecurityCareerRequirement(
                    scope_node_id=agency.scope_node_id,
                    agency_id=agency.id,
                    rank_id=rank.id,
                    requirement_kind=kind,
                    course_code=course_code,
                    course_category=category,
                    is_mandatory=mandatory,
                    data_status=curricula.C,
                    status="active",
                )
            )
            have_reqs.add((agency.id, rank.id, kind, course_code))
            n.career_requirements += 1


def _seed_institution(
    cmd: uow.Command, n: Seeded, spec: ref.Institution, courses: list[ref.Course], states: dict[str, Any]
) -> None:
    from syntegra.governance import services as gov
    from syntegra.governance.models import ScopeNode
    from syntegra.institutions.models import Institution
    from syntegra.security_training.models import AgencyUnit, SecurityAgency, SecurityInstitution

    agency = SecurityAgency.objects.get(code=spec.agency)
    unit = AgencyUnit.objects.get(agency_id=agency.id, code=spec.unit)
    existing = ScopeNode.objects.filter(code=f"{agency.code}.{spec.code}").first()
    prof = SecurityInstitution.objects.filter(scope_node_id=existing.id).first() if existing else None
    if prof is None:
        inst_node = gov.add_node(
            cmd,
            parent=ScopeNode.objects.get(pk=unit.scope_node_id),
            level="institution",
            code=f"{agency.code}.{spec.code}",
            name=spec.name,
            ref_kind="institution",
            ownership="federal",
        )
        serial = Institution.unscoped.using(cmd.alias).count() + 1
        inst = cmd.add(
            Institution(
                scope_node_id=inst_node.id,
                institution_code=format_institution_code("NG", serial),
                name=spec.name,
                short_name=spec.short_name,
                category=spec.category,
                ownership="federal",
                is_public=True,
                operating_tenant_id=cmd.ctx.state_tenant_id,
                lga_scope_id=states[spec.state].id,  # state-level location until the agency confirms the LGA
                levels=list(spec.levels),
                address={"town": spec.town, "state": BY_CODE[spec.state][0]},
                onboarding_status="not_onboarded",
                regulatory_status="approved",
                status="active",
            )
        )
        ScopeNode.objects.filter(pk=inst_node.id).update(ref_id=inst.id)
        prof = cmd.add(
            SecurityInstitution(
                scope_node_id=inst_node.id,
                institution_id=inst.id,
                agency_id=agency.id,
                unit_id=unit.id,
                institution_type=spec.institution_type,
                access_regime=spec.access_regime,
                accreditation=list(spec.accreditation) or None,
                commandant_title=spec.head_title,
                established_year=spec.established,
                data_status=spec.status,
            )
        )
        n.institutions += 1
        from syntegra.regulation import services as regulation

        regulation.apply_rules(cmd, inst, data_status=spec.status, **regulation._extras(inst))
    for c in courses:
        _seed_course(cmd, n, prof, agency, c)


def _seed_course(cmd: uow.Command, n: Seeded, prof: Any, agency: Any, c: ref.Course) -> None:
    from syntegra.security_training.models import SecurityCourse, SecurityCourseModule

    if SecurityCourse.objects.filter(institution_id=prof.institution_id, code=c.code).exists():
        return
    course = cmd.add(
        SecurityCourse(
            scope_node_id=prof.scope_node_id,
            institution_id=prof.institution_id,
            agency_id=agency.id,
            code=c.code,
            title=c.title,
            category=c.category,
            award=c.award,
            award_title=c.award_title,
            accrediting_body=c.accrediting_body,
            duration_weeks=c.duration_weeks,
            entry_requirements=list(c.entry) or None,
            target_ranks=list(c.target_ranks) or None,
            version="1.0",
            content_held=c.content_held,
            data_status=c.status,
            status="published",
        )
    )
    n.courses += 1
    if not c.content_held:
        return  # the agency does not release module detail
    for seq, (mcode, title, area, assessment) in enumerate(c.modules or ref.TEMPLATES[c.category], start=1):
        cmd.add(
            SecurityCourseModule(
                course_id=course.id,
                sequence=seq,
                code=mcode,
                title=title,
                area=area,
                assessment=assessment,
                is_mandatory=True,
            )
        )
        n.modules += 1
