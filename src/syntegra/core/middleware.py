"""Request context middleware (MFS §16.3 layer 2).

Resolves the tenant from the host, authenticates the session (``Authorization: Bearer`` or the
``syn_session`` cookie), expands the active role grant and installs the ``Context`` for the request.
Unauthenticated requests get a *public* context (tenant known, no permissions).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable

from django.conf import settings
from django.db import DatabaseError
from django.http import HttpRequest, HttpResponse, JsonResponse

from syntegra.core import authz, context
from syntegra.core.context import Context
from syntegra.core.errors import DomainError
from syntegra.core.tenancy import resolve_host

log = logging.getLogger(__name__)
EXEMPT_PREFIXES = ("/healthz", "/static/")


def client_ip(request: HttpRequest) -> str | None:
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    if fwd and getattr(settings, "SYNTEGRA_TRUST_PROXY", False):
        return fwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def session_token(request: HttpRequest) -> tuple[str | None, bool]:
    """(token, from_cookie)."""
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip(), False
    cookie = request.COOKIES.get(getattr(settings, "SESSION_COOKIE_NAME", "syn_session"))
    return (cookie, True) if cookie else (None, False)


class ContextMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path.startswith(EXEMPT_PREFIXES):
            return self.get_response(request)
        try:
            ctx = self._build(request)
        except DomainError as exc:
            return JsonResponse(exc.problem(), status=exc.status, content_type="application/problem+json")
        except DatabaseError:
            log.exception("tenant resolution failed")
            return JsonResponse({"title": "Service unavailable", "status": 503}, status=503,
                                content_type="application/problem+json")
        if ctx is None:
            return JsonResponse({"type": "https://errors.syntegra.io/TENANT-UNKNOWN", "title": "Unknown tenant",
                                 "status": 404}, status=404, content_type="application/problem+json")
        request.syntegra_ctx = ctx  # type: ignore[attr-defined]
        with context.use(ctx):
            response = self.get_response(request)
        response["X-Correlation-Id"] = ctx.correlation_id
        return response

    def _build(self, request: HttpRequest) -> Context | None:
        tenant = resolve_host(request.get_host())
        if tenant is None:
            return None
        corr = request.META.get("HTTP_X_REQUEST_ID") or uuid.uuid4().hex
        base = Context(
            tenant_id=tenant.id, state_tenant_id=tenant.state_tenant_id, actor_kind="public",
            clearance="public", permissions=frozenset(), scope_ids=frozenset(), correlation_id=corr[:64],
            ip=client_ip(request), user_agent=request.META.get("HTTP_USER_AGENT", "")[:400] or None,
        )
        request.syntegra_tenant = tenant  # type: ignore[attr-defined]
        request.syntegra_token_cookie = False  # type: ignore[attr-defined]
        token, from_cookie = session_token(request)
        if not token:
            return base
        from syntegra.iam import services as iam

        resolved = iam.resolve(token, base)
        if resolved is None:
            return base
        ctx, sess = resolved
        request.syntegra_session = sess  # type: ignore[attr-defined]
        request.syntegra_token_cookie = from_cookie  # type: ignore[attr-defined]
        purpose = request.META.get("HTTP_X_SYNTEGRA_PURPOSE")
        if purpose:
            ctx = ctx.with_(purpose=authz.validate_purpose(ctx, purpose))
        return ctx
