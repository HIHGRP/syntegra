"""The second factor on the user's own profile: authenticator enrolment, recovery codes and removal (CR-008,
FR-AUT-104/105; CR-003 FR-AUT-01–03).

* Which accounts must have one: any whose roles reach ``SYNTEGRA_MFA_REQUIRED_CLEARANCE`` (restricted by default).
  After the password such a user without a factor is taken straight to enrolment; no role applies until the
  authenticator is set up and its first code entered (``iam.services.resolve``).
* Enrolment: a new TOTP seed is kept as an inactive factor, shown as a QR code, and becomes active only when a first
  code from the app matches it. Confirming counts as passing the second factor for that session.
* Recovery codes: ten, shown once at enrolment (or when regenerated), stored only as keyed hashes; each stands in
  for the app once (``verify_mfa``).
* Adding a further factor, removing one or regenerating codes needs a session that has passed the second factor; the
  last factor of an account that needs one cannot be removed.
"""

from __future__ import annotations

import datetime as dt
import secrets
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode

from django.conf import settings
from django.db import transaction

from syntegra.core import audit, crypto
from syntegra.core.context import Context, class_rank
from syntegra.core.errors import DomainError, Forbidden, HardValidation
from syntegra.core.fields import utcnow
from syntegra.iam.models import AppUser, MfaFactor, MfaRecoveryCode, Role, RoleGrant, UserSession

RECOVERY_COUNT = 10
RECOVERY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I: written down and typed back
PENDING_FOR = dt.timedelta(minutes=30)  # an unconfirmed seed is reused on reload, then replaced


def required_level() -> str | None:
    level = str(getattr(settings, "SYNTEGRA_MFA_REQUIRED_CLEARANCE", "") or "").strip().lower()
    return level or None


def required_for(alias: str, user: AppUser, today: dt.date | None = None) -> bool:
    """Whether any role the user holds today acts at or above the level that needs a second factor."""
    from syntegra.iam.services import _grant_in_date, effective_clearance

    threshold = required_level()
    if threshold is None:
        return False
    today = today or dt.date.today()
    for g in RoleGrant.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active"):
        if not _grant_in_date(g, today):
            continue
        role = Role.unscoped.using(alias).filter(pk=g.role_id).only("clearance").first()
        if role and class_rank(effective_clearance(role.clearance, g.clearance_cap)) >= class_rank(threshold):
            return True
    return False


def has_factor(alias: str, user: AppUser) -> bool:
    return MfaFactor.unscoped.using(alias).filter(tenant_id=user.tenant_id, user_id=user.id, status="active").exists()


# --------------------------------------------------------------------------- the session asking
@dataclass(frozen=True)
class Owner:
    alias: str
    session: UserSession
    user: AppUser
    ctx: Context


def _owner(token: str) -> Owner:
    from syntegra.iam.services import AuthFailed, _alias, _token_hash

    alias = _alias()
    s = (
        UserSession.unscoped.using(alias)
        .filter(session_hash=_token_hash(token or ""), revoked_at__isnull=True, expires_at__gt=utcnow())
        .first()
    )
    if s is None:
        raise AuthFailed("Session not found.", "AUTH-SESSION")
    user = AppUser.unscoped.using(alias).filter(pk=s.user_id, status="active").first()
    if user is None:
        raise AuthFailed("This account cannot sign in. Contact your administrator.", "AUTH-ACCOUNT-INACTIVE")
    ctx = Context(tenant_id=s.tenant_id, state_tenant_id=s.tenant_id, actor_kind="user", actor_id=user.id)
    return Owner(alias, s, user, ctx)


def _need_passed(o: Owner, action: str) -> None:
    """Changing the factors of an account that has one needs a session that has passed it (FR-AUT-02)."""
    if has_factor(o.alias, o.user) and o.session.mfa_at is None:
        raise Forbidden(f"Enter the code from your authenticator app before you {action}.", code="AUTH-MFA-REQUIRED")


