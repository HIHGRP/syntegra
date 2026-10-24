"""Server-rendered pages (MFS Part B). Pages call the same services as the API — no logic lives here."""

from __future__ import annotations

import datetime as dt
import re
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_sameorigin
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
    from syntegra.core import access

    c = context.current(required=False)
    signed_in = c is not None and c.actor_kind == "user"
    user = None
    sess = getattr(request, "syntegra_session", None) if signed_in else None
    refused = 0
    if signed_in:
        from syntegra.iam import services as iam
        from syntegra.iam.models import AppUser

        user = AppUser.objects.filter(pk=c.actor_id).first()  # type: ignore[union-attr]
        if sess is not None:
            refused = iam.refused_attempts(sess)
    return {
        "ctx": c,
        "signed_in": signed_in,
        "user": user,
        "session": sess,
        "refused_sign_ins": refused,
        "my_level": access.level(c.clearance) if signed_in and c is not None and c.grant_id else None,
        "can_open": lambda pid: signed_in and c is not None and access.covers(c.clearance, pages.entry_level(pid)),
        "tenant": getattr(request, "syntegra_tenant", None),
        "government_office": _government_office(sess),
        "nav": pages.for_role(c.role_code if c else None),
        "page_status": pages.status,
        **extra,
    }


def _government_office(sess: Any) -> bool:
    """Whether the user signed in for a government office (a ministry, board or LGA office) rather than a school."""
    if sess is None or not getattr(sess, "affiliation_scope_id", None):
        return False
    from syntegra.governance.models import ScopeNode

    node = ScopeNode.objects.filter(pk=sess.affiliation_scope_id).only("ref_kind").first()
    return node is not None and node.ref_kind != "institution"


def _signed_out_redirect(request: HttpRequest) -> HttpResponse:
    """To the sign-in page, saying why when the session behind the cookie has ended (FR-AUT-102)."""
    from syntegra.core.middleware import session_token
    from syntegra.iam import services as iam

    q = {"next": request.get_full_path()}
    token, from_cookie = session_token(request)
    reason = iam.end_reason(token) if from_cookie else None
    if reason and reason != "signed_out":
        q["ended"] = reason
    resp = HttpResponseRedirect(f"/sign-in?{urlencode(q)}")
    if reason:
        resp.delete_cookie(settings.SESSION_COOKIE_NAME)
    return resp


def _check_level(page_id: str) -> None:
    """Refuse a page above the active grant's access level (CR-007, FR-ADM-201)."""
    from syntegra.core import access

    c = context.require()
    needed = access.level(pages.entry_level(page_id))
    if not access.covers(c.clearance, needed.classification):
        raise Forbidden(
            f"This page needs {needed.label}. Your access level in this role is {access.level(c.clearance).label}.",
            code="AUTH-LEVEL",
        )


def page(
    page_id: str | None = None, *, public: bool = False, confirm: bool = True, mfa: bool = True
) -> Callable[[View], View]:
    """Wrap a page: sign-in required unless public; the second factor must have been entered when the account has
    one (``mfa=False`` only for the code page itself and sign-out); the school or office must have been confirmed
    after the password (``confirm=False`` only for the confirmation page, the code page and sign-out); the page's
    access level is enforced; domain errors render the problem page."""

    def deco(fn: View) -> View:
        @wraps(fn)
        def wrapper(request: HttpRequest, *args: Any, **kw: Any) -> HttpResponse:
            c = context.current(required=False)
            if not public and (c is None or c.actor_kind != "user"):
                return _signed_out_redirect(request)
            sess = getattr(request, "syntegra_session", None)
            if not public and mfa and sess is not None and getattr(sess, "mfa_pending", False):
                return HttpResponseRedirect(f"/auth/mfa?{urlencode({'next': request.get_full_path()})}")
            if not public and mfa and sess is not None and getattr(sess, "mfa_setup_pending", False):
                return HttpResponseRedirect(f"/me/authenticator?{urlencode({'next': request.get_full_path()})}")
            if (
                not public
                and confirm
                and sess is not None
                and getattr(request, "syntegra_token_cookie", False)
                and sess.affiliation_confirmed_at is None
            ):
                return HttpResponseRedirect(f"/auth/context?{urlencode({'next': request.get_full_path()})}")
            try:
                if not public and page_id:
                    _check_level(page_id)
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


ENDED_MESSAGES = {
    "replaced": "You were signed out because your account signed in on another device.",
    "ended_by_administrator": "An administrator ended your session.",
    "idle_timeout": "You were signed out after a period of inactivity.",
    "expired": "Your session expired. Please sign in again.",
    "account_inactive": "This account can no longer sign in. Contact your administrator.",
}


