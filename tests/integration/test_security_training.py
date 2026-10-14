"""CR-004: the security agencies' education and training institutions, each under its own agency structure."""

from __future__ import annotations

import datetime as dt
import re
import uuid
from collections.abc import Iterator
from typing import Any

import pytest

from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound

pytestmark = pytest.mark.django_db(databases="__all__")
HOST = "fse.testserver"


@pytest.fixture(scope="session")
def fse(django_db_setup: Any, django_db_blocker: Any) -> Iterator[Any]:
    """Provision the Federal Security Education registry once and load the reference data."""
    from syntegra.core import tenancy
    from syntegra.security_training import registry

    with django_db_blocker.unblock():
        p = registry.provision(hosts=[HOST])
        seeded = registry.seed_reference()
    tenancy.clear_caches()
    yield p, seeded
    tenancy.clear_caches()


def use(ctx: Any) -> Any:
    from syntegra.core import context

    return context.use(ctx)


def node(code: str) -> uuid.UUID:
    from syntegra.core import context
    from syntegra.governance.models import ScopeNode
    from syntegra.security_training import registry

    with context.use(registry.system_context()):
        return uuid.UUID(str(ScopeNode.objects.get(code=code).id))


def as_fse(role: str, scope_code: str) -> Any:
    """(context, user) for a new user holding ``role`` at the FSE scope node ``scope_code``; use with context.use."""
    from syntegra.core import authz, context
    from syntegra.core.context import Context
    from syntegra.iam import services as iam
    from syntegra.security_training import registry

    sysctx = registry.system_context()
    with context.use(sysctx):
        u = iam.create_user(
            sysctx,
            username=f"{role.lower()}-{uuid.uuid4().hex[:8]}@fse.test",
            display_name=role,
            password="correct-horse-battery",
        )
        g = iam.grant_role(sysctx, user=u, role_code=role, scope_id=node(scope_code))
    tid = registry.tenant_id()
    base = Context(tenant_id=tid, state_tenant_id=tid, actor_kind="user", actor_id=u.id)
    with context.use(base):
        return authz.grant_context(base, g.id), u


def test_every_agency_is_modelled_with_its_own_structure_ranks_institutions_and_courses(fse: Any) -> None:
    from syntegra.core import context
    from syntegra.security_training import registry
    from syntegra.security_training.models import (
        AgencyRank,
        AgencyUnit,
        SecurityAgency,
        SecurityCourse,
        SecurityCourseModule,
        SecurityInstitution,
    )

    with context.use(registry.system_context()):
        agencies = {a.code: a for a in SecurityAgency.objects.all()}
        assert set(agencies) == {"DHQ", "NA", "NN", "NAF", "NPF", "NSCDC", "NCOS", "NIS", "FFS", "NCS", "FRSC",
                                 "NDLEA", "EFCC", "DSS"}  # fmt: skip
        for a in agencies.values():  # each agency has its own headquarters at the top of its structure
            assert AgencyUnit.objects.filter(agency_id=a.id, unit_type="headquarters", parent_unit_id=None).count() == 1
        npf_states = AgencyUnit.objects.filter(agency_id=agencies["NPF"].id, unit_type="state_command").count()
        assert npf_states == 37  # 36 states and the FCT
        assert AgencyUnit.objects.filter(agency_id=agencies["FRSC"].id, unit_type="sector_command").count() == 37
        tradoc = AgencyUnit.objects.get(agency_id=agencies["NA"].id, code="TRADOC")
        assert AgencyUnit.objects.get(pk=tradoc.parent_unit_id).code == "AHQ"
        assert [r.code for r in AgencyRank.objects.filter(agency_id=agencies["NPF"].id).order_by("seniority")][
            -1
        ] == "IGP"
        assert (
            AgencyRank.objects.filter(agency_id=agencies["NA"].id, rank_category="commissioned_officer").count() == 10
        )
        profiles = list(SecurityInstitution.objects.all())
        assert len(profiles) == 33 and {p.agency_id for p in profiles} == {a.id for a in agencies.values()}
        for p in profiles:  # every institution has its own catalogue
            assert SecurityCourse.objects.filter(institution_id=p.institution_id).exists()
        for c in SecurityCourse.objects.all():
            n = SecurityCourseModule.objects.filter(course_id=c.id).count()
            assert (n > 0) == c.content_held
        statuses = set(SecurityAgency.objects.values_list("data_status", flat=True)) | set(
            SecurityInstitution.objects.values_list("data_status", flat=True)
        )
        assert "verified" not in statuses  # agencies confirm their own data before live use
        titles = " ".join(SecurityCourseModule.objects.values_list("title", flat=True)).lower()
        assert not re.search(r"weapon|firing|tactic|ammunition|explosive", titles)  # syllabus headings only
    assert fse[1].agencies == 14 or fse[1].agencies == 0  # idempotent: a second seed adds nothing


