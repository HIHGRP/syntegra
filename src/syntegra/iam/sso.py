"""Single sign-on with a state's identity providers by OpenID Connect (CR-003 FR-AUT-04–06, CR-008 FR-AUT-106).

Authorization code flow with PKCE, a confidential client per provider (``identity_provider_config``):

1. ``start`` sends the browser to the provider with a fresh ``state``, ``nonce`` and PKCE challenge; the three secrets
   travel in a short-lived signed cookie, never in the database.
2. ``finish`` checks ``state``, exchanges the code (with the PKCE verifier and the client secret) at the provider's
   token endpoint, and verifies the ID token: signature against the provider's published keys (RS256/PS256/ES256),
   issuer, audience, expiry and nonce.
3. The person is matched to an account the state already created — by the provider's subject once linked, otherwise
   by an e-mail address the provider marks as verified, in a domain allowed for that provider. Nothing is created:
   roles and scope are only ever granted by the state.
4. The session is opened as for a password sign-in (one session per account, school or office confirmed next). The
   provider's MFA counts as the second factor only where the state trusts that provider; otherwise the local code
   is asked for, and a user whose roles need one and who has none is taken to enrolment.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import secrets
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.db import transaction

from syntegra.core import audit, authz, crypto
from syntegra.core.context import Context
from syntegra.core.errors import DomainError, HardValidation, NotFound
from syntegra.core.fields import utcnow
from syntegra.core.tenancy import TenantInfo
from syntegra.iam import mfa as mfa_mod
from syntegra.iam.models import AppUser, IdentityProviderConfig

PROVIDERS = {"gov_sso": "State government ID", "entra": "Microsoft Entra ID", "google": "Google Workspace"}
ALGORITHMS = ["RS256", "PS256", "ES256"]
COOKIE = "syntegra_sso"
COOKIE_AGE = 600  # seconds the person has to complete the provider's sign-in
SALT = "syntegra.iam.sso"
MFA_AMR = {"mfa", "otp", "hwk", "swk", "fido", "sms", "face", "fpt", "iris", "retina", "vbm", "sc"}
DISCOVERY_TTL = 3600


class SsoFailed(DomainError):
    def __init__(self, detail: str, code: str = "AUTH-SSO") -> None:
        super().__init__(code, "Single sign-on failed", detail, 401)


# --------------------------------------------------------------------------- HTTP (replaced in tests by a fake IdP)
def _check_url(url: str) -> None:
    parts = urlsplit(url)
    allow_http = bool(getattr(settings, "SYNTEGRA_SSO_ALLOW_HTTP", False))
    if parts.scheme != "https" and not (allow_http and parts.scheme == "http"):
        raise SsoFailed(f"The provider's address must use https: {url}", "AUTH-SSO-CONFIG")


def _get_json(url: str) -> dict[str, Any]:
    import urllib.request

    _check_url(url)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})  # noqa: S310 — https checked above
    with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
        return dict(json.loads(resp.read(1_000_000)))


def _post_form(url: str, data: dict[str, str], auth: tuple[str, str] | None = None) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    _check_url(url)
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    if auth:
        from urllib.parse import quote

        pair = f"{quote(auth[0], safe='')}:{quote(auth[1], safe='')}".encode()
        headers["Authorization"] = "Basic " + base64.b64encode(pair).decode()
    req = urllib.request.Request(url, data=urlencode(data).encode(), headers=headers, method="POST")  # noqa: S310
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            return dict(json.loads(resp.read(1_000_000)))
    except urllib.error.HTTPError as exc:
        body = exc.read(4000).decode(errors="replace")
        raise SsoFailed(f"The provider refused the sign-in code ({exc.code}): {body[:300]}") from exc


# --------------------------------------------------------------------------- configuration
@dataclass(frozen=True)
class Provider:
    id: uuid.UUID
    provider: str
    label: str
    issuer: str
    client_id: str
    scopes: str
    allowed_domains: tuple[str, ...]
    trust_idp_mfa: bool
    tenant_id: uuid.UUID

    def client_secret(self) -> str:
        row = IdentityProviderConfig.unscoped.using(_alias()).get(pk=self.id)
        if not row.client_secret_enc:
            return ""
        return crypto.decrypt(bytes(row.client_secret_enc), purpose="sso-client-secret", tenant_id=self.tenant_id)


def _alias() -> str:
    from syntegra.iam.services import _alias as alias

    return alias()


def _provider(row: IdentityProviderConfig) -> Provider:
    domains = tuple(str(d).strip().lower().lstrip("@") for d in (row.allowed_domains or []) if str(d).strip())
    return Provider(
        row.id,
        row.provider,
        row.label,
        row.issuer.rstrip("/"),
        row.client_id,
        row.scopes,
        domains,
        bool(row.trust_idp_mfa),
        row.tenant_id,
    )


def enabled(tenant: TenantInfo) -> list[Provider]:
    """The providers shown on the sign-in page, in their configured order."""
    rows = IdentityProviderConfig.unscoped.using(_alias()).filter(tenant_id=tenant.state_tenant_id, status="active")
    return [_provider(r) for r in rows.order_by("sort_order", "label")]


def _enabled_one(tenant: TenantInfo, provider: str) -> Provider:
    row = (
        IdentityProviderConfig.unscoped.using(_alias())
        .filter(tenant_id=tenant.state_tenant_id, provider=provider, status="active")
        .first()
    )
    if row is None:
        raise NotFound("Sign-in provider", provider)
    return _provider(row)


def discovery(issuer: str) -> dict[str, Any]:
    key = "sso:discovery:" + hashlib.sha256(issuer.encode()).hexdigest()
    doc = cache.get(key)
    if doc is None:
        doc = _get_json(f"{issuer}/.well-known/openid-configuration")
        if str(doc.get("issuer", "")).rstrip("/") != issuer:
            raise SsoFailed("The provider's discovery document names a different issuer.", "AUTH-SSO-CONFIG")
        for field in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
            if not doc.get(field):
                raise SsoFailed(f"The provider's discovery document has no {field}.", "AUTH-SSO-CONFIG")
        cache.set(key, doc, DISCOVERY_TTL)
    return dict(doc)


def _jwks(uri: str, *, refresh: bool = False) -> dict[str, Any]:
    key = "sso:jwks:" + hashlib.sha256(uri.encode()).hexdigest()
    keys = None if refresh else cache.get(key)
    if keys is None:
        keys = _get_json(uri)
        cache.set(key, keys, DISCOVERY_TTL)
    return dict(keys)


# --------------------------------------------------------------------------- the flow
def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


@dataclass(frozen=True)
class Started:
    url: str
    cookie: str


def start(tenant: TenantInfo, provider: str, redirect_uri: str, next_url: str) -> Started:
    p = _enabled_one(tenant, provider)
    doc = discovery(p.issuer)
    state, nonce, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(32), secrets.token_urlsafe(48)
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    params = {
        "response_type": "code",
        "client_id": p.client_id,
        "redirect_uri": redirect_uri,
        "scope": p.scopes,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    if p.provider in ("entra", "google"):
        params["prompt"] = "select_account"
    sep = "&" if "?" in doc["authorization_endpoint"] else "?"
    cookie = signing.dumps(
        {"p": p.provider, "s": state, "n": nonce, "v": verifier, "next": next_url, "r": redirect_uri},
        salt=SALT,
        compress=True,
    )
    return Started(f"{doc['authorization_endpoint']}{sep}{urlencode(params)}", cookie)


@dataclass(frozen=True)
class Finished:
    sign_in: Any  # iam.services.SignIn
    next_url: str
    provider: str
    linked_now: bool


def _verify_id_token(p: Provider, doc: dict[str, Any], id_token: str, nonce: str) -> dict[str, Any]:
    import jwt

    try:
        header = jwt.get_unverified_header(id_token)
    except jwt.PyJWTError as exc:
        raise SsoFailed("The provider's ID token could not be read.") from exc
    if header.get("alg") not in ALGORITHMS:
        raise SsoFailed(f"The provider signed the ID token with {header.get('alg')}, which is not accepted.")
    key = None
    for refresh in (False, True):  # keys rotate: look again once before refusing
        jwks = jwt.PyJWKSet.from_dict(_jwks(doc["jwks_uri"], refresh=refresh))
        key = next((k for k in jwks.keys if k.key_id == header.get("kid")), None)
        if key is None and len(jwks.keys) == 1 and not header.get("kid"):
            key = jwks.keys[0]
        if key is not None:
            break
    if key is None:
        raise SsoFailed("The ID token was signed with a key the provider does not publish.")
    try:
        claims: dict[str, Any] = jwt.decode(
            id_token,
            key=key.key,
            algorithms=ALGORITHMS,
            audience=p.client_id,
            issuer=p.issuer,
            leeway=60,
            options={"require": ["exp", "iat", "sub", "aud", "iss", "nonce"]},
        )
    except jwt.PyJWTError as exc:
        raise SsoFailed(f"The provider's ID token is not valid: {exc}.") from exc
    if not hmac.compare_digest(str(claims.get("nonce")), nonce):
        raise SsoFailed("The ID token does not belong to this sign-in (nonce).")
    aud = claims.get("aud")
    if isinstance(aud, list) and len(aud) > 1 and claims.get("azp") != p.client_id:
        raise SsoFailed("The ID token was issued to another application (azp).")
    return claims


def _verified_email(p: Provider, claims: dict[str, Any]) -> str:
    email = str(claims.get("email") or "").strip().lower()
    verified = claims.get("email_verified") is True or str(claims.get("email_verified")).lower() == "true"
    if p.provider == "entra":  # Entra ID marks a verified domain owner's address with xms_edov
        verified = verified or claims.get("xms_edov") is True
    if not email or "@" not in email or not verified:
        raise SsoFailed(
            "The provider did not confirm a verified e-mail address for you, so it cannot be linked to an account.",
            "AUTH-SSO-EMAIL",
        )
    if email.rsplit("@", 1)[1] not in p.allowed_domains:
        raise SsoFailed(
            f"Addresses at {email.rsplit('@', 1)[1]} cannot sign in through {p.label}. Use your official address.",
            "AUTH-SSO-DOMAIN",
        )
    return email


def finish(
    tenant: TenantInfo,
    provider: str,
    *,
    cookie: str | None,
    code: str | None,
    state: str | None,
    error: str | None = None,
    ip: str | None = None,
    ua: str | None = None,
    current_token: str | None = None,
) -> Finished:
    try:
        saved = signing.loads(cookie or "", salt=SALT, max_age=COOKIE_AGE)
    except signing.BadSignature as exc:
        raise SsoFailed("The sign-in took too long or was started elsewhere. Start again.", "AUTH-SSO-STATE") from exc
    if saved.get("p") != provider or not state or not hmac.compare_digest(str(saved.get("s")), state):
        raise SsoFailed("The sign-in could not be matched to this browser. Start again.", "AUTH-SSO-STATE")
    if error:
        raise SsoFailed(f"The provider did not sign you in ({error[:80]}).")
    if not code:
        raise SsoFailed("The provider returned no sign-in code.")
    p = _enabled_one(tenant, provider)
    doc = discovery(p.issuer)
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": str(saved["r"]),
        "code_verifier": str(saved["v"]),
        "client_id": p.client_id,
    }
    secret = p.client_secret()
    methods = doc.get("token_endpoint_auth_methods_supported") or ["client_secret_basic"]
    auth: tuple[str, str] | None = None
    if secret and "client_secret_basic" in methods:
        auth = (p.client_id, secret)
    elif secret:
        form["client_secret"] = secret
    tokens = _post_form(doc["token_endpoint"], form, auth)
    if not tokens.get("id_token"):
        raise SsoFailed("The provider returned no ID token.")
    claims = _verify_id_token(p, doc, str(tokens["id_token"]), str(saved["n"]))
    email = _verified_email(p, claims)
    amr = {str(a).lower() for a in (claims.get("amr") or [])}
    idp_mfa = p.trust_idp_mfa and bool(amr & MFA_AMR)
    signed, linked = _sign_in(tenant, p, str(claims["sub"]), email, idp_mfa, ip, ua, current_token)
    return Finished(signed, str(saved.get("next") or "/"), p.provider, linked)


def _sign_in(
    tenant: TenantInfo,
    p: Provider,
    subject: str,
    email: str,
    idp_mfa: bool,
    ip: str | None,
    ua: str | None,
    current_token: str | None,
) -> tuple[Any, bool]:
    """Match the person to an existing active account and open its session (FR-AUT-05)."""
    from syntegra.iam import services as iam

    alias = _alias()
    now = utcnow()
    base = Context(
        tenant_id=tenant.id, state_tenant_id=tenant.state_tenant_id, actor_kind="public", ip=ip, user_agent=ua
    )
    linked = False
    refused = None
    with transaction.atomic(using=alias):
        users = AppUser.unscoped.using(alias).select_for_update().filter(tenant_id=tenant.state_tenant_id)
        user = users.filter(idp=p.provider, idp_subject=subject).first()
        if user is None:
            user = users.filter(username=email).first()
            if user is None:
                raise SsoFailed(
                    f"There is no Syntegra account for {email}. Accounts are created by the state; ask your "
                    "administrator.",
                    "AUTH-SSO-NO-ACCOUNT",
                )
            if user.idp and user.idp not in ("local", p.provider):
                raise SsoFailed("This account is linked to another sign-in provider.", "AUTH-SSO-LINKED")
            if user.idp == p.provider and user.idp_subject and user.idp_subject != subject:
                raise SsoFailed("This account is linked to another identity at this provider.", "AUTH-SSO-LINKED")
        if user.status != "active":
            raise SsoFailed("This account cannot sign in. Contact your administrator.", "AUTH-ACCOUNT-INACTIVE")
        if user.locked_until and user.locked_until > now:
            raise SsoFailed("The account is locked after repeated failures. Try again later.", "AUTH-LOCKED")
        ctx = base.with_(actor_kind="user", actor_id=user.id)
        if user.idp != p.provider or user.idp_subject != subject:
            user.idp, user.idp_subject = p.provider, subject
            user.save(using=alias)
            linked = True
            audit.write_event(
                alias,
                ctx,
                action="sso_linked",
                record_kind="app_user",
                record_id=user.id,
                field_changes=[{"field": "idp", "new": p.provider}],
            )
        refused = iam._claim_sessions(alias, user, ctx, now, current_token)
        if refused is not None:
            audit.write_event(
                alias, ctx, action="sign_in_refused_concurrent", record_kind="user_session", record_id=refused.id
            )
        else:
            method = f"sso:{p.provider}" + ("+idp_mfa" if idp_mfa else "")
            token, session_id, mfa_owed, grants = iam._open_session(
                alias, user, ctx, None, ip, ua, now, auth_method=method, mfa_at=now if idp_mfa else None
            )
            setup = not idp_mfa and not mfa_owed and mfa_mod.required_for(alias, user)
    if refused is not None:
        raise iam.SessionInUse(refused, iam.in_use_window())
    signed = iam.SignIn(
        token=token,
        session_id=session_id,
        user_id=user.id,
        mfa_required=mfa_owed,
        grants=grants,
        mfa_setup_required=setup,
    )
    return signed, linked


# --------------------------------------------------------------------------- administration (ADM-103)
def configs(ctx: Context) -> list[dict[str, Any]]:
    authz.require("sso:manage", ctx)
    rows = IdentityProviderConfig.unscoped.using(_alias()).filter(tenant_id=ctx.state_tenant_id)
    return [
        {
            "id": str(r.id),
            "provider": r.provider,
            "provider_name": PROVIDERS.get(r.provider, r.provider),
            "label": r.label,
            "issuer": r.issuer,
            "client_id": r.client_id,
            "has_secret": bool(r.client_secret_enc),
            "scopes": r.scopes,
            "allowed_domains": list(r.allowed_domains or []),
            "trust_idp_mfa": bool(r.trust_idp_mfa),
            "sort_order": r.sort_order,
            "status": r.status,
            "updated_at": r.updated_at,
        }
        for r in rows.order_by("sort_order", "label")
    ]


def save(
    ctx: Context,
    *,
    provider: str,
    label: str,
    issuer: str,
    client_id: str,
    client_secret: str | None,
    scopes: str,
    allowed_domains: list[str],
    trust_idp_mfa: bool,
    sort_order: int | None,
    status: str,
) -> dict[str, Any]:
    """Create or update a state's provider (one per kind). A blank secret keeps the stored one."""
    authz.require("sso:manage", ctx)
    errors: list[dict[str, str]] = []
    if provider not in PROVIDERS:
        errors.append({"field": "provider", "detail": "Choose the state's government ID, Entra ID or Google."})
    issuer = (issuer or "").strip().rstrip("/")
    try:
        _check_url(issuer)
    except SsoFailed as exc:
        errors.append({"field": "issuer", "detail": exc.detail or "Use an https address."})
    scope_set = (scopes or "openid email profile").split()
    if "openid" not in scope_set or "email" not in scope_set:
        errors.append({"field": "scopes", "detail": "Scopes must include openid and email."})
    domains = sorted({d.strip().lower().lstrip("@") for d in allowed_domains if d.strip()})
    if not domains or any("." not in d or " " in d for d in domains):
        errors.append({"field": "allowed_domains", "detail": "List the e-mail domains allowed, e.g. abiastate.gov.ng."})
    if len((label or "").strip()) < 3:
        errors.append({"field": "label", "detail": "Give the button text, e.g. Sign in with Abia Government ID."})
    if not (client_id or "").strip():
        errors.append({"field": "client_id", "detail": "Give the client (application) id the provider issued."})
    if status not in ("active", "inactive"):
        errors.append({"field": "status", "detail": "Active or inactive."})
    if errors:
        raise HardValidation("SSO-CONFIG", "Check the provider settings", errors[0]["detail"], errors)
    alias = _alias()
    tenant_id = ctx.state_tenant_id
    assert tenant_id is not None
    with transaction.atomic(using=alias):
        row = (
            IdentityProviderConfig.unscoped.using(alias)
            .select_for_update()
            .filter(tenant_id=tenant_id, provider=provider)
            .first()
        )
        created = row is None
        if row is None:
            row = IdentityProviderConfig(tenant_id=tenant_id, provider=provider, created_by=ctx.actor_id)
        row.label = label.strip()[:80]
        row.issuer = issuer
        row.client_id = client_id.strip()[:255]
        if client_secret:
            row.client_secret_enc = crypto.encrypt(client_secret, purpose="sso-client-secret", tenant_id=tenant_id)
        row.scopes = " ".join(dict.fromkeys(scope_set))[:200]
        row.allowed_domains = domains
        row.trust_idp_mfa = bool(trust_idp_mfa)
        row.sort_order = sort_order
        row.status = status
        row.updated_at = utcnow()
        row.updated_by = ctx.actor_id
        row.save(using=alias)
        audit.write_event(
            alias,
            ctx,
            action="sso_provider_created" if created else "sso_provider_updated",
            record_kind="identity_provider_config",
            record_id=row.id,
            field_changes=[
                {"field": "issuer", "new": issuer},
                {"field": "allowed_domains", "new": ", ".join(domains)},
                {"field": "trust_idp_mfa", "new": str(bool(trust_idp_mfa))},
                {"field": "status", "new": status},
                *([{"field": "client_secret", "new": "(replaced)"}] if client_secret else []),
            ],
        )
    cache.delete("sso:discovery:" + hashlib.sha256(issuer.encode()).hexdigest())
    return next(c for c in configs(ctx) if c["id"] == str(row.id))


def check(ctx: Context, provider_id: uuid.UUID) -> dict[str, Any]:
    """Fetch the provider's discovery document and keys now, to show the administrator it answers."""
    authz.require("sso:manage", ctx)
    row = IdentityProviderConfig.unscoped.using(_alias()).filter(pk=provider_id, tenant_id=ctx.state_tenant_id).first()
    if row is None:
        raise NotFound("Sign-in provider", provider_id)
    p = _provider(row)
    cache.delete("sso:discovery:" + hashlib.sha256(p.issuer.encode()).hexdigest())
    doc = discovery(p.issuer)
    keys = _jwks(doc["jwks_uri"], refresh=True)
    return {
        "issuer": doc["issuer"],
        "authorization_endpoint": doc["authorization_endpoint"],
        "token_endpoint": doc["token_endpoint"],
        "key_count": len(keys.get("keys", [])),
        "pkce": "S256" in (doc.get("code_challenge_methods_supported") or ["S256"]),
        "checked_at": dt.datetime.now(dt.UTC),
    }
