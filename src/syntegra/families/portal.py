"""Who a parent or a learner is when they sign in (MFS FAM-03, CR-009 phase 4).

A parent's account is the guardian's own (``app_user.person_kind = guardian``) and holds the parent role at the
school. A school-wide grant is what lets the account into the school's pages, but a parent never sees the school:
every parent page starts from :func:`children` — the learners the guardian is currently linked to with parental
responsibility, enrolled in a class in the grant's school — and every action on a learner checks
:func:`require_child` first. A link marked contact-restricted gives the parent nothing about that child: the court
order behind the flag is held by the safeguarding lead, and the safe reading of an order we cannot see is that it
withholds information.

A learner's account (``person_kind = learner``) sees only that learner: :func:`me_learner`.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from syntegra.core import context
from syntegra.core.errors import Forbidden
from syntegra.families.models import Guardian, LearnerGuardian


def _account() -> Any:
    from syntegra.iam.models import AppUser

    ctx = context.require()
    if ctx.actor_kind != "user" or ctx.actor_id is None:
        return None
    return AppUser.objects.filter(pk=ctx.actor_id).first()


def guardian() -> Guardian | None:
    """The guardian record behind the signed-in account, if it is a parent's."""
    u = _account()
    if u is None or u.person_kind != "guardian" or u.person_id is None:
        return None
    g: Guardian | None = Guardian.objects.filter(pk=u.person_id, status="active").first()
    return g


def guardian_name(g: Guardian) -> str:
    return " ".join(x for x in (g.title, g.given_name, g.family_name) if x)


def _classes(learner_ids: list[uuid.UUID], on: dt.date) -> dict[uuid.UUID, Any]:
    """Each learner's current class arm within the caller's scope."""
    from syntegra.academic.models import ClassGroup, ClassMembership

    members = list(
        ClassMembership.objects.filter(learner_id__in=learner_ids, is_arm=True, valid_from__lte=on).exclude(
            valid_to__lt=on
        )
    )
    groups = {
        c.id: c
        for c in ClassGroup.objects.in_scope().filter(id__in=[m.class_group_id for m in members], status="active")
    }
    return {m.learner_id: groups[m.class_group_id] for m in members if m.class_group_id in groups}


def children(on: dt.date | None = None) -> list[dict[str, Any]]:
    """The signed-in parent's children at this school, eldest first."""
    from syntegra.learners.models import Learner

    on = on or dt.date.today()
    g = guardian()
    if g is None:
        return []
    links = list(
        LearnerGuardian.objects.filter(
            guardian_id=g.id, has_parental_responsibility=True, is_contact_restricted=False, valid_from__lte=on
        ).exclude(valid_to__lt=on)
    )
    ids = [lg.learner_id for lg in links]
    rel = {lg.learner_id: lg.relationship for lg in links}
    classes = _classes(ids, on)
    learners = Learner.objects.filter(id__in=list(classes), status__in=("registered", "active"))
    rows = [
        {
            "id": lr.id,
            "name": f"{lr.preferred_name or lr.legal_given_name} {lr.legal_family_name}",
            "given": lr.preferred_name or lr.legal_given_name,
            "class_id": classes[lr.id].id,
            "class_name": classes[lr.id].name,
            "institution_id": classes[lr.id].institution_id,
            "relationship": rel.get(lr.id),
            "date_of_birth": lr.date_of_birth,
        }
        for lr in learners
    ]
    return sorted(rows, key=lambda r: r["date_of_birth"])


def require_child(learner_id: uuid.UUID) -> dict[str, Any]:
    """The child, when the signed-in parent may act for them; otherwise refuse."""
    for c in children():
        if c["id"] == learner_id:
            return c
    raise Forbidden("You can only see and act for your own children at this school.", code="FAM-OWN")


def me_learner(on: dt.date | None = None) -> dict[str, Any] | None:
    """The signed-in learner, with their class at this school."""
    from syntegra.learners.models import Learner

    on = on or dt.date.today()
    u = _account()
    if u is None or u.person_kind != "learner" or u.person_id is None:
        return None
    lr = Learner.objects.filter(pk=u.person_id).first()
    if lr is None:
        return None
    cls = _classes([lr.id], on).get(lr.id)
    if cls is None:
        return None
    return {
        "id": lr.id,
        "name": f"{lr.preferred_name or lr.legal_given_name} {lr.legal_family_name}",
        "given": lr.preferred_name or lr.legal_given_name,
        "class_id": cls.id,
        "class_name": cls.name,
        "institution_id": cls.institution_id,
    }


def is_parent() -> bool:
    return guardian() is not None


def parents_of(learner_ids: list[uuid.UUID], on: dt.date | None = None) -> dict[uuid.UUID, list[dict[str, Any]]]:
    """The guardians the school may contact about each learner: parental responsibility, not contact-restricted.
    Each comes with the account they sign in with (None when they have none yet)."""
    from syntegra.iam.models import AppUser

    on = on or dt.date.today()
    links = list(
        LearnerGuardian.objects.filter(
            learner_id__in=learner_ids, has_parental_responsibility=True, is_contact_restricted=False,
            valid_from__lte=on,
        )
        .exclude(valid_to__lt=on)
        .order_by("contact_priority")
    )  # fmt: skip
    people = {g.id: g for g in Guardian.objects.filter(id__in=[lg.guardian_id for lg in links], status="active")}
    accounts = {
        u.person_id: u
        for u in AppUser.objects.filter(
            person_kind="guardian", person_id__in=list(people), status__in=("active", "invited")
        )
    }
    out: dict[uuid.UUID, list[dict[str, Any]]] = {lid: [] for lid in learner_ids}
    for lg in links:
        g = people.get(lg.guardian_id)
        if g is None:
            continue
        acct = accounts.get(g.id)
        out[lg.learner_id].append(
            {
                "guardian_id": g.id,
                "name": guardian_name(g),
                "relationship": lg.relationship,
                "user_id": acct.id if acct is not None and acct.status == "active" else None,
                "phone": g.phone,
                "language": g.preferred_language,
            }
        )
    return out
