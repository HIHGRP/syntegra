"""CR-001 enterprise HRMS integrated across the CEDA: IAM, staff register, academic, coverage, cover, payroll."""

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any

import pytest

from syntegra.core.errors import ConflictError, Forbidden, HardValidation

pytestmark = pytest.mark.django_db(databases="__all__")


@dataclass
class HR:
    subject: Any
    p1: Any
    p2: Any
    p3: Any
    user: Any
    grant_id: uuid.UUID
    staff: Any
    record: Any


def next_monday() -> dt.date:
    d = dt.date.today() + dt.timedelta(days=7)
    return d - dt.timedelta(days=d.weekday())


@pytest.fixture
def hr(world, as_user) -> HR:  # type: ignore[no-untyped-def]
    from syntegra.academic import services as academic
    from syntegra.hr import establishment as est
    from syntegra.people import services as people
    from tests.conftest import make_user

    with as_user("STA", world.state_scope):
        subj = academic.create_subject(world.state_scope, f"MTH{uuid.uuid4().hex[:4]}", "Mathematics", ["jss_2"])
    with as_user("HR", world.state_scope):

        def mk(inst, sid):  # type: ignore[no-untyped-def]
            return est.create_position(
                est.NewPosition(
                    title="Mathematics teacher",
                    cadre_code="TEACHER",
                    employer_scope_id=world.state_scope,
                    grade_level_min=7,
                    grade_level_max=12,
                    institution_id=inst.id,
                    subject_id=sid,
                    education_levels=["jss_2"],
                )
            )

        p1, p2, p3 = mk(world.institution, subj.id), mk(world.institution2, subj.id), mk(world.institution, None)
    user, grant = make_user(world, "TCH", world.institution.scope_node_id, "Teacher")
    with as_user("HR", world.state_scope):
        staff = people.create_staff_master(
            "Ngozi", "Eze", date_of_birth=dt.date(1980, 5, 1), sex="female", user_id=user.id
        )
        rec = est.appoint(
            est.Appointment(
                staff_id=staff.id,
                position_id=p1.id,
                appointment_type="first_appointment",
                first_appointment_on=dt.date(2012, 1, 9),
                grade_level=8,
                step=2,
                confirmed_on=dt.date(2014, 1, 9),
            )
        )
    return HR(subj, p1, p2, p3, user, grant, staff, rec)


def test_appointment_establishment_and_retirement(world, as_user, hr) -> None:  # type: ignore[no-untyped-def]
    from syntegra.hr import establishment as est
    from syntegra.people import services as people

    assert (hr.record.retirement_due_on, hr.record.retirement_basis) == (dt.date(2045, 5, 1), "age")
    assert hr.record.status == "confirmed"
    with as_user("HR", world.state_scope):
        other = people.create_staff_master("Musa", "Bello", date_of_birth=dt.date(1990, 1, 1))
        with pytest.raises(ConflictError, match="already filled"):
            est.appoint(
                est.Appointment(
                    staff_id=other.id,
                    position_id=hr.p1.id,
                    appointment_type="first_appointment",
                    first_appointment_on=dt.date(2020, 1, 6),
                    grade_level=7,
                )
            )
        with pytest.raises(HardValidation, match="band"):
            est.appoint(
                est.Appointment(
                    staff_id=other.id,
                    position_id=hr.p3.id,
                    appointment_type="first_appointment",
                    first_appointment_on=dt.date(2020, 1, 6),
                    grade_level=14,
                )
            )
        e = est.establishment(world.institution.id)
    assert (e["approved"], e["filled"], e["vacant"]) == (2, 1, 1)
    assert e["vacancies_by_subject"] == {"general": 1}


