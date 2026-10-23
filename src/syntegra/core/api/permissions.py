"""DRF permission classes over the request ``Context``."""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from syntegra.core import context


class RequiresContext(BasePermission):
    """Authenticated user with an active role grant; per-view ``required_permission`` is checked too."""

    message = (
        "Sign in, enter your code when asked (POST /api/v1/auth/mfa) and confirm your school or office "
        "(POST /api/v1/auth/role) to continue."
    )

    def has_permission(self, request: Request, view: Any) -> bool:
        ctx = context.current(required=False)
        if ctx is None or ctx.actor_kind == "public":
            return False
        if ctx.grant_id is None and not ctx.is_system:
            return False
        perm = getattr(view, "required_permission", None)
        if isinstance(perm, dict):
            perm = perm.get(request.method or "GET") or perm.get("*")
        return ctx.has(perm) if perm else True


class Public(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return True


class Authenticated(BasePermission):
    """Signed in (a grant need not be selected yet) — for the session endpoints."""

    def has_permission(self, request: Request, view: Any) -> bool:
        ctx = context.current(required=False)
        return ctx is not None and ctx.actor_kind != "public"
