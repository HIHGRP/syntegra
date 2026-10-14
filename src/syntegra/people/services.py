"""Staff 360 services (MFS §11): staff master, posts and teaching authorisations."""

from __future__ import annotations

import datetime as dt
import uuid
from decimal import Decimal

from syntegra.core import uow
from syntegra.core.ids import format_staff_number
from syntegra.core.text import name_phonetic
from syntegra.people.models import Staff, StaffPost, StaffQualification


def create_staff(
    given: str,
    family: str,
    *,
    institution_id: uuid.UUID,
    scope_node_id: uuid.UUID,
    job_title: str = "Teacher",
    category: str = "teaching",
    user_id: uuid.UUID | None = None,
    email: str | None = None,
) -> tuple[Staff, StaffPost]:
    with uow.command("registry", "staff:manage", action="create", record_kind="staff") as cmd:
        serial = Staff.objects.count() + 1
        s = cmd.add(
            Staff(
                staff_number=format_staff_number(serial),
                given_name=given,
                family_name=family,
                name_phonetic=name_phonetic(given, family),
                email=email,
                user_id=user_id,
                status="active",
            )
        )
        p = cmd.add(
            StaffPost(
                scope_node_id=scope_node_id,
                staff_id=s.id,
                institution_id=institution_id,
                job_title=job_title,
                staff_category=category,
                contract="permanent",
                fte=Decimal("1.00"),
                valid_from=dt.date.today(),
            )
        )
        return s, p


def add_authorisation(
    staff_id: uuid.UUID,
    subject_id: uuid.UUID,
    levels: list[str],
    *,
    issuer: str = "TRCN",
    expires_on: dt.date | None = None,
    verified: bool = True,
) -> StaffQualification:
    with uow.command("registry", "staff:manage", action="authorise", record_kind="staff") as cmd:
        q = cmd.add(
            StaffQualification(
                staff_id=staff_id,
                kind="teaching_authorisation",
                title="Teaching authorisation",
                subject_id=subject_id,
                levels=levels,
                issuer=issuer,
                expires_on=expires_on,
                issued_on=dt.date.today(),
                verification="verified" if verified else "pending",
            )
        )
        cmd.record_id = staff_id
        return q


def is_authorised(staff_id: uuid.UUID, subject_id: uuid.UUID, level: str, on: dt.date | None = None) -> bool:
    on = on or dt.date.today()
    for q in StaffQualification.objects.filter(
        staff_id=staff_id, kind="teaching_authorisation", subject_id=subject_id, verification="verified"
    ):
        if q.expires_on and q.expires_on < on:
            continue
        if not q.levels or level in q.levels:
            return True
    return False
