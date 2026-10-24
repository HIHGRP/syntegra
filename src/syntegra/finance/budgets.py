"""Institutional accounting and budget control (CR-006, FR-ACC-01 – FR-ACC-06).

A budget is approved as lines (cost centre × ledger account × economic code × source of funds). Money is spent
only through a commitment against a line, and a line can never be committed or spent beyond its revised amount
(the database check ``within_budget`` backs the service). Budget moves between lines through a virement decided by
someone other than the requester. Imprest (cash advances) commits its line when issued and is retired with
receipts and refunds by a due date. Budget execution — original, revised, committed, actual, available — is
reported per institution, cost centre and economic code and rolled up through the warehouse.
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any

from django.db.models import Sum

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.ids import short_code
from syntegra.finance.models import (
    Account,
    Budget,
    BudgetCommitment,
    BudgetLine,
    BudgetVirement,
    CostCentre,
    Imprest,
    ImprestRetirement,
)
from syntegra.institutions.models import Institution

CURRENCY = "NGN"


def available(line: BudgetLine) -> int:
    return int(line.revised_minor - line.committed_minor - line.actual_minor)


def _institution(institution_id: uuid.UUID) -> Institution:
    inst: Institution | None = Institution.objects.filter(pk=institution_id).first()
    if inst is None:
        raise NotFound("institution", institution_id)
    authz.require_scope(inst.scope_node_id)
    return inst


def _number(prefix: str) -> str:
    return f"{prefix}-{dt.date.today():%Y}-{short_code().replace('-', '')}"


# --------------------------------------------------------------------------- cost centres (FR-ACC-01)
def create_cost_centre(
    institution_id: uuid.UUID,
    code: str,
    name: str,
    kind: str,
    *,
    holder_staff_id: uuid.UUID | None = None,
    parent_id: uuid.UUID | None = None,
) -> CostCentre:
    inst = _institution(institution_id)
    code = code.strip().upper()
    if CostCentre.objects.filter(scope_node_id=inst.scope_node_id, code=code).exists():
        raise ConflictError("ACC-CC-EXISTS", "Cost centre exists", f"{code} is already a cost centre of {inst.name}.")
    with uow.command("ops", "budget:prepare", action="create", record_kind="cost_centre") as cmd:
        return cmd.add(
            CostCentre(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                code=code,
                name=name,
                cost_centre_kind=kind,
                parent_id=parent_id,
                holder_staff_id=holder_staff_id,
                status="active",
            )
        )


def cost_centres(institution_id: uuid.UUID) -> list[CostCentre]:
    _institution(institution_id)
    return list(CostCentre.objects.in_scope().filter(institution_id=institution_id, status="active").order_by("code"))


# --------------------------------------------------------------------------- budgets (FR-ACC-02)
@dataclass(frozen=True)
class LineInput:
    cost_centre_id: uuid.UUID
    economic_code: str
    amount_minor: int
    funding_source_kind: str = "subvention"
    description: str | None = None
    account_name: str | None = None


def _gl_account(cmd: uow.Command, scope_node_id: uuid.UUID, economic_code: str, name: str | None) -> Account:
    """The general-ledger account for an economic code (created on first use; revenue codes start with 1)."""
    acc = Account.objects.filter(scope_node_id=scope_node_id, code=economic_code).first()
    if acc is None:
        acc = cmd.add(
            Account(
                scope_node_id=scope_node_id,
                account_kind="general_ledger",
                code=economic_code,
                name=name or f"Economic code {economic_code}",
                currency=CURRENCY,
                gl_type="income" if economic_code.startswith("1") else "expense",
                status="active",
            )
        )
    return acc


def prepare_budget(
    institution_id: uuid.UUID, fiscal_year: int, lines: list[LineInput], *, assumptions: dict[str, Any] | None = None
) -> Budget:
    """A new draft version of the institution's budget for the year, with its lines."""
    inst = _institution(institution_id)
    if not lines:
        raise HardValidation("ACC-BUDGET-EMPTY", "A budget needs at least one line", "")
    centres = {c.id: c for c in CostCentre.objects.filter(id__in={ln.cost_centre_id for ln in lines})}
    errors = []
    for i, ln in enumerate(lines):
        c = centres.get(ln.cost_centre_id)
        if c is None or c.institution_id != inst.id:
            errors.append({"field": f"lines[{i}].cost_centre_id", "message": "not a cost centre of this institution"})
        if not (ln.economic_code.isdigit() and 6 <= len(ln.economic_code) <= 16):
            errors.append({"field": f"lines[{i}].economic_code", "message": "economic codes are 6–16 digits"})
        if ln.amount_minor < 0:
            errors.append({"field": f"lines[{i}].amount_minor", "message": "amounts cannot be negative"})
    keys = [(ln.cost_centre_id, ln.economic_code, ln.funding_source_kind) for ln in lines]
    if len(set(keys)) != len(keys):
        errors.append({"field": "lines", "message": "a cost centre, economic code and source of funds appear twice"})
    if errors:
        raise HardValidation("ACC-BUDGET-LINES", "Budget lines are not valid", errors=errors)
    version = (
        Budget.objects.filter(scope_node_id=inst.scope_node_id, fiscal_year=fiscal_year).order_by("-version").first()
    )
    with uow.command("ops", "budget:prepare", action="prepare", record_kind="budget") as cmd:
        budget = cmd.add(
            Budget(
                scope_node_id=inst.scope_node_id,
                fiscal_year=fiscal_year,
                version=(version.version + 1) if version else 1,
                line_items=[
                    {
                        "cost_centre": centres[ln.cost_centre_id].code,
                        "economic_code": ln.economic_code,
                        "source": ln.funding_source_kind,
                        "amount_minor": ln.amount_minor,
                    }
                    for ln in lines
                ],
                assumptions=assumptions,
                currency=CURRENCY,
                status="draft",
            )
        )
        for ln in lines:
            acc = _gl_account(cmd, inst.scope_node_id, ln.economic_code, ln.account_name)
            cmd.add(
                BudgetLine(
                    scope_node_id=inst.scope_node_id,
                    budget_id=budget.id,
                    cost_centre_id=ln.cost_centre_id,
                    account_id=acc.id,
                    economic_code=ln.economic_code,
                    funding_source_kind=ln.funding_source_kind,
                    description=ln.description,
                    original_minor=ln.amount_minor,
                    revised_minor=ln.amount_minor,
                    committed_minor=0,
                    actual_minor=0,
                    currency=CURRENCY,
                )
            )
        return budget


