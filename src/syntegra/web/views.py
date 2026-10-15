"""Server-rendered pages (MFS Part B). Pages call the same services as the API — no logic lives here."""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from syntegra.core import catalog, context
from syntegra.core.errors import DomainError, Forbidden, HardValidation, NotFound
from syntegra.web import pages

View = Callable[..., HttpResponse]


def _uuid_or_fail(value: object, what: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except ValueError as exc:
        raise HardValidation("PAGE-PARAM", f"Invalid {what}", f"Choose a {what} from the list.") from exc


def _ctx(request: HttpRequest, **extra: Any) -> dict[str, Any]:
    c = context.current(required=False)
    signed_in = c is not None and c.actor_kind == "user"
    user = None
    if signed_in:
        from syntegra.iam.models import AppUser

        user = AppUser.objects.filter(pk=c.actor_id).first()  # type: ignore[union-attr]
    return {
        "ctx": c,
        "signed_in": signed_in,
        "user": user,
        "tenant": getattr(request, "syntegra_tenant", None),
        "nav": pages.for_role(c.role_code if c else None),
        "page_status": pages.status,
        **extra,
    }


def page(page_id: str | None = None, *, public: bool = False) -> Callable[[View], View]:
    """Wrap a page: sign-in required unless public; domain errors render the problem page."""

    def deco(fn: View) -> View:
        @wraps(fn)
        def wrapper(request: HttpRequest, *args: Any, **kw: Any) -> HttpResponse:
            c = context.current(required=False)
            if not public and (c is None or c.actor_kind != "user"):
                return HttpResponseRedirect(f"/sign-in?next={request.path}")
            try:
                return fn(request, *args, **kw)
            except DomainError as exc:
                return render(
                    request,
                    "error.html",
                    _ctx(request, problem=exc.problem(), page=pages.page(page_id) if page_id else None),
                    status=exc.status,
                )

        return wrapper

    return deco


@require_http_methods(["GET", "POST"])
@page(public=True)
def sign_in(request: HttpRequest) -> HttpResponse:
    from syntegra.iam import services as iam

    error = None
    if request.method == "POST":
        try:
            c = context.require()
            r = iam.sign_in(
                getattr(request, "syntegra_tenant"),  # noqa: B009 — set by ContextMiddleware
                request.POST.get("username", ""),
                request.POST.get("password", ""),
                ip=c.ip,
                ua=c.user_agent,
            )
            nxt = _safe_next(request.GET.get("next"))
            if len(r.grants) > 1 and not r.mfa_required:  # several roles: choose the workspace first (AUT-03)
                nxt = f"/auth/context?{urlencode({'next': nxt})}"
            resp = HttpResponseRedirect(nxt)
            resp.set_cookie(
                settings.SESSION_COOKIE_NAME,
                r.token,
                httponly=True,
                samesite="Lax",
                secure=not settings.DEBUG,
                max_age=int(iam.SESSION_MAX.total_seconds()),
            )
            return resp
        except DomainError as exc:
            error = exc.detail or exc.title
    return render(request, "sign_in.html", _ctx(request, error=error), status=401 if error else 200)


@require_http_methods(["POST"])
@page()
def sign_out(request: HttpRequest) -> HttpResponse:
    from syntegra.core.middleware import session_token
    from syntegra.iam import services as iam

    token, _ = session_token(request)
    iam.sign_out(token or "")
    resp = HttpResponseRedirect("/sign-in")
    resp.delete_cookie(settings.SESSION_COOKIE_NAME)
    return resp


@page()
def home(request: HttpRequest) -> HttpResponse:
    from syntegra.analytics import metrics

    c = context.require()
    tiles = []
    if c.has("metric:view"):
        for mid in ("ENR-COUNT", "CUR-GAPS-OPEN"):
            try:
                m = metrics.compute(mid)
                tiles.append({"id": mid, "name": m["name"], "value": m["total_visible_n"], "cells": m["cells"][:8]})
            except DomainError:
                continue
    classes = []
    if c.has("attendance:mark"):
        from syntegra.academic.models import ClassGroup

        classes = list(ClassGroup.objects.in_scope().filter(status="active").order_by("name")[:30])
    return render(request, "home.html", _ctx(request, tiles=tiles, classes=classes))


@page()
def catalogue(request: HttpRequest) -> HttpResponse:
    rows = pages.all_pages()
    q = request.GET.get("q", "").lower()
    if q:
        rows = [p for p in rows if q in p["title"].lower() or q in p["id"].lower() or q in p["module"].lower()]
    live = sum(1 for p in pages.all_pages() if pages.status(p["id"]) == "live")
    return render(request, "catalogue.html", _ctx(request, rows=rows, q=q, live=live, total=len(pages.all_pages())))


def _allow_verify(ip: str | None) -> bool:
    """Same budget as the API's ``public_verify`` throttle (per client address, per hour)."""
    from django.core.cache import cache

    rates: Any = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES") or {}
    rate = str(rates.get("public_verify", "20/hour"))
    limit = int(rate.split("/")[0])
    key = f"syn:verify-page:{ip or '-'}:{dt.datetime.now(dt.UTC):%Y%m%d%H}"
    cache.add(key, 0, 3600)
    return int(cache.incr(key)) <= limit


@require_http_methods(["GET"])
@page("PUB-01", public=True)
def verify(request: HttpRequest) -> HttpResponse:
    from syntegra.certificates import services as certs

    q = (request.GET.get("number") or request.GET.get("code") or "").strip()
    if q and not _allow_verify(context.require().ip):
        return render(
            request,
            "error.html",
            _ctx(
                request,
                problem={
                    "title": "Too many checks",
                    "detail": "Please wait before verifying more certificates.",
                    "code": "RATE-LIMIT",
                },
                page=pages.page("PUB-01"),
            ),
            status=429,
        )
    result = certs.verify(q, channel="qr" if request.GET.get("via") == "qr" else "web_number") if q else None
    resp = render(request, "verify.html", _ctx(request, q=q, result=result, page=pages.page("PUB-01")))
    resp["Cache-Control"] = "no-store"
    return resp


@require_http_methods(["GET", "POST"])
@page("ATT-01")
def register(request: HttpRequest, class_id: uuid.UUID) -> HttpResponse:
    from syntegra.academic.models import ClassGroup
    from syntegra.attendance import services as att
    from syntegra.attendance.domain.rates import CODES
    from syntegra.learners.models import Learner

    c = context.require()
    if not c.has("attendance:view"):
        raise Forbidden()
    try:
        day = dt.date.fromisoformat(request.GET.get("date") or dt.date.today().isoformat())
    except ValueError as exc:
        raise HardValidation("PAGE-PARAM", "Invalid date", "date must be YYYY-MM-DD") from exc
    reg = att.open_register(class_id, day)
    message = None
    if request.method == "POST":
        marks = []
        for key, code in request.POST.items():
            code = str(code)
            if key.startswith("mark_") and code:
                lid = _uuid_or_fail(key[5:], "learner")
                late = request.POST.get(f"late_{lid}")
                if late and not late.isdigit():
                    raise HardValidation("ATT-LATE", "Invalid minutes late", "Enter whole minutes.")
                marks.append(
                    att.Mark(
                        learner_id=lid,
                        code=code,
                        minutes_late=int(late) if late and code == "L" else None,
                        client_op_id=uuid.uuid5(reg.id, f"{lid}:{code}:{late}"),
                    )
                )
        rv = request.POST.get("row_version", "0")
        r = att.submit(reg.id, marks, if_match=int(rv) if rv.isdigit() and int(rv) else None)
        message = f"Saved: {r['created']} new, {r['corrected']} corrected. Register {r['status'].replace('_', ' ')}."
    view = att.register_view(reg.id)
    names = {lr.id: lr for lr in Learner.objects.filter(id__in=[m.learner_id for m in view["roster"]])}
    roster = sorted(
        view["roster"], key=lambda m: (names[m.learner_id].legal_family_name, names[m.learner_id].legal_given_name)
    )
    cls = ClassGroup.objects.get(pk=class_id)
    return render(
        request,
        "register.html",
        _ctx(
            request,
            reg=view["register"],
            cls=cls,
            roster=roster,
            names=names,
            marks=view["marks"],
            codes=CODES,
            day=day,
            message=message,
            page=pages.page("ATT-01"),
        ),
    )


POST_SECONDARY = (
    "technical_college",
    "college_of_education",
    "polytechnic",
    "monotechnic",
    "university",
    "school_of_nursing",
    "school_of_health_technology",
)
LEVELS = catalog.code_list("education_level")


def _guardians_from_form(f: Any) -> list[Any]:
    """Guardian blocks g1_* and g2_* of the registration form; an untouched block is ignored."""
    from syntegra.families.services import GuardianInput

    out = []
    for n in (1, 2):
        p = f"g{n}_"
        if not any((f.get(p + k) or "").strip() for k in ("given", "family", "phone", "email", "nin")):
            continue
        out.append(
            GuardianInput(
                given=f.get(p + "given", ""),
                family=f.get(p + "family", ""),
                relationship=f.get(p + "relationship", ""),
                title=f.get(p + "title") or None,
                phone=f.get(p + "phone") or None,
                email=f.get(p + "email") or None,
                nin=f.get(p + "nin") or None,
                has_parental_responsibility=bool(f.get(p + "responsibility")),
                lives_with=bool(f.get(p + "lives_with")),
                is_authorised_collector=bool(f.get(p + "collector")),
                is_payer=bool(f.get(p + "payer")),
            )
        )
    return out


@require_http_methods(["GET", "POST"])
@page("LRN-02")
def learner_new(request: HttpRequest) -> HttpResponse:
    """Register a learner: identity matching, then fee clearance across every state on the network, then enrolment."""
    from syntegra.academic.models import Programme
    from syntegra.clearance.models import ClearanceCheck, ClearanceDecision
    from syntegra.clearance.services import AdmissionDeferred, ClearanceDecisionRequired, DecisionInput
    from syntegra.core.errors import HardValidation, SoftWarning
    from syntegra.families import services as families
    from syntegra.families.domain.guardians import RELATIONSHIPS
    from syntegra.institutions.models import Institution
    from syntegra.learners import services as lrn
    from syntegra.learners.models import Enrolment
    from syntegra.platform.states import STATES

    c = context.require()
    if not c.has("learner:register"):
        raise Forbidden()
    institutions = list(Institution.objects.in_scope().filter(status="active").order_by("name")[:200])
    names = {i.id: i.name for i in institutions}
    programmes = [
        {"id": str(p.id), "institution_id": str(p.institution_id), "label": f"{p.name} ({p.code})"}
        for p in Programme.objects.filter(
            institution_id__in=list(names), status__in=("approved", "published")
        ).order_by("name")
    ]
    f = request.POST if request.method == "POST" else {}
    errors: dict[str, str] = {}
    out: dict[str, Any] = {}
    if request.method == "POST":
        dob = None
        try:
            dob = dt.date.fromisoformat(f.get("date_of_birth", ""))
        except ValueError:
            errors["date_of_birth"] = "enter the date of birth"
        start_on = None
        if f.get("start_on"):
            try:
                start_on = dt.date.fromisoformat(f["start_on"])
            except ValueError:
                errors["start_on"] = "enter a valid date"
        if not f.get("institution_id"):
            errors["institution_id"] = "choose the admitting institution"
        if not errors and dob is not None:
            data = lrn.RegisterLearner(
                given=f.get("given", ""),
                middle=f.get("middle") or None,
                family=f.get("family", ""),
                preferred_name=f.get("preferred_name") or None,
                date_of_birth=dob,
                dob_precision=f.get("dob_precision", "day"),
                sex=f.get("sex", ""),
                nin=f.get("nin") or None,
                nationality=f.get("nationality") or "NG",
                state_of_origin=f.get("state_of_origin") or None,
                institution_id=uuid.UUID(f["institution_id"]),
                education_level=f.get("education_level", ""),
                start_on=start_on,
                is_minimal_documentation=bool(f.get("is_minimal_documentation")),
                guardians=_guardians_from_form(f),
                programme_id=uuid.UUID(f["programme_id"]) if f.get("programme_id") else None,
                cohort_label=f.get("cohort_label") or None,
                identifiers={s: f[k] for s, k in (("JAMB-REG", "jamb_reg"), ("INST-ID", "matric_no")) if f.get(k)},
            )
            decision = None
            if f.get("decision"):
                decision = DecisionInput(
                    decision=f["decision"],
                    reason=f.get("decision_reason", ""),
                    check_id=uuid.UUID(f["check_id"]) if f.get("check_id") else None,
                    protected_reason=f.get("protected_reason") or None,
                    payment_plan_ref=f.get("payment_plan_ref") or None,
                )
            try:
                reg = lrn.register(data, override_reason=f.get("override_reason") or None, clearance=decision)
                out["registration"] = reg
                chk = ClearanceCheck.objects.filter(learner_id=reg.learner.id).order_by("-checked_at").first()
                out["check"] = chk
                pid = reg.enrolment.programme_id if reg.enrolment else None
                out["programme"] = Programme.objects.filter(pk=pid).first() if pid else None
                out["decision"] = ClearanceDecision.objects.filter(check_id=chk.id).first() if chk else None
                # A record created moments earlier while the clearance decision was pending is new to this state.
                out["new_here"] = (
                    reg.outcome == "created" or Enrolment.objects.filter(learner_id=reg.learner.id).count() == 1
                )
            except SoftWarning as exc:
                out["probable"] = exc.problem()
            except ClearanceDecisionRequired as exc:
                out["clearance"] = exc.problem()
            except AdmissionDeferred:
                out["deferred"] = True
            except HardValidation as exc:
                for e in exc.errors or [{"field": None, "message": exc.detail or exc.title}]:
                    errors.setdefault(str(e.get("field") or "form"), str(e["message"]))
            except DomainError as exc:  # e.g. already enrolled elsewhere: shown on the form, values kept
                errors["form"] = f"{exc.title}: {exc.detail}" if exc.detail else exc.title
    return render(
        request,
        "learner_new.html",
        _ctx(
            request,
            f=f,
            errors=errors,
            institutions=institutions,
            levels=LEVELS,
            states=STATES,
            relationships=RELATIONSHIPS,
            programmes=programmes,
            post_secondary=[str(i.id) for i in institutions if i.category in POST_SECONDARY],
            majority=families.majority_age(institutions[0].scope_node_id if institutions else None),
            today=dt.date.today().isoformat(),
            page=pages.page("LRN-02"),
            **out,
        ),
    )


@page("LRN-04")
def learner(request: HttpRequest, learner_id: uuid.UUID) -> HttpResponse:
    from syntegra.academic.models import Programme
    from syntegra.attendance import services as att
    from syntegra.families import services as families
    from syntegra.institutions.models import Institution
    from syntegra.learners import services as lrn

    c = context.require()
    if not c.has("learner:view"):
        raise Forbidden()
    learner_ = lrn.get(learner_id)
    enrolments = lrn.enrolments(learner_id)
    insts = {i.id: i for i in Institution.objects.filter(id__in=[e.institution_id for e in enrolments])}
    today = dt.date.today()
    attendance = (
        att.learner_summary(learner_id, today - dt.timedelta(days=90), today) if c.has("attendance:view") else None
    )
    return render(
        request,
        "learner.html",
        _ctx(
            request,
            learner=learner_,
            enrolments=enrolments,
            insts=insts,
            attendance=attendance,
            guardians=families.guardians_of(learner_id),
            identifiers=lrn.identifiers_of(learner_id),
            programmes={
                p.id: p for p in Programme.objects.filter(id__in=[e.programme_id for e in enrolments if e.programme_id])
            },
            page=pages.page("LRN-04"),
        ),
    )


@page("CUR-101")
def coverage(request: HttpRequest) -> HttpResponse:
    from syntegra.curriculum import services as cov
    from syntegra.institutions.models import Institution

    gaps = cov.open_gaps()
    insts = {i.id: i for i in Institution.objects.filter(id__in={g.institution_id for g in gaps})}
    return render(
        request,
        "coverage.html",
        _ctx(request, gaps=gaps, insts=insts, today=dt.date.today(), page=pages.page("CUR-101")),
    )


@require_http_methods(["GET", "POST"])
@page("FCL-01")
def clearance(request: HttpRequest) -> HttpResponse:
    """Admissions desk: run the fee-clearance check for an incoming learner and record the human decision."""
    from syntegra.clearance import services as fcl
    from syntegra.clearance.models import ClearanceCheck, ClearanceDecision
    from syntegra.institutions.models import Institution
    from syntegra.learners.models import Learner

    c = context.require()
    if not c.has("clearance:check"):
        raise Forbidden()
    institutions = list(Institution.objects.in_scope().filter(status="active").order_by("name")[:50])
    chk = decision = learner = None
    message = None
    if request.method == "POST" and request.POST.get("check_id"):
        chk = ClearanceCheck.objects.filter(pk=_uuid_or_fail(request.POST["check_id"], "check")).first()
        if chk is None:
            raise NotFound("clearance check", request.POST["check_id"])
        decision = fcl.decide(
            chk.id,
            fcl.DecisionInput(
                decision=request.POST.get("decision", ""),
                reason=request.POST.get("reason", ""),
                protected_reason=request.POST.get("protected_reason") or None,
                payment_plan_ref=request.POST.get("payment_plan_ref") or None,
            ),
        )
        learner = Learner.objects.get(pk=chk.learner_id)
        message = "Decision recorded. Continue the admission or transfer."
    elif request.method == "POST":
        learner = Learner.objects.filter(global_learner_id=request.POST.get("glid", "").strip().upper()).first()
        if learner is None:
            message = "No learner with that Global Learner ID in this state."
        else:
            chk = fcl.check(
                learner.id,
                _uuid_or_fail(request.POST.get("institution_id"), "institution"),
                purpose=request.POST.get("purpose", "admission"),
                education_level=request.POST.get("education_level", ""),
            )
            decision = ClearanceDecision.objects.filter(check_id=chk.id).first()
    return render(
        request,
        "clearance.html",
        _ctx(
            request,
            institutions=institutions,
            chk=chk,
            decision=decision,
            learner=learner,
            message=message,
            page=pages.page("FCL-01"),
        ),
    )


@page("FCL-04")
def clearance_network(request: HttpRequest) -> HttpResponse:
    """National clearance network: every state registry, its status and this state's traffic with it (CR-002)."""
    from syntegra.clearance import federation

    data = federation.network_status()
    return render(request, "clearance_network.html", _ctx(request, data=data, page=pages.page("FCL-04")))


@page("HRM-01")
def establishment(request: HttpRequest) -> HttpResponse:
    from syntegra.hr import establishment as est
    from syntegra.institutions.models import Institution

    c = context.require()
    if not c.has("hr:view"):
        raise Forbidden()
    institutions = list(Institution.objects.in_scope().filter(status="active").order_by("name")[:200])
    chosen = request.GET.get("institution_id") or (str(institutions[0].id) if institutions else None)
    data = est.establishment(_uuid_or_fail(chosen, "institution")) if chosen else None
    return render(
        request,
        "establishment.html",
        _ctx(request, institutions=institutions, chosen=chosen, data=data, page=pages.page("HRM-01")),
    )


# --------------------------------------------------------------------------- security agencies' training (CR-004)
@page("STI-01")
def security_training(request: HttpRequest) -> HttpResponse:
    from syntegra.security_training import services as sti

    data = sti.directory()
    q = request.GET.get("category", "")
    shown = [a for a in data if not q or a["category"] == q]
    return render(
        request,
        "security_training.html",
        _ctx(
            request,
            agencies=shown,
            categories=sorted({a["category"] for a in data}),
            category=q,
            page=pages.page("STI-01"),
        ),
    )


@page("STI-01")
def security_agency(request: HttpRequest, agency_id: uuid.UUID) -> HttpResponse:
    from syntegra.security_training import services as sti

    return render(request, "security_agency.html", _ctx(request, a=sti.agency(agency_id), page=pages.page("STI-01")))


@page("STI-02")
def security_institution(request: HttpRequest, institution_id: uuid.UUID) -> HttpResponse:
    from syntegra.security_training import services as sti

    return render(
        request,
        "security_institution.html",
        _ctx(request, i=sti.institution(institution_id), page=pages.page("STI-02")),
    )


@page("STI-03")
def security_course(request: HttpRequest, course_id: uuid.UUID) -> HttpResponse:
    from syntegra.security_training import services as sti

    return render(request, "security_course.html", _ctx(request, c=sti.course(course_id), page=pages.page("STI-03")))


@page("STI-04")
def security_intake(request: HttpRequest, intake_id: uuid.UUID) -> HttpResponse:
    from syntegra.security_training import services as sti

    return render(request, "security_intake.html", _ctx(request, t=sti.intake(intake_id), page=pages.page("STI-04")))


# ------------------------------------------------------------------------- federal institutions and watchdogs (CR-005)
@page("FED-01")
def federal_institutions(request: HttpRequest) -> HttpResponse:
    from syntegra.federal_institutions import services as fed

    q = request.GET
    data = fed.directory(body=q.get("body") or None, zone=q.get("zone") or None, institution_type=q.get("type") or None)
    zones = ["north_central", "north_east", "north_west", "south_east", "south_south", "south_west"]
    return render(
        request, "federal_institutions.html", _ctx(request, data=data, zones=zones, q=q, page=pages.page("FED-01"))
    )


@page("REG-01", public=True)
def regulators(request: HttpRequest) -> HttpResponse:
    from syntegra.regulation import services as reg

    return render(request, "regulators.html", _ctx(request, data=reg.directory(), page=pages.page("REG-01")))


@page("REG-02")
def institution_regulation(request: HttpRequest, institution_id: uuid.UUID) -> HttpResponse:
    from syntegra.regulation import services as reg

    return render(
        request, "institution_regulation.html", _ctx(request, p=reg.profile(institution_id), page=pages.page("REG-02"))
    )


# ------------------------------------------------------------------------------------- forms for every write action
@page()
def forms_hub(request: HttpRequest) -> HttpResponse:
    from syntegra.web import forms

    return render(request, "forms/hub.html", _ctx(request, groups=forms.available(context.current(required=False))))


@require_http_methods(["GET", "POST"])
@page()
def form_page(request: HttpRequest, key: str) -> HttpResponse:
    """One form: GET shows it (values may be prefilled from the query string, e.g. ``?target=<id>``); POST
    validates with the API serializer, calls the service and shows the outcome beside the fields."""
    from syntegra.web import forms

    form = forms.REGISTRY.get(key)
    if form is None:
        raise NotFound("form", key)
    if not form.allowed(context.require()):
        raise Forbidden()
    posted = request.method == "POST"
    params = request.POST if posted else request.GET
    opts = forms.options(form, params)
    outcome = forms.submit(form, request.POST, request.FILES, opts) if posted else forms.Outcome()
    keep = posted and bool(outcome.errors)
    values: dict[str, Any] = {}
    for f in form.fields:
        if keep:
            values[f.name] = params.getlist(f.name) if f.kind == "multi" else params.get(f.name, "")
        elif f.kind == "hidden" or not posted:
            src = request.GET if not posted or f.kind != "hidden" else request.POST
            values[f.name] = src.getlist(f.name) if f.kind == "multi" else src.get(f.name, f.default)
        else:
            values[f.name] = [] if f.kind == "multi" else f.default
    nothing = any(f.name == "target" and not opts.get("target") for f in form.fields)
    return render(
        request,
        "forms/form.html",
        _ctx(
            request,
            form=form,
            opts=opts,
            values=values,
            outcome=outcome,
            nothing=nothing,
            multipart=any(f.kind == "file" for f in form.fields),
            today=dt.date.today().isoformat(),
        ),
        status=422 if outcome.errors else 200,
    )


# ------------------------------------------------------------------------------------- workspace (role) chooser
def _safe_next(value: str | None) -> str:
    return value if value and value.startswith("/") and not value.startswith("//") else "/"


@require_http_methods(["GET", "POST"])
@page("AUT-03")
def workspace(request: HttpRequest) -> HttpResponse:
    """AUT-03: choose which role-at-scope grant the session acts under."""
    from syntegra.core.middleware import session_token
    from syntegra.governance.models import ScopeNode
    from syntegra.iam import services as iam
    from syntegra.iam.models import AppUser

    c = context.require()
    user = AppUser.objects.get(pk=c.actor_id)
    grants = iam.user_grants(user)
    nodes = {str(n.id): n for n in ScopeNode.objects.filter(id__in=[g["scope_id"] for g in grants])}
    error = None
    if request.method == "POST":
        chosen = request.POST.get("grant_id", "")
        if chosen not in {str(g["grant_id"]) for g in grants}:
            error = "Choose one of your roles."
        else:
            token, _ = session_token(request)
            iam.select_grant(token or "", uuid.UUID(chosen))
            return HttpResponseRedirect(_safe_next(request.GET.get("next")))
    return render(
        request,
        "workspace.html",
        _ctx(
            request,
            grants=grants,
            nodes=nodes,
            active=str(c.grant_id) if c.grant_id else None,
            error=error,
            next=_safe_next(request.GET.get("next")),
            page=pages.page("AUT-03"),
        ),
        status=422 if error else 200,
    )


# ---------------------------------------------------------------------------------- command centre (CMD-101, CMD-102)
@page("CMD-101")
def control_room(request: HttpRequest) -> HttpResponse:
    """The state education control room: headline figures, the best school and learner, LGAs and schools compared."""
    from syntegra.analytics import performance

    data = performance.performance()
    return render(request, "control_room.html", _ctx(request, d=data, page=pages.page("CMD-101")))


@page("CMD-102")
def league(request: HttpRequest) -> HttpResponse:
    """Institution league with context: ranked only within comparison groups, filterable by LGA."""
    from syntegra.analytics import performance

    data = performance.performance()
    group = request.GET.get("group") if request.GET.get("group") in performance.GROUPS else "secondary"
    lga = request.GET.get("lga", "")
    rows = [r for r in data["league"][group] if not lga or r["lga"] == lga]
    lgas = sorted({r["lga"] for g in data["league"].values() for r in g if r["lga"]})
    return render(
        request,
        "league.html",
        _ctx(
            request,
            d=data,
            rows=rows,
            group=group,
            groups=performance.GROUP_LABEL,
            lga=lga,
            lgas=lgas,
            best=data["best_learners"].get(group, []),
            page=pages.page("CMD-102"),
        ),
    )


# ---------------------------------------------------------------- budgets, funding and facilities (CR-006)
def _institution_choice(request: HttpRequest) -> tuple[list[Any], str | None]:
    from syntegra.institutions.models import Institution

    institutions = list(Institution.objects.in_scope().filter(status="active").order_by("name")[:500])
    chosen = request.GET.get("institution_id") or (str(institutions[0].id) if len(institutions) == 1 else None)
    return institutions, chosen


@page("FIN-02")
def budget_execution(request: HttpRequest) -> HttpResponse:
    """Budget against actual: original, revised, committed, spent and available per line, with execution."""
    from syntegra.finance import budgets

    institutions, chosen = _institution_choice(request)
    year = request.GET.get("fiscal_year", "")
    data = budgets.execution(
        institution_id=_uuid_or_fail(chosen, "institution") if chosen else None,
        fiscal_year=int(year) if year.isdigit() else None,
    )
    return render(
        request,
        "budget_execution.html",
        _ctx(request, d=data, institutions=institutions, chosen=chosen, page=pages.page("FIN-02")),
    )


@page("ACC-01")
def imprest(request: HttpRequest) -> HttpResponse:
    from syntegra.core import catalog
    from syntegra.finance import budgets

    status = request.GET.get("status") or None
    if status not in (None, *catalog.enum_values("imprest_status")):
        status = None
    rows = budgets.imprest_register(status=status)
    statuses = catalog.enum_values("imprest_status")
    return render(
        request,
        "imprest.html",
        _ctx(request, rows=rows, status=status or "", statuses=statuses, page=pages.page("ACC-01")),
    )


@page("FND-01")
def funding(request: HttpRequest) -> HttpResponse:
    from syntegra.funding import services as fnd

    kind = request.GET.get("for", "")
    data = fnd.overview()
    shown = [p for p in data["programmes"] if not kind or p["beneficiary_kind"] == kind]
    return render(
        request, "funding.html", _ctx(request, d=data, programmes=shown, kind=kind, page=pages.page("FND-01"))
    )


@page("FND-02")
def funding_agreement(request: HttpRequest, agreement_id: uuid.UUID) -> HttpResponse:
    from syntegra.funding import services as fnd

    return render(
        request, "funding_agreement.html", _ctx(request, a=fnd.agreement(agreement_id), page=pages.page("FND-02"))
    )


@page("EST-01")
def property_register(request: HttpRequest) -> HttpResponse:
    from syntegra.estate import services as est

    rows = est.property_register()
    return render(request, "property_register.html", _ctx(request, rows=rows, page=pages.page("EST-01")))


@page("EST-02")
def facility_actions(request: HttpRequest) -> HttpResponse:
    from syntegra.estate import services as est

    status = request.GET.get("status", "open")
    status = status if status in ("open", "done", "dismissed") else "open"
    rows = est.actions_in_scope(status=status)
    return render(request, "facility_actions.html", _ctx(request, rows=rows, status=status, page=pages.page("EST-02")))


@page("EST-03")
def infrastructure(request: HttpRequest) -> HttpResponse:
    """The Commissioner's holistic view of school infrastructure, from the data warehouse (drill down by scope)."""
    from syntegra.analytics import warehouse

    scope = request.GET.get("scope_id")
    data = warehouse.state_overview(_uuid_or_fail(scope, "area") if scope else None)
    return render(request, "infrastructure.html", _ctx(request, d=data, page=pages.page("EST-03")))


@page("OPS-01")
def facilities(request: HttpRequest) -> HttpResponse:
    """The head's facilities workspace: sites, buildings, rooms, equipment, the maintenance plan and open actions."""
    from syntegra.estate import services as est

    institutions, chosen = _institution_choice(request)
    data = est.workspace(_uuid_or_fail(chosen, "institution")) if chosen else None
    return render(
        request,
        "facilities.html",
        _ctx(request, w=data, institutions=institutions, chosen=chosen, page=pages.page("OPS-01")),
    )


@page("STI-05")
def security_careers(request: HttpRequest, agency_id: uuid.UUID) -> HttpResponse:
    from syntegra.security_training import services as sti

    return render(request, "security_careers.html", _ctx(request, c=sti.careers(agency_id), page=pages.page("STI-05")))


# ----------------------------------------------------------------------------------- examinations (EXM-01, EXM-03)
@page("EXM-01")
def exam_series(request: HttpRequest) -> HttpResponse:
    from syntegra.assessment import exams

    return render(request, "exams.html", _ctx(request, rows=exams.series_list(), page=pages.page("EXM-01")))


@page("EXM-03")
def exam_seating(request: HttpRequest, series_id: uuid.UUID) -> HttpResponse:
    """Timetable and sitting arrangements: each paper's halls with their seat charts and seating lists."""
    from syntegra.assessment import exams

    return render(
        request, "exam_seating.html", _ctx(request, d=exams.arrangements(series_id), page=pages.page("EXM-03"))
    )


# ------------------------------------------------------------------------------- classroom seating plans (BEH-102)
@require_http_methods(["GET", "POST"])
@page("BEH-102")
def seating(request: HttpRequest, class_id: uuid.UUID) -> HttpResponse:
    """Seating plan: generate by strategy, rearrange by drag and drop, board-safe view, logged watermarked print."""
    import json

    from syntegra.success import arrange
    from syntegra.success import seating_plans as sp

    message, problem = None, None
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "generate":
                room = request.POST.get("room_id") or None
                sp.generate(
                    class_id,
                    strategy=request.POST.get("strategy", ""),
                    style=request.POST.get("style", "pairs"),
                    room_id=_uuid_or_fail(room, "classroom") if room else None,
                )
                message = "New seating plan made."
            elif action == "save":
                try:
                    placements = json.loads(request.POST.get("placements") or "{}")
                except ValueError as exc:
                    raise HardValidation("SEAT-PLACEMENTS", "The arrangement could not be read", "") from exc
                if not isinstance(placements, dict):
                    raise HardValidation("SEAT-PLACEMENTS", "The arrangement could not be read", "")
                sp.save_manual(
                    _uuid_or_fail(request.POST.get("plan_id"), "plan"), {str(k): str(v) for k, v in placements.items()}
                )
                message = "Your arrangement is saved."
            elif action == "print":
                pr = sp.log_print(
                    _uuid_or_fail(request.POST.get("plan_id"), "plan"), request.POST.get("viewer_name", "")
                )
                data = sp.plan_view(class_id)
                return render(request, "seating_print.html", _ctx(request, d=data, pr=pr, page=pages.page("BEH-102")))
        except HardValidation as exc:
            problem = exc.problem()
    board = request.GET.get("view") == "board"
    data = sp.plan_view(class_id, board=board)
    if board:
        return render(request, "seating_board.html", _ctx(request, d=data, page=pages.page("BEH-102")))
    return render(
        request,
        "seating.html",
        _ctx(
            request,
            d=data,
            rooms=sp.rooms(class_id),
            strategies=[s for s in arrange.STRATEGIES if s != "manual"],
            styles=sp.STYLE_LABEL,
            message=message,
            problem=problem,
            page=pages.page("BEH-102"),
        ),
        status=422 if problem else 200,
    )
