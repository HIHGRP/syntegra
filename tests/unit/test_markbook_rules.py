"""Marksheet and report-card rules (CR-009): positions, ordinals, the PDF's text fallback and the comments drafted
for each learner from their own results and attendance."""

from __future__ import annotations

from typing import Any

from syntegra.assessment.markbook import ordinal, positions
from syntegra.assessment.reports import _plain, draft_comments


def test_positions_share_equal_totals_and_skip() -> None:
    assert positions({"a": 70.0, "b": 82.5, "c": 70.0, "d": 41.0}) == {"b": 1, "a": 2, "c": 2, "d": 4}
    assert positions({}) == {}


def test_ordinals() -> None:
    assert [ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 22, 23, 101, 111, 112)] == [
        "1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "23rd", "101st", "111th", "112th",
    ]  # fmt: skip


def test_plain_text_for_the_builtin_font() -> None:
    assert _plain("Ọkọrọ — Ụzọ’s") == "Okoro - Uzo's"


def _learner(avg: float | None, totals: dict[str, float | None], rate: float | None, possible: int = 60) -> Any:
    return {
        "first_name": "Adaeze",
        "average": avg,
        "position": "3rd",
        "subjects": [{"subject": k, "total": v} for k, v in totals.items()],
        "attendance": {"rate": rate, "possible": possible},
    }


def test_comments_are_written_for_the_learner() -> None:
    c = draft_comments(_learner(78.4, {"Mathematics": 91, "Biology": 82, "Chemistry": 64}, 0.98), 42)
    assert c["form"].startswith("Adaeze has had an excellent term, finishing 3rd of 42 with an average of 78.4%.")
    assert "Mathematics and Biology is a real strength" in c["form"] and "Attendance has been excellent." in c["form"]
    assert c["head"] == "An outstanding result, Adaeze. Keep it up."
    c = draft_comments(_learner(46.0, {"Mathematics": 38, "English": 61, "Physics": 44}, 0.81), 40)
    assert "passed this term with an average of 46.0% (3rd of 40) but can do better" in c["form"]
    assert "The work in English is a real strength." in c["form"]
    assert "More practice is needed in Mathematics and Physics (38%, 44%)." in c["form"]
    assert "Attendance of 81% is below the 90% expected" in c["form"]
    assert c["head"] == "Adaeze must work harder next term, above all in Mathematics."
    c = draft_comments(_learner(31.0, {"Mathematics": 22, "English": 40}, None, possible=0), 40)
    assert "found this term difficult" in c["form"] and "Attendance" not in c["form"]
    assert "extra lessons in Mathematics" in c["head"]


def test_no_marks_no_judgement() -> None:
    c = draft_comments(_learner(None, {"Mathematics": None}, 0.9), 40)
    assert c == {"form": "Adaeze has no marks recorded this term.", "head": "Results to follow."}
