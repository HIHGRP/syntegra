"""Teacher assignment (ACA-101) and lessons linked to the curriculum (CUR-09) end to end, on the Abia demonstration
school: the head assigns and replaces teachers with the G2/G3 checks, the timetable never double-books, and the
teacher logs a lesson against its curriculum objectives."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

import pytest

from tests.conftest import system_ctx
from tests.integration.test_cr006_web import _ok, _sign_in

pytestmark = pytest.mark.django_db(databases="__all__")


def _plan_row(page: str, subject: str) -> str:
    m = re.search(rf"<tr>\s*<td>(?:<a [^>]*>)?{re.escape(subject)}.*?</tr>", page, re.S)
    assert m, subject
    return m.group(0)


def test_head_assigns_teachers_and_teacher_logs_lessons(world: Any, client: Any) -> None:
    from syntegra.academic.models import ClassGroup, ClassSubjectPlan, Subject, TeachingAssignment
    from syntegra.core import context
    from syntegra.curriculum import lessons
    from syntegra.curriculum.models import DeliveryLog, SchemeOfWork
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.institutions.models import Institution
    from syntegra.people.models import StaffPost
    from syntegra.platform.demo import abia
    from syntegra.timetable import services as timetable
    from syntegra.timetable.models import Timetable, TimetableLesson

    abia.run(
        abia.Scale(schools_per_lga=1, pupils=120, lgas=1, absu_students=3, asceta_students=3, absu_staff=2,
                   asceta_staff=2, days=1),
        log=lambda _m: None,
    )  # fmt: skip
    with context.use(system_ctx()):
        school = Institution.objects.get(name="Government Secondary School, Eziama")
        classes = {c.name: c for c in ClassGroup.objects.filter(institution_id=school.id)}
        subjects = dict(Subject.objects.values_list("name", "id"))
        head = AppUser.objects.get(
            id__in=RoleGrant.objects.filter(scope_id=school.scope_node_id).values("user_id"),
            username__startswith="head.",
        )
        posts = {p.job_title: p for p in StaffPost.objects.filter(institution_id=school.id, valid_to__isnull=True)}
        tt = Timetable.objects.get(institution_id=school.id, status="published")
        ls = list(TimetableLesson.objects.filter(timetable_id=tt.id))
        plans = {p.id: p for p in ClassSubjectPlan.objects.filter(class_group_id__in=[c.id for c in classes.values()])}
        tor = list(TeachingAssignment.objects.filter(class_subject_plan_id__in=list(plans), role="teacher_of_record"))
        assert len(SchemeOfWork.objects.filter(status="published", class_subject_plan_id__in=list(plans))) == 10
    code = school.institution_code.lower()

    # the published timetable: every class-subject's periods placed, nobody and no room in two places at once
    assert not tt.unmet_requirements and len(tor) == len(plans)
    assert len(ls) == sum(p.periods_per_week for p in plans.values())
    for key in ("class_group_id", "staff_id", "room_id"):
        slots = [(getattr(x, key), x.cycle_day, x.period_code) for x in ls]
        assert len(slots) == len(set(slots)), key
    assert (
        max(sum(1 for x in ls if x.class_subject_plan_id == p and x.cycle_day == d) for p in plans for d in range(1, 6))
        == 1
    )

    # ACA-101 as the head: SS 2A is fully staffed and authorised; JSS 1B's Basic Science is flagged G3 with the reason
    _sign_in(client, head.username)
    ss2a = f"/classes/{classes['SS 2A'].id}/plan"
    page = _ok(client.get(ss2a))
    assert "Subjects and teachers — SS 2A" in page and "G3 —" not in page and "G2 —" not in page
    assert "version 1.0" in _plan_row(page, "Mathematics") and "Co-teacher:" in _plan_row(page, "Biology")
    jss1b = _ok(client.get(f"/classes/{classes['JSS 1B'].id}/plan"))
    assert "G3 — not authorised" in _plan_row(jss1b, "Basic Science and Technology") and "Reason given:" in jss1b

    maths = next(
        p for p in plans.values() if p.class_group_id == classes["SS 2A"].id and p.subject_id == subjects["Mathematics"]
    )
    biology_teacher = posts["Teacher, Biology"].staff_id
    # a second teacher of record is refused unless the head asks to replace; an unauthorised teacher needs a reason
    r = client.post(ss2a, {"action": "assign", "plan_id": str(maths.id), "staff_id": str(biology_teacher),
                           "role": "teacher_of_record", "replace": "1"})  # fmt: skip
    assert r.status_code == 422 and "no authorisation for the subject" in r.content.decode()
    r = client.post(ss2a, {"action": "assign", "plan_id": str(maths.id), "staff_id": str(biology_teacher),
                           "role": "teacher_of_record", "justification": "Covering for two weeks"})  # fmt: skip
    assert r.status_code == 422 and "already has a teacher of record" in r.content.decode()
    page = _ok(client.post(ss2a, {"action": "assign", "plan_id": str(maths.id), "staff_id": str(biology_teacher),
                                  "role": "teacher_of_record", "replace": "1",
                                  "justification": "Covering while the Mathematics teacher is on leave"}))  # fmt: skip
    assert "Teacher assigned." in page and "G3 — not authorised" in _plan_row(page, "Mathematics")
    with context.use(system_ctx()):
        current = TeachingAssignment.objects.filter(class_subject_plan_id=maths.id, role="teacher_of_record")
        assert [a.staff_id for a in current if a.valid_to is None] == [biology_teacher]
        new = next(a for a in current if a.valid_to is None)
    page = _ok(client.post(ss2a, {"action": "end", "assignment_id": str(new.id)}))
    assert "Assignment ended." in page
    # hand the class back to the Mathematics teacher (authorised: no reason needed)
    page = _ok(client.post(ss2a, {"action": "assign", "plan_id": str(maths.id),
                                  "staff_id": str(posts["Teacher, Mathematics"].staff_id), "role": "teacher_of_record",
                                  "replace": "1"}))  # fmt: skip
    assert "Authorised" in _plan_row(page, "Mathematics")
    # a teacher cannot reach the page's changes
    _sign_in(client, f"teacher.{code}@abia.demo")
    r = client.post(ss2a, {"action": "end", "assignment_id": str(new.id)})
    assert r.status_code == 403

    # CUR-09 as the Mathematics teacher: SS 2A Mathematics opens first, each lesson with its curriculum objectives
    page = _ok(client.get("/teaching/plans"))
    assert "Lessons — SS 2A, Mathematics" in page or "Lessons — SS 2B, Mathematics" in page
    assert "Senior Secondary Mathematics — SS 2" in page and "MTH2." in page and "Planned from the curriculum" in page
    with context.use(system_ctx()):
        ta = TeachingAssignment.objects.get(
            class_subject_plan_id=maths.id, role="teacher_of_record", valid_to__isnull=True
        )
        teacher = AppUser.objects.get(username=f"teacher.{code}@abia.demo")
        assert teacher.person_id == ta.staff_id
        tas = TeachingAssignment.objects.filter(class_subject_plan_id=maths.id)
        logged = DeliveryLog.objects.filter(teaching_assignment__in=tas)
        assert logged.exists() and logged.filter(is_as_planned=True).exists()
    today = dt.date.today()
    teacher_ctx = abia._user(teacher.username, teacher.display_name, "TCH", school.scope_node_id, abia.Loaded(), "")
    open_: list[Any] = []
    for week in (timetable.monday(today), timetable.monday(today) - dt.timedelta(days=7)):  # the demo leaves one each
        with context.use(teacher_ctx):
            view = lessons.plan_view(ta.id, week)
            ctx_rows = timetable.week(school.id, week, class_subject_plan_id=maths.id)
        open_ = [r for r in view["lessons"] if r["can_log"]]
        if open_:
            break
    if not open_:
        pytest.skip("the term has only just started: no lesson taught yet to log")
    target = open_[0]
    assert target["planned"] and len(ctx_rows) == maths.periods_per_week
    url = f"/teaching/plans?assignment={ta.id}&week={week}"
    form = {"action": "log", "assignment": str(ta.id), "week": str(week), "lesson_id": str(target["lesson_id"]),
            "occurs_on": str(target["on"]), "node_ids": [o["id"] for o in target["planned"]],
            "learners_present": str(view["class"]["learners"]), "minutes": "35", "note": "Worked examples"}  # fmt: skip
    page = _ok(client.post(url, form))
    assert "Lesson logged." in page and "Taught as planned" in page and "Worked examples" in page
    again = client.post(url, form)
    assert again.status_code == 409 or (again.status_code == 422 and "already logged" in again.content.decode())
    # an objective outside the class-subject's curriculum, a day the lesson is not on, a lesson not yet taught
    bad = client.post(url, {**form, "lesson_id": str(open_[-1]["lesson_id"]), "occurs_on": str(open_[-1]["on"]),
                            "node_ids": ["00000000-0000-7000-8000-00000000abcd"]})  # fmt: skip
    assert bad.status_code == 422 and "not in this class-subject" in bad.content.decode()
    wrong_day = target["on"] + dt.timedelta(days=1 if target["on"].weekday() < 4 else -1)
    r = client.post(url, {**form, "occurs_on": str(wrong_day)})
    assert r.status_code == 422 and "not on that day" in r.content.decode()
    with context.use(system_ctx()):
        later = next(x for x in ls if x.class_subject_plan_id == maths.id)
    future = timetable.monday(today) + dt.timedelta(days=7 + later.cycle_day - 1)
    r = client.post(url, {**form, "lesson_id": str(later.id), "occurs_on": str(future)})
    assert r.status_code == 422 and "once it has taken place" in r.content.decode()
    # another teacher's lesson cannot be logged
    other = next(x for x in ls if x.staff_id != ta.staff_id and x.cycle_day <= today.isoweekday())
    r = client.post(
        url, {**form, "lesson_id": str(other.id), "occurs_on": str(week + dt.timedelta(days=other.cycle_day - 1))}
    )
    assert r.status_code == 403
