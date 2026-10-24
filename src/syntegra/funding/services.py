"""Funding and loan platforms (CR-006, FR-FND-01 – FR-FND-07).

Programme → application (eligibility evaluated, recommended and decided by two different people) → agreement
(terms and repayment schedule) → disbursements → repayments allocated oldest instalment first → arrears.
Institutional funding can be received into a budget line and linked to the capital plan item it pays for.
Loans and arrears never touch a learner's education (P9): nothing here is read by attendance, assessment,
results or record transfer (import contract). Borrowers always see their own agreements.
"""

from __future__ import annotations

import datetime as dt
import uuid
from decimal import Decimal
from typing import Any

from syntegra.core import authz, context, policy, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.ids import short_code
from syntegra.funding import reference as ref
from syntegra.funding.domain import eligibility, schedule
from syntegra.funding.models import (
    FundingAgreement,
    FundingApplication,
    FundingDisbursement,
    FundingProgramme,
    FundingRepayment,
    RepaymentInstalment,
)
from syntegra.institutions.models import Institution

REPAYABLE = ("loan", "salary_advance")
OPEN_AGREEMENT = ("signed", "disbursing", "in_moratorium", "repaying", "in_arrears")


def _number(prefix: str) -> str:
    return f"{prefix}-{dt.date.today():%Y}-{short_code().replace('-', '')}"


def _institution(institution_id: uuid.UUID) -> Institution:
    inst: Institution | None = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _own_staff_id(ctx: context.Context) -> uuid.UUID | None:
    from syntegra.people.models import Staff

    s = Staff.objects.filter(user_id=ctx.actor_id).first() if ctx.actor_id else None
    return s.id if s else None


# --------------------------------------------------------------------------- programmes (FR-FND-01)
def seed_programmes(root_scope_id: uuid.UUID) -> int:
    """Load the national and template programmes into the current registry (idempotent)."""
    have = set(FundingProgramme.objects.values_list("code", flat=True))
    n = 0
    with uow.command("ops", None, action="seed_reference", record_kind="funding_programme") as cmd:
        for p in ref.PROGRAMMES:
            if p.code in have:
                continue
            cmd.add(
                FundingProgramme(
                    scope_node_id=root_scope_id,
                    code=p.code,
                    name=p.name,
                    provider_name=p.provider,
                    provider_kind=p.provider_kind,
                    provider_body_code=p.body,
                    beneficiary_kind=p.beneficiary,
                    purpose=p.purpose,
                    instrument=p.instrument,
                    interest_rate=Decimal(str(p.rate)),
                    tenor_months=p.tenor,
                    moratorium_months=p.moratorium,
                    repayment_basis=p.basis,
                    max_amount_minor=p.max_minor,
                    currency="NGN",
                    eligibility=p.eligibility or None,
                    terms=p.terms or None,
                    data_status=p.status,
                    status="published",
                )
            )
            n += 1
        if not n:
            cmd.audited = False
    return n


def programmes(beneficiary_kind: str | None = None) -> list[dict[str, Any]]:
    authz.require("funding:view")
    qs = FundingProgramme.objects.filter(status="published").order_by("beneficiary_kind", "name")
    if beneficiary_kind:
        qs = qs.filter(beneficiary_kind=beneficiary_kind)
    return [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "provider": p.provider_name,
            "beneficiary_kind": p.beneficiary_kind,
            "purpose": p.purpose,
            "instrument": p.instrument,
            "interest_rate": p.interest_rate,
            "tenor_months": p.tenor_months,
            "moratorium_months": p.moratorium_months,
            "repayment_basis": p.repayment_basis,
            "max_amount_minor": p.max_amount_minor,
            "eligibility": p.eligibility or {},
            "terms": p.terms or {},
            "data_status": p.data_status,
        }
        for p in qs
    ]


def create_programme(**fields: Any) -> FundingProgramme:
    """A programme run by the state or an institution (scholarship board, co-operative, bank facility …)."""
    ctx = context.require()
    scope = fields.pop("scope_node_id", None) or ctx.scope_node_id
    authz.require_scope(scope, ctx)
    if FundingProgramme.objects.filter(code=fields["code"]).exists():
        raise ConflictError("FND-PROGRAMME-EXISTS", "Programme code in use", fields["code"])
    with uow.command("ops", "funding:configure", action="create", record_kind="funding_programme") as cmd:
        return cmd.add(
            FundingProgramme(scope_node_id=scope, currency="NGN", data_status="verified", status="published", **fields)
        )


