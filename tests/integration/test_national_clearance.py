"""CR-002 national clearance network: fee-clearance checks that cover every state (FR-FCL-09..14).

Lagos (NG-LA) is provisioned on the same platform as the seed state, Abia (NG-AB). A child who owes fees at a
private school in Lagos turns up for admission in Abia; Abia's check asks every other state in the national
directory and reports exactly which states answered and which are not yet on the network.
"""

from __future__ import annotations

import datetime as dt
import time
import urllib.error
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from django.db import connections

from syntegra.core.errors import HardValidation
from tests.conftest import guardian

pytestmark = pytest.mark.django_db(databases="__all__")
NAIRA = 100
NIN = "12345678901"


# --------------------------------------------------------------------------- Lagos on the same platform
class State:
    def __init__(self, code: str) -> None:
        from syntegra.core.tenancy import state_tenant_id

        self.code = code
        self.tid = state_tenant_id(code)

    def system(self) -> Any:
        from syntegra.core import context

        return context.system(self.tid, self.tid)

    def as_user(self, role: str, scope_id: uuid.UUID) -> Any:
        from syntegra.core import authz, context
        from syntegra.core.context import Context
        from syntegra.iam import services as iam

        with context.use(self.system()):
            u = iam.create_user(
                self.system(),
                username=f"{role.lower()}-{uuid.uuid4().hex[:8]}@{self.code.lower()}.test",
                display_name=role,
                password="correct-horse-battery",
            )
            g = iam.grant_role(self.system(), user=u, role_code=role, scope_id=scope_id)
        base = Context(tenant_id=self.tid, state_tenant_id=self.tid, actor_kind="user", actor_id=u.id)
        with context.use(base):
            return context.use(authz.grant_context(base, g.id))


@pytest.fixture
def lagos(world: Any) -> Iterator[Any]:
    from syntegra.core import context, tenancy
    from syntegra.governance.models import ScopeNode
    from syntegra.institutions import services as inst
    from syntegra.platform.bootstrap import provision_state

    seeded = provision_state("NG-LA", hosts=["lagos.test"])
    la = State("NG-LA")
    la.state_scope = seeded.state_scope_id  # type: ignore[attr-defined]
    with context.use(la.system()):
        la.lga = ScopeNode.objects.get(code="LA-IKJ").id  # type: ignore[attr-defined]
    with la.as_user("STA", seeded.state_scope_id):
        la.school = inst.register(  # type: ignore[attr-defined]
            inst.RegisterInstitution(
                name="Lekki Heights Private College",
                category="secondary",
                ownership="private",
                lga_scope_id=la.lga,  # type: ignore[attr-defined]
                address={"town": "Ikeja"},
                levels=["jss_1", "sss_3"],
                location=(3.35, 6.60),
                operating_tenant_id=la.tid,
            )
        )
    yield la
    tenancy.clear_caches()


def enrol_in_lagos(la: Any, given: str = "Emeka", nin: str | None = NIN) -> Any:
    from syntegra.learners import services as learners

    with la.as_user("HEAD", la.school.scope_node_id):
        return learners.register(
            learners.RegisterLearner(
                guardians=[guardian()],
                given=given,
                family="Adeyemi",
                date_of_birth=dt.date(2010, 6, 15),
                sex="male",
                nin=nin,
                institution_id=la.school.id,
                education_level="sss_1",
                start_on=dt.date(2025, 9, 8),
            )
        ).learner


def lagos_owes(la: Any, learner: Any, amount_naira: int = 380_000) -> Any:
    from syntegra.clearance import services as fcl

    with la.as_user("FINO", la.school.scope_node_id):
        return fcl.publish(
            learner_id=learner.id,
            creditor_institution_id=la.school.id,
            kind="tuition_fees",
            amount_minor=amount_naira * NAIRA,
            oldest_due_on=dt.date(2026, 4, 1),
            evidence=[{"invoice": f"LHC-{uuid.uuid4().hex[:6]}"}],
        )


def arrive_in_abia(world: Any, as_user: Any, given: str = "Emeka", nin: str | None = NIN, **kw: Any) -> Any:
    from syntegra.learners import services as learners

    with as_user("HEAD", world.institution.scope_node_id):
        return learners.register(
            learners.RegisterLearner(
                guardians=[guardian()],
                given=given,
                family="Adeyemi",
                date_of_birth=dt.date(2010, 6, 15),
                sex="male",
                nin=nin,
                institution_id=world.institution.id,
                education_level="sss_1",
            ),
            **kw,
        )


