"""Employee relations (FR-HRM-08): queries, disciplinary and grievance cases with due process.

Outcomes are human decisions (MFS §6: staff discipline is never automated). A dismissal or retirement in the
public interest is recorded here and the separation is then recorded through ``hr.postings.record_separation``.
Allegations about adults that concern children stay in the vault; the case keeps a reference only.
"""

from __future__ import annotations

import datetime as dt
import uuid

from syntegra.core import authz, context, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation
from syntegra.hr.establishment import active_record
from syntegra.hr.models import EmployeeRelationsCase

RESPONSE_DAYS = {"query": 2, "disciplinary": 14, "grievance": 14, "appeal": 21, "petition": 21}
SEVERE = {"suspension", "interdiction", "demotion", "dismissal", "retirement_in_public_interest"}


def open_case(
    staff_id: uuid.UUID, case_kind: str, summary: str, *, vault_allegation_ref: uuid.UUID | None = None
) -> EmployeeRelationsCase:
    ctx = context.require()
    authz.require("hr:relations", ctx)
    rec = active_record(staff_id)
    today = dt.date.today()
    with uow.command("ops", None, action="open", record_kind="employee_relations_case") as cmd:
        n = EmployeeRelationsCase.objects.count() + 1
        return cmd.add(
            EmployeeRelationsCase(
                scope_node_id=rec.scope_node_id,
                case_number=f"ER-{today:%Y}-{n:06d}",
                staff_id=staff_id,
                case_kind=case_kind,
                summary=summary,
                vault_allegation_ref=vault_allegation_ref,
                raised_by=ctx.actor_id,
                raised_on=today,
                response_due_on=today + dt.timedelta(days=RESPONSE_DAYS[case_kind]),
                steps=[{"step": "opened", "on": today.isoformat(), "by": str(ctx.actor_id)}],
                status="open",
            )
        )


def add_step(case_id: uuid.UUID, step: str, note: str) -> EmployeeRelationsCase:
    ctx = context.require()
    authz.require("hr:relations", ctx)
    with uow.command("ops", None, action="step", record_kind="employee_relations_case") as cmd:
        c = cmd.lock(EmployeeRelationsCase, case_id)
        if c.status == "closed":
            raise ConflictError("HR-CASE-CLOSED", "Case closed", "")
        steps = [*c.steps, {"step": step, "note": note, "on": dt.date.today().isoformat(), "by": str(ctx.actor_id)}]
        return cmd.update(c, steps=steps, status="in_progress")


def decide(case_id: uuid.UUID, outcome: str, reason: str) -> EmployeeRelationsCase:
    """Human outcome. Severe sanctions need the staff member's response (or its deadline passed) and a hearing."""
    ctx = context.require()
    authz.require("hr:relations_decide", ctx)
    if ctx.actor_kind != "user":
        raise Forbidden("Employee relations outcomes are decided by people.", code="HUMAN-ONLY")
    with uow.command("ops", None, action="decide", record_kind="employee_relations_case", reason=reason) as cmd:
        c = cmd.lock(EmployeeRelationsCase, case_id)
        names = {s["step"] for s in c.steps}
        responded = "response_received" in names or (c.response_due_on and c.response_due_on < dt.date.today())
        if outcome in SEVERE and not (responded and "hearing" in names):
            raise HardValidation(
                "HR-DUE-PROCESS",
                "Due process incomplete",
                "A severe sanction needs the staff member's response (or the deadline passed) and a hearing.",
            )
        steps = [
            *c.steps,
            {"step": "decided", "outcome": outcome, "on": dt.date.today().isoformat(), "by": str(ctx.actor_id)},
        ]
        return cmd.update(
            c,
            outcome=outcome,
            outcome_decided_by=ctx.actor_id,
            outcome_on=dt.date.today(),
            steps=steps,
            status="closed",
        )