@require_http_methods(["GET", "POST"])
@page(public=True)
def sign_in(request: HttpRequest) -> HttpResponse:
    from syntegra.iam import services as iam

    error = None
    notice = ENDED_MESSAGES.get(request.GET.get("ended", ""))
    if request.method == "POST":
        from syntegra.core.middleware import session_token

        try:
            c = context.require()
            current, _ = session_token(request)
            r = iam.sign_in(
                getattr(request, "syntegra_tenant"),  # noqa: B009 — set by ContextMiddleware
                request.POST.get("username", ""),
                request.POST.get("password", ""),
                ip=c.ip,
                ua=c.user_agent,
                current_token=current,
            )
            # then the code from the authenticator app (AUT-02) when the account has one, then confirm the school or
            # office (and the role, when there are several) — AUT-03
            return _after_sign_in(r, request.GET.get("next") or "/")
        except DomainError as exc:
            error = exc.detail or exc.title
            in_use = exc.code == "AUTH-SESSION-IN-USE"
            return render(
                request,
                "sign_in.html",
                _ctx(request, error=error, in_use=in_use, providers=_sso_buttons(request)),
                status=exc.status if in_use else 401,
            )
    return render(request, "sign_in.html", _ctx(request, error=error, notice=notice, providers=_sso_buttons(request)))


def _sso_buttons(request: HttpRequest) -> list[Any]:
    from syntegra.iam import sso

    tenant = getattr(request, "syntegra_tenant", None)
    return sso.enabled(tenant) if tenant is not None else []


def _after_sign_in(r: Any, nxt: str) -> HttpResponse:
    """Where the browser goes after the password or the provider: the code, or enrolment, then the school or office
    (AUT-03); the session cookie is set here."""
    from syntegra.iam import services as iam

    target = f"/auth/context?{urlencode({'next': _safe_next(nxt)})}"
    if r.mfa_required:
        target = f"/auth/mfa?{urlencode({'next': target})}"
    elif r.mfa_setup_required:  # roles that need a second factor, and none set up yet (FR-AUT-104)
        target = f"/me/authenticator?{urlencode({'next': target})}"
    resp = HttpResponseRedirect(target)
    resp.set_cookie(
        settings.SESSION_COOKIE_NAME,
        r.token,
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,
        max_age=int(iam.SESSION_MAX.total_seconds()),
    )
    return resp


@require_http_methods(["GET"])
@page(public=True)
def sso_start(request: HttpRequest, provider: str) -> HttpResponse:
    """AUT-01: send the browser to the state's identity provider (OpenID Connect, code flow with PKCE)."""
    from syntegra.iam import sso

    tenant = getattr(request, "syntegra_tenant")  # noqa: B009 — set by ContextMiddleware
    redirect_uri = request.build_absolute_uri(f"/auth/sso/{provider}/callback")
    try:
        started = sso.start(tenant, provider, redirect_uri, _safe_next(request.GET.get("next")))
    except DomainError as exc:
        return render(request, "sign_in.html", _ctx(request, error=exc.detail or exc.title), status=exc.status)
    resp = HttpResponseRedirect(started.url)
    resp.set_cookie(
        sso.COOKIE,
        started.cookie,
        max_age=sso.COOKIE_AGE,
        httponly=True,
        samesite="Lax",  # sent on the provider's top-level redirect back to the callback
        secure=not settings.DEBUG,
        path="/auth/sso/",
    )
    return resp


@require_http_methods(["GET"])
@page(public=True)
def sso_callback(request: HttpRequest, provider: str) -> HttpResponse:
    """The provider sends the browser back here with a code: verify, match the account, open the session."""
    from syntegra.core.middleware import session_token
    from syntegra.iam import sso

    tenant = getattr(request, "syntegra_tenant")  # noqa: B009 — set by ContextMiddleware
    c = context.require()
    current, _ = session_token(request)
    try:
        done = sso.finish(
            tenant,
            provider,
            cookie=request.COOKIES.get(sso.COOKIE),
            code=request.GET.get("code"),
            state=request.GET.get("state"),
            error=request.GET.get("error"),
            ip=c.ip,
            ua=c.user_agent,
            current_token=current,
        )
    except DomainError as exc:
        in_use = exc.code == "AUTH-SESSION-IN-USE"
        resp = render(
            request,
            "sign_in.html",
            _ctx(request, error=exc.detail or exc.title, in_use=in_use, providers=_sso_buttons(request)),
            status=exc.status,
        )
        resp.delete_cookie(sso.COOKIE, path="/auth/sso/")
        return resp
    resp = _after_sign_in(done.sign_in, done.next_url)
    resp.delete_cookie(sso.COOKIE, path="/auth/sso/")
    return resp


