"""DRF permission classes over the request ``Context``."""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

from syntegra.core import access, context
from syntegra.core.context import class_rank
from syntegra.core.errors import Forbidden


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
            if ctx.auth_pending == "mfa_setup":
                self.message = (
                    "Your roles need a second factor: set up an authenticator app (POST /api/v1/me/mfa/totp, then "
                    "POST /api/v1/me/mfa/totp/{id}/confirm with its first code) to continue."
                )
            elif ctx.auth_pending == "mfa":
                self.message = "Enter the code from your authenticator app (POST /api/v1/auth/mfa) to continue."
            return False
        perm = getattr(view, "required_permission", None)
        if isinstance(perm, dict):
            perm = perm.get(request.method or "GET") or perm.get("*")
        if perm and not ctx.has(perm):
            return False
        if request.method not in SAFE_METHODS and not ctx.is_system:
            # views whose service chooses between permissions (own or on behalf) name them in ``level_permissions``
            _check_write_level(ctx, getattr(view, "level_permissions", None) or (perm,))
        return True


def _check_write_level(ctx: context.Context, permissions: tuple[str | None, ...]) -> None:
    """A write needs the access level of the web form that does the same thing (CR-008, FR-ADM-203)."""
    levels = [lv for lv in (access.write_level(p) for p in permissions) if lv]
    needed = min(levels, key=class_rank) if levels else None
    if needed and not access.covers(ctx.clearance, needed):
        raise Forbidden(
            f"This action needs {access.level(needed).label}. Your access level in this role is "
            f"{access.level(ctx.clearance).label}.",
            code="AUTH-LEVEL",
        )


class Public(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return True


class Authenticated(BasePermission):
    """Signed in (a grant need not be selected yet) — for the session endpoints."""

    def has_permission(self, request: Request, view: Any) -> bool:
        ctx = context.current(required=False)
        return ctx is not None and ctx.actor_kind != "public"
