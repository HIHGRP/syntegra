"""Web forms for every write action that the API offers (MFS Part B, data-entry pattern).

A form is declared once: its fields, the permission that shows it, the API serializer that validates it and the
service call that performs it. The pages therefore validate exactly as the API does and call the same services —
there is no form-only logic. ``/forms`` lists the forms the signed-in role may use; ``/forms/<key>`` renders one.

Field kinds: ``text``, ``textarea``, ``date``, ``number``, ``money`` (naira, stored in kobo), ``select``,
``multi`` (several options), ``checkbox``, ``glid`` (a Global Learner ID, resolved to the learner), ``list``
(one value per line), ``file`` (UTF-8 text upload) and ``hidden``.
"""

from __future__ import annotations

import datetime as dt
import re
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from rest_framework import serializers

from syntegra.core import context
from syntegra.core.errors import DomainError, HardValidation
from syntegra.web import choices as ch

Data = dict[str, Any]


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    kind: str = "text"
    required: bool = True
    hint: str = ""
    choices: ch.Provider | None = None
    default: str = ""


@dataclass(frozen=True)
class Form:
    key: str
    title: str
    module: str
    permission: str | tuple[str, ...]  # any of
    intro: str
    fields: tuple[Field, ...]
    handler: Callable[[Data], Any]
    done: Callable[[Any, Data], tuple[str, str | None]]
    serializer: Callable[..., serializers.Serializer] | None = None  # type: ignore[type-arg]
    prepare: Callable[[Data], Data] | None = None
    submit: str = "Save"
    caution: str = ""  # shown beside the button for consequential actions

    def permitted(self, ctx: context.Context | None) -> bool:
        if ctx is None:
            return False
        perms = (self.permission,) if isinstance(self.permission, str) else self.permission
        return any(ctx.has(p) for p in perms)

    def allowed(self, ctx: context.Context | None) -> bool:
        """The role holds the permission and its access level covers the form's (CR-007, FR-ADM-201)."""
        from syntegra.core import access

        return self.permitted(ctx) and ctx is not None and access.covers(ctx.clearance, level(self))


class Invalid(Exception):
    """Field errors found while preparing a form's data."""

    def __init__(self, errors: Mapping[str, str]) -> None:
        super().__init__(dict(errors))
        self.errors = dict(errors)


@dataclass
class Outcome:
    errors: dict[str, str] = field(default_factory=dict)
    message: str | None = None
    link: str | None = None
    result: Any = None


# --------------------------------------------------------------------------- processing
def _money(raw: str) -> int:
    try:
        value = Decimal(raw.replace(",", "").replace("₦", "").replace("NGN", "").strip())
    except InvalidOperation as exc:
        raise ValueError("enter an amount in naira, e.g. 12500 or 12,500.50") from exc
    if value < 0 or value != value.quantize(Decimal("0.01")):
        raise ValueError("enter an amount in naira with at most two decimal places")
    return int(value * 100)


def _learner_id(glid: str) -> str:
    from syntegra.learners.models import Learner

    lr = Learner.objects.filter(global_learner_id=glid.strip().upper()).first()
    if lr is None:
        raise ValueError("no learner with that Global Learner ID in this registry")
    return str(lr.id)


def _flatten(detail: Any) -> str:
    if isinstance(detail, dict):
        return "; ".join(f"{k}: {_flatten(v)}" for k, v in detail.items())
    if isinstance(detail, list | tuple):
        return " ".join(_flatten(d) for d in detail if d)
    return str(detail)


def options(form: Form, params: Mapping[str, Any]) -> dict[str, ch.Options]:
    return {f.name: f.choices(params) for f in form.fields if f.choices is not None}


def collect(form: Form, post: Any, files: Any, opts: Mapping[str, ch.Options]) -> tuple[Data, dict[str, str]]:
    """Raw POST → typed values. Blank optional fields are left out so the serializer applies its defaults."""
    data: Data = {}
    errors: dict[str, str] = {}
    for f in form.fields:
        allowed = {v for v, _ in opts.get(f.name, [])}
        if f.kind == "checkbox":
            data[f.name] = bool(post.get(f.name))
            continue
        if f.kind == "multi":
            picked = [v for v in post.getlist(f.name) if v]
            if not picked and f.required:
                errors[f.name] = "Choose at least one."
            elif f.choices is not None and not set(picked) <= allowed:
                errors[f.name] = "Choose from the options shown."
            elif picked:
                data[f.name] = picked
            continue
        if f.kind == "file":
            up = files.get(f.name)
            if up is None:
                if f.required:
                    errors[f.name] = "Choose a file."
                continue
            if up.size > 5 * 1024 * 1024:
                errors[f.name] = "The file is larger than 5 MB."
                continue
            data[f.name] = up.read().decode("utf-8-sig", errors="replace")
            continue
        raw = str(post.get(f.name) or "").strip()
        if not raw:
            if f.required:
                errors[f.name] = "Required."
            continue
        try:
            if f.kind == "money":
                data[f.name] = _money(raw)
            elif f.kind == "glid":
                data[f.name] = _learner_id(raw)
            elif f.kind == "list":
                data[f.name] = [x.strip() for x in re.split(r"[\n,;]+", raw) if x.strip()]
            elif f.kind in ("select", "hidden") and f.choices is not None and raw not in allowed:
                raise ValueError("choose from the options shown")
            else:
                data[f.name] = raw
        except ValueError as exc:
            errors[f.name] = str(exc)[:1].upper() + str(exc)[1:] + "."
    return data, errors


def submit(form: Form, post: Any, files: Any, opts: Mapping[str, ch.Options]) -> Outcome:
    names = {f.name for f in form.fields}
    data, errors = collect(form, post, files, opts)
    if errors:
        return Outcome(errors=errors)
    try:
        if form.prepare is not None:
            data = form.prepare(data)
    except Invalid as exc:
        return Outcome(errors=exc.errors)
    if form.serializer is not None:
        s = form.serializer(data=data)
        if not s.is_valid():
            out: dict[str, str] = {}
            for k, v in s.errors.items():
                key = k if k in names else "form"
                out[key] = (
                    out.get(key, "") + " " + (k + ": " if key == "form" and k in data else "") + _flatten(v)
                ).strip()
            return Outcome(errors=out)
        data = {**data, **s.validated_data}
    try:
        result = form.handler(data)
    except HardValidation as exc:
        errs: dict[str, str] = {}
        summary = f"{exc.title}: {exc.detail}" if exc.detail else exc.title
        for e in exc.errors or [{"field": None, "message": summary}]:
            f_ = str(e.get("field") or "form")
            errs.setdefault(f_ if f_ in names else "form", str(e.get("message")))
        if "form" not in errs and exc.title:
            errs["form"] = exc.title
        return Outcome(errors=errs)
    except DomainError as exc:
        return Outcome(errors={"form": f"{exc.title}: {exc.detail}" if exc.detail else exc.title})
    message, link = form.done(result, data)
    return Outcome(message=message, link=link, result=result)


# --------------------------------------------------------------------------- shared serializers and helpers
class ReasonSerializer(serializers.Serializer):  # type: ignore[type-arg]
    reason = serializers.CharField(min_length=10)


def _u(value: Any) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


def _target(label: str, provider: ch.Provider, hint: str = "") -> Field:
    return Field("target", label, "select", choices=provider, hint=hint)


YES_NO = ch.fixed(["true", "false"], {"true": "Approve", "false": "Reject"})
REASON = Field("reason", "Reason", "textarea", hint="At least 10 characters; kept in the audit trail.")


def _ok(message: str, link: str | None = None) -> Callable[[Any, Data], tuple[str, str | None]]:
    return lambda _r, _d: (message, link)


# --------------------------------------------------------------------------- institutions and learners
def _institution_prepare(d: Data) -> Data:
    d["address"] = {k: d.pop(k) for k in ("town", "street") if d.get(k)}
    lat, lng = d.pop("latitude", None), d.pop("longitude", None)
    if (lat is None) != (lng is None):
        raise Invalid({"longitude": "Give both latitude and longitude, or neither."})
    if lat is not None:
        d["location"] = [lat, lng]
    return d


def _register_institution(d: Data) -> Any:
    from syntegra.institutions import services

    keys = services.RegisterInstitution.__dataclass_fields__
    data = {k: v for k, v in d.items() if k in keys}
    if data.get("location"):
        data["location"] = tuple(data["location"])
    if data["ownership"] not in services.PUBLIC_OWNERSHIP:  # held by the state registry until the provider onboards
        data.setdefault("operating_tenant_id", context.require().state_tenant_id)
    return services.register(services.RegisterInstitution(**data), override_reason=d.get("override_reason") or None)


def _transfer(d: Data) -> Any:
    from syntegra.clearance.services import DecisionInput
    from syntegra.learners import services as lrn

    decision = None
    if d.get("decision"):
        decision = DecisionInput(
            decision=d["decision"], reason=d.get("decision_reason", ""), payment_plan_ref=d.get("payment_plan_ref")
        )
    return lrn.transfer(
        _u(d["learner"]),
        d["to_institution_id"],
        effective_on=d.get("effective_on"),
        education_level=d.get("education_level"),
        clearance=decision,
    )


def _create_class(d: Data) -> Any:
    from syntegra.academic import services

    return services.create_class(
        d["institution_id"], d["period_id"], d["name"], d["education_level"], capacity=d.get("capacity")
    )


def _add_member(d: Data) -> Any:
    from syntegra.academic import services

    return services.add_member(_u(d["target"]), d["learner_id"])


# --------------------------------------------------------------------------- certificates
def _certificate_prepare(d: Data) -> Data:
    from syntegra.certificates.models import Certificate

    c = Certificate.objects.in_scope().filter(certificate_number=d["certificate_number"].strip().upper()).first()
    if c is None:
        raise Invalid({"certificate_number": "No certificate with that number that you may act on."})
    d["certificate_id"] = str(c.id)
    return d