def approve_budget(budget_id: uuid.UUID) -> Budget:
    """Approve a draft; the preparer cannot approve it. The previous approved version of the year is superseded."""
    ctx = context.require()
    with uow.command("ops", "budget:approve", action="approve", record_kind="budget") as cmd:
        b = cmd.lock(Budget, budget_id)
        if b.status not in ("draft", "in_review"):
            raise ConflictError("ACC-BUDGET-STATE", "Budget is not awaiting approval", f"It is {b.status}.")
        if b.created_by == ctx.actor_id:
            raise Forbidden("The person who prepared the budget cannot approve it.", code="ACC-FOUR-EYES")
        for old in Budget.objects.filter(scope_node_id=b.scope_node_id, fiscal_year=b.fiscal_year, status="approved"):
            if BudgetLine.objects.filter(budget_id=old.id).exclude(committed_minor=0, actual_minor=0).exists():
                raise ConflictError(
                    "ACC-BUDGET-IN-USE",
                    "The approved budget is already committed",
                    "Revise it by virement instead of a new version.",
                )
            cmd.update(old, status="superseded")
        return cmd.update(b, status="approved")


def _approved_line(cmd: uow.Command, line_id: uuid.UUID) -> BudgetLine:
    line = cmd.lock(BudgetLine, line_id)
    if not Budget.objects.filter(pk=line.budget_id, status="approved").exists():
        raise ConflictError("ACC-BUDGET-NOT-APPROVED", "The budget is not approved", "Only approved lines can be used.")
    return line