# --------------------------------------------------------------------------- applications (FR-FND-02, FR-FND-07)
def _facts(applicant_kind: str, applicant_id: uuid.UUID, inst: Institution, amount_minor: int) -> dict[str, Any]:
    facts: dict[str, Any] = {"ownership": inst.ownership, "category": inst.category, "amount_minor": amount_minor}
    if applicant_kind == "learner":
        from syntegra.learners.models import Enrolment

        e = (
            Enrolment.objects.filter(learner_id=applicant_id, status="active", is_primary=True)
            .order_by("-created_at")
            .first()
        )
        facts.update(actively_enrolled=e is not None, education_level=e.education_level if e else None)
    elif applicant_kind == "staff":
        from syntegra.hr.models import EmploymentRecord

        r = (
            EmploymentRecord.objects.filter(staff_id=applicant_id)
            .exclude(status="separated")
            .order_by("first_appointment_on")
            .first()
        )
        if r is not None:
            facts.update(
                service_years=round((dt.date.today() - r.first_appointment_on).days / 365.25, 1),
                appointment_status=r.status,
            )
    return facts


def apply(
    programme_id: uuid.UUID,
    *,
    applicant_kind: str,
    applicant_id: uuid.UUID,
    institution_id: uuid.UUID,
    amount_minor: int,
    purpose_detail: str,
    capital_plan_item_id: uuid.UUID | None = None,
    documents: list[dict[str, Any]] | None = None,
    facts: dict[str, Any] | None = None,
) -> FundingApplication:
    """Apply for, or on behalf of, an institution, a member of staff or a learner. Staff may apply for themselves
    (funding:apply_own); applying for others needs funding:apply."""
    ctx = context.require()
    prog = FundingProgramme.objects.filter(pk=programme_id, status="published").first()
    if prog is None:
        raise NotFound("funding programme", programme_id)
    if prog.beneficiary_kind != applicant_kind:
        raise HardValidation(
            "FND-BENEFICIARY",
            "Wrong applicant",
            f"{prog.name} supports {prog.beneficiary_kind}s, not {applicant_kind}s.",
        )
    own = applicant_kind == "staff" and applicant_id == _own_staff_id(ctx)
    authz.require("funding:apply_own" if own and not ctx.has("funding:apply") else "funding:apply", ctx)
    inst = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    if not own:
        authz.require_scope(inst.scope_node_id, ctx)
    if applicant_kind == "institution" and applicant_id != inst.id:
        raise HardValidation("FND-APPLICANT", "Institution mismatch", "An institution applies for itself.")
    if amount_minor <= 0:
        raise HardValidation("FND-AMOUNT", "Amount must be positive", "")
    if prog.max_amount_minor and amount_minor > prog.max_amount_minor:
        raise HardValidation(
            "FND-CEILING", "Above the programme ceiling", f"The ceiling is ₦{prog.max_amount_minor / 100:,.2f}."
        )
    if len(purpose_detail.strip()) < 10:
        raise HardValidation("FND-PURPOSE", "Describe the purpose", "At least 10 characters.")
    results = eligibility.evaluate(
        prog.eligibility, {**_facts(applicant_kind, applicant_id, inst, amount_minor), **(facts or {})}
    )
    ok = eligibility.eligible(results)
    with uow.command("ops", None, action="apply", record_kind="funding_application") as cmd:
        app = cmd.add(
            FundingApplication(
                scope_node_id=inst.scope_node_id,
                application_number=_number("FND"),
                programme_id=prog.id,
                applicant_kind=applicant_kind,
                applicant_id=applicant_id,
                institution_id=inst.id,
                amount_requested_minor=amount_minor,
                currency=prog.currency,
                purpose_detail=purpose_detail.strip(),
                capital_plan_item_id=capital_plan_item_id,
                documents=documents,
                eligibility=[r.as_dict() for r in results],
                eligible=ok,
                submitted_by=ctx.actor_id,
                submitted_at=utcnow(),
                status="submitted",
            ),
            cross_scope_basis="applicant's own application" if own else None,
        )
        cmd.emit(
            "FND.APPLICATION_SUBMITTED",
            aggregate_id=app.id,
            payload={
                "funding_application_id": str(app.id),
                "programme_id": str(prog.id),
                "applicant_kind": applicant_kind,
                "eligible": ok,
            },
            scope_node_id=inst.scope_node_id,
        )
        return app


