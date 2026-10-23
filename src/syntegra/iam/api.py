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
from syntegra.core.api import views as v
from syntegra.core.api.permissions import Authenticated, Public
from syntegra.core.middleware import session_token
from syntegra.iam import mfa, services, sso


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
        current, _ = session_token(request._request)
        r = services.sign_in(
            tenant,
            s.validated_data["username"],
            s.validated_data["password"],
            ip=ctx.ip,
            ua=ctx.user_agent,
            current_token=current,
        )
        # Nothing else opens until the school or office is confirmed with POST /auth/role (FR-AUT-101), after the
        # code with POST /auth/mfa when mfa_required, or after setting up an authenticator (POST /me/mfa/totp, then
        # its confirm) when mfa_setup_required.
        resp = Response(
            {
                "token": r.token,
                "mfa_required": r.mfa_required,
                "mfa_setup_required": r.mfa_setup_required,
                "confirm_required": True,
                "grants": r.grants,
                "session_id": str(r.session_id),
            },
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


# --------------------------------------------------------------------------- my second factor (CR-008, FR-AUT-104/105)
def _token(request: Request) -> str:
    token, _ = session_token(request._request)
    return token or ""


class MyMfaView(APIView):
    """GET my second factor: authenticators, recovery codes left, and whether my roles require one."""

    permission_classes = [Authenticated]

    def get(self, request: Request) -> Response:
        return Response(v.jsonable(mfa.status(_token(request))))


class NewFactorSerializer(serializers.Serializer):  # type: ignore[type-arg]
    name = serializers.CharField(max_length=80, required=False, default="Authenticator app")


class MyTotpView(APIView):
    """POST: start setting up an authenticator app; returns the key and the otpauth:// URI to show as a QR code."""

    permission_classes = [Authenticated]

    def post(self, request: Request) -> Response:
        s = NewFactorSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        e = mfa.begin(_token(request), s.validated_data["name"])
        return Response({"factor_id": str(e.factor_id), "secret": e.secret, "otpauth_uri": e.uri}, status=201)


class CodeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    code = serializers.RegexField(r"^\s*\d{3}\s?\d{3}\s*$", max_length=8)


class MyTotpConfirmView(APIView):
    """POST the first code from the app: the authenticator is on, and the ten recovery codes are returned once."""

    permission_classes = [Authenticated]

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = CodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response({"recovery_codes": mfa.confirm(_token(request), pk, s.validated_data["code"])})


class MyMfaRemoveView(APIView):
    permission_classes = [Authenticated]

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        mfa.remove(_token(request), pk)
        return Response(status=204)


class MyRecoveryCodesView(APIView):
    """POST: ten new recovery codes (the old ones stop working); needs a session that has passed the second factor."""

    permission_classes = [Authenticated]

    def post(self, request: Request) -> Response:
        return Response({"recovery_codes": mfa.regenerate(_token(request))}, status=201)


# --------------------------------------------------------------------------- single sign-on (CR-003, CR-008)
class SsoProvidersView(APIView):
    """GET the enabled sign-in providers (button text and start URL) — public, for sign-in screens."""

    authentication_classes: list[Any] = []
    permission_classes = [Public]

    def get(self, request: Request) -> Response:
        tenant = request._request.syntegra_tenant  # type: ignore[attr-defined]
        return Response(
            {
                "providers": [
                    {"provider": p.provider, "label": p.label, "start": f"/auth/sso/{p.provider}/start"}
                    for p in sso.enabled(tenant)
                ]
            }
        )


class ProviderSerializer(serializers.Serializer):  # type: ignore[type-arg]
    provider = serializers.ChoiceField(choices=sorted(sso.PROVIDERS))
    label = serializers.CharField(max_length=80)  # type: ignore[assignment]  # the field, not DRF's label
    issuer = serializers.URLField(max_length=2048)
    client_id = serializers.CharField(max_length=255)
    client_secret = serializers.CharField(max_length=2000, required=False, allow_blank=True, trim_whitespace=False)
    scopes = serializers.CharField(max_length=200, required=False, default="openid email profile")
    allowed_domains = serializers.ListField(child=serializers.CharField(max_length=253), min_length=1, max_length=50)
    trust_idp_mfa = serializers.BooleanField(default=False)
    sort_order = serializers.IntegerField(min_value=0, max_value=99, required=False, allow_null=True)
    status = serializers.ChoiceField(choices=["active", "inactive"], default="active")


class AdminProvidersView(APIView):
    """GET the state's sign-in providers; POST to create or change one (ADM-103, sso:manage). The client secret is
    write-only and stored encrypted."""

    required_permission = "sso:manage"

    def get(self, request: Request) -> Response:
        return Response(v.jsonable({"results": sso.configs(context.require())}))

    def post(self, request: Request) -> Response:
        s = ProviderSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        d["client_secret"] = d.get("client_secret") or None
        d.setdefault("sort_order", None)
        return Response(v.jsonable(sso.save(context.require(), **d)), status=201)


class AdminProviderCheckView(APIView):
    """POST: read the provider's discovery document and keys now."""

    required_permission = "sso:manage"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.jsonable(sso.check(context.require(), pk)))


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
        s = ReasonSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.end_session(context.require(), uuid.UUID(str(pk)), s.validated_data["reason"])
        return Response(status=204)