@require_http_methods(["GET", "POST"])
@page("ADM-103")
def sign_in_providers(request: HttpRequest) -> HttpResponse:
    """ADM-103: the state's single sign-on providers — issuer, client, allowed domains, whether their MFA is trusted
    (CR-008, FR-AUT-106). The client secret is stored encrypted and never shown again."""
    from syntegra.iam import sso

    c = context.require()
    if not c.has("sso:manage"):
        raise Forbidden("Missing permission sso:manage.", code="AUTH-PERMISSION")
    error = done = None
    status = 200
    checked = None
    form: dict[str, Any] = {}
    if request.method == "POST":
        if request.POST.get("action") == "check":
            try:
                checked = sso.check(c, _uuid_or_fail(request.POST.get("id"), "provider"))
                done = "The provider answered: its discovery document and keys were read."
            except DomainError as exc:
                error, status = exc.detail or exc.title, exc.status
            except OSError as exc:
                error, status = f"The provider could not be reached: {exc}", 502
        else:
            form = {k: request.POST.get(k, "") for k in ("provider", "label", "issuer", "client_id", "scopes")}
            form["allowed_domains"] = request.POST.get("allowed_domains", "")
            try:
                sso.save(
                    c,
                    provider=form["provider"],
                    label=form["label"],
                    issuer=form["issuer"],
                    client_id=form["client_id"],
                    client_secret=request.POST.get("client_secret") or None,
                    scopes=form["scopes"] or "openid email profile",
                    allowed_domains=re.split(r"[\s,;]+", form["allowed_domains"]),
                    trust_idp_mfa=request.POST.get("trust_idp_mfa") == "on",
                    sort_order=_int_or_none(request.POST.get("sort_order")),
                    status=request.POST.get("status") or "active",
                )
                done = "Saved. Enabled providers appear on the sign-in page straight away."
                form = {}
            except DomainError as exc:
                error, status = exc.detail or exc.title, exc.status
    return render(
        request,
        "sign_in_providers.html",
        _ctx(
            request,
            rows=sso.configs(c),
            kinds=sso.PROVIDERS,
            form=form,
            error=error,
            done=done,
            checked=checked,
            redirect_base=request.build_absolute_uri("/auth/sso/"),
            page=pages.page("ADM-103"),
        ),
        status=status,
    )


@require_http_methods(["POST"])
@page(confirm=False, mfa=False)
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
    from syntegra.assessment import reports
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
            results=reports.learner_results(learner_id),
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
    c = context.require()
    if not form.permitted(c):
        raise Forbidden()
    forms.require_level(form, c)
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
    """A local path to return to after signing in; anything that a browser could read as another site gives '/'.
    Browsers treat a backslash as a slash (``/\\evil.example``) and drop tabs and newlines, so those are refused too."""
    from django.utils.http import url_has_allowed_host_and_scheme

    if not value or not value.startswith("/") or value.startswith("//"):
        return "/"
    if any(ch in value for ch in "\\\t\r\n") or not url_has_allowed_host_and_scheme(value, allowed_hosts=None):
        return "/"
    return value


@require_http_methods(["GET", "POST"])
@page("AUT-02", confirm=False, mfa=False)
def mfa_challenge(request: HttpRequest) -> HttpResponse:
    """AUT-02: the six-digit code from the authenticator app, for accounts with a second factor. Wrong codes count
    towards the account lock with wrong passwords; a code is accepted once only."""
    from syntegra.core.middleware import session_token
    from syntegra.iam import services as iam

    nxt = _safe_next(request.GET.get("next"))
    sess = getattr(request, "syntegra_session", None)
    if sess is not None and not getattr(sess, "mfa_pending", False):
        return HttpResponseRedirect(nxt)
    error = None
    if request.method == "POST":
        token, _ = session_token(request)
        try:
            iam.verify_mfa(token or "", request.POST.get("code", ""))
            return HttpResponseRedirect(nxt)
        except DomainError as exc:
            error = exc.detail or exc.title
    return render(
        request,
        "mfa.html",
        _ctx(request, error=error, next=nxt, page=pages.page("AUT-02")),
        status=401 if error else 200,
    )


# --------------------------------------------------------------------------- my profile and second factor (HOM-04)
def _token(request: HttpRequest) -> str:
    from syntegra.core.middleware import session_token

    token, _ = session_token(request)
    return token or ""


@require_http_methods(["GET"])
@page("HOM-04")
def profile(request: HttpRequest) -> HttpResponse:
    """HOM-04: my account — roles, this session, and the second factor (authenticators and recovery codes)."""
    from syntegra.iam import mfa
    from syntegra.iam import services as iam
    from syntegra.iam.models import AppUser

    c = context.require()
    u = AppUser.objects.get(pk=c.actor_id)
    return render(
        request,
        "profile.html",
        _ctx(request, me=u, grants=iam.user_grants(u), mfa=mfa.status(_token(request)), page=pages.page("HOM-04")),
    )


