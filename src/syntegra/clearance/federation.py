"""National clearance network (CR-002, FR-FCL-09..14): cross-state fee-clearance queries covering every state.

Every state registry — the 36 states and the FCT — has a row in the national directory (``exchange_peer``, platform
zone). When a learner is admitted, the admitting state signs one query per *other* state on the network and
merges the answers into its clearance check:

* **co-hosted** peers (provisioned on this platform) are answered in-process by the peer's own registry;
* **remote** peers (hosted elsewhere) are called over HTTPS at ``{endpoint}/api/v1/exchange/clearance``, in parallel,
  with a short timeout;
* peers **not on the network**, or that do not answer, are recorded as coverage gaps — never a reason to block
  or delay an admission (P9, FR-FCL-13).

Messages are compact JWS (ES256) signed with the state's exchange key and verified against the directory; replays
are refused (``query_ref`` is unique per counterpart). States never exchange NINs or ledgers: the subject is
identified by Global Learner ID, the national NIN lookup token and demographics, and an answering state returns
obligations only for a confident match (≥ 0.98). Both states log the message; the answering state notifies the
creditor institutions of a matched learner.
"""

from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Q

from syntegra.clearance.domain import rules
from syntegra.clearance.models import ClearanceExchangeQuery, LearnerObligation
from syntegra.core import context, crypto, jws, uow
from syntegra.core.errors import DomainError
from syntegra.core.fields import utcnow
from syntegra.core.tenancy import tenant_info
from syntegra.institutions.models import Institution
from syntegra.learners.domain import matching
from syntegra.learners.models import Learner
from syntegra.mdm.models import ExternalIdentifier
from syntegra.platform.models import ExchangePeer

STATES_TOTAL = 37
TTL_SECONDS = 120
REMOTE_TIMEOUT = 3.0
ALLOWED_PURPOSES = ("admission", "transfer", "re_enrolment")
ANSWERED = ("matched", "possible_match", "not_found")


class ExchangeRefused(DomainError):
    def __init__(self, reason: str):
        super().__init__("FCL-EXCHANGE-REFUSED", "Exchange message refused", reason, 403)


def _reason(exc: Exception) -> str:
    return (exc.detail if isinstance(exc, DomainError) else str(exc))[:64]


def kid_for(state_code: str) -> str:
    return f"exchange-{state_code.lower()}"


def network_active() -> bool:
    """True when at least one other state is an active member of the clearance network."""
    return ExchangePeer.objects.using("platform").filter(status="active").exclude(state_code=my_state_code()).exists()


def my_state_code() -> str:
    ctx = context.require()
    code = tenant_info(ctx.state_tenant_id).state_code
    if not code:
        raise ExchangeRefused("this tenant is not a state")
    return code


# --------------------------------------------------------------------------- subject (requesting side)
def subject_for(learner: Learner) -> dict[str, Any]:
    """What is sent about the learner: GLID, national NIN token and normalised demographics — never the NIN."""
    ident = ExternalIdentifier.objects.filter(person_kind="learner", person_id=learner.id, scheme="NG-NIN").first()
    token = None
    if ident is not None:
        token = (
            bytes(ident.value_national_hmac)
            if ident.value_national_hmac
            else crypto.national_lookup_hmac(
                crypto.decrypt(bytes(ident.value_enc), purpose="id:NG-NIN", tenant_id=ident.tenant_id), scheme="NG-NIN"
            )
        )
    return {
        "glid": learner.global_learner_id,
        "nin_token": token.hex() if token else None,
        "given": learner.legal_given_name,
        "family": learner.legal_family_name,
        "date_of_birth": learner.date_of_birth.isoformat(),
        "dob_precision": learner.dob_precision,
        "sex": learner.sex,
    }


# --------------------------------------------------------------------------- transports
@dataclass
class PeerResult:
    state_code: str
    outcome: str  # matched | possible_match | not_found | refused | unavailable | not_on_network
    obligations: list[dict[str, Any]] = field(default_factory=list)
    query_ref: uuid.UUID | None = None
    latency_ms: int | None = None
    error: str | None = None
    kid: str | None = None
    identifiers_used: list[str] = field(default_factory=list)


HttpPost = Callable[[str, dict[str, Any], float], dict[str, Any]]


