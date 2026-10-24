"""Guardians (FR-FAM-01, FR-FAM-02) and the guardian rule at registration (FR-LRN-05, FR-LRN-06).

* ``majority_age`` — the age of majority is the state's published policy ``LRN-AGE-OF-MAJORITY``.
* ``check`` — validates the guardians given for a learner, including the parental-responsibility rule for minors.
* ``link`` — inside the registration command: finds each guardian in the registry (NIN, then phone or e-mail with
  agreeing names) or creates the master, then records the learner–guardian relationship. Re-submitting the same
  guardian never creates a second master or a second current link.
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from syntegra.core import context, crypto, policy, uow
from syntegra.core.errors import HardValidation
from syntegra.core.text import name_phonetic, name_similarity
from syntegra.families.domain import guardians as rules
from syntegra.families.domain.guardians import GuardianInput
from syntegra.families.models import Guardian, LearnerGuardian
from syntegra.mdm.models import ExternalIdentifier

__all__ = ["GuardianInput", "LinkedGuardian", "check", "guardians_of", "link", "majority_age"]


@dataclass
class LinkedGuardian:
    guardian: Guardian
    link: LearnerGuardian
    created: bool  # a new guardian master (False: matched an existing guardian)
    linked: bool  # a new learner–guardian link (False: already linked)


def majority_age(scope_node_id: uuid.UUID | None, on: dt.date | None = None) -> int:
    """FR-LRN-05: the jurisdiction's age of majority, never hard-coded in the services."""
    rule = policy.effective_rule("LRN-AGE-OF-MAJORITY", scope_node_id, on=on) if scope_node_id else None
    if rule is None:
        return rules.DEFAULT_MAJORITY
    return int(rule.parameters.get("age", rules.DEFAULT_MAJORITY))