def _request_reissue(d: Data) -> Any:
    from syntegra.certificates import services

    return services.request_reissue(
        _u(d["certificate_id"]), d["reason"], applicant_name=d["applicant_name"], applicant_phone=d["applicant_phone"]
    )


def _decide_reissue(d: Data) -> Any:
    from syntegra.certificates import services

    return services.decide_reissue(_u(d["target"]), d["approve"], note=d.get("note") or None)


# --------------------------------------------------------------------------- fee clearance
def _obligation_prepare(d: Data) -> Data:
    d["evidence"] = [{"invoice": i} for i in d.pop("invoices", [])] + [{"document_id": d.pop("document_id")}]
    d["source"] = "manual_with_evidence"
    return d


def _publish(d: Data) -> Any:
    from syntegra.clearance import services
    from syntegra.clearance.api import ObligationSerializer

    keys = ObligationSerializer().fields
    return services.publish(**{k: v for k, v in d.items() if k in keys})


def _published(r: Any, d: Data) -> tuple[str, str | None]:
    if r is None:
        return "No open obligation to settle for that learner, creditor and kind.", None
    if r.status == "settled":
        return "The obligation is settled and no longer shows on clearance checks.", None
    return f"Published: {ch.naira(r.amount_outstanding_minor)} outstanding. It now shows on clearance checks.", None


def _raise_dispute(d: Data) -> Any:
    from syntegra.clearance import services

    return services.raise_dispute(_u(d["target"]), party=d["party"], grounds=d["grounds"], statement=d["statement"])


def _resolve_dispute(d: Data) -> Any:
    from syntegra.clearance import services

    return services.resolve_dispute(
        _u(d["target"]), d["resolution"], reason=d["reason"], resolved_amount_minor=d.get("resolved_amount_minor")
    )


# --------------------------------------------------------------------------- coverage and financing
def _evaluate(d: Data) -> Any:
    from syntegra.curriculum import services

    return services.evaluate_institution(_u(d["institution_id"]))


def _accept_gap(d: Data) -> Any:
    from syntegra.curriculum import services

    return services.accept(_u(d["target"]), d["reason"])


def _take_census(d: Data) -> Any:
    from syntegra.financing import services

    return services.take_census(_u(d["institution_id"]), d["billing_period_id"])


def _freeze(d: Data) -> Any:
    from syntegra.financing import services

    return services.confirm_and_freeze(_u(d["target"]))


def _demand(d: Data) -> Any:
    from syntegra.financing import services

    return services.issue_demand(_u(d["target"]))


# --------------------------------------------------------------------------- HR
def _hr(name: str) -> Any:
    import importlib

    return importlib.import_module(f"syntegra.hr.{name}")


def _create_position(d: Data) -> Any:
    est = _hr("establishment")
    keys = est.NewPosition.__dataclass_fields__
    return est.create_position(est.NewPosition(**{k: v for k, v in d.items() if k in keys}))


def _appoint(d: Data) -> Any:
    est = _hr("establishment")
    keys = est.Appointment.__dataclass_fields__
    return est.appoint(est.Appointment(**{k: v for k, v in d.items() if k in keys}))


def _request_posting(d: Data) -> Any:
    return _hr("postings").request_posting(
        staff_id=d["staff_id"],
        to_position_id=d["to_position_id"],
        posting_kind=d["posting_kind"],
        reason=d["reason"],
        effective_on=d["effective_on"],
    )


def _decide_posting(d: Data) -> Any:
    postings = _hr("postings")
    if d["action"] == "effective":
        return postings.make_effective(_u(d["target"]))
    return postings.approve_posting(_u(d["target"]), approve=d["action"] == "approve", note=d.get("note") or None)


def _separate(d: Data) -> Any:
    return _hr("postings").record_separation(d["staff_post_id"], d["separation_kind"], effective_on=d["effective_on"])


def _request_leave(d: Data) -> Any:
    return _hr("leave").request_leave(
        d["staff_id"], d["leave_type"], d["starts_on"], d["ends_on"], note=d.get("note") or None
    )


def _decide_leave(d: Data) -> Any:
    return _hr("leave").decide_leave(_u(d["target"]), d["approve"], relief_staff_id=d.get("relief_staff_id"))


def _open_promotion(d: Data) -> Any:
    return _hr("establishment").open_promotion(d["staff_id"], d["exercise_label"])


def _decide_promotion(d: Data) -> Any:
    return _hr("establishment").decide_promotion(
        _u(d["target"]), d["decision"], reason=d.get("reason") or None, effective_on=d.get("effective_on")
    )


def _open_case(d: Data) -> Any:
    return _hr("relations").open_case(d["staff_id"], d["case_kind"], d["summary"])


def _scan(_d: Data) -> Any:
    return _hr("payroll").scan_integrity()


def _hold(d: Data) -> Any:
    return _hr("payroll").decide_hold(_u(d["target"]), d["hold"], d["reason"])


def _payroll_run(d: Data) -> Any:
    return _hr("payroll").compute_payroll(d["employer_scope_id"], d["period_label"], d["pay_date"])


def _approve_payroll(d: Data) -> Any:
    return _hr("payroll").approve_payroll(_u(d["target"]))


def _establishment_link(r: Any, _d: Data) -> str | None:
    inst = getattr(r, "institution_id", None) or getattr(r, "to_institution_id", None)
    return f"/hr/establishment?institution_id={inst}" if inst else "/hr/establishment"


# --------------------------------------------------------------------------- regulation, federal, security training
def _set_link(d: Data) -> Any:
    from syntegra.regulation import services

    return services.set_link(
        _u(d["institution_id"]),
        d["body_code"],
        d["relationship"],
        covers=d["covers"],
        levels=d.get("levels"),
        reason=d["reason"],
    )


def _end_link(d: Data) -> Any:
    from syntegra.regulation import services

    return services.end_link(_u(d["target"]), reason=d["reason"])


def _import(d: Data) -> Any:
    from syntegra.federal_institutions import services

    return services.import_csv(d["csv"], dry_run=bool(d.get("dry_run")))


def _imported(r: Any, _d: Data) -> tuple[str, str | None]:
    if r["errors"]:
        lines = "; ".join(
            f"row {e['row']} ({e.get('code') or '?'}): {_flatten(e['problems'])}" for e in r["errors"][:20]
        )
        return f"Nothing imported — {len(r['errors'])} row(s) need correcting: {lines}", None
    if not r["applied"]:
        return f"All {r['valid']} rows are valid. Untick “check only” to import them.", None
    return (
        f"Imported {r['rows']} rows: {r['added']} new institutions, {r['updated']} updated, "
        f"{r['regulatory_links']} regulatory links.",
        "/federal-institutions",
    )


def _create_intake(d: Data) -> Any:
    from syntegra.security_training import services

    return services.create_intake(
        _u(d["target"]),
        intake_code=d["intake_code"],
        name=d["name"],
        starts_on=d["starts_on"],
        ends_on=d.get("ends_on"),
        capacity=d.get("capacity"),
    )


def _add_trainee(d: Data) -> Any:
    from syntegra.security_training import services

    return services.add_trainee(_u(d["target"]), d["learner_id"], rank_code=d.get("rank_code") or None)


def _record_outcome(d: Data) -> Any:
    from syntegra.security_training import services

    return services.record_outcome(
        _u(d["target"]), d["outcome"], result=d.get("result"), reason=d.get("reason"), on=d.get("on")
    )


# --------------------------------------------------------------------------- budgets and imprest (CR-006)
def _budgets() -> Any:
    from syntegra.finance import budgets

    return budgets


def _budget_prepare(d: Data) -> Data:
    """One line per row: ``cost centre code | economic code | amount in naira | source | description``."""
    from syntegra.finance.models import CostCentre

    iid = ch.as_uuid(d.get("institution_id"))
    centres = {c.code: c.id for c in CostCentre.objects.in_scope().filter(institution_id=iid, status="active")}
    lines, bad = [], []
    for n, row in enumerate(str(d.pop("lines_text", "")).splitlines(), start=1):
        if not row.strip():
            continue
        parts = [p.strip() for p in row.split("|")]
        if len(parts) < 3 or parts[0].upper() not in centres:
            bad.append(
                f"row {n}: start with one of your cost-centre codes ({', '.join(sorted(centres)) or 'none yet'})"
            )
            continue
        try:
            amount = _money(parts[2])
        except ValueError as exc:
            bad.append(f"row {n}: {exc}")
            continue
        line: Data = {
            "cost_centre_id": str(centres[parts[0].upper()]),
            "economic_code": parts[1],
            "amount_minor": amount,
        }
        if len(parts) > 3 and parts[3]:
            line["funding_source_kind"] = parts[3].lower().replace(" ", "_")
        if len(parts) > 4 and parts[4]:
            line["description"] = parts[4]
        lines.append(line)
    if bad or not lines:
        raise Invalid({"lines_text": "; ".join(bad) or "Enter at least one line."})
    d["lines"] = lines
    return d


def _budget_lines_out(d: Data) -> Any:
    b = _budgets()
    lines = [b.LineInput(**{k: x for k, x in ln.items() if x not in (None, "")}) for ln in d["lines"]]
    return b.prepare_budget(_u(d["institution_id"]), int(d["fiscal_year"]), lines)


def _imprest_retire_prepare(d: Data) -> Data:
    """One receipt per row: ``reference | amount in naira | payee``."""
    receipts, bad = [], []
    for n, row in enumerate(str(d.pop("receipts_text", "")).splitlines(), start=1):
        if not row.strip():
            continue
        parts = [p.strip() for p in row.split("|")]
        try:
            receipts.append({"reference": parts[0], "amount_minor": _money(parts[1] if len(parts) > 1 else ""),
                             **({"payee": parts[2]} if len(parts) > 2 and parts[2] else {})})  # fmt: skip
        except ValueError as exc:
            bad.append(f"row {n}: {exc}")
    if bad or not receipts:
        raise Invalid({"receipts_text": "; ".join(bad) or "List at least one receipt."})
    d["receipts"] = receipts
    return d