def recommend(application_id: uuid.UUID, recommendation: str) -> FundingApplication:
    if len(recommendation.strip()) < 10:
        raise HardValidation("FND-RECOMMENDATION", "Recommendation required", "At least 10 characters.")
    ctx = context.require()
    with uow.command("ops", "funding:review", action="recommend", record_kind="funding_application") as cmd:
        app = cmd.lock(FundingApplication, application_id)
        if app.status not in ("submitted", "under_review"):
            raise ConflictError("FND-STATE", "Application is not awaiting review", f"It is {app.status}.")
        if app.submitted_by == ctx.actor_id:
            raise Forbidden("The person who submitted the application cannot review it.", code="FND-FOUR-EYES")
        return cmd.update(app, status="recommended", recommended_by=ctx.actor_id, recommendation=recommendation.strip())


def decide(
    application_id: uuid.UUID, approve: bool, reason: str, *, amount_approved_minor: int | None = None
) -> FundingApplication:
    """A human decision by someone other than the submitter and the recommender (FR-FND-02)."""
    if len(reason.strip()) < 10:
        raise HardValidation("FND-REASON", "Reason required", "At least 10 characters.")
    ctx = context.require()
    with uow.command("ops", "funding:decide", action="decide", record_kind="funding_application") as cmd:
        app = cmd.lock(FundingApplication, application_id)
        if app.status != "recommended":
            raise ConflictError("FND-STATE", "Application has not been recommended", f"It is {app.status}.")
        if ctx.actor_id in (app.recommended_by, app.submitted_by):
            raise Forbidden(
                "The decision needs someone other than the submitter and the reviewer.", code="FND-FOUR-EYES"
            )
        amount = amount_approved_minor if amount_approved_minor is not None else app.amount_requested_minor
        if approve and not 0 < amount <= app.amount_requested_minor:
            raise HardValidation("FND-AMOUNT", "Approved amount must be positive and within the request", "")
        app = cmd.update(
            app,
            status="approved" if approve else "declined",
            decided_by=ctx.actor_id,
            decided_at=utcnow(),
            decision_reason=reason.strip(),
            amount_approved_minor=amount if approve else None,
        )
        cmd.emit(
            "FND.APPLICATION_DECIDED",
            aggregate_id=app.id,
            payload={"funding_application_id": str(app.id), "status": app.status},
            scope_node_id=app.scope_node_id,
        )
        return app


# --------------------------------------------------------------------------- agreements (FR-FND-03, FR-FND-06)
def floor_fraction(scope_node_id: uuid.UUID | None) -> Decimal:
    rule = policy.effective_rule("FND-NET-PAY-FLOOR", scope_node_id) if scope_node_id else None
    return Decimal(str(rule.parameters.get("fraction", "0.3333333333"))) if rule else Decimal(1) / 3


