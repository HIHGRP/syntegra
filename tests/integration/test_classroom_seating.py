"""Classroom seating plan (BEH-102) end to end, as a teacher."""

from __future__ import annotations

import json
from typing import Any

import pytest

from tests.conftest import system_ctx
from tests.integration.test_cr006_web import _ok, _sign_in

pytestmark = pytest.mark.django_db(databases="__all__")


def test_teacher_arranges_a_class(world: Any, client: Any) -> None:
    from syntegra.academic.models import ClassGroup
    from syntegra.core import context
    from syntegra.estate import services as estate
    from syntegra.institutions.models import Institution
    from syntegra.operations.models import Room
    from syntegra.platform.demo import abia
    from syntegra.success.models import Adjustment, SeatingPlan, SeatingPlanPrint

    abia.run(
        abia.Scale(schools_per_lga=1, pupils=120, lgas=1, absu_students=3, asceta_students=3, absu_staff=2,
                   asceta_staff=2, days=1),
        log=lambda _m: None,
    )  # fmt: skip
    with context.use(system_ctx()):
        school = Institution.objects.get(name="Government Secondary School, Eziama")
        ss2a = ClassGroup.objects.get(institution_id=school.id, name="SS 2A")
        rooms = {r.code: r for r in Room.objects.filter(scope_node_id=school.scope_node_id)}
    code = school.institution_code.lower()
    url = f"/classes/{ss2a.id}/seating"

    _sign_in(client, f"teacher.{code}@abia.demo")
    assert "No seating plan yet" in _ok(client.get(url))
    r = client.post(url, {"action": "generate", "strategy": "separate_negative_influences", "style": "pairs",
                          "room_id": str(ss2a.room_id)})  # fmt: skip
    page = _ok(r)
    assert (
        "New seating plan made" in page
        and "3 pairs kept apart" in page
        and "sitting together now: <strong>0" in page
        and "Behaviour evidence" in page
    )
    assert page.count('class="seat"') == 10 and "★" in page and "att." in page
    with context.use(system_ctx()):
        plan = SeatingPlan.objects.get(class_group_id=ss2a.id, is_active=True)
        adjusted = Adjustment.objects.get(adjustment_kind="seating", learner_id__in=list(plan.placements["seats"]))
    assert plan.placements["seats"][str(adjusted.learner_id)].startswith("R1-")  # front row, whatever the strategy

    board = _ok(client.get(url + "?view=board"))
    assert "Board-safe view" in board and "att." not in board and "Green" not in board and "★" not in board

    # the teacher swaps two learners by drag and drop
    seats = dict(plan.placements["seats"])
    a, b = list(seats)[:2]
    seats[a], seats[b] = seats[b], seats[a]
    page = _ok(client.post(url, {"action": "save", "plan_id": str(plan.id), "placements": json.dumps(seats)}))
    assert "Your arrangement is saved" in page and "strategy: Manual" in page
    r = client.post(url, {"action": "save", "plan_id": str(plan.id), "placements": json.dumps({a: "R99-S9"})})
    assert r.status_code == 422

    # a logged, watermarked print
    page = _ok(client.post(url, {"action": "print", "plan_id": str(plan.id), "viewer_name": "Mrs A. Eze, ASUBEB QA"}))
    assert page.count("For Mrs A. Eze, ASUBEB QA") >= 10 and "This print is logged" in page
    with context.use(system_ctx()):
        assert SeatingPlanPrint.objects.filter(seating_plan_id=plan.id).count() == 1

    # a classroom assessed unsafe is refused
    officer = abia._user(f"estate.{code}@abia.demo", "Facilities officer", "OPSM", school.scope_node_id, abia.Loaded(),
                         school.name)  # fmt: skip
    with context.use(officer):
        estate.assess("room", rooms["B2"].id, condition_grade="unsafe", usability="unusable", structural_risk="high",
                      in_use=False)  # fmt: skip
    r = client.post(url, {"action": "generate", "strategy": "alphabetical", "style": "rows",
                          "room_id": str(rooms["B2"].id)})  # fmt: skip
    assert r.status_code == 422 and "B2 is assessed unusable" in r.content.decode()

    # someone without seating permission cannot open it
    _sign_in(client, f"estate.{code}@abia.demo")
    assert client.get(url).status_code == 403