@require_http_methods(["GET", "POST"])
@page(confirm=False, mfa=False)
def authenticator(request: HttpRequest) -> HttpResponse:
    """Set up an authenticator app: scan the QR code, type its first code, keep the ten recovery codes (FR-AUT-105).
    Straight after the password for users whose roles need a second factor and who have none (FR-AUT-104)."""
    from syntegra.iam import mfa

    sess = getattr(request, "syntegra_session", None)
    nxt = _safe_next(request.GET.get("next") or "/me")
    if sess is not None and getattr(sess, "mfa_pending", False):  # an account with a factor proves it first
        return HttpResponseRedirect(f"/auth/mfa?{urlencode({'next': request.get_full_path()})}")
    token = _token(request)
    error = None
    if request.method == "POST":
        try:
            factor = _uuid_or_fail(request.POST.get("factor_id", ""), "factor")
            codes = mfa.confirm(token, factor, request.POST.get("code", ""))
            page_meta = pages.page("HOM-04")
            return render(
                request, "recovery_codes.html", _ctx(request, codes=codes, next=nxt, enrolled=True, page=page_meta)
            )
        except DomainError as exc:
            error = f"{exc.title}. {exc.detail}" if exc.detail else exc.title
    try:
        enrol = mfa.begin(token, request.POST.get("label") or "Authenticator app")
    except DomainError as exc:
        return render(request, "error.html", _ctx(request, problem=exc.problem()), status=exc.status)
    return render(
        request,
        "authenticator.html",
        _ctx(
            request,
            enrol=enrol,
            next=nxt,
            error=error,
            required=getattr(sess, "mfa_setup_pending", False),
            page=pages.page("HOM-04"),
        ),
        status=422 if error else 200,
    )


@require_http_methods(["POST"])
@page("HOM-04")
def authenticator_remove(request: HttpRequest, factor_id: uuid.UUID) -> HttpResponse:
    from syntegra.iam import mfa

    mfa.remove(_token(request), factor_id)
    return HttpResponseRedirect("/me?removed=1")


@require_http_methods(["POST"])
@page("HOM-04")
def recovery_codes(request: HttpRequest) -> HttpResponse:
    from syntegra.iam import mfa

    codes = mfa.regenerate(_token(request))
    return render(request, "recovery_codes.html", _ctx(request, codes=codes, next="/me", page=pages.page("HOM-04")))