def sign_agreement(
    application_id: uuid.UUID,
    *,
    signed_on: dt.date | None = None,
    first_repayment_on: dt.date | None = None,
    interest_rate: Decimal | float | None = None,
    tenor_months: int | None = None,
    gross_pay_minor: int | None = None,
    other_deductions_minor: int = 0,
) -> FundingAgreement:
    """Turn an approved application into an agreement with its repayment schedule. Staff loans repaid from pay are
    refused when the instalment would take net pay below the policy floor (FR-FND-06)."""
    ctx = context.require()
    signed_on = signed_on or dt.date.today()
    with uow.command("ops", "funding:decide", action="sign", record_kind="funding_agreement") as cmd:
        app = cmd.lock(FundingApplication, application_id)
        if app.status != "approved":
            raise ConflictError("FND-STATE", "Application is not approved", f"It is {app.status}.")
        if FundingAgreement.objects.filter(application_id=app.id).exists():
            raise ConflictError("FND-SIGNED", "Agreement already signed", app.application_number)
        prog = FundingProgramme.objects.get(pk=app.programme_id)
        rate = Decimal(str(interest_rate)) if interest_rate is not None else prog.interest_rate
        tenor = tenor_months or prog.tenor_months
        principal = app.amount_approved_minor or 0
        repayable = prog.instrument in REPAYABLE and prog.repayment_basis not in schedule.NO_SCHEDULE
        first_due = first_repayment_on or schedule.add_months(signed_on, (prog.moratorium_months or 0) + 1)
        plan = (
            schedule.build(
                principal, rate, tenor, prog.repayment_basis, first_due, moratorium_months=prog.moratorium_months
            )
            if repayable
            else []
        )
        if plan and app.applicant_kind == "staff" and prog.repayment_basis == "payroll_deduction":
            if gross_pay_minor is None:
                raise HardValidation(
                    "FND-PAY",
                    "Gross pay needed",
                    "Payroll-deduction loans need gross monthly pay to check affordability.",
                )
            room = schedule.affordable(gross_pay_minor, other_deductions_minor, floor_fraction(app.scope_node_id))
            biggest = max(i.total for i in plan)
            if biggest > room:
                raise HardValidation(
                    "FND-AFFORDABILITY",
                    "Repayment would take net pay below the floor",
                    f"Monthly repayment ₦{biggest / 100:,.2f}; at most ₦{room / 100:,.2f} can be deducted.",
                )
        agreement = cmd.add(
            FundingAgreement(
                scope_node_id=app.scope_node_id,
                agreement_number=_number("AGR"),
                application_id=app.id,
                programme_id=prog.id,
                beneficiary_kind=app.applicant_kind,
                beneficiary_id=app.applicant_id,
                institution_id=app.institution_id,
                instrument=prog.instrument,
                principal_minor=principal,
                interest_rate=rate,
                tenor_months=tenor,
                moratorium_months=prog.moratorium_months,
                repayment_basis=prog.repayment_basis,
                first_repayment_on=plan[0].due_on if plan else None,
                disbursed_minor=0,
                repaid_minor=0,
                outstanding_minor=0,
                arrears_minor=0,
                currency=app.currency,
                signed_on=signed_on,
                signed_by=ctx.actor_id,
                status="signed",
            )
        )
        for i in plan:
            cmd.add(
                RepaymentInstalment(
                    agreement_id=agreement.id,
                    sequence=i.sequence,
                    due_on=i.due_on,
                    principal_minor=i.principal,
                    interest_minor=i.interest,
                    paid_minor=0,
                    currency=agreement.currency,
                    status="due",
                )
            )
        cmd.emit(
            "FND.AGREEMENT_SIGNED",
            aggregate_id=agreement.id,
            payload={
                "funding_agreement_id": str(agreement.id),
                "instrument": agreement.instrument,
                "principal_minor": principal,
            },
            scope_node_id=agreement.scope_node_id,
        )
        return agreement


# --------------------------------------------------------------------------- disbursement (FR-FND-04, FR-FND-07)
def disburse(
    agreement_id: uuid.UUID,
    amount_minor: int,
    *,
    payee_kind: str,
    purpose: str,
    reference: str,
    payee_reference: str | None = None,
    budget_line_id: uuid.UUID | None = None,
    disbursed_on: dt.date | None = None,
) -> FundingDisbursement:
    with uow.command("ops", "funding:disburse", action="disburse", record_kind="funding_disbursement") as cmd:
        a = cmd.lock(FundingAgreement, agreement_id)
        if a.status not in OPEN_AGREEMENT:
            raise ConflictError("FND-STATE", "Agreement is closed", f"It is {a.status}.")
        if amount_minor <= 0 or amount_minor > a.principal_minor - a.disbursed_minor:
            raise HardValidation(
                "FND-DISBURSE",
                "More than remains to disburse",
                f"₦{(a.principal_minor - a.disbursed_minor) / 100:,.2f} remains under this agreement.",
            )
        if FundingDisbursement.objects.filter(agreement_id=a.id, reference=reference).exists():
            raise ConflictError("FND-DUPLICATE", "Disbursement already recorded", reference)
        if budget_line_id:
            if a.beneficiary_kind != "institution":
                raise HardValidation("FND-BUDGET", "Only institutional funding is received into a budget", "")
            from syntegra.finance import budgets

            budgets.receive_funds(cmd, budget_line_id, amount_minor)
        app = FundingApplication.objects.get(pk=a.application_id)
        d = cmd.add(
            FundingDisbursement(
                scope_node_id=a.scope_node_id,
                agreement_id=a.id,
                amount_minor=amount_minor,
                currency=a.currency,
                payee_kind=payee_kind,
                payee_reference=payee_reference,
                purpose=purpose,
                budget_line_id=budget_line_id,
                capital_plan_item_id=app.capital_plan_item_id,
                reference=reference,
                disbursed_on=disbursed_on or dt.date.today(),
                status="paid",
            )
        )
        disbursed = a.disbursed_minor + amount_minor
        repayable = a.instrument in REPAYABLE
        cmd.update(
            a,
            disbursed_minor=disbursed,
            outstanding_minor=_outstanding(a, disbursed) if repayable else 0,
            status=_status(a, disbursed, a.arrears_minor, dt.date.today()),
        )
        cmd.emit(
            "FND.DISBURSED",
            aggregate_id=d.id,
            payload={
                "funding_disbursement_id": str(d.id),
                "funding_agreement_id": str(a.id),
                "amount_minor": amount_minor,
            },
            scope_node_id=a.scope_node_id,
        )
        return d


