"""First-run provisioning of a state tenant (MFS §16.6) — used by ``manage.py syntegra_bootstrap`` and tests.

Creates the residency region, the country and state tenants, the tenant domains, the governance hierarchy
(country → state → LGAs), built-in roles with permissions, purpose codes, baseline policy rules and workflow
definitions, a GLID block and the first state administrator. Idempotent: re-running leaves existing rows.
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field
from typing import Any

from django.db import transaction

from syntegra.core import context, tenancy
from syntegra.core.fields import utcnow
from syntegra.core.tenancy import SEED_STATE_TENANT

COUNTRY_TENANT = uuid.UUID("00000000-0000-7000-8000-0000000000a0")

# Built-in roles (MFS §5.2). Permissions are resource:action; '*' is all.
ROLES: dict[str, tuple[str, str, list[str]]] = {
    "PLAT": ("Platform administrator", "special", ["*"]),
    "STA": (
        "State education administrator",
        "restricted",
        [
            "institution:*",
            "learner:view",
            "enrolment:view",
            "attendance:view",
            "coverage:*",
            "certificate:*",
            "financing:*",
            "metric:view",
            "ceda:view",
            "user:*",
            "policy:*",
            "staff:view",
            "class:view",
            "learner.nin:reveal",
            "curriculum:*",
            "calendar:*",
            "hr:*",
            "clearance:*",
            "admission:decide",
        ],
    ),
    "LGA": (
        "LGA education officer",
        "confidential",
        [
            "institution:view",
            "learner:view",
            "attendance:view",
            "coverage:view",
            "coverage:manage",
            "metric:view",
            "ceda:view",
            "staff:view",
            "class:view",
            "hr:view",
            "hr:posting_request",
            "clearance:resolve",
        ],
    ),
    "HEAD": (
        "Head of institution",
        "restricted",
        [
            "learner:*",
            "enrolment:*",
            "class:*",
            "attendance:*",
            "coverage:*",
            "staff:*",
            "metric:view",
            "census:*",
            "ceda:view",
            "institution:view",
            "certificate:view",
            "admission:decide",
            "clearance:check",
            "clearance:dispute",
            "clearance:publish",
            "hr:view",
            "hr:leave_approve",
            "hr:posting_request",
            "hr:relations",
        ],
    ),
    "TCH": (
        "Teacher",
        "confidential",
        ["attendance:mark", "attendance:view", "learner:view", "class:view", "hr:leave_request"],
    ),
    "REG": (
        "Registrar / admissions officer",
        "confidential",
        [
            "learner:register",
            "learner:view",
            "enrolment:view",
            "clearance:check",
            "clearance:dispute",
            "institution:view",
        ],
    ),
    "HR": (
        "HR officer",
        "restricted",
        [
            "hr:view",
            "hr:configure",
            "hr:establishment",
            "hr:appoint",
            "hr:posting_request",
            "hr:posting_approve",
            "hr:leave_manage",
            "hr:leave_approve",
            "hr:promote",
            "hr:separate",
            "hr:relations",
            "hr:relations_decide",
            "hr:bank_request",
            "staff:*",
            "institution:view",
            "metric:view",
        ],
    ),
    "PAYR": (
        "Payroll officer",
        "restricted",
        ["hr:view", "hr:payroll_prepare", "hr:bank_approve", "institution:view"],
    ),
    "CERT": (
        "Certification registrar",
        "confidential",
        [
            "certificate:issue",
            "certificate:view",
            "certificate:reissue",
            "certificate:approve",
            "learner:view",
            "institution:view",
        ],
    ),
    "INTEG": (
        "Integrity investigator",
        "restricted",
        ["certificate:view", "learner:view", "institution:view", "hr:integrity", "hr:view"],
    ),
    "FINO": (
        "Finance officer (SDAF)",
        "confidential",
        [
            "financing:*",
            "census:view",
            "institution:view",
            "metric:view",
            "clearance:publish",
            "clearance:dispute",
            "hr:payroll_approve",
        ],
    ),
}

PURPOSES = [
    ("registration", "Registration and enrolment", False, None),
    ("transfer_query", "Transfer between institutions", False, None),
    ("safeguarding", "Safeguarding a child", True, ["HEAD", "STA"]),
    ("investigation", "Investigation or audit", True, ["STA", "PLAT", "INTEG"]),
    ("exam_integrity", "Examination integrity", True, ["STA", "CERT", "INTEG"]),
    ("child_missing_education", "Child missing education", True, ["HEAD", "LGA", "STA"]),
]

POLICIES = [
    # rule_key, domain, title, expression, parameters, mandatory_below
    (
        "ATT-PERSISTENT",
        "attendance",
        "Persistent absence threshold",
        "rate < threshold",
        {"threshold": 0.90, "_tighten": {"threshold": "higher"}},
        True,
    ),
    (
        "ATT-SEVERE",
        "attendance",
        "Severe absence threshold",
        "rate < threshold",
        {"threshold": 0.50, "_tighten": {"threshold": "higher"}},
        True,
    ),
    (
        "G2",
        "coverage",
        "Exactly one teacher of record per class-subject",
        "teachers_of_record == 1",
        {"due_school_days": 3, "severity": "critical", "owner_role": "HEAD"},
        True,
    ),
    (
        "G3",
        "coverage",
        "Teacher of record holds a valid authorisation",
        "authorised",
        {"due_school_days": 10, "severity": "high", "owner_role": "HEAD"},
        True,
    ),
    (
        "G11",
        "coverage",
        "Teacher load within state maximum",
        "periods <= max_periods",
        {"max_periods": 30, "_tighten": {"max_periods": "lower"}},
        True,
    ),
    (
        "SUPPRESS",
        "alerting",
        "Small-number suppression for published statistics",
        "n >= k",
        {"k": 5, "_tighten": {"k": "higher"}},
        True,
    ),
]

WORKFLOWS: dict[str, dict[str, Any]] = {
    "certificate_reissue": {
        "title": "Certificate reissue (four eyes)",
        "definition": {
            "initial": "requested",
            "transitions": [
                {
                    "from": "requested",
                    "on": "approve",
                    "to": "approved",
                    "permission": "certificate:approve",
                    "guard": "requested_by != approver",
                },
                {"from": "requested", "on": "reject", "to": "rejected", "permission": "certificate:approve"},
            ],
            "tasks": {"requested": {"title": "Approve certificate reissue", "role": "CERT", "sla_hours": 72}},
            "final": ["approved", "rejected"],
        },
    },
}

LGAS = [("AB-ABS", "Aba South"), ("AB-UMN", "Umuahia North"), ("AB-OHF", "Ohafia")]


@dataclass
class Seeded:
    state_tenant_id: uuid.UUID
    country_scope_id: uuid.UUID
    state_scope_id: uuid.UUID
    lga_scope_ids: dict[str, uuid.UUID] = field(default_factory=dict)
    admin_user_id: uuid.UUID | None = None
    role_ids: dict[str, uuid.UUID] = field(default_factory=dict)


def _platform(hosts: list[str]) -> None:
    from syntegra.platform.models import GlidBlock, ResidencyRegion, Tenant, TenantDomain

    alias = "platform"
    with transaction.atomic(using=alias):
        region = ResidencyRegion.objects.using(alias).filter(code="ng-lagos").first()
        if region is None:
            region = ResidencyRegion(
                code="ng-lagos",
                name="Nigeria — Lagos",
                country="NG",
                primary_site="Lagos DC1",
                secondary_site="Abuja DC1",
                status="active",
            )
            region.save(using=alias)
        if not Tenant.objects.using(alias).filter(pk=COUNTRY_TENANT).exists():
            Tenant(
                id=COUNTRY_TENANT,
                kind="country",
                code="ng",
                name="Federal Republic of Nigeria",
                residency_region_id=region.id,
                isolation="dedicated_schema",
                ops_schema="syn_ops_ng",
                status="active",
                activated_at=utcnow(),
            ).save(using=alias, force_insert=True)
        if not Tenant.objects.using(alias).filter(pk=SEED_STATE_TENANT).exists():
            Tenant(
                id=SEED_STATE_TENANT,
                parent_id=COUNTRY_TENANT,
                kind="state",
                code="ng-ab",
                name="Abia State",
                residency_region_id=region.id,
                state_code="NG-AB",
                isolation="dedicated_schema",
                ops_schema="syn_ops_ng-ab",
                status="active",
                activated_at=utcnow(),
            ).save(using=alias, force_insert=True)
        for i, h in enumerate(hosts):
            if not TenantDomain.objects.using(alias).filter(hostname=h).exists():
                TenantDomain(
                    tenant_id=SEED_STATE_TENANT, hostname=h, is_primary=i == 0, verified_at=utcnow(), status="active"
                ).save(using=alias)
        if not GlidBlock.objects.using(alias).filter(tenant_id=SEED_STATE_TENANT).exists():
            GlidBlock(tenant_id=SEED_STATE_TENANT, first_serial=1, last_serial=10_000, leased_at=utcnow()).save(
                using=alias
            )


def bootstrap(
    *,
    admin_username: str = "admin@abia.gov.ng",
    admin_password: str | None = None,
    hosts: list[str] | None = None,
) -> Seeded:
    from syntegra.core import uow
    from syntegra.governance import services as gov
    from syntegra.governance.models import PolicyRule, ScopeNode, WorkflowDefinition
    from syntegra.iam import services as iam
    from syntegra.iam.models import AppUser, PurposeCode, Role, RolePermission

    _platform(hosts or ["abia.syntegra.ng", "localhost", "127.0.0.1", "testserver"])
    tenancy.clear_caches()
    ctx = context.system(SEED_STATE_TENANT, SEED_STATE_TENANT, correlation_id="bootstrap")
    with context.use(ctx):
        out = Seeded(SEED_STATE_TENANT, uuid.UUID(int=0), uuid.UUID(int=0))
        with uow.command("registry", None, action="bootstrap", record_kind="tenant") as cmd:
            cmd.record_id = SEED_STATE_TENANT
            ng = ScopeNode.objects.filter(code="NG").first() or gov.add_node(
                cmd, parent=None, level="country", code="NG", name="Nigeria", ref_kind="tenant", ref_id=COUNTRY_TENANT
            )
            ab = ScopeNode.objects.filter(code="NG-AB").first() or gov.add_node(
                cmd,
                parent=ng,
                level="state",
                code="NG-AB",
                name="Abia State",
                ref_kind="tenant",
                ref_id=SEED_STATE_TENANT,
            )
            out.country_scope_id, out.state_scope_id = ng.id, ab.id
            for code, name in LGAS:
                lga = ScopeNode.objects.filter(code=code).first() or gov.add_node(
                    cmd, parent=ab, level="lga", code=code, name=name
                )
                out.lga_scope_ids[code] = lga.id
            for code, (name, clearance, perms) in ROLES.items():
                role = Role.objects.filter(code=code).first()
                if role is None:
                    role = cmd.add(Role(code=code, name=name, clearance=clearance, is_builtin=True, status="active"))
                have = set(RolePermission.objects.filter(role_id=role.id).values_list("permission", flat=True))
                for p in perms:  # built-in roles gain permissions added by later releases
                    if p not in have:
                        cmd.add(RolePermission(role_id=role.id, permission=p))
                out.role_ids[code] = role.id
            for code, label, reason, roles in PURPOSES:
                if not PurposeCode.objects.filter(code=code).exists():
                    cmd.add(PurposeCode(code=code, label=label, requires_reason_text=reason, allowed_roles=roles))
            for key, domain, title, expr, params, mandatory in POLICIES:
                if not PolicyRule.objects.filter(rule_key=key, scope_node_id=ab.id).exists():
                    cmd.add(
                        PolicyRule(
                            scope_node_id=ab.id,
                            rule_key=key,
                            rule_domain=domain,
                            title=title,
                            version=1,
                            is_mandatory_below=mandatory,
                            expression=expr,
                            parameters=params,
                            status="published",
                            effective_from=dt.date(2020, 1, 1),
                        )
                    )
            for key, spec in WORKFLOWS.items():
                if not WorkflowDefinition.objects.filter(workflow_key=key).exists():
                    cmd.add(
                        WorkflowDefinition(
                            scope_node_id=ab.id,
                            workflow_key=key,
                            version=1,
                            title=spec["title"],
                            definition=spec["definition"],
                            status="published",
                        )
                    )
        from syntegra.hr import defaults as hr_defaults

        hr_defaults.seed(out.state_scope_id)
        admin = AppUser.objects.filter(username=admin_username).first()
        if admin is None:
            admin = iam.create_user(
                ctx, username=admin_username, display_name="State Administrator", password=admin_password
            )
            iam.grant_role(ctx, user=admin, role_code="STA", scope_id=ab.id)
        out.admin_user_id = admin.id
    return out