# --------------------------------------------------------------------------- funding and loans (CR-006)
def _funding() -> Any:
    from syntegra.funding import services

    return services


def _funding_apply_prepare(d: Data) -> Data:
    kind = d.get("applicant_kind")
    if kind == "institution":
        d["applicant_id"] = d.get("institution_id")
    elif kind == "staff":
        if not d.get("staff_id"):
            raise Invalid({"staff_id": "Choose the member of staff."})
        d["applicant_id"] = d["staff_id"]
    elif kind == "learner":
        if not d.get("learner"):
            raise Invalid({"learner": "Enter the learner's Global Learner ID."})
        d["applicant_id"] = d["learner"]
    return d


def _funding_apply(d: Data) -> Any:
    return _funding().apply(
        _u(d["programme_id"]),
        applicant_kind=d["applicant_kind"],
        applicant_id=_u(d["applicant_id"]),
        institution_id=_u(d["institution_id"]),
        amount_minor=d["amount_minor"],
        purpose_detail=d["purpose_detail"],
    )


def _clean(d: Data, *names: str) -> Data:
    return {k: d[k] for k in names if d.get(k) not in (None, "")}


# --------------------------------------------------------------------------- facilities (CR-006)
def _estate() -> Any:
    from syntegra.estate import services

    return services


def _facility_prepare(d: Data) -> Data:
    kind, _, sid = str(d.pop("facility", "")).partition(":")
    d["subject_kind"], d["subject_id"] = kind, sid
    return d


def _site_prepare(d: Data) -> Data:
    lat, lng = d.get("latitude"), d.get("longitude")
    if (lat is None) != (lng is None):
        raise Invalid({"longitude": "Give both latitude and longitude, or neither."})
    return d


def _register_site(d: Data) -> Any:
    names = ("site_code", "name", "owner", "title_document", "title_reference", "area_sqm", "fenced", "encroachment")
    kw = _clean(d, *names, "acquired_on", "valuation_minor")
    if d.get("latitude") is not None:
        kw["location"] = (d["latitude"], d["longitude"])
    return _estate().register_site(_u(d["institution_id"]), **kw)


def _assess(d: Data) -> Any:
    kw = _clean(d, "learners_affected", "repair_estimate_minor", "next_due_on", "assessed_on")
    return _estate().assess(
        d["subject_kind"],
        _u(d["subject_id"]),
        condition_grade=d["condition_grade"],
        usability=d["usability"],
        structural_risk=d["structural_risk"],
        in_use=bool(d.get("in_use")),
        assessor_kind=d.get("assessor_kind") or "head_of_institution",
        **kw,
    )


# --------------------------------------------------------------------------- examinations (EXM-01, EXM-03)
def _exams() -> Any:
    from syntegra.assessment import exams

    return exams


def _plan_sitting(d: Data) -> Any:
    from syntegra.assessment.api import starts_at

    return _exams().plan_sitting(
        _u(d["target"]),
        [_u(x) for x in d["room_ids"]],
        starts_at(d),
        spacing=d.get("spacing") or "alternate",
        invigilator_staff_ids=[_u(x) for x in d.get("invigilator_staff_ids") or []],
    )


def _sitting_done(r: Any, _d: Data) -> tuple[str, str | None]:
    from syntegra.assessment.models import ExamPaper, ExamSeries

    seated = sum(len(x.seat_allocations or {}) for x in r)
    paper = ExamPaper.objects.get(pk=r[0].paper_id)
    series = ExamSeries.objects.get(pk=paper.series_id)
    return (
        f"{paper.paper_code}: {seated} candidates seated in {len(r)} hall{'s' if len(r) != 1 else ''}.",
        f"/exams/series/{series.id}/sittings#paper-{paper.paper_code}",
    )


# --------------------------------------------------------------------------- serializers reused from the API
def _api(module: str, name: str) -> Any:
    import importlib

    return getattr(importlib.import_module(f"syntegra.{module}.api"), name)


class _Lazy:
    """Defers importing an API serializer until the form is used (keeps import order simple)."""

    def __init__(self, module: str, name: str) -> None:
        self.module, self.name = module, name

    def __call__(self, *a: Any, **kw: Any) -> Any:
        return _api(self.module, self.name)(*a, **kw)


def api(module: str, name: str) -> Any:
    return _Lazy(module, name)


LEVELS = ch.code_list("education_level")
DECISIONS = ch.fixed(
    ["admit", "admit_with_payment_plan", "defer_pending_settlement"],
    {
        "admit": "Admit (the creditor recovers through its own process)",
        "admit_with_payment_plan": "Admit with a payment plan",
        "defer_pending_settlement": "Defer pending settlement",
    },
)

