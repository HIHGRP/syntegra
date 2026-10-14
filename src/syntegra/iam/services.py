"""Identity and session services (MFS §5.1–5.3, FR-IAM-*).

Local sign-in uses Argon2id; five failures within ten minutes lock the account for fifteen minutes. A session
token is 256 random bits returned once; only its SHA-256 is stored (``user_session.session_hash``). Sessions
expire after an idle period that depends on the active grant's clearance (30 minutes for restricted/special,
8 hours otherwise). Accounts with an active TOTP factor must complete MFA before the session carries a grant.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import secrets
import struct
import time
import uuid
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from django.conf import settings
from django.db import transaction

from syntegra.core import audit, authz, crypto
from syntegra.core.context import Context, class_rank
from syntegra.core.errors import DomainError, Forbidden
from syntegra.core.fields import utcnow
from syntegra.core.tenancy import TenantInfo
from syntegra.core.zones import current_alias
from syntegra.iam.models import AppUser, MfaFactor, Role, RoleGrant, UserSession

_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
LOCK_AFTER = 5
LOCK_WINDOW = dt.timedelta(minutes=10)
LOCK_FOR = dt.timedelta(minutes=15)
SESSION_MAX = dt.timedelta(hours=12)


class AuthFailed(DomainError):
    def __init__(self, detail: str = "The username or password is incorrect.", code: str = "AUTH-401"):
        super().__init__(code, "Sign-in failed", detail, 401)


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise DomainError("AUTH-PASSWORD-WEAK", "Password too short", "Use at least 12 characters.", 422)
    return _hasher.hash(password)


def verify_password(stored: str | None, password: str) -> bool:
    if not stored:
        return False
    try:
        return _hasher.verify(stored, password)
    except (VerificationError, InvalidHashError):
        return False


# --------------------------------------------------------------------------- TOTP (RFC 6238)
def totp(secret_b32: str, at: float | None = None, step: int = 30, digits: int = 6) -> str:
    key = base64.b32decode(secret_b32 + "=" * (-len(secret_b32) % 8), casefold=True)
    counter = int((at if at is not None else time.time()) // step)
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    off = mac[-1] & 0x0F
    code = (struct.unpack(">I", mac[off : off + 4])[0] & 0x7FFFFFFF) % (10**digits)
    return str(code).zfill(digits)


def totp_valid(secret_b32: str, code: str, at: float | None = None) -> bool:
    now = at if at is not None else time.time()
    return any(hmac.compare_digest(totp(secret_b32, now + d * 30), code.strip()) for d in (-1, 0, 1))


def new_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


# --------------------------------------------------------------------------- sessions
@dataclass(frozen=True)
class SignIn:
    token: str
    session_id: uuid.UUID
    user_id: uuid.UUID
    mfa_required: bool
    grants: list[dict[str, object]]


def _alias() -> str:
    return current_alias("registry")


def _token_hash(token: str) -> bytes:
    return hashlib.sha256(token.encode()).digest()


def user_grants(user: AppUser, today: dt.date | None = None) -> list[dict[str, object]]:
    today = today or dt.date.today()
    alias = _alias()
    out = []
    for g in RoleGrant.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active"):
        if g.valid_from > today or (g.valid_to and g.valid_to < today):
            continue
        role = Role.unscoped.using(alias).get(pk=g.role_id)
        out.append({"grant_id": str(g.id), "role": role.code, "role_name": role.name, "scope_id": str(g.scope_id)})
    return out


def sign_in(tenant: TenantInfo, username: str, password: str, *, ip: str | None = None, ua: str | None = None) -> SignIn:
    alias = _alias()
    now = utcnow()
    base = Context(tenant_id=tenant.id, state_tenant_id=tenant.state_tenant_id, actor_kind="public", ip=ip, user_agent=ua)
    failed = False
    with transaction.atomic(using=alias):
        user = (
            AppUser.unscoped.using(alias).select_for_update()
            .filter(tenant_id=tenant.state_tenant_id, username=username.strip().lower()).first()
        )
        if user is None:
            verify_password(None, password)  # constant-ish time
            raise AuthFailed()
        if user.status in ("suspended", "deactivated", "invited"):
            raise AuthFailed("This account cannot sign in. Contact your administrator.", "AUTH-ACCOUNT-INACTIVE")
        if user.locked_until and user.locked_until > now:
            raise AuthFailed("The account is locked after repeated failures. Try again later.", "AUTH-LOCKED")
        ctx = base.with_(actor_kind="user", actor_id=user.id)
        if not verify_password(user.password_hash, password):
            recent = now - (user.updated_at or now) <= LOCK_WINDOW  # updated_at = time of the previous failure
            user.failed_attempts = (user.failed_attempts if recent else 0) + 1
            if user.failed_attempts >= LOCK_AFTER:
                user.locked_until = now + LOCK_FOR
                user.failed_attempts = 0
            user.save(using=alias)
            audit.write_event(alias, ctx, action="sign_in_failed", record_kind="app_user", record_id=user.id)
            failed = True  # commit the failure count and audit event, then refuse
        else:
            token, session_id, mfa, grants = _open_session(alias, user, ctx, password, ip, ua, now)
    if failed:
        raise AuthFailed()
    return SignIn(token=token, session_id=session_id, user_id=user.id, mfa_required=mfa, grants=grants)


def _open_session(alias: str, user: AppUser, ctx: Context, password: str, ip: str | None, ua: str | None,
                  now: dt.datetime) -> tuple[str, uuid.UUID, bool, list[dict[str, object]]]:
    if _hasher.check_needs_rehash(user.password_hash or ""):
        user.password_hash = _hasher.hash(password)
    user.failed_attempts = 0
    user.locked_until = None
    user.last_sign_in_at = now
    user.save(using=alias)
    mfa = MfaFactor.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active").exists()
    grants = user_grants(user)
    token = secrets.token_urlsafe(32)
    s = UserSession(
        tenant_id=user.tenant_id, user_id=user.id, session_hash=_token_hash(token),
        active_grant_id=uuid.UUID(str(grants[0]["grant_id"])) if len(grants) == 1 and not mfa else None,
        ip=ip, user_agent=(ua or "")[:400] or None, started_at=now, last_seen_at=now, expires_at=now + SESSION_MAX,
    )
    s.save(using=alias)
    audit.write_event(alias, ctx, action="sign_in", record_kind="user_session", record_id=s.id)
    return token, s.id, mfa, grants


def verify_mfa(token: str, code: str) -> None:
    alias = _alias()
    s = UserSession.unscoped.using(alias).filter(session_hash=_token_hash(token), revoked_at__isnull=True).first()
    if s is None:
        raise AuthFailed("Session not found.", "AUTH-SESSION")
    for f in MfaFactor.unscoped.using(alias).filter(tenant_id=s.tenant_id, user_id=s.user_id, status="active", factor_type="totp"):
        seed = crypto.decrypt(bytes(f.secret_enc), purpose="mfa", tenant_id=s.tenant_id)
        if totp_valid(seed, code):
            s.mfa_at = utcnow()
            f.last_used_at = s.mfa_at
            f.save(using=alias)
            s.save(using=alias)
            return
    raise AuthFailed("The code is not valid.", "AUTH-MFA")


def enrol_totp(user: AppUser) -> str:
    """Create a TOTP factor; returns the base32 seed to show once as a QR code."""
    seed = new_totp_secret()
    f = MfaFactor(
        tenant_id=user.tenant_id, user_id=user.id, factor_type="totp", label="Authenticator app",
        secret_enc=crypto.encrypt(seed, purpose="mfa", tenant_id=user.tenant_id), status="active",
    )
    f.save(using=_alias())
    return seed


def select_grant(token: str, grant_id: uuid.UUID) -> None:
    alias = _alias()
    s = UserSession.unscoped.using(alias).filter(session_hash=_token_hash(token), revoked_at__isnull=True).first()
    if s is None:
        raise AuthFailed("Session not found.", "AUTH-SESSION")
    if not RoleGrant.unscoped.using(alias).filter(pk=grant_id, user_id=s.user_id, status="active").exists():
        raise Forbidden("That role is not yours.", code="AUTH-GRANT")
    s.active_grant_id = grant_id
    s.save(using=alias)


def sign_out(token: str) -> None:
    alias = _alias()
    s = UserSession.unscoped.using(alias).filter(session_hash=_token_hash(token), revoked_at__isnull=True).first()
    if s is not None:
        s.revoked_at = utcnow()
        s.save(using=alias)


def _idle_limit(clearance: str) -> dt.timedelta:
    limits = getattr(settings, "SYNTEGRA_SESSION_IDLE_MINUTES", {})
    key = "restricted" if class_rank(clearance) >= class_rank("restricted") else "default"
    return dt.timedelta(minutes=int(limits.get(key, 480)))


def resolve(token: str, base: Context) -> tuple[Context, UserSession] | None:
    """Session token → user context (with the active grant expanded) or None when invalid/expired."""
    alias = _alias()
    s = UserSession.unscoped.using(alias).filter(
        session_hash=_token_hash(token), tenant_id=base.state_tenant_id, revoked_at__isnull=True
    ).first()
    now = utcnow()
    if s is None or s.expires_at <= now:
        return None
    user = AppUser.unscoped.using(alias).filter(pk=s.user_id).first()
    if user is None or user.status != "active":
        return None
    mfa_needed = MfaFactor.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active").exists()
    ctx = base.with_(actor_kind="user", actor_id=user.id, clearance="public", permissions=frozenset(), scope_ids=frozenset())
    if s.active_grant_id and (s.mfa_at or not mfa_needed):
        ctx = authz.grant_context(ctx, s.active_grant_id)
    if now - s.last_seen_at > _idle_limit(ctx.clearance):
        s.revoked_at = now
        s.save(using=alias)
        return None
    if now - s.last_seen_at > dt.timedelta(minutes=1):  # throttle last-seen writes
        UserSession.unscoped.using(alias).filter(pk=s.id).update(last_seen_at=now)
    return ctx, s


def create_user(
    ctx: Context, *, username: str, display_name: str, password: str | None, person_kind: str = "staff",
    phone: str | None = None, person_id: uuid.UUID | None = None,
) -> AppUser:
    alias = _alias()
    with transaction.atomic(using=alias):
        u = AppUser(
            tenant_id=ctx.state_tenant_id, username=username.strip().lower(), display_name=display_name, phone=phone,
            person_kind=person_kind, person_id=person_id, idp="local",
            password_hash=hash_password(password) if password else None,
            status="active" if password else "invited",
        )
        u.save(using=alias)
        audit.write_event(alias, ctx, action="create", record_kind="app_user", record_id=u.id,
                          field_changes=[{"field": "username", "new": u.username}])
    return u


def grant_role(ctx: Context, *, user: AppUser, role_code: str, scope_id: uuid.UUID, valid_from: dt.date | None = None) -> RoleGrant:
    alias = _alias()
    role = Role.unscoped.using(alias).get(tenant_id=ctx.state_tenant_id, code=role_code)
    with transaction.atomic(using=alias):
        g = RoleGrant(
            tenant_id=ctx.state_tenant_id, user_id=user.id, role_id=role.id, scope_id=scope_id,
            granted_by_id=ctx.actor_id if ctx.actor_kind == "user" else None, status="active",
            valid_from=valid_from or dt.date.today(),
        )
        g.save(using=alias)
        audit.write_event(alias, ctx, action="grant", record_kind="role_grant", record_id=g.id,
                          field_changes=[{"field": "role", "new": role_code}, {"field": "scope_id", "new": str(scope_id)}])
    return g
