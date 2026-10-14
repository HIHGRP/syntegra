"""DRF authentication backed by the request ``Context`` installed by ``ContextMiddleware``."""

from __future__ import annotations

from typing import Any

from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request


class _CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request: Any, reason: str) -> str:  # type: ignore[override]
        return reason


class ContextAuthentication(BaseAuthentication):
    """Authenticated when the middleware resolved a user session; enforces CSRF for cookie sessions."""

    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        raw = request._request
        ctx = getattr(raw, "syntegra_ctx", None)
        if ctx is None or ctx.actor_kind == "public":
            return None
        if getattr(raw, "syntegra_token_cookie", False):
            check = _CSRFCheck(lambda r: None)  # type: ignore[arg-type,return-value]
            check.process_request(raw)
            reason = check.process_view(raw, None, (), {})  # type: ignore[arg-type]
            if reason:
                raise exceptions.PermissionDenied(f"CSRF failed: {reason}")
        return ctx, getattr(raw, "syntegra_session", None)

    def authenticate_header(self, request: Request) -> str:
        return 'Bearer realm="syntegra"'