FORMS: tuple[Form, ...] = (
    # ------------------------------------------------------------------ institutions and learners
    Form(
        "institution-register",
        "Register an institution",
        "Institutions",
        "institution:register",
        "Adds a school or college to the state register. Possible duplicates (same name, registration number or "
        "location in the LGA) are shown; give an override reason only if you are sure it is a different institution.",
        (
            Field("name", "Name"),
            Field("short_name", "Short name", required=False),
            Field("category", "Category", "select", choices=ch.code_list("institution_category")),
            Field("ownership", "Ownership", "select", choices=ch.code_list("ownership")),
            Field("lga_scope_id", "Local government area", "select", choices=ch.lgas),
            Field("town", "Town"),
            Field("street", "Street address", required=False),
            Field("levels", "Levels offered", "multi", choices=LEVELS, hint="Hold Ctrl (⌘ on Mac) to choose several."),
            Field("gov_reg_no", "Government registration number", required=False),
            Field("capacity", "Capacity (learners)", "number", required=False),
            Field(
                "day_boarding",
                "Day or boarding",
                "select",
                required=False,
                choices=ch.fixed(["day", "boarding", "mixed"]),
            ),
            Field("gender_intake", "Intake", "select", required=False, choices=ch.fixed(["mixed", "boys", "girls"])),
            Field("latitude", "Latitude", "number", required=False, hint="Decimal degrees, e.g. 5.5320"),
            Field("longitude", "Longitude", "number", required=False, hint="Decimal degrees, e.g. 7.4860"),
            Field(
                "override_reason", "Override reason", "textarea", required=False, hint="Only if warned of a duplicate."
            ),
        ),
        _register_institution,
        lambda r, _d: (f"{r.name} registered as {r.institution_code}.", f"/institutions/{r.id}/regulation"),
        api("institutions", "RegisterSerializer"),
        _institution_prepare,
        "Register institution",
    ),
    Form(
        "learner-transfer",
        "Transfer a learner",
        "Learners",
        "enrolment:transfer",
        "Moves a learner's current enrolment to another institution in the state. The receiving institution's fee "
        "clearance check runs first; if it finds unpaid fees, record your admission decision below. The check never "
        "holds back the learner's records.",
        (
            Field("learner", "Global Learner ID", "glid", hint="e.g. LRN-0000-0000-00"),
            Field("to_institution_id", "Receiving institution", "select", choices=ch.institutions),
            Field("education_level", "Level of entry", "select", required=False, choices=LEVELS),
            Field("effective_on", "Effective on", "date", required=False, hint="Today if left blank."),
            Field(
                "decision", "Admission decision (if fees are outstanding)", "select", required=False, choices=DECISIONS
            ),
            Field("decision_reason", "Reason for the decision", "textarea", required=False),
            Field("payment_plan_ref", "Payment plan reference", required=False),
        ),
        _transfer,
        lambda r, d: ("Transfer recorded.", f"/learners/{d['learner']}"),
        api("learners", "TransferSerializer"),
        submit="Transfer",
    ),
    Form(
        "class-create",
        "Create a class",
        "Classes",
        "class:manage",
        "Creates a class (arm) for an academic session. Capacity defaults to the standard for the level.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("period_id", "Session or term", "select", choices=ch.periods),
            Field("name", "Class name", hint="e.g. JSS1 Gold"),
            Field("education_level", "Level", "select", choices=LEVELS),
            Field("capacity", "Capacity", "number", required=False),
        ),
        _create_class,
        lambda r, _d: (f"Class {r.name} created.", f"/registers/class/{r.id}"),
        api("academic", "ClassSerializer"),
    ),
    Form(
        "class-member",
        "Add a learner to a class",
        "Classes",
        "class:manage",
        "Places an enrolled learner in a class from today.",
        (_target("Class", ch.classes), Field("learner_id", "Global Learner ID", "glid")),
        _add_member,
        lambda r, d: ("Learner added to the class.", f"/registers/class/{d['target']}"),
        api("academic", "MemberSerializer"),
        submit="Add to class",
    ),
    # ------------------------------------------------------------------ certificates
    Form(
        "certificate-reissue",
        "Request a certificate reissue",
        "Certificates",
        "certificate:reissue",
        "Opens a reissue case for a lost, damaged or incorrect certificate. A second officer approves it; the "
        "replacement then supersedes the original, which stops verifying.",
        (
            Field("certificate_number", "Certificate number"),
            Field(
                "reason",
                "Reason",
                "select",
                choices=ch.fixed(["lost_or_stolen", "damaged", "change_of_name", "issuer_error", "certified_copy"]),
            ),
            Field("applicant_name", "Applicant's name"),
            Field("applicant_phone", "Applicant's phone", hint="e.g. 08031234567"),
        ),
        _request_reissue,
        lambda r, _d: (f"Reissue case {r.case_number} opened.", None),
        api("certificates", "ReissueSerializer"),
        _certificate_prepare,
        "Open case",
    ),
    Form(
        "certificate-reissue-decision",
        "Decide a reissue case",
        "Certificates",
        "certificate:approve",
        "Second-person decision (four eyes): the officer who reviewed the case cannot approve it.",
        (
            _target("Reissue case", ch.reissue_cases),
            Field(
                "approve",
                "Decision",
                "select",
                choices=ch.fixed(["true", "false"], {"true": "Approve and issue the replacement", "false": "Reject"}),
            ),
            Field("note", "Note", "textarea", required=False),
        ),
        _decide_reissue,
        lambda r, _d: (f"Case {r.case_number} is now {ch.human(r.status).lower()}.", None),
        api("certificates", "ReissueDecisionSerializer"),
        submit="Record decision",
    ),
    # ------------------------------------------------------------------ fee clearance
    Form(
        "obligation-publish",
        "Publish unpaid fees",
        "Fee clearance",
        "clearance:publish",
        "Publishes what a learner owes your institution so that receiving schools see it on their clearance check. "
        "Manual entries need the invoice references and a supporting document. Enter 0 to settle an open obligation.",
        (
            Field("learner_id", "Global Learner ID", "glid"),
            Field("creditor_institution_id", "Owed to (your institution)", "select", choices=ch.institutions),
            Field("kind", "Kind", "select", choices=ch.enum("obligation_kind")),
            Field("amount_minor", "Amount outstanding (₦)", "money", hint="0 settles the open obligation."),
            Field("oldest_due_on", "Oldest unpaid due date", "date"),
            Field("invoices", "Invoice references", "list", hint="One per line."),
            Field("document_id", "Supporting document reference", hint="Statement of account or ledger extract."),
            Field("periods", "Terms covered", "list", required=False, hint="e.g. 2025/2026 T1, one per line."),
            Field("payer_kind", "Payer", "select", choices=ch.enum("account_holder"), default="guardian"),
        ),
        _publish,
        _published,
        api("clearance", "ObligationSerializer"),
        _obligation_prepare,
        "Publish",
    ),
    Form(
        "obligation-dispute",
        "Dispute an obligation",
        "Fee clearance",
        "clearance:dispute",
        "Records a dispute. While it is open the amount shows as disputed and needs no admission decision.",
        (
            _target("Obligation", ch.open_obligations),
            Field(
                "party",
                "Raised by",
                "select",
                choices=ch.fixed(["guardian", "learner", "admitting_institution", "creditor"]),
            ),
            Field(
                "grounds",
                "Grounds",
                "select",
                choices=ch.fixed(
                    [
                        "already_paid",
                        "amount_wrong",
                        "not_liable",
                        "waiver_granted",
                        "statute_barred",
                        "protected_learner",
                        "other",
                    ]
                ),
            ),
            Field("statement", "Statement", "textarea", hint="At least 10 characters."),
        ),
        _raise_dispute,
        _ok("Dispute recorded; the claim now shows as disputed."),
        api("clearance", "DisputeSerializer"),
        submit="Record dispute",
    ),
    Form(
        "obligation-dispute-resolve",
        "Resolve a dispute",
        "Fee clearance",
        "clearance:resolve",
        "Upheld or withdrawn disputes withdraw the claim; partly upheld sets the new amount; rejected restores it.",
        (
            _target("Dispute", ch.open_disputes),
            Field(
                "resolution",
                "Resolution",
                "select",
                choices=ch.fixed(["upheld", "partly_upheld", "rejected", "withdrawn"]),
            ),
            Field(
                "resolved_amount_minor", "Amount still owed (₦)", "money", required=False, hint="Partly upheld only."
            ),
            REASON,
        ),
        _resolve_dispute,
        _ok("Dispute resolved."),
        api("clearance", "ResolutionSerializer"),
        submit="Resolve",
    ),
    # ------------------------------------------------------------------ curriculum coverage
    Form(
        "coverage-evaluate",
        "Evaluate curriculum coverage",
        "Curriculum coverage",
        "coverage:evaluate",
        "Checks every class and subject of the institution against the curriculum and opens, updates or closes gaps.",
        (Field("institution_id", "Institution", "select", choices=ch.institutions),),
        _evaluate,
        lambda r, _d: (
            f"Evaluated: {r['opened']} gaps opened, {r['updated']} updated, {r['closed']} closed; {r['open']} open.",
            "/coverage",
        ),
        submit="Evaluate",
    ),
    Form(
        "coverage-gap-accept",
        "Accept a coverage gap",
        "Curriculum coverage",
        "coverage:manage",
        "The head of institution accepts a gap that cannot be closed this term; the reason is kept.",
        (_target("Gap", ch.open_gaps), REASON),
        _accept_gap,
        _ok("Gap accepted.", "/coverage"),
        ReasonSerializer,
        submit="Accept gap",
    ),
    # ------------------------------------------------------------------ school financing
    Form(
        "census-take",
        "Take the enrolment census",
        "School financing",
        "census:take",
        "Counts eligible learners on census day for the billing period; the head of institution then confirms it.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("billing_period_id", "Billing period", "select", choices=ch.billing_periods),
        ),
        _take_census,
        lambda r, _d: (f"Census taken ({ch.human(r.status).lower()}).", None),
        api("financing", "CensusSerializer"),
        submit="Take census",
    ),
    Form(
        "census-freeze",
        "Confirm and freeze a census",
        "School financing",
        "census:confirm",
        "Confirms the census and freezes it; it becomes the basis of the financing demand.",
        (_target("Census", ch.census_awaiting),),
        _freeze,
        _ok("Census confirmed and frozen."),
        submit="Confirm and freeze",
        caution="A frozen census cannot be changed.",
    ),
    Form(
        "census-demand",
        "Issue the financing demand",
        "School financing",
        "financing:demand",
        "Issues the demand to each funder from a frozen census.",
        (_target("Frozen census", ch.census_frozen),),
        _demand,
        lambda r, _d: (f"{len(r)} demand(s) issued.", None),
        submit="Issue demand",
    ),
    # ------------------------------------------------------------------ HR
    Form(
        "hr-position",
        "Create a position",
        "HR",
        "hr:establishment",
        "Adds a position to the establishment. It must be approved before anyone is appointed or posted to it.",
        (
            Field("title", "Title"),
            Field("cadre_code", "Cadre", "select", choices=ch.cadres),
            Field("employer_scope_id", "Employer", "select", choices=ch.employer_scopes),
            Field("institution_id", "Institution", "select", required=False, choices=ch.institutions),
            Field("grade_level_min", "Lowest grade level", "number", hint="1–17"),
            Field("grade_level_max", "Highest grade level", "number", hint="1–17"),
            Field("education_levels", "Levels taught", "multi", required=False, choices=LEVELS),
            Field(
                "funding",
                "Funding",
                "select",
                choices=ch.fixed(["funded", "unfunded", "donor_funded", "privately_funded"]),
            ),
        ),
        _create_position,
        lambda r, d: (f"Position {r.position_code} created ({r.status}).", _establishment_link(r, d)),
        api("hr", "PositionSerializer"),
    ),
    Form(
        "hr-appoint",
        "Appoint a member of staff",
        "HR",
        "hr:appoint",
        "Appoints staff to an approved, vacant position.",
        (
            Field("staff_id", "Staff", "select", choices=ch.staff),
            Field("position_id", "Position", "select", choices=ch.positions),
            Field("appointment_type", "Appointment type", "select", choices=ch.enum("appointment_type")),
            Field("first_appointment_on", "First appointment date", "date"),
            Field("grade_level", "Grade level", "number"),
            Field("step", "Step", "number", default="1"),
            Field("confirmed_on", "Confirmed on", "date", required=False),
        ),
        _appoint,
        lambda r, d: ("Appointment recorded.", _establishment_link(r, d)),
        api("hr", "AppointSerializer"),
        submit="Appoint",
    ),
    Form(
        "hr-posting",
        "Request a posting",
        "HR",
        "hr:posting_request",
        "Requests a transfer or posting to an approved position. A second officer approves it.",
        (
            Field("staff_id", "Staff", "select", choices=ch.staff),
            Field("to_position_id", "To position", "select", choices=ch.positions),
            Field("posting_kind", "Kind", "select", choices=ch.enum("posting_kind")),
            Field("effective_on", "Effective on", "date"),
            Field("reason", "Reason", "textarea"),
        ),
        _request_posting,
        lambda r, _d: (f"Posting {r.order_number} submitted for approval.", None),
        api("hr", "PostingSerializer"),
        submit="Submit",
    ),
    Form(
        "hr-posting-decision",
        "Decide a posting",
        "HR",
        "hr:posting_approve",
        "Approve or reject a submitted posting, or make an approved posting effective (moves the post and access).",
        (
            _target("Posting", ch.postings),
            Field(
                "action",
                "Action",
                "select",
                choices=ch.fixed(["approve", "reject", "effective"], {"effective": "Make effective"}),
            ),
            Field("note", "Note", "textarea", required=False),
        ),
        _decide_posting,
        lambda r, _d: (f"Posting {r.order_number} is now {r.status}.", None),
        api("hr", "PostingDecisionSerializer"),
        submit="Record",
    ),
    Form(
        "hr-separation",
        "Record a separation",
        "HR",
        "hr:separate",
        "Ends a staff post (resignation, retirement, death, dismissal …). Access is withdrawn from the effective date.",
        (
            Field("staff_post_id", "Staff post", "select", choices=ch.staff_posts),
            Field(
                "separation_kind",
                "Kind",
                "select",
                choices=ch.fixed(
                    [
                        "resignation",
                        "retirement_statutory",
                        "retirement_voluntary",
                        "death",
                        "dismissal",
                        "termination",
                        "end_of_contract",
                        "transfer_of_service",
                        "abandonment",
                    ]
                ),
            ),
            Field("effective_on", "Effective on", "date"),
        ),
        _separate,
        _ok("Separation recorded."),
        api("hr", "SeparationSerializer"),
        submit="Record separation",
        caution="Sign-in access ends on the effective date.",
    ),
    Form(
        "hr-leave",
        "Request leave",
        "HR",
        ("hr:leave_request", "hr:leave_manage"),
        "Your own leave, or leave on behalf of a member of staff (needs leave management rights).",
        (
            Field("staff_id", "Staff", "select", choices=ch.staff),
            Field("leave_type", "Leave type", "select", choices=ch.leave_types),
            Field("starts_on", "Starts on", "date"),
            Field("ends_on", "Ends on", "date"),
            Field("note", "Note", "textarea", required=False),
        ),
        _request_leave,
        lambda r, _d: (f"Leave requested: {r.starts_on} to {r.ends_on}.", None),
        api("hr", "LeaveSerializer"),
        submit="Request leave",
    ),
    Form(
        "hr-leave-decision",
        "Decide a leave request",
        "HR",
        "hr:leave_approve",
        "Approve or reject a leave request; name relief staff where cover is needed.",
        (
            _target("Leave request", ch.leave_requests),
            Field("approve", "Decision", "select", choices=YES_NO),
            Field("relief_staff_id", "Relief staff", "select", required=False, choices=ch.staff),
        ),
        _decide_leave,
        lambda r, _d: (f"Leave {r.status}.", None),
        api("hr", "LeaveDecisionSerializer"),
        submit="Record decision",
    ),
    Form(
        "hr-promotion",
        "Open a promotion case",
        "HR",
        "hr:promote",
        "Opens a case for the promotion exercise; eligibility (years in grade, discipline) is checked.",
        (
            Field("staff_id", "Staff", "select", choices=ch.staff),
            Field("exercise_label", "Exercise", hint="e.g. 2026 promotion exercise"),
        ),
        _open_promotion,
        lambda r, _d: (f"Promotion case opened: GL {r.from_grade_level} → {r.to_grade_level}.", None),
        api("hr", "PromotionSerializer"),
        submit="Open case",
    ),
    Form(
        "hr-promotion-decision",
        "Record a promotion board decision",
        "HR",
        "hr:promote",
        "The board's decision; an approval takes effect on the date given.",
        (
            _target("Promotion case", ch.promotion_cases),
            Field("decision", "Decision", "select", choices=ch.fixed(["approved", "deferred", "not_approved"])),
            Field("effective_on", "Effective on", "date", required=False),
            Field("reason", "Reason", "textarea", required=False),
        ),
        _decide_promotion,
        lambda r, _d: (f"Promotion case {r.status}.", None),
        api("hr", "PromotionDecisionSerializer"),
        submit="Record decision",
    ),
    Form(
        "hr-relations",
        "Open an employee relations case",
        "HR",
        "hr:relations",
        "A query, disciplinary case, grievance, appeal or petition. Open cases pause promotion.",
        (
            Field("staff_id", "Staff", "select", choices=ch.staff),
            Field(
                "case_kind",
                "Kind",
                "select",
                choices=ch.fixed(["query", "disciplinary", "grievance", "appeal", "petition"]),
            ),
            Field("summary", "Summary", "textarea", hint="At least 10 characters."),
        ),
        _open_case,
        _ok("Case opened."),
        api("hr", "RelationsSerializer"),
        submit="Open case",
    ),
    Form(
        "hr-integrity-scan",
        "Run the payroll integrity scan",
        "HR",
        "hr:integrity",
        "Looks for shared bank accounts or BVNs, concurrent public posts, pay after separation or retirement and "
        "failed headcounts. Flags are for human review; nothing is stopped automatically.",
        (),
        _scan,
        lambda r, _d: ("Scan complete: " + ", ".join(f"{ch.human(k).lower()} {v}" for k, v in r.items()) + ".", None),
        submit="Run scan",
    ),
    Form(
        "hr-integrity-hold",
        "Decide an integrity flag",
        "HR",
        "hr:integrity",
        "Hold the staff member's pay while the flag is investigated, or release it with the finding.",
        (
            _target("Flag", ch.integrity_flags),
            Field(
                "hold",
                "Decision",
                "select",
                choices=ch.fixed(
                    ["true", "false"], {"true": "Hold pay pending investigation", "false": "Release — resolved"}
                ),
            ),
            REASON,
        ),
        _hold,
        lambda r, _d: (f"Flag {ch.human(r.status).lower()}.", None),
        api("hr", "HoldSerializer"),
        submit="Record",
    ),
    Form(
        "hr-payroll-run",
        "Compute a payroll run",
        "HR",
        "hr:payroll_prepare",
        "Calculates pay for the employer's active staff; exceptions are listed for review before approval.",
        (
            Field("employer_scope_id", "Employer", "select", choices=ch.employer_scopes),
            Field("period_label", "Period", hint="e.g. 2026-10"),
            Field("pay_date", "Pay date", "date"),
        ),
        _payroll_run,
        lambda r, _d: (
            f"Payroll {r.period_label} {ch.human(r.status).lower()}: net {ch.naira(r.net_total_minor)}.",
            None,
        ),
        api("hr", "PayrollRunSerializer"),
        submit="Compute",
    ),
    Form(
        "hr-payroll-approve",
        "Approve a payroll run",
        "HR",
        "hr:payroll_approve",
        "Second-person approval; the officer who computed the run cannot approve it.",
        (_target("Payroll run", ch.payroll_runs),),
        _approve_payroll,
        lambda r, _d: (f"Payroll {r.period_label} approved.", None),
        submit="Approve",
        caution="Approval releases the run for payment.",
    ),
    # ------------------------------------------------------------------ regulation
    Form(
        "regulation-link",
        "Add a regulatory link",
        "Regulators",
        "regulation:manage",
        "Links an institution to a supervising ministry, regulator, examination body or council beyond what the "
        "rules derive (e.g. an affiliating university or a professional council).",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("body_code", "Body", "select", choices=ch.regulatory_bodies),
            Field(
                "relationship",
                "Relationship",
                "select",
                choices=ch.fixed(
                    [
                        "supervision",
                        "accreditation",
                        "licensing",
                        "curriculum",
                        "examination",
                        "admission",
                        "teacher_registration",
                        "professional_regulation",
                        "funding",
                        "affiliation",
                    ]
                ),
            ),
            Field("covers", "Covers", hint="e.g. WASSCE for SSS3"),
            Field("levels", "Levels", "list", required=False, hint="Level codes, one per line, e.g. SSS3."),
            REASON,
        ),
        _set_link,
        lambda r, _d: (f"{r.body_code} linked.", f"/institutions/{r.institution_id}/regulation"),
        api("regulation", "LinkSerializer"),
        submit="Add link",
    ),
    Form(
        "regulation-end",
        "End a regulatory link",
        "Regulators",
        "regulation:manage",
        "Ends a link from today; the history is kept.",
        (
            Field("institution_id", "Institution", "hidden", required=False),
            _target("Link", ch.regulation_links),
            REASON,
        ),
        _end_link,
        lambda r, _d: (f"{r.body_code} link ended.", f"/institutions/{r.institution_id}/regulation"),
        ReasonSerializer,
        submit="End link",
    ),
    Form(
        "federal-import",
        "Import federal institutions",
        "Federal institutions",
        "federal_institutions:import",
        "Loads the official list of federal institutions from a CSV file in the published template "
        "(ceda/templates/federal_institutions.csv). Existing institutions are updated; each new one gets its "
        "regulatory profile.",
        (
            Field("csv", "CSV file", "file"),
            Field("dry_run", "Check only — do not import", "checkbox", required=False, default="on"),
        ),
        _import,
        _imported,
        submit="Upload",
    ),
    # ------------------------------------------------------------------ security agencies' training
    Form(
        "security-intake",
        "Create a course intake",
        "Security training",
        "security_training:intake",
        "Opens an intake (a course or set) of a training institution's course.",
        (
            _target("Course", ch.security_courses),
            Field("intake_code", "Intake code", hint="e.g. RC78"),
            Field("name", "Name", hint="e.g. 78 Regular Course"),
            Field("starts_on", "Starts on", "date"),
            Field("ends_on", "Ends on", "date", required=False),
            Field("capacity", "Capacity", "number", required=False),
        ),
        _create_intake,
        lambda r, _d: (f"Intake {r.intake_code} created.", f"/security-training/intakes/{r.id}"),
        api("security_training", "IntakeSerializer"),
        submit="Create intake",
    ),
    Form(
        "security-trainee",
        "Add a trainee to an intake",
        "Security training",
        "security_training:record",
        "Adds a registered learner to an intake, with their rank at entry where the agency uses ranks.",
        (
            _target("Intake", ch.security_intakes),
            Field("learner_id", "Global Learner ID", "glid"),
            Field("rank_code", "Rank at entry", required=False, hint="Rank code, e.g. OCDT, ASP, CPL."),
        ),
        _add_trainee,
        lambda r, _d: ("Trainee added.", f"/security-training/intakes/{r.intake_id}"),
        api("security_training", "TraineeSerializer"),
        submit="Add trainee",
    ),
    Form(
        "security-outcome",
        "Record a trainee's outcome",
        "Security training",
        "security_training:record",
        "Final outcome of the course for the trainee. Failed, relegated, withdrawn and discharged need a reason.",
        (
            _target("Trainee", ch.trainees_in_training),
            Field(
                "outcome",
                "Outcome",
                "select",
                choices=ch.fixed(
                    ["passed", "passed_out", "commissioned", "failed", "relegated", "withdrawn", "discharged"]
                ),
            ),
            Field("result", "Result", required=False, hint="e.g. Second Class Upper; 3rd in order of merit"),
            Field("reason", "Reason", "textarea", required=False),
            Field("on", "Date", "date", required=False),
        ),
        _record_outcome,
        lambda r, _d: (
            f"Outcome recorded: {ch.human(r.outcome).lower()}.",
            f"/security-training/intakes/{r.intake_id}",
        ),
        api("security_training", "OutcomeSerializer"),
        submit="Record outcome",
    ),
    # ------------------------------------------------------------------ budgets and imprest (CR-006)
    Form(
        "budget-cost-centre",
        "Add a cost centre",
        "Budgets",
        "budget:prepare",
        "A cost centre is a part of the institution that holds a budget — administration, a department, boarding, "
        "the estate, ICT. Budget lines, commitments and imprest are all recorded against a cost centre.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("code", "Code", hint="Short code, e.g. ADM, SCI, ESTATE."),
            Field("name", "Name", hint="e.g. Science department"),
            Field("kind", "Kind", "select", choices=ch.enum("cost_centre_kind")),
        ),
        lambda d: _budgets().create_cost_centre(_u(d["institution_id"]), d["code"], d["name"], d["kind"]),
        lambda r, _d: (f"Cost centre {r.code} added.", "/finance/performance"),
        api("finance", "CostCentreSerializer"),
        submit="Add cost centre",
    ),
    Form(
        "budget-prepare",
        "Prepare a budget",
        "Budgets",
        "budget:prepare",
        "Creates a draft budget for the year. Enter one line per row as: cost-centre code | economic code | amount "
        "in naira | source | description. For example: ADM | 22020101 | 1,250,000 | overhead | Stationery. Source "
        "is one of subvention, overhead, capital allocation, internally generated revenue, grant, intervention. A "
        "second officer approves it.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("fiscal_year", "Year", "number", default=str(dt.date.today().year)),
            Field("lines_text", "Budget lines", "textarea", hint="One line per row, fields separated by |"),
        ),
        _budget_lines_out,
        lambda r, _d: (f"Draft budget {r.fiscal_year} version {r.version} saved; it now needs approval.", None),
        api("finance", "BudgetSerializer"),
        _budget_prepare,
        "Save draft",
    ),
    Form(
        "budget-approve",
        "Approve a budget",
        "Budgets",
        "budget:approve",
        "Approves a draft budget; the previous approved version of the year is superseded. The person who prepared "
        "it cannot approve it.",
        (_target("Draft budget", ch.draft_budgets),),
        lambda d: _budgets().approve_budget(_u(d["target"])),
        lambda r, _d: (f"Budget {r.fiscal_year} version {r.version} approved.", "/finance/performance"),
        submit="Approve",
        caution="Approval makes the budget the one spending is checked against.",
    ),
    Form(
        "budget-commit",
        "Commit funds",
        "Budgets",
        "budget:commit",
        "Reserves money on a budget line for an order, contract or requisition, so it cannot be spent twice. Refused "
        "if the line does not have enough available.",
        (
            Field("budget_line_id", "Budget line", "select", choices=ch.budget_lines),
            Field("amount_minor", "Amount (₦)", "money"),
            Field("source_kind", "For", "select", choices=ch.enum("commitment_source"), default="purchase_order"),
            Field("description", "Description", hint="e.g. LPO 0042 — laboratory reagents"),
        ),
        lambda d: _budgets().commit(
            _u(d["budget_line_id"]),
            d["amount_minor"],
            source_kind=d["source_kind"],
            source_id=uuid.uuid4(),
            description=d["description"],
        ),
        lambda r, _d: (f"{ch.naira(r.amount_minor)} committed.", "/finance/performance"),
        api("finance", "CommitmentSerializer"),
        submit="Commit",
    ),
    Form(
        "budget-spend",
        "Record spending against a commitment",
        "Budgets",
        "budget:commit",
        "Records what was actually paid. Tick 'final payment' to release whatever is left of the commitment back to "
        "the budget line.",
        (
            _target("Commitment", ch.open_commitments),
            Field("amount_minor", "Amount paid (₦)", "money"),
            Field("final", "Final payment — release the balance", "checkbox", required=False),
        ),
        lambda d: _budgets().spend(_u(d["target"]), d["amount_minor"], final=bool(d.get("final"))),
        lambda r, _d: (
            f"Spending recorded; commitment is now {ch.human(r.status).lower()}.",
            "/finance/performance",
        ),
        api("finance", "SpendSerializer"),
        submit="Record",
    ),
    Form(
        "budget-virement",
        "Move funds between lines (virement)",
        "Budgets",
        "budget:virement",
        "Asks to move budget from one approved line to another. Someone other than you approves it.",
        (
            Field("from_line_id", "From line", "select", choices=ch.budget_lines),
            Field("to_line_id", "To line", "select", choices=ch.budget_lines),
            Field("amount_minor", "Amount (₦)", "money"),
            REASON,
        ),
        lambda d: _budgets().request_virement(
            _u(d["from_line_id"]), _u(d["to_line_id"]), d["amount_minor"], d["reason"]
        ),
        lambda r, _d: (f"Virement {r.virement_number} submitted for approval.", None),
        api("finance", "VirementSerializer"),
        submit="Submit",
    ),
    Form(
        "budget-virement-decision",
        "Decide a virement",
        "Budgets",
        "budget:approve",
        "Approve or reject a request to move funds. You cannot decide your own request.",
        (_target("Virement", ch.submitted_virements), Field("approve", "Decision", "select", choices=YES_NO)),
        lambda d: _budgets().decide_virement(_u(d["target"]), d["approve"]),
        lambda r, _d: (f"Virement {r.virement_number} {r.status}.", "/finance/performance"),
        api("finance", "DecisionSerializer"),
        submit="Record decision",
    ),
    Form(
        "imprest-request",
        "Request imprest",
        "Budgets",
        "imprest:request",
        "Cash advanced to a member of staff for a stated purpose, to be accounted for with receipts by the retirement "
        "date. Someone other than you approves and issues it.",
        (
            Field("holder_staff_id", "Member of staff", "select", choices=ch.staff),
            Field("budget_line_id", "Budget line", "select", choices=ch.budget_lines),
            Field("purpose", "Purpose", hint="e.g. Inter-house sports — first aid and refreshments"),
            Field("amount_minor", "Amount (₦)", "money"),
            Field("retire_by", "Account for it by", "date"),
        ),
        lambda d: _budgets().request_imprest(
            _u(d["holder_staff_id"]), _u(d["budget_line_id"]), d["purpose"], d["amount_minor"], d["retire_by"]
        ),
        lambda r, _d: (f"Imprest {r.imprest_number} requested.", "/finance/imprest"),
        api("finance", "ImprestSerializer"),
        submit="Request",
    ),
    Form(
        "imprest-approve",
        "Approve and issue imprest",
        "Budgets",
        "imprest:approve",
        "Approving issues the imprest and commits its budget line. You cannot approve imprest you requested.",
        (_target("Imprest", ch.requested_imprest), Field("approve", "Decision", "select", choices=YES_NO)),
        lambda d: _budgets().approve_imprest(_u(d["target"]), d["approve"]),
        lambda r, _d: (f"Imprest {r.imprest_number} {ch.human(r.status).lower()}.", "/finance/imprest"),
        api("finance", "DecisionSerializer"),
        submit="Record decision",
    ),
    Form(
        "imprest-retire",
        "Retire imprest",
        "Budgets",
        "imprest:retire",
        "Account for an imprest. List the receipts one per row as: reference | amount in naira | payee. Enter the "
        "total spent and any cash refunded; the spent amount becomes actual expenditure on the budget line.",
        (
            _target("Imprest", ch.issued_imprest),
            Field("receipts_text", "Receipts", "textarea", hint="e.g. RCT-118 | 45,000 | Mercy Pharmacy"),
            Field("amount_minor", "Total spent (₦)", "money"),
            Field("refund_minor", "Cash refunded (₦)", "money", required=False),
        ),
        lambda d: _budgets().retire_imprest(
            _u(d["target"]), d["receipts"], d["amount_minor"], d.get("refund_minor") or 0
        ),
        lambda r, _d: (f"Imprest {r.imprest_number} is now {ch.human(r.status).lower()}.", "/finance/imprest"),
        api("finance", "RetireSerializer"),
        _imprest_retire_prepare,
        "Retire",
    ),
    # ------------------------------------------------------------------ funding and loans (CR-006)
    Form(
        "funding-apply",
        "Apply for funding or a loan",
        "Funding and loans",
        ("funding:apply", "funding:apply_own"),
        "Apply for an institution (capital, intervention), a member of staff (welfare loan, salary advance) or a "
        "learner (scholarship, bursary). Fill only the applicant field that matches. Eligibility is checked "
        "automatically; a reviewer and a different decision-maker then consider it.",
        (
            Field("programme_id", "Programme", "select", choices=ch.funding_programmes),
            Field("applicant_kind", "Applying for", "select", choices=ch.enum("funding_beneficiary")),
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("staff_id", "Member of staff (staff applications)", "select", required=False, choices=ch.staff),
            Field("learner", "Global Learner ID (learner applications)", "glid", required=False),
            Field("amount_minor", "Amount requested (₦)", "money"),
            Field("purpose_detail", "What the money is for", "textarea", hint="At least 10 characters."),
        ),
        _funding_apply,
        lambda r, _d: (
            f"Application {r.application_number} submitted"
            + ("." if r.eligible else " — the eligibility check found a problem; the reviewer will see it."),
            "/funding",
        ),
        api("funding", "ApplicationSerializer"),
        _funding_apply_prepare,
        "Submit application",
    ),
    Form(
        "funding-recommend",
        "Review a funding application",
        "Funding and loans",
        "funding:review",
        "Record your recommendation. You cannot review an application you submitted.",
        (_target("Application", ch.applications_to_review), Field("recommendation", "Recommendation", "textarea")),
        lambda d: _funding().recommend(_u(d["target"]), d["recommendation"]),
        lambda r, _d: (f"Application {r.application_number} recommended for decision.", "/funding"),
        api("funding", "RecommendSerializer"),
        submit="Save recommendation",
    ),
    Form(
        "funding-decide",
        "Decide a funding application",
        "Funding and loans",
        "funding:decide",
        "A person decides — never the system. You cannot decide an application you submitted or reviewed.",
        (
            _target("Application", ch.applications_to_decide),
            Field("approve", "Decision", "select", choices=YES_NO),
            REASON,
            Field(
                "amount_approved_minor", "Amount approved (₦)", "money", required=False, hint="Blank = as requested."
            ),
        ),
        lambda d: _funding().decide(
            _u(d["target"]), d["approve"], d["reason"], amount_approved_minor=d.get("amount_approved_minor")
        ),
        lambda r, _d: (f"Application {r.application_number} {r.status}.", "/funding"),
        api("funding", "DecideSerializer"),
        submit="Record decision",
    ),
    Form(
        "funding-sign",
        "Sign a funding agreement",
        "Funding and loans",
        "funding:decide",
        "Turns an approved application into an agreement and, for loans, a repayment schedule. For staff loans "
        "repaid from pay, give the gross monthly pay: the agreement is refused if the instalment would take net pay "
        "below the policy floor.",
        (
            _target("Approved application", ch.applications_approved),
            Field("first_repayment_on", "First repayment on", "date", required=False),
            Field("gross_pay_minor", "Gross monthly pay (₦)", "money", required=False),
            Field("other_deductions_minor", "Other monthly deductions (₦)", "money", required=False),
        ),
        lambda d: _funding().sign_agreement(
            _u(d["target"]), **_clean(d, "first_repayment_on", "gross_pay_minor", "other_deductions_minor")
        ),
        lambda r, _d: (f"Agreement {r.agreement_number} signed.", f"/funding/agreements/{r.id}"),
        api("funding", "AgreementSerializer"),
        submit="Sign agreement",
    ),
    Form(
        "funding-disburse",
        "Disburse funds",
        "Funding and loans",
        "funding:disburse",
        "Records money paid out under an agreement. If you choose a budget line, the institution's budget rises by "
        "the amount received.",
        (
            _target("Agreement", ch.funding_agreements),
            Field("amount_minor", "Amount (₦)", "money"),
            Field("payee_kind", "Paid to", "select", choices=ch.enum("disbursement_payee")),
            Field("purpose", "Purpose"),
            Field("reference", "Payment reference"),
            Field("budget_line_id", "Budget line receiving it", "select", required=False, choices=ch.budget_lines),
        ),
        lambda d: _funding().disburse(
            _u(d["target"]),
            d["amount_minor"],
            payee_kind=d["payee_kind"],
            purpose=d["purpose"],
            reference=d["reference"],
            **_clean(d, "budget_line_id"),
        ),
        lambda r, _d: (f"{ch.naira(r.amount_minor)} disbursed.", f"/funding/agreements/{r.agreement_id}"),
        api("funding", "DisbursementSerializer"),
        submit="Disburse",
    ),
    Form(
        "funding-repay",
        "Record a repayment",
        "Funding and loans",
        "funding:collect",
        "Records a repayment; it is allocated to the oldest instalment first. The same reference is never counted "
        "twice.",
        (
            _target("Agreement", ch.funding_agreements),
            Field("amount_minor", "Amount (₦)", "money"),
            Field("method", "Method", "select", choices=ch.enum("repayment_method")),
            Field("reference", "Reference"),
            Field("received_on", "Received on", "date", required=False),
        ),
        lambda d: _funding().record_repayment(
            _u(d["target"]), d["amount_minor"], method=d["method"], reference=d["reference"], **_clean(d, "received_on")
        ),
        lambda r, _d: (f"Repayment of {ch.naira(r.amount_minor)} recorded.", f"/funding/agreements/{r.agreement_id}"),
        api("funding", "RepaymentSerializer"),
        submit="Record repayment",
    ),
    # ------------------------------------------------------------------ facilities (CR-006)
    Form(
        "estate-site",
        "Register a government property site",
        "Facilities",
        "estate:manage",
        "Records the land an institution uses: who owns it, the title document, area, fencing and any encroachment. "
        "New entries are marked 'to confirm' until checked against the land registry.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("site_code", "Site code", hint="e.g. MAIN, ANNEX"),
            Field("name", "Name", hint="e.g. Main campus"),
            Field("owner", "Owner", "select", choices=ch.enum("property_owner"), default="state_government"),
            Field("title_document", "Title held", "select", choices=ch.enum("land_title")),
            Field("title_reference", "Title reference", required=False),
            Field("area_sqm", "Area (square metres)", "number", required=False),
            Field("fenced", "Fencing", "select", choices=ch.enum("fence_status"), default="unknown"),
            Field("encroachment", "Encroachment", "select", choices=ch.enum("encroachment_status"), default="unknown"),
            Field("latitude", "Latitude", "number", required=False),
            Field("longitude", "Longitude", "number", required=False),
        ),
        _register_site,
        lambda r, _d: (f"Site {r.site_code} registered.", "/estate/property"),
        api("estate", "SiteSerializer"),
        _site_prepare,
        "Register site",
    ),
    Form(
        "estate-building",
        "Add a building",
        "Facilities",
        "estate:manage",
        "Adds a building to the institution's main campus. Add its rooms next.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("name", "Name", hint="e.g. Classroom block A"),
            Field("built_year", "Year built", "number", required=False),
        ),
        lambda d: _estate().add_building(_u(d["institution_id"]), d["name"], built_year=d.get("built_year")),
        lambda r, _d: (f"Building {r.name} added.", None),
        api("estate", "BuildingSerializer"),
        submit="Add building",
    ),
    Form(
        "estate-room",
        "Add a room",
        "Facilities",
        "estate:manage",
        "Adds a classroom, laboratory, toilet block or other room to a building.",
        (
            Field("building_id", "Building", "select", choices=ch.buildings),
            Field("code", "Room code", hint="e.g. A1"),
            Field("room_type", "Type", "select", choices=ch.code_list("room_type")),
            Field("capacity", "Capacity (people)", "number"),
            Field("name", "Name", required=False),
        ),
        lambda d: _estate().add_room(
            _u(d["building_id"]), d["code"], d["room_type"], d["capacity"], name=d.get("name") or None
        ),
        lambda r, _d: (f"Room {r.code} added.", None),
        api("estate", "RoomSerializer"),
        submit="Add room",
    ),
    Form(
        "estate-asset",
        "Add equipment",
        "Facilities",
        "estate:manage",
        "Records equipment that needs servicing or safety checks — generators, boreholes, solar systems, fire "
        "extinguishers, laboratory equipment. Service dates drive the proactive reminders.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("asset_tag", "Asset tag", hint="e.g. GEN-001"),
            Field("name", "Name", hint="e.g. 20 kVA generator"),
            Field("category", "Category", "select", choices=ch.code_list("asset_category")),
            Field("next_service_on", "Next service due", "date", required=False),
            Field("safety_check_due_on", "Next safety check due", "date", required=False),
            Field("value_minor", "Value (₦)", "money", required=False),
        ),
        lambda d: _estate().add_asset(
            _u(d["institution_id"]),
            d["asset_tag"],
            d["name"],
            d["category"],
            **_clean(d, "next_service_on", "safety_check_due_on", "value_minor"),
        ),
        lambda r, _d: (f"Equipment {r.asset_tag} added.", None),
        api("estate", "AssetSerializer"),
        submit="Add equipment",
    ),
    Form(
        "estate-assess",
        "Record a condition assessment",
        "Facilities",
        "estate:assess",
        "Records how usable a site, building, room or item of equipment is today. An unsafe facility still in use, "
        "or a major repair, raises an action for the head straight away.",
        (
            Field("facility", "Facility", "select", choices=ch.facilities),
            Field("condition_grade", "Condition", "select", choices=ch.code_list("condition_grade")),
            Field("usability", "Usability", "select", choices=ch.enum("usability_status")),
            Field("structural_risk", "Structural risk", "select", choices=ch.enum("severity"), default="info"),
            Field("in_use", "Still in use", "checkbox", required=False),
            Field("assessor_kind", "Assessed by", "select", choices=ch.enum("facility_assessor"), required=False),
            Field("learners_affected", "Learners affected", "number", required=False),
            Field("repair_estimate_minor", "Repair estimate (₦)", "money", required=False),
            Field("next_due_on", "Re-assess by", "date", required=False),
        ),
        _assess,
        lambda r, _d: ("Assessment recorded; the rules have been re-run.", "/estate"),
        api("estate", "AssessmentSerializer"),
        _facility_prepare,
        "Record assessment",
    ),
    Form(
        "estate-schedule",
        "Plan preventive maintenance",
        "Facilities",
        "estate:manage",
        "A repeating task — servicing a generator every 90 days, a fire-safety check every year. The task appears as "
        "an action when it falls due.",
        (
            Field("facility", "Facility", "select", choices=ch.facilities),
            Field("task", "Task", hint="e.g. Service 20 kVA generator"),
            Field("task_kind", "Kind", "select", choices=ch.enum("maintenance_task_kind")),
            Field("frequency_days", "Every (days)", "number"),
            Field("next_due_on", "Next due", "date"),
            Field("estimated_cost_minor", "Estimated cost (₦)", "money", required=False),
        ),
        lambda d: _estate().schedule_maintenance(
            d["subject_kind"],
            _u(d["subject_id"]),
            task=d["task"],
            task_kind=d["task_kind"],
            frequency_days=d["frequency_days"],
            next_due_on=d["next_due_on"],
            **_clean(d, "estimated_cost_minor"),
        ),
        lambda r, _d: (f"Planned: {r.task}, next due {r.next_due_on:%d %b %Y}.", "/estate"),
        api("estate", "ScheduleSerializer"),
        _facility_prepare,
        "Save plan",
    ),
    Form(
        "estate-done",
        "Mark planned maintenance done",
        "Facilities",
        "estate:act",
        "Records the task as done; a completed work order is kept and the next due date moves on.",
        (
            _target("Planned task", ch.maintenance_schedules),
            Field("done_on", "Done on", "date", required=False),
            Field("cost_minor", "Cost (₦)", "money", required=False),
            Field("note", "Note", "textarea", required=False),
        ),
        lambda d: _estate().complete_maintenance(_u(d["target"]), **_clean(d, "done_on", "cost_minor", "note")),
        lambda r, _d: (f"Done. Next due {r.next_due_on:%d %b %Y}.", "/estate"),
        api("estate", "CompleteSerializer"),
        submit="Mark done",
    ),
    Form(
        "estate-action",
        "Update a facility action",
        "Facilities",
        "estate:act",
        "Acknowledge an action, mark work started or done, or dismiss it with a reason.",
        (
            _target("Action", ch.open_facility_actions),
            Field(
                "status",
                "New status",
                "select",
                choices=ch.fixed(["acknowledged", "in_progress", "done", "dismissed"]),
            ),
            Field("note", "Note", "textarea", required=False, hint="Required (10+ characters) to dismiss."),
        ),
        lambda d: _estate().act(_u(d["target"]), d["status"], d.get("note") or None),
        lambda r, _d: (f"Action is now {ch.human(r.status).lower()}.", "/estate/actions"),
        api("estate", "ActSerializer"),
        submit="Update",
    ),
    Form(
        "estate-work-order",
        "Raise a work order",
        "Facilities",
        "estate:act",
        "Turns an action into a maintenance request (work order) with the action's priority and due date.",
        (_target("Action", ch.open_facility_actions),),
        lambda d: _estate().raise_work_order(_u(d["target"])),
        _ok("Work order raised.", "/estate/actions"),
        submit="Raise work order",
    ),
    # ------------------------------------------------------------------ examinations (EXM-01, EXM-03)
    Form(
        "exam-series",
        "Set up an examination series",
        "Examinations",
        "exam:manage",
        "An examination series is one set of papers sat together — the first-term examinations, a mock WASSCE, the "
        "BECE. Add its papers next, then enter the candidates and plan the sitting arrangements.",
        (
            Field("institution_id", "Institution", "select", choices=ch.institutions),
            Field("name", "Name", hint="e.g. First Term Examinations 2026/2027 — SS3"),
            Field("exam_body", "Set by", "select", choices=ch.code_list("exam_body"), default="INSTITUTION"),
            Field("entry_closes_on", "Entries close on", "date", required=False),
        ),
        lambda d: _exams().create_series(
            _u(d["institution_id"]), d["name"], exam_body=d["exam_body"], entry_closes_on=d.get("entry_closes_on")
        ),
        lambda r, _d: (f"Series {r.name} set up. Add its papers next.", f"/exams/series/{r.id}/sittings"),
        api("assessment", "SeriesSerializer"),
        submit="Set up series",
    ),
    Form(
        "exam-paper",
        "Add a paper",
        "Examinations",
        "exam:manage",
        "A paper of the series, with its code and how long it lasts.",
        (
            _target("Series", ch.exam_series),
            Field("paper_code", "Paper code", hint="e.g. MTH-SS3"),
            Field("title", "Title", hint="e.g. Mathematics (Paper 1: objective and theory)"),
            Field("duration_minutes", "Duration (minutes)", "number", default="120"),
        ),
        lambda d: _exams().add_paper(_u(d["target"]), d["paper_code"], d["title"], int(d["duration_minutes"])),
        lambda r, d: (f"Paper {r.paper_code} added.", f"/exams/series/{d['target']}/sittings"),
        api("assessment", "PaperSerializer"),
        submit="Add paper",
    ),
    Form(
        "exam-entries",
        "Enter candidates",
        "Examinations",
        "exam:manage",
        "Enters every learner in the chosen classes for the chosen papers. Each candidate gets a candidate number; "
        "learners already entered keep theirs.",
        (
            _target("Series", ch.exam_series),
            Field("class_ids", "Classes", "multi", choices=ch.classes, hint="Hold Ctrl (⌘ on Mac) to choose several."),
            Field("paper_codes", "Papers", "multi", choices=ch.exam_paper_codes),
        ),
        lambda d: _exams().enter_classes(_u(d["target"]), [_u(x) for x in d["class_ids"]], d["paper_codes"]),
        lambda r, d: (
            f"{r['entered']} candidates entered" + (f", {r['updated']} updated." if r["updated"] else "."),
            f"/exams/series/{d['target']}/sittings",
        ),
        api("assessment", "EntriesSerializer"),
        submit="Enter candidates",
    ),
    Form(
        "exam-sitting",
        "Plan the sitting arrangement",
        "Examinations",
        "exam:manage",
        "Seats every candidate entered for the paper across the halls you choose, mixing classes so that neighbours "
        "are from different classes, and shares out the invigilators — at least one per hall and one more for every "
        "further 30 candidates. A hall assessed unsafe, or already used by another paper at that time, is refused. "
        "Planning a paper again replaces its earlier arrangement.",
        (
            _target("Paper", ch.exam_papers),
            Field("room_ids", "Halls", "multi", choices=ch.exam_halls, hint="Hold Ctrl (⌘ on Mac) to choose several."),
            Field("starts_on", "Date", "date"),
            Field("starts_time", "Starts at", hint="24-hour time, e.g. 09:00"),
            Field(
                "spacing",
                "Spacing",
                "select",
                choices=ch.fixed(
                    ["alternate", "every_desk"],
                    {"alternate": "Alternate desks (no one directly beside another)", "every_desk": "Every desk"},
                ),
                default="alternate",
            ),
            Field("invigilator_staff_ids", "Invigilators", "multi", choices=ch.staff),
        ),
        _plan_sitting,
        _sitting_done,
        api("assessment", "SittingSerializer"),
        submit="Plan seating",
    ),
)