# --------------------------------------------------------------------------- commitment control (FR-ACC-03)
def _commit(
    cmd: uow.Command, line: BudgetLine, amount_minor: int, source_kind: str, source_id: uuid.UUID, description: str
) -> BudgetCommitment:
    if amount_minor <= 0:
        raise HardValidation("ACC-AMOUNT", "Amount must be positive", "")
    if amount_minor > available(line):
        raise HardValidation(
            "ACC-OVER-COMMIT",
            "Not enough budget on the line",
            f"Available ₦{available(line) / 100:,.2f}; requested ₦{amount_minor / 100:,.2f}. Raise a virement first.",
        )
    cmd.update(line, committed_minor=line.committed_minor + amount_minor)
    c = cmd.add(
        BudgetCommitment(
            scope_node_id=line.scope_node_id,
            budget_line_id=line.id,
            source_kind=source_kind,
            source_id=source_id,
            description=description,
            amount_minor=amount_minor,
            spent_minor=0,
            released_minor=0,
            currency=line.currency,
            committed_on=dt.date.today(),
            committed_by=cmd.ctx.actor_id,
            status="open",
        )
    )
    cmd.emit(
        "FIN.FUNDS_COMMITTED",
        aggregate_id=c.id,
        aggregate_kind="budget_commitment",
        payload={
            "budget_commitment_id": str(c.id),
            "budget_line_id": str(line.id),
            "amount_minor": amount_minor,
            "currency": line.currency,
        },
        scope_node_id=line.scope_node_id,
    )
    return c


def commit(
    line_id: uuid.UUID, amount_minor: int, *, source_kind: str, source_id: uuid.UUID, description: str
) -> BudgetCommitment:
    with uow.command("ops", "budget:commit", action="commit", record_kind="budget_commitment") as cmd:
        return _commit(cmd, _approved_line(cmd, line_id), amount_minor, source_kind, source_id, description)


def _settle(cmd: uow.Command, c: BudgetCommitment, spend_minor: int, release_minor: int) -> BudgetCommitment:
    """Move part of a commitment to actual expenditure and/or release part back to the line."""
    remaining = c.amount_minor - c.spent_minor - c.released_minor
    if spend_minor < 0 or release_minor < 0 or spend_minor + release_minor > remaining:
        raise HardValidation(
            "ACC-SPEND", "Amount exceeds the commitment", f"₦{remaining / 100:,.2f} remains on this commitment."
        )
    line = cmd.lock(BudgetLine, c.budget_line_id)
    cmd.update(
        line,
        committed_minor=line.committed_minor - spend_minor - release_minor,
        actual_minor=line.actual_minor + spend_minor,
    )
    spent, released = c.spent_minor + spend_minor, c.released_minor + release_minor
    if spent + released == c.amount_minor:
        status = "spent" if spent else "released"
    else:
        status = "partly_spent" if spent else "open"
    return cmd.update(c, spent_minor=spent, released_minor=released, status=status)


def spend(commitment_id: uuid.UUID, amount_minor: int, *, final: bool = False) -> BudgetCommitment:
    """Record actual expenditure against a commitment; ``final`` releases whatever is left back to the line."""
    with uow.command("ops", "budget:commit", action="spend", record_kind="budget_commitment") as cmd:
        c = cmd.lock(BudgetCommitment, commitment_id)
        if c.status in ("spent", "released", "cancelled"):
            raise ConflictError("ACC-COMMITMENT-CLOSED", "Commitment is closed", f"It is {c.status}.")
        rest = c.amount_minor - c.spent_minor - c.released_minor - amount_minor
        return _settle(cmd, c, amount_minor, max(rest, 0) if final else 0)


def release(commitment_id: uuid.UUID) -> BudgetCommitment:
    with uow.command("ops", "budget:commit", action="release", record_kind="budget_commitment") as cmd:
        c = cmd.lock(BudgetCommitment, commitment_id)
        if c.status in ("spent", "released", "cancelled"):
            raise ConflictError("ACC-COMMITMENT-CLOSED", "Commitment is closed", f"It is {c.status}.")
        return _settle(cmd, c, 0, c.amount_minor - c.spent_minor - c.released_minor)


