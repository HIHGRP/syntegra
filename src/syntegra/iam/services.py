"""Identity and session services (MFS §5.1–5.3, FR-IAM-*).

Local sign-in uses Argon2id; five failures within ten minutes lock the account for fifteen minutes. A session
token is 256 random bits returned once; only its SHA-256 is stored (``user_session.session_hash``). Sessions
expire after an idle period that depends on the active grant's clearance (30 minutes for restricted/special,
8 hours otherwise). Accounts with an active TOTP factor must complete MFA before the session carries a grant.

CR-007: after the password, the school or office of each grant (name and address, never typed by the user) is
shown and the confirmed one is copied onto the session. One account has one session: a sign-in is refused while
another session of the account is in use (activity within ``SYNTEGRA_SESSION_IN_USE_MINUTES``, 15 by default);
quieter sessions are ended as ``replaced``. Every ended session records why.
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


class SessionInUse(DomainError):
    """The account already has a session in use (CR-007, FR-AUT-102). Raised only after the password is verified."""

    def __init__(self, active: UserSession, window: dt.timedelta):
        from django.utils import timezone

        started = timezone.localtime(active.started_at)
        last = timezone.localtime(active.last_seen_at)
        free = timezone.localtime(active.last_seen_at + window)
        super().__init__(
            "AUTH-SESSION-IN-USE",
            "This account is already signed in",
            f"This account is already signed in on another device (signed in at {started:%H:%M}, last active at "
            f"{last:%H:%M}). One account cannot be used by two people at the same time. Sign out on the other "
            f"device, or try again after {free:%H:%M} if it is no longer in use. If this was not you, change your "
            "password and tell your administrator.",
            409,
            extra={"active_since": started.isoformat(), "available_after": free.isoformat()},
        )


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


TERTIARY = ("university", "polytechnic", "college_of_education", "monotechnic")


def format_address(addr: object) -> str:
    """Structured address (street, town, LGA, state, postcode) → one line; '' when nothing is recorded."""
    if not isinstance(addr, dict):
        return str(addr or "")
    parts: list[str] = []
    for key in ("street", "town", "lga", "state", "postcode"):
        v = str(addr.get(key) or "").strip()
        if not v:
            continue
        if key == "lga" and "LGA" not in v and "Local Government" not in v:
            v = f"{v} LGA"
        if key == "state" and not v.lower().endswith(("state", "territory")) and v not in ("FCT",):
            v = f"{v} State"
        if v not in parts:
            parts.append(v)
    return ", ".join(parts)


def _institution(alias: str, institution_id: uuid.UUID) -> tuple[str, object, str, str] | None:
    """Name, address, category and code of a registry institution. Read directly so that identity (imported by the
    kernel's middleware) does not depend on the institutions module."""
    import json

    from django.db import connections

    with connections[alias].cursor() as cur:
        cur.execute(
            "SELECT name, address, category, institution_code FROM institution WHERE id = %s",
            [institution_id.bytes],
        )
        row = cur.fetchone()
    if row is None:
        return None
    address = json.loads(row[1]) if isinstance(row[1], (str, bytes)) else row[1]
    return str(row[0]), address, str(row[2]), str(row[3])


def affiliation(scope_id: uuid.UUID | None, office_scope_id: uuid.UUID | None = None) -> dict[str, str]:
    """The school or office a grant belongs to: the grant's office when recorded, else its scope node. An institution
    node gives the institution's name and address; any other node its own name and office address (CR-007)."""
    from syntegra.governance.models import ScopeNode

    alias = _alias()
    node = ScopeNode.unscoped.using(alias).filter(pk=office_scope_id or scope_id).first() if scope_id else None
    if node is None:
        return {"scope_id": str(scope_id or ""), "name": "", "address": "", "kind": "", "code": ""}
    if node.ref_kind == "institution" and node.ref_id:
        inst = _institution(alias, node.ref_id)
        if inst is not None:
            name, address, category, code = inst
            return {
                "scope_id": str(node.id),
                "name": name,
                "address": format_address(address),
                "kind": "institution" if category in TERTIARY else "school",
                "code": code,
            }
    addr = getattr(node, "address", None)
    office = addr.get("office") if isinstance(addr, dict) else None
    return {
        "scope_id": str(node.id),
        "name": str(office or node.name),
        "address": format_address(addr),
        "kind": "office",
        "code": node.code,
    }


def effective_clearance(role_clearance: str, cap: str | None) -> str:
    """The level a grant acts at: the role's clearance, lowered by the grant's cap (as ``authz.grant_context``)."""
    return cap if cap and class_rank(cap) < class_rank(role_clearance) else role_clearance


def _grant_in_date(g: RoleGrant, today: dt.date) -> bool:
    return g.status == "active" and g.valid_from <= today and not (g.valid_to and g.valid_to < today)


def user_grants(user: AppUser, today: dt.date | None = None) -> list[dict[str, object]]:
    today = today or dt.date.today()
    alias = _alias()
    out: list[dict[str, object]] = []
    for g in RoleGrant.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active"):
        if not _grant_in_date(g, today):
            continue
        role = Role.unscoped.using(alias).get(pk=g.role_id)
        out.append(
            {
                "grant_id": str(g.id),
                "role": role.code,
                "role_name": role.name,
                "scope_id": str(g.scope_id),
                "access_level": effective_clearance(role.clearance, g.clearance_cap),
                "affiliation": affiliation(g.scope_id, getattr(g, "office_scope_id", None)),
            }
        )
    return out


def sign_in(
    tenant: TenantInfo,
    username: str,
    password: str,
    *,
    ip: str | None = None,
    ua: str | None = None,
    current_token: str | None = None,
) -> SignIn:
    """Password sign-in. ``current_token`` is the session the request already carries (the browser's cookie or the
    client's bearer token): signing in again from the same browser or client replaces it rather than being refused."""
    alias = _alias()
    now = utcnow()
    base = Context(
        tenant_id=tenant.id, state_tenant_id=tenant.state_tenant_id, actor_kind="public", ip=ip, user_agent=ua
    )
    failed = False
    with transaction.atomic(using=alias):
        user = (
            AppUser.unscoped.using(alias)
            .select_for_update()
            .filter(tenant_id=tenant.state_tenant_id, username=username.strip().lower())
            .first()
        )
        if user is None:
            verify_password(None, password)  # constant-ish time
            raise AuthFailed()
        if user.status in ("suspended", "deactivated", "invited"):
            raise AuthFailed("This account cannot sign in. Contact your administrator.", "AUTH-ACCOUNT-INACTIVE")
        if user.locked_until and user.locked_until > now:
            raise AuthFailed("The account is locked after repeated failures. Try again later.", "AUTH-LOCKED")
        ctx = base.with_(actor_kind="user", actor_id=user.id)
        refused: UserSession | None = None
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
            refused = _claim_sessions(alias, user, ctx, now, current_token)
            if refused is not None:
                audit.write_event(
                    alias, ctx, action="sign_in_refused_concurrent", record_kind="user_session", record_id=refused.id
                )
            else:
                token, session_id, mfa, grants = _open_session(alias, user, ctx, password, ip, ua, now)
    if failed:
        raise AuthFailed()
    if refused is not None:
        raise SessionInUse(refused, in_use_window())
    return SignIn(token=token, session_id=session_id, user_id=user.id, mfa_required=mfa, grants=grants)


def in_use_window() -> dt.timedelta:
    return dt.timedelta(minutes=int(getattr(settings, "SYNTEGRA_SESSION_IN_USE_MINUTES", 15)))


def _end(alias: str, s: UserSession, reason: str, ctx: Context | None = None, note: str | None = None) -> None:
    """End a session with its reason; audited when a context is given (caller holds the transaction)."""
    s.revoked_at = s.revoked_at or utcnow()
    s.ended_reason = reason
    s.save(using=alias)
    if ctx is not None:
        audit.write_event(
            alias,
            ctx,
            action=f"session_ended_{reason}",
            record_kind="user_session",
            record_id=s.id,
            reason=note,
        )


def _claim_sessions(
    alias: str, user: AppUser, ctx: Context, now: dt.datetime, current_token: str | None = None
) -> UserSession | None:
    """One account, one session (FR-AUT-102): the session in use, if any, else end the account's sessions.

    Not "in use": the session this request already carries (the same browser or client signing in again), and a
    session whose school or office was never confirmed — it never got past sign-in, so nothing can be done with it."""
    live = list(
        UserSession.unscoped.using(alias)
        .select_for_update()
        .filter(tenant_id=user.tenant_id, user_id=user.id, revoked_at__isnull=True, expires_at__gt=now)
        .order_by("-last_seen_at")
    )
    window = in_use_window()
    mine = _token_hash(current_token) if current_token else None
    for s in live:
        if bytes(s.session_hash) == mine or s.affiliation_confirmed_at is None:
            continue
        if now - s.last_seen_at <= window:
            return s
    for s in live:
        _end(alias, s, "replaced", ctx)
    return None


def _open_session(
    alias: str, user: AppUser, ctx: Context, password: str, ip: str | None, ua: str | None, now: dt.datetime
) -> tuple[str, uuid.UUID, bool, list[dict[str, object]]]:
    if _hasher.check_needs_rehash(user.password_hash or ""):
        user.password_hash = _hasher.hash(password)
    user.failed_attempts = 0
    user.locked_until = None
    user.last_sign_in_at = now
    user.save(using=alias)
    mfa = MfaFactor.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active").exists()
    grants = user_grants(user)
    token = secrets.token_urlsafe(32)
    single = grants[0] if len(grants) == 1 and not mfa else None
    aff: dict[str, str] = single["affiliation"] if single else {}  # type: ignore[assignment]
    s = UserSession(
        tenant_id=user.tenant_id,
        user_id=user.id,
        session_hash=_token_hash(token),
        active_grant_id=uuid.UUID(str(single["grant_id"])) if single else None,
        affiliation_scope_id=uuid.UUID(aff["scope_id"]) if aff.get("scope_id") else None,
        affiliation_name=aff.get("name") or None,
        affiliation_address=aff.get("address") or None,
        ip=ip,
        user_agent=(ua or "")[:400] or None,
        started_at=now,
        last_seen_at=now,
        expires_at=now + SESSION_MAX,
    )
    s.save(using=alias)
    audit.write_event(alias, ctx, action="sign_in", record_kind="user_session", record_id=s.id)
    return token, s.id, mfa, grants


def totp_step(secret_b32: str, code: str, at: float | None = None) -> int | None:
    """The time step of the window (previous, current, next) whose code matches, or None."""
    now = at if at is not None else time.time()
    for d in (-1, 0, 1):
        t = now + d * 30
        if hmac.compare_digest(totp(secret_b32, t), code.strip()):
            return int(t // 30)
    return None


def verify_mfa(token: str, code: str) -> None:
    """Second factor for a signed-in session. Wrong codes count with wrong passwords towards the account lock (five
    within ten minutes lock it for fifteen), and a code is accepted once only (``mfa_factor.last_step``)."""
    alias = _alias()
    now = utcnow()
    failed = False
    with transaction.atomic(using=alias):
        s = (
            UserSession.unscoped.using(alias)
            .filter(session_hash=_token_hash(token), revoked_at__isnull=True, expires_at__gt=now)
            .first()
        )
        if s is None:
            raise AuthFailed("Session not found.", "AUTH-SESSION")
        user = AppUser.unscoped.using(alias).select_for_update().filter(pk=s.user_id).first()
        if user is None or user.status != "active":
            raise AuthFailed("This account cannot sign in. Contact your administrator.", "AUTH-ACCOUNT-INACTIVE")
        if user.locked_until and user.locked_until > now:
            raise AuthFailed("The account is locked after repeated failures. Try again later.", "AUTH-LOCKED")
        ctx = Context(tenant_id=s.tenant_id, state_tenant_id=s.tenant_id, actor_kind="user", actor_id=user.id)
        for f in (
            MfaFactor.unscoped.using(alias)
            .select_for_update()
            .filter(tenant_id=s.tenant_id, user_id=s.user_id, status="active", factor_type="totp")
        ):
            seed = crypto.decrypt(bytes(f.secret_enc or b""), purpose="mfa", tenant_id=s.tenant_id)
            step = totp_step(seed, code)
            if step is not None and (f.last_step is None or step > f.last_step):
                s.mfa_at = now
                f.last_used_at = now
                f.last_step = step
                f.save(using=alias)
                s.save(using=alias)
                user.failed_attempts = 0
                user.save(using=alias)
                audit.write_event(alias, ctx, action="mfa_verified", record_kind="user_session", record_id=s.id)
                return
        recent = now - (user.updated_at or now) <= LOCK_WINDOW
        user.failed_attempts = (user.failed_attempts if recent else 0) + 1
        if user.failed_attempts >= LOCK_AFTER:
            user.locked_until = now + LOCK_FOR
            user.failed_attempts = 0
        user.save(using=alias)
        audit.write_event(alias, ctx, action="mfa_failed", record_kind="user_session", record_id=s.id)
        failed = True  # commit the failure count and audit event, then refuse
    if failed:
        raise AuthFailed("The code is not valid.", "AUTH-MFA")


def enrol_totp(user: AppUser) -> str:
    """Create a TOTP factor; returns the base32 seed to show once as a QR code."""
    seed = new_totp_secret()
    f = MfaFactor(
        tenant_id=user.tenant_id,
        user_id=user.id,
        factor_type="totp",
        label="Authenticator app",
        secret_enc=crypto.encrypt(seed, purpose="mfa", tenant_id=user.tenant_id),
        status="active",
    )
    f.save(using=_alias())
    return seed


def select_grant(token: str, grant_id: uuid.UUID, *, confirm: bool = True) -> dict[str, str]:
    """Act under one of the user's grants; copies that grant's school or office onto the session (FR-AUT-101).
    ``confirm`` records that the user saw and confirmed it (the sign-in page and the API both confirm)."""
    alias = _alias()
    s = UserSession.unscoped.using(alias).filter(session_hash=_token_hash(token), revoked_at__isnull=True).first()
    if s is None:
        raise AuthFailed("Session not found.", "AUTH-SESSION")
    g = RoleGrant.unscoped.using(alias).filter(pk=grant_id, user_id=s.user_id, status="active").first()
    if g is None:
        raise Forbidden("That role is not yours.", code="AUTH-GRANT")
    if not _grant_in_date(g, dt.date.today()):
        raise Forbidden("That role is not in force today.", code="AUTH-GRANT-INACTIVE")
    aff = affiliation(g.scope_id, getattr(g, "office_scope_id", None))
    s.active_grant_id = grant_id
    s.affiliation_scope_id = uuid.UUID(aff["scope_id"]) if aff.get("scope_id") else None
    s.affiliation_name = aff.get("name") or None
    s.affiliation_address = aff.get("address") or None
    if confirm:
        s.affiliation_confirmed_at = utcnow()
    with transaction.atomic(using=alias):
        s.save(using=alias)
        if confirm:
            _audit_confirm(alias, s, aff)
    return aff


def _audit_confirm(alias: str, s: UserSession, aff: dict[str, str]) -> None:
    ctx = Context(tenant_id=s.tenant_id, state_tenant_id=s.tenant_id, actor_kind="user", actor_id=s.user_id)
    audit.write_event(
        alias,
        ctx,
        action="sign_in_affiliation_confirmed",
        record_kind="user_session",
        record_id=s.id,
        field_changes=[{"field": "affiliation", "new": f"{aff.get('name')} — {aff.get('address')}"}],
    )


def sign_out(token: str) -> None:
    alias = _alias()
    s = UserSession.unscoped.using(alias).filter(session_hash=_token_hash(token), revoked_at__isnull=True).first()
    if s is not None:
        _end(alias, s, "signed_out")


def end_reason(token: str | None) -> str | None:
    """Why the session behind a token ended (for the sign-in page), or None."""
    if not token:
        return None
    s = UserSession.unscoped.using(_alias()).filter(session_hash=_token_hash(token)).only("ended_reason").first()
    return s.ended_reason if s is not None else None


def refused_attempts(s: UserSession) -> int:
    """Sign-ins refused because this session was in use — shown to its holder (FR-AUT-102: tell both people)."""
    from django.db import connections

    with connections[_alias()].cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM audit_event WHERE tenant_id = %s AND record_kind = 'user_session' "
            "AND record_id = %s AND action = 'sign_in_refused_concurrent' AND occurred_at >= %s",
            [s.tenant_id.bytes, s.id.bytes, s.started_at],
        )
        row = cur.fetchone()
    return int(row[0]) if row else 0


def _drop_grant(alias: str, s: UserSession) -> None:
    """The session's grant is no longer in force: clear it and the confirmation, so the next page is AUT-03."""
    s.active_grant_id = None
    s.affiliation_confirmed_at = None
    UserSession.unscoped.using(alias).filter(pk=s.id).update(active_grant_id=None, affiliation_confirmed_at=None)


def _idle_limit(clearance: str) -> dt.timedelta:
    limits = getattr(settings, "SYNTEGRA_SESSION_IDLE_MINUTES", {})
    key = "restricted" if class_rank(clearance) >= class_rank("restricted") else "default"
    return dt.timedelta(minutes=int(limits.get(key, 480)))


def resolve(token: str, base: Context) -> tuple[Context, UserSession] | None:
    """Session token → user context (with the active grant expanded) or None when invalid/expired."""
    alias = _alias()
    s = (
        UserSession.unscoped.using(alias)
        .filter(session_hash=_token_hash(token), tenant_id=base.state_tenant_id, revoked_at__isnull=True)
        .first()
    )
    now = utcnow()
    if s is None:
        return None
    if s.expires_at <= now:
        _end(alias, s, "expired")
        return None
    user = AppUser.unscoped.using(alias).filter(pk=s.user_id).first()
    if user is None or user.status != "active":
        _end(alias, s, "account_inactive")
        return None
    mfa_needed = (
        MfaFactor.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active").exists()
    )
    s.mfa_pending = bool(mfa_needed and not s.mfa_at)  # type: ignore[attr-defined]  # read by the page wrapper
    ctx = base.with_(
        actor_kind="user", actor_id=user.id, clearance="public", permissions=frozenset(), scope_ids=frozenset()
    )
    # The grant applies once MFA is done and the school or office has been confirmed (FR-AUT-101) — on the pages
    # and the API alike. A grant that has ended since (revoked, expired, moved by a posting) is dropped from the
    # session: the person is asked to choose again instead of every request being refused.
    if s.active_grant_id and (s.mfa_at or not mfa_needed) and s.affiliation_confirmed_at:
        try:
            ctx = authz.grant_context(ctx, s.active_grant_id)
        except Forbidden:
            _drop_grant(alias, s)
    if now - s.last_seen_at > _idle_limit(ctx.clearance):
        _end(alias, s, "idle_timeout")
        return None
    if now - s.last_seen_at > dt.timedelta(minutes=1):  # throttle last-seen writes
        UserSession.unscoped.using(alias).filter(pk=s.id).update(last_seen_at=now)
    return ctx, s


def create_user(
    ctx: Context,
    *,
    username: str,
    display_name: str,
    password: str | None,
    person_kind: str = "staff",
    phone: str | None = None,
    person_id: uuid.UUID | None = None,
) -> AppUser:
    alias = _alias()
    with transaction.atomic(using=alias):
        u = AppUser(
            tenant_id=ctx.state_tenant_id,
            username=username.strip().lower(),
            display_name=display_name,
            phone=phone,
            person_kind=person_kind,
            person_id=person_id,
            idp="local",
            password_hash=hash_password(password) if password else None,
            status="active" if password else "invited",
        )
        u.save(using=alias)
        audit.write_event(
            alias,
            ctx,
            action="create",
            record_kind="app_user",
            record_id=u.id,
            field_changes=[{"field": "username", "new": u.username}],
        )
    return u


def grant_role(
    ctx: Context,
    *,
    user: AppUser,
    role_code: str,
    scope_id: uuid.UUID,
    valid_from: dt.date | None = None,
    office_scope_id: uuid.UUID | None = None,
) -> RoleGrant:
    """Grant a role at a scope. ``office_scope_id`` is the office the person works in when the scope is wider (a
    ministry official with state-wide scope): its name and address are shown at sign-in (CR-007, FR-AUT-101)."""
    alias = _alias()
    role = Role.unscoped.using(alias).get(tenant_id=ctx.state_tenant_id, code=role_code)
    if office_scope_id is not None:
        _office_node(ctx, office_scope_id)
    with transaction.atomic(using=alias):
        g = RoleGrant(
            tenant_id=ctx.state_tenant_id,
            user_id=user.id,
            role_id=role.id,
            scope_id=scope_id,
            office_scope_id=office_scope_id,
            granted_by_id=ctx.actor_id if ctx.actor_kind == "user" else None,
            status="active",
            valid_from=valid_from or dt.date.today(),
        )
        g.save(using=alias)
        audit.write_event(
            alias,
            ctx,
            action="grant",
            record_kind="role_grant",
            record_id=g.id,
            field_changes=[
                {"field": "role", "new": role_code},
                {"field": "scope_id", "new": str(scope_id)},
                *([{"field": "office_scope_id", "new": str(office_scope_id)}] if office_scope_id else []),
            ],
        )
    return g


# --------------------------------------------------------------------------- offices shown at sign-in (CR-007)
OFFICE_LEVELS = ("state", "authority", "agency", "formation", "lga", "network")
ADDRESS_FIELDS = ("office", "street", "town", "lga", "state", "postcode")


def _office_node(ctx: Context, node_id: uuid.UUID) -> object:
    """An office (a scope node that is not an institution) in the caller's scope."""
    from syntegra.core.errors import NotFound
    from syntegra.governance.models import ScopeNode

    node = ScopeNode.unscoped.using(_alias()).filter(pk=node_id, tenant_id=ctx.state_tenant_id).first()
    if node is None or node.level not in OFFICE_LEVELS:
        raise NotFound("Office", node_id)
    if ctx.scope_ids is not None and not ctx.is_system and node.id not in ctx.scope_ids:
        raise NotFound("Office", node_id)
    return node


def offices(ctx: Context) -> list[dict[str, object]]:
    """Offices in the caller's scope — the state, its boards and agencies, LGA education offices — with the
    address shown at sign-in to people who work there."""
    from syntegra.governance.models import ScopeNode

    authz.require("access:manage", ctx)
    q = ScopeNode.unscoped.using(_alias()).filter(tenant_id=ctx.state_tenant_id, level__in=OFFICE_LEVELS)
    if ctx.scope_ids is not None and not ctx.is_system:
        q = q.filter(id__in=list(ctx.scope_ids))
    out: list[dict[str, object]] = []
    for n in q.order_by("depth", "name")[:1000]:
        addr = n.address if isinstance(n.address, dict) else {}
        out.append(
            {
                "id": str(n.id),
                "code": n.code,
                "name": n.name,
                "level": n.level,
                "office": str(addr.get("office") or n.name),
                "address": format_address(addr),
                "fields": {k: str(addr.get(k) or "") for k in ADDRESS_FIELDS},
            }
        )
    return out


def set_office_address(ctx: Context, node_id: uuid.UUID, fields: dict[str, str], reason: str) -> None:
    """Record an office's name and address as shown at sign-in (FR-AUT-101), audited with the reason."""
    from syntegra.core import uow
    from syntegra.core.errors import HardValidation
    from syntegra.governance.models import ScopeNode

    authz.require("access:manage", ctx)
    if len((reason or "").strip()) < 5:
        raise HardValidation("OFFICE-REASON", "Give a reason", "Say why the address is changing.")
    clean = {k: " ".join(str(fields.get(k) or "").split())[:160] for k in ADDRESS_FIELDS}
    if not clean["street"] or not clean["town"]:
        raise HardValidation("OFFICE-ADDRESS", "Give the address", "Enter at least the street and the town.")
    node = _office_node(ctx, node_id)
    with uow.command("registry", "access:manage", action="office_address", record_kind="scope_node", ctx=ctx) as cmd:
        cmd.reason = reason.strip()
        locked = cmd.lock(ScopeNode, getattr(node, "id"))  # noqa: B009
        before = locked.address if isinstance(locked.address, dict) else {}
        cmd.update(locked, address={**before, **{k: v for k, v in clean.items() if v or k in before}})


def set_grant_office(ctx: Context, grant_id: uuid.UUID, office_id: uuid.UUID | None, reason: str) -> None:
    """Set the office a grant's holder works in (shown at sign-in instead of the grant's scope), or clear it."""
    from syntegra.core.errors import HardValidation, NotFound

    authz.require("access:manage", ctx)
    if len((reason or "").strip()) < 5:
        raise HardValidation("OFFICE-REASON", "Give a reason", "Say why the office is changing.")
    if office_id is not None:
        _office_node(ctx, office_id)
    alias = _alias()
    with transaction.atomic(using=alias):
        g = (
            RoleGrant.unscoped.using(alias)
            .select_for_update()
            .filter(pk=grant_id, tenant_id=ctx.state_tenant_id)
            .first()
        )
        if g is None or (ctx.scope_ids is not None and not ctx.is_system and g.scope_id not in ctx.scope_ids):
            raise NotFound("Role grant", grant_id)
        before = g.office_scope_id
        g.office_scope_id = office_id
        g.save(using=alias)
        audit.write_event(
            alias,
            ctx,
            action="office_changed",
            record_kind="role_grant",
            record_id=g.id,
            field_changes=[
                {"field": "office_scope_id", "old": str(before) if before else None, "new": str(office_id or "")}
            ],
            reason=reason.strip(),
        )


# --------------------------------------------------------------------------- administration (CR-007)
def _users_in_scope(ctx: Context) -> set[uuid.UUID]:
    q = RoleGrant.unscoped.using(_alias()).filter(tenant_id=ctx.state_tenant_id, status="active")
    if ctx.scope_ids is not None and not ctx.is_system:
        q = q.filter(scope_id__in=list(ctx.scope_ids))
    return set(q.values_list("user_id", flat=True))


def _device(ua: str | None) -> str:
    ua = ua or ""
    browser = next((b for b in ("Edg", "Chrome", "Firefox", "Safari") if b in ua), "")
    system = next((o for o in ("Android", "iPhone", "iPad", "Windows", "Mac OS X", "Linux") if o in ua), "")
    label = " on ".join(x for x in ({"Edg": "Edge"}.get(browser, browser), system) if x)
    return label or ("API client" if ua else "Unknown device")


def active_sessions(ctx: Context) -> list[dict[str, object]]:
    """Sessions in use by users in the caller's scope (FR-AUT-103)."""
    authz.require("session:manage", ctx)
    alias = _alias()
    now = utcnow()
    users = _users_in_scope(ctx)
    rows = (
        UserSession.unscoped.using(alias)
        .filter(tenant_id=ctx.state_tenant_id, revoked_at__isnull=True, expires_at__gt=now, user_id__in=list(users))
        .order_by("-last_seen_at")[:500]
    )
    people = {u.id: u for u in AppUser.unscoped.using(alias).filter(id__in=[r.user_id for r in rows])}
    grants = {g.id: g for g in RoleGrant.unscoped.using(alias).filter(id__in=[r.active_grant_id for r in rows])}
    roles = {r.id: r.code for r in Role.unscoped.using(alias).filter(id__in=[g.role_id for g in grants.values()])}
    window = in_use_window()
    out: list[dict[str, object]] = []
    for s in rows:
        u = people.get(s.user_id)
        g = grants.get(s.active_grant_id) if s.active_grant_id else None
        out.append(
            {
                "session_id": str(s.id),
                "user": u.display_name if u else str(s.user_id),
                "username": u.username if u else "",
                "role": roles.get(g.role_id, "") if g else "",
                "affiliation": s.affiliation_name or "",
                "address": s.affiliation_address or "",
                "confirmed": bool(s.affiliation_confirmed_at),
                "device": _device(s.user_agent),
                "ip": s.ip or "",
                "started_at": s.started_at,
                "last_seen_at": s.last_seen_at,
                "in_use": now - s.last_seen_at <= window,
                "is_me": ctx.actor_id == s.user_id,
            }
        )
    return out


def end_session(ctx: Context, session_id: uuid.UUID, reason: str) -> None:
    """An administrator ends a session of a user in scope, with a reason (FR-AUT-103)."""
    from syntegra.core.errors import HardValidation, NotFound

    authz.require("session:manage", ctx)
    if len((reason or "").strip()) < 5:
        raise HardValidation("SESSION-REASON", "Give a reason", "Say why the session is being ended.")
    alias = _alias()
    with transaction.atomic(using=alias):
        s = (
            UserSession.unscoped.using(alias)
            .select_for_update()
            .filter(pk=session_id, tenant_id=ctx.state_tenant_id, revoked_at__isnull=True)
            .first()
        )
        if s is None or s.user_id not in _users_in_scope(ctx):
            raise NotFound("Active session", session_id)
        _end(alias, s, "ended_by_administrator", ctx, note=reason.strip())


def access_overview(ctx: Context, *, q: str = "", offset: int = 0, limit: int = 300) -> dict[str, object]:
    """Roles with their access level and the grants in scope with their effective level (FR-ADM-202). The search
    (person, username, role or school) and the per-role holder counts run in the database over every grant in scope;
    one page of ``limit`` grants from ``offset`` is returned with the total."""
    from django.db.models import Count, Q

    from syntegra.core import access

    authz.require("access:manage", ctx)
    alias = _alias()
    roles = list(Role.unscoped.using(alias).filter(tenant_id=ctx.state_tenant_id, status="active").order_by("code"))
    base = RoleGrant.unscoped.using(alias).filter(tenant_id=ctx.state_tenant_id, status="active")
    if ctx.scope_ids is not None and not ctx.is_system:
        base = base.filter(scope_id__in=list(ctx.scope_ids))
    holders = dict(base.values_list("role_id").annotate(n=Count("id")).values_list("role_id", "n"))
    found = base
    q = (q or "").strip()
    if q:
        found = base.filter(
            Q(user__username__icontains=q)
            | Q(user__display_name__icontains=q)
            | Q(role__code__icontains=q)
            | Q(role__name__icontains=q)
            | Q(scope__name__icontains=q)
        )
    total = found.count()
    offset = max(0, offset)
    grants = list(
        found.select_related("user", "role", "scope").order_by("role__code", "user__display_name", "id")[
            offset : offset + max(1, min(limit, 1000))
        ]
    )
    rows = []
    for g in grants:
        r, u, n = g.role, g.user, g.scope
        eff = effective_clearance(r.clearance, g.clearance_cap)
        rows.append(
            {
                "grant_id": str(g.id),
                "user": u.display_name if u else "",
                "username": u.username if u else "",
                "role": r.code,
                "role_name": r.name,
                "scope": n.name if n else "",
                "office_id": str(g.office_scope_id) if g.office_scope_id else "",
                "role_level": access.level(r.clearance),
                "cap": access.level(g.clearance_cap) if g.clearance_cap else None,
                "effective": access.level(eff),
                "caps_allowed": [
                    lv
                    for lv in access.lower_or_equal(r.clearance)
                    if class_rank(lv.classification) <= class_rank(ctx.clearance)
                ],
                "is_me": g.user_id == ctx.actor_id,
            }
        )
    role_rows = [
        {"code": r.code, "name": r.name, "level": access.level(r.clearance), "holders": holders.get(r.id, 0)}
        for r in roles
    ]
    role_rows.sort(key=lambda x: (-x["level"].number, str(x["code"])))
    return {
        "levels": access.LEVELS,
        "roles": role_rows,
        "grants": rows,
        "total": total,
        "offset": offset,
        "q": q,
    }


def set_grant_cap(ctx: Context, grant_id: uuid.UUID, cap: str | None, reason: str) -> None:
    """Lower (or restore) the access level of one grant (FR-ADM-202): never above the role's level or the caller's."""
    from syntegra.core.context import CLASS_ORDER
    from syntegra.core.errors import HardValidation, NotFound

    authz.require("access:manage", ctx)
    if len((reason or "").strip()) < 5:
        raise HardValidation("ACCESS-REASON", "Give a reason", "Say why the access level is changing.")
    if cap is not None and cap not in CLASS_ORDER:
        raise HardValidation("ACCESS-LEVEL", "Unknown access level", "Choose one of the five levels.")
    alias = _alias()
    with transaction.atomic(using=alias):
        g = (
            RoleGrant.unscoped.using(alias)
            .select_for_update()
            .filter(pk=grant_id, tenant_id=ctx.state_tenant_id)
            .first()
        )
        if g is None or (ctx.scope_ids is not None and not ctx.is_system and g.scope_id not in ctx.scope_ids):
            raise NotFound("Role grant", grant_id)
        if g.user_id == ctx.actor_id:
            raise Forbidden("You cannot change the access level of your own role.", code="ACCESS-SELF")
        role = Role.unscoped.using(alias).get(pk=g.role_id)
        if cap is not None and class_rank(cap) > class_rank(role.clearance):
            raise HardValidation(
                "ACCESS-ABOVE-ROLE", "Above the role's level", "A grant can only be lowered below its role's level."
            )
        # the level the grant will act at — restoring (no cap) gives the role's own level, which must not be above
        # the administrator's either
        if class_rank(effective_clearance(role.clearance, cap)) > class_rank(ctx.clearance):
            raise Forbidden("You cannot set a level above your own.", code="ACCESS-ABOVE-OWN")
        before = g.clearance_cap
        g.clearance_cap = None if cap == role.clearance else cap
        g.save(using=alias)
        audit.write_event(
            alias,
            ctx,
            action="access_level_changed",
            record_kind="role_grant",
            record_id=g.id,
            field_changes=[{"field": "clearance_cap", "old": before, "new": g.clearance_cap}],
            reason=reason.strip(),
        )