def status(token: str) -> dict[str, Any]:
    o = _owner(token)
    factors = MfaFactor.unscoped.using(o.alias).filter(tenant_id=o.user.tenant_id, user_id=o.user.id, status="active")
    left = MfaRecoveryCode.unscoped.using(o.alias).filter(
        tenant_id=o.user.tenant_id, user_id=o.user.id, status="active", used_at__isnull=True
    )
    return {
        "required": required_for(o.alias, o.user),
        "required_level": required_level(),
        "passed": o.session.mfa_at is not None,
        "factors": [
            {
                "id": str(f.id),
                "type": f.factor_type,
                "label": f.label or "Authenticator app",
                "added_at": f.created_at,
                "last_used_at": f.last_used_at,
            }
            for f in factors.order_by("created_at")
        ],
        "recovery_codes_left": left.count(),
    }


# --------------------------------------------------------------------------- enrolment
@dataclass(frozen=True)
class Enrolment:
    factor_id: uuid.UUID
    secret: str
    uri: str
    issuer: str
    account: str

    def qr_svg(self) -> str:
        import segno

        return str(segno.make(self.uri, error="m").svg_inline(scale=5, border=2, dark="#111", light="#fff"))

    def grouped_secret(self) -> str:
        return " ".join(self.secret[i : i + 4] for i in range(0, len(self.secret), 4))


def _issuer() -> str:
    return str(getattr(settings, "SYNTEGRA_MFA_ISSUER", "Syntegra"))


def _uri(secret: str, account: str) -> str:
    issuer = _issuer()
    label = quote(f"{issuer}:{account}")
    query = urlencode({"secret": secret, "issuer": issuer, "algorithm": "SHA1", "digits": 6, "period": 30})
    return f"otpauth://totp/{label}?{query}"


def begin(token: str, label: str = "Authenticator app") -> Enrolment:
    """A new seed for the authenticator app, kept inactive until a first code confirms it. Reloading the page within
    half an hour shows the same seed, so a code already scanned still works."""
    from syntegra.iam.services import new_totp_secret

    o = _owner(token)
    _need_passed(o, "add another authenticator")
    now = utcnow()
    with transaction.atomic(using=o.alias):
        pending = (
            MfaFactor.unscoped.using(o.alias)
            .select_for_update()
            .filter(tenant_id=o.user.tenant_id, user_id=o.user.id, status="inactive", factor_type="totp")
            .order_by("-created_at")
        )
        current = None
        for f in pending:
            if current is None and now - f.created_at <= PENDING_FOR:
                current = f
            else:  # older seeds that were never confirmed are retired
                f.status = "retired"
                f.save(using=o.alias)
        if current is not None:
            seed = crypto.decrypt(bytes(current.secret_enc or b""), purpose="mfa", tenant_id=o.user.tenant_id)
        else:
            seed = new_totp_secret()
            current = MfaFactor(
                tenant_id=o.user.tenant_id,
                user_id=o.user.id,
                factor_type="totp",
                label=(label or "Authenticator app").strip()[:80],
                secret_enc=crypto.encrypt(seed, purpose="mfa", tenant_id=o.user.tenant_id),
                status="inactive",
            )
            current.save(using=o.alias)
            audit.write_event(
                o.alias, o.ctx, action="mfa_enrolment_started", record_kind="mfa_factor", record_id=current.id
            )
    return Enrolment(current.id, seed, _uri(seed, o.user.username), _issuer(), o.user.username)


def confirm(token: str, factor_id: uuid.UUID, code: str) -> list[str]:
    """The first code from the app activates the factor, completes the second factor for this session and issues
    ten recovery codes (returned once, never stored in clear)."""
    from syntegra.iam.services import totp_step

    o = _owner(token)
    _need_passed(o, "add another authenticator")
    now = utcnow()
    with transaction.atomic(using=o.alias):
        f = (
            MfaFactor.unscoped.using(o.alias)
            .select_for_update()
            .filter(pk=factor_id, tenant_id=o.user.tenant_id, user_id=o.user.id, status="inactive")
            .first()
        )
        if f is None or now - f.created_at > PENDING_FOR:
            raise HardValidation(
                "MFA-ENROL-EXPIRED", "Start again", "This set-up has expired. Scan the new QR code and enter its code."
            )
        seed = crypto.decrypt(bytes(f.secret_enc or b""), purpose="mfa", tenant_id=o.user.tenant_id)
        step = totp_step(seed, code or "")
        if step is None:
            audit.write_event(o.alias, o.ctx, action="mfa_enrolment_failed", record_kind="mfa_factor", record_id=f.id)
            raise HardValidation(
                "MFA-CODE",
                "That code did not match",
                "Check that the phone's clock is set automatically, then type the six-digit code shown now.",
            )
        f.status = "active"
        f.last_step = step
        f.last_used_at = now
        f.save(using=o.alias)
        UserSession.unscoped.using(o.alias).filter(pk=o.session.id).update(mfa_at=now)
        audit.write_event(o.alias, o.ctx, action="mfa_enrolled", record_kind="mfa_factor", record_id=f.id)
        return _issue_codes(o, now)