class AccessLevelsView(APIView):
    """GET the five levels, every role's level and the grants in scope with their effective level (FR-ADM-202)."""

    permission_classes = [Authenticated]

    def get(self, request: Request) -> Response:
        p = request.query_params
        offset = int(p["from"]) if str(p.get("from", "")).isdigit() else 0
        data = services.access_overview(context.require(), q=p.get("q", ""), offset=offset, limit=500)

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
                "total": data["total"],
                "from": data["offset"],
            }
        )


class GrantLevelSerializer(serializers.Serializer):  # type: ignore[type-arg]
    level = serializers.ChoiceField(choices=["public", "internal", "confidential", "restricted", "special"])
    reason = serializers.CharField(min_length=5, max_length=1000)


class GrantLevelView(APIView):
    """PUT the access level of one grant (lower it, or restore the role's level) with a reason (FR-ADM-202)."""

    permission_classes = [Authenticated]

    def put(self, request: Request, pk: str) -> Response:
        s = GrantLevelSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.set_grant_cap(
            context.require(), uuid.UUID(str(pk)), s.validated_data["level"], s.validated_data["reason"]
        )
        return Response(status=204)


class OfficesView(APIView):
    """GET the offices in scope (state, boards, agencies, LGA offices) with the address shown at sign-in."""

    permission_classes = [Authenticated]

    def get(self, request: Request) -> Response:
        return Response({"results": services.offices(context.require())})


class OfficeAddressSerializer(serializers.Serializer):  # type: ignore[type-arg]
    office = serializers.CharField(max_length=160, required=False, allow_blank=True, default="")
    street = serializers.CharField(max_length=160)
    town = serializers.CharField(max_length=160)
    lga = serializers.CharField(max_length=160, required=False, allow_blank=True, default="")
    state = serializers.CharField(max_length=160, required=False, allow_blank=True, default="")
    postcode = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    reason = serializers.CharField(min_length=5, max_length=1000)


class OfficeAddressView(APIView):
    """PUT an office's name and address as shown at sign-in, with a reason (FR-AUT-101)."""

    permission_classes = [Authenticated]

    def put(self, request: Request, pk: str) -> Response:
        s = OfficeAddressSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        reason = d.pop("reason")
        services.set_office_address(context.require(), uuid.UUID(str(pk)), d, reason)
        return Response(status=204)


class GrantOfficeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    office_id = serializers.UUIDField(allow_null=True)
    reason = serializers.CharField(min_length=5, max_length=1000)


class GrantOfficeView(APIView):
    """PUT the office a grant's holder works in (or null for the grant's own scope), with a reason."""

    permission_classes = [Authenticated]

    def put(self, request: Request, pk: str) -> Response:
        s = GrantOfficeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.set_grant_office(
            context.require(), uuid.UUID(str(pk)), s.validated_data["office_id"], s.validated_data["reason"]
        )
        return Response(status=204)
