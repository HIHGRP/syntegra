"""Organised marksheets (ASM-01) and fully personalised report cards (ASM-04) end to end, on the Abia demonstration
school: the teacher adds a second-term assessment and enters its marks with the range and number checks, the head
locks them, and the head issues the first term's report cards as PDFs filed in the school's register."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

import pytest

from tests.conftest import system_ctx
from tests.integration.test_cr006_web import _ok, _sign_in

pytestmark = pytest.mark.django_db(databases="__all__")


def test_marksheet_entry_and_report_cards(world: Any, client: Any) -> None:
    from syntegra.academic.models import ClassGroup, Subject
    from syntegra.assessment.models import Assessment, AssessmentResult, ReportCard, ReportCardRun
    from syntegra.core import context
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions.models import Institution
    from syntegra.platform.demo import abia
    from syntegra.records.models import Document

    abia.run(
        abia.Scale(schools_per_lga=1, pupils=120, lgas=1, absu_students=3, asceta_students=3, absu_staff=2,
                   asceta_staff=2, days=1),
        log=lambda _m: None,
    )  # fmt: skip
    with context.use(system_ctx()):
        school = Institution.objects.get(name="Government Secondary School, Eziama")
        ss2a = ClassGroup.objects.get(institution_id=school.id, name="SS 2A")
        maths = Subject.objects.get(name="Mathematics")
        head = AppUser.objects.get(
            id__in=RoleGrant.objects.filter(scope_id=school.scope_node_id).values("user_id"),
            username__startswith="head.",
        )
    code = school.institution_code.lower()
    sheet = f"/markbook/{ss2a.id}/{maths.id}"

    # ASM-01 as the Mathematics teacher: the first term's locked CA and examination, totals, grades and positions
    _sign_in(client, f"teacher.{code}@abia.demo")
    page = _ok(client.get(sheet))
    assert "Marksheet — SS 2A, Mathematics" in page and "First Term" in page and "First term examination" in page
    assert page.count("Locked</span>") == 2 and "1st" in page and "Class average" in page
    assert "weights 100 of 100" in page
    # the first term's weights are full; a second-term test is accepted and opens on the second term
    r = client.post(sheet, {"action": "add", "title": "Extra test", "kind": "ca_test", "max_mark": "20", "weight": "10",
                            "assessed_on": str(dt.date(2026, 11, 2))})  # fmt: skip
    assert r.status_code == 422 and "add up to more than 100" in r.content.decode()
    page = _ok(client.post(sheet, {"action": "add", "title": "Second term test 1", "kind": "ca_test", "max_mark": "20",
                                   "weight": "20", "assessed_on": "2027-01-20"}))  # fmt: skip
    assert "Second term test 1 added" in page and 'aria-current="page">Second Term' in page
    with context.use(system_ctx()):
        a = Assessment.objects.get(title="Second term test 1")
        assert a.status == "open" and a.max_mark == 20
    learners = re.findall(r'name="mark_([0-9a-f-]{36})"', page)
    assert len(learners) >= 10
    form = {"action": "save", "assessment_id": str(a.id), **{f"mark_{lid}": "15" for lid in learners}}
    # a mark that is not a number, a mark above the maximum; nothing is saved
    r = client.post(sheet, {**form, f"mark_{learners[0]}": "abc"})
    assert r.status_code == 422 and "not numbers" in r.content.decode()
    r = client.post(sheet, {**form, f"mark_{learners[1]}": "25"})
    assert r.status_code == 422 and "out of range" in r.content.decode()
    with context.use(system_ctx()):
        assert not AssessmentResult.objects.filter(assessment_id=a.id).exists()
    # one learner did not do the work (blank): recorded as missing work
    page = _ok(client.post(sheet, {**form, f"mark_{learners[2]}": "", f"mark_{learners[3]}": "18.5"}))
    assert f"Marks saved ({len(learners)} new, 0 changed)." in page
    with context.use(system_ctx()):
        res = {str(x.learner_id): x for x in AssessmentResult.objects.filter(assessment_id=a.id)}
        assert res[learners[2]].is_missing_work and res[learners[2]].score is None
        assert res[learners[3]].score == pytest.approx(18.5) and res[learners[3]].grade_label == "A1"
    # a teacher cannot lock marks
    assert client.post(sheet, {**form, "lock": "1"}).status_code == 403

    # the head locks the marks; afterwards they cannot be changed
    _sign_in(client, head.username)
    page = _ok(client.post(sheet, {"action": "lock", "assessment_id": str(a.id)}))
    assert "Marks locked." in page
    _sign_in(client, f"teacher.{code}@abia.demo")
    r = client.post(sheet, form)
    assert r.status_code == 422 and "locked" in r.content.decode()

    # ASM-04 as the head: the first term is complete; each learner's comments are written for them
    _sign_in(client, head.username)
    reports_url = f"/reports/class/{ss2a.id}"
    page = _ok(client.get(reports_url))
    assert "Report cards — SS 2A" in page and "First Term" in page and "Complete" in page
    first = re.search(r'name="form_([0-9a-f-]{36})"[^>]*>([^<]+)</textarea>', page)
    assert first is not None
    lid, drafted = first.group(1), first.group(2)
    assert re.search(r"average of \d+\.\d%", drafted) and re.search(r"\d+(st|nd|rd|th) of \d+", drafted)
    edited = "A thoughtful, hard-working member of the class who helps others in Mathematics."
    page = _ok(client.post(reports_url, {"action": "comments", f"form_{lid}": edited}))
    assert "Comments saved (1 learner with edited comments)." in page and edited in page
    card_url = f"{reports_url}/learner/{lid}"
    card = _ok(client.get(card_url))
    assert edited in card and "GOVERNMENT SECONDARY SCHOOL, EZIAMA" in card and "img/emblems/NG-AB.png" in card
    assert "Termly report card — First Term, 2026/2027 session" in card and "Next term begins" in card
    assert "11 Jan 2027" in card and "Second term test 1" not in card

    # a teacher cannot issue; the head issues one PDF per learner, filed in the register with its fingerprint
    _sign_in(client, f"teacher.{code}@abia.demo")
    assert client.post(reports_url, {"action": "issue"}).status_code == 403
    _sign_in(client, head.username)
    page = _ok(client.post(reports_url, {"action": "issue"}))
    m = re.search(r"(\d+) report cards issued", page)
    assert m is not None
    with context.use(system_ctx()):
        run = ReportCardRun.objects.get(institution_id=school.id, status="issued")
        cards = list(ReportCard.objects.filter(run_id=run.id))
        assert len(cards) == int(m.group(1)) >= 10
        docs = {d.id: d for d in Document.objects.filter(id__in=[c.document_id for c in cards])}
        assert len(docs) == len(cards)
        for c in cards:
            d = docs[c.document_id]
            assert bytes(d.sha256) == bytes(c.content_hash) and d.mime_type == "application/pdf"
            assert d.classification == "confidential" and d.institution_id == school.id
        mine = next(c for c in cards if str(c.learner_id) == lid)
        assert (run.completeness or {})["comments"][lid]["form"] == edited
    assert "Issued PDF" in _ok(client.get(card_url)) and f"/documents/{mine.document_id}" in _ok(client.get(card_url))
    # issued once: a second issue and further comment changes are refused
    r = client.post(reports_url, {"action": "issue"})
    assert r.status_code == 422 and "already issued" in r.content.decode()
    r = client.post(reports_url, {"action": "comments", f"form_{lid}": "Changed"})
    assert r.status_code == 422 and "already issued" in r.content.decode()

    # Learner 360: the term's results with the link to the report card
    page = _ok(client.get(f"/learners/{lid}"))
    assert "Results — First Term, SS 2A" in page and card_url in page