# --------------------------------------------------------------------------- the national check
def test_directory_lists_every_state_and_the_fct(lagos: Any) -> None:
    from syntegra.platform.models import ExchangePeer
    from syntegra.platform.states import STATES

    rows = {p.state_code: p for p in ExchangePeer.objects.using("platform").all()}
    assert set(rows) == {c for c, _n, _cap in STATES} and len(rows) == 37
    assert {c for c, p in rows.items() if p.status == "active"} == {"NG-AB", "NG-LA"}
    assert rows["NG-LA"].hosting == "co_hosted" and rows["NG-LA"].tenant_id == lagos.tid
    assert rows["NG-FC"].state_name.startswith("Federal Capital Territory")


def test_lagos_debt_found_when_the_child_arrives_in_abia(world: Any, as_user: Any, lagos: Any) -> None:
    from syntegra.clearance.models import ClearanceCheck, ClearanceExchangeQuery
    from syntegra.clearance.services import ClearanceDecisionRequired, DecisionInput
    from syntegra.core import context
    from syntegra.learners.models import Enrolment, Learner

    lrn_la = enrol_in_lagos(lagos)
    lagos_owes(lagos, lrn_la)
    with pytest.raises(ClearanceDecisionRequired) as e:
        arrive_in_abia(world, as_user)
    body = e.value.problem()
    assert body["status"] == 409 and body["total_outstanding_minor"] == 380_000 * NAIRA
    (ob,) = body["obligations"]
    assert ob["state"] == "NG-LA" and ob["creditor"] == "Lekki Heights Private College"
    fed = body["federation"]
    assert fed["requesting_state"] == "NG-AB" and fed["matched"] == ["NG-LA"]
    assert fed["covered"] == 2 and fed["states_total"] == 37 and fed["complete"] is False
    assert len(fed["not_on_network"]) == 35 and "NG-FC" in fed["not_on_network"]
    with context.use(world_ctx()):
        abia = Learner.objects.get(pk=ClearanceCheck.objects.get(pk=body["clearance_check_id"]).learner_id)
        assert abia.status == "registered" and not Enrolment.objects.filter(learner_id=abia.id).exists()
        chk = ClearanceCheck.objects.get(pk=body["clearance_check_id"])
        assert chk.coverage == "national" and chk.result == "outstanding"
        out = ClearanceExchangeQuery.objects.get(clearance_check_id=chk.id)
        assert out.direction == "outbound" and out.counterpart_state_code == "NG-LA"
        assert out.match_outcome == "matched" and out.identifiers_used == ["glid", "nin_token", "demographics"]
    # Lagos logged the query it answered (and it never saw the NIN) and notified its side.
    with context.use(lagos.system()):
        inbound = ClearanceExchangeQuery.objects.get(query_ref=out.query_ref, direction="inbound")
        assert inbound.counterpart_state_code == "NG-AB" and inbound.learner_id == lrn_la.id
        assert inbound.total_minor == 380_000 * NAIRA and "Government Secondary School Aba" in str(
            inbound.requesting_institution
        )
    with connections["registry"].cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM outbox_event WHERE event_type = 'FCL.EXCHANGE_QUERY_RECEIVED' AND tenant_id = %s",
            [lagos.tid.bytes],
        )
        assert cur.fetchone()[0] == 1
    # The head decides (never a refusal); the retry enrols the same Abia learner record.
    reg = arrive_in_abia(
        world,
        as_user,
        clearance=DecisionInput(
            decision="admit_with_payment_plan",
            reason="Plan agreed with Lekki Heights bursar",
            payment_plan_ref="LHC-PP-7",
            check_id=uuid.UUID(body["clearance_check_id"]),
        ),
    )
    assert reg.outcome == "linked" and reg.learner.id == abia.id
    assert reg.enrolment is not None and reg.enrolment.institution_id == world.institution.id


def world_ctx() -> Any:
    from tests.conftest import system_ctx

    return system_ctx()


