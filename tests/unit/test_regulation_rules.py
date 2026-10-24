"""CR-005: rules that give every institution its regulatory profile."""

from syntegra.regulation.reference import gaps, normalise_level, profile


def links(**kw):  # type: ignore[no-untyped-def]
    return {(link.body, link.relationship) for link in profile(**kw)}


def test_levels_normalise_to_national_codes() -> None:
    assert [normalise_level(x) for x in ("jss_1", "primary_4", "SSS 3", "ug100")] == ["JSS1", "PRY4", "SSS3", "UG100"]


def test_state_public_junior_secondary() -> None:
    got = links(category="junior_secondary", ownership="state", levels=["jss_1", "jss_2", "jss_3"])
    assert got >= {
        ("STATE_MOE", "supervision"),
        ("SUBEB", "supervision"),
        ("UBEC", "funding"),
        ("NERDC", "curriculum"),
        ("TRCN", "teacher_registration"),
        ("STATE_EXAM_BOARD", "examination"),
    }


def test_private_senior_secondary_is_licensed_and_examined_by_waec_and_neco() -> None:
    got = links(category="senior_secondary", ownership="private", levels=["SSS1", "SSS2", "SSS3"])
    assert ("STATE_MOE", "licensing") in got and ("WAEC", "examination") in got and ("NECO", "examination") in got
    assert ("SUBEB", "supervision") not in got


def test_unity_college_depends_on_fme_and_neco_for_entrance_and_bece() -> None:
    got = links(
        category="combined_secondary",
        ownership="federal",
        levels=["JSS1", "SSS3"],
        owner_ministry="FME",
        unity_college=True,
    )
    assert got >= {("FME", "supervision"), ("NECO", "admission"), ("NECO", "examination"), ("WAEC", "examination")}
    assert ("STATE_EXAM_BOARD", "examination") not in got


def test_tertiary_and_technical() -> None:
    uni = links(category="university", ownership="federal", levels=["UG100"], owner_ministry="FME")
    assert uni >= {("NUC", "accreditation"), ("JAMB", "admission"), ("TETFUND", "funding")}
    poly = links(category="polytechnic", ownership="private", levels=["ND"])
    assert ("NBTE", "accreditation") in poly and ("TETFUND", "funding") not in poly
    tech = links(
        category="technical_college", ownership="federal", levels=["SSS1", "NTC"], technical=True, owner_ministry="FME"
    )
    assert tech >= {("NABTEB", "examination"), ("NBTE", "accreditation")} and ("JAMB", "admission") not in tech
    nursing = links(category="school_of_nursing", ownership="federal", levels=["NURSING"])
    assert ("NMCN", "professional_regulation") in nursing


def test_gaps_are_reported() -> None:
    assert gaps([], category="university", levels=["UG100"]) == [
        "no supervising or licensing body",
        "no accrediting body",
    ]
    assert "no examination body for examined levels" in gaps(
        [("FME", "supervision")], category="combined_secondary", levels=["SSS3"]
    )