def receive_funds(cmd: uow.Command, line_id: uuid.UUID, amount_minor: int) -> BudgetLine:
    """Funds received for a line from outside the budget (a grant or intervention disbursement): the revised
    amount rises. Used by the funding service inside its own command."""
    line = cmd.lock(BudgetLine, line_id)
    return cmd.update(line, revised_minor=line.revised_minor + amount_minor)


# --------------------------------------------------------------------------- virements (FR-ACC-04)
def request_virement(from_line_id: uuid.UUID, to_line_id: uuid.UUID, amount_minor: int, reason: str) -> BudgetVirement:
    if from_line_id == to_line_id:
        raise HardValidation("ACC-VIREMENT-SAME", "Choose two different lines", "")
    if len(reason.strip()) < 10:
        raise HardValidation("ACC-REASON", "Reason required", "Explain the virement (10+ characters).")
    with uow.command("ops", "budget:virement", action="request_virement", record_kind="budget_virement") as cmd:
        src, dst = _approved_line(cmd, from_line_id), _approved_line(cmd, to_line_id)
        if src.budget_id != dst.budget_id:
            raise HardValidation("ACC-VIREMENT-BUDGET", "Lines are in different budgets", "")
        if amount_minor <= 0 or amount_minor > available(src):
            raise HardValidation(
                "ACC-VIREMENT-AMOUNT",
                "Not enough available on the source line",
                f"Available ₦{available(src) / 100:,.2f}.",
            )
        return cmd.add(
            BudgetVirement(
                scope_node_id=src.scope_node_id,
                virement_number=_number("VIR"),
                from_line_id=src.id,
                to_line_id=dst.id,
                amount_minor=amount_minor,
                currency=src.currency,
                reason=reason.strip(),
                requested_by=cmd.ctx.actor_id,
                status="submitted",
            )
        )


def decide_virement(virement_id: uuid.UUID, approve: bool) -> BudgetVirement:
    ctx = context.require()
    with uow.command("ops", "budget:approve", action="decide_virement", record_kind="budget_virement") as cmd:
        v = cmd.lock(BudgetVirement, virement_id)
        if v.status != "submitted":
            raise ConflictError("ACC-VIREMENT-STATE", "Virement already decided", f"It is {v.status}.")
        if v.requested_by == ctx.actor_id:
            raise Forbidden("The person who requested the virement cannot approve it.", code="ACC-FOUR-EYES")
        if approve:
            src, dst = _approved_line(cmd, v.from_line_id), _approved_line(cmd, v.to_line_id)
            if v.amount_minor > available(src):
                raise HardValidation(
                    "ACC-VIREMENT-AMOUNT",
                    "No longer enough available on the source line",
                    f"Available ₦{available(src) / 100:,.2f}.",
                )
            cmd.update(src, revised_minor=src.revised_minor - v.amount_minor)
            cmd.update(dst, revised_minor=dst.revised_minor + v.amount_minor)
            cmd.emit(
                "FIN.VIREMENT_APPROVED",
                aggregate_id=v.id,
                payload={
                    "budget_virement_id": str(v.id),
                    "from_line_id": str(src.id),
                    "to_line_id": str(dst.id),
                    "amount_minor": v.amount_minor,
                },
                scope_node_id=v.scope_node_id,
            )
        return cmd.update(v, status="approved" if approve else "rejected", decided_by=ctx.actor_id, decided_at=utcnow())


