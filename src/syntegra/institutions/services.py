"""Institution register (MFS §8, FR-INS-*): registration with duplicate detection and its scope node."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from django.db import IntegrityError

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound, SoftWarning
from syntegra.core.ids import format_institution_code
from syntegra.governance import services as gov
from syntegra.governance.models import ScopeNode
from syntegra.institutions.domain import duplicates
from syntegra.institutions.models import Institution

PUBLIC_OWNERSHIP = {"federal", "state", "lga"}


@dataclass
class RegisterInstitution:
    name: str
    category: str
    ownership: str
    lga_scope_id: uuid.UUID
    address: dict[str, Any]
    levels: list[str]
    gov_reg_no: str | None = None
    location: tuple[float, float] | None = None
    short_name: str | None = None
    capacity: int | None = None
    day_boarding: str | None = None
    gender_intake: str | None = None
    location_class: str | None = None
    phone: str | None = None
    email: str | None = None
    operating_tenant_id: uuid.UUID | None = None


def duplicate_findings(data: RegisterInstitution) -> list[duplicates.Finding]:
    existing = [
        duplicates.Candidate(i.id, i.name, i.gov_reg_no, i.location, i.category)
        for i in Institution.objects.filter(lga_scope_id=data.lga_scope_id).exclude(status__in=("closed", "merged"))
    ]
    return duplicates.check(data.name, data.gov_reg_no, data.location, data.category, existing)


def register(data: RegisterInstitution, *, override_reason: str | None = None) -> Institution:
    ctx = context.require()
    authz.require("institution:register", ctx)
    lga = ScopeNode.objects.filter(pk=data.lga_scope_id, level="lga").first()
    if lga is None:
        raise HardValidation(
            "INS-LGA",
            "Unknown LGA",
            "Choose the LGA from the state hierarchy.",
            [{"field": "lga_scope_id", "message": "not an LGA in this state"}],
        )
    authz.require_scope(lga.id, ctx)
    findings = duplicate_findings(data)
    hard = [f for f in findings if f.level == "hard"]
    if hard:
        raise ConflictError(
            "INS-DUPLICATE", "Institution already registered", f"{hard[0].reason} (institution {hard[0].key})."
        )
    if findings and not override_reason:
        err = SoftWarning(
            "INS-PROBABLE-DUPLICATE",
            "Possible duplicate institution",
            "; ".join(f"{f.reason} (similarity {f.similarity:.2f})" for f in findings[:3]),
        )
        err.extra["candidates"] = [
            {
                "institution_id": str(f.key),
                "reason": f.reason,
                "similarity": round(f.similarity, 3),
                "distance_m": round(f.distance_m) if f.distance_m is not None else None,
            }
            for f in findings[:5]
        ]
        raise err
    is_public = data.ownership in PUBLIC_OWNERSHIP
    for attempt in range(3):
        try:
            with uow.command(
                "registry", None, action="register", record_kind="institution", reason=override_reason
            ) as cmd:
                serial = Institution.objects.count() + 1 + attempt
                inst = Institution(
                    institution_code=format_institution_code("NG", serial),
                    gov_reg_no=data.gov_reg_no,
                    name=data.name.strip(),
                    short_name=data.short_name,
                    category=data.category,
                    ownership=data.ownership,
                    is_public=is_public,
                    operating_tenant_id=data.operating_tenant_id or (ctx.state_tenant_id if is_public else None),
                    lga_scope_id=lga.id,
                    levels=data.levels,
                    day_boarding=data.day_boarding,
                    gender_intake=data.gender_intake,
                    address=data.address,
                    location=data.location,
                    location_class=data.location_class,
                    capacity=data.capacity,
                    phone=data.phone,
                    email=data.email,
                    onboarding_status="not_onboarded",
                    regulatory_status="approved" if is_public else "regularising",
                    status="active",
                )
                node = gov.add_node(
                    cmd,
                    parent=lga,
                    level="institution",
                    code=inst.institution_code,
                    name=inst.name,
                    ref_kind="institution",
                    ref_id=inst.id,
                    ownership="public" if is_public else "private",
                )
                inst.scope_node_id = node.id
                if inst.operating_tenant_id is None:
                    raise HardValidation(
                        "INS-OPERATOR",
                        "Operating tenant required",
                        "Private institutions run in their provider's tenant.",
                    )
                cmd.add(inst)
                cmd.record_id = inst.id
                cmd.emit(
                    "INS.REGISTERED",
                    aggregate_id=inst.id,
                    scope_node_id=node.id,
                    payload={"institution_id": inst.id, "ownership": inst.ownership, "scope_node_id": node.id},
                )
                return inst
        except IntegrityError as exc:
            if "uq_institution_institution_code" in str(exc) and attempt < 2:
                continue
            raise
    raise ConflictError("INS-CODE", "Could not allocate an institution code", "Retry the request.")


def get(institution_id: uuid.UUID) -> Institution:
    inst: Institution | None = Institution.objects.in_scope().filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    return inst
