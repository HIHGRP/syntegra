"""Server-rendered pages (MFS Part B). Pages call the same services as the API — no logic lives here."""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from syntegra.core import context
from syntegra.core.errors import DomainError, Forbidden
from syntegra.web import pages

View = Callable[..., HttpResponse]


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
            nxt = request.GET.get("next", "/")
            resp = HttpResponseRedirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else "/")
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


@require_http_methods(["GET"])
@page("PUB-01", public=True)
def verify(request: HttpRequest) -> HttpResponse:
    from syntegra.certificates import services as certs

    q = (request.GET.get("number") or request.GET.get("code") or "").strip()
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
    day = dt.date.fromisoformat(request.GET.get("date", dt.date.today().isoformat()))
    reg = att.open_register(class_id, day)
    message = None
    if request.method == "POST":
        marks = []
        for key, code in request.POST.items():
            code = str(code)
            if key.startswith("mark_") and code:
                lid = uuid.UUID(key[5:])
                late = request.POST.get(f"late_{lid}")
                marks.append(
                    att.Mark(
                        learner_id=lid,
                        code=code,
                        minutes_late=int(late) if late and code == "L" else None,
                        client_op_id=uuid.uuid5(reg.id, f"{lid}:{code}:{late}"),
                    )
                )
        r = att.submit(reg.id, marks, if_match=int(request.POST.get("row_version", "0")) or None)
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


@page("LRN-04")
def learner(request: HttpRequest, learner_id: uuid.UUID) -> HttpResponse:
    from syntegra.attendance import services as att
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
