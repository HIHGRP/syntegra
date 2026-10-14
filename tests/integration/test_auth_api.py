import pytest

pytestmark = pytest.mark.django_db(databases="__all__")


def test_sign_in_me_and_role_scoped_permissions(world, api, client) -> None:  # type: ignore[no-untyped-def]
    call = api("TCH", world.institution.scope_node_id)
    r = call("get", "/api/v1/me")
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "TCH" and "attendance:mark" in body["permissions"]
    assert call("post", "/api/v1/institutions", {}).status_code == 403


def test_unauthenticated_requests_get_problem_json(world, client) -> None:  # type: ignore[no-untyped-def]
    r = client.get("/api/v1/learners")
    assert r.status_code in (401, 403)
    assert r["Content-Type"].startswith("application/problem+json")
    assert r.json()["type"].startswith("https://errors.syntegra.io/")


def test_lockout_after_five_failures(world, client) -> None:  # type: ignore[no-untyped-def]
    from tests.conftest import make_user

    u, _ = make_user(world, "TCH", world.institution.scope_node_id)
    for _ in range(5):
        r = client.post("/api/v1/auth/sign-in", {"username": u.username, "password": "nope"},
                        content_type="application/json")
        assert r.status_code == 401
    r = client.post("/api/v1/auth/sign-in", {"username": u.username, "password": "correct-horse-battery"},
                    content_type="application/json")
    assert r.status_code == 401 and r.json()["code"] == "AUTH-LOCKED"


def test_sign_out_revokes_the_session(world, api) -> None:  # type: ignore[no-untyped-def]
    call = api("HT", world.institution.scope_node_id)
    assert call("post", "/api/v1/auth/sign-out").status_code == 204
    assert call("get", "/api/v1/me").status_code in (401, 403)
