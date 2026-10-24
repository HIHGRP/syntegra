import datetime as dt
import uuid

import pytest

from syntegra.attendance.domain import rates
from syntegra.core import policy
from syntegra.curriculum.domain import coverage
from syntegra.financing.domain import sdaf
from syntegra.institutions.domain import duplicates
from syntegra.learners.domain import matching


def P(given: str, family: str, dob: dt.date, sex: str = "female", **kw: object) -> matching.Person:
    return matching.Person(given, family, dob, sex, **kw)  # type: ignore[arg-type]


class TestMatching:
    dob = dt.date(2014, 3, 9)

    def test_identical_records_auto_link(self) -> None:
        r = matching.compare(P("Chiamaka", "Okafor", self.dob), P("Chiamaka", "Okafor", self.dob))
        assert r.band == "auto_link" and r.score >= 0.98

    def test_name_variant_and_diacritics_still_auto_link(self) -> None:
        r = matching.compare(P("Seun", "Adébáyọ̀", self.dob, "male"), P("Oluwaseun", "Adebayo", self.dob, "male"))
        assert r.band == "auto_link"

    def test_transposed_birth_date_goes_to_review(self) -> None:
        r = matching.compare(P("Chiamaka", "Okafor", dt.date(2014, 3, 9)), P("Chiamaka", "Okafor", dt.date(2014, 9, 3)))
        assert r.band == "review"

    def test_different_child_same_name(self) -> None:
        r = matching.compare(P("Chiamaka", "Okafor", dt.date(2014, 3, 9)), P("Chiamaka", "Okafor", dt.date(2011, 6, 1)))
        assert r.band == "distinct"

    def test_nin_disagreement_vetoes_auto_link(self) -> None:
        r = matching.compare(P("Ada", "Eze", self.dob, nin_hmac=b"a"), P("Ada", "Eze", self.dob, nin_hmac=b"b"))
        assert r.band != "auto_link"


class TestPolicy:
    def test_safe_evaluation(self) -> None:
        assert policy.evaluate("rate < threshold and not excused", {"rate": 0.8, "threshold": 0.9, "excused": False})
        assert policy.evaluate("min(a, b) + abs(-2)", {"a": 3, "b": 5}) == 5

    @pytest.mark.parametrize(
        "expr", ["__import__('os')", "a.__class__", "(lambda: 1)()", "[x for x in a]", "open('f')"]
    )
    def test_rejects_unsafe_expressions(self, expr: str) -> None:
        with pytest.raises(policy.PolicyExpressionError):
            policy.evaluate(expr, {"a": [1]})

    def test_mandatory_floor_only_tightens(self) -> None:
        chain = [
            {
                "id": 1,
                "expression": "rate < threshold",
                "is_mandatory_below": True,
                "parameters": {"threshold": 0.9, "_tighten": {"threshold": "higher"}},
            },
            {"id": 2, "expression": "rate < 0.5", "is_mandatory_below": False, "parameters": {"threshold": 0.85}},
        ]
        params, conflicts, expr = policy.merge_chain(chain)
        assert params["threshold"] == 0.9 and conflicts and expr == "rate < threshold"
        chain[1]["parameters"] = {"threshold": 0.95}
        params, conflicts, _ = policy.merge_chain(chain)
        assert params["threshold"] == 0.95 and not conflicts


def test_attendance_rate_excludes_not_required() -> None:
    s = rates.summarise(["P", "L", "A", "M", "AA", "NR", "E", "P"])
    assert s.possible == 7 and s.attended == 4 and s.unauthorised_absence == 1 and s.authorised_absence == 2
    assert s.rate == round(4 / 7, 4)
    assert rates.validate_mark("L", None) and not rates.validate_mark("L", 12) and rates.validate_mark("X", None)


def test_institution_duplicate_detection() -> None:
    existing = [
        duplicates.Candidate(1, "Community Secondary School, Ogbor Hill", None, (7.3667, 5.1066), "secondary"),
        duplicates.Candidate(2, "St Mary's Primary", "AB/PS/0001", (7.40, 5.20), "primary"),
    ]
    f = duplicates.check("Ogbor Hill Community Sec. School", None, (7.3670, 5.1068), "secondary", existing)
    assert f and f[0].key == 1 and f[0].level == "soft"
    f = duplicates.check("New name", "ab/ps/0001", None, "primary", existing)
    assert f[0].level == "hard"
    assert 300 < duplicates.haversine_m((7.3667, 5.1066), (7.3667, 5.1096)) < 340


def test_coverage_invariants() -> None:
    plan, cls, sub = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    t1, t2 = uuid.uuid4(), uuid.uuid4()
    base = {"plan_id": plan, "class_id": cls, "subject_id": sub, "level": "jss_2", "learners": 38, "is_mandatory": True}
    assert [b.rule for b in coverage.evaluate(coverage.ClassSubjectFacts(**base))] == ["g2"]
    assert coverage.evaluate(coverage.ClassSubjectFacts(**base, teachers_of_record=[t1], authorised={t1: True})) == []
    rules = [
        b.rule
        for b in coverage.evaluate(
            coverage.ClassSubjectFacts(**base, teachers_of_record=[t1, t2], authorised={t1: True})
        )
    ]
    assert rules == ["g2", "g3"]
    assert coverage.add_school_days(dt.date(2026, 10, 16), 3) == dt.date(2026, 10, 21)  # Fri + 3 school days


def test_sdaf_classification_and_ube() -> None:
    a, b, c = (uuid.uuid4() for _ in range(3))
    lines = sdaf.classify(
        [
            sdaf.CensusInput(a, uuid.uuid4(), True),
            sdaf.CensusInput(b, uuid.uuid4(), False),
            sdaf.CensusInput(c, uuid.uuid4(), True),
            sdaf.CensusInput(a, uuid.uuid4(), True),
        ],
        billed_elsewhere={b},
        exempt={c},
    )
    assert sdaf.totals(lines) == {"enrolled": 3, "verified": 3, "billable": 1, "exempt": 1, "excluded": 2}
    assert sdaf.is_basic_education("jss_2", True) and not sdaf.is_basic_education("jss_2", False)
    assert not sdaf.is_basic_education("sss_1", True)
    assert sdaf.amount(10, 2, 150_000) == 1_200_000
