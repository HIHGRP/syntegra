"""CR-001 pure rules: HR employment, leave and payroll arithmetic; integrity detection; fee-clearance rules."""

import datetime as dt
import uuid
from decimal import Decimal

import pytest

from syntegra.clearance.domain import rules as fcl
from syntegra.hr.domain import employment, integrity, leave, payroll

K = payroll.KOBO


class TestEmployment:
    def test_teacher_retires_at_65_or_40_years_whichever_first(self) -> None:
        on, basis = employment.retirement_due(dt.date(1975, 3, 1), dt.date(2000, 1, 10), 65, 40)
        assert (on, basis) == (dt.date(2040, 1, 10), "length_of_service")
        on, basis = employment.retirement_due(dt.date(1975, 3, 1), dt.date(2015, 1, 10), 65, 40)
        assert (on, basis) == (dt.date(2040, 3, 1), "age")

    def test_promotion_eligibility(self) -> None:
        checks = employment.promotion_eligibility(
            on=dt.date(2026, 10, 1),
            grade_level=8,
            max_grade_level=16,
            last_promotion_on=dt.date(2022, 1, 1),
            present_appointment_on=dt.date(2015, 1, 1),
            years_per_promotion=3,
            open_disciplinary=False,
            confirmed=True,
            last_rating="good",
        )
        assert all(c.passed for c in checks)
        checks = employment.promotion_eligibility(
            on=dt.date(2026, 10, 1),
            grade_level=8,
            max_grade_level=16,
            last_promotion_on=dt.date(2025, 1, 1),
            present_appointment_on=dt.date(2015, 1, 1),
            years_per_promotion=3,
            open_disciplinary=True,
            confirmed=True,
            last_rating="good",
        )
        failed = {c.name for c in checks if not c.passed}
        assert failed == {"years_on_grade", "no_open_disciplinary_case"}


class TestLeave:
    def test_working_and_calendar_days(self) -> None:
        assert leave.leave_days(dt.date(2026, 10, 12), dt.date(2026, 10, 23), "working_days") == 10
        assert (
            leave.leave_days(dt.date(2026, 10, 12), dt.date(2026, 10, 23), "working_days", [dt.date(2026, 10, 14)]) == 9
        )
        assert (
            leave.leave_days(dt.date(2026, 10, 1), dt.date(2026, 10, 1) + dt.timedelta(days=111), "calendar_days")
            == 112
        )

    def test_most_specific_policy_wins(self) -> None:
        general = leave.Policy("A", "annual_leave", None, 7, 17, Decimal(30), "working_days", Decimal(5))
        junior = leave.Policy("J", "annual_leave", None, 1, 6, Decimal(21), "working_days", Decimal(5))
        teacher = leave.Policy("T", "annual_leave", "TEACHER", 7, 17, Decimal(35), "working_days", Decimal(5))
        assert leave.select_policy([general, junior], "annual_leave", "SUPPORT", 4) is junior
        assert leave.select_policy([general, junior, teacher], "annual_leave", "TEACHER", 9) is teacher
        assert leave.select_policy([general], "sick", "TEACHER", 9) is None


class TestPayroll:
    def test_paye_bands_nigeria_tax_act_2025(self) -> None:
        assert payroll.annual_paye(800_000 * K) == 0
        assert payroll.annual_paye(3_000_000 * K) == 330_000 * K
        assert payroll.annual_paye(12_000_000 * K) == 1_950_000 * K
        assert payroll.annual_paye(60_000_000 * K) == (330_000 + 1_620_000 + 2_730_000 + 5_750_000 + 2_500_000) * K

    def test_monthly_payslip(self) -> None:
        s = payroll.compute_month(
            1_800_000 * K,
            {"HOUSING": 60_000 * K, "TRANSPORT": 40_000 * K},
            other_elements=(payroll.Element("UNION", "voluntary_deduction", 1_000 * K),),
        )
        lines = {ln["code"]: ln["amount"] for ln in s.lines}
        assert s.gross == 250_000 * K
        assert lines["PENSION_EE"] == -20_000 * K and lines["PENSION_ER"] == 25_000 * K
        assert lines["NHF"] == -3_750 * K
        assert lines["PAYE"] == -2_393_750  # (2,715,000 − 800,000) × 15% ÷ 12, in kobo
        assert s.net == s.gross - s.deductions and s.deductions == (20_000 + 3_750 + 1_000) * K + 2_393_750

    def test_low_earner_pays_no_paye(self) -> None:
        s = payroll.compute_month(840_000 * K, {})
        assert {ln["code"]: ln["amount"] for ln in s.lines}["PAYE"] == 0