@require_http_methods(["GET", "POST"])
@page("AUT-03", confirm=False)
def workspace(request: HttpRequest) -> HttpResponse:
    """AUT-03: after the password, confirm the school or office (name and address from the grant, never typed) and,
    when there are several, the role to act under (CR-007, FR-AUT-101)."""
    from syntegra.core import access
    from syntegra.core.middleware import session_token
    from syntegra.iam import services as iam
    from syntegra.iam.models import AppUser

    c = context.require()
    user = AppUser.objects.get(pk=c.actor_id)
    grants = iam.user_grants(user)
    for g in grants:
        g["level"] = access.level(str(g["access_level"]))
    error = None
    if request.method == "POST":
        chosen = request.POST.get("grant_id", "")
        if chosen not in {str(g["grant_id"]) for g in grants}:
            error = "Choose your school or office."
        else:
            token, _ = session_token(request)
            iam.select_grant(token or "", uuid.UUID(chosen), confirm=True)
            return HttpResponseRedirect(_safe_next(request.GET.get("next")))
    sess = getattr(request, "syntegra_session", None)
    return render(
        request,
        "workspace.html",
        _ctx(
            request,
            grants=grants,
            active=str(c.grant_id) if c.grant_id else None,
            confirmed=bool(sess is not None and sess.affiliation_confirmed_at),
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


# ------------------------------------------------------------------------- class subject plan and teachers (ACA-101)
@require_http_methods(["GET", "POST"])
@page("ACA-101")
def class_plan(request: HttpRequest, class_id: uuid.UUID) -> HttpResponse:
    """Each subject of the class with its teacher of record, validated live (G2/G3); assign, replace or end."""
    from syntegra.academic import teaching

    message, problem = None, None
    if request.method == "POST":
        try:
            if request.POST.get("action") == "assign":
                ta = teaching.assign(
                    _uuid_or_fail(request.POST.get("plan_id"), "subject"),
                    _uuid_or_fail(request.POST.get("staff_id"), "teacher"),
                    role=request.POST.get("role", "teacher_of_record"),
                    replace=request.POST.get("replace") == "1",
                    justification=request.POST.get("justification"),
                )
                message = "Teacher assigned." if ta.role == "teacher_of_record" else "Co-teacher added."
            elif request.POST.get("action") == "end":
                teaching.end(_uuid_or_fail(request.POST.get("assignment_id"), "assignment"))
                message = "Assignment ended."
        except DomainError as exc:
            if isinstance(exc, Forbidden):
                raise
            problem = exc.problem()
    return render(
        request,
        "class_plan.html",
        _ctx(
            request,
            d=teaching.class_plan(class_id),
            roles=teaching.ROLES,
            open_plan=request.POST.get("plan_id") if problem else None,
            message=message,
            problem=problem,
            page=pages.page("ACA-101"),
        ),
        status=422 if problem else 200,
    )


# --------------------------------------------------------------------- lesson plan and delivery log (CUR-09)
@require_http_methods(["GET", "POST"])
@page("CUR-09")
def lesson_plans(request: HttpRequest) -> HttpResponse:
    """Each lesson of a class-subject linked to its curriculum objectives; the teacher logs what was delivered."""
    from syntegra.curriculum import lessons

    message, problem = None, None
    picked = request.POST.get("assignment") or request.GET.get("assignment")
    week = _date_or_none(request.POST.get("week") or request.GET.get("week"), "week")
    if request.method == "POST":
        try:
            if request.POST.get("action") == "draft":
                lessons.draft_scheme(_uuid_or_fail(picked, "class-subject"))
                message = "Scheme of work drafted from the curriculum."
            elif request.POST.get("action") == "log":
                on = _date_or_none(request.POST.get("occurs_on"), "lesson date")
                if on is None:
                    raise HardValidation("PAGE-PARAM", "Invalid lesson date", "")
                lessons.log_delivery(
                    _uuid_or_fail(request.POST.get("lesson_id"), "lesson"),
                    on,
                    request.POST.getlist("node_ids"),
                    learners_present=_int_or_none(request.POST.get("learners_present")),
                    minutes=_int_or_none(request.POST.get("minutes")),
                    note=request.POST.get("note"),
                )
                message = "Lesson logged."
        except DomainError as exc:
            if isinstance(exc, Forbidden):
                raise
            problem = exc.problem()
    options = lessons.choices()
    if not picked and options:
        picked = str(options[0]["assignment_id"])
    d = lessons.plan_view(_uuid_or_fail(picked, "class-subject"), week) if picked else None
    return render(
        request,
        "lesson_plans.html",
        _ctx(
            request,
            d=d,
            options=options,
            open_lesson=request.POST.get("lesson_id") if problem else None,
            message=message,
            problem=problem,
            page=pages.page("CUR-09"),
        ),
        status=422 if problem else 200,
    )


# ------------------------------------------------------------------------- marksheets and report cards (CR-009)
def _decimal_or_fail(value: str | None, what: str) -> Any:
    from decimal import Decimal, InvalidOperation

    try:
        return Decimal((value or "").strip())
    except InvalidOperation as exc:
        raise HardValidation("PAGE-PARAM", f"Invalid {what}", f"Enter the {what} as a number.") from exc


@require_http_methods(["GET", "POST"])
@page("ASM-01")
def markbook(request: HttpRequest, class_id: uuid.UUID, subject_id: uuid.UUID) -> HttpResponse:
    """The marksheet of a class-subject: add an assessment, enter a column of marks, lock approved marks."""
    from syntegra.assessment import markbook as mb

    message, problem = None, None
    editing = request.POST.get("assessment_id") or request.GET.get("enter")
    picked = request.POST.get("term") or request.GET.get("term")
    term_id = _uuid_or_fail(picked, "term") if picked else None
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "add":
                a = mb.add_assessment(
                    class_id,
                    subject_id,
                    request.POST.get("title", ""),
                    request.POST.get("kind", ""),
                    _decimal_or_fail(request.POST.get("max_mark"), "maximum mark"),
                    _decimal_or_fail(request.POST.get("weight"), "weight"),
                    _date_or_none(request.POST.get("assessed_on"), "date"),
                )
                message, editing = f"{a.title} added — enter its marks below.", str(a.id)
                term_id = _term_of(class_id, a.assessed_on)
            elif action == "save":
                aid = _uuid_or_fail(request.POST.get("assessment_id"), "assessment")
                marks = {
                    uuid.UUID(k[5:]): request.POST.get(k, "")
                    for k in request.POST
                    if k.startswith("mark_") and _is_uuid(k[5:])
                }
                lock = request.POST.get("lock") == "1"
                r = mb.save_marks(aid, marks, lock=lock)
                message = f"Marks saved ({r['created']} new, {r['updated']} changed)" + (
                    " and locked." if lock else "."
                )
                editing = None if lock else str(aid)
            elif action == "lock":
                mb.lock(_uuid_or_fail(request.POST.get("assessment_id"), "assessment"))
                message, editing = "Marks locked.", None
        except DomainError as exc:
            if isinstance(exc, Forbidden):
                raise
            problem = exc.problem()
    d = mb.sheet(class_id, subject_id, term_id)
    return render(
        request,
        "markbook.html",
        _ctx(
            request,
            d=d,
            editing=editing if d["can_enter"] else None,
            posted=request.POST if problem else {},
            names={str(r["learner_id"]): r["name"] for r in d["rows"]},
            today=dt.date.today(),
            message=message,
            problem=problem,
            page=pages.page("ASM-01"),
        ),
        status=422 if problem else 200,
    )


def _term_of(class_id: uuid.UUID, on: dt.date | None) -> uuid.UUID | None:
    from syntegra.academic.models import ClassGroup
    from syntegra.assessment import markbook as mb

    cls = ClassGroup.objects.in_scope().filter(pk=class_id).first()
    term = mb.current_term(cls, on) if cls is not None else None
    return term.id if term is not None else None


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True


@require_http_methods(["GET", "POST"])
@page("ASM-04")
def report_cards(request: HttpRequest, class_id: uuid.UUID) -> HttpResponse:
    """A class's termly report cards: completeness, each learner's result and personalised comments; issue."""
    from syntegra.assessment import reports

    message, problem = None, None
    if request.method == "POST":
        try:
            if request.POST.get("action") == "comments":
                comments: dict[str, dict[str, str]] = {}
                for k in request.POST:
                    kind, _, lid = k.partition("_")
                    if kind in ("form", "head") and _is_uuid(lid):
                        comments.setdefault(lid, {})[kind] = request.POST.get(k, "")
                n = reports.save_comments(class_id, comments)
                message = f"Comments saved ({n} learner{'' if n == 1 else 's'} with edited comments)."
            elif request.POST.get("action") == "issue":
                r = reports.issue(class_id)
                message = f"{r['issued']} report cards issued and filed in the school's register."
        except DomainError as exc:
            if isinstance(exc, Forbidden):
                raise
            problem = exc.problem()
    return render(
        request,
        "report_cards.html",
        _ctx(request, d=reports.class_reports(class_id), message=message, problem=problem, page=pages.page("ASM-04")),
        status=422 if problem else 200,
    )


@require_http_methods(["GET"])
@page("ASM-04")
def report_card(request: HttpRequest, class_id: uuid.UUID, learner_id: uuid.UUID) -> HttpResponse:
    """One learner's report card, laid out as it prints and as the issued PDF reads."""
    from syntegra.assessment import reports

    return render(
        request,
        "report_card.html",
        _ctx(request, d=reports.learner_report(class_id, learner_id), page=pages.page("ASM-04")),
    )


# ---------------------------------------------------------------------------------- administration (CR-007)
@require_http_methods(["GET", "POST"])
@page("ADM-102")
def sessions_admin(request: HttpRequest) -> HttpResponse:
    """ADM-102: sessions in use by users in scope; end one with a reason (FR-AUT-103)."""
    from syntegra.iam import services as iam

    c = context.require()
    if not c.has("session:manage"):
        raise Forbidden("Missing permission session:manage.", code="AUTH-PERMISSION")
    error = done = None
    status = 200
    if request.method == "POST":
        try:
            iam.end_session(c, _uuid_or_fail(request.POST.get("session_id"), "session"), request.POST.get("reason", ""))
            done = "The session was ended. The person will be asked to sign in again."
        except DomainError as exc:
            error = exc.detail or exc.title
            status = exc.status
    rows = iam.active_sessions(c)
    return render(
        request,
        "sessions_admin.html",
        _ctx(
            request,
            rows=rows,
            window=int(iam.in_use_window().total_seconds() // 60),
            error=error,
            done=done,
            page=pages.page("ADM-102"),
        ),
        status=status,
    )


@require_http_methods(["GET", "POST"])
@page("ADM-101")
def access_levels(request: HttpRequest) -> HttpResponse:
    """ADM-101: the five access levels, each role's level, and lowering one user's level for a grant (FR-ADM-202)."""
    from syntegra.iam import services as iam

    c = context.require()
    if not c.has("access:manage"):
        raise Forbidden("Missing permission access:manage.", code="AUTH-PERMISSION")
    error = done = None
    status = 200
    if request.method == "POST":
        action = request.POST.get("action") or "level"
        reason = request.POST.get("reason", "")
        try:
            if action == "office":
                office = request.POST.get("office_id") or ""
                iam.set_grant_office(
                    c,
                    _uuid_or_fail(request.POST.get("grant_id"), "role grant"),
                    _uuid_or_fail(office, "office") if office else None,
                    reason,
                )
                done = "The office was changed. The person sees it the next time they sign in."
            elif action == "address":
                iam.set_office_address(
                    c,
                    _uuid_or_fail(request.POST.get("node_id"), "office"),
                    {k: request.POST.get(k, "") for k in iam.ADDRESS_FIELDS},
                    reason,
                )
                done = "The office address was saved. People who work there see it when they sign in."
            else:
                cap = request.POST.get("cap") or None
                iam.set_grant_cap(c, _uuid_or_fail(request.POST.get("grant_id"), "role grant"), cap, reason)
                done = "The access level was changed. It applies from the person's next page."
        except DomainError as exc:
            error = exc.detail or exc.title
            status = exc.status
    per_page = 300
    offices = iam.offices(c)
    data = iam.access_overview(
        c, q=request.GET.get("q") or "", offset=_int_or_none(request.GET.get("from")) or 0, limit=per_page
    )
    return render(
        request,
        "access_levels.html",
        _ctx(
            request,
            levels=data["levels"],
            roles=data["roles"],
            grants=data["grants"],
            offices=offices,
            office_names={o["id"]: o["office"] for o in offices},
            total=data["total"],
            offset=data["offset"],
            per_page=per_page,
            q=data["q"],
            error=error,
            done=done,
            page=pages.page("ADM-101"),
        ),
        status=status,
    )


# ---------------------------------------------------------------------------------- documents (CR-007)
def _int_or_none(value: str | None) -> int | None:
    return int(value) if value and value.isdigit() else None


def _date_or_none(value: str | None, what: str) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise HardValidation("PAGE-PARAM", f"Invalid {what}", "Use the date picker (YYYY-MM-DD).") from exc


def _doc_schools(c: Any) -> list[Any]:
    """Institutions the caller may file or search under: their own school, or every school in scope."""
    from syntegra.institutions.models import Institution

    qs = Institution.objects.all()
    if c.scope_ids is not None:
        qs = qs.filter(scope_node_id__in=list(c.scope_ids))
    return list(qs.order_by("name")[:2000])


@require_http_methods(["GET"])
@page("DOC-104")
def documents(request: HttpRequest) -> HttpResponse:
    """DOC-104 Documents: search every school's digitised documents in scope (FR-DOC-204/206)."""
    from syntegra.records import services as rec

    c = context.require()
    if not (c.has("document:view") or c.has("document:search") or c.has("document:upload")):
        raise Forbidden("Missing permission document:view.", code="AUTH-PERMISSION")
    schools = _doc_schools(c)
    inst_param = request.GET.get("institution") or ""
    institution_id = _uuid_or_fail(inst_param, "school") if inst_param else None
    if institution_id is None and not c.has("document:search") and len(schools) == 1:
        return HttpResponseRedirect(f"/institutions/{schools[0].id}/documents")
    q = (request.GET.get("q") or "").strip()
    cat = request.GET.get("category") or ""
    year = _int_or_none(request.GET.get("year"))
    purpose = request.GET.get("purpose") or None
    searched = bool(q or institution_id or cat or year)
    result = None
    if searched and (c.has("document:view") or c.has("document:search")):
        result = rec.search(c, q=q, institution_id=institution_id, category_code=cat, year=year, purpose=purpose)
    by_school = rec.institutions_with_documents(c) if c.has("document:view") or c.has("document:search") else []
    names = {str(s.id): s.name for s in schools}
    return render(
        request,
        "documents.html",
        _ctx(
            request,
            q=q,
            cat=cat,
            year=year or "",
            institution=str(institution_id or ""),
            schools=schools,
            names=names,
            categories=rec.categories(),
            result=result,
            searched=searched,
            by_school=by_school,
            ocr=rec.ocr_available(),
            purpose=purpose or "",
            purposes=_purposes(c) if rec.restricted_needs_purpose(c) else [],
            page=pages.page("DOC-104"),
        ),
    )


@require_http_methods(["GET", "POST"])
@page("DOC-107")
def document_upload(request: HttpRequest) -> HttpResponse:
    """DOC-107 Upload digitised paper documents under a school (FR-DOC-202)."""
    from syntegra.records import services as rec

    c = context.require()
    if not c.has("document:upload"):
        raise Forbidden("Missing permission document:upload.", code="AUTH-PERMISSION")
    schools = _doc_schools(c)
    error = None
    errors: list[dict[str, Any]] = []
    form = request.POST if request.method == "POST" else request.GET
    if request.method == "POST":
        try:
            files = [rec.Upload(f.name or "file", f.read()) for f in request.FILES.getlist("files")]
            docs = rec.upload(
                c,
                institution_id=_uuid_or_fail(form.get("institution"), "school"),
                category_code=form.get("category", ""),
                title=form.get("title", ""),
                files=files,
                date_from=_date_or_none(form.get("date_from"), "date"),
                date_to=_date_or_none(form.get("date_to"), "date"),
                session_label=form.get("session_label", ""),
                level_or_class=form.get("level_or_class", ""),
                subject_label=form.get("subject_label", ""),
                source_reference=form.get("source_reference", ""),
                description=form.get("description", ""),
                transcription=form.get("transcription", ""),
                classification=form.get("classification") or None,
            )
            refs = ",".join(str(d.id) for d in docs)
            return HttpResponseRedirect(
                f"/institutions/{docs[0].institution_id}/documents?{urlencode({'added': refs})}"
            )
        except DomainError as exc:
            error = exc.detail or exc.title
            errors = exc.errors
    from syntegra.core import access

    return render(
        request,
        "document_upload.html",
        _ctx(
            request,
            schools=schools,
            categories=rec.categories(),
            levels=[lv for lv in access.LEVELS if c.cleared_for(lv.classification) and lv.number < 5],
            form=form,
            error=error,
            errors=errors,
            ocr=rec.ocr_available(),
            max_mb=int(settings.SYNTEGRA_DOCUMENT_MAX_BYTES // (1024 * 1024)),
            page=pages.page("DOC-107"),
        ),
        status=422 if error else 200,
    )


@require_http_methods(["GET"])
@page("DOC-108")
def school_documents(request: HttpRequest, institution_id: uuid.UUID) -> HttpResponse:
    """DOC-108 One school's complete document register, grouped by category (FR-DOC-205)."""
    from syntegra.records import services as rec

    c = context.require()
    q = (request.GET.get("q") or "").strip()
    purpose = request.GET.get("purpose") or None
    reg = rec.register(c, institution_id, q=q, purpose=purpose)
    added = {x for x in (request.GET.get("added") or "").split(",") if x}
    return render(
        request,
        "school_documents.html",
        _ctx(
            request,
            reg=reg,
            q=q,
            added=added,
            purpose=purpose or "",
            purposes=_purposes(c) if rec.restricted_needs_purpose(c) else [],
            page=pages.page("DOC-108"),
        ),
    )


def _purposes(c: Any) -> list[Any]:
    from syntegra.iam.models import PurposeCode

    return [p for p in PurposeCode.objects.order_by("label") if not p.allowed_roles or c.role_code in p.allowed_roles]


@require_http_methods(["GET"])
@page("DOC-105")
def document_view(request: HttpRequest, document_id: uuid.UUID) -> HttpResponse:
    """DOC-105 Document viewer: metadata, the scan (watermarked on screen), downloads and the Word copy."""
    from syntegra.core.errors import PurposeRequired
    from syntegra.records import services as rec

    c = context.require()
    purpose = request.GET.get("purpose") or None
    try:
        d = rec.detail(c, document_id, purpose)
    except PurposeRequired:
        return render(
            request,
            "document_purpose.html",
            _ctx(request, document_id=document_id, purposes=_purposes(c), page=pages.page("DOC-105")),
            status=428,
        )
    from django.utils import timezone

    return render(
        request,
        "document.html",
        _ctx(
            request,
            d=d,
            purpose=purpose or "",
            stamp=timezone.localtime().strftime("%d %b %Y %H:%M"),
            page=pages.page("DOC-105"),
        ),
    )


@xframe_options_sameorigin
@require_http_methods(["GET"])
@page("DOC-105")
def document_file(request: HttpRequest, document_id: uuid.UUID) -> HttpResponse:
    """A stamped copy of the scan (or of its searchable copy), shown inline or downloaded; each one is entered in the
    release register (CR-008)."""
    from syntegra.records import evidence

    c = context.require()
    kind = "stamped_searchable" if request.GET.get("kind") == "searchable" else "stamped_original"
    downloading = bool(request.GET.get("download"))
    r = evidence.release(c, document_id, kind, purpose=request.GET.get("purpose") or None, on_screen=not downloading)
    data, mime, name = r.data, r.mime, r.filename
    resp = HttpResponse(data, content_type=mime)
    resp["X-Syntegra-Release"] = r.code
    disposition = "attachment" if downloading else "inline"
    resp["Content-Disposition"] = f'{disposition}; filename="{name}"'
    resp["Cache-Control"] = "no-store"
    resp["X-Content-Type-Options"] = "nosniff"  # the type was sniffed from the bytes at upload: PDF, image or text
    if mime == "text/plain":
        resp["Content-Security-Policy"] = "default-src 'none'; sandbox"
    return resp


@require_http_methods(["POST"])
@page("DOC-105")
def document_certified(request: HttpRequest, document_id: uuid.UUID) -> HttpResponse:
    """A certified true copy of the master — byte for byte, unstamped — with a reason (CR-008, FR-DOC-305)."""
    from syntegra.records import evidence

    c = context.require()
    r = evidence.release(
        c,
        document_id,
        "certified_original",
        purpose=request.GET.get("purpose") or None,
        reason=request.POST.get("reason", ""),
    )
    resp = HttpResponse(r.data, content_type=r.mime)
    resp["Content-Disposition"] = f'attachment; filename="{r.filename}"'
    resp["Cache-Control"] = "no-store"
    resp["X-Syntegra-Release"] = r.code
    return resp


@require_http_methods(["GET", "POST"])
@page("DOC-109")
def releases_page(request: HttpRequest) -> HttpResponse:
    """DOC-109: copies of documents that left the system, and checking a presented copy by its release code."""
    from syntegra.records import evidence

    c = context.require()
    code = (request.POST.get("code") or request.GET.get("code") or "").strip()
    doc = request.GET.get("document") or ""
    found = None
    error = None
    if code:
        up = request.FILES.get("file")
        try:
            found = evidence.lookup(c, code, up.read() if up else None)
        except DomainError as exc:
            error = exc.detail or exc.title
    rows = evidence.releases(c, document_id=_uuid_or_fail(doc, "document") if doc else None)
    return render(
        request,
        "releases.html",
        _ctx(request, rows=rows, found=found, code=code, error=error, document=doc, page=pages.page("DOC-109")),
        status=404 if error else 200,
    )


@require_http_methods(["GET"])
@page("DOC-105")
def document_word(request: HttpRequest, document_id: uuid.UUID) -> HttpResponse:
    """An editable Word copy of the document's text, made on demand (the scan stays the record)."""
    from syntegra.records import services as rec

    c = context.require()
    data, name = rec.word_copy(c, document_id, request.GET.get("purpose") or None)
    resp = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    resp["Content-Disposition"] = f'attachment; filename="{name}"'
    resp["Cache-Control"] = "no-store"
    return resp