def test_access_follows_each_agency_structure(fse: Any) -> None:
    from syntegra.security_training import services as sti

    police, _ = as_fse("SADM", "NPF")
    with use(police):
        codes = {a["code"] for a in sti.directory()}
        assert codes == {"NPF"}
        polac = next(i for i in sti.directory()[0]["institutions"] if i["short_name"] == "POLAC")
        assert sti.institution(polac["institution_id"])["agency"]["code"] == "NPF"
    root, _ = as_fse("SADM", "NG-FSE")
    with use(root):
        everyone = sti.directory()
        nda = next(i for a in everyone if a["code"] == "DHQ" for i in a["institutions"] if i["short_name"] == "NDA")
    assert len(everyone) == 14
    with use(police), pytest.raises(NotFound):
        sti.institution(nda["institution_id"])  # the police cannot open an armed-forces institution
    tradoc, _ = as_fse("SADM", "NA.TRADOC")
    with use(tradoc):
        names = {i["short_name"] for a in sti.directory() for i in a["institutions"]}
    assert {"NASI", "NASA", "Depot NA"} <= names and "NAUB" not in names  # NAUB is under Army HQ, not TRADOC
    officer, _ = as_fse("STO", "NPF.POLAC")
    with use(officer):
        assert [i["short_name"] for a in sti.directory() for i in a["institutions"]] == ["POLAC"]


def test_state_registries_do_not_see_security_training(world: Any, as_user: Any, fse: Any) -> None:
    from syntegra.security_training import services as sti
    from syntegra.security_training.models import SecurityAgency

    with as_user("STA", world.state_scope):
        assert SecurityAgency.objects.count() == 0  # a different registry tenant
        with pytest.raises(Forbidden):
            sti.directory()


