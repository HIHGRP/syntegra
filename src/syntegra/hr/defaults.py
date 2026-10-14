"""Default HR configuration for a new state tenant (idempotent). Every value is data the state can version.

* Statutory payroll tables (2026): PAYE bands of the Nigeria Tax Act 2025, pension 8%/10% (Pension Reform Act 2014),
  NHF 2.5% of basic — confirm with the state's payroll and tax advisers before the first live pay run.
* Leave: Public Service Rules practice — annual 21 working days (GL 01–06) and 30 (GL 07+), sick 30 working days,
  maternity 16 weeks, paternity 14 working days, casual 7 working days.
* Cadres: teacher and education officer with the statutory retirement rules (teachers 65 years / 40 years of
  service under the Harmonised Retirement Age for Teachers in Nigeria Act 2022; others 60 / 35).
* Salary structure ``AB-TSS-ILLUSTRATIVE``: a placeholder scale so the platform computes end to end. It is NOT the
  state's approved scale and must be replaced (a new version) before payroll goes live.
"""

from __future__ import annotations

import datetime as dt
import uuid
from decimal import Decimal

from syntegra.core import uow
from syntegra.hr.domain.payroll import DEFAULT_NHF, DEFAULT_PAYE_BANDS, DEFAULT_PENSION, KOBO
from syntegra.hr.models import Cadre, LeavePolicy, PayElement, SalaryScalePoint, SalaryStructure
from syntegra.people.models import PayrollTaxTable

LEAVE = [
    # code, type, cadre, gl_min, gl_max, days, basis, carry_over
    ("ANNUAL-JUNIOR", "annual_leave", None, 1, 6, "21", "working_days", "5"),
    ("ANNUAL-SENIOR", "annual_leave", None, 7, 17, "30", "working_days", "5"),
    ("SICK", "sick", None, 1, 17, "30", "working_days", "0"),
    ("MATERNITY", "maternity", None, 1, 17, "112", "calendar_days", "0"),
    ("PATERNITY", "paternity", None, 1, 17, "14", "working_days", "0"),
    ("CASUAL", "casual", None, 1, 17, "7", "working_days", "0"),
    ("EXAMINATION", "examination", None, 1, 17, "10", "working_days", "0"),
]
ELEMENTS = [
    ("BASIC", "Basic salary", "earning", "fixed", None, None, True, True),
    ("HOUSING", "Housing allowance", "allowance", "pct_of_basic", "40", None, True, True),
    ("TRANSPORT", "Transport allowance", "allowance", "pct_of_basic", "25", None, True, True),
    ("RURAL", "Rural posting allowance", "allowance", "fixed", None, None, True, False),
    ("PAYE", "Pay As You Earn (Nigeria Tax Act 2025)", "statutory_deduction", "table", None, "paye", False, False),
    ("PENSION_EE", "Pension — employee 8%", "statutory_deduction", "table", None, "pension", False, False),
    ("PENSION_ER", "Pension — employer 10%", "employer_contribution", "table", None, "pension", False, False),
    ("NHF", "National Housing Fund 2.5%", "statutory_deduction", "table", None, "nhf", False, False),
    ("UNION", "Union dues (NUT)", "voluntary_deduction", "fixed", None, None, False, False),
    ("COOP", "Cooperative savings", "voluntary_deduction", "fixed", None, None, False, False),
    ("LOAN", "Loan repayment", "loan_repayment", "fixed", None, None, False, False),
]


def _illustrative_points() -> list[tuple[int, int, int, dict[str, object]]]:
    points: list[tuple[int, int, int, dict[str, object]]] = []
    for gl in range(1, 18):
        for step in range(1, 16):
            annual = (480_000 + (gl - 1) * 210_000 + (step - 1) * 18_000) * KOBO
            points.append((gl, step, annual, {"HOUSING": {"pct_of_basic": 40}, "TRANSPORT": {"pct_of_basic": 25}}))
    return points


def seed(state_scope_id: uuid.UUID) -> None:
    with uow.command("registry", None, action="seed_hr", record_kind="cadre") as cmd:
        if not SalaryStructure.objects.filter(code="AB-TSS-ILLUSTRATIVE").exists():
            st = cmd.add(
                SalaryStructure(
                    scope_node_id=state_scope_id,
                    code="AB-TSS-ILLUSTRATIVE",
                    title="Illustrative teacher scale (replace)",
                    currency="NGN",
                    effective_from=dt.date(2026, 1, 1),
                    version=1,
                    approval_instrument="Placeholder — replace with the approved scale",
                    status="published",
                )
            )
            SalaryScalePoint.unscoped.using(cmd.alias).bulk_create(
                [
                    SalaryScalePoint(
                        tenant_id=st.tenant_id,
                        structure_id=st.id,
                        grade_level=gl,
                        step=step,
                        annual_basic_minor=basic,
                        currency="NGN",
                        allowances=allow,
                    )
                    for gl, step, basic, allow in _illustrative_points()
                ]
            )
        for code, title, teaching, category, entry, top, age, service in [
            ("TEACHER", "Teacher", True, "teaching", 7, 16, 65, 40),
            ("EDU-OFFICER", "Education officer", False, "administrative", 7, 17, 60, 35),
            ("SUPPORT", "Support staff", False, "support", 1, 6, 60, 35),
        ]:
            if not Cadre.objects.filter(code=code).exists():
                cmd.add(
                    Cadre(
                        scope_node_id=state_scope_id,
                        code=code,
                        title=title,
                        staff_category=category,
                        is_teaching=teaching,
                        salary_structure_code="AB-TSS-ILLUSTRATIVE",
                        entry_grade_level=entry,
                        max_grade_level=top,
                        years_per_promotion=3,
                        retirement_age=age,
                        max_years_service=service,
                        status="active",
                    )
                )
        if cmd.changes == []:
            cmd.audited = False
    with uow.command("ops", None, action="seed_hr", record_kind="leave_policy") as cmd:
        for code, typ, cadre, lo, hi, days, basis, carry in LEAVE:
            if not LeavePolicy.objects.filter(code=code).exists():
                cmd.add(
                    LeavePolicy(
                        scope_node_id=state_scope_id,
                        code=code,
                        leave_type=typ,
                        cadre_code=cadre,
                        grade_level_min=lo,
                        grade_level_max=hi,
                        days_per_year=Decimal(days),
                        day_basis=basis,
                        carry_over_max=Decimal(carry),
                        requires_document=typ in ("sick", "maternity"),
                        is_paid=True,
                        version=1,
                        status="published",
                    )
                )
        for code, title, kind, method, rate, table, taxable, pensionable in ELEMENTS:
            if not PayElement.objects.filter(code=code).exists():
                cmd.add(
                    PayElement(
                        scope_node_id=state_scope_id,
                        code=code,
                        title=title,
                        element_kind=kind,
                        calc_method=method,
                        rate=Decimal(rate) if rate else None,
                        table_kind=table,
                        is_taxable=taxable,
                        is_pensionable=pensionable,
                        version=1,
                        status="published",
                    )
                )
        for kind, bands in (("paye", DEFAULT_PAYE_BANDS), ("pension", DEFAULT_PENSION), ("nhf", DEFAULT_NHF)):
            if not PayrollTaxTable.objects.filter(table_kind=kind).exists():
                cmd.add(
                    PayrollTaxTable(
                        table_kind=kind, version=1, bands=bands, effective_from=dt.date(2026, 1, 1), status="published"
                    )
                )
        if cmd.changes == []:
            cmd.audited = False
