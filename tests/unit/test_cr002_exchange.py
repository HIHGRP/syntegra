"""CR-002 primitives: JWS ES256 messages, the state list, coverage reporting."""

import uuid

import pytest

from syntegra.clearance import federation
from syntegra.core import crypto, jws
from syntegra.core.tenancy import SEED_STATE_TENANT, state_tenant_id
from syntegra.platform.states import BY_CODE, STATES


def test_every_state_and_the_fct_once() -> None:
    codes = [c for c, _n, _cap in STATES]
    assert len(codes) == len(set(codes)) == 37 == federation.STATES_TOTAL
    assert "NG-FC" in codes and "NG-LA" in codes and "NG-AB" in codes
    assert all(cap[0].startswith(c.split("-")[1] + "-") for c, _n, cap in STATES)
    assert BY_CODE["NG-KN"][0] == "Kano State"


def test_state_tenant_ids_are_deterministic_and_keep_the_seed() -> None:
    assert state_tenant_id("NG-AB") == SEED_STATE_TENANT
    assert state_tenant_id("ng-la") == state_tenant_id("NG-LA") != state_tenant_id("NG-KN")
    assert len({state_tenant_id(c) for c, _n, _cap in STATES}) == 37


def test_jws_round_trip_and_tamper_detection() -> None:
    token = jws.sign({"iss": "NG-AB", "jti": str(uuid.uuid4()), "n": 1}, "exchange-ng-ab")
    jwk = crypto.provider().public_jwk("exchange-ng-ab")
    assert jws.verify(token, jwk)["iss"] == "NG-AB"
    assert jws.unverified_header(token) == {"alg": "ES256", "kid": "exchange-ng-ab", "typ": "JWT"}
    h, _p, s = token.split(".")
    forged = jws.b64url(b'{"iss":"NG-LA","n":1}')
    with pytest.raises(jws.JWSError):
        jws.verify(f"{h}.{forged}.{s}", jwk)
    with pytest.raises(jws.JWSError):
        jws.verify(token, crypto.provider().public_jwk("exchange-ng-la"))  # another state's key
    with pytest.raises(jws.JWSError):
        jws.verify("not.a-token", jwk)


def test_national_token_is_the_same_in_every_state_but_local_tokens_differ() -> None:
    nin = "12345678901"
    assert crypto.national_lookup_hmac(nin, scheme="NG-NIN") == crypto.national_lookup_hmac(
        " 1234 5678 901", scheme="NG-NIN"
    )
    la, ab = state_tenant_id("NG-LA"), state_tenant_id("NG-AB")
    assert crypto.lookup_hmac(nin, scheme="NG-NIN", tenant_id=la) != crypto.lookup_hmac(
        nin, scheme="NG-NIN", tenant_id=ab
    )


def test_coverage_counts_the_requesting_state_and_lists_gaps() -> None:
    P = federation.PeerResult
    results = [P("NG-LA", "matched"), P("NG-KN", "unavailable"), P("NG-OY", "possible_match")] + [
        P(c, "not_on_network") for c, _n, _cap in STATES if c not in ("NG-AB", "NG-LA", "NG-KN", "NG-OY")
    ]
    cov = federation.coverage("NG-AB", results)
    assert cov["covered"] == 3 and cov["complete"] is False
    assert cov["unavailable"] == ["NG-KN"] and len(cov["not_on_network"]) == 33
    full = federation.coverage("NG-AB", [P(c, "not_found") for c, _n, _cap in STATES if c != "NG-AB"])
    assert full["covered"] == 37 and full["complete"] is True
