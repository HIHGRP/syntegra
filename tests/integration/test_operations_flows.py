"""Attendance (API, offline replay), coverage gaps, certificates (sign/verify/reissue), SDAF, metrics."""

import datetime as dt
import uuid
from decimal import Decimal

import pytest

from syntegra.core.errors import ConflictError, Forbidden, HardValidation
from tests.conftest import guardian

pytestmark = pytest.mark.django_db(databases="__all__")


def enrol_class(world, as_user, n=6):  # type: ignore[no-untyped-def]
    from syntegra.academic import services as academic
    from syntegra.learners import services as learners

    node = world.institution.scope_node_id
    with as_user("HEAD", node):
        cls = academic.create_class(world.institution.id, world.period.id, "JSS 2 Gold", "jss_2")
        ids = []
        for i in range(n):
            r = learners.register(
                learners.RegisterLearner(
                    guardians=[guardian()],
                    given=["Ada", "Bayo", "Chidi", "Dami", "Efe", "Funke", "Gbenga", "Hauwa"][i],
                    family=f"Pupil{i}x",
                    date_of_birth=dt.date(2013, 1 + i, 10 + i),
                    sex="female" if i % 2 else "male",
                    institution_id=world.institution.id,
                    education_level="jss_2",
                )
            )
            academic.add_member(cls.id, r.learner.id)
            ids.append(r.learner.id)
    return cls, ids


def test_register_submission_with_offline_replay_and_rates(world, as_user, api) -> None:  # type: ignore[no-untyped-def]
    cls, ids = enrol_class(world, as_user)
    tch = api("TCH", world.institution.scope_node_id)
    day = dt.date.today()
    r = tch("post", f"/api/v1/classes/{cls.id}/registers", {"session_date": day.isoformat()})
    assert r.status_code == 201, r.content
    reg_id, etag = r.json()["id"], r["ETag"]
    ops = [str(uuid.uuid4()) for _ in ids]
    marks = [
        {"learner_id": str(lid), "code": c, "client_op_id": op, **({"minutes_late": 7} if c == "L" else {})}
        for lid, c, op in zip(ids, ["P", "P", "L", "A", "M", "P"], ops, strict=True)
    ]
    # partial submission first (device synced half the class)
    r = tch("put", f"/api/v1/registers/{reg_id}", {"marks": marks[:3]}, **{"If-Match": etag})
    assert r.status_code == 200, r.content
    assert r.json()["status"] == "in_progress" and r.json()["missing"] == 3
    # stale ETag is refused
    assert tch("put", f"/api/v1/registers/{reg_id}", {"marks": marks[3:]}, **{"If-Match": etag}).status_code == 412
    r = tch("put", f"/api/v1/registers/{reg_id}", {"marks": marks}, **{"Idempotency-Key": "sync-1"})
    body = r.json()
    assert body["status"] in ("submitted", "late") and body["created"] == 3 and body["replayed"] == 3
    # replaying the exact offline batch changes nothing
    again = tch("put", f"/api/v1/registers/{reg_id}", {"marks": marks}, **{"Idempotency-Key": "sync-1"})
    assert again.json() == body and again["Idempotent-Replayed"] == "true"
    # a teacher cannot change a submitted mark; the head can (audited correction)
    marks[3]["code"], marks[3]["client_op_id"] = "E", str(uuid.uuid4())
    assert tch("put", f"/api/v1/registers/{reg_id}", {"marks": [marks[3]]}).status_code == 403
    ht = api("HEAD", world.institution.scope_node_id)
    r = ht("put", f"/api/v1/registers/{reg_id}", {"marks": [marks[3]]})
    assert r.json()["status"] == "corrected" and r.json()["corrected"] == 1
    # learner not in the class
    stranger = {"learner_id": str(uuid.uuid4()), "code": "P"}
    assert ht("put", f"/api/v1/registers/{reg_id}", {"marks": [stranger]}).status_code == 422
    s = ht("get", f"/api/v1/learners/{ids[3]}/attendance?from={day - dt.timedelta(days=7)}&to={day}").json()
    assert s["possible"] == 1 and s["authorised_absence"] == 1 and s["flags"]["ATT-PERSISTENT"] is True