class TestIntegrity:
    def test_shared_tokens_and_concurrent_posts(self) -> None:
        a, b, c = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        f = integrity.shared_tokens([(a, b"t1"), (b, b"t1"), (c, b"t2")], "shared_bank_account")
        assert {x.staff_id for x in f} == {a, b}
        e1, e2 = uuid.uuid4(), uuid.uuid4()
        f = integrity.concurrent_posts([(a, e1, uuid.uuid4()), (a, e2, uuid.uuid4()), (b, e1, uuid.uuid4())])
        assert [x.staff_id for x in f] == [a]

    def test_past_retirement_and_attendance(self) -> None:
        a, b = uuid.uuid4(), uuid.uuid4()
        assert [
            x.staff_id
            for x in integrity.past_retirement([(a, dt.date(2026, 1, 1), None), (b, None, None)], dt.date(2026, 10, 1))
        ] == [a]
        assert [
            x.staff_id for x in integrity.no_recent_attendance([(a, None), (b, None)], {b}, dt.date(2026, 10, 1))
        ] == [a]


class TestFeeClearance:
    def ob(self, status: str = "outstanding", creditor: uuid.UUID | None = None, amount: int = 1000) -> fcl.Obligation:
        return fcl.Obligation(
            uuid.uuid4(), creditor or uuid.uuid4(), "School", "tuition_fees", amount, "NGN", dt.date(2026, 5, 1), status
        )

    def test_assessment(self) -> None:
        assert (
            fcl.assess([], protected_reason=None, prior_outstanding_checks=0, creditors_with_open=0).result == "clear"
        )
        a = fcl.assess(
            [self.ob(), self.ob("disputed")], protected_reason=None, prior_outstanding_checks=0, creditors_with_open=1
        )
        assert a.result == "outstanding" and a.total_outstanding_minor == 1000
        assert (
            fcl.assess(
                [self.ob("disputed")], protected_reason=None, prior_outstanding_checks=0, creditors_with_open=0
            ).result
            == "disputed_only"
        )
        assert (
            fcl.assess(
                [self.ob()],
                protected_reason="public_basic_education",
                prior_outstanding_checks=0,
                creditors_with_open=1,
            ).result
            == "protected"
        )
        a = fcl.assess([self.ob(), self.ob()], protected_reason=None, prior_outstanding_checks=0, creditors_with_open=2)
        assert a.pattern_flags[0]["flag"] == "repeat_unsettled_transfers"

    def test_sdaf_never_published(self) -> None:
        assert fcl.kind_for_charge("SDAF_TERM") is None
        assert fcl.kind_for_charge("TUITION_T1") == "tuition_fees"
        assert fcl.kind_for_charge("BUS_ROUTE_3") == "transport"
        assert fcl.kind_for_charge("CLUB") == "other_dues"
        errs = fcl.validate_publication(
            kind="sdaf",
            amount_minor=1,
            oldest_due_on=dt.date(2026, 1, 1),
            evidence=["x"],
            source="ledger",
            on=dt.date(2026, 10, 1),
        )
        assert any("SDAF" in e for e in errs)

    def test_publication_guards(self) -> None:
        on = dt.date(2026, 10, 1)
        assert (
            fcl.validate_publication(
                kind="tuition_fees",
                amount_minor=5,
                oldest_due_on=dt.date(2026, 5, 1),
                evidence=[{"invoice": "INV-1"}],
                source="ledger",
                on=on,
            )
            == []
        )
        assert fcl.validate_publication(
            kind="tuition_fees",
            amount_minor=5,
            oldest_due_on=dt.date(2019, 5, 1),
            evidence=[{"invoice": "INV-1"}],
            source="ledger",
            on=on,
        )
        assert fcl.validate_publication(
            kind="damaged_property",
            amount_minor=5,
            oldest_due_on=dt.date(2026, 5, 1),
            evidence=["photo"],
            source="manual_with_evidence",
            on=on,
        )

    @pytest.mark.parametrize(
        ("level", "public", "expected"),
        [
            ("JSS1", True, True),
            ("jss_2", True, True),
            ("PRY4", True, True),
            ("ECCDE", True, True),
            ("SSS1", True, False),
            ("jss_2", False, False),
            ("ND1", True, False),
        ],
    )
    def test_public_basic_education_is_protected(self, level: str, public: bool, expected: bool) -> None:
        assert fcl.is_public_basic_education(public, level) is expected

    def test_there_is_no_refusal_decision(self) -> None:
        assert "refuse" not in fcl.DECISIONS
        assert fcl.decision_errors("refuse", protected_reason=None, payment_plan_ref=None, reason="x" * 20)
        assert fcl.decision_errors(
            "admit_with_payment_plan", protected_reason=None, payment_plan_ref=None, reason="Agreed with the bursar"
        )
        assert not fcl.decision_errors(
            "admit_protected",
            protected_reason="safeguarding",
            payment_plan_ref=None,
            reason="Child protection plan in place",
        )
