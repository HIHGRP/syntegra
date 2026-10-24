"""Salary bank accounts, payroll computation and state-wide payroll integrity (FR-HRM-10/11/12/13).

Payroll integrity is the HR half of CR-001's anti-abuse aim: because every employer's staff, posts, bank
tokens and BVN tokens sit in the one state registry, the scan finds what no single employer can see —
the same account or BVN paid by two employers, a teacher on two public payrolls, pay after exit or past the
statutory retirement date, no attendance for 30 days, and failed headcounts. A flag never stops pay by
itself: a person decides to hold or release (A1), and the pay run excludes held posts.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from django.db.models import Q

from syntegra.attendance.models import StaffAttendance
from syntegra.core import authz, context, crypto, uow
from syntegra.core.errors import ConflictError, Forbidden, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.hr.domain import integrity as rules
from syntegra.hr.domain import payroll as calc
from syntegra.hr.establishment import ACTIVE
from syntegra.hr.models import (
    EmploymentRecord,
    HeadcountExercise,
    HeadcountResult,
    HrIntegrityFlag,
    PayElement,
    SalaryScalePoint,
    Separation,
    StaffBankAccount,
    StaffPayElement,
)
from syntegra.mdm.models import ExternalIdentifier
from syntegra.people.models import PayrollRun, PayrollTaxTable, Payslip, StaffPost

FAILED_HEADCOUNT = ("absent_without_reason", "not_on_nominal_roll", "impersonation_suspected")


# --------------------------------------------------------------------------- bank accounts
def request_bank_account(
    staff_id: uuid.UUID, bank_code: str, account_number: str, account_name: str
) -> StaffBankAccount:
    ctx = context.require()
    authz.require("hr:bank_request", ctx)
    nuban = "".join(account_number.split())
    if not (nuban.isdigit() and len(nuban) == 10):
        raise HardValidation("HR-NUBAN", "Invalid account number", "A NUBAN has 10 digits.")
    with uow.command("registry", None, action="request", record_kind="staff_bank_account") as cmd:
        return cmd.add(
            StaffBankAccount(
                staff_id=staff_id,
                bank_code=bank_code,
                account_number_enc=crypto.encrypt(nuban, purpose="bank:NUBAN", tenant_id=ctx.state_tenant_id),
                account_number_hmac=crypto.lookup_hmac(nuban, scheme="NUBAN", tenant_id=ctx.state_tenant_id),
                account_number_last4=crypto.last4(nuban),
                account_name=account_name,
                is_primary=True,
                verified_via="none",
                requested_by_id=ctx.actor_id,
                status="inactive",
            )
        )


def approve_bank_account(account_id: uuid.UUID, *, verified_via: str) -> StaffBankAccount:
    """Second person confirms after call-back or NIBSS name enquiry; the previous primary account is retired."""
    ctx = context.require()
    authz.require("hr:bank_approve", ctx)
    if verified_via not in ("call_back", "nibss_name_enquiry", "document"):
        raise HardValidation("HR-BANK-VERIFY", "Verification required", "Confirm by call-back or name enquiry.")
    with uow.command("registry", None, action="approve", record_kind="staff_bank_account") as cmd:
        acc = cmd.lock(StaffBankAccount, account_id)
        if acc.requested_by_id == ctx.actor_id:
            raise Forbidden("A bank detail change needs a second person.", code="FOUR-EYES")
        if acc.status != "inactive" or acc.approved_by_id:
            raise ConflictError("HR-BANK-STATE", "Already decided", "")
        for old in StaffBankAccount.unscoped.using(cmd.alias).filter(staff_id=acc.staff_id, status="active"):
            cmd.update(old, status="retired", is_primary=False)
        cmd.update(acc, status="active", approved_by_id=ctx.actor_id, verified_via=verified_via, verified_at=utcnow())
        cmd.emit(
            "HR.BANK_ACCOUNT_CHANGED",
            aggregate_id=acc.id,
            payload={"staff_bank_account_id": acc.id, "staff_id": acc.staff_id},
        )
        return acc


# --------------------------------------------------------------------------- integrity scan
def scan_integrity(*, on: dt.date | None = None, run_label: str | None = None) -> dict[str, int]:
    """State-wide scan across every employer; raises one open flag per kind per staff member."""
    ctx = context.require()
    authz.require("hr:integrity", ctx)
    on = on or dt.date.today()
    reg = list(
        EmploymentRecord.objects.filter(status__in=ACTIVE).values_list(
            "staff_id", "employer_scope_id", "id", "retirement_due_on", "staff_post_id"
        )
    )
    employer_of = {r[0]: r[1] for r in reg}
    findings: list[rules.Finding] = []
    findings += rules.shared_tokens(
        StaffBankAccount.objects.filter(status="active").values_list("staff_id", "account_number_hmac"),
        "shared_bank_account",
    )
    findings += rules.shared_tokens(
        ExternalIdentifier.objects.filter(person_kind="staff", scheme="NG-BVN")
        .exclude(status="revoked")
        .values_list("person_id", "value_hmac"),
        "shared_bvn",
    )
    findings += rules.concurrent_posts((s, e, r) for s, e, r, _, _ in reg)
    findings += rules.past_retirement(((s, d, e) for s, e, _, d, _ in reg), on)
    since = on - dt.timedelta(days=30)
    seen = set(
        StaffAttendance.objects.filter(signed_on__gte=since, signed_on__lte=on).values_list("staff_id", flat=True)
    )
    on_leave = set(_on_leave(since, on))
    teaching = set(
        StaffPost.objects.filter(staff_category="teaching", valid_to__isnull=True).values_list("staff_id", flat=True)
    )
    findings += rules.no_recent_attendance(
        ((s, e) for s, e, *_ in reg if s in teaching and s not in on_leave), seen, on
    )
    failed = HeadcountResult.objects.filter(
        outcome__in=FAILED_HEADCOUNT, exercise_id__in=HeadcountExercise.objects.filter(status="completed").values("id")
    )
    findings += [
        rules.Finding(r.staff_id, "failed_headcount", {"exercise_id": str(r.exercise_id), "outcome": r.outcome})
        for r in failed
    ]
    findings += _paid_after_separation()
    raised: dict[str, int] = {}
    with uow.command("registry", None, action="integrity_scan", record_kind="hr_integrity_flag") as cmd:
        open_keys = set(
            HrIntegrityFlag.unscoped.using(cmd.alias)
            .filter(tenant_id=ctx.state_tenant_id, status__in=("open", "in_progress"))
            .values_list("flag_kind", "staff_id")
        )
        for f in findings:
            if (f.kind, f.staff_id) in open_keys:
                continue
            open_keys.add((f.kind, f.staff_id))
            flag = cmd.add(
                HrIntegrityFlag(
                    staff_id=f.staff_id,
                    employer_scope_id=f.employer_scope_id or employer_of.get(f.staff_id),
                    flag_kind=f.kind,
                    evidence=f.evidence,
                    detected_at=utcnow(),
                    run_label=run_label or f"scan-{on}",
                    payroll_hold=False,
                    status="open",
                )
            )
            cmd.emit(
                "HR.INTEGRITY_FLAG_RAISED",
                aggregate_id=flag.id,
                payload={"hr_integrity_flag_id": flag.id, "flag_kind": f.kind},
            )
            raised[f.kind] = raised.get(f.kind, 0) + 1
        if not raised:
            cmd.audited = False
    return raised


def _on_leave(start: dt.date, end: dt.date) -> list[uuid.UUID]:
    from syntegra.people.models import StaffAbsence

    return list(
        StaffAbsence.objects.filter(
            status__in=("approved", "recorded"), starts_at__date__lte=end, ends_at__date__gte=start
        ).values_list("staff_id", flat=True)
    )


def _paid_after_separation() -> list[rules.Finding]:
    seps = {s.staff_post_id: s for s in Separation.objects.filter(status="approved")}
    if not seps:
        return []
    out = []
    for slip in Payslip.objects.filter(staff_post_id__in=list(seps)):
        run = PayrollRun.objects.filter(pk=slip.payroll_run_id).first()
        sep = seps[slip.staff_post_id]
        if run and run.pay_date > sep.effective_on and run.status not in ("cancelled", "draft"):
            out.append(
                rules.Finding(
                    sep.staff_id,
                    "paid_after_separation",
                    {
                        "payroll_run_id": str(run.id),
                        "pay_date": run.pay_date.isoformat(),
                        "separated_on": sep.effective_on.isoformat(),
                    },
                )
            )
    return out


def decide_hold(flag_id: uuid.UUID, hold: bool, reason: str) -> HrIntegrityFlag:
    """A person holds or releases pay on a flag (human only, A1)."""
    ctx = context.require()
    authz.require("hr:integrity", ctx)
    if ctx.actor_kind != "user":
        raise Forbidden("Pay holds are decided by people.", code="HUMAN-ONLY")
    if len(reason.strip()) < 10:
        raise HardValidation("HR-HOLD-REASON", "Reason required", "Explain the decision (10+ characters).")
    with uow.command(
        "registry", None, action="hold" if hold else "release", record_kind="hr_integrity_flag", reason=reason
    ) as cmd:
        f = cmd.lock(HrIntegrityFlag, flag_id)
        cmd.update(
            f,
            payroll_hold=hold,
            decided_by_id=ctx.actor_id,
            decision_reason=reason,
            status="in_progress" if hold else "resolved",
        )
        cmd.emit(
            "HR.PAYROLL_HOLD_DECIDED", aggregate_id=f.id, payload={"hr_integrity_flag_id": f.id, "payroll_hold": hold}
        )
        return f


# --------------------------------------------------------------------------- headcount
def open_headcount(
    institution_id: uuid.UUID, label: str, method: str, starts_on: dt.date, ends_on: dt.date
) -> HeadcountExercise:
    from syntegra.institutions.models import Institution

    ctx = context.require()
    authz.require("hr:integrity", ctx)
    inst = Institution.objects.get(pk=institution_id)
    with uow.command("registry", None, action="open", record_kind="headcount_exercise") as cmd:
        return cmd.add(
            HeadcountExercise(
                scope_node_id=inst.scope_node_id,
                institution_id=inst.id,
                label=label,
                method=method,
                starts_on=starts_on,
                ends_on=ends_on,
                conducted_by_id=ctx.actor_id,
                status="active",
            )
        )


def record_headcount(
    exercise_id: uuid.UUID, staff_id: uuid.UUID, outcome: str, evidence: dict[str, Any] | None = None
) -> HeadcountResult:
    ctx = context.require()
    authz.require("hr:integrity", ctx)
    with uow.command("registry", None, action="verify", record_kind="headcount_exercise") as cmd:
        ex = cmd.lock(HeadcountExercise, exercise_id)
        post = StaffPost.objects.filter(
            staff_id=staff_id, institution_id=ex.institution_id, valid_to__isnull=True
        ).first()
        cmd.record_id = ex.id
        return cmd.add(
            HeadcountResult(
                exercise_id=ex.id,
                staff_id=staff_id,
                staff_post_id=post.id if post else None,
                outcome=outcome,
                verified_at=utcnow(),
                evidence=evidence or {},
                verifier_id=ctx.actor_id,
            )
        )


def close_headcount(exercise_id: uuid.UUID) -> HeadcountExercise:
    with uow.command("registry", "hr:integrity", action="close", record_kind="headcount_exercise") as cmd:
        ex = cmd.lock(HeadcountExercise, exercise_id)
        cmd.update(ex, status="completed")
        cmd.emit(
            "HR.HEADCOUNT_COMPLETED",
            aggregate_id=ex.id,
            payload={"headcount_exercise_id": ex.id, "institution_id": ex.institution_id},
        )
        return ex


# --------------------------------------------------------------------------- payroll
def _tables() -> tuple[dict[str, Any], dict[str, int]]:
    tables: dict[str, Any] = {}
    versions: dict[str, int] = {}
    for kind in ("paye", "pension", "nhf"):
        t = (
            PayrollTaxTable.objects.filter(table_kind=kind, status="published", effective_from__lte=dt.date.today())
            .order_by("-version")
            .first()
        )
        if t is not None:
            tables[kind], versions[kind] = t.bands, t.version
    return tables, versions


def _allowances(point: SalaryScalePoint, basic_monthly: int) -> dict[str, int]:
    out = {}
    for code, spec in (point.allowances or {}).items():
        if isinstance(spec, dict) and "pct_of_basic" in spec:
            out[code] = calc.pct(basic_monthly, round(float(spec["pct_of_basic"]) * 100))
        elif isinstance(spec, dict) and "monthly_minor" in spec:
            out[code] = int(spec["monthly_minor"])
        elif isinstance(spec, int):
            out[code] = spec
    return out


def compute_payroll(employer_scope_id: uuid.UUID, period_label: str, pay_date: dt.date) -> PayrollRun:
    """Compute a pay run for every active post of an employer. Posts on hold are excluded; other open flags
    are carried onto the payslip as exceptions for review before approval."""
    ctx = context.require()
    authz.require("hr:payroll_prepare", ctx)
    if (
        PayrollRun.objects.filter(employer_scope_id=employer_scope_id, period_label=period_label)
        .exclude(status="cancelled")
        .exists()
    ):
        raise ConflictError("PAY-RUN-EXISTS", "Pay run already exists", period_label)
    records = list(EmploymentRecord.objects.filter(employer_scope_id=employer_scope_id, status__in=ACTIVE))
    flags: dict[uuid.UUID, list[HrIntegrityFlag]] = {}
    for f in HrIntegrityFlag.objects.filter(
        staff_id__in=[r.staff_id for r in records], status__in=("open", "in_progress")
    ):
        flags.setdefault(f.staff_id, []).append(f)
    tables, versions = _tables()
    kinds = {e.code: e.element_kind for e in PayElement.objects.filter(status="published").order_by("version")}
    slips: list[tuple[EmploymentRecord, calc.Payslip, list[dict[str, Any]]]] = []
    held: list[str] = []
    for r in records:
        fl = flags.get(r.staff_id, [])
        if any(f.payroll_hold for f in fl):
            held.append(str(r.staff_post_id))
            continue
        point = SalaryScalePoint.objects.get(structure_id=r.salary_structure_id, grade_level=r.grade_level, step=r.step)
        basic_monthly = (point.annual_basic_minor + 6) // 12
        extras = [
            calc.Element(e.element_code, kinds.get(e.element_code, "allowance"), abs(int(e.amount_minor or 0)))
            for e in StaffPayElement.objects.filter(staff_post_id=r.staff_post_id, valid_from__lte=pay_date).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=pay_date)
            )
        ]
        slip = calc.compute_month(
            point.annual_basic_minor,
            _allowances(point, basic_monthly),
            other_elements=tuple(extras),
            paye_bands=tables.get("paye"),
            pension=tables.get("pension"),
            nhf=tables.get("nhf"),
            versions=versions,
        )
        slips.append((r, slip, [{"flag": f.flag_kind, "flag_id": str(f.id)} for f in fl]))
    from syntegra.governance.models import ScopeNode

    employer_node = ScopeNode.objects.filter(pk=employer_scope_id).first()
    with uow.command("ops", None, action="compute", record_kind="payroll_run") as cmd:
        run = cmd.add(
            PayrollRun(
                scope_node_id=employer_node.id if employer_node else ctx.scope_node_id,
                employer_scope_id=employer_scope_id,
                period_label=period_label,
                pay_date=pay_date,
                gross_total_minor=sum(s.gross for _, s, _ in slips),
                net_total_minor=sum(s.net for _, s, _ in slips),
                currency="NGN",
                prepared_by=ctx.actor_id,
                status="exceptions_review" if any(e for *_, e in slips) or held else "calculated",
            )
        )
        for r, s, exc in slips:
            acc = StaffBankAccount.objects.filter(staff_id=r.staff_id, status="active", is_primary=True).first()
            enc = last4 = None
            if acc is not None:
                nuban = crypto.decrypt(
                    bytes(acc.account_number_enc), purpose="bank:NUBAN", tenant_id=ctx.state_tenant_id
                )
                enc = crypto.encrypt(nuban, purpose="payslip:bank", tenant_id=ctx.tenant_id)
                last4 = acc.account_number_last4
            else:
                exc = [*exc, {"exception": "no_verified_bank_account"}]
            cmd.add(
                Payslip(
                    payroll_run_id=run.id,
                    staff_post_id=r.staff_post_id,
                    gross_minor=s.gross,
                    deductions_minor=s.deductions,
                    net_minor=s.net,
                    currency="NGN",
                    line_items=s.lines,
                    bank_account_enc=enc,
                    bank_account_last4=last4,
                    exception_flags=exc or None,
                )
            )
        cmd.note("held_posts", None, held)
        cmd.record_id = run.id
        return run


def approve_payroll(run_id: uuid.UUID) -> PayrollRun:
    """Two people approve, neither of them the preparer (CHECK two_person + service rule)."""
    ctx = context.require()
    authz.require("hr:payroll_approve", ctx)
    with uow.command("ops", None, action="approve", record_kind="payroll_run") as cmd:
        run = cmd.lock(PayrollRun, run_id)
        if ctx.actor_id in (run.prepared_by, run.approved_by):
            raise Forbidden("Preparer and approvers must be different people.", code="FOUR-EYES")
        if run.status not in ("calculated", "exceptions_review"):
            raise ConflictError("PAY-RUN-STATE", "Pay run cannot be approved", f"It is {run.status}.")
        if run.approved_by is None:
            return cmd.update(run, approved_by=ctx.actor_id)
        cmd.update(run, second_approver_id=ctx.actor_id, status="approved")
        cmd.emit("PAY.RUN_APPROVED", aggregate_id=run.id, payload=_run_payload(run))
        return run


def _run_payload(run: PayrollRun) -> dict[str, Any]:
    from syntegra.core import catalog

    spec = catalog.event("PAY.RUN_APPROVED").get("payload") or {}
    full = {"payroll_run_id": run.id, "employer_scope_id": run.employer_scope_id, "period_label": run.period_label}
    return {k: v for k, v in full.items() if k in spec}


def payslip_for(run_id: uuid.UUID, staff_post_id: uuid.UUID) -> Payslip:
    s: Payslip | None = Payslip.objects.filter(payroll_run_id=run_id, staff_post_id=staff_post_id).first()
    if s is None:
        raise NotFound("payslip", staff_post_id)
    return s
