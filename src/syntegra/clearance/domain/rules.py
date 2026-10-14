"""Fee-clearance rules (CR-001, FR-FCL-01..08) — pure functions.

The check *informs*; it never decides. Principle P9 (education is never withheld for money) and the
human-only rule for admission refusal mean there is deliberately no "refuse" outcome: an outstanding
obligation requires a recorded human decision — admit, admit with a payment plan, or defer pending
settlement — and some learners are always admitted.
"""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Iterable
from dataclasses import dataclass

OPEN = ("outstanding", "payment_plan", "disputed")
DECISIONS = ("admit", "admit_with_payment_plan", "defer_pending_settlement", "admit_protected")
HUMAN_PROTECTED = ("send", "safeguarding", "child_in_care", "displaced", "other_vulnerability")
LIMITATION_YEARS = 6  # simple contract debts (Limitation Laws of the states)
RECONFIRM_DAYS = 90
DISPUTE_SCHOOL_DAYS = 10

# Charge-type code prefixes → obligation kind. SDAF is deliberately absent: it is pursued only through state
# revenue processes (MFS §20.9) and can never appear in an admission check.
CHARGE_KINDS = [
    ("TUITION", "tuition_fees"),
    ("SCHOOL_FEE", "tuition_fees"),
    ("FEES", "tuition_fees"),
    ("BOARD", "boarding"),
    ("HOSTEL", "boarding"),
    ("ACCOM", "boarding"),
    ("EXAM", "examination_fees"),
    ("WAEC", "examination_fees"),
    ("NECO", "examination_fees"),
    ("TRANSPORT", "transport"),
    ("BUS", "transport"),
    ("MEAL", "meals"),
    ("FEEDING", "meals"),
    ("BOOK", "books_and_materials"),
    ("MATERIAL", "books_and_materials"),
    ("UNIFORM", "uniform"),
    ("DEV", "development_levy"),
    ("PTA", "development_levy"),
    ("LEVY", "development_levy"),
    ("DAMAGE", "damaged_property"),
    ("LIBRARY", "library"),
]
NEVER = ("SDAF", "DIGITAL_ACCESS")


def kind_for_charge(code: str) -> str | None:
    """Obligation kind for a ledger charge type; ``None`` = never published (SDAF)."""
    c = code.upper()
    if c.startswith(NEVER):
        return None
    for prefix, kind in CHARGE_KINDS:
        if c.startswith(prefix):
            return kind
    return "other_dues"


def is_public_basic_education(is_public: bool, level: str) -> bool:
    """UBE Act 2004: early childhood, primary and junior secondary in public institutions are free."""
    lv = level.lower().replace(" ", "").replace("_", "")
    return is_public and lv.startswith(("eccde", "kg", "nursery", "pry", "primary", "jss", "basic"))


@dataclass(frozen=True)
class Obligation:
    id: uuid.UUID
    creditor_institution_id: uuid.UUID
    creditor_name: str
    kind: str
    amount_minor: int
    currency: str
    oldest_due_on: dt.date
    status: str


@dataclass(frozen=True)
class Assessment:
    result: str  # clear | outstanding | disputed_only | protected
    total_outstanding_minor: int
    obligations: list[Obligation]
    protected_reason: str | None
    pattern_flags: list[dict[str, object]]


def assess(
    obligations: Iterable[Obligation],
    *,
    protected_reason: str | None,
    prior_outstanding_checks: int,
    creditors_with_open: int,
) -> Assessment:
    obs = [o for o in obligations if o.status in OPEN]
    owing = [o for o in obs if o.status != "disputed"]
    total = sum(o.amount_minor for o in owing)
    flags: list[dict[str, object]] = []
    if creditors_with_open >= 2 or prior_outstanding_checks >= 2:
        flags.append(
            {
                "flag": "repeat_unsettled_transfers",
                "creditors_with_open_obligations": creditors_with_open,
                "prior_checks_with_outstanding": prior_outstanding_checks,
            }
        )
    if not obs:
        result = "clear"
    elif protected_reason:
        result = "protected"
    elif not owing:
        result = "disputed_only"
    else:
        result = "outstanding"
    return Assessment(result, total, obs, protected_reason, flags)


def validate_publication(
    *, kind: str, amount_minor: int, oldest_due_on: dt.date, evidence: list[object], source: str, on: dt.date
) -> list[str]:
    errs = []
    if kind in ("sdaf", "sdaf_levy"):
        errs.append("SDAF arrears are never published to the clearance register")
    if amount_minor <= 0:
        errs.append("amount must be positive (publish zero as settlement)")
    if oldest_due_on > on:
        errs.append("an obligation cannot be due in the future")
    if (on - oldest_due_on).days > LIMITATION_YEARS * 365:
        errs.append(f"claims older than {LIMITATION_YEARS} years cannot be published")
    if not evidence:
        errs.append("evidence is required (invoice numbers, or documents for manual claims)")
    if source == "manual_with_evidence" and not any(isinstance(e, dict) and e.get("document_id") for e in evidence):
        errs.append("manual claims need at least one evidence document")
    return errs


def decision_errors(
    decision: str, *, protected_reason: str | None, payment_plan_ref: str | None, reason: str
) -> list[str]:
    errs = []
    if decision not in DECISIONS:
        errs.append(f"decision must be one of {', '.join(DECISIONS)} — refusal is not a clearance outcome")
    if decision == "admit_protected" and protected_reason not in (*HUMAN_PROTECTED, "public_basic_education"):
        errs.append("state why the learner is protected")
    if decision == "admit_with_payment_plan" and not payment_plan_ref:
        errs.append("give the payment plan reference agreed with the creditor")
    if len(reason.strip()) < 10:
        errs.append("give a reason of at least 10 characters")
    return errs