def _principal_repaid(agreement_id: uuid.UUID) -> int:
    return sum(
        schedule.principal_paid(i.paid_minor, i.interest_minor, i.principal_minor)
        for i in RepaymentInstalment.objects.filter(agreement_id=agreement_id)
    )


def _outstanding(a: FundingAgreement, disbursed: int) -> int:
    """Principal outstanding: disbursed less principal repaid (income-contingent loans: disbursed less repaid)."""
    if a.repayment_basis in schedule.NO_SCHEDULE:
        return max(0, disbursed - a.repaid_minor)
    return max(0, disbursed - _principal_repaid(a.id))


def _status(a: FundingAgreement, disbursed: int, arrears: int, on: dt.date) -> str:
    if a.instrument not in REPAYABLE:
        return "completed" if disbursed >= a.principal_minor else "disbursing"
    if disbursed == 0:
        return "signed"
    if a.repaid_minor and _outstanding(a, disbursed) == 0 and disbursed >= a.principal_minor:
        return "settled"
    if arrears > 0:
        return "in_arrears"
    if a.first_repayment_on and on < a.first_repayment_on:
        return "in_moratorium"
    if a.repayment_basis in schedule.NO_SCHEDULE and not a.repaid_minor:
        return "in_moratorium"  # income-contingent: no repayment until the borrower earns
    return "repaying"


# --------------------------------------------------------------------------- repayments (FR-FND-05)
def record_repayment(
    agreement_id: uuid.UUID,
    amount_minor: int,
    *,
    method: str,
    reference: str,
    received_on: dt.date | None = None,
    source_kind: str | None = None,
    source_id: uuid.UUID | None = None,
) -> FundingRepayment:
    """Record a repayment and allocate it oldest instalment first (idempotent on the reference)."""
    received_on = received_on or dt.date.today()
    if amount_minor <= 0:
        raise HardValidation("FND-AMOUNT", "Amount must be positive", "")
    with uow.command("ops", "funding:collect", action="repay", record_kind="funding_repayment") as cmd:
        a = cmd.lock(FundingAgreement, agreement_id)
        if a.instrument not in REPAYABLE:
            raise HardValidation("FND-NOT-REPAYABLE", "Grants, scholarships and bursaries are not repaid", "")
        if a.status not in ("in_moratorium", "repaying", "in_arrears"):
            raise ConflictError("FND-STATE", "Agreement is not being repaid", f"It is {a.status}.")
        if FundingRepayment.objects.filter(agreement_id=a.id, reference=reference).exists():
            raise ConflictError("FND-DUPLICATE", "Repayment already recorded", reference)
        insts = list(
            RepaymentInstalment.objects.using(cmd.alias)
            .select_for_update()
            .filter(agreement_id=a.id)
            .exclude(status__in=("paid", "waived"))
            .order_by("due_on", "sequence")
        )
        if insts:
            alloc, left = schedule.allocate(
                amount_minor, [(i.sequence, i.principal_minor + i.interest_minor, i.paid_minor) for i in insts]
            )
            if left:
                raise HardValidation(
                    "FND-OVERPAY", "More than is owed", f"₦{left / 100:,.2f} would remain unallocated."
                )
            for i in insts:
                if i.sequence in alloc:
                    paid = i.paid_minor + alloc[i.sequence]
                    total = i.principal_minor + i.interest_minor
                    cmd.update(
                        i,
                        paid_minor=paid,
                        paid_on=received_on,
                        status="paid" if paid == total else ("overdue" if i.due_on < received_on else "partly_paid"),
                    )
        else:  # income-contingent loans: no schedule, the balance falls
            if amount_minor > a.disbursed_minor - a.repaid_minor:
                raise HardValidation("FND-OVERPAY", "More than is owed", "")
            alloc = {}
        r = cmd.add(
            FundingRepayment(
                agreement_id=a.id,
                amount_minor=amount_minor,
                currency=a.currency,
                method=method,
                source_kind=source_kind,
                source_id=source_id,
                reference=reference,
                received_on=received_on,
                allocations={str(k): v for k, v in alloc.items()},
                recorded_by=cmd.ctx.actor_id,
            )
        )
        a.repaid_minor += amount_minor
        arrears = _arrears(a.id, received_on)
        cmd.update(
            a,
            repaid_minor=a.repaid_minor,
            outstanding_minor=_outstanding(a, a.disbursed_minor),
            arrears_minor=arrears,
            status=_status(a, a.disbursed_minor, arrears, received_on),
        )
        cmd.emit(
            "FND.REPAYMENT_RECEIVED",
            aggregate_id=r.id,
            payload={
                "funding_repayment_id": str(r.id),
                "funding_agreement_id": str(a.id),
                "amount_minor": amount_minor,
            },
            scope_node_id=a.scope_node_id,
        )
        return r


