"""Session API (MFS §5.1): sign in, MFA, choose role, sign out, who am I."""

from __future__ import annotations

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


class SelectRoleSerializer(serializers.Serializer):  # type: ignore[type-arg]
    grant_id = serializers.UUIDField()


class SelectRoleView(APIView):
    permission_classes = [Authenticated]

    def post(self, request: Request) -> Response:
        token, _ = session_token(request._request)
        s = SelectRoleSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        aff = services.select_grant(token or "", s.validated_data["grant_id"], confirm=True)
        return Response({"ok": True, "affiliation": aff})


class SignOutView(APIView):
    permission_classes = [Authenticated]

    def post(self, request: Request) -> Response:
        token, _ = session_token(request._request)
        services.sign_out(token or "")
        resp = Response(status=204)
        resp.delete_cookie(settings.SESSION_COOKIE_NAME)
        return resp


def _level(clearance: str) -> dict[str, Any]:
    from syntegra.core import access

    lv = access.level(clearance)
    return {"number": lv.number, "name": lv.name, "classification": lv.classification}


def _affiliation(request: Request) -> dict[str, Any] | None:
    sess = getattr(request._request, "syntegra_session", None)
    if sess is None or not sess.affiliation_name:
        return None
    return {
        "scope_id": str(sess.affiliation_scope_id) if sess.affiliation_scope_id else None,
        "name": sess.affiliation_name,
        "address": sess.affiliation_address,
        "confirmed_at": sess.affiliation_confirmed_at.isoformat() if sess.affiliation_confirmed_at else None,
    }


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
                "access_level": _level(ctx.clearance),
                "affiliation": _affiliation(request),
                "permissions": sorted(ctx.permissions),
                "grants": services.user_grants(u),
                "tenant": {"id": str(ctx.tenant_id), "state_tenant_id": str(ctx.state_tenant_id)},
            }
        )


# --------------------------------------------------------------------------- administration (CR-007)
class ReasonSerializer(serializers.Serializer):  # type: ignore[type-arg]
    reason = serializers.CharField(min_length=5, max_length=1000)


class SessionsView(APIView):
    """GET sessions in use by users in scope (FR-AUT-103)."""

    permission_classes = [Authenticated]

    def get(self, request: Request) -> Response:
        rows = services.active_sessions(context.require())
        for r in rows:
            for k in ("started_at", "last_seen_at"):
                r[k] = r[k].isoformat()  # type: ignore[attr-defined]
        return Response({"results": rows, "in_use_minutes": int(services.in_use_window().total_seconds() // 60)})


class SessionEndView(APIView):
    """POST: an administrator ends a session, with a reason (FR-AUT-103)."""

    permission_classes = [Authenticated]

    def post(self, request: Request, pk: str) -> Response:
        import uuid as _uuid

        s = ReasonSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.end_session(context.require(), _uuid.UUID(str(pk)), s.validated_data["reason"])
        return Response(status=204)


class AccessLevelsView(APIView):
    """GET the five levels, every role's level and the grants in scope with their effective level (FR-ADM-202)."""

    permission_classes = [Authenticated]

    def get(self, request: Request) -> Response:
        data = services.access_overview(context.require())

        def lv(x: Any) -> dict[str, Any] | None:
            return None if x is None else {"number": x.number, "name": x.name, "classification": x.classification}

        return Response(
            {
                "levels": [{**(lv(x) or {}), "sees": x.sees} for x in data["levels"]],  # type: ignore[attr-defined]
                "roles": [
                    {"code": r["code"], "name": r["name"], "level": lv(r["level"]), "holders": r["holders"]}
                    for r in data["roles"]  # type: ignore[attr-defined]
                ],
                "grants": [
                    {
                        "grant_id": g["grant_id"],
                        "user": g["user"],
                        "username": g["username"],
                        "role": g["role"],
                        "scope": g["scope"],
                        "role_level": lv(g["role_level"]),
                        "effective_level": lv(g["effective"]),
                        "lowered": g["cap"] is not None,
                    }
                    for g in data["grants"]  # type: ignore[attr-defined]
                ],
            }
        )


class GrantLevelSerializer(serializers.Serializer):  # type: ignore[type-arg]
    level = serializers.ChoiceField(choices=["public", "internal", "confidential", "restricted", "special"])
    reason = serializers.CharField(min_length=5, max_length=1000)


class GrantLevelView(APIView):
    """PUT the access level of one grant (lower it, or restore the role's level) with a reason (FR-ADM-202)."""

    permission_classes = [Authenticated]

    def put(self, request: Request, pk: str) -> Response:
        import uuid as _uuid

        s = GrantLevelSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.set_grant_cap(
            context.require(), _uuid.UUID(str(pk)), s.validated_data["level"], s.validated_data["reason"]
        )
        return Response(status=204)
