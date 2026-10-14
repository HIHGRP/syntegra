from syntegra.iam import services


def test_totp_rfc6238_vector() -> None:
    seed = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"  # "12345678901234567890"
    assert services.totp(seed, at=59, digits=8)[-6:] == "287082"
    assert services.totp_valid(seed, services.totp(seed, at=1_000_000), at=1_000_015)


def test_password_hashing() -> None:
    h = services.hash_password("a long enough passphrase")
    assert h.startswith("$argon2id$")
    assert services.verify_password(h, "a long enough passphrase")
    assert not services.verify_password(h, "wrong")