REGISTRY: dict[str, Form] = {f.key: f for f in FORMS}

# The catalogue page whose records each form writes. A form needs the same access level as that page (CR-007,
# FR-ADM-201), so a grant capped below it can neither see the form in /forms nor submit it.
FORM_PAGES: dict[str, str] = {
    "institution-register": "INS-03",
    "learner-transfer": "LRN-05",
    "class-create": "LRN-07",
    "class-member": "LRN-07",
    "certificate-reissue": "CER-101",
    "certificate-reissue-decision": "CER-102",
    "obligation-publish": "FCL-01",
    "obligation-dispute": "FCL-01",
    "obligation-dispute-resolve": "FCL-01",
    "coverage-evaluate": "CUR-101",
    "coverage-gap-accept": "CUR-103",
    "census-take": "FIN-01",
    "census-freeze": "FIN-01",
    "census-demand": "FIN-01",
    "hr-position": "HRM-01",
    "hr-appoint": "HRM-02",
    "hr-posting": "HRM-03",
    "hr-posting-decision": "HRM-03",
    "hr-separation": "HRM-07",
    "hr-leave": "HRM-04",
    "hr-leave-decision": "HRM-04",
    "hr-promotion": "HRM-05",
    "hr-promotion-decision": "HRM-05",
    "hr-relations": "HRM-06",
    "hr-integrity-scan": "HRM-08",
    "hr-integrity-hold": "HRM-08",
    "hr-payroll-run": "PAY-01",
    "hr-payroll-approve": "PAY-01",
    "regulation-link": "REG-02",
    "regulation-end": "REG-02",
    "federal-import": "FED-01",
    "security-intake": "STI-04",
    "security-trainee": "STI-04",
    "security-outcome": "STI-04",
    "budget-cost-centre": "FIN-01",
    "budget-prepare": "FIN-01",
    "budget-approve": "FIN-01",
    "budget-commit": "FIN-02",
    "budget-spend": "FIN-02",
    "budget-virement": "FIN-02",
    "budget-virement-decision": "FIN-02",
    "imprest-request": "ACC-01",
    "imprest-approve": "ACC-01",
    "imprest-retire": "ACC-01",
    "funding-apply": "FND-01",
    "funding-recommend": "FND-02",
    "funding-decide": "FND-02",
    "funding-sign": "FND-02",
    "funding-disburse": "FND-02",
    "funding-repay": "FND-02",
    "estate-site": "EST-01",
    "estate-building": "EST-01",
    "estate-room": "EST-01",
    "estate-asset": "EST-01",
    "estate-assess": "EST-02",
    "estate-schedule": "EST-02",
    "estate-done": "EST-02",
    "estate-action": "EST-02",
    "estate-work-order": "EST-02",
    "exam-series": "EXM-01",
    "exam-paper": "EXM-01",
    "exam-entries": "EXM-02",
    "exam-sitting": "EXM-03",
}


