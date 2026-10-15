"""Malformed or missing input is a 422 problem, never a 500 (regression for raw request.data access)."""

import uuid

import pytest

pytestmark = pytest.mark.django_db(databases="__all__")


def test_bad_input_returns_422_problems(world, api) -> None:  # type: ignore[no-untyped-def]
    sta = api("STA", world.state_scope)
    some = uuid.uuid4()
    cases = [
        ("/api/v1/hr/separations", {}),
        ("/api/v1/hr/separations", {"staff_post_id": "nope", "separation_kind": "resignation", "effective_on": "x"}),
        ("/api/v1/hr/promotions", {}),
        (f"/api/v1/hr/promotions/{some}/decision", {"decision": "maybe"}),
        ("/api/v1/hr/relations", {"staff_id": "nope", "case_kind": "query", "summary": "short"}),
        (
            "/api/v1/hr/payroll-runs",
            {"employer_scope_id": str(world.state_scope), "period_label": "x", "pay_date": "bad"},
        ),
        (f"/api/v1/hr/integrity/{some}/hold", {}),
        (f"/api/v1/hr/postings/{some}/decision", {"action": "explode"}),
        (f"/api/v1/hr/leave/{some}/decision", {}),
        ("/api/v1/auth/role", {"grant_id": "not-a-uuid"}),
        (f"/api/v1/clearance/disputes/{some}/resolution", {"resolution": "upheld"}),
        (f"/api/v1/reissue-cases/{some}/decision", {}),
        ("/api/v1/clearance/obligations", {"learner_id": "x"}),
    ]
    for path, body in cases:
        r = sta("post", path, body)
        assert r.status_code == 422, (path, r.status_code, r.content[:200])
        assert r["Content-Type"].startswith("application/problem+json")
    assert sta("get", "/api/v1/coverage/gaps?institution_id=bad").status_code == 422
    assert sta("get", "/api/v1/certificates?learner_id=bad").status_code == 422
    assert sta("get", "/api/v1/classes?institution_id=bad").status_code == 422
    assert sta("get", "/api/v1/institutions?lga_scope_id=bad").status_code == 422
    for path, body in [
        ("/api/v1/finance/budgets", {"institution_id": "x", "fiscal_year": "y", "lines": "z"}),
        ("/api/v1/finance/imprest", {"amount_minor": "x"}),
        (f"/api/v1/finance/imprest/{some}/retirement", {"receipts": [{}], "amount_minor": -1}),
        ("/api/v1/funding/applications", {"applicant_kind": "dog"}),
        ("/api/v1/estate/sites", {"owner": "nobody"}),
        ("/api/v1/estate/assessments", {"subject_kind": "planet", "defects": [{"severity": "zz"}]}),
    ]:
        r = sta("post", path, body)
        assert r.status_code == 422, (path, r.status_code, r.content[:200])
    assert sta("get", "/api/v1/finance/imprest?status=bogus").status_code == 422
    assert sta("get", "/api/v1/estate/infrastructure?scope_id=bad").status_code == 422
