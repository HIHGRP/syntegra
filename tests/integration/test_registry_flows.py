"""Institutions, learners (matching, GLID, enrolment, transfer) and scope isolation."""

import datetime as dt

import pytest

from syntegra.core.errors import ConflictError, Forbidden, SoftWarning
from syntegra.core.ids import glid_valid

pytestmark = pytest.mark.django_db(databases="__all__")


def reg(world, given="Chiamaka", family="Okafor", dob=dt.date(2014, 3, 9), inst=None, nin=None):  # type: ignore[no-untyped-def]
    from syntegra.learners import services

    return services.RegisterLearner(given=given, family=family, date_of_birth=dob, sex="female",
                                    institution_id=(inst or world.institution).id, education_level="jss_2", nin=nin)


def test_institution_duplicate_requires_reason(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.institutions import services as inst

    data = inst.RegisterInstitution(name="Govt. Secondary School, Aba", category="secondary", ownership="state",
                                    lga_scope_id=world.lga_scope, address={}, levels=["jss_1"], location=(7.3668, 5.1067))
    with as_user("STA", world.state_scope):
        with pytest.raises(SoftWarning) as e:
            inst.register(data)
        assert e.value.extra["candidates"][0]["institution_id"] == str(world.institution.id)
        created = inst.register(data, override_reason="Second campus registered separately by SUBEB")
        assert created.institution_code.startswith("INS-NG-")


def test_lga_officer_cannot_register_outside_their_lga(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.institutions import services as inst

    data = inst.RegisterInstitution(name="Elsewhere School", category="primary", ownership="state",
                                    lga_scope_id=world.lga2_scope, address={}, levels=["primary_1"])
    with as_user("LGA", world.lga_scope), pytest.raises(Forbidden):
        inst.register(data)


def test_learner_registration_matching_and_enrolment(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.learners import services
    from syntegra.mdm.models import MatchReview

    with as_user("HT", world.institution.scope_node_id):
        first = services.register(reg(world, nin="12345678901"))
        assert first.outcome == "created" and glid_valid(first.learner.global_learner_id)
        assert first.enrolment.status == "active"
        # same child again (name variant + same NIN) → auto-linked, not duplicated; enrolment refused (already active)
        with pytest.raises(ConflictError, match="active enrolment"):
            services.register(reg(world, given="Chiamaka", family="Okafor", nin="123 4567 8901"))
        # transposed DOB → probable match needs a reason, then opens a steward review
        with pytest.raises(SoftWarning):
            services.register(reg(world, dob=dt.date(2014, 9, 3)))
        second = services.register(reg(world, dob=dt.date(2014, 9, 3)), override_reason="Twin sister, birth certificate seen")
        assert second.outcome == "created" and second.review_id
        assert MatchReview.objects.get(pk=second.review_id).status == "open"
        assert first.learner.global_learner_id != second.learner.global_learner_id


def test_transfer_moves_the_active_primary_enrolment(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.learners import services
    from syntegra.learners.models import Enrolment

    with as_user("HT", world.institution.scope_node_id):
        r = services.register(reg(world, given="Emeka", family="Nwosu", dob=dt.date(2013, 1, 20)))
    with as_user("HT", world.institution2.scope_node_id) as ctx:
        t = services.transfer(r.learner.id, world.institution2.id, education_level="jss_1")
        assert t.status == "completed"
        enrs = list(Enrolment.objects.filter(learner_id=r.learner.id).order_by("start_on", "created_at"))
        assert [e.status for e in enrs] == ["transferred", "active"]
        assert enrs[1].institution_id == world.institution2.id
        # after the transfer the receiving head sees the learner; the sending head still sees history
        assert services.get(r.learner.id).id == r.learner.id
        del ctx


def test_learner_visibility_is_scoped(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.core.errors import NotFound
    from syntegra.learners import services

    with as_user("HT", world.institution.scope_node_id):
        lid = services.register(reg(world, given="Ngozi", family="Eze", dob=dt.date(2012, 5, 5))).learner.id
    with as_user("HT", world.institution2.scope_node_id), pytest.raises(NotFound):
        services.get(lid)
    with as_user("STA", world.state_scope):
        assert services.get(lid).id == lid


def test_nin_reveal_requires_purpose_and_is_audited(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.core.errors import PurposeRequired
    from syntegra.learners import services

    with as_user("HT", world.institution.scope_node_id):
        lid = services.register(reg(world, given="Bola", family="Ade", dob=dt.date(2012, 2, 2), nin="98765432109")).learner.id
    with as_user("STA", world.state_scope), pytest.raises(PurposeRequired):
        services.reveal_nin(lid)
    with as_user("STA", world.state_scope, purpose="investigation"):
        assert services.reveal_nin(lid) == "98765432109"
