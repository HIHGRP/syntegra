"""University students on the single registration path: programme, intake cohort, JAMB and matriculation numbers."""

import datetime as dt
import re

import pytest

from syntegra.core.errors import HardValidation

pytestmark = pytest.mark.django_db(databases="__all__")


@pytest.fixture
def university(world, as_user):  # type: ignore[no-untyped-def]
    from syntegra.academic import services as academic
    from syntegra.institutions import services as inst

    with as_user("STA", world.state_scope):
        uni = inst.register(
            inst.RegisterInstitution(
                name="Abia State University, Uturu",
                category="university",
                ownership="state",
                lga_scope_id=world.lga2_scope,
                address={"town": "Uturu"},
                levels=["UG100", "UG200", "UG300", "UG400", "PG"],
                location=(7.25, 5.83),
                capacity=25000,
            )
        )
        csc = academic.create_programme(
            uni.id, "csc", "B.Sc. Computer Science", duration_terms=8, accreditation_status="full"
        )
        other = academic.create_programme(world.institution.id, "SCI", "Science stream")
    return uni, csc, other


def student(uni, csc, **kw):  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    base = {
        "given": "Chinedu",
        "family": "Okafor",
        "date_of_birth": dt.date(2007, 11, 2),
        "sex": "male",
        "institution_id": uni.id,
        "education_level": "UG100",
        "programme_id": csc.id,
        "cohort_label": "2026/2027 entry",
        "identifiers": {"JAMB-REG": "2026 1234 5678 AB", "INST-ID": "ABSU/CSC/26/0142"},
    }
    return services.RegisterLearner(**{**base, **kw})


def test_university_student_registers_with_programme_and_identifiers(university, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    uni, csc, _ = university
    assert csc.code == "CSC"
    with as_user("HEAD", uni.scope_node_id):
        with pytest.raises(HardValidation, match="Some fields"):
            services.register(student(uni, csc, identifiers={"INST-ID": "ABSU#26"}))
        r = services.register(student(uni, csc))
        ids = services.identifiers_of(r.learner.id)
    assert r.outcome == "created" and r.guardians == []  # an adult student: no guardian required
    assert r.enrolment.programme_id == csc.id and r.enrolment.cohort_label == "2026/2027 entry"
    assert r.enrolment.education_level == "UG100"
    assert {i["scheme"]: i["last4"] for i in ids} == {"INST-ID": "0142", "JAMB-REG": "78AB"}  # ABSU/CSC/26/0142


def test_programme_must_belong_to_the_university_and_identifiers_to_one_person(university, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    uni, csc, other = university
    ok = {"JAMB-REG": "202612345678AB"}
    with as_user("HEAD", uni.scope_node_id):
        with pytest.raises(HardValidation) as e:
            services.register(student(uni, csc, programme_id=other.id, identifiers=ok))
        assert e.value.errors[0]["field"] == "programme_id"
        first = services.register(student(uni, csc, identifiers=ok))
        with pytest.raises(HardValidation) as e:
            services.register(
                student(
                    uni,
                    csc,
                    given="Ngozi",
                    family="Eze",
                    sex="female",
                    date_of_birth=dt.date(2008, 1, 5),
                    identifiers=ok,
                )
            )
    assert e.value.errors[0]["field"] == "identifiers[JAMB-REG]"
    assert first.learner.global_learner_id in e.value.errors[0]["message"]


def test_university_registration_page(world, university, client) -> None:  # type: ignore[no-untyped-def]
    from tests.conftest import make_user

    uni, csc, _ = university
    u, _ = make_user(world, "HEAD", uni.scope_node_id)
    client.handler.enforce_csrf_checks = False
    client.post("/sign-in", {"username": u.username, "password": "correct-horse-battery"})
    page = client.get("/learners/new").content
    assert b"JAMB registration number" in page and b"B.Sc. Computer Science (CSC)" in page
    assert str(uni.id).encode() in re.search(rb'data-institutions="([^"]*)"', page).group(1)
    r = client.post(
        "/learners/new",
        {
            "institution_id": str(uni.id),
            "education_level": "UG100",
            "programme_id": str(csc.id),
            "cohort_label": "2026/2027 entry",
            "jamb_reg": "202687654321CD",
            "matric_no": "ABSU/CSC/26/0177",
            "given": "Adaobi",
            "family": "Nwankwo",
            "date_of_birth": "2007-04-18",
            "sex": "female",
        },
    )
    assert b"Registered" in r.content and b"100 level of B.Sc. Computer Science" in r.content, r.content[:3000]
    lid = re.search(rb'href="/learners/([0-9a-f-]{36})"', r.content).group(1).decode()
    learner_page = client.get(f"/learners/{lid}").content
    assert (
        b"JAMB registration" in learner_page and b"21CD" in learner_page and b"B.Sc. Computer Science" in learner_page
    )
