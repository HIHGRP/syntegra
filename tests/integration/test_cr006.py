"""CR-006: institutional budgets and imprest, funding and loans, the property register and proactive facility
actions, the infrastructure warehouse and the Commissioner's view, and security curricula through each agency's
structure."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

import pytest

from syntegra.core.errors import ConflictError, Forbidden, HardValidation
from tests.conftest import make_user, system_ctx, user_ctx
from tests.integration.test_hrms import hr  # noqa: F401 — fixture

pytestmark = pytest.mark.django_db(databases="__all__")
NAIRA = 100
TODAY = dt.date.today()


def use(ctx: Any) -> Any:
    from syntegra.core import context

    return context.use(ctx)


def as_(world: Any, role: str, scope: uuid.UUID) -> tuple[Any, Any]:
    u, g = make_user(world, role, scope)
    return user_ctx(u.id, g), u


def staff_member(world: Any, given: str, user_id: uuid.UUID | None = None) -> Any:
    from syntegra.people import services as people

    with use(as_(world, "HR", world.state_scope)[0]):
        return people.create_staff_master(given, "Obi", date_of_birth=dt.date(1985, 1, 1), user_id=user_id)


# --------------------------------------------------------------------------- budgets and imprest
def test_budget_commitment_control_virement_and_imprest(world: Any) -> None:
    from syntegra.finance import budgets
    from syntegra.finance.models import BudgetLine

    node = world.institution.scope_node_id
    bursar, _ = as_(world, "FINO", node)
    head, _ = as_(world, "HEAD", node)
    with use(bursar):
        admin = budgets.create_cost_centre(world.institution.id, "adm", "Administration", "administration")
        estate = budgets.create_cost_centre(world.institution.id, "EST", "Estate and works", "estate")
        with pytest.raises(ConflictError):
            budgets.create_cost_centre(world.institution.id, "ADM", "Again", "administration")
        with pytest.raises(HardValidation, match="not valid"):
            budgets.prepare_budget(world.institution.id, 2026, [budgets.LineInput(admin.id, "22-02", 1)])
        b = budgets.prepare_budget(
            world.institution.id,
            2026,
            [
                budgets.LineInput(admin.id, "22020301", 500_000 * NAIRA, description="Stationery"),
                budgets.LineInput(estate.id, "22020403", 2_000_000 * NAIRA, description="Building maintenance"),
            ],
        )
        with pytest.raises(Forbidden):
            budgets.approve_budget(b.id)  # a bursar does not approve
    with use(head):
        assert budgets.approve_budget(b.id).status == "approved"
        lines = {ln.economic_code: ln for ln in BudgetLine.objects.filter(budget_id=b.id)}
    stationery, works = lines["22020301"], lines["22020403"]
    with use(bursar):
        c = budgets.commit(
            stationery.id,
            300_000 * NAIRA,
            source_kind="requisition",
            source_id=uuid.uuid4(),
            description="Exam stationery",
        )
        with pytest.raises(HardValidation, match="Not enough budget"):
            budgets.commit(
                stationery.id, 300_000 * NAIRA, source_kind="requisition", source_id=uuid.uuid4(), description="More"
            )
        budgets.spend(c.id, 250_000 * NAIRA, final=True)  # the rest goes back to the line
        v = budgets.request_virement(works.id, stationery.id, 400_000 * NAIRA, "Additional examination stationery")
        with pytest.raises(Forbidden):
            budgets.decide_virement(v.id, True)
    with use(head):
        assert budgets.decide_virement(v.id, True).status == "approved"
    holder = staff_member(world, "Chika")
    with use(bursar):
        imp = budgets.request_imprest(
            holder.id, works.id, "Emergency roof repair", 150_000 * NAIRA, TODAY + dt.timedelta(14)
        )
    with use(head):
        imp = budgets.approve_imprest(imp.id)
        assert imp.status == "issued" and imp.commitment_id
    with use(bursar):
        imp = budgets.retire_imprest(
            imp.id,
            [{"receipt": "R-1", "payee": "Roofer", "amount_minor": 120_000 * NAIRA}],
            120_000 * NAIRA,
            30_000 * NAIRA,
        )
        assert imp.status == "retired"
        ex = budgets.execution(institution_id=world.institution.id, fiscal_year=2026)
    rows = {r["economic_code"]: r for r in ex["lines"]}
    assert rows["22020301"]["revised"] == 900_000 * NAIRA and rows["22020301"]["actual"] == 250_000 * NAIRA
    assert rows["22020301"]["committed"] == 0 and rows["22020301"]["available"] == 650_000 * NAIRA
    assert rows["22020403"]["revised"] == 1_600_000 * NAIRA and rows["22020403"]["actual"] == 120_000 * NAIRA
    assert rows["22020403"]["available"] == 1_480_000 * NAIRA
    assert ex["totals"]["actual"] == 370_000 * NAIRA
    with use(system_ctx()):
        from syntegra.finance.models import Imprest

        late = Imprest.objects.get(pk=imp.id)
        assert budgets.flag_overdue_imprest(TODAY + dt.timedelta(30)) == 0 and late.status == "retired"


# --------------------------------------------------------------------------- funding and loans
def programme(code: str) -> Any:
    from syntegra.funding.models import FundingProgramme

    with use(system_ctx()):
        return FundingProgramme.objects.get(code=code)


def test_programmes_are_seeded_and_student_loan_eligibility_is_explained(world: Any, as_user: Any) -> None:
    from syntegra.funding import services as funding
    from tests.integration.test_fee_clearance import enrol_at

    lrn = enrol_at(world, as_user, world.institution, "Ngozi", level="jss_3")
    officer, _ = as_(world, "FINO", world.institution.scope_node_id)
    with use(officer):
        codes = {p["code"] for p in funding.programmes()}
        assert {"NELFUND-FEES", "TETFUND-AI", "UBEC-MATCHING", "STAFF-COOP", "NHF-HOUSING"} <= codes
        app = funding.apply(
            programme("NELFUND-FEES").id,
            applicant_kind="learner",
            applicant_id=lrn.id,
            institution_id=world.institution.id,
            amount_minor=350_000 * NAIRA,
            purpose_detail="Tuition for the first year of a degree",
        )
        with pytest.raises(HardValidation, match="supports"):
            funding.apply(
                programme("NELFUND-FEES").id,
                applicant_kind="staff",
                applicant_id=uuid.uuid4(),
                institution_id=world.institution.id,
                amount_minor=1,
                purpose_detail="wrong kind of applicant",
            )
    failed = {r["rule"] for r in app.eligibility if not r["passed"]}
    assert app.status == "submitted" and app.eligible is False
    assert "education_levels" in failed and "ownership" not in failed  # JSS3 is not tertiary; a state school is public


def test_staff_loan_four_eyes_affordability_schedule_repayment_and_arrears(world: Any, hr: Any) -> None:  # noqa: F811
    from syntegra.funding import services as funding
    from syntegra.funding.models import RepaymentInstalment

    node = world.institution.scope_node_id
    officer, _ = as_(world, "HR", world.state_scope)
    head, _ = as_(world, "HEAD", node)
    bursar, _ = as_(world, "FINO", node)
    with use(officer):
        app = funding.apply(
            programme("STAFF-COOP").id,
            applicant_kind="staff",
            applicant_id=hr.staff.id,
            institution_id=world.institution.id,
            amount_minor=480_000 * NAIRA,
            purpose_detail="Children's school fees for the new session",
        )
        assert app.eligible and app.eligibility[0]["rule"] == "min_service_years"
        with pytest.raises(Forbidden):
            funding.recommend(app.id, "Recommended: good standing and service record")
    with use(head):
        funding.recommend(app.id, "Recommended: good standing and service record")
        with pytest.raises(Forbidden):
            funding.decide(app.id, True, "Approved by the co-operative committee")  # the reviewer cannot decide
    with use(bursar):
        funding.decide(app.id, True, "Approved by the co-operative committee")
        with pytest.raises(HardValidation, match="below the floor"):
            funding.sign_agreement(app.id, gross_pay_minor=60_000 * NAIRA, other_deductions_minor=20_000 * NAIRA)
        a = funding.sign_agreement(app.id, gross_pay_minor=250_000 * NAIRA, other_deductions_minor=40_000 * NAIRA)
        sched = list(RepaymentInstalment.objects.filter(agreement_id=a.id).order_by("sequence"))
        assert len(sched) == 24 and sum(i.principal_minor for i in sched) == 480_000 * NAIRA
        assert all(i.interest_minor > 0 for i in sched[:-1])
        funding.disburse(
            a.id, 480_000 * NAIRA, payee_kind="beneficiary", purpose="Loan to member", reference="COOP-001"
        )
        with pytest.raises(HardValidation, match="remains"):
            funding.disburse(a.id, 1, payee_kind="beneficiary", purpose="Loan to member", reference="COOP-002")
        first = sched[0]
        funding.record_repayment(
            a.id, first.principal_minor + first.interest_minor, method="payroll_deduction", reference="PAY-2026-11"
        )
        with pytest.raises(ConflictError):
            funding.record_repayment(a.id, 100, method="payroll_deduction", reference="PAY-2026-11")
        detail = funding.agreement(a.id)
    assert (
        detail["schedule"][0]["status"] == "paid"
        and detail["outstanding_minor"] == 480_000 * NAIRA - first.principal_minor
    )
    assert detail["status"] in ("repaying", "in_moratorium")
    with use(system_ctx()):
        res = funding.refresh_arrears(sched[3].due_on + dt.timedelta(1))
        from syntegra.funding.models import FundingAgreement

        late = FundingAgreement.objects.get(pk=a.id)
    assert res["newly_in_arrears"] >= 1 and late.status == "in_arrears"
    assert late.arrears_minor == sum(i.principal_minor + i.interest_minor for i in sched[1:4])
    # the borrower sees their own agreement without funding permissions
    with use(user_ctx(hr.user.id, hr.grant_id)):
        assert funding.agreement(a.id)["agreement_number"] == a.agreement_number
        assert [x["number"] for x in funding.my_agreements()] == [a.agreement_number]


def test_institutional_matching_grant_funds_a_budget_line(world: Any) -> None:
    from syntegra.finance import budgets
    from syntegra.finance.models import BudgetLine
    from syntegra.funding import services as funding

    node = world.institution2.scope_node_id
    bursar, _ = as_(world, "FINO", node)
    head, _ = as_(world, "HEAD", node)
    sta, _ = as_(world, "STA", world.state_scope)
    with use(bursar):
        cc = budgets.create_cost_centre(world.institution2.id, "CAP", "Capital projects", "project")
        b = budgets.prepare_budget(
            world.institution2.id, 2026, [budgets.LineInput(cc.id, "23030121", 0, "intervention")]
        )
    with use(head):
        budgets.approve_budget(b.id)
        line = BudgetLine.objects.get(budget_id=b.id)
    with use(bursar):
        app = funding.apply(
            programme("UBEC-MATCHING").id,
            applicant_kind="institution",
            applicant_id=world.institution2.id,
            institution_id=world.institution2.id,
            amount_minor=12_000_000 * NAIRA,
            purpose_detail="Rehabilitate two classroom blocks and build a toilet block",
            facts={"matching_contribution_pct": 50},
        )
        assert app.eligible
    with use(head):
        funding.recommend(app.id, "Both blocks are assessed unsafe; priority for the LGA")
    with use(sta):
        funding.decide(app.id, True, "Within the state's UBE intervention allocation")
        a = funding.sign_agreement(app.id)
        assert a.instrument == "matching_grant" and a.first_repayment_on is None
        funding.disburse(
            a.id,
            12_000_000 * NAIRA,
            payee_kind="institution",
            purpose="First tranche",
            reference="UBEC-T1",
            budget_line_id=line.id,
        )
        line.refresh_from_db()
        assert line.revised_minor == 12_000_000 * NAIRA
        assert funding.agreement(a.id)["status"] == "completed"
        with pytest.raises(HardValidation, match="not repaid"):
            funding.record_repayment(a.id, 1, method="bank_transfer", reference="X")


# --------------------------------------------------------------------------- estate and proactive actions
def build_school(world: Any) -> dict[str, Any]:
    from syntegra.estate import services as estate

    node = world.institution.scope_node_id
    head, _ = as_(world, "HEAD", node)
    with use(head):
        site = estate.register_site(
            world.institution.id,
            site_code="gssa-1",
            name="GSS Aba main site",
            owner="state_government",
            title_document="none_or_unknown",
            area_sqm=24_000,
            fenced="partly_fenced",
            encroachment="suspected",
        )
        block = estate.add_building(
            world.institution.id, "Classroom block A", built_year=1978, facilities={"water": True}
        )
        rooms = [estate.add_room(block.id, f"A{i}", "classroom", 45) for i in range(1, 4)]
        toilet = estate.add_room(block.id, "T1", "toilet", 10)
        gen = estate.add_asset(
            world.institution.id,
            "gen-001",
            "Generator 20 kVA",
            "generator",
            safety_check_due_on=TODAY - dt.timedelta(3),
        )
    return {"head": head, "site": site, "block": block, "rooms": rooms, "toilet": toilet, "generator": gen}


def test_property_register_assessment_and_proactive_actions(world: Any) -> None:
    from syntegra.estate import services as estate
    from syntegra.estate.models import FacilityAction

    s = build_school(world)
    with use(s["head"]):
        with pytest.raises(HardValidation, match="disagree"):
            estate.assess(
                "room",
                s["rooms"][0].id,
                condition_grade="good",
                usability="unusable",
                structural_risk="high",
                in_use=True,
            )
        estate.assess(
            "room",
            s["rooms"][0].id,
            condition_grade="unsafe",
            usability="unsafe_restricted",
            structural_risk="critical",
            in_use=True,
            learners_affected=45,
            repair_estimate_minor=3_500_000 * NAIRA,
            defects=[{"element": "roof", "defect": "sagging trusses", "severity": "critical"}],
        )
        estate.assess(
            "building",
            s["block"].id,
            condition_grade="poor",
            usability="usable_major_repairs",
            structural_risk="high",
            in_use=True,
            utilities={"water": True, "power": False},
        )
        estate.schedule_maintenance(
            "asset",
            s["generator"].id,
            task="Generator 250-hour service",
            task_kind="generator_service",
            frequency_days=90,
            next_due_on=TODAY - dt.timedelta(1),
        )
        ws = estate.workspace(world.institution.id)
    rules_ = {a["rule"] for a in ws["actions"]}
    assert {
        "unsafe_in_use",
        "never_assessed",
        "maintenance_overdue",
        "safety_check_overdue",
        "encroachment",
        "no_title",
    } <= rules_
    assert ws["actions"][0]["rule"] == "unsafe_in_use" and ws["actions"][0]["priority"] == "critical"
    assert ws["summary"]["classrooms"] == 3 and ws["summary"]["classrooms_usable"] == 2
    assert ws["summary"]["unsafe"] == 1 and ws["summary"]["repair_backlog"] == 3_500_000 * NAIRA
    unsafe = next(a for a in ws["actions"] if a["rule"] == "unsafe_in_use")
    with use(s["head"]):
        mr = estate.raise_work_order(unsafe["id"])
        assert mr.risk == "critical" and mr.room_id == s["rooms"][0].id
        with pytest.raises(HardValidation, match="Reason"):
            estate.act(next(a["id"] for a in ws["actions"] if a["rule"] == "no_title"), "dismissed", "no")
        estate.evaluate(world.institution.id)  # no duplicates
        assert FacilityAction.objects.filter(institution_id=world.institution.id, rule="unsafe_in_use").count() == 1
        # learners moved out and the roof repaired: the critical action clears itself
        estate.assess(
            "room",
            s["rooms"][0].id,
            condition_grade="good",
            usability="fully_usable",
            structural_risk="info",
            in_use=True,
        )
        estate.complete_maintenance(
            next(x["id"] for x in estate.workspace(world.institution.id)["schedules"]), cost_minor=85_000 * NAIRA
        )
        after = {a["rule"] for a in estate.workspace(world.institution.id)["actions"]}
    assert "unsafe_in_use" not in after and "maintenance_overdue" not in after
    with use(system_ctx()):
        n = estate.escalate(TODAY + dt.timedelta(10))
        esc = FacilityAction.objects.filter(institution_id=world.institution.id, rule="safety_check_overdue").get()
    assert n >= 1 and esc.escalation_level == 1 and esc.owner_role == "LGA"
    lga, _ = as_(world, "LGA", world.lga_scope)
    with use(lga):
        listed = estate.actions_in_scope()
        assert listed[0]["escalation_level"] == 1 and listed[0]["institution"] == world.institution.name
        estate.act(esc.id, "acknowledged")
    other, _ = as_(world, "LGA", world.lga2_scope)
    with use(other):
        assert estate.actions_in_scope() == []  # another LGA sees nothing of Aba South
        with pytest.raises(Forbidden):
            estate.workspace(world.institution.id)


# --------------------------------------------------------------------------- the warehouse and the Commissioner's view
def test_warehouse_load_and_commissioner_view(world: Any) -> None:
    from syntegra.analytics import warehouse
    from syntegra.analytics.models import DimInstitution
    from syntegra.estate import services as estate
    from syntegra.institutions.models import Institution

    s = build_school(world)
    with use(s["head"]):
        estate.assess(
            "room",
            s["rooms"][1].id,
            condition_grade="poor",
            usability="unusable",
            structural_risk="high",
            in_use=True,
            repair_estimate_minor=2_000_000 * NAIRA,
        )
        estate.assess(
            "site",
            s["site"].id,
            condition_grade="fair",
            usability="fully_usable",
            structural_risk="info",
            in_use=True,
            utilities={"water": True, "power": True},
        )
    with use(system_ctx()):
        first = warehouse.load()
        again = warehouse.load()
    assert first["institutions"] >= 2 and first["scope_aggregates"] == again["scope_aggregates"]
    comm, _ = as_(world, "COMM", world.state_scope)
    with use(comm):
        view = warehouse.state_overview()
    st = view["scope"]
    assert view["loaded"] and st["level"] == "state" and st["classrooms"] >= 3
    assert st["classrooms_usable"] == st["classrooms"] - 1 and st["facilities_unsafe_in_use"] >= 1
    assert st["repair_backlog_minor"] >= 2_000_000 * NAIRA and st["institutions_with_water"] >= 1
    lgas = {c["name"]: c for c in view["children"]}
    aba = next(c for n, c in lgas.items() if c["classrooms"])
    assert aba["level"] == "lga" and aba["institutions"] >= 1
    worst = next(i for i in view["institutions"] if i["name"] == world.institution.name)
    assert worst["infrastructure_index"] is not None and worst["actions_critical_open"] >= 1
    lga, _ = as_(world, "LGA", world.lga2_scope)
    with use(lga), pytest.raises(Forbidden):
        warehouse.state_overview(world.state_scope)  # an LGA sees its own subtree only
    # SCD2: a renamed institution gets a new current row; the old one is closed
    with use(system_ctx()):
        Institution.objects.filter(pk=world.institution.id).update(name="Government Secondary School Aba (renamed)")
        warehouse.load()
        rows = list(DimInstitution.unscoped.filter(institution_id=world.institution.id).order_by("institution_key"))
    assert [r.is_current for r in rows][-2:] == [False, True] and rows[-1].name.endswith("(renamed)")


# ------------------------------------------------------------------- security-agency curricula through the structure
def test_agency_specific_curricula_units_and_career_requirements(fse: Any) -> None:
    from syntegra.core import context
    from syntegra.security_training import registry
    from syntegra.security_training import services as sti
    from syntegra.security_training.models import (
        AgencyRank,
        SecurityAgency,
        SecurityCareerRequirement,
        SecurityCourse,
        SecurityCourseModule,
    )
    from tests.integration.test_security_training import as_fse

    with context.use(registry.system_context()):
        agencies = {a.code: a for a in SecurityAgency.objects.all()}
        for code in ("NPF", "NCS", "NIS", "FRSC", "NDLEA", "EFCC"):
            courses = SecurityCourse.objects.filter(agency_id=agencies[code].id, status="published", content_held=True)
            assert courses.exists()
            for c in courses:
                mods = set(SecurityCourseModule.objects.filter(course_id=c.id).values_list("code", flat=True))
                assert mods & {"POLACT", "CUSTACT", "IMMACT", "FRSCACT", "NDLEAACT", "EFCCACT"}, (code, c.code)
        for code in ("NSCDC", "NCOS", "NIS", "FFS", "NCS", "FRSC", "NDLEA"):
            assert AgencyRank.objects.filter(agency_id=agencies[code].id).count() >= 10
        assert SecurityCareerRequirement.objects.count() >= 30
        again = registry.seed_reference()
    assert again.agency_modules == again.course_units == again.career_requirements == 0  # idempotent

    army, _ = as_fse("SADM", "NA")
    with use(army):
        na = sti.careers(agencies["NA"].id)
        ltcol = next(r for r in na["ranks"] if r["code"] == "LTCOL")
        assert ltcol["requirements"][0]["course_code"] == "SC"
        assert ltcol["requirements"][0]["courses"][0]["institution"] == "Armed Forces Command and Staff College"
        assert na["coverage"]["with_requirements"] >= 6
        units = {u["role"]: u["unit_code"] for c in na["courses"] if c["code"] == "BMT" for u in c["units"]}
        assert units["approving_authority"] == "AHQ" and units["sponsor"] == "TRADOC"
    root, _ = as_fse("SADM", "NG-FSE")
    with use(root):
        nda_rc = next(c for c in sti.careers(agencies["DHQ"].id)["courses"] if c["code"] == "RC")
        quota = {u["agency"] for u in nda_rc["units"] if u["role"] == "quota_holder"}
        assert quota == {"NA", "NN", "NAF"}


def test_agency_curriculum_import_versions_courses(fse: Any) -> None:
    from syntegra.security_training import services as sti
    from syntegra.security_training.models import SecurityCourse
    from tests.integration.test_security_training import as_fse

    head = ",".join(sti.IMPORT_COLUMNS)
    row = (
        "NPF,POLAC,CYB{n},Cybercrime investigation administration,specialist,certificate,Certificate,,6,INSP ASP,"
        "{m},{t},{a},written,{h}"
    )
    code = uuid.uuid4().hex[:4].upper()
    text = "\n".join(
        [
            head,
            row.format(n=code, m="LAW", t="Cybercrimes Act 2015 and electronic evidence", a="law_human_rights", h=20),
            row.format(n=code, m="RECS", t="Digital case records management", a="ict_cyber", h=30),
        ]
    )
    police, _ = as_fse("SADM", "NPF")
    with use(police):
        dry = sti.import_courses(text, dry_run=True)
        assert dry == {**dry, "rows": 2, "courses": 1, "errors": [], "applied": False}
        assert sti.import_courses(text)["created"] == 1
        assert sti.import_courses(text)["unchanged"] == 1
        changed = text.replace("Digital case records management", "Digital case records and data protection")
        assert sti.import_courses(changed)["new_versions"] == 1
        versions = list(
            SecurityCourse.objects.filter(code=f"CYB{code}").order_by("version").values_list("version", "status")
        )
        assert versions == [("1.0", "superseded"), ("1.1", "published")]
        bad = text.replace("Digital case records management", "Firing range qualification")
        assert sti.import_courses(bad)["errors"][0]["problems"][0].startswith("syllabus headings must not")
        army_row = text.replace("NPF,POLAC", "NA,NDA")
        assert "not one you administer" in sti.import_courses(army_row, dry_run=True)["errors"][0]["problems"][0]
