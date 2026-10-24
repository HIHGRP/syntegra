"""Examination sitting arrangements (EXM-01, EXM-03) end to end through the forms, as a head teacher."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tests.conftest import system_ctx
from tests.integration.test_cr006_web import _ok, _option, _sign_in, _submit

pytestmark = pytest.mark.django_db(databases="__all__")


def test_secondary_school_plans_its_examination_seating(world: Any, client: Any) -> None:
    from syntegra.assessment.models import ExamEntry, ExamSitting
    from syntegra.core import context
    from syntegra.estate import services as estate
    from syntegra.institutions.models import Institution
    from syntegra.operations.models import Room
    from syntegra.platform.demo import abia

    abia.run(
        abia.Scale(
            schools_per_lga=1,
            pupils=60,
            lgas=1,
            absu_students=3,
            asceta_students=3,
            absu_staff=2,
            asceta_staff=2,
            days=1,
        ),
        log=lambda _m: None,
    )
    with context.use(system_ctx()):
        school = Institution.objects.get(name="Government Secondary School, Eziama")
        b1 = Room.objects.get(scope_node_id=school.scope_node_id, code="B1")
    officer = abia._user(
        f"estate.{school.institution_code.lower()}@abia.demo", "Facilities officer", "OPSM", school.scope_node_id,
        abia.Loaded(), school.name,
    )  # fmt: skip
    with context.use(officer):
        estate.assess("room", b1.id, condition_grade="unsafe", usability="unsafe_restricted", structural_risk="high",
                      in_use=False)  # fmt: skip

    _sign_in(client, "head.secondary.abn1@abia.demo")
    assert 'href="/exams/series"' in _ok(client.get("/"))
    body = _submit(client, "exam-series", {"institution_id": str(school.id), "name": "First Term Examinations — SS3",
                   "exam_body": "INSTITUTION"}, "set up")  # fmt: skip
    series = re.search(r'href="/exams/series/([0-9a-f-]{36})/sittings"', body)
    assert series
    sid = series.group(1)
    _submit(client, "exam-paper", {"target": sid, "paper_code": "MTH-SS3", "title": "Mathematics",
            "duration_minutes": "120"}, "added")  # fmt: skip
    _submit(client, "exam-paper", {"target": sid, "paper_code": "ENG-SS3", "title": "English Language",
            "duration_minutes": "90"}, "added")  # fmt: skip
    form = _ok(client.get("/forms/exam-entries"))
    block = re.search(r'name="class_ids".*?</select>', form, re.S).group(0)  # type: ignore[union-attr]
    ss3 = re.findall(r'<option value="([0-9a-f-]{36})"[^>]*>SS 3[AB] ', block)  # SS 3A and SS 3B, not JSS 3A/3B
    assert len(ss3) == 2
    r = client.post("/forms/exam-entries", {"target": sid, "class_ids": ss3, "paper_codes": ["MTH-SS3", "ENG-SS3"]})
    assert "10 candidates entered" in _ok(r)
    with context.use(system_ctx()):
        entries = list(ExamEntry.objects.filter(series_id=sid))
    assert len(entries) == 10 and {e.eligibility["class"] for e in entries} == {"SS 3A", "SS 3B"}

    form = _ok(client.get("/forms/exam-sitting"))
    mth = _option(form, "target", "MTH-SS3")
    eng = _option(form, "target", "ENG-SS3")
    teachers = re.findall(r'name="invigilator_staff_ids".*?</select>', form, re.S)[0]
    staff = re.findall(r'<option value="([0-9a-f-]{36})"', teachers)
    assert len(staff) >= 2
    a1, b1_opt = _option(form, "room_ids", "A1 Classroom"), _option(form, "room_ids", "B1 Classroom")
    assert "assessed unsafe restricted" in form  # the hall list warns before anyone chooses it
    plan = {"target": mth, "starts_on": "2026-12-07", "starts_time": "09:00", "spacing": "alternate",
            "invigilator_staff_ids": staff[:1]}  # fmt: skip
    r = client.post("/forms/exam-sitting", {**plan, "room_ids": [b1_opt]})
    assert r.status_code == 422 and "assessed unsafe restricted" in r.content.decode()
    r = client.post("/forms/exam-sitting", {**plan, "room_ids": [a1], "spacing": "alternate"})
    assert "10 candidates seated in 1 hall" in _ok(r)
    with context.use(system_ctx()):
        sitting = ExamSitting.objects.get(paper_id=mth, status="active")
    assert len(sitting.seat_allocations) == 10 and sitting.invigilator_staff_ids == [staff[0]]
    assert all(re.fullmatch(r"A1-[A-H][1-6]", d) for d in sitting.seat_allocations.values())

    # the same hall cannot hold two papers at once; planning again replaces the earlier plan
    r = client.post("/forms/exam-sitting", {**plan, "target": eng, "room_ids": [a1], "starts_time": "10:00"})
    assert r.status_code == 422 and "is used for MTH-SS3" in r.content.decode()
    r = client.post("/forms/exam-sitting", {**plan, "room_ids": [a1], "spacing": "every_desk",
                    "invigilator_staff_ids": staff[:2]})  # fmt: skip
    assert "10 candidates seated" in _ok(r)
    with context.use(system_ctx()):
        assert ExamSitting.objects.filter(paper_id=mth, status="active").count() == 1

    page = _ok(client.get(f"/exams/series/{sid}/sittings"))
    assert "Hall A1" in page and "Seating list for hall A1" in page and "same-class neighbours" in page
    assert page.count('class="desk c') == 10 and "SS 3A" in page and "SS 3B" in page
    assert "First Term Examinations" in _ok(client.get("/exams/series"))

    # one account, one session (CR-007): an API sign-in from another client is refused while the page session is
    # in use …
    from django.test import Client

    from tests.conftest import api_sign_in

    creds = {"username": "head.secondary.abn1@abia.demo", "password": "Demo-password-2026"}
    r = Client().post("/api/v1/auth/sign-in", creds, content_type="application/json")
    assert r.status_code == 409 and r.json()["code"] == "AUTH-SESSION-IN-USE"
    client.post("/sign-out")
    # … and after signing out, the API applies the same rules: no invigilator is refused
    tok = api_sign_in(client, creds["username"], creds["password"])
    r = client.post(f"/api/v1/exams/papers/{eng}/sitting", {"room_ids": [a1], "starts_on": "2026-12-08",
                    "starts_time": "09:00", "invigilator_staff_ids": []}, content_type="application/json",
                    HTTP_AUTHORIZATION=f"Bearer {tok}")  # fmt: skip
    assert r.status_code == 422 and "invigilator" in r.content.decode()
    r = client.get(f"/api/v1/exams/series/{sid}/sittings", HTTP_AUTHORIZATION=f"Bearer {tok}")
    assert r.status_code == 200 and r.json()["papers"][0]["code"] == "MTH-SS3"
    assert r.json()["papers"][0]["sittings"][0]["candidates"] == 10