# --------------------------------------------------------------------------- imprest (FR-ACC-05)
def request_imprest(
    holder_staff_id: uuid.UUID, line_id: uuid.UUID, purpose: str, amount_minor: int, retire_by: dt.date
) -> Imprest:
    line = BudgetLine.objects.in_scope().filter(pk=line_id).first()
    if line is None:
        raise NotFound("budget line", line_id)
    if retire_by < dt.date.today():
        raise HardValidation("ACC-IMPREST-DATE", "Retirement date is in the past", "")
    if amount_minor <= 0:
        raise HardValidation("ACC-AMOUNT", "Amount must be positive", "")
    with uow.command("ops", "imprest:request", action="request", record_kind="imprest") as cmd:
        return cmd.add(
            Imprest(
                scope_node_id=line.scope_node_id,
                imprest_number=_number("IMP"),
                holder_staff_id=holder_staff_id,
                cost_centre_id=line.cost_centre_id,
                budget_line_id=line.id,
                purpose=purpose,
                amount_minor=amount_minor,
                retired_minor=0,
                refunded_minor=0,
                currency=line.currency,
                requested_by=cmd.ctx.actor_id,
                retire_by=retire_by,
                status="requested",
            )
        )


def approve_imprest(imprest_id: uuid.UUID, approve: bool = True) -> Imprest:
    """Second person approves and issues the imprest, committing its budget line; or rejects it."""
    ctx = context.require()
    with uow.command("ops", "imprest:approve", action="approve" if approve else "reject", record_kind="imprest") as cmd:
        imp = cmd.lock(Imprest, imprest_id)
        if imp.status != "requested":
            raise ConflictError("ACC-IMPREST-STATE", "Imprest already decided", f"It is {imp.status}.")
        if imp.requested_by == ctx.actor_id:
            raise Forbidden("The person who requested the imprest cannot approve it.", code="ACC-FOUR-EYES")
        if not approve:
            return cmd.update(imp, status="rejected", approved_by=ctx.actor_id)
        c = _commit(cmd, _approved_line(cmd, imp.budget_line_id), imp.amount_minor, "imprest", imp.id, imp.purpose)
        return cmd.update(imp, status="issued", approved_by=ctx.actor_id, commitment_id=c.id, issued_on=dt.date.today())


def retire_imprest(
    imprest_id: uuid.UUID, receipts: list[dict[str, Any]], amount_minor: int, refund_minor: int = 0
) -> Imprest:
    """Account for an imprest with receipts and any cash refunded; spent amounts become actual expenditure."""
    if not receipts:
        raise HardValidation("ACC-RECEIPTS", "Receipts required", "List the receipts that account for the imprest.")
    if amount_minor < 0 or refund_minor < 0 or amount_minor + refund_minor == 0:
        raise HardValidation("ACC-AMOUNT", "Enter the amount accounted for and any refund", "")
    with uow.command("ops", "imprest:retire", action="retire", record_kind="imprest") as cmd:
        imp = cmd.lock(Imprest, imprest_id)
        if imp.status not in ("issued", "partly_retired", "overdue"):
            raise ConflictError("ACC-IMPREST-STATE", "Imprest is not open", f"It is {imp.status}.")
        if imp.holder_staff_id and _own_staff(cmd.ctx) == imp.holder_staff_id:
            raise Forbidden("The imprest holder cannot verify their own retirement.", code="ACC-FOUR-EYES")
        outstanding = imp.amount_minor - imp.retired_minor - imp.refunded_minor
        if amount_minor + refund_minor > outstanding:
            raise HardValidation(
                "ACC-IMPREST-OVER", "More than the imprest outstanding", f"₦{outstanding / 100:,.2f} is outstanding."
            )
        cmd.add(
            ImprestRetirement(
                imprest_id=imp.id,
                receipts=receipts,
                amount_minor=amount_minor,
                refund_minor=refund_minor,
                currency=imp.currency,
                retired_on=dt.date.today(),
                verified_by=cmd.ctx.actor_id,
            )
        )
        retired, refunded = imp.retired_minor + amount_minor, imp.refunded_minor + refund_minor
        done = retired + refunded == imp.amount_minor
        if imp.commitment_id:
            _settle(cmd, cmd.lock(BudgetCommitment, imp.commitment_id), amount_minor, refund_minor)
        return cmd.update(
            imp, retired_minor=retired, refunded_minor=refunded, status="retired" if done else "partly_retired"
        )