def test_coverage_g2_g3_open_and_close(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.academic import services as academic
    from syntegra.curriculum import services as coverage
    from syntegra.curriculum.models import CoverageGap
    from syntegra.people import services as people

    cls, _ = enrol_class(world, as_user, n=3)
    node = world.institution.scope_node_id
    with as_user("STA", world.state_scope):  # subjects belong to the state library
        subj = academic.create_subject(world.state_scope, f"BSC{uuid.uuid4().hex[:4]}", "Basic Science", ["jss_2"])
    with as_user("HEAD", node):
        with pytest.raises(Forbidden):
            academic.create_subject(world.state_scope, "XX1", "Not mine", ["jss_2"])
        plan = academic.add_subject_plan(cls.id, subj.id, 4)
        r = coverage.evaluate_institution(world.institution.id)
        assert r["opened"] == 1
        gap = CoverageGap.objects.get(class_subject_plan_id=plan.id, status="open")
        assert gap.rule == "g2" and gap.severity == "critical" and gap.learners_affected == 3
        assert (gap.due_on - dt.date.today()).days >= 3
        assert coverage.evaluate_institution(world.institution.id)["opened"] == 0  # deduplicated
        staff, post = people.create_staff("Ifeoma", "Obi", institution_id=world.institution.id, scope_node_id=node)
        ta = academic.assign_teacher(plan.id, staff.id, post.id, weekly_periods=Decimal("4"))
        with pytest.raises(ConflictError, match="teacher of record"):
            academic.assign_teacher(plan.id, staff.id, post.id)
        r = coverage.evaluate_institution(world.institution.id)
        assert r["closed"] == 1 and r["opened"] == 1  # G2 closed, G3 opened (no authorisation yet)
        assert CoverageGap.objects.get(class_subject_plan_id=plan.id, status="open").rule == "g3"
        people.add_authorisation(staff.id, subj.id, ["jss_1", "jss_2", "jss_3"])
        assert coverage.evaluate_institution(world.institution.id)["closed"] == 1
        assert not coverage.open_gaps(world.institution.id)
        del ta


def test_certificate_issue_verify_and_four_eyes_reissue(world, as_user, client) -> None:  # type: ignore[no-untyped-def]
    from syntegra.certificates import services as certs
    from syntegra.learners import services as learners

    node = world.institution.scope_node_id
    with as_user("HEAD", node):
        lrn = learners.register(
            learners.RegisterLearner(
                guardians=[guardian()],
                given="Amarachi",
                family="Udeh",
                date_of_birth=dt.date(2010, 4, 4),
                sex="female",
                institution_id=world.institution.id,
                education_level="jss_3",
            )
        ).learner
    with as_user("STA", world.state_scope) as sta:
        certs.ensure_signing_key(world.state_scope, "abia-moe-test-01")
        tpl = certs.create_template(world.state_scope, f"BECE-{uuid.uuid4().hex[:4]}")
        sig = certs.add_signatory(
            world.state_scope, sta.actor_id, "Honourable Commissioner for Education", valid_from=dt.date(2026, 1, 1)
        )
    req = certs.IssueRequest(
        learner_id=lrn.id,
        institution_id=world.institution.id,
        template_id=tpl.id,
        signatory_id=sig.id,
        award_date=dt.date(2026, 7, 20),
        award_title="Basic Education Certificate",
        award_class="Distinction",
    )
    with as_user("CERT", world.state_scope):
        cert = certs.issue(req)
        with pytest.raises(ConflictError, match="already"):
            certs.issue(req)
    assert cert.certificate_number.startswith("NG-ABMOE-2026-")
    r = client.get(f"/api/v1/public/verify?number={cert.certificate_number}")
    assert r.status_code == 200 and r.json()["result"] == "valid" and r.json()["signature_valid"] is True
    assert client.get(f"/api/v1/public/verify?code={cert.verification_code}").json()["result"] == "valid"
    assert client.get("/api/v1/public/verify?number=NG-ABMOE-2026-00000199").json()["result"] == "not_found"
    jwks = client.get("/api/v1/public/jwks.json").json()
    assert any(k["kid"] == "abia-moe-test-01" and k["crv"] == "P-256" for k in jwks["keys"])
    with as_user("CERT", world.state_scope):
        case = certs.request_reissue(
            cert.id, "lost_or_stolen", applicant_name="Amarachi Udeh", applicant_phone="+2348030000000"
        )
        with pytest.raises(Forbidden, match="four eyes"):
            certs.decide_reissue(case.id, True)  # the reviewer cannot approve their own case
    with as_user("TCH", world.state_scope), pytest.raises(Forbidden):
        certs.decide_reissue(case.id, True)
    with as_user("CERT", world.state_scope):  # a second registrar
        done = certs.decide_reissue(case.id, True, note="Police report and affidavit verified")
    assert done.status == "issued"
    old = client.get(f"/api/v1/public/verify?number={cert.certificate_number}").json()
    assert old["result"] == "superseded" and old["superseded_by"]
    new = client.get(f"/api/v1/public/verify?number={old['superseded_by']}").json()
    assert new["result"] == "valid"


def test_sdaf_census_freeze_once_per_period_and_ube_demand(world, as_user) -> None:  # type: ignore[no-untyped-def]
    from syntegra.financing import services as fin
    from syntegra.learners import services as learners

    node = world.institution.scope_node_id
    with as_user("HEAD", node):
        lids = [
            learners.register(
                learners.RegisterLearner(
                    guardians=[guardian()],
                    given=g,
                    family="Census",
                    date_of_birth=dt.date(2012, 1, i + 1),
                    sex="male",
                    institution_id=world.institution.id,
                    education_level=lvl,
                    start_on=dt.date(2026, 9, 8),
                )
            ).learner.id
            for i, (g, lvl) in enumerate([("Uche", "jss_1"), ("Obinna", "jss_1"), ("Tunde", "sss_1")])
        ]
    with as_user("STA", world.state_scope) as sta:
        maker, _ = __import__("tests.conftest", fromlist=["make_user"]).make_user(world, "FINO", world.state_scope)
        fin.publish_rate_card(
            world.state_scope,
            [("secondary", "jss_1", 150_000), ("secondary", "sss_1", 250_000)],
            effective_from=dt.date(2026, 9, 1),
            proposed_by=maker.id,
            approval_instrument="Abia State Executive Council resolution 2026/14",
        )
        with pytest.raises(HardValidation, match="UBE"):
            fin.set_payer_rule(world.state_scope, "secondary", "jss_1", "parent_or_student", public=True)
        fin.set_payer_rule(world.state_scope, "secondary", "sss_1", "parent_or_student", public=True)
        period = fin.open_period(
            world.state_scope, world.period.id, f"T1-{uuid.uuid4().hex[:4]}", dt.date(2026, 9, 25), ["secondary"]
        )
        del sta
    with as_user("HEAD", node):
        snap = fin.take_census(world.institution.id, period.id)
        assert (snap.enrolled, snap.billable) == (3, 3)
        frozen = fin.confirm_and_freeze(snap.id)
        assert frozen.status == "frozen" and len(bytes(frozen.content_hash)) == 32
    with as_user("HEAD", world.institution2.scope_node_id):
        learners.transfer(lids[0], world.institution2.id, effective_on=dt.date(2026, 9, 20))
        snap2 = fin.take_census(world.institution2.id, period.id)
        assert snap2.billable == 0 and snap2.excluded == 1  # already billed at the first school this period
    with as_user("FINO", world.state_scope):
        demands = fin.issue_demand(frozen.id)
    gov = [d for d in demands if d.payer_kind == "government"]
    parents = [d for d in demands if d.payer_kind == "parent_or_student"]
    assert len(gov) == 1 and gov[0].is_basic_education and gov[0].amount_minor == 2 * 150_000
    assert len(parents) == 1 and parents[0].amount_minor == 250_000 and parents[0].learner_id == lids[2]


def test_metrics_scope_and_small_number_suppression(world, as_user, api) -> None:  # type: ignore[no-untyped-def]
    enrol_class(world, as_user, n=6)
    sta = api("STA", world.state_scope)
    r = sta("get", "/api/v1/metrics/ENR-COUNT")
    assert r.status_code == 200, r.content
    cells = {c["scope_node_id"]: c for c in r.json()["cells"]}
    mine = cells[str(world.institution.scope_node_id)]
    assert mine["n"] == 6 and not mine["suppressed"]
    with as_user("HEAD", world.institution2.scope_node_id):
        from syntegra.learners import services as learners

        learners.register(
            learners.RegisterLearner(
                guardians=[guardian()],
                given="Solo",
                family="Learner",
                date_of_birth=dt.date(2016, 1, 1),
                sex="male",
                institution_id=world.institution2.id,
                education_level="primary_4",
            )
        )
    cells = {c["scope_node_id"]: c for c in sta("get", "/api/v1/metrics/ENR-COUNT").json()["cells"]}
    small = cells[str(world.institution2.scope_node_id)]
    assert small["suppressed"] and small["value"] is None and small["n"] is None
    lga = api("LGA", world.lga2_scope)
    lga_cells = lga("get", "/api/v1/metrics/ENR-COUNT").json()["cells"]
    assert {c["scope_node_id"] for c in lga_cells} == {str(world.institution2.scope_node_id)}


def test_generic_ceda_api_trims_and_scopes(world, api) -> None:  # type: ignore[no-untyped-def]
    lga = api("LGA", world.lga_scope)
    r = lga("get", "/api/v1/ceda/institution")
    assert r.status_code == 200, r.content
    ids = {x["id"] for x in r.json()["data"]}
    assert str(world.institution.id) in ids and str(world.institution2.id) not in ids
    assert lga("get", "/api/v1/ceda/safeguarding_concern").status_code in (403, 404)
    assert lga("get", "/api/v1/ceda/learner").status_code == 403  # derived scope → module endpoint only
    assert lga("get", "/api/v1/ceda").json()["ceda"]["version"] == "1.6.0"
