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
from syntegra.core.tenancy import SEED_STATE_TENANT, state_tenant_id
from syntegra.platform.states import BY_CODE, STATES

COUNTRY_TENANT = uuid.UUID("00000000-0000-7000-8000-0000000000a0")

# Built-in roles (MFS §5.2). Permissions are resource:action; '*' is all.
ROLES: dict[str, tuple[str, str, list[str]]] = {
    "PLAT": ("Platform administrator", "special", ["*"]),
    # security agencies' education and training (CR-004) — granted in the Federal Security Education registry
    "SADM": (
        "Security training administrator (agency, command or registry)",
        "restricted",
        [
            "security_training:*",
            "regulation:*",
            "institution:view",
            "learner:*",
            "enrolment:*",
            "metric:view",
            "ceda:view",
            "user:*",
            "estate:*",
            "warehouse:view",
        ],
    ),
    # federal unity colleges and special training institutions (CR-005) — granted in the Federal Institutions registry
    "FADM": (
        "Federal institutions administrator (body, unit or registry)",
        "restricted",
        [
            "federal_institutions:*",
            "regulation:*",
            "institution:view",
            "learner:*",
            "enrolment:*",
            "metric:view",
            "ceda:view",
            "user:*",
            "estate:*",
            "warehouse:view",
            "budget:view",
            "funding:view",
        ],
    ),
    "STO": (
        "Security training officer (institution)",
        "restricted",
        [
            "security_training:view",
            "security_training:intake",
            "security_training:record",
            "institution:view",
            "learner:register",
            "learner:view",
            "enrolment:view",
            "ceda:view",
        ],
    ),
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
            "regulation:*",
            "admission:decide",
            "budget:*",
            "imprest:*",
            "funding:*",
            "estate:*",
            "warehouse:*",
            "assessment:view",
            "exam:view",
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
            "estate:view",
            "estate:act",
            "warehouse:view",
            "budget:view",
            "funding:view",
            "assessment:view",
            "exam:view",
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
            "budget:view",
            "budget:approve",
            "budget:commit",
            "imprest:approve",
            "funding:view",
            "funding:apply",
            "funding:review",
            "estate:*",
            "warehouse:view",
            "assessment:*",
            "exam:*",
            "seating:*",
        ],
    ),
    "EXO": (
        "Examinations officer",
        "confidential",
        [
            "exam:*",
            "assessment:view",
            "learner:view",
            "class:view",
            "staff:view",
            "institution:view",
            "estate:view",
            "metric:view",
        ],
    ),
    "TCH": (
        "Teacher",
        "confidential",
        [
            "attendance:mark",
            "attendance:view",
            "learner:view",
            "class:view",
            "hr:leave_request",
            "funding:apply_own",
            "assessment:enter",
            "assessment:manage",
            "assessment:view",
            "exam:view",
            "seating:*",
        ],
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
            "assessment:view",
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
            "funding:view",
            "funding:apply",
            "funding:review",
        ],
    ),
    "PAYR": (
        "Payroll officer",
        "restricted",
        ["hr:view", "hr:payroll_prepare", "hr:bank_approve", "institution:view", "funding:collect"],
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
            "budget:prepare",
            "budget:commit",
            "budget:virement",
            "budget:view",
            "imprest:request",
            "imprest:retire",
            "funding:view",
            "funding:apply",
            "funding:disburse",
            "funding:collect",
            "funding:decide",
        ],
    ),
    # CR-006: facilities and the Commissioner's view
    "OPSM": (
        "Operations and facilities manager",
        "confidential",
        ["estate:*", "institution:view", "metric:view", "warehouse:view", "budget:view", "imprest:request"],
    ),
    "COMM": (
        "Commissioner for Education",
        "restricted",
        [
            "warehouse:view",
            "estate:view",
            "budget:view",
            "funding:view",
            "metric:view",
            "institution:view",
            "coverage:view",
            "hr:view",
            "ceda:view",
            "assessment:view",
            "attendance:view",
            "learner:view",
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
        "FND-NET-PAY-FLOOR",
        "financing",
        "Net pay floor for loan repayments deducted from pay (CR-006)",
        "net_pay >= gross_pay * fraction",
        {"fraction": "0.3333333333", "_tighten": {"fraction": "higher"}},
        True,
    ),
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
        "LRN-AGE-OF-MAJORITY",
        "registration",
        "Age of majority: learners below it need a guardian with parental responsibility (FR-LRN-05, FR-LRN-06)",
        "learner_age >= age",
        {"age": 18, "_tighten": {"age": "higher"}},
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


def _platform_base() -> uuid.UUID:
    """Residency region and the country tenant (national control plane). Returns the region id."""
    from syntegra.platform.models import ResidencyRegion, Tenant

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
        return uuid.UUID(str(region.id))


def _state_tenant(state_code: str, hosts: list[str]) -> uuid.UUID:
    name, _ = BY_CODE[state_code]
    return registry_tenant(state_code, name, "state", hosts, state_code=state_code)


def registry_tenant(code_upper: str, name: str, kind: str, hosts: list[str], *, state_code: str | None) -> uuid.UUID:
    """Create (idempotently) a registry tenant — a state, or a national sector registry — its hosts and GLID block."""
    from syntegra.platform.models import GlidBlock, Tenant, TenantDomain
    from syntegra.regulation.services import seed_directory

    alias = "platform"
    region_id = _platform_base()
    seed_directory()  # national directory of education watchdogs (CR-005), idempotent
    tid = state_tenant_id(code_upper)
    with transaction.atomic(using=alias):
        if not Tenant.objects.using(alias).filter(pk=tid).exists():
            code = code_upper.lower()
            Tenant(
                id=tid,
                parent_id=COUNTRY_TENANT,
                kind=kind,
                code=code,
                name=name,
                residency_region_id=region_id,
                state_code=state_code,
                isolation="dedicated_schema",
                ops_schema=f"syn_ops_{code}",
                status="active",
                activated_at=utcnow(),
            ).save(using=alias, force_insert=True)
        for i, h in enumerate(hosts):
            if not TenantDomain.objects.using(alias).filter(hostname=h).exists():
                TenantDomain(tenant_id=tid, hostname=h, is_primary=i == 0, verified_at=utcnow(), status="active").save(
                    using=alias
                )
        if not GlidBlock.objects.using(alias).filter(tenant_id=tid).exists():
            from syntegra.platform.glid import lease_block

            lease_block(tid)  # national GLID allocator: the next free block of 10,000 serials
    return tid


def seed_national_directory() -> int:
    """National clearance network directory: one row per state registry (36 states and the FCT), idempotent."""
    from syntegra.platform.models import ExchangePeer

    n = 0
    with transaction.atomic(using="platform"):
        for code, name, _ in STATES:
            if not ExchangePeer.objects.using("platform").filter(state_code=code).exists():
                ExchangePeer(
                    state_code=code,
                    state_name=name,
                    hosting="remote",
                    kid=f"exchange-{code.lower()}",
                    status="not_on_network",
                ).save(using="platform")
                n += 1
    return n


def join_network(state_code: str) -> None:
    """Mark a state provisioned on this platform as an active, co-hosted peer with its exchange verification key."""
    from syntegra.core import crypto
    from syntegra.platform.models import ExchangePeer

    seed_national_directory()
    kid = f"exchange-{state_code.lower()}"
    with transaction.atomic(using="platform"):
        peer = ExchangePeer.objects.using("platform").select_for_update().get(state_code=state_code)
        if peer.status != "active" or peer.hosting != "co_hosted":
            peer.hosting, peer.status, peer.kid = "co_hosted", "active", kid
            peer.tenant_id = state_tenant_id(state_code)
            peer.public_jwk = crypto.provider().public_jwk(kid)
            peer.agreement_ref = "NG-NCX-2026-001"
            peer.onboarded_at = utcnow()
            peer.save(using="platform")


def _copy_code_lists(tid: uuid.UUID) -> None:
    """Single-tenancy deployments share one registry schema: give a new state the jurisdiction code lists."""
    from django.db import connections

    from syntegra.core.zones import current_alias

    if tid == SEED_STATE_TENANT:
        return
    alias = current_alias("registry")
    with connections[alias].cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM code_list WHERE tenant_id = %s", [tid.bytes])
        if cur.fetchone()[0]:
            return
        cur.execute("SELECT COUNT(*) FROM code_list WHERE tenant_id = %s", [SEED_STATE_TENANT.bytes])
        if not cur.fetchone()[0]:
            return  # schema-per-state: the registry was seeded for this state by the migration
        cur.execute(
            "INSERT INTO code_list (id, tenant_id, code, title, pack, is_extensible) "
            "SELECT UUID_TO_BIN(UUID()), %s, code, title, pack, is_extensible FROM code_list WHERE tenant_id = %s",
            [tid.bytes, SEED_STATE_TENANT.bytes],
        )
        cur.execute(
            "INSERT INTO code_value (id, tenant_id, code_list_id, code, label, sort_order, valid_from) "
            "SELECT UUID_TO_BIN(UUID()), %s, nl.id, v.code, v.label, v.sort_order, v.valid_from FROM code_value v "
            "JOIN code_list ol ON ol.id = v.code_list_id JOIN code_list nl ON nl.tenant_id = %s AND nl.code = ol.code "
            "WHERE v.tenant_id = %s",
            [tid.bytes, tid.bytes, SEED_STATE_TENANT.bytes],
        )


def seed_registry_config(cmd: Any, root: Any) -> dict[str, uuid.UUID]:
    """Roles, purposes, policies and workflows of a registry (state or sector), idempotent; returns role ids."""
    from syntegra.governance.models import PolicyRule, WorkflowDefinition
    from syntegra.iam.models import PurposeCode, Role, RolePermission

    role_ids: dict[str, uuid.UUID] = {}
    for code, (role_name, clearance, perms) in ROLES.items():
        role = Role.objects.filter(code=code).first()
        if role is None:
            role = cmd.add(Role(code=code, name=role_name, clearance=clearance, is_builtin=True, status="active"))
        have = set(RolePermission.objects.filter(role_id=role.id).values_list("permission", flat=True))
        for p in perms:  # built-in roles gain permissions added by later releases
            if p not in have:
                cmd.add(RolePermission(role_id=role.id, permission=p))
        role_ids[code] = role.id
    for code, label, reason, roles in PURPOSES:
        if not PurposeCode.objects.filter(code=code).exists():
            cmd.add(PurposeCode(code=code, label=label, requires_reason_text=reason, allowed_roles=roles))
    for key, domain, title, expr, params, mandatory in POLICIES:
        if not PolicyRule.objects.filter(rule_key=key, scope_node_id=root.id).exists():
            cmd.add(
                PolicyRule(
                    scope_node_id=root.id,
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
                    scope_node_id=root.id,
                    workflow_key=key,
                    version=1,
                    title=spec["title"],
                    definition=spec["definition"],
                    status="published",
                )
            )
    return role_ids


def bootstrap(
    *,
    admin_username: str = "admin@abia.gov.ng",
    admin_password: str | None = None,
    hosts: list[str] | None = None,
) -> Seeded:
    """Provision the seed state (Abia) — kept for compatibility; see ``provision_state``."""
    return provision_state(
        "NG-AB",
        admin_username=admin_username,
        admin_password=admin_password,
        hosts=hosts or ["abia.syntegra.ng", "localhost", "127.0.0.1", "testserver"],
        lgas=LGAS,
    )


def provision_state(
    state_code: str,
    *,
    admin_username: str | None = None,
    admin_password: str | None = None,
    hosts: list[str] | None = None,
    lgas: list[tuple[str, str]] | None = None,
) -> Seeded:
    """Provision any of the 36 states or the FCT on this platform (idempotent) and join the clearance network."""
    from syntegra.core import uow
    from syntegra.governance import services as gov
    from syntegra.governance.models import ScopeNode
    from syntegra.iam import services as iam
    from syntegra.iam.models import AppUser

    state_code = state_code.upper()
    if state_code not in BY_CODE:
        raise ValueError(f"{state_code} is not a Nigerian state or the FCT")
    name, capital = BY_CODE[state_code]
    short = state_code.split("-")[1].lower()
    tid = _state_tenant(state_code, hosts or [f"{short}.syntegra.ng"])
    tenancy.clear_caches()
    ctx = context.system(tid, tid, correlation_id=f"provision-{state_code}")
    with context.use(ctx):
        _copy_code_lists(tid)
        out = Seeded(tid, uuid.UUID(int=0), uuid.UUID(int=0))
        with uow.command("registry", None, action="bootstrap", record_kind="tenant") as cmd:
            cmd.record_id = tid
            ng = ScopeNode.objects.filter(code="NG").first() or gov.add_node(
                cmd, parent=None, level="country", code="NG", name="Nigeria", ref_kind="tenant", ref_id=COUNTRY_TENANT
            )
            st = ScopeNode.objects.filter(code=state_code).first() or gov.add_node(
                cmd, parent=ng, level="state", code=state_code, name=name, ref_kind="tenant", ref_id=tid
            )
            out.country_scope_id, out.state_scope_id = ng.id, st.id
            for code, lga_name in lgas or [capital]:
                lga = ScopeNode.objects.filter(code=code).first() or gov.add_node(
                    cmd, parent=st, level="lga", code=code, name=lga_name
                )
                out.lga_scope_ids[code] = lga.id
            out.role_ids = seed_registry_config(cmd, st)
        from syntegra.hr import defaults as hr_defaults

        hr_defaults.seed(out.state_scope_id)
        from syntegra.funding import services as funding

        funding.seed_programmes(out.state_scope_id)
        if admin_username:
            admin = AppUser.objects.filter(username=admin_username).first()
            if admin is None:
                admin = iam.create_user(
                    ctx, username=admin_username, display_name=f"{name} Administrator", password=admin_password
                )
                iam.grant_role(ctx, user=admin, role_code="STA", scope_id=st.id)
            out.admin_user_id = admin.id
    join_network(state_code)
    return out