def test_match_by_demographics_when_no_nin_was_recorded(world: Any, as_user: Any, lagos: Any) -> None:
    from syntegra.clearance.services import ClearanceDecisionRequired

    lrn_la = enrol_in_lagos(lagos, nin=None)
    lagos_owes(lagos, lrn_la, 90_000)
    with pytest.raises(ClearanceDecisionRequired) as e:
        arrive_in_abia(world, as_user, nin=None)
    assert e.value.problem()["federation"]["matched"] == ["NG-LA"]
    assert e.value.problem()["total_outstanding_minor"] == 90_000 * NAIRA


def test_a_possible_match_shares_no_data(world: Any, as_user: Any, lagos: Any) -> None:
    from syntegra.clearance import federation
    from syntegra.core import context

    lrn_la = enrol_in_lagos(lagos, given="Chukwuemeka", nin=None)
    lagos_owes(lagos, lrn_la)
    subject = {
        "glid": None,
        "nin_token": None,
        "given": "Chukwuemeka",
        "family": "Adeyemi",
        "date_of_birth": "2010-06-15",
        "dob_precision": "day",
        "sex": "female",  # same name and birthday, sex recorded differently: probable, not confident
    }
    with context.use(lagos.system()):
        learner, outcome = federation._match(subject)
    assert learner is None and outcome == "possible_match"
    with context.use(lagos.system()):
        exact, outcome = federation._match({**subject, "sex": "male"})
    assert outcome == "matched" and exact is not None and exact.id == lrn_la.id


def test_no_debt_anywhere_admits_straight_away_with_coverage_recorded(world: Any, as_user: Any, lagos: Any) -> None:
    from syntegra.clearance.models import ClearanceCheck
    from syntegra.core import context

    enrol_in_lagos(lagos)  # known in Lagos, owes nothing
    reg = arrive_in_abia(world, as_user)
    assert reg.enrolment is not None and reg.learner.status == "active"
    with context.use(world_ctx()):
        chk = ClearanceCheck.objects.get(learner_id=reg.learner.id)
    assert chk.result == "clear" and chk.coverage == "national"
    assert chk.federation["not_found"] == [] and chk.federation["matched"] == ["NG-LA"]


def test_transfer_within_abia_also_asks_lagos(world: Any, as_user: Any, lagos: Any) -> None:
    from syntegra.clearance.services import ClearanceDecisionRequired
    from syntegra.learners import services as learners

    lrn_la = enrol_in_lagos(lagos)
    with as_user("HEAD", world.institution2.scope_node_id):
        # registered in Abia before the Lagos debt was published
        reg = learners.register(
            learners.RegisterLearner(
                guardians=[guardian()],
                given="Emeka",
                family="Adeyemi",
                date_of_birth=dt.date(2010, 6, 15),
                sex="male",
                nin=NIN,
                institution_id=world.institution2.id,
                education_level="jss_1",
            )
        )
    lagos_owes(lagos, lrn_la, 50_000)
    with as_user("HEAD", world.institution.scope_node_id), pytest.raises(ClearanceDecisionRequired) as e:
        learners.transfer(reg.learner.id, world.institution.id, education_level="sss_1")
    assert e.value.problem()["obligations"][0]["state"] == "NG-LA"


# --------------------------------------------------------------------------- message security
def _query(iss: str, aud: str, **over: Any) -> str:
    from syntegra.clearance import federation
    from syntegra.core import jws

    now = int(time.time())
    claims = {
        "iss": iss,
        "aud": aud,
        "iat": now,
        "exp": now + 60,
        "jti": str(uuid.uuid4()),
        "purpose": "admission",
        "subject": {"given": "Ada", "family": "Obi", "date_of_birth": "2011-01-01", "sex": "female"},
        "requester": {"name": "Test School"},
        **over,
    }
    return jws.sign(claims, federation.kid_for(iss))


def _answer(token: str, jwk: dict[str, str]) -> dict[str, Any]:
    from syntegra.clearance import federation
    from syntegra.core import jws

    return jws.verify(federation.answer(token), jwk)