def test_posting_moves_grants_ends_teaching_and_opens_g2(world, as_user, hr) -> None:  # type: ignore[no-untyped-def]
    from syntegra.academic import services as academic
    from syntegra.academic.models import TeachingAssignment
    from syntegra.curriculum.models import CoverageGap
    from syntegra.hr import postings
    from syntegra.hr.models import EmploymentRecord
    from syntegra.iam.models import RoleGrant
    from syntegra.people.models import StaffPost

    with as_user("HEAD", world.institution.scope_node_id):
        cls = academic.create_class(world.institution.id, world.period.id, "JSS 2 Blue", "jss_2")
        plan = academic.add_subject_plan(cls.id, hr.subject.id, 5)
        ta = academic.assign_teacher(plan.id, hr.staff.id, hr.record.staff_post_id)
    effective = dt.date.today() + dt.timedelta(days=1)
    with as_user("HR", world.state_scope) as hr1:
        p = postings.request_posting(
            hr.staff.id, hr.p2.id, posting_kind="redeployment", reason="Rationalisation", effective_on=effective
        )
        assert p.coverage_impact["count"] == 1
        with pytest.raises(Forbidden, match="cannot approve"):
            postings.approve_posting(p.id)
        del hr1
    with as_user("HR", world.state_scope):
        with pytest.raises(HardValidation, match="handover"):
            postings.approve_posting(p.id)
        postings.approve_posting(p.id, note="Mr Obi covers JSS 2 Blue maths until the vacancy is filled")
        p = postings.make_effective(p.id)
    assert p.status == "effective"
    old = StaffPost.unscoped.get(pk=hr.record.staff_post_id)
    assert old.valid_to == effective - dt.timedelta(days=1)
    recs = {r.position_id: r.status for r in EmploymentRecord.unscoped.filter(staff_id=hr.staff.id)}
    assert recs == {hr.p1.id: "separated", hr.p2.id: "confirmed"}
    grants = {g.scope_id: g.status for g in RoleGrant.unscoped.filter(user_id=hr.user.id)}
    assert grants[world.institution.scope_node_id] == "inactive"
    assert grants[world.institution2.scope_node_id] == "active"
    assert TeachingAssignment.unscoped.get(pk=ta.id).valid_to is not None
    gap = CoverageGap.unscoped.get(class_subject_plan_id=plan.id, status="open")
    assert gap.rule == "g2" and gap.severity == "critical"


def test_leave_balance_four_eyes_and_cover(world, as_user, hr) -> None:  # type: ignore[no-untyped-def]
    from syntegra.core import context
    from syntegra.hr import leave
    from syntegra.hr.models import LeaveBalance
    from syntegra.people.models import StaffAbsence
    from tests.conftest import user_ctx

    mon = next_monday()
    with context.use(user_ctx(hr.user.id, hr.grant_id)):  # the teacher, self-service
        lr = leave.request_leave(hr.staff.id, "annual_leave", mon, mon + dt.timedelta(days=4))
        assert lr.days == 5
        with pytest.raises(Forbidden):
            leave.decide_leave(lr.id, True)
        with pytest.raises(HardValidation, match="Not enough leave"):
            leave.request_leave(hr.staff.id, "annual_leave", mon + dt.timedelta(days=7), mon + dt.timedelta(days=60))
    b = LeaveBalance.unscoped.get(staff_id=hr.staff.id, leave_type="annual_leave", leave_year=mon.year)
    assert (b.entitled, b.pending) == (30, 5)
    with as_user("HEAD", world.institution.scope_node_id):
        lr = leave.decide_leave(lr.id, True)
    a = StaffAbsence.unscoped.get(pk=lr.absence_id)
    assert a.status == "approved" and a.is_planned and a.absence_type == "annual_leave"
    b = LeaveBalance.unscoped.get(pk=b.id)
    assert (b.pending, b.taken) == (0, 5)


def test_promotion_is_a_human_decision(world, as_user, hr) -> None:  # type: ignore[no-untyped-def]
    from syntegra.hr import establishment as est
    from syntegra.hr.models import EmploymentRecord

    with as_user("HR", world.state_scope):
        case = est.open_promotion(hr.staff.id, "2026-PROMO")
        assert all(c["passed"] for c in case.eligibility)
        est.decide_promotion(case.id, "approved")
    rec = EmploymentRecord.unscoped.get(pk=hr.record.id)
    assert (rec.grade_level, rec.step) == (9, 1)


