import uuid

from syntegra.core import ids
from syntegra.core.canonical_json import canonicalize


def test_uuid7_is_time_ordered_and_version_7() -> None:
    a, b = ids.uuid7(), ids.uuid7()
    assert a.version == 7 and b.version == 7
    assert a.bytes < b.bytes


def test_glid_check_digits_detect_single_digit_errors() -> None:
    g = ids.format_glid(41185)
    assert g == "LRN-0004-1185-" + g[-2:] and ids.glid_valid(g)
    for i, ch in enumerate(g):
        if ch.isdigit() and i < 13:
            wrong = g[:i] + str((int(ch) + 1) % 10) + g[i + 1:]
            assert not ids.glid_valid(wrong)


def test_certificate_number_round_trip() -> None:
    n = ids.format_certificate_number("NG", "ABMOE", 2026, 117)
    assert n.startswith("NG-ABMOE-2026-000117") and ids.certificate_number_valid(n)
    assert not ids.certificate_number_valid(n[:-1] + ("0" if n[-1] != "0" else "1"))


def test_jcs_canonical_ordering_and_numbers() -> None:
    assert canonicalize({"b": 1, "a": [True, None, "é"]}) == '{"a":[true,null,"é"],"b":1}'.encode()
    assert canonicalize({"x": 1.0, "y": 1e21}) == b'{"x":1,"y":1e+21}'
    assert canonicalize({"id": uuid.UUID(int=1)}) == b'{"id":"00000000-0000-0000-0000-000000000001"}'


def test_es256_sign_and_verify_detects_tampering(settings: object) -> None:
    from syntegra.core import crypto

    msg = canonicalize({"number": "NG-ABMOE-2026-00011702"})
    sig = crypto.sign_es256("abia-moe-test", msg)
    jwk = crypto.provider().public_jwk("abia-moe-test")
    assert crypto.verify_es256(jwk, msg, sig)
    assert not crypto.verify_es256(jwk, msg + b" ", sig)


def test_envelope_encryption_and_lookup() -> None:
    from syntegra.core import crypto

    t = uuid.uuid4()
    blob = crypto.encrypt("12345678901", purpose="id:NG-NIN", tenant_id=t)
    assert b"12345678901" not in blob
    assert crypto.decrypt(blob, purpose="id:NG-NIN", tenant_id=t) == "12345678901"
    assert crypto.lookup_hmac("123 4567 8901", scheme="NG-NIN", tenant_id=t) == crypto.lookup_hmac(
        "12345678901", scheme="NG-NIN", tenant_id=t)
    assert crypto.lookup_hmac("12345678901", scheme="NG-NIN", tenant_id=uuid.uuid4()) != crypto.lookup_hmac(
        "12345678901", scheme="NG-NIN", tenant_id=t)