def regenerate(token: str) -> list[str]:
    """Ten new recovery codes; the old ones stop working."""
    o = _owner(token)
    if not has_factor(o.alias, o.user):
        raise HardValidation("MFA-NONE", "No authenticator", "Set up an authenticator app first.")
    _need_passed(o, "make new recovery codes")
    with transaction.atomic(using=o.alias):
        return _issue_codes(o, utcnow())


def _new_code() -> str:
    raw = "".join(secrets.choice(RECOVERY_ALPHABET) for _ in range(10))
    return f"{raw[:5]}-{raw[5:]}"


def _code_hash(code: str, tenant_id: uuid.UUID) -> bytes:
    return crypto.lookup_hmac(code.replace("-", ""), scheme="mfa-recovery", tenant_id=tenant_id)


def _issue_codes(o: Owner, now: dt.datetime) -> list[str]:
    MfaRecoveryCode.unscoped.using(o.alias).filter(
        tenant_id=o.user.tenant_id, user_id=o.user.id, status="active"
    ).update(status="retired", updated_at=now)
    codes = [_new_code() for _ in range(RECOVERY_COUNT)]
    MfaRecoveryCode.unscoped.using(o.alias).bulk_create(
        [
            MfaRecoveryCode(
                tenant_id=o.user.tenant_id,
                user_id=o.user.id,
                code_hash=_code_hash(c, o.user.tenant_id),
                status="active",
            )
            for c in codes
        ]
    )
    audit.write_event(o.alias, o.ctx, action="mfa_recovery_codes_issued", record_kind="app_user", record_id=o.user.id)
    return codes


def looks_like_recovery_code(code: str) -> bool:
    c = "".join(code.split()).replace("-", "").upper()
    return len(c) == 10 and all(ch in RECOVERY_ALPHABET for ch in c)


def use_recovery_code(alias: str, user: AppUser, code: str, now: dt.datetime) -> MfaRecoveryCode | None:
    """Spend one recovery code (caller holds the transaction); None when it is not a live code of this account."""
    norm = "".join(code.split()).upper()
    rc = (
        MfaRecoveryCode.unscoped.using(alias)
        .select_for_update()
        .filter(
            tenant_id=user.tenant_id,
            user_id=user.id,
            code_hash=_code_hash(norm, user.tenant_id),
            status="active",
            used_at__isnull=True,
        )
        .first()
    )
    if rc is None:
        return None
    rc.used_at = now
    rc.status = "inactive"
    rc.save(using=alias)
    return rc


def remove(token: str, factor_id: uuid.UUID) -> None:
    """Remove an authenticator. The last one of an account whose roles need a second factor stays."""
    o = _owner(token)
    _need_passed(o, "remove an authenticator")
    now = utcnow()
    with transaction.atomic(using=o.alias):
        active = list(
            MfaFactor.unscoped.using(o.alias)
            .select_for_update()
            .filter(tenant_id=o.user.tenant_id, user_id=o.user.id, status="active")
        )
        f = next((x for x in active if x.id == factor_id), None)
        if f is None:
            raise DomainError("MFA-NOT-FOUND", "Not found", "That authenticator is not on your account.", 404)
        if len(active) == 1 and required_for(o.alias, o.user):
            raise HardValidation(
                "MFA-LAST",
                "Your roles need a second factor",
                "Add your new authenticator app first, then remove this one.",
            )
        f.status = "retired"
        f.save(using=o.alias)
        if len(active) == 1:  # no factor left: its recovery codes go with it
            MfaRecoveryCode.unscoped.using(o.alias).filter(
                tenant_id=o.user.tenant_id, user_id=o.user.id, status="active"
            ).update(status="retired", updated_at=now)
        audit.write_event(o.alias, o.ctx, action="mfa_removed", record_kind="mfa_factor", record_id=f.id)