def _own_staff(ctx: context.Context) -> uuid.UUID | None:
    from syntegra.people.models import Staff

    s = Staff.objects.filter(user_id=ctx.actor_id).first() if ctx.actor_id else None
    return s.id if s else None


def flag_overdue_imprest(on: dt.date | None = None) -> int:
    """Daily job: imprest not retired by its due date becomes overdue (and the holder and bursar are told)."""
    on = on or dt.date.today()
    n = 0
    with uow.command("ops", None, action="flag_overdue", record_kind="imprest") as cmd:
        for imp in Imprest.objects.filter(status__in=("issued", "partly_retired"), retire_by__lt=on):
            cmd.update(imp, status="overdue")
            cmd.emit(
                "FIN.IMPREST_OVERDUE",
                aggregate_id=imp.id,
                payload={"imprest_id": str(imp.id), "retire_by": imp.retire_by.isoformat()},
                scope_node_id=imp.scope_node_id,
            )
            n += 1
        if not n:
            cmd.audited = False
    return n


# --------------------------------------------------------------------------- budget execution (FR-ACC-06)
def execution(*, institution_id: uuid.UUID | None = None, fiscal_year: int | None = None) -> dict[str, Any]:
    """FIN-02: approved budget lines in scope with original, revised, committed, actual and available amounts."""
    authz.require("budget:view")
    fiscal_year = fiscal_year or dt.date.today().year
    budgets = Budget.objects.in_scope().filter(fiscal_year=fiscal_year, status="approved")
    if institution_id:
        budgets = budgets.filter(scope_node_id=_institution(institution_id).scope_node_id)
    lines = list(BudgetLine.objects.filter(budget_id__in=list(budgets.values_list("id", flat=True))))
    centres = {c.id: c for c in CostCentre.objects.filter(id__in={ln.cost_centre_id for ln in lines})}
    insts = dict(
        Institution.objects.filter(id__in={c.institution_id for c in centres.values()}).values_list("id", "name")
    )
    rows = []
    for ln in sorted(lines, key=lambda x: (centres[x.cost_centre_id].code, x.economic_code)):
        cc = centres[ln.cost_centre_id]
        rows.append(
            {
                "id": ln.id,
                "institution": insts.get(cc.institution_id),
                "institution_id": cc.institution_id,
                "cost_centre": f"{cc.code} {cc.name}",
                "economic_code": ln.economic_code,
                "source": ln.funding_source_kind,
                "description": ln.description,
                "original": ln.original_minor,
                "revised": ln.revised_minor,
                "committed": ln.committed_minor,
                "actual": ln.actual_minor,
                "available": available(ln),
                "execution": round(ln.actual_minor / ln.revised_minor, 4) if ln.revised_minor else None,
            }
        )
    totals = {k: sum(r[k] for r in rows) for k in ("original", "revised", "committed", "actual", "available")}
    totals["execution"] = round(totals["actual"] / totals["revised"], 4) if totals["revised"] else None
    imprest = Imprest.objects.in_scope().filter(status="overdue").aggregate(n=Sum("amount_minor"))
    return {"fiscal_year": fiscal_year, "lines": rows, "totals": totals, "overdue_imprest_minor": imprest["n"] or 0}


def imprest_register(*, status: str | None = None) -> list[dict[str, Any]]:
    """ACC-01: imprest in scope, newest first, with what is still to be accounted for."""
    authz.require("budget:view")
    from syntegra.people.models import Staff

    qs = Imprest.objects.in_scope().order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    rows = list(qs[:500])
    who = {
        s.id: f"{s.given_name} {s.family_name}" for s in Staff.objects.filter(id__in={r.holder_staff_id for r in rows})
    }
    return [
        {
            "id": r.id,
            "number": r.imprest_number,
            "holder": who.get(r.holder_staff_id, "?"),
            "purpose": r.purpose,
            "amount": r.amount_minor,
            "outstanding": r.amount_minor - r.retired_minor - r.refunded_minor,
            "retire_by": r.retire_by,
            "status": r.status,
        }
        for r in rows
    ]