# Forms entered below their page's level, as pages are in ``pages.ENTRY_LEVEL``: the service still applies its own
# data-level checks. Obligation forms are mapped to FCL-01 (entered at confidential) for the same reason.
FORM_LEVEL: dict[str, str] = {
    "hr-payroll-approve": "confidential",  # the finance officer approves the run's totals; pay lines stay restricted
}


def level(form: Form) -> str:
    """The access level needed to use a form: that of the page it writes through (``internal`` when unmapped)."""
    from syntegra.web import pages

    if form.key in FORM_LEVEL:
        return FORM_LEVEL[form.key]
    page_id = FORM_PAGES.get(form.key)
    return pages.entry_level(page_id) if page_id else "internal"


def write_levels() -> dict[str, str]:
    """Each form permission's level (the highest of the forms that use it), for the API's writes (FR-ADM-203)."""
    from syntegra.core.context import class_rank

    out: dict[str, str] = {}
    for f in FORMS:
        lv = level(f)
        for p in (f.permission,) if isinstance(f.permission, str) else f.permission:
            if p not in out or class_rank(lv) > class_rank(out[p]):
                out[p] = lv
    return out


def require_level(form: Form, ctx: context.Context) -> None:
    from syntegra.core import access
    from syntegra.core.errors import Forbidden

    needed = access.level(level(form))
    if not access.covers(ctx.clearance, needed.classification):
        raise Forbidden(
            f"This form needs {needed.label}. Your access level in this role is {access.level(ctx.clearance).label}.",
            code="AUTH-LEVEL",
        )


def available(ctx: context.Context | None) -> dict[str, list[Form]]:
    """Forms the role may use, grouped by module, in declaration order."""
    out: dict[str, list[Form]] = {}
    for f in FORMS:
        if f.allowed(ctx):
            out.setdefault(f.module, []).append(f)
    return out


def today() -> str:
    return dt.date.today().isoformat()