def test_course_curriculum_and_trainee_outcomes(fse: Any) -> None:
    from syntegra.core import context
    from syntegra.learners import services as learners
    from syntegra.learners.models import Enrolment
    from syntegra.security_training import services as sti
    from syntegra.security_training.models import SecurityCourse

    root, _ = as_fse("SADM", "NG-FSE")
    with use(root):
        nda = next(
            i for a in sti.directory() if a["code"] == "DHQ" for i in a["institutions"] if i["short_name"] == "NDA"
        )
        rc = next(c for c in sti.institution(nda["institution_id"])["courses"] if c["code"] == "RC")
        detail = sti.course(rc["id"])
        assert detail["award"] == "degree" and detail["accrediting_body"] == "NUC"
        assert [m["area"] for m in detail["modules"]][:3] == ["academic", "professional_core", "leadership_ethics"]
        assert detail["target_ranks"] == [{"code": "OCDT", "title": "Officer Cadet"}]
        niss = next(i for a in sti.directory() if a["code"] == "DSS" for i in a["institutions"])
        eimc = sti.course(sti.institution(niss["institution_id"])["courses"][0]["id"])
        assert eimc["content_held"] is False and eimc["modules"] == []
        intake = sti.create_intake(
            rc["id"], intake_code="rc78", name="78 Regular Course", starts_on=dt.date(2026, 9, 7), capacity=2
        )
        with pytest.raises(ConflictError):
            sti.create_intake(rc["id"], intake_code="RC78", name="dup", starts_on=dt.date(2026, 9, 7))
    officer, _ = as_fse("STO", "DHQ.NDA")
    with use(officer):
        cadet = learners.register(
            learners.RegisterLearner(
                given="Musa",
                family="Danjuma",
                date_of_birth=dt.date(2006, 3, 4),
                sex="male",
                institution_id=nda["institution_id"],
                education_level="UG100",
                identifiers={"SVC-NO": "N/18001"},
            )
        ).learner
        other = learners.register(
            learners.RegisterLearner(
                given="Amina",
                family="Bello",
                date_of_birth=dt.date(2006, 7, 9),
                sex="female",
                institution_id=nda["institution_id"],
                education_level="UG100",
            )
        ).learner
        with pytest.raises(HardValidation, match="Unknown rank"):
            sti.add_trainee(intake.id, cadet.id, rank_code="IGP")
        rec = sti.add_trainee(intake.id, cadet.id, rank_code="OCDT")
        sti.add_trainee(intake.id, other.id)
        with pytest.raises(ConflictError):
            sti.add_trainee(intake.id, cadet.id)  # already on the intake / intake full
        with pytest.raises(HardValidation, match="reason"):
            sti.record_outcome(rec.id, "relegated")
        sti.record_outcome(rec.id, "commissioned", result="Second Class Upper; 3rd in order of merit")
        with pytest.raises(ConflictError):
            sti.record_outcome(rec.id, "failed", reason="recorded twice by mistake")
        roll = sti.intake(intake.id)
        assert {r["name"]: r["outcome"] for r in roll["trainees"]} == {"Musa Danjuma": "commissioned",
                                                                       "Amina Bello": "in_training"}  # fmt: skip
        assert roll["trainees"][1]["rank_at_entry"] == "Officer Cadet"
        assert sti.learner_courses(cadet.id)[0]["outcome"] == "commissioned"
        assert Enrolment.objects.get(learner_id=cadet.id).status == "completed"
        assert learners.identifiers_of(cadet.id)[0]["scheme"] == "SVC-NO"
    from syntegra.security_training import registry

    with context.use(registry.system_context()):
        assert SecurityCourse.objects.filter(code="RC").count() == 1


def test_security_training_pages(fse: Any, client: Any, settings: Any) -> None:
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, HOST]
    _, u = as_fse("SADM", "NG-FSE")
    client.handler.enforce_csrf_checks = False
    r = client.post("/sign-in", {"username": u.username, "password": "correct-horse-battery"}, HTTP_HOST=HOST)
    assert r.status_code == 302
    page = client.get("/security-training", HTTP_HOST=HOST).content
    assert b"Nigerian Defence Academy" in page and b"Nigeria Police Academy" in page and b"Security training" in page
    inst = re.search(rb'href="/security-training/institutions/([0-9a-f-]{36})">Nigerian Defence Academy', page).group(1)
    page = client.get(f"/security-training/institutions/{inst.decode()}", HTTP_HOST=HOST).content
    assert b"Regular Course" in page and b"NUC" in page
    course = re.search(rb'href="/security-training/courses/([0-9a-f-]{36})">Regular Course', page).group(1)
    page = client.get(f"/security-training/courses/{course.decode()}", HTTP_HOST=HOST).content
    assert b"Leadership, character and ethics" in page and b"Officer Cadet" in page
    agency = re.search(
        rb'href="/security-training/agencies/([0-9a-f-]{36})">Nigerian Army',
        client.get("/security-training", HTTP_HOST=HOST).content,
    ).group(1)
    page = client.get(f"/security-training/agencies/{agency.decode()}", HTTP_HOST=HOST).content
    assert b"Training and Doctrine Command" in page and b"Lieutenant General" in page
    assert client.get("/api/v1/security-training/agencies", HTTP_HOST=HOST).status_code == 200