def test_replayed_expired_unknown_and_suspended_messages_are_refused(lagos: Any) -> None:
    from syntegra.platform.models import ExchangePeer

    la_jwk = ExchangePeer.objects.using("platform").get(state_code="NG-LA").public_jwk
    token = _query("NG-AB", "NG-LA")
    first = _answer(token, la_jwk)
    assert first["match"] == "not_found" and first["iss"] == "NG-LA" and first["aud"] == "NG-AB"
    assert _answer(token, la_jwk) == {**_answer(token, la_jwk), "match": "refused"}
    assert _answer(token, la_jwk)["error"] == "replayed message"
    assert _answer(_query("NG-AB", "NG-LA", exp=int(time.time()) - 5), la_jwk)["error"] == "message expired"
    assert _answer(_query("NG-AB", "NG-LA", purpose="marketing"), la_jwk)["match"] == "refused"
    assert "not an active member" in _answer(_query("NG-KN", "NG-LA"), la_jwk)["error"]  # Kano not on network
    forged = _query("NG-AB", "NG-LA").rsplit(".", 1)[0] + "." + _query("NG-LA", "NG-AB").rsplit(".", 1)[1]
    assert _answer(forged, la_jwk)["error"] == "bad signature"
    ExchangePeer.objects.using("platform").filter(state_code="NG-AB").update(status="suspended")
    assert _answer(_query("NG-AB", "NG-LA"), la_jwk)["match"] == "refused"


def test_queries_for_states_not_hosted_here_are_refused(lagos: Any) -> None:
    from syntegra.clearance import federation

    with pytest.raises(federation.ExchangeRefused):
        federation.answer(_query("NG-AB", "NG-KN"))


# --------------------------------------------------------------------------- remote peers over HTTPS
def test_remote_state_answers_over_the_exchange_endpoint(
    world: Any, as_user: Any, lagos: Any, client: Any, monkeypatch: Any
) -> None:
    from syntegra.clearance import federation
    from syntegra.clearance.services import ClearanceDecisionRequired
    from syntegra.platform.models import ExchangePeer

    lrn_la = enrol_in_lagos(lagos)
    lagos_owes(lagos, lrn_la)
    # Lagos as seen from Abia: a registry hosted elsewhere, reached at its HTTPS endpoint.
    ExchangePeer.objects.using("platform").filter(state_code="NG-LA").update(
        hosting="remote", endpoint_url="https://registry.lagos.test"
    )
    calls: list[str] = []

    def via_test_client(url: str, body: dict[str, Any], timeout: float) -> dict[str, Any]:
        calls.append(url)
        r = client.post("/api/v1/exchange/clearance", body, content_type="application/json")
        assert r.status_code == 200, r.content
        return dict(r.json())

    monkeypatch.setattr(federation, "http_post", via_test_client)
    with pytest.raises(ClearanceDecisionRequired) as e:
        arrive_in_abia(world, as_user)
    assert calls == ["https://registry.lagos.test/api/v1/exchange/clearance"]
    assert e.value.problem()["federation"]["matched"] == ["NG-LA"]
    r = client.post("/api/v1/exchange/clearance", {"jws": "not-a-token"}, content_type="application/json")
    assert r.status_code == 403


def test_unreachable_state_is_a_coverage_gap_never_a_block(world: Any, as_user: Any, monkeypatch: Any) -> None:
    from syntegra.clearance import federation
    from syntegra.clearance.models import ClearanceCheck, ClearanceExchangeQuery
    from syntegra.core import context, crypto

    with context.use(world_ctx()):
        federation.onboard_remote(
            "NG-KN",
            "https://registry.kano.test",
            crypto.provider().public_jwk("exchange-ng-kn"),
            agreement_ref="NG-NCX-2026-001",
        )
        with pytest.raises(federation.ExchangeRefused):
            federation.onboard_remote("NG-KD", "http://plain.test", {"kty": "EC"}, agreement_ref="x")

    def down(url: str, body: dict[str, Any], timeout: float) -> dict[str, Any]:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(federation, "http_post", down)
    reg = arrive_in_abia(world, as_user, given="Musa", nin="98765432101")
    assert reg.enrolment is not None  # admitted: a silent state never holds up the child
    with context.use(world_ctx()):
        chk = ClearanceCheck.objects.get(learner_id=reg.learner.id)
        assert chk.result == "clear" and chk.federation["unavailable"] == ["NG-KN"]
        assert chk.federation["covered"] == 1 and len(chk.federation["not_on_network"]) == 35
        q = ClearanceExchangeQuery.objects.get(clearance_check_id=chk.id)
        assert q.match_outcome == "unavailable" and q.error == "URLError"


