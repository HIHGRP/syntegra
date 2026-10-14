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

    def allowed(self, ctx: context.Context | None) -> bool:
        if ctx is None:
            return False
        perms = (self.permission,) if isinstance(self.permission, str) else self.permission
        return any(ctx.has(p) for p in perms)


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
)

REGISTRY: dict[str, Form] = {f.key: f for f in FORMS}


def available(ctx: context.Context | None) -> dict[str, list[Form]]:
    """Forms the role may use, grouped by module, in declaration order."""
    out: dict[str, list[Form]] = {}
    for f in FORMS:
        if f.allowed(ctx):
            out.setdefault(f.module, []).append(f)
    return out


def today() -> str:
    return dt.date.today().isoformat()
