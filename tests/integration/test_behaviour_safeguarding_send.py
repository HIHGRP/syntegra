"""Behaviour (BEH-01/02/101), safeguarding concerns and cases (SAF-01/02/03) and the special educational needs
register (SEN-01/02), end to end on the Abia demonstration school — including who may see what."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

import pytest

from tests.conftest import system_ctx
from tests.integration.test_cr006_web import _ok, _sign_in

pytestmark = pytest.mark.django_db(databases="__all__")


def test_behaviour_safeguarding_and_send(world: Any, client: Any) -> None:
    from syntegra.academic.models import ClassGroup, ClassMembership
    from syntegra.core import context
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions.models import Institution
    from syntegra.platform.demo import abia
    from syntegra.safeguarding.models import CaseAccessLog, SafeguardingCase, SafeguardingConcern
    from syntegra.success.models import BehaviourEvent, SendProfile

    abia.run(
        abia.Scale(schools_per_lga=1, pupils=120, lgas=1, absu_students=3, asceta_students=3, absu_staff=2,
                   asceta_staff=2, days=1),
        log=lambda _m: None,
    )  # fmt: skip
    with context.use(system_ctx()):
        school = Institution.objects.get(name="Government Secondary School, Eziama")
        ss2a = ClassGroup.objects.get(institution_id=school.id, name="SS 2A")
        roster = sorted(
            ClassMembership.objects.filter(class_group_id=ss2a.id, valid_to__isnull=True).values_list(
                "learner_id", flat=True
            ),
            key=str,
        )
        head = AppUser.objects.get(
            id__in=RoleGrant.objects.filter(scope_id=school.scope_node_id).values("user_id"),
            username__startswith="head.",
        )
        on_register = set(SendProfile.objects.filter(status="active").values_list("learner_id", flat=True))
        assert BehaviourEvent.objects.filter(scope_node_id=school.scope_node_id).count() > 40
    code = school.institution_code.lower()
    teacher, dsl, senco = (f"{r}.{code}@abia.demo" for r in ("teacher", "dsl", "senco"))
    log_url = f"/behaviour/new?school={school.id}&class={ss2a.id}"

    # BEH-01: the teacher logs behaviour for one or several learners
    _sign_in(client, teacher)
    page = _ok(client.get(log_url))
    assert "Log behaviour — SS 2A" in page and "Excellent work" in page and "Bullying" in page
    types = dict(re.findall(r'name="type_id" value="([0-9a-f-]{36})"[^>]*> ([^<]+?) <span', page))
    by_label = {v: k for k, v in types.items()}
    base = {"school": str(school.id), "class": str(ss2a.id), "on": str(dt.date.today()), "at": "00:01"}
    page = _ok(client.post(log_url, {**base, "learner_ids": [str(roster[0]), str(roster[1])],
                                     "type_id": by_label["Helping others"]}))  # fmt: skip
    assert "Recorded for 2 learners." in page
    r = client.post(log_url, {**base, "learner_ids": [str(roster[2])], "type_id": by_label["Bullying"],
                              "description": "Pushed a younger learner into the gutter after school."})  # fmt: skip
    assert r.status_code == 422 and "Name who was bullied" in r.content.decode()
    r = client.post(log_url, {**base, "learner_ids": [str(roster[2])], "type_id": by_label["Fighting"]})
    assert r.status_code == 422 and "Say what happened" in r.content.decode()
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    r = client.post(log_url, {**base, "on": str(tomorrow), "learner_ids": [str(roster[2])],
                              "type_id": by_label["Excellent work"]})  # fmt: skip
    assert r.status_code == 422 and "has not come yet" in r.content.decode()
    disrupt = {**base, "learner_ids": [str(roster[2])], "type_id": by_label["Disrupting learning"]}
    page = _ok(client.post(log_url, {**disrupt, "outcome": "suspension", "description": "Third disruption this week."}))
    assert "waits for the head" in page
    overview = f"/behaviour?school={school.id}"
    page = _ok(client.get(overview))
    assert "Waiting for the head's decision" in page and "Examination malpractice" in page
    with context.use(system_ctx()):
        waiting = BehaviourEvent.objects.filter(
            learner_id=roster[2], outcome="suspension", decision_by__isnull=True
        ).get()
    assert (
        client.post(overview, {"action": "decide", "event_id": str(waiting.id), "outcome": "detention"}).status_code
        == 403
    )

    # BEH-02: the head decides and withdraws
    _sign_in(client, head.username)
    page = _ok(client.post(overview, {"action": "decide", "event_id": str(waiting.id), "outcome": "detention"}))
    assert "Decision recorded." in page
    page = _ok(client.post(overview, {"action": "withdraw", "event_id": str(waiting.id)}))
    assert "Entry withdrawn." in page
    with context.use(system_ctx()):
        waiting.refresh_from_db()
        assert waiting.outcome == "detention" and waiting.decision_by == head.id and waiting.reversed_at is not None
    assert "Exam" in _ok(client.get(f"/behaviour/policy?school={school.id}"))
    assert client.get("/safeguarding").status_code == 403  # the head is not the safeguarding lead
    assert client.get("/send").status_code == 403  # nor the SENCO

    # SAF-01: the teacher records a concern and gets only a receipt
    _sign_in(client, teacher)
    concern = f"/safeguarding/concerns/new?school={school.id}&class={ss2a.id}"
    what = "Came to school with fresh bruises on both arms and said an uncle beats him when he is late home."
    r = client.post(concern, {"learner_id": str(roster[4]), "category": "physical_abuse", "what": "bruises"})
    assert r.status_code == 422 and "Say what you saw or heard" in r.content.decode()
    page = _ok(client.post(concern, {"learner_id": str(roster[4]), "category": "physical_abuse", "what": what}))
    receipt = re.search(r"receipt (SC-[0-9A-F]{6})", page)
    assert receipt is not None and "will not see it again" in page and what not in page
    with context.use(system_ctx()):
        stored = SafeguardingConcern.objects.get(receipt_code=receipt.group(1))
        assert b"bruises" not in bytes(stored.body) and stored.learner_id == roster[4]
    assert receipt.group(1) in _ok(client.get(concern))
    assert client.get("/safeguarding").status_code == 403

    # SAF-02/03: the DSL opens a case, records the work, refers, and closes it
    _sign_in(client, dsl)
    page = _ok(client.get("/safeguarding"))
    assert receipt.group(1) in page and "Physical abuse" in page
    page = _ok(client.post("/safeguarding", {"concern_id": str(stored.id), "risk": "high"}))
    m = re.search(r"Concern added to case (SG-\d{4}-\d{4})", page)
    assert m is not None
    with context.use(system_ctx()):
        case = SafeguardingCase.objects.get(case_reference=m.group(1))
        assert case.risk_level == "high" and case.learner_id == roster[4]
    case_url = f"/safeguarding/cases/{case.id}"
    page = _ok(client.get(case_url))
    assert what in page and receipt.group(1) in page and "Access log" in page
    page = _ok(client.post(case_url, {"action": "entry", "kind": "action",
                                      "text": "Spoke with the learner with the form teacher present."}))  # fmt: skip
    assert "Added to the chronology." in page
    agency = "Ministry of Women Affairs and Social Development"
    page = _ok(client.post(case_url, {"action": "refer", "agency": agency, "contact": "Child protection desk, Umuahia",
                                      "basis": "vital_interests"}))  # fmt: skip
    assert "Referral recorded." in page and "Child protection desk" in page
    r = client.post(case_url, {"action": "close", "reason": "Child placed safely with the grandmother; monitored."})
    assert r.status_code == 422 and "Referrals are still waiting" in r.content.decode()
    with context.use(system_ctx()):
        from syntegra.safeguarding.models import SafeguardingReferral

        ref = SafeguardingReferral.objects.get(case_id=case.id)
    _ok(client.post(case_url, {"action": "outcome", "referral_id": str(ref.id), "status": "accepted",
                               "outcome": "Social worker visited; care arranged with the grandmother."}))  # fmt: skip
    page = _ok(
        client.post(case_url, {"action": "close", "reason": "Child placed safely with the grandmother; monitored."})
    )
    assert "Case closed and signed." in page
    with context.use(system_ctx()):
        case.refresh_from_db()
        assert case.status == "closed" and case.closed_signed_by is not None
        views = CaseAccessLog.objects.filter(case_kind="safeguarding_case", case_id=case.id).count()
        assert views >= 6  # every opening of the case is logged
    _sign_in(client, teacher)
    assert client.get(case_url).status_code == 403

    # SEN-01/02: the SENCO's register and a learner's profile, plan, review and adjustments
    _sign_in(client, senco)
    page = _ok(client.get(f"/send?school={school.id}&class={ss2a.id}"))
    assert "Special educational needs register" in page and page.count("/send/learners/") >= 3
    new = next(lid for lid in roster if lid not in on_register)
    form = {"school": str(school.id), "class": str(ss2a.id), "learner_id": str(new), "support_level": "school_support",
            "primary": "communication", "needs": "Finds it hard to follow long spoken instructions.",
            "helps": "Visual timetable and instructions written as short steps."}  # fmt: skip
    r = client.post("/send", form)
    assert r.status_code == 422 and "Choose at least one area of need" in r.content.decode()
    page = _ok(client.post("/send", {**form, "need_areas": ["communication"]}))
    assert "Added to the register." in page
    profile = f"/send/learners/{new}"
    page = _ok(client.get(profile))
    assert "Finds it hard to follow long spoken instructions." in page
    page = _ok(client.post(profile, {"action": "plan", "plan_type": "isp", "cycle": "2",
                                     "outcomes": "Follows a three-step instruction\nAsks for help when stuck",
                                     "participants": "SENCO, form teacher, father"}))  # fmt: skip
    assert "Support plan published." in page and "Follows a three-step instruction" in page
    with context.use(system_ctx()):
        from syntegra.success.models import SupportPlan

        plan = SupportPlan.objects.get(profile__learner_id=new, status="published")
        first_review = plan.next_review_on
    page = _ok(client.post(profile, {"action": "review", "plan_id": str(plan.id),
                                     "notes": "Follows two-step instructions reliably; working on three.",
                                     "attendees": "SENCO, father"}))  # fmt: skip
    assert "Review recorded" in page
    with context.use(system_ctx()):
        plan.refresh_from_db()
        assert plan.next_review_on >= first_review
        assert CaseAccessLog.objects.filter(case_kind="send_profile").count() >= 3
    page = _ok(client.post(profile, {"action": "adjust", "kind": "visual_supports",
                                     "note": "Write the lesson's steps on the board as a numbered list",
                                     "applies_to": ["lessons"]}))  # fmt: skip
    assert "Adjustment added" in page

    # teachers see the adjustments and strategies for their class — never the needs behind them
    _sign_in(client, teacher)
    page = _ok(client.get("/teaching/plans"))
    assert "Support for learners in SS 2A" in page and "numbered list" in page and "25% extra time" in page
    assert "Finds it hard to follow" not in page and "hearing loss" not in page
    assert client.get("/send").status_code == 403 and client.get(profile).status_code == 403
    learner = _ok(client.get(f"/learners/{roster[0]}"))
    assert "Behaviour (90 days)" in learner and "Helping others" in learner