# --------------------------------------------------------------------------- transparency and operations
def test_family_sees_checks_made_from_other_states(world: Any, as_user: Any, lagos: Any) -> None:
    from syntegra.clearance import services as fcl
    from syntegra.clearance.services import ClearanceDecisionRequired

    lrn_la = enrol_in_lagos(lagos)
    lagos_owes(lagos, lrn_la)
    with pytest.raises(ClearanceDecisionRequired):
        arrive_in_abia(world, as_user)
    with lagos.as_user("HEAD", lagos.school.scope_node_id):
        seen = fcl.checks_about(lrn_la.id)
    (row,) = [r for r in seen if r["coverage"] == "cross_state"]
    assert row["from_state"] == "NG-AB" and row["result"] == "matched"


def test_network_page_and_status(world: Any, as_user: Any, lagos: Any, api: Any) -> None:
    from syntegra.clearance import federation
    from syntegra.core.errors import Forbidden

    with as_user("STA", world.state_scope):
        s = federation.network_status()
    assert s["state"] == "NG-AB" and s["active"] == 2 and s["not_on_network"] == 35 and len(s["peers"]) == 37
    with as_user("HEAD", world.institution.scope_node_id), pytest.raises(Forbidden):
        federation.network_status()
    sta = api("STA", world.state_scope)
    r = sta("get", "/api/v1/exchange/keys")
    assert {k["state_code"] for k in r.json()["keys"]} == {"NG-AB", "NG-LA"}


def test_national_tokens_backfilled_for_older_identifiers(world: Any, as_user: Any) -> None:
    from syntegra.clearance import federation
    from syntegra.core import context
    from syntegra.mdm.models import ExternalIdentifier

    reg = arrive_in_abia(world, as_user, given="Ngozi", nin="55566677788")
    with context.use(world_ctx()):
        ExternalIdentifier.objects.filter(person_id=reg.learner.id).update(value_national_hmac=None)
        assert federation.backfill_national_tokens() >= 1
        e = ExternalIdentifier.objects.get(person_id=reg.learner.id)
    from syntegra.core import crypto

    assert bytes(e.value_national_hmac) == crypto.national_lookup_hmac("55566677788", scheme="NG-NIN")


def test_provisioning_an_unknown_state_fails() -> None:
    from syntegra.platform.bootstrap import provision_state

    with pytest.raises(ValueError, match="not a Nigerian state"):
        provision_state("NG-XX")


def test_decision_still_required_for_lagos_debt_cannot_be_refusal(world: Any, as_user: Any, lagos: Any) -> None:
    from syntegra.clearance.services import ClearanceDecisionRequired, DecisionInput

    lrn_la = enrol_in_lagos(lagos)
    lagos_owes(lagos, lrn_la)
    with pytest.raises(ClearanceDecisionRequired) as e:
        arrive_in_abia(world, as_user)
    with pytest.raises(HardValidation):
        arrive_in_abia(
            world,
            as_user,
            clearance=DecisionInput(
                decision="refuse",
                reason="Owes Lagos school",
                check_id=uuid.UUID(e.value.problem()["clearance_check_id"]),
            ),
        )


def test_every_state_on_the_network_gives_complete_national_coverage(world: Any, as_user: Any) -> None:
    from syntegra.clearance.models import ClearanceCheck, ClearanceExchangeQuery
    from syntegra.core import context, tenancy
    from syntegra.platform.bootstrap import provision_state
    from syntegra.platform.states import STATES

    for code, _name, _capital in STATES:
        provision_state(code)
    try:
        started = time.monotonic()
        reg = arrive_in_abia(world, as_user, given="Zainab", nin="31415926535")
        elapsed = time.monotonic() - started
        with context.use(world_ctx()):
            chk = ClearanceCheck.objects.get(learner_id=reg.learner.id)
            sent = ClearanceExchangeQuery.objects.filter(clearance_check_id=chk.id).count()
        assert chk.coverage == "national" and chk.result == "clear" and reg.enrolment is not None
        assert chk.federation["covered"] == 37 and chk.federation["complete"] is True
        assert len(chk.federation["not_found"]) == 36 and chk.federation["not_on_network"] == []
        assert sent == 36  # one signed query to every other state and the FCT
        assert elapsed < 30
    finally:
        tenancy.clear_caches()
