"""Funding and loan programmes seeded into every registry (FR-FND-01).

Terms are taken from public sources where they exist and are marked ``to_confirm`` until the provider confirms
them; programmes a state or institution runs itself (scholarship boards, staff co-operatives, PTA and alumni
funds) are ``illustrative`` templates the state adjusts. Amounts are kobo. Nothing here is advice on terms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

I = "illustrative"  # noqa: E741
C = "to_confirm"
TERTIARY_PUBLIC = {"ownership": ["federal", "state"], "education_levels": ["TERTIARY"], "actively_enrolled": True}


@dataclass(frozen=True)
class Programme:
    code: str
    name: str
    provider: str
    provider_kind: str
    beneficiary: str
    purpose: str
    instrument: str
    basis: str
    rate: float = 0
    tenor: int | None = None
    moratorium: int = 0
    max_minor: int | None = None
    body: str | None = None
    eligibility: dict[str, Any] = field(default_factory=dict)
    terms: dict[str, Any] = field(default_factory=dict)
    status: str = C


PROGRAMMES: list[Programme] = [
    # ------------------------------------------------------------------ student support
    Programme(
        "NELFUND-FEES",
        "Student loan — institutional charges (tuition and fees)",
        "Nigerian Education Loan Fund (NELFUND)",
        "federal_government_agency",
        "learner",
        "tuition_fees",
        "loan",
        "income_contingent",
        body="NELFUND",
        eligibility=TERTIARY_PUBLIC,
        terms={
            "law": "Students Loans (Access to Higher Education) Act 2024",
            "interest": "interest-free",
            "paid_to": "institution",
            "repayment": "a share of earnings once employed, starting after national service",
        },
    ),
    Programme(
        "NELFUND-UPKEEP",
        "Student loan — upkeep allowance",
        "Nigerian Education Loan Fund (NELFUND)",
        "federal_government_agency",
        "learner",
        "upkeep",
        "loan",
        "income_contingent",
        body="NELFUND",
        eligibility=TERTIARY_PUBLIC,
        terms={"law": "Students Loans (Access to Higher Education) Act 2024", "paid_to": "student, monthly"},
    ),
    Programme(
        "STATE-SCHOLARSHIP",
        "State scholarship (merit and need)",
        "State Scholarship Board",
        "state_government",
        "learner",
        "scholarship",
        "scholarship",
        "none",
        eligibility={"education_levels": ["TERTIARY"], "actively_enrolled": True},
        status=I,
    ),
    Programme(
        "STATE-BURSARY",
        "State bursary for indigent students",
        "State Scholarship Board",
        "state_government",
        "learner",
        "bursary",
        "bursary",
        "none",
        eligibility={"actively_enrolled": True, "max_household_income_minor": 120_000_000},
        status=I,
    ),
    Programme(
        "SEND-SUPPORT",
        "Support for learners with special educational needs (devices, transport, assistive technology)",
        "State Ministry of Education",
        "state_government",
        "learner",
        "special_needs",
        "grant",
        "none",
        eligibility={"actively_enrolled": True},
        status=I,
    ),
    # ------------------------------------------------------------------ institutional capital
    Programme(
        "TETFUND-AI",
        "TETFund annual direct disbursement intervention",
        "Tertiary Education Trust Fund (TETFund)",
        "federal_government_agency",
        "institution",
        "capital_works",
        "intervention",
        "none",
        body="TETFUND",
        eligibility={
            "ownership": ["federal", "state"],
            "categories": ["university", "polytechnic", "college_of_education"],
        },
        terms={"law": "Tertiary Education Trust Fund (Establishment) Act 2011"},
    ),
    Programme(
        "UBEC-MATCHING",
        "UBE intervention — matching grant for basic education infrastructure",
        "Universal Basic Education Commission (UBEC)",
        "federal_government_agency",
        "institution",
        "capital_works",
        "matching_grant",
        "none",
        body="UBEC",
        eligibility={
            "ownership": ["state", "lga"],
            "categories": ["eccde_centre", "nursery_primary", "primary", "junior_secondary"],
            "matching_contribution_pct": 50,
        },
        terms={"law": "Compulsory, Free Universal Basic Education Act 2004", "counterpart": "state contributes 50%"},
    ),
    Programme(
        "DP-INFRA-GRANT",
        "Development partner school infrastructure grant",
        "Development partner (e.g. World Bank-assisted programme)",
        "development_partner",
        "institution",
        "capital_works",
        "grant",
        "none",
        eligibility={"ownership": ["state", "lga", "community"]},
        status=I,
    ),
    Programme(
        "BANK-CAPEX",
        "Term loan for school buildings and equipment",
        "Commercial or development bank",
        "bank",
        "institution",
        "capital_works",
        "loan",
        "annuity",
        rate=0,
        tenor=60,
        moratorium=6,
        eligibility={"ownership": ["private", "faith", "community", "ngo"]},
        terms={"rate": "agreed per facility at signing", "security": "as agreed with the lender"},
        status=I,
    ),
    Programme(
        "PTA-ALUMNI",
        "PTA, alumni and philanthropy support",
        "Parent–teacher association, alumni association or foundation",
        "alumni",
        "institution",
        "equipment",
        "in_kind",
        "none",
        status=I,
    ),
    # ------------------------------------------------------------------ staff welfare
    Programme(
        "STAFF-COOP",
        "Staff co-operative society loan",
        "Staff multipurpose co-operative society",
        "cooperative",
        "staff",
        "welfare_emergency",
        "loan",
        "payroll_deduction",
        rate=10,
        tenor=24,
        max_minor=200_000_000,
        eligibility={"min_service_years": 1},
        status=I,
    ),
    Programme(
        "SALARY-ADVANCE",
        "Salary advance",
        "Employer",
        "employer",
        "staff",
        "salary_advance",
        "salary_advance",
        "payroll_deduction",
        tenor=3,
        eligibility={"confirmed_appointment": True},
        terms={"ceiling": "one month's basic salary"},
        status=I,
    ),
    Programme(
        "NHF-HOUSING",
        "National Housing Fund mortgage loan",
        "Federal Mortgage Bank of Nigeria (National Housing Fund)",
        "federal_government_agency",
        "staff",
        "housing",
        "loan",
        "annuity",
        rate=6,
        tenor=360,
        eligibility={"min_service_years": 0.5},
        terms={"law": "National Housing Fund Act", "contributions": "NHF contributions required"},
    ),
    Programme(
        "VEHICLE-LOAN",
        "Vehicle purchase or refurbishment loan",
        "Employer (state public service)",
        "employer",
        "staff",
        "vehicle",
        "loan",
        "payroll_deduction",
        tenor=48,
        eligibility={"confirmed_appointment": True, "min_service_years": 2},
        terms={"rate": "set by the state's public service rules"},
        status=I,
    ),
    Programme(
        "STAFF-DEV",
        "Staff development and conference support",
        "Institution or TETFund",
        "institution",
        "staff",
        "staff_development",
        "grant",
        "none",
        eligibility={"confirmed_appointment": True},
        status=I,
    ),
]