def _arrears(agreement_id: uuid.UUID, on: dt.date) -> int:
    return sum(
        i.principal_minor + i.interest_minor - i.paid_minor
        for i in RepaymentInstalment.objects.filter(agreement_id=agreement_id, due_on__lt=on).exclude(
            status__in=("paid", "waived")
        )
    )


def refresh_arrears(on: dt.date | None = None) -> dict[str, int]:
    """Daily job: overdue instalments, arrears and status of every open repayable agreement in the tenant."""
    on = on or dt.date.today()
    n = {"agreements": 0, "newly_in_arrears": 0}
    with uow.command("ops", None, action="refresh_arrears", record_kind="funding_agreement") as cmd:
        for a in FundingAgreement.objects.filter(status__in=OPEN_AGREEMENT, instrument__in=REPAYABLE):
            for i in RepaymentInstalment.objects.filter(
                agreement_id=a.id, due_on__lt=on, status__in=("due", "partly_paid")
            ):
                cmd.update(i, status="overdue")
            arrears = _arrears(a.id, on)
            status = _status(a, a.disbursed_minor, arrears, on)
            if (arrears, status) != (a.arrears_minor, a.status):
                if arrears and not a.arrears_minor:
                    n["newly_in_arrears"] += 1
                    cmd.emit(
                        "FND.ARREARS_RAISED",
                        aggregate_id=a.id,
                        payload={"funding_agreement_id": str(a.id), "arrears_minor": arrears},
                        scope_node_id=a.scope_node_id,
                    )
                cmd.update(a, arrears_minor=arrears, status=status)
                n["agreements"] += 1
        if not n["agreements"]:
            cmd.audited = False
    return n


# --------------------------------------------------------------------------- reads
def _visible_agreement(agreement_id: uuid.UUID) -> FundingAgreement:
    """Agreements in scope (funding:view), or the borrower's own (FR-FND-06)."""
    ctx = context.require()
    a: FundingAgreement | None = FundingAgreement.objects.filter(pk=agreement_id).first()
    if a is None:
        raise NotFound("funding agreement", agreement_id)
    own = a.beneficiary_kind == "staff" and a.beneficiary_id == _own_staff_id(ctx)
    if not own:
        authz.require("funding:view", ctx)
        authz.require_scope(a.scope_node_id, ctx)
    return a


