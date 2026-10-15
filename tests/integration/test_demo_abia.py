"""The Abia demonstration load (``syntegra_demo_abia``) end to end, at a small scale."""

from __future__ import annotations

import itertools
from typing import Any

import pytest

from tests.conftest import system_ctx

pytestmark = pytest.mark.django_db(databases="__all__")


def test_abia_demonstration_load_small_scale(world: Any) -> None:
    from syntegra.academic.models import ClassGroup
    from syntegra.assessment.models import AssessmentResult
    from syntegra.attendance.models import AttendanceMark
    from syntegra.core import context
    from syntegra.governance.models import ScopeNode
    from syntegra.hr.models import EmploymentRecord
    from syntegra.institutions.models import Institution
    from syntegra.learners.models import Enrolment
    from syntegra.mdm.models import ExternalIdentifier
    from syntegra.platform.demo import abia
    from syntegra.regulation import services as reg
    from syntegra.regulation.models import BodyDependency, RegulatoryBody

    scale = abia.Scale(
        schools_per_lga=1, pupils=24, lgas=2, absu_students=21, asceta_students=7, absu_staff=6, asceta_staff=4, days=2
    )
    out = abia.run(scale, log=lambda _m: None)
    assert out.lgas == 17 and out.schools == 4 and out.pupils == 4 * 24
    assert out.tertiary_students == 28 and out.staff == 10
    assert out.results > 0 and out.attendance_marks > 0
    with context.use(system_ctx()):
        moe, board = ScopeNode.objects.get(code="AB-MOE"), ScopeNode.objects.get(code="AB-ASUBEB")
        assert board.parent_id == moe.id and ScopeNode.objects.filter(code="AB-MOTE", level="authority").exists()
        asubeb = RegulatoryBody.objects.using("platform").get(code="ASUBEB")
        assert (
            BodyDependency.objects.using("platform")
            .filter(from_body_id=asubeb.id, to_body_id=RegulatoryBody.objects.using("platform").get(code="ABMOE").id)
            .exists()
        )
        school = Institution.objects.get(name="Community Primary School, Eziama")
        assert Enrolment.objects.filter(institution_id=school.id, status="active").count() == 24
        assert ClassGroup.objects.filter(institution_id=school.id).count() == 12
        links = {(x["body_code"], x["relationship"]) for x in reg.profile(school.id)["links"]}
        assert ("ASUBEB", "supervision") in links and ("ABMOE", "supervision") in links
        secondary = Institution.objects.get(name="Government Secondary School, Eziama")
        board = next(
            x
            for x in reg.profile(secondary.id)["links"]
            if (x["body_code"], x["relationship"]) == ("ASUBEB", "supervision")
        )
        assert {"JSS1", "SSS3"} <= set(board["levels"])  # the board supervises the senior classes too
        absu = Institution.objects.get(name="Abia State University, Uturu")
        assert ("ABMTE", "supervision") in {(x["body_code"], x["relationship"]) for x in reg.profile(absu.id)["links"]}
        students = Enrolment.objects.filter(institution_id=absu.id, status="active")
        assert students.count() == 21 and all(e.programme_id for e in students)
        assert ExternalIdentifier.objects.filter(person_id=students[0].learner_id, scheme="INST-ID").exists()
        assert EmploymentRecord.objects.count() >= 10
        assert AssessmentResult.objects.count() == out.results
        assert AttendanceMark.objects.count() >= out.attendance_marks
    again = abia.run(scale, log=lambda _m: None)  # idempotent: nothing loaded twice
    assert again.schools == 0 and again.pupils == 0 and again.tertiary_students == 0 and again.staff == 0


def test_control_room_compares_schools_and_selects_the_best(world: Any, client: Any) -> None:
    from django.core.cache import cache

    from syntegra.analytics import performance
    from syntegra.core import context
    from syntegra.governance.models import ScopeNode
    from syntegra.platform.demo import abia
    from tests.conftest import make_user, user_ctx

    cache.clear()
    scale = abia.Scale(
        schools_per_lga=1, pupils=12, lgas=2, absu_students=6, asceta_students=3, absu_staff=2, asceta_staff=2, days=2
    )
    abia.run(scale, log=lambda _m: None)
    with context.use(system_ctx()):
        state = ScopeNode.objects.get(level="state")
        lga = ScopeNode.objects.get(code="AB-ABN")
    u, g = make_user(world, "COMM", state.id)
    with context.use(user_ctx(u.id, g)):
        d = performance.performance()
    assert {len(d["league"][x]) for x in ("primary", "secondary")} == {2}
    assert len(d["league"]["tertiary"]) == 2
    for rows in d["league"].values():
        assert [r["rank"] for r in rows] == list(range(1, len(rows) + 1))
        assert all(a["index"] >= b["index"] for a, b in itertools.pairwise(rows))
    best = d["best_school"]
    assert best["index"] == max(r["index"] for g in ("primary", "secondary") for r in d["league"][g])
    assert d["best_learner"] and d["best_learner"]["subjects"] >= 5
    assert d["kpis"]["learners"] == 4 * 12 + 9

    client.handler.enforce_csrf_checks = False
    sign_in = {"username": "commissioner.education@abia.gov.ng", "password": "Demo-password-2026"}
    assert client.post("/sign-in", sign_in).status_code == 302
    r = client.get("/command/control-room")
    assert r.status_code == 200, r.content.decode()[-2000:]
    body = r.content.decode()
    assert "Best overall school" in body and best["name"] in body and d["best_learner"]["name"] in body
    r = client.get("/command/compare?group=secondary&lga=Aba+North")
    assert r.status_code == 200 and "Aba North" in r.content.decode()
    client.post("/sign-out")

    cache.clear()
    u, g = make_user(world, "LGA", lga.id)  # an LGA officer sees only the LGA's schools
    with context.use(user_ctx(u.id, g)):
        local = performance.performance()
    assert {r["lga"] for rows in local["league"].values() for r in rows} <= {"Aba North"}
    assert len(local["league"]["primary"]) == 1