def responsible_links(learner_id: uuid.UUID, on: dt.date) -> int:
    return (
        LearnerGuardian.objects.filter(learner_id=learner_id, has_parental_responsibility=True, valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .count()
    )


def check(
    guardians: Sequence[GuardianInput],
    *,
    date_of_birth: dt.date,
    on: dt.date,
    scope_node_id: uuid.UUID | None,
    learner_id: uuid.UUID | None = None,
    learner_nin: str | None = None,
) -> None:
    """Raise ``HardValidation`` (422) if the guardians do not satisfy FR-LRN-06 and FR-FAM-01."""
    majority = majority_age(scope_node_id, on)
    errs = rules.errors_for(
        guardians,
        minor=rules.is_minor(date_of_birth, on, majority),
        majority=majority,
        existing_with_responsibility=responsible_links(learner_id, on) if learner_id else 0,
        learner_nin=learner_nin,
    )
    if errs:
        raise HardValidation("FAM-GUARDIANS", "Guardian details need attention", errors=errs)


def _find(g: GuardianInput, phone: str | None, email: str | None, nin_hmac: bytes | None) -> Guardian | None:
    by_nin: set[uuid.UUID] = set()
    if nin_hmac:
        by_nin = set(
            ExternalIdentifier.objects.filter(person_kind="guardian", scheme="NG-NIN", value_hmac=nin_hmac).values_list(
                "person_id", flat=True
            )
        )
    candidates = Guardian.objects.exclude(status="merged")
    found: list[Guardian] = []
    if by_nin:
        found += list(candidates.filter(id__in=by_nin))
    if phone:
        found += list(candidates.filter(phone=phone)[:50])
    if email:
        found += list(candidates.filter(email=email)[:50])
    for c in found:
        if rules.same_person(
            g,
            c.given_name,
            c.family_name,
            nin_matches=c.id in by_nin,
            phone_matches=bool(phone and c.phone == phone),
            email_matches=bool(email and c.email == email),
            name_score=name_similarity,
        ):
            return c
    return None


def link(
    cmd: uow.Command, learner_id: uuid.UUID, guardians: Sequence[GuardianInput], *, valid_from: dt.date
) -> list[LinkedGuardian]:
    """Find-or-create each guardian and link them to the learner (call inside the registration command)."""
    ctx = context.require()
    out: list[LinkedGuardian] = []
    current = {
        lg.guardian_id: lg
        for lg in LearnerGuardian.unscoped.using(cmd.alias)
        .filter(tenant_id=ctx.state_tenant_id, learner_id=learner_id)
        .exclude(valid_to__lt=valid_from)
    }
    priority = max([lg.contact_priority or 0 for lg in current.values()], default=0)
    for g in guardians:
        phone, email = rules.normalise_phone(g.phone), rules.normalise_email(g.email)
        nin = "".join(g.nin.split()) if g.nin else None
        nin_hmac = crypto.lookup_hmac(nin, scheme="NG-NIN", tenant_id=ctx.state_tenant_id) if nin else None
        guardian = _find(g, phone, email, nin_hmac)
        created = guardian is None
        if guardian is None:
            guardian = cmd.add(
                Guardian(
                    given_name=g.given.strip(),
                    family_name=g.family.strip(),
                    title=g.title or None,
                    name_phonetic=name_phonetic(g.given, g.family),
                    phone=phone,
                    email=email,
                    preferred_language=g.preferred_language,
                    preferred_channel=g.preferred_channel or ("sms" if phone else "email"),
                    status="active",
                )
            )
            cmd.emit("FAM.GUARDIAN_CREATED", aggregate_id=guardian.id, aggregate_kind="guardian",
                     payload={"guardian_id": guardian.id})  # fmt: skip
        else:
            fill: dict[str, Any] = {
                k: v for k, v in (("phone", phone), ("email", email)) if v and not getattr(guardian, k)
            }
            if fill:
                cmd.update(guardian, **fill)
        if (
            nin
            and nin_hmac
            and not ExternalIdentifier.objects.filter(
                person_kind="guardian", person_id=guardian.id, scheme="NG-NIN"
            ).exists()
        ):
            cmd.add(
                ExternalIdentifier(
                    person_kind="guardian",
                    person_id=guardian.id,
                    scheme="NG-NIN",
                    value_hmac=nin_hmac,
                    value_national_hmac=crypto.national_lookup_hmac(nin, scheme="NG-NIN"),
                    value_enc=crypto.encrypt(nin, purpose="id:NG-NIN", tenant_id=ctx.state_tenant_id),
                    value_last4=crypto.last4(nin),
                    status="unverified",
                )
            )
        existing = current.get(guardian.id)
        if existing is not None:
            out.append(LinkedGuardian(guardian, existing, created, False))
            continue
        priority += 1
        lg = cmd.add(
            LearnerGuardian(
                learner_id=learner_id,
                guardian_id=guardian.id,
                relationship=g.relationship,
                has_parental_responsibility=g.has_parental_responsibility,
                contact_priority=priority,
                lives_with=g.lives_with,
                is_authorised_collector=g.is_authorised_collector,
                is_payer=g.is_payer,
                valid_from=valid_from,
            )
        )
        current[guardian.id] = lg
        out.append(LinkedGuardian(guardian, lg, created, True))
    return out


def guardians_of(learner_id: uuid.UUID, on: dt.date | None = None) -> list[dict[str, Any]]:
    """Current guardians of a learner, by contact priority; contact details hidden where contact is restricted."""
    on = on or dt.date.today()
    links = list(
        LearnerGuardian.objects.filter(learner_id=learner_id, valid_from__lte=on)
        .exclude(valid_to__lt=on)
        .order_by("contact_priority")
    )
    people = {g.id: g for g in Guardian.objects.filter(id__in=[lg.guardian_id for lg in links])}
    rows = []
    for lg in links:
        g = people.get(lg.guardian_id)
        if g is None:
            continue
        rows.append(
            {
                "guardian_id": g.id,
                "name": " ".join(x for x in (g.title, g.given_name, g.family_name) if x),
                "relationship": lg.relationship,
                "has_parental_responsibility": lg.has_parental_responsibility,
                "contact_priority": lg.contact_priority,
                "lives_with": lg.lives_with,
                "is_authorised_collector": lg.is_authorised_collector and not lg.is_contact_restricted,
                "is_payer": lg.is_payer,
                "is_contact_restricted": lg.is_contact_restricted,
                "phone": None if lg.is_contact_restricted else g.phone,
                "email": None if lg.is_contact_restricted else g.email,
            }
        )
    return rows