def agreement(agreement_id: uuid.UUID) -> dict[str, Any]:
    a = _visible_agreement(agreement_id)
    prog = FundingProgramme.objects.get(pk=a.programme_id)
    app = FundingApplication.objects.get(pk=a.application_id)
    return {
        **{
            f: getattr(a, f)
            for f in (
                "id",
                "agreement_number",
                "beneficiary_kind",
                "beneficiary_id",
                "instrument",
                "principal_minor",
                "interest_rate",
                "tenor_months",
                "moratorium_months",
                "repayment_basis",
                "first_repayment_on",
                "disbursed_minor",
                "repaid_minor",
                "outstanding_minor",
                "arrears_minor",
                "currency",
                "signed_on",
                "status",
            )
        },
        "beneficiary": _beneficiary_name(a.beneficiary_kind, a.beneficiary_id),
        "programme": {"code": prog.code, "name": prog.name, "provider": prog.provider_name, "terms": prog.terms or {}},
        "application": {
            "number": app.application_number,
            "purpose": app.purpose_detail,
            "eligibility": app.eligibility,
        },
        "schedule": [
            {
                "sequence": i.sequence,
                "due_on": i.due_on,
                "principal": i.principal_minor,
                "interest": i.interest_minor,
                "paid": i.paid_minor,
                "status": i.status,
            }
            for i in RepaymentInstalment.objects.filter(agreement_id=a.id).order_by("sequence")
        ],
        "disbursements": [
            {
                "on": d.disbursed_on,
                "amount": d.amount_minor,
                "payee": d.payee_kind,
                "purpose": d.purpose,
                "reference": d.reference,
            }
            for d in FundingDisbursement.objects.filter(agreement_id=a.id).order_by("disbursed_on")
        ],
        "repayments": [
            {"on": r.received_on, "amount": r.amount_minor, "method": r.method, "reference": r.reference}
            for r in FundingRepayment.objects.filter(agreement_id=a.id).order_by("received_on")
        ],
    }


def _beneficiary_name(kind: str, bid: uuid.UUID) -> str:
    if kind == "institution":
        i = Institution.objects.filter(pk=bid).first()
        return i.name if i else "?"
    if kind == "staff":
        from syntegra.people.models import Staff

        s = Staff.objects.filter(pk=bid).first()
        return f"{s.given_name} {s.family_name}" if s else "?"
    from syntegra.learners.models import Learner

    lr = Learner.objects.filter(pk=bid).first()
    return f"{lr.legal_given_name} {lr.legal_family_name} ({lr.global_learner_id})" if lr else "?"


def overview() -> dict[str, Any]:
    """FND-01: programmes, applications in scope by status, and agreements with balances and arrears."""
    authz.require("funding:view")
    apps = list(FundingApplication.objects.in_scope().order_by("-created_at")[:300])
    progs = {p.id: p for p in FundingProgramme.objects.filter(id__in={x.programme_id for x in apps})}
    agreements = list(FundingAgreement.objects.in_scope().order_by("-signed_on")[:300])
    return {
        "programmes": programmes(),
        "applications": [
            {
                "id": x.id,
                "number": x.application_number,
                "programme": progs[x.programme_id].name,
                "applicant_kind": x.applicant_kind,
                "applicant": _beneficiary_name(x.applicant_kind, x.applicant_id),
                "amount": x.amount_requested_minor,
                "eligible": x.eligible,
                "status": x.status,
            }
            for x in apps
        ],
        "agreements": [
            {
                "id": a.id,
                "number": a.agreement_number,
                "beneficiary": _beneficiary_name(a.beneficiary_kind, a.beneficiary_id),
                "instrument": a.instrument,
                "principal": a.principal_minor,
                "disbursed": a.disbursed_minor,
                "outstanding": a.outstanding_minor,
                "arrears": a.arrears_minor,
                "status": a.status,
            }
            for a in agreements
        ],
        "totals": {
            "approved": sum(x.amount_approved_minor or 0 for x in apps if x.status == "approved"),
            "disbursed": sum(a.disbursed_minor for a in agreements),
            "outstanding": sum(a.outstanding_minor for a in agreements),
            "arrears": sum(a.arrears_minor for a in agreements),
            "in_arrears": sum(1 for a in agreements if a.status == "in_arrears"),
        },
    }


def my_agreements() -> list[dict[str, Any]]:
    """Self-service: the signed-in member of staff's own funding agreements."""
    sid = _own_staff_id(context.require())
    if sid is None:
        return []
    return [
        {
            "id": a.id,
            "number": a.agreement_number,
            "outstanding": a.outstanding_minor,
            "arrears": a.arrears_minor,
            "status": a.status,
        }
        for a in FundingAgreement.objects.filter(beneficiary_kind="staff", beneficiary_id=sid)
    ]