def _urllib_post(url: str, body: dict[str, Any], timeout: float) -> dict[str, Any]:
    if not url.startswith("https://"):
        raise ValueError("exchange endpoints must use https")
    req = urllib.request.Request(  # noqa: S310 — https only, checked above
        url, data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return dict(json.loads(resp.read()))


http_post: HttpPost = _urllib_post  # replaced in tests to route through the Django test client


def _send(peer: ExchangePeer, token: str) -> str:
    if peer.hosting == "co_hosted":
        return answer(token)
    if not peer.endpoint_url:
        raise ExchangeRefused("remote peer has no endpoint")
    url = peer.endpoint_url.rstrip("/") + "/api/v1/exchange/clearance"
    return str(http_post(url, {"jws": token}, REMOTE_TIMEOUT)["jws"])


def _query_peer(
    peer: ExchangePeer, me: str, subject: dict[str, Any], purpose: str, requester: dict[str, str]
) -> PeerResult:
    jti = uuid.uuid4()
    now = int(time.time())
    claims = {
        "iss": me,
        "aud": peer.state_code,
        "iat": now,
        "exp": now + TTL_SECONDS,
        "jti": str(jti),
        "purpose": purpose,
        "subject": subject,
        "requester": requester,
    }
    started = time.monotonic()
    try:
        reply = _send(peer, jws.sign(claims, kid_for(me)))
        got = jws.verify(reply, peer.public_jwk or {})
        if got.get("iss") != peer.state_code or got.get("aud") != me or got.get("in_reply_to") != str(jti):
            raise jws.JWSError("answer does not match the query")
        outcome = str(got.get("match", "refused"))
        return PeerResult(
            peer.state_code,
            outcome if outcome in (*ANSWERED, "refused") else "refused",
            list(got.get("obligations") or []) if outcome == "matched" else [],
            jti,
            int((time.monotonic() - started) * 1000),
            got.get("error"),
            jws.unverified_header(reply).get("kid"),
        )
    except (jws.JWSError, ExchangeRefused) as exc:
        return PeerResult(peer.state_code, "refused", [], jti, int((time.monotonic() - started) * 1000), _reason(exc))
    except (urllib.error.URLError, TimeoutError, OSError, KeyError, ValueError) as exc:
        return PeerResult(
            peer.state_code, "unavailable", [], jti, int((time.monotonic() - started) * 1000), type(exc).__name__[:64]
        )


def query_all(learner: Learner, requesting_institution: Institution, purpose: str) -> list[PeerResult]:
    """Ask every other state in the national directory. Never raises for a peer: each gets a recorded outcome."""
    me = my_state_code()
    subject = subject_for(learner)
    requester = {"institution_code": requesting_institution.institution_code, "name": requesting_institution.name}
    peers = list(ExchangePeer.objects.using("platform").exclude(state_code=me).order_by("state_code"))
    results: list[PeerResult] = []
    remote: list[ExchangePeer] = []
    for p in peers:
        if p.status != "active" or not p.public_jwk:
            results.append(PeerResult(p.state_code, "not_on_network"))
        elif p.hosting == "co_hosted":
            results.append(_query_peer(p, me, subject, purpose, requester))
        else:
            remote.append(p)
    if len(remote) == 1:
        results.append(_query_peer(remote[0], me, subject, purpose, requester))
    elif remote:
        with ThreadPoolExecutor(max_workers=min(16, len(remote))) as pool:
            results += list(pool.map(lambda p: _query_peer(p, me, subject, purpose, requester), remote))
    used = [k for k in ("glid", "nin_token") if subject.get(k)] + ["demographics"]
    for r in results:
        if r.query_ref is not None:
            r.identifiers_used = used
    seen = [r.state_code for r in results if r.outcome in ANSWERED]
    if seen:
        ExchangePeer.objects.using("platform").filter(state_code__in=seen).update(last_seen_at=utcnow())
    return sorted(results, key=lambda r: r.state_code)


def coverage(me: str, results: list[PeerResult]) -> dict[str, Any]:
    by: dict[str, list[str]] = {
        k: [] for k in ("matched", "possible_match", "not_found", "refused", "unavailable", "not_on_network")
    }
    for r in results:
        by[r.outcome].append(r.state_code)
    answered = by["matched"] + by["possible_match"] + by["not_found"]
    return {
        "requesting_state": me,
        "states_total": STATES_TOTAL,
        "covered": len(answered) + 1,
        "complete": len(answered) + 1 == STATES_TOTAL,
        **by,
    }


def log_outbound(
    cmd: uow.Command, check_id: uuid.UUID, learner_id: uuid.UUID, purpose: str, results: list[PeerResult]
) -> None:
    for r in results:
        if r.query_ref is None:
            continue  # not on the network: no message was sent
        cmd.add(
            ClearanceExchangeQuery(
                direction="outbound",
                query_ref=r.query_ref,
                counterpart_state_code=r.state_code,
                clearance_check_id=check_id,
                learner_id=learner_id,
                purpose=purpose,
                identifiers_used=r.identifiers_used,
                match_outcome=r.outcome,
                obligations=r.obligations or None,
                total_minor=sum(int(o["amount_minor"]) for o in r.obligations if o.get("status") != "disputed"),
                currency="NGN",
                kid=r.kid,
                latency_ms=r.latency_ms,
                error=r.error,
                occurred_at=utcnow(),
            )
        )


def remote_obligations(results: list[PeerResult]) -> list[rules.Obligation]:
    out = []
    for r in results:
        for o in r.obligations:
            out.append(
                rules.Obligation(
                    uuid.UUID(o["obligation_ref"]),
                    uuid.UUID(o["creditor_ref"]),
                    str(o["creditor"]),
                    o["kind"],
                    int(o["amount_minor"]),
                    o.get("currency", "NGN"),
                    dt.date.fromisoformat(o["oldest_due_on"]),
                    o["status"],
                    r.state_code,
                )
            )
    return out


# --------------------------------------------------------------------------- answering side
def _claims_unverified(token: str) -> dict[str, Any]:
    try:
        return dict(json.loads(jws.b64url_decode(token.split(".")[1])))
    except (ValueError, IndexError) as exc:
        raise ExchangeRefused("malformed message") from exc


def answer(token: str) -> str:
    """Answer a signed query for a state hosted on this platform; returns the signed answer (or refusal)."""
    claims = _claims_unverified(token)
    iss, aud = str(claims.get("iss", "")), str(claims.get("aud", ""))
    me = ExchangePeer.objects.using("platform").filter(state_code=aud, status="active", tenant_id__isnull=False).first()
    if me is None or me.tenant_id is None:  # only registries provisioned on this platform are answered here
        raise ExchangeRefused(f"{aud} is not answered by this platform")
    caller = ExchangePeer.objects.using("platform").filter(state_code=iss).first()
    try:
        if caller is None or caller.status != "active" or not caller.public_jwk:
            raise ExchangeRefused(f"{iss} is not an active member of the clearance network")
        claims = jws.verify(token, caller.public_jwk)
        now = time.time()
        if not (claims.get("iat", 0) - 60 <= now <= claims.get("exp", 0)):
            raise ExchangeRefused("message expired")
        if claims.get("purpose") not in ALLOWED_PURPOSES:
            raise ExchangeRefused("purpose not allowed on the clearance network")
        match, obligations, _learner = _respond(me.tenant_id, claims, jws.unverified_header(token).get("kid"))
        body: dict[str, Any] = {"match": match, "obligations": obligations}
    except (jws.JWSError, ExchangeRefused) as exc:
        body = {"match": "refused", "obligations": [], "error": _reason(exc)}
    reply = {"iss": aud, "aud": iss, "iat": int(time.time()), "in_reply_to": claims.get("jti"), **body}
    return jws.sign(reply, kid_for(aud))


def _match(subject: dict[str, Any]) -> tuple[Learner | None, str]:
    token = bytes.fromhex(subject["nin_token"]) if subject.get("nin_token") else None
    person = matching.Person(
        subject["given"],
        subject["family"],
        dt.date.fromisoformat(subject["date_of_birth"]),
        subject["sex"],
        subject.get("dob_precision", "day"),
        nin_hmac=token,
    )
    by_id: dict[uuid.UUID, Learner] = {}
    if subject.get("glid"):
        for lr in Learner.objects.filter(global_learner_id=subject["glid"]).exclude(status="merged"):
            by_id[lr.id] = lr
    tokens: dict[uuid.UUID, bytes] = {}
    if token:
        for e in ExternalIdentifier.objects.filter(person_kind="learner", scheme="NG-NIN", value_national_hmac=token):
            tokens[e.person_id] = token
        for lr in Learner.objects.filter(id__in=list(tokens)).exclude(status="merged"):
            by_id[lr.id] = lr
    if not by_id:  # demographic search, blocked on family-name key or date of birth
        from syntegra.core.text import phonetic_key

        q = Q(name_phonetic__endswith=" " + phonetic_key(subject["family"])) | Q(date_of_birth=person.date_of_birth)
        for lr in Learner.objects.filter(q).exclude(status="merged")[:500]:
            by_id[lr.id] = lr
    scored = matching.best(
        person,
        [
            (
                lr,
                matching.Person(
                    lr.legal_given_name,
                    lr.legal_family_name,
                    lr.date_of_birth,
                    lr.sex,
                    lr.dob_precision,
                    nin_hmac=tokens.get(lr.id),
                ),
            )
            for lr in by_id.values()
        ],
    )
    if not scored:
        return None, "not_found"
    lr, res = scored[0]
    if res.band == "auto_link" and (len(scored) == 1 or scored[1][1].band != "auto_link"):
        return lr, "matched"
    return None, "possible_match"  # near or ambiguous match: no data leaves the state


def _respond(
    tenant_id: uuid.UUID, claims: dict[str, Any], kid: str | None
) -> tuple[str, list[dict[str, Any]], uuid.UUID | None]:
    ctx = context.system(tenant_id, tenant_id, correlation_id=str(claims.get("jti"))[:64])
    with context.use(ctx):
        learner, outcome = _match(dict(claims.get("subject") or {}))
        obligations: list[dict[str, Any]] = []
        if learner is not None:
            names = {}
            for ob in LearnerObligation.objects.filter(learner_id=learner.id, status__in=rules.OPEN):
                if ob.creditor_institution_id not in names:
                    inst = Institution.objects.filter(pk=ob.creditor_institution_id).first()
                    names[ob.creditor_institution_id] = (inst.name, inst.institution_code) if inst else ("?", "?")
                name, code = names[ob.creditor_institution_id]
                obligations.append(
                    {
                        "obligation_ref": str(ob.id),
                        "creditor_ref": str(ob.creditor_institution_id),
                        "creditor": name,
                        "creditor_code": code,
                        "kind": ob.obligation_kind,
                        "amount_minor": ob.amount_outstanding_minor,
                        "currency": ob.currency,
                        "oldest_due_on": ob.oldest_due_on.isoformat(),
                        "status": ob.status,
                    }
                )
        requester = dict(claims.get("requester") or {})
        try:
            with (
                uow.command("registry", None, action="exchange_answer", record_kind="clearance_exchange_query") as cmd,
                transaction.atomic(using=cmd.alias),
            ):
                q = cmd.add(
                    ClearanceExchangeQuery(
                        direction="inbound",
                        query_ref=uuid.UUID(str(claims["jti"])),
                        counterpart_state_code=str(claims["iss"]),
                        learner_id=learner.id if learner else None,
                        purpose=str(claims["purpose"]),
                        identifiers_used=[k for k in ("glid", "nin_token") if (claims.get("subject") or {}).get(k)]
                        + ["demographics"],
                        match_outcome=outcome,
                        obligations=obligations or None,
                        total_minor=sum(o["amount_minor"] for o in obligations if o["status"] != "disputed"),
                        currency="NGN",
                        requesting_institution=f"{requester.get('name', '?')} ({claims['iss']})"[:300],
                        kid=kid,
                        occurred_at=utcnow(),
                    )
                )
                cmd.emit(
                    "FCL.EXCHANGE_QUERY_RECEIVED",
                    aggregate_id=q.id,
                    payload={"clearance_exchange_query_id": q.id, "match_outcome": outcome},
                )
        except IntegrityError as exc:
            raise ExchangeRefused("replayed message") from exc
        return outcome, obligations, learner.id if learner else None


# --------------------------------------------------------------------------- directory (FCL-04)
def network_status(days: int = 30) -> dict[str, Any]:
    """The national directory as this state sees it: every state, its status and recent traffic both ways."""
    from django.db.models import Count

    from syntegra.clearance.models import ClearanceCheck
    from syntegra.core import authz
    from syntegra.platform.states import STATES

    authz.require("clearance:administer")
    me = my_state_code()
    since = utcnow() - dt.timedelta(days=days)
    traffic: dict[tuple[str, str], int] = {}
    for row in (
        ClearanceExchangeQuery.objects.filter(occurred_at__gte=since)
        .values("counterpart_state_code", "direction")
        .annotate(n=Count("id"))
    ):
        traffic[(row["counterpart_state_code"], row["direction"])] = row["n"]
    matched = dict(
        ClearanceExchangeQuery.objects.filter(occurred_at__gte=since, direction="outbound", match_outcome="matched")
        .values("counterpart_state_code")
        .annotate(n=Count("id"))
        .values_list("counterpart_state_code", "n")
    )
    peers = {p.state_code: p for p in ExchangePeer.objects.using("platform").all()}
    rows = []
    for code, name, _capital in STATES:
        p = peers.get(code)
        rows.append(
            {
                "state_code": code,
                "state_name": name,
                "is_self": code == me,
                "status": p.status if p else "not_on_network",
                "hosting": p.hosting if p else None,
                "endpoint_url": p.endpoint_url if p else None,
                "kid": p.kid if p else None,
                "agreement_ref": p.agreement_ref if p else None,
                "onboarded_at": p.onboarded_at if p else None,
                "last_seen_at": p.last_seen_at if p else None,
                "sent": traffic.get((code, "outbound"), 0),
                "received": traffic.get((code, "inbound"), 0),
                "matched": matched.get(code, 0),
            }
        )
    checks = list(ClearanceCheck.objects.filter(checked_at__gte=since).values_list("coverage", "federation"))
    national = [f for c, f in checks if c == "national" and f]
    active = sum(1 for r in rows if r["status"] == "active")
    return {
        "state": me,
        "states_total": STATES_TOTAL,
        "active": active,
        "not_on_network": sum(1 for r in rows if r["status"] == "not_on_network"),
        "checks": len(checks),
        "national_checks": len(national),
        "complete_checks": sum(1 for f in national if f.get("complete")),
        "average_covered": round(sum(f.get("covered", 1) for f in national) / len(national), 1) if national else None,
        "peers": rows,
        "days": days,
    }


# --------------------------------------------------------------------------- maintenance
def backfill_national_tokens(batch: int = 1000) -> int:
    """Give existing NIN identifiers of the current state their national lookup token (FR-FCL-14)."""
    n = 0
    with uow.command(
        "registry", "clearance:administer", action="backfill_tokens", record_kind="external_identifier"
    ) as cmd:
        for e in ExternalIdentifier.unscoped.using(cmd.alias).filter(
            tenant_id=cmd.ctx.state_tenant_id, scheme="NG-NIN", value_national_hmac__isnull=True
        )[:batch]:
            nin = crypto.decrypt(bytes(e.value_enc), purpose="id:NG-NIN", tenant_id=e.tenant_id)
            ExternalIdentifier.unscoped.using(cmd.alias).filter(pk=e.pk).update(
                value_national_hmac=crypto.national_lookup_hmac(nin, scheme="NG-NIN")
            )
            n += 1
        cmd.note("backfilled", None, n)
        if not n:
            cmd.audited = False
    return n


def onboard_remote(
    state_code: str, endpoint_url: str, public_jwk: dict[str, str], *, agreement_ref: str
) -> ExchangePeer:
    """Platform operator: add a state hosted elsewhere to the network (its endpoint and verification key)."""
    peer = ExchangePeer.objects.using("platform").get(state_code=state_code.upper())
    if peer.hosting == "co_hosted":
        raise ExchangeRefused(f"{state_code} is hosted on this platform")
    if not endpoint_url.startswith("https://"):
        raise ExchangeRefused("remote peers must use https")
    if public_jwk.get("kty") != "EC" or public_jwk.get("crv") != "P-256" or not public_jwk.get("x"):
        raise ExchangeRefused("the verification key must be an ES256 (P-256) JWK")
    peer.endpoint_url, peer.public_jwk, peer.agreement_ref = endpoint_url, public_jwk, agreement_ref
    peer.kid = public_jwk.get("kid") or peer.kid
    peer.status, peer.onboarded_at = "active", utcnow()
    peer.save(using="platform")
    return peer
