"""Guardians at registration: FR-LRN-05 (age of majority is policy), FR-LRN-06 (a guardian with parental
responsibility for minors), FR-FAM-01 (guardians are matched before creation), FR-FAM-02 (the relationship)."""

import datetime as dt

import pytest

from syntegra.core.errors import HardValidation
from tests.conftest import guardian

pytestmark = pytest.mark.django_db(databases="__all__")


def child(world, given="Tobi", family="Eze", dob=dt.date(2014, 5, 2), guardians=None, nin=None):  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    return services.RegisterLearner(
        given=given,
        family=family,
        date_of_birth=dob,
        sex="male",
        institution_id=world.institution.id,
        education_level="jss_1",
        nin=nin,
        guardians=guardians or [],
    )


def test_a_minor_needs_a_guardian_with_parental_responsibility(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    with as_user("HEAD", world.institution.scope_node_id):
        with pytest.raises(HardValidation) as e:
            services.register(child(world))
        assert e.value.errors[0]["field"] == "guardians" and "under 18" in e.value.errors[0]["message"]
        uncle = guardian("Eze", "Obinna", relationship="aunt_uncle", has_parental_responsibility=False)
        with pytest.raises(HardValidation):
            services.register(child(world, guardians=[uncle]))
        # a child in care: the social worker holds parental responsibility
        sw = guardian("Bello", "Hauwa", relationship="social_worker", email="h.bello@abia-sw.gov.ng", phone=None)
        r = services.register(child(world, guardians=[sw, uncle]))
    assert [
        (g.link.relationship, g.link.has_parental_responsibility, g.link.contact_priority) for g in r.guardians
    ] == [
        ("social_worker", True, 1),
        ("aunt_uncle", False, 2),
    ]


def test_adults_need_no_guardian(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    with as_user("HEAD", world.institution.scope_node_id):
        r = services.register(
            child(world, given="Kelechi", dob=dt.date(2000, 1, 9))
        )  # adult learner, e.g. evening class
    assert r.enrolment is not None and r.guardians == []


def test_age_of_majority_comes_from_state_policy(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.core import context
    from syntegra.families import services as families
    from syntegra.governance.models import PolicyRule
    from syntegra.learners import services
    from tests.conftest import system_ctx

    with context.use(system_ctx()):
        assert families.majority_age(world.state_scope) == 18
        PolicyRule.objects.filter(rule_key="LRN-AGE-OF-MAJORITY").update(parameters={"age": 21})
        assert families.majority_age(world.institution.scope_node_id) == 21
    with as_user("HEAD", world.institution.scope_node_id), pytest.raises(HardValidation, match="Guardian details"):
        services.register(child(world, given="Amara", dob=dt.date(2006, 1, 1)))  # 20 years old


def test_guardians_are_matched_not_duplicated(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.families.models import Guardian, LearnerGuardian
    from syntegra.learners import services

    mum = guardian("Eze", "Chinwe", phone="0803 111 2222", nin="40000000001")
    with as_user("HEAD", world.institution.scope_node_id):
        first = services.register(child(world, given="Tobi", guardians=[mum]))
        # same mother, phone written differently, for a sibling: matched by phone and name
        again = guardian("Eze", "Chinwe", phone="+234 803 111 2222")
        sibling = services.register(child(world, given="Ada", dob=dt.date(2016, 8, 1), guardians=[again]))
        # same phone, different name (shared family phone): a different person
        dad = guardian("Eze", "Uche", phone="08031112222", relationship="father")
        third = services.register(child(world, given="Ike", dob=dt.date(2017, 3, 3), guardians=[dad]))
        # NIN alone identifies, whatever the phone
        by_nin = guardian("Eze", "Chinwe", phone="0809 999 0000", nin="4000 0000 001")
        fourth = services.register(child(world, given="Nkem", dob=dt.date(2018, 4, 4), guardians=[by_nin]))
    assert first.guardians[0].created and not sibling.guardians[0].created
    assert sibling.guardians[0].guardian.id == first.guardians[0].guardian.id
    assert third.guardians[0].created and third.guardians[0].guardian.id != first.guardians[0].guardian.id
    assert fourth.guardians[0].guardian.id == first.guardians[0].guardian.id
    g = Guardian.unscoped.get(pk=first.guardians[0].guardian.id)
    assert g.phone == "+2348031112222" and g.name_phonetic
    assert LearnerGuardian.unscoped.filter(guardian_id=g.id).count() == 3


def test_guardian_validation_and_distinct_identities(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    with as_user("HEAD", world.institution.scope_node_id), pytest.raises(HardValidation) as e:
        services.register(
            child(
                world,
                nin="50000000002",
                guardians=[guardian("Eze", "Ngo", phone="12", email="not-an-email", nin="50000000002")],
            )
        )
    fields = {x["field"] for x in e.value.errors}
    assert {"guardians[0].phone", "guardians[0].email", "guardians[0].nin"} <= fields


def test_api_registers_with_guardians_and_lists_them(world, api) -> None:  # type: ignore[no-untyped-def]
    head = api("HEAD", world.institution.scope_node_id)
    body = {
        "given": "Zainab",
        "family": "Musa",
        "date_of_birth": "2013-09-14",
        "sex": "female",
        "institution_id": str(world.institution.id),
        "education_level": "jss_2",
        "guardians": [{"given": "Fatima", "family": "Musa", "relationship": "mother", "phone": "0807 000 1111"}],
    }
    r = head("post", "/api/v1/learners", {**body, "guardians": []})
    assert r.status_code == 422 and r.json()["code"] == "FAM-GUARDIANS"
    r = head("post", "/api/v1/learners", body)
    assert r.status_code == 201, r.content
    assert r.json()["guardians"][0]["created"] is True
    lid = r.json()["learner"]["id"]
    rows = head("get", f"/api/v1/learners/{lid}/guardians").json()["data"]
    assert rows[0]["name"] == "Fatima Musa" and rows[0]["phone"] == "+2348070001111"
    assert rows[0]["has_parental_responsibility"] is True and rows[0]["contact_priority"] == 1


def test_contact_restriction_hides_contact_details(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.families import services as families
    from syntegra.families.models import LearnerGuardian
    from syntegra.learners import services

    dad = guardian("Okoye", "Emeka", relationship="father", phone="0802 333 4444")
    mum = guardian("Okoye", "Ifeoma", phone="0802 333 5555")
    with as_user("HEAD", world.institution.scope_node_id):
        r = services.register(child(world, given="Chidi", family="Okoye", guardians=[mum, dad]))
        LearnerGuardian.unscoped.filter(pk=r.guardians[1].link.id).update(is_contact_restricted=True)
        rows = families.guardians_of(r.learner.id)
    assert rows[0]["phone"] == "+2348023335555"
    assert rows[1]["is_contact_restricted"] and rows[1]["phone"] is None and not rows[1]["is_authorised_collector"]