def test_payroll_four_eyes_and_integrity_hold(world, as_user, hr) -> None:  # type: ignore[no-untyped-def]
    from syntegra.hr import establishment as est
    from syntegra.hr import payroll
    from syntegra.hr.domain import payroll as calc
    from syntegra.hr.models import HrIntegrityFlag, SalaryScalePoint
    from syntegra.people import services as people
    from syntegra.people.models import Payslip

    with as_user("HR", world.state_scope):
        acc = payroll.request_bank_account(hr.staff.id, "044", "0123456789", "Ngozi Eze")
        with pytest.raises(Forbidden):
            payroll.approve_bank_account(acc.id, verified_via="call_back")  # the requester
        twin = people.create_staff_master("Ghost", "Worker", date_of_birth=dt.date(1985, 1, 1))
        est.appoint(
            est.Appointment(
                staff_id=twin.id,
                position_id=hr.p3.id,
                appointment_type="first_appointment",
                first_appointment_on=dt.date(2016, 1, 4),
                grade_level=7,
                confirmed_on=dt.date(2018, 1, 4),
            )
        )
        acc2 = payroll.request_bank_account(twin.id, "044", "0123456789", "G Worker")  # same account number
    with as_user("PAYR", world.state_scope):
        payroll.approve_bank_account(acc.id, verified_via="call_back")
        payroll.approve_bank_account(acc2.id, verified_via="nibss_name_enquiry")
    with as_user("INTEG", world.state_scope):
        raised = payroll.scan_integrity()
        assert raised.get("shared_bank_account") == 2
        assert raised.get("no_attendance_30_days") == 2  # neither has signed in at school for 30 days
        assert payroll.scan_integrity().get("shared_bank_account") is None  # deduplicated
        flag = HrIntegrityFlag.unscoped.get(staff_id=twin.id, flag_kind="shared_bank_account")
        payroll.decide_hold(flag.id, True, "Account belongs to another employee; verify in person")
    with as_user("PAYR", world.state_scope) as preparer:
        run = payroll.compute_payroll(world.state_scope, f"2026-{uuid.uuid4().hex[:2]}", dt.date(2026, 10, 28))
        with pytest.raises(Forbidden):
            payroll.approve_payroll(run.id)
        del preparer
    slips = {s.staff_post_id: s for s in Payslip.unscoped.filter(payroll_run_id=run.id)}
    assert hr.record.staff_post_id in slips and len(slips) == 1  # the held post is excluded
    point = SalaryScalePoint.unscoped.get(structure_id=hr.record.salary_structure_id, grade_level=8, step=2)
    expect = calc.compute_month(
        point.annual_basic_minor,
        {
            "HOUSING": calc.pct((point.annual_basic_minor + 6) // 12, 4000),
            "TRANSPORT": calc.pct((point.annual_basic_minor + 6) // 12, 2500),
        },
    )
    slip = slips[hr.record.staff_post_id]
    assert (slip.gross_minor, slip.net_minor) == (expect.gross, expect.net)
    assert slip.bank_account_last4 == "6789"
    assert {f["flag"] for f in slip.exception_flags} == {"shared_bank_account", "no_attendance_30_days"}
    with as_user("FINO", world.state_scope):
        payroll.approve_payroll(run.id)
    with as_user("FINO", world.state_scope):
        assert payroll.approve_payroll(run.id).status == "approved"


def test_separation_ends_access_everywhere(world, as_user, hr, client) -> None:  # type: ignore[no-untyped-def]
    from syntegra.core import context
    from syntegra.hr import postings
    from syntegra.iam.models import AppUser, RoleGrant
    from syntegra.people.models import Staff

    with as_user("HR", world.state_scope):
        postings.record_separation(hr.record.staff_post_id, "resignation", effective_on=dt.date.today())
    assert Staff.unscoped.get(pk=hr.staff.id).status == "leaver"
    assert AppUser.unscoped.get(pk=hr.user.id).status == "deactivated"
    assert not RoleGrant.unscoped.filter(user_id=hr.user.id, status="active").exists()
    r = client.post(
        "/api/v1/auth/sign-in",
        {"username": hr.user.username, "password": "correct-horse-battery"},
        content_type="application/json",
    )
    assert r.status_code == 401 and r.json()["code"] == "AUTH-ACCOUNT-INACTIVE"
    del context


def test_hr_api(world, api, hr) -> None:  # type: ignore[no-untyped-def]
    hr_officer = api("HR", world.state_scope)
    r = hr_officer("get", f"/api/v1/hr/institutions/{world.institution.id}/establishment")
    assert r.status_code == 200 and r.json()["filled"] == 1
    teacher = api("TCH", world.institution.scope_node_id)
    assert teacher("get", f"/api/v1/hr/institutions/{world.institution.id}/establishment").status_code == 403
