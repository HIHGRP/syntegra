"""Roll import — onboarding an institution's existing roll in one step (part of FR-ADM-12, legacy data import).

When a school joins the platform its pupils are already enrolled: registering them one by one would run
probabilistic matching and the national clearance network for each child, which is right for an admission and
wrong for an onboarding roll. ``import_roll`` validates every row with the same rules as single registration
(names, sex, date of birth, a guardian with parental responsibility for every minor — FR-LRN-06), refuses exact
duplicates (same names, date of birth and sex already registered in the state, or twice in the roll), allocates a
contiguous run of Global Learner IDs from the state's leased block, and writes learners, guardians, guardian
links, identifiers and active primary enrolments in one audited command. Nothing is written if any row fails.
Probable (non-exact) matches are not searched here; a batch duplicate review of imported rolls is not automated yet.
The staged commit and 30-day rollback of FR-ADM-12 are not provided yet.
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from django.db import connections

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.ids import format_glid, uuid7
from syntegra.core.text import name_phonetic
from syntegra.families import services as families
from syntegra.families.domain import guardians as family_rules
from syntegra.families.models import Guardian, LearnerGuardian
from syntegra.families.services import GuardianInput
from syntegra.institutions.models import Institution
from syntegra.learners import services as lrn
from syntegra.learners.models import Enrolment, Learner

MAX_ROWS = 5000


@dataclass
class RollRow:
    given: str
    family: str
    date_of_birth: dt.date
    sex: str
    education_level: str
    middle: str | None = None
    state_of_origin: str | None = "NG-AB"
    guardian: GuardianInput | None = None
    programme_id: uuid.UUID | None = None
    cohort_label: str | None = None
    identifiers: dict[str, str] = field(default_factory=dict)
    class_group_id: uuid.UUID | None = None  # the ops-zone class (arm) the learner joins


@dataclass
class Imported:
    learner_id: uuid.UUID
    enrolment_id: uuid.UUID
    global_learner_id: str
    row: RollRow


def allocate_glids(alias: str, n: int) -> list[str]:
    """``n`` consecutive Global Learner IDs from the state's leased blocks (CD-07), under the registry lock; the
    state leases its next block from the national allocator when its blocks run out."""
    from syntegra.platform.glid import lease_block
    from syntegra.platform.models import GlidBlock

    ctx = context.require()
    assert ctx.state_tenant_id is not None
    out: list[str] = []
    seen: set[uuid.UUID] = set()
    for _attempt in range(3):
        blocks = [
            b
            for b in GlidBlock.objects.using("platform").filter(tenant_id=ctx.state_tenant_id).order_by("first_serial")
            if b.id not in seen
        ]
        with connections[alias].cursor() as cur:
            for b in blocks:
                seen.add(b.id)
                lo, hi = format_glid(b.first_serial)[:13], format_glid(b.last_serial)[:13]
                cur.execute(
                    "SELECT global_learner_id FROM learner WHERE tenant_id = %s AND global_learner_id >= %s "
                    "AND global_learner_id < %s ORDER BY global_learner_id DESC LIMIT 1 FOR UPDATE",
                    [ctx.state_tenant_id.bytes, lo, hi + "~"],
                )
                r = cur.fetchone()
                nxt = b.first_serial if r is None else int(r[0][4:8] + r[0][9:13]) + 1
                taken = set(out)
                while nxt <= b.last_serial and len(out) < n:
                    g = format_glid(nxt)
                    if g not in taken:
                        out.append(g)
                    nxt += 1
                if len(out) == n:
                    return out
        lease_block(ctx.state_tenant_id, n - len(out))
    raise ConflictError("GLID-EXHAUSTED", "Not enough Global Learner IDs", "The national allocator has no free block.")


def _stamp(objs: Iterable[Any], tenant_id: uuid.UUID, actor: uuid.UUID | None) -> list[Any]:
    out = list(objs)
    now = utcnow()
    for o in out:
        o.tenant_id = tenant_id
        if hasattr(o, "created_by"):
            o.created_by = actor
            o.created_at = now
        if hasattr(o, "updated_at"):
            o.updated_at = now
    return out


def _validate(rows: Sequence[RollRow], inst: Institution, start_on: dt.date) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    majority = families.majority_age(inst.scope_node_id, start_on)
    seen: dict[tuple[str, str, dt.date, str], int] = {}
    for i, r in enumerate(rows, start=1):
        problems: list[str] = []
        try:
            lrn._validate(
                lrn.RegisterLearner(
                    given=r.given, family=r.family, date_of_birth=r.date_of_birth, sex=r.sex,
                    institution_id=inst.id, education_level=r.education_level,
                )
            )  # fmt: skip
        except HardValidation as exc:
            problems += [f"{e['field']}: {e['message']}" for e in exc.errors or []]
        if not r.education_level:
            problems.append("education_level: required")
        minor = family_rules.is_minor(r.date_of_birth, start_on, majority)
        if minor and not (r.guardian and r.guardian.has_parental_responsibility):
            problems.append(
                "guardian: a learner under the age of majority needs a guardian with parental responsibility"
            )
        key = (r.given.strip().lower(), r.family.strip().lower(), r.date_of_birth, r.sex)
        if key in seen:
            problems.append(f"duplicate of row {seen[key]} in this roll")
        seen.setdefault(key, i)
        if problems:
            errors.append({"row": i, "name": f"{r.given} {r.family}", "problems": problems})
    # exact duplicates already registered in the state
    if not errors:
        dobs = {r.date_of_birth for r in rows}
        existing = {
            (lr.legal_given_name.lower(), lr.legal_family_name.lower(), lr.date_of_birth, lr.sex)
            for lr in Learner.objects.filter(date_of_birth__in=dobs).only(
                "legal_given_name", "legal_family_name", "date_of_birth", "sex"
            )
        }
        for i, r in enumerate(rows, start=1):
            if (r.given.strip().lower(), r.family.strip().lower(), r.date_of_birth, r.sex) in existing:
                errors.append(
                    {"row": i, "name": f"{r.given} {r.family}", "problems": ["already registered in the state"]}
                )
    return errors


def import_roll(
    institution_id: uuid.UUID, rows: Sequence[RollRow], *, start_on: dt.date | None = None, dry_run: bool = False
) -> dict[str, Any]:
    """Import an onboarding institution's roll (all or nothing). Returns counts, errors and the created records."""
    ctx = context.require()
    authz.require("learner:register", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id, ctx)
    if not rows or len(rows) > MAX_ROWS:
        raise HardValidation("LRN-ROLL-SIZE", "Roll size", f"Import between 1 and {MAX_ROWS} learners at a time.")
    start_on = start_on or dt.date.today()
    errors = _validate(rows, inst, start_on)
    result: dict[str, Any] = {"rows": len(rows), "errors": errors, "applied": False, "imported": []}
    if errors or dry_run:
        return result
    tenant, actor = ctx.state_tenant_id, ctx.actor_id
    assert tenant is not None
    with uow.command("registry", "learner:register", action="import_roll", record_kind="enrolment") as cmd:
        glids = allocate_glids(cmd.alias, len(rows))
        learners, guardians, links, enrolments, imported = [], [], [], [], []
        for r, glid in zip(rows, glids, strict=True):
            learner = Learner(
                id=uuid7(),
                global_learner_id=glid,
                legal_given_name=r.given.strip(),
                legal_middle_names=r.middle,
                legal_family_name=r.family.strip(),
                name_phonetic=name_phonetic(r.given, r.family),
                date_of_birth=r.date_of_birth,
                dob_precision="day",
                sex=r.sex,
                nationality="NG",
                state_of_origin=r.state_of_origin,
                identity_verified_level="unverified",
                status="active",
            )
            learners.append(learner)
            enr = Enrolment(
                id=uuid7(),
                scope_node_id=inst.scope_node_id,
                learner_id=learner.id,
                institution_id=inst.id,
                operating_tenant_id=inst.operating_tenant_id,
                education_level=r.education_level,
                programme_id=r.programme_id,
                cohort_label=r.cohort_label,
                class_group_id=r.class_group_id,
                is_primary=True,
                basis="admission",
                start_on=start_on,
                status="active",
            )
            enrolments.append(enr)
            if r.guardian is not None:
                g = r.guardian
                guardian = Guardian(
                    id=uuid7(),
                    given_name=g.given.strip(),
                    family_name=g.family.strip(),
                    title=g.title or None,
                    name_phonetic=name_phonetic(g.given, g.family),
                    phone=family_rules.normalise_phone(g.phone),
                    email=family_rules.normalise_email(g.email),
                    preferred_channel="sms" if g.phone else "email",
                    status="active",
                )
                guardians.append(guardian)
                links.append(
                    LearnerGuardian(
                        learner_id=learner.id,
                        guardian_id=guardian.id,
                        relationship=g.relationship,
                        has_parental_responsibility=g.has_parental_responsibility,
                        contact_priority=1,
                        lives_with=g.lives_with,
                        is_authorised_collector=g.is_authorised_collector,
                        is_payer=g.is_payer,
                        valid_from=start_on,
                    )
                )
            imported.append(Imported(learner.id, enr.id, glid, r))
        alias = cmd.alias
        Learner.unscoped.using(alias).bulk_create(_stamp(learners, tenant, actor), batch_size=1000)
        Guardian.unscoped.using(alias).bulk_create(_stamp(guardians, tenant, actor), batch_size=1000)
        LearnerGuardian.unscoped.using(alias).bulk_create(_stamp(links, tenant, actor), batch_size=1000)
        Enrolment.unscoped.using(alias).bulk_create(_stamp(enrolments, tenant, actor), batch_size=1000)
        for item in imported:
            if item.row.identifiers:
                lrn._add_identifiers(cmd, item.learner_id, item.row.identifiers)
        cmd.record_id = inst.id
        cmd.note(
            "roll_imported",
            None,
            {"institution_id": str(inst.id), "learners": len(rows), "first": glids[0], "last": glids[-1]},
        )
        cmd.emit(
            "LRN.ROLL_IMPORTED",
            aggregate_id=inst.id,
            aggregate_kind="institution",
            scope_node_id=inst.scope_node_id,
            payload={
                "institution_id": str(inst.id),
                "learners": len(rows),
                "first_glid": glids[0],
                "last_glid": glids[-1],
            },
        )
    result.update(applied=True, imported=imported)
    return result
