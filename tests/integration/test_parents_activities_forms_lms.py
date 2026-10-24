"""Parents and learners at school (CR-009 phase 4), end to end on the Abia demonstration school: messages between
staff and parents (COM-01, COM-101), the parent's home (FAM-03), parents' meetings (PTM-101), clubs and activities
(OPS-05), the school's own forms (FRM-101, FRM-102) and remote learning (LMS-101 to LMS-107) — and that a parent
sees only their own children and a learner only themselves."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

import pytest

from tests.conftest import system_ctx
from tests.integration.test_cr006_web import _ok, _sign_in

pytestmark = pytest.mark.django_db(databases="__all__")


def _next_weekday(days: int) -> dt.date:
    on = dt.date.today() + dt.timedelta(days=days)
    while on.weekday() not in (1, 2, 3):
        on += dt.timedelta(days=1)
    return on


def test_parents_messages_meetings_activities_forms_and_online_classes(world: Any, client: Any) -> None:
    from syntegra.academic.models import ClassGroup, ClassMembership
    from syntegra.comms.models import Conversation, Message
    from syntegra.core import context
    from syntegra.families.models import LearnerGuardian
    from syntegra.forms.models import FormResponse, MeetingBooking
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions.models import Institution
    from syntegra.lms.models import Submission, SubmissionMark
    from syntegra.operations.models import Activity, ActivityEnrolment
    from syntegra.platform.demo import abia

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
        code = school.institution_code.lower()
        p1 = AppUser.objects.get(username=f"parent1.{code}@abia.demo")
        kid1, kid2 = roster[0], roster[1]
        teacher = AppUser.objects.get(username=f"teacher.{code}@abia.demo")
    parent1, parent2, learner1 = (f"{r}.{code}@abia.demo" for r in ("parent1", "parent2", "learner1"))

    # FAM-03 and COM-101: the parent lands on their own home; the demo message is there, and the reply
    _sign_in(client, parent1)
    r = client.get("/")
    assert r.status_code == 302 and r["Location"] == "/parent"
    home = _ok(client.get("/parent"))
    assert "Welcome, " in home
    assert "SS 2A" in home and "Exercise 6.2" in home and "Medical information" in home
    assert client.get("/behaviour").status_code == 403 and client.get("/messages/new").status_code == 403
    assert client.get(f"/learners/{kid1}").status_code == 403
    inbox = _ok(client.get("/conversations"))
    conv_ids = re.findall(r'href="/conversations/([0-9a-f-]{36})"', inbox)
    assert conv_ids
    page = _ok(client.get(f"/conversations/{conv_ids[0]}"))
    assert "quadratic equations" in page and "We will make sure she practises" in page
    with context.use(system_ctx()):
        other = Conversation.objects.filter(linked_record_id=kid2).first()
    assert other is not None and client.get(f"/conversations/{other.id}").status_code == 404  # another parent's
    # the parent writes to their child's teacher
    page = _ok(client.get(f"/conversations?learner={kid1}"))
    assert teacher.display_name in page
    r = client.post("/conversations", {"learner_id": str(kid1), "staff_user_id": str(teacher.id), "body": "x"})
    assert r.status_code == 422 and "Write the message" in r.content.decode()
    r = client.post("/conversations", {"learner_id": str(kid1), "staff_user_id": str(teacher.id),
                                       "body": "Could you tell me which topics the test will cover?"})  # fmt: skip
    assert r.status_code == 302
    r = client.post("/conversations", {"learner_id": str(kid2), "staff_user_id": str(teacher.id), "body": "Hello"})
    assert r.status_code == 403  # not their child

    # COM-01: the teacher writes to two learners' parents; a parent whose contact is restricted is not written to
    with context.use(system_ctx()):
        LearnerGuardian.objects.filter(learner_id=roster[5]).update(is_contact_restricted=True)
    _sign_in(client, teacher.username)
    compose = f"/messages/new?school={school.id}&class={ss2a.id}"
    page = _ok(client.get(compose))
    assert "About which learners — SS 2A" in page and "no contact" in page
    r = client.post(compose, {"school": str(school.id), "class": str(ss2a.id), "learner_ids": [str(kid1)], "body": ""})
    assert r.status_code == 422 and "Write the message" in r.content.decode()
    page = _ok(client.post(compose, {"school": str(school.id), "class": str(ss2a.id),
                                     "learner_ids": [str(kid1), str(roster[7]), str(roster[5])],
                                     "body": "Reminder: bring your mathematical sets tomorrow."}))  # fmt: skip
    sent = re.search(r'id="sent">(.*?)</div>', page, re.S)
    assert sent is not None, page[-3000:]
    assert "Sent to the parents of 2 learner(s)" in sent.group(1), sent.group(1)
    assert "in the app" in sent.group(1) and "by SMS (queued" in sent.group(1)
    assert "no parent the school can contact" in page
    page = _ok(client.get("/conversations"))
    assert "new</span>" in page  # the parent's question waits unread
    mine = re.findall(r'href="/conversations/([0-9a-f-]{36})"', page)
    with context.use(system_ctx()):
        asked = Conversation.objects.filter(linked_record_id=kid1, assigned_user_id=teacher.id).first()
    assert asked is not None and str(asked.id) in mine
    page = _ok(client.get(f"/conversations/{asked.id}"))
    assert "which topics the test will cover" in page
    _ok(client.post(f"/conversations/{asked.id}", {"body": "Factorising and the quadratic formula."}))
    with context.use(system_ctx()):
        assert Message.objects.filter(conversation_id=asked.id, direction="inbound", read_at__isnull=True).count() == 0
        assert Message.objects.filter(about_learner_id=roster[7], channel="sms", delivery_status="queued").exists()
        assert not Message.objects.filter(about_learner_id=roster[5], body__startswith="Reminder: bring").exists()

    # PTM-101: the head sets up a meeting; parents book under the clash rules; the teacher records it
    _sign_in(client, head.username)
    evening = _next_weekday(12)
    r = client.post("/parents-meetings", {"school": str(school.id), "title": "SS 2A consultation evening",
                                          "class_ids": [str(ss2a.id)], "day1": str(evening), "from1": "16:00",
                                          "to1": "17:00", "slot": "10", "gap": "5", "modes": ["in_person"],
                                          "opens": str(dt.date.today()), "closes": str(evening)})  # fmt: skip
    assert r.status_code == 422 and "closes before the first evening" in r.content.decode()
    r = client.post("/parents-meetings", {"school": str(school.id), "title": "SS 2A consultation evening",
                                          "class_ids": [str(ss2a.id)], "day1": str(evening), "from1": "16:00",
                                          "to1": "17:00", "slot": "10", "gap": "5", "modes": ["in_person"],
                                          "opens": str(dt.date.today()),
                                          "closes": str(evening - dt.timedelta(days=1))})  # fmt: skip
    assert r.status_code == 302
    event_url = r["Location"].split("?")[0]
    page = _ok(client.get(event_url))
    assert "Every teacher" in page and "16:50" in page
    _sign_in(client, parent1)
    page = _ok(client.get(event_url))
    slots = re.findall(r'name="staff_id" value="([0-9a-f-]{36})">.*?<option value="([^"]+)"', page, re.S)
    assert len(slots) >= 2
    (t1, s1), (t2, _s2) = slots[0], slots[1]
    page = _ok(client.post(event_url, {"action": "book", "learner_id": str(kid1), "staff_id": t1, "slot": s1}))
    assert "Booked for" in page
    first = dt.datetime.fromisoformat(s1)
    r = client.post(event_url, {"action": "book", "learner_id": str(kid1), "staff_id": t2,
                                "slot": (first + dt.timedelta(minutes=10)).isoformat()})  # fmt: skip
    assert r.status_code == 422 and "no time to get from your" in r.content.decode()
    page = _ok(client.post(event_url, {"action": "book", "learner_id": str(kid1), "staff_id": t2,
                                       "slot": (first + dt.timedelta(minutes=20)).isoformat()}))  # fmt: skip
    assert "Booked for" in page
    _sign_in(client, parent2)
    r = client.post(event_url, {"action": "book", "learner_id": str(kid2), "staff_id": t1, "slot": s1})
    assert r.status_code == 422 and "just been taken" in r.content.decode()
    r = client.post(event_url, {"action": "book", "learner_id": str(kid1), "staff_id": t1, "slot": s1})
    assert r.status_code == 403  # not their child
    with context.use(system_ctx()):
        booking = MeetingBooking.objects.get(staff_id=t1, learner_id=kid1, status="confirmed",
                                             starts_at=first)  # fmt: skip
        assert MeetingBooking.objects.filter(guardian_id=p1.person_id, status="confirmed").count() >= 2
    if str(teacher.person_id) == t1:
        _sign_in(client, teacher.username)
        r = client.post(event_url, {"action": "record", "booking_id": str(booking.id), "attended": "yes", "note": "ok"})
        assert "has not happened yet" in r.content.decode()

    # OPS-05: chess is full; a parent's request goes on the waiting list and moves up when a place is freed
    with context.use(system_ctx()):
        chess = Activity.objects.get(scope_node_id=school.scope_node_id, name="Chess club")
        placed_n = ActivityEnrolment.objects.filter(activity_id=chess.id, allocation="allocated").count()
        assert placed_n >= 2
        Activity.objects.filter(pk=chess.id).update(capacity=placed_n)  # full, whatever the size of the class
        ActivityEnrolment.objects.filter(activity_id=chess.id, learner_id=kid1).delete()
        waiting_before = ActivityEnrolment.objects.filter(activity_id=chess.id, allocation="waitlisted").count()
    _sign_in(client, parent1)
    page = _ok(client.get("/activities"))
    assert "Chess club" in page and "JETS club" in page
    page = _ok(client.post("/activities", {"action": "join", "activity_id": str(chess.id), "learner_id": str(kid1)}))
    assert f"on the waiting list, number {waiting_before + 1}" in page
    r = client.post("/activities", {"action": "join", "activity_id": str(chess.id), "learner_id": str(kid1)})
    assert r.status_code == 422 and "already on the waiting list" in r.content.decode()
    _sign_in(client, head.username)
    roster_page = _ok(client.get(f"/activities/{chess.id}"))
    assert "Waiting list" in roster_page and "Registers taken" in roster_page
    with context.use(system_ctx()):
        placed = ActivityEnrolment.objects.filter(activity_id=chess.id, allocation="allocated").first()
        head_of_queue = ActivityEnrolment.objects.get(activity_id=chess.id, allocation="waitlisted", waiting_position=1)
    page = _ok(client.post(f"/activities/{chess.id}", {"action": "leave", "enrolment_id": str(placed.id)}))
    assert "first learner waiting has been given the place" in page
    with context.use(system_ctx()):
        head_of_queue.refresh_from_db()
        assert head_of_queue.allocation == "allocated"
        mine = ActivityEnrolment.objects.get(activity_id=chess.id, learner_id=kid1)
        if waiting_before:  # the parent's child moved up one place
            assert mine.allocation == "waitlisted" and mine.waiting_position == waiting_before
        else:  # the child was first in the queue and has the freed place
            assert mine.allocation == "allocated" and mine.waiting_position is None
    wrong_day = dt.date.today() - dt.timedelta(days=dt.date.today().weekday() or 7)  # the last Monday before today
    r = client.post(f"/activities/{chess.id}", {"action": "register", "on": str(wrong_day)})
    assert r.status_code == 422 and "does not meet on Monday" in r.content.decode()

    # FRM-101/102: the head builds a form with a conditional question; a parent answers; only the head reads it
    page = _ok(client.get(f"/forms/builder?school={school.id}"))
    assert "Medical information and emergency contacts" in page and "Consent: inter-house sports day" in page
    r = client.post("/forms/builder", {"school": str(school.id), "title": "School bus registration",
                                       "filled_by": "parents", "level": "confidential", "intro": ""})  # fmt: skip
    assert r.status_code == 302
    form_url = r["Location"]
    form_id = form_url.rsplit("/", 1)[1]
    _ok(client.post(form_url, {"action": "add", "label": "Will your child use the school bus?", "kind": "yes_no",
                               "required": "on"}))  # fmt: skip
    _ok(client.post(form_url, {"action": "add", "label": "Which stop", "kind": "choice", "required": "on",
                               "options": "Umuahia main market\nOld Umuahia junction", "show_if_key": "q1",
                               "show_if_value": "yes"}))  # fmt: skip
    page = _ok(client.post(form_url, {"action": "publish"}))
    assert "Published" in page
    r = client.post(form_url, {"action": "add", "label": "Another question", "kind": "text"})
    assert r.status_code == 422 and "start a new version" in r.content.decode().lower()
    _sign_in(client, parent1)
    fill = f"/daybook/{form_id}?learner={kid1}"
    assert "Which stop" in _ok(client.get(fill))
    r = client.post(fill, {"learner_id": str(kid1), "q1": "yes"})
    assert r.status_code == 422 and "“Which stop” needs an answer" in r.content.decode()
    page = _ok(client.post(fill, {"learner_id": str(kid1), "q1": "yes", "q2": "Old Umuahia junction"}))
    assert "Thank you — sent to the school." in page
    page = _ok(client.post(fill, {"learner_id": str(kid1), "q1": "no", "q2": "Old Umuahia junction"}))
    assert "replaces the answers you sent before" in page
    with context.use(system_ctx()):
        resp = FormResponse.objects.get(form_id=form_id, subject_id=kid1)
        assert resp.answers == {"q1": "no"}  # the hidden question's answer is not kept
    r = client.post(f"/daybook/{form_id}", {"learner_id": str(kid2), "q1": "no"})
    assert r.status_code == 403
    _sign_in(client, teacher.username)
    assert client.get(f"/forms/builder/{form_id}/answers").status_code == 403
    _sign_in(client, head.username)
    page = _ok(client.get(f"/forms/builder/{form_id}/answers"))
    assert "Will your child use the school bus?" in page and p1.display_name in page

    # LMS: the teacher sets work; the learner hands it in; the mark reaches learner and parent only when released
    _sign_in(client, teacher.username)
    page = _ok(client.get(f"/courses?school={school.id}"))
    space_id = re.search(r'href="/courses/([0-9a-f-]{36})">Mathematics', page)
    assert space_id is not None
    course_url = f"/courses/{space_id.group(1)}"
    assert "Week 6 — Quadratic equations" in _ok(client.get(course_url))
    due = dt.date.today() + dt.timedelta(days=4)
    r = client.post(f"{course_url}/assignments/new", {"title": "Exercise 6.3", "kind": "homework",
                                                       "instructions": "Questions 1 to 5 using the formula.",
                                                       "max_mark": "10", "opens_on": str(dt.date.today()),
                                                       "opens_at": "00:00", "due_on": str(due), "due_at": "18:00",
                                                       "late_policy": "accept_flag"})  # fmt: skip
    assert r.status_code == 302
    _sign_in(client, learner1)
    assert client.get("/").status_code == 302
    work = _ok(client.get("/work"))
    item = re.search(r'href="/work/([0-9a-f-]{36})">Exercise 6.3', work)
    assert item is not None
    work_url = f"/work/{item.group(1)}"
    r = client.post(work_url, {"text": "1. x = 2", "ai": "used_acknowledged", "ai_note": ""})
    assert r.status_code == 422 and "Say how you used AI tools" in r.content.decode()
    page = _ok(client.post(work_url, {"text": "1. x = 2 or x = 3\n2. x = -1", "ai": "none_used"}))
    receipt = re.search(r"receipt ([0-9A-F]{16})", page)
    assert receipt is not None
    r = client.post(work_url, {"text": "again", "ai": "none_used"})
    assert r.status_code == 422 and "already handed this in" in r.content.decode()
    assert client.get("/parent").status_code == 403 and client.get("/conversations").status_code == 403
    _sign_in(client, teacher.username)
    with context.use(system_ctx()):
        sub = Submission.objects.get(assignment_id=item.group(1))
    marking = f"{course_url}/assignments/{item.group(1)}/marking"
    r = client.post(marking, {"submission_id": str(sub.id), "score": "11"})
    assert r.status_code == 422 and "Between 0 and" in r.content.decode()
    _ok(client.post(marking, {"submission_id": str(sub.id), "score": "8", "feedback": "Check question 2."}))
    _sign_in(client, learner1)
    assert "Check question 2." not in _ok(client.get(work_url))
    _sign_in(client, teacher.username)
    page = _ok(client.post(marking, {"action": "release"}))
    assert "1 mark released" in page
    with context.use(system_ctx()):
        assert SubmissionMark.objects.get(submission_id=sub.id).released_at is not None
    _sign_in(client, learner1)
    page = _ok(client.get(work_url))
    assert "Check question 2." in page and receipt.group(1) in page
    _sign_in(client, parent1)
    assert "<strong>8 / 10</strong>" in _ok(client.get("/work"))
