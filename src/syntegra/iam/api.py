"""Session API (MFS §5.1): sign in, MFA, choose role, sign out, who am I."""

from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from syntegra.core import context
from syntegra.core.api.permissions import Authenticated, Public
from syntegra.core.middleware import session_token
from syntegra.iam import services


class SignInSerializer(serializers.Serializer):  # type: ignore[type-arg]
    username = serializers.CharField(max_length=254)
    password = serializers.CharField(max_length=512, trim_whitespace=False)


def _set_cookie(resp: Response, token: str) -> None:
    resp.set_cookie(
        settings.SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,
        max_age=int(services.SESSION_MAX.total_seconds()),
    )


class SignInView(APIView):
    authentication_classes: list[Any] = []
    permission_classes = [Public]
    throttle_classes = [AnonRateThrottle]

    def post(self, request: Request) -> Response:
        s = SignInSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        ctx = context.require()
        tenant = request._request.syntegra_tenant  # type: ignore[attr-defined]
        r = services.sign_in(
            tenant, s.validated_data["username"], s.validated_data["password"], ip=ctx.ip, ua=ctx.user_agent
        )
        resp = Response(
            {"token": r.token, "mfa_required": r.mfa_required, "grants": r.grants, "session_id": str(r.session_id)},
            status=201,
        )
        _set_cookie(resp, r.token)
        return resp


class MfaView(APIView):
    authentication_classes: list[Any] = []
    permission_classes = [Public]
    throttle_classes = [AnonRateThrottle]

    def post(self, request: Request) -> Response:
        token, _ = session_token(request._request)
        services.verify_mfa(token or "", str(request.data.get("code", "")))
        return Response({"ok": True})


class SelectRoleView(APIView):
    permission_classes = [Authenticated]

    def post(self, request: Request) -> Response:
        token, _ = session_token(request._request)
        services.select_grant(token or "", uuid.UUID(str(request.data.get("grant_id"))))
        return Response({"ok": True})


class SignOutView(APIView):
    permission_classes = [Authenticated]

    def post(self, request: Request) -> Response:
        token, _ = session_token(request._request)
        services.sign_out(token or "")
        resp = Response(status=204)
        resp.delete_cookie(settings.SESSION_COOKIE_NAME)
        return resp


class MeView(APIView):
    permission_classes = [Authenticated]

    def get(self, request: Request) -> Response:
        from syntegra.iam.models import AppUser

        ctx = context.require()
        u = AppUser.objects.get(pk=ctx.actor_id)
        return Response(
            {
                "user_id": str(u.id),
                "username": u.username,
                "display_name": u.display_name,
                "role": ctx.role_code,
                "grant_id": str(ctx.grant_id) if ctx.grant_id else None,
                "scope_node_id": str(ctx.scope_node_id) if ctx.scope_node_id else None,
                "clearance": ctx.clearance,
                "permissions": sorted(ctx.permissions),
                "grants": services.user_grants(u),
                "tenant": {"id": str(ctx.tenant_id), "state_tenant_id": str(ctx.state_tenant_id)},
            }
        )
