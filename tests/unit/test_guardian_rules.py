import datetime as dt

from syntegra.core.text import name_similarity
from syntegra.families.domain import guardians as g


def test_phone_numbers_normalise_to_e164() -> None:
    for raw in ("0803 123 4567", "+234 803 123 4567", "2348031234567", "(0803)-123-4567"):
        assert g.normalise_phone(raw) == "+2348031234567"
    assert g.normalise_phone("12") is None and g.normalise_phone("") is None


def test_age_and_minority() -> None:
    dob = dt.date(2008, 10, 15)
    assert g.age_on(dob, dt.date(2026, 10, 14)) == 17 and g.is_minor(dob, dt.date(2026, 10, 14), 18)
    assert not g.is_minor(dob, dt.date(2026, 10, 15), 18)


def test_same_person_needs_names_to_agree_with_phone_or_email() -> None:
    mum = g.GuardianInput("Chinwe", "Eze", "mother", phone="0803")
    kw = {"nin_matches": False, "phone_matches": True, "email_matches": False, "name_score": name_similarity}
    assert g.same_person(mum, "Chinwe", "Eze", **kw)
    assert not g.same_person(mum, "Uche", "Eze", **kw)
    assert g.same_person(mum, "Somebody", "Else", **{**kw, "nin_matches": True})
    assert not g.same_person(mum, "Chinwe", "Eze", **{**kw, "phone_matches": False})


def test_errors_for_minor_without_responsibility() -> None:
    aunt = g.GuardianInput("Nne", "Obi", "aunt_uncle", has_parental_responsibility=False, phone="08030000000")
    errs = g.errors_for([aunt], minor=True, majority=18, existing_with_responsibility=0, learner_nin=None)
    assert errs[-1]["field"] == "guardians"
    assert not g.errors_for([aunt], minor=True, majority=18, existing_with_responsibility=1, learner_nin=None)
    assert not g.errors_for([], minor=False, majority=18, existing_with_responsibility=0, learner_nin=None)
