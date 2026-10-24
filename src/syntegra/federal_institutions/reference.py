"""Reference data for the Federal Institutions registry (CR-005) — public, high-level, to be confirmed.

Federal unity colleges and federal special training institutions with their owning bodies. Nothing is ``verified``:
the Federal Ministry of Education and each owning body confirm their lists, and the reference import completes and
corrects them (FR-FED-04). Where a name or location is uncertain the entry is ``to_confirm``.
"""

from __future__ import annotations

from dataclasses import dataclass

I = "illustrative"  # noqa: E741
C = "to_confirm"
JSS_SSS = ("JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3")


@dataclass(frozen=True)
class Body:
    code: str
    name: str
    category: str
    parent: str | None = None
    status: str = I


@dataclass(frozen=True)
class Unit:
    body: str
    code: str
    name: str
    unit_type: str
    parent: str | None = None
    status: str = I


@dataclass(frozen=True)
class Inst:
    body: str
    unit: str
    code: str
    name: str
    short_name: str
    institution_type: str
    category: str
    state: str
    town: str
    levels: tuple[str, ...]
    gender: str | None = None
    boarding: str | None = None
    admission: str | None = None
    status: str = C


BODIES = [
    Body("FME", "Federal Ministry of Education", "ministry"),
    Body("NTI", "National Teachers' Institute", "parastatal", "FME"),
    Body("FMAFS", "Federal Ministry of Agriculture and Food Security", "ministry", status=C),
    Body("FMENV", "Federal Ministry of Environment", "ministry", status=C),
    Body("FRIN", "Forestry Research Institute of Nigeria", "parastatal", "FMENV", status=C),
    Body("FMAV", "Federal Ministry of Aviation", "ministry", status=C),
    Body("FMMBE", "Federal Ministry of Marine and Blue Economy", "ministry", status=C),
    Body("FMPR", "Federal Ministry of Petroleum Resources", "ministry", status=C),
    Body("NBS", "National Bureau of Statistics", "agency", status=C),
    Body("OSGOF", "Office of the Surveyor-General of the Federation", "agency", status=C),
]

ZONE_UNITS = [
    ("NC", "North Central zone", "north_central"),
    ("NE", "North East zone", "north_east"),
    ("NW", "North West zone", "north_west"),
    ("SE", "South East zone", "south_east"),
    ("SS", "South South zone", "south_south"),
    ("SW", "South West zone", "south_west"),
]
UNITS = [
    Unit("FME", "SSE", "Department of Senior Secondary Education", "department", status=C),
    Unit("FME", "FUC", "Federal Unity Colleges", "division", "SSE", status=C),
    *[Unit("FME", f"FUC-{z}", f"Federal Unity Colleges — {n}", "zone", "FUC") for z, n, _ in ZONE_UNITS],
    Unit("FME", "TSE", "Department of Technology and Science Education", "department", status=C),
    Unit("FME", "FSTC", "Federal Science and Technical Colleges", "division", "TSE", status=C),
    Unit("FME", "TED", "Department of Tertiary Education", "department", status=C),
    Unit("FME", "COE", "Federal Colleges of Education", "division", "TED", status=C),
    Unit("NTI", "HQ", "National Teachers' Institute headquarters", "directorate"),
    Unit("FMAFS", "COLL", "Federal colleges of agriculture and allied sciences", "department", status=C),
    Unit("FRIN", "COLL", "Federal colleges of forestry and wildlife", "department", status=C),
    Unit("FMAV", "TRG", "Aviation training", "department", status=C),
    Unit("FMMBE", "TRG", "Maritime training", "department", status=C),
    Unit("FMPR", "TRG", "Petroleum training", "department", status=C),
    Unit("NBS", "TRG", "Federal Schools of Statistics", "department", status=C),
    Unit("OSGOF", "TRG", "Survey training", "department", status=C),
]


def _unity(code: str, name: str, state: str, town: str, gender: str, status: str = C) -> Inst:
    from syntegra.platform.states import ZONES

    zone = {v: k for k, _n, v in ZONE_UNITS}[ZONES[state]]
    t = {"girls": "unity_college_girls", "boys": "unity_college_boys"}.get(gender, "unity_college")
    return Inst(
        "FME",
        f"FUC-{zone}",
        code,
        name,
        code,
        t,
        "combined_secondary",
        state,
        town,
        JSS_SSS,
        gender,
        "boarding",
        "national_common_entrance",
        status,
    )


UNITY_COLLEGES = [
    _unity("KC", "King's College, Lagos", "NG-LA", "Lagos", "boys", I),
    _unity("QC", "Queen's College, Lagos", "NG-LA", "Yaba", "girls", I),
    _unity("FGC-IJANIKIN", "Federal Government College, Ijanikin", "NG-LA", "Ijanikin", "mixed"),
    _unity("FGC-ODOGBOLU", "Federal Government College, Odogbolu", "NG-OG", "Odogbolu", "mixed"),
    _unity("FGGC-SAGAMU", "Federal Government Girls' College, Sagamu", "NG-OG", "Sagamu", "girls"),
    _unity("FGC-IKIRUN", "Federal Government College, Ikirun", "NG-OS", "Ikirun", "mixed"),
    _unity("FGGC-IPETUMODU", "Federal Government Girls' College, Ipetumodu", "NG-OS", "Ipetumodu", "girls"),
    _unity("FGC-OGBOMOSO", "Federal Government College, Ogbomoso", "NG-OY", "Ogbomoso", "mixed"),
    _unity("FGGC-OYO", "Federal Government Girls' College, Oyo", "NG-OY", "Oyo", "girls"),
    _unity("FGC-IDOANI", "Federal Government College, Idoani", "NG-ON", "Idoani", "mixed"),
    _unity("FGGC-AKURE", "Federal Government Girls' College, Akure", "NG-ON", "Akure", "girls"),
    _unity("FGC-IKOLE", "Federal Government College, Ikole-Ekiti", "NG-EK", "Ikole-Ekiti", "mixed"),
    _unity("FGGC-EFON", "Federal Government Girls' College, Efon-Alaaye", "NG-EK", "Efon-Alaaye", "girls"),
    _unity("FGC-ENUGU", "Federal Government College, Enugu", "NG-EN", "Enugu", "mixed"),
    _unity("FGGC-LEJJA", "Federal Government Girls' College, Lejja", "NG-EN", "Lejja", "girls"),
    _unity("FGC-OWERRI", "Federal Government College, Owerri", "NG-IM", "Owerri", "mixed"),
    _unity("FGGC-OWERRI", "Federal Government Girls' College, Owerri", "NG-IM", "Owerri", "girls"),
    _unity("FGC-OKIGWE", "Federal Government College, Okigwe", "NG-IM", "Okigwe", "mixed"),
    _unity("FGC-OHAFIA", "Federal Government College, Ohafia", "NG-AB", "Ohafia", "mixed"),
    _unity("FGGC-UMUAHIA", "Federal Government Girls' College, Umuahia", "NG-AB", "Umuahia", "girls"),
    _unity("FGC-NISE", "Federal Government College, Nise", "NG-AN", "Nise", "mixed"),
    _unity("FGGC-ONITSHA", "Federal Government Girls' College, Onitsha", "NG-AN", "Onitsha", "girls"),
    _unity("FGC-OKPOSI", "Federal Government College, Okposi", "NG-EB", "Okposi", "mixed"),
    _unity("FGGC-EZZAMGBO", "Federal Government Girls' College, Ezzamgbo", "NG-EB", "Ezzamgbo", "girls"),
    _unity("FGC-PH", "Federal Government College, Port Harcourt", "NG-RI", "Port Harcourt", "mixed"),
    _unity("FGGC-ABULOMA", "Federal Government Girls' College, Abuloma", "NG-RI", "Abuloma", "girls"),
    _unity("FGC-WARRI", "Federal Government College, Warri", "NG-DE", "Warri", "mixed"),
    _unity("FGGC-IBUSA", "Federal Government Girls' College, Ibusa", "NG-DE", "Ibusa", "girls"),
    _unity("FGC-IBILLO", "Federal Government College, Ibillo", "NG-ED", "Ibillo", "mixed"),
    _unity("FGGC-BENIN", "Federal Government Girls' College, Benin City", "NG-ED", "Benin City", "girls"),
    _unity("FGC-CALABAR", "Federal Government College, Calabar", "NG-CR", "Calabar", "mixed"),
    _unity("FGGC-CALABAR", "Federal Government Girls' College, Calabar", "NG-CR", "Calabar", "girls"),
    _unity("FGC-IKOTEKPENE", "Federal Government College, Ikot Ekpene", "NG-AK", "Ikot Ekpene", "mixed"),
    _unity(
        "FGGC-IKOTOBIOITONG", "Federal Government Girls' College, Ikot Obio Itong", "NG-AK", "Ikot Obio Itong", "girls"
    ),
    _unity("FGC-ODI", "Federal Government College, Odi", "NG-BY", "Odi", "mixed"),
    _unity("FGGC-IMIRINGI", "Federal Government Girls' College, Imiringi", "NG-BY", "Imiringi", "girls"),
    _unity("FGC-KADUNA", "Federal Government College, Kaduna", "NG-KD", "Kaduna", "mixed"),
    _unity("FGGC-ZARIA", "Federal Government Girls' College, Zaria", "NG-KD", "Zaria", "girls"),
    _unity("FGC-KANO", "Federal Government College, Kano", "NG-KN", "Kano", "mixed"),
    _unity("FGGC-MINJIBIR", "Federal Government Girls' College, Minjibir", "NG-KN", "Minjibir", "girls"),
    _unity("FGGC-KAZAURE", "Federal Government Girls' College, Kazaure", "NG-JI", "Kazaure", "girls"),
    _unity("FGC-SOKOTO", "Federal Government College, Sokoto", "NG-SO", "Sokoto", "mixed"),
    _unity("FGGC-TAMBUWAL", "Federal Government Girls' College, Tambuwal", "NG-SO", "Tambuwal", "girls"),
    _unity("FGC-DAURA", "Federal Government College, Daura", "NG-KT", "Daura", "mixed"),
    _unity("FGGC-MALUMFASHI", "Federal Government Girls' College, Malumfashi", "NG-KT", "Malumfashi", "girls"),
    _unity("FGC-BIRNINYAURI", "Federal Government College, Birnin Yauri", "NG-KE", "Birnin Yauri", "mixed"),
    _unity("FGGC-GWANDU", "Federal Government Girls' College, Gwandu", "NG-KE", "Gwandu", "girls"),
    _unity("FGC-ANKA", "Federal Government College, Anka", "NG-ZA", "Anka", "mixed"),
    _unity("FGGC-GUSAU", "Federal Government Girls' College, Gusau", "NG-ZA", "Gusau", "girls"),
    _unity("FGC-MAIDUGURI", "Federal Government College, Maiduguri", "NG-BO", "Maiduguri", "mixed"),
    _unity("FGGC-MONGUNO", "Federal Government Girls' College, Monguno", "NG-BO", "Monguno", "girls"),
    _unity("FGC-BUNIYADI", "Federal Government College, Buni Yadi", "NG-YO", "Buni Yadi", "mixed"),
    _unity("FGGC-POTISKUM", "Federal Government Girls' College, Potiskum", "NG-YO", "Potiskum", "girls"),
    _unity("FGC-AZARE", "Federal Government College, Azare", "NG-BA", "Azare", "mixed"),
    _unity("FGGC-BAUCHI", "Federal Government Girls' College, Bauchi", "NG-BA", "Bauchi", "girls"),
    _unity("FGC-BILLIRI", "Federal Government College, Billiri", "NG-GO", "Billiri", "mixed"),
    _unity("FGGC-BAJOGA", "Federal Government Girls' College, Bajoga", "NG-GO", "Bajoga", "girls"),
    _unity("FGC-YOLA", "Federal Government College, Yola", "NG-AD", "Yola", "mixed"),
    _unity("FGGC-YOLA", "Federal Government Girls' College, Yola", "NG-AD", "Yola", "girls"),
    _unity("FGC-WUKARI", "Federal Government College, Wukari", "NG-TA", "Wukari", "mixed"),
    _unity("FGGC-JALINGO", "Federal Government Girls' College, Jalingo", "NG-TA", "Jalingo", "girls"),
    _unity("FGC-JOS", "Federal Government College, Jos", "NG-PL", "Jos", "mixed"),
    _unity("FGC-KEFFI", "Federal Government College, Keffi", "NG-NA", "Keffi", "mixed"),
    _unity("FGGC-KEANA", "Federal Government Girls' College, Keana", "NG-NA", "Keana", "girls"),
    _unity("FGC-OTOBI", "Federal Government College, Otobi", "NG-BE", "Otobi", "mixed"),
    _unity("FGGC-GBOKO", "Federal Government Girls' College, Gboko", "NG-BE", "Gboko", "girls"),
    _unity("FGC-UGWOLAWO", "Federal Government College, Ugwolawo", "NG-KO", "Ugwolawo", "mixed"),
    _unity("FGGC-KABBA", "Federal Government Girls' College, Kabba", "NG-KO", "Kabba", "girls"),
    _unity("FGC-ILORIN", "Federal Government College, Ilorin", "NG-KW", "Ilorin", "mixed"),
    _unity("FGGC-OMUARAN", "Federal Government Girls' College, Omu-Aran", "NG-KW", "Omu-Aran", "girls"),
    _unity("FGC-MINNA", "Federal Government College, Minna", "NG-NI", "Minna", "mixed"),
    _unity("FGGC-BIDA", "Federal Government Girls' College, Bida", "NG-NI", "Bida", "girls"),
    _unity("FGC-KWALI", "Federal Government College, Kwali", "NG-FC", "Kwali", "mixed"),
    _unity("FGC-RUBOCHI", "Federal Government College, Rubochi", "NG-FC", "Rubochi", "mixed"),
    _unity("FGBC-GARKI", "Federal Government Boys' College, Garki", "NG-FC", "Garki", "boys"),
    _unity("FGGC-BWARI", "Federal Government Girls' College, Bwari", "NG-FC", "Bwari", "girls"),
]


def _fstc(code: str, name: str, state: str, town: str) -> Inst:
    return Inst(
        "FME",
        "FSTC",
        code,
        name,
        code,
        "science_technical_college",
        "technical_college",
        state,
        town,
        (*JSS_SSS, "NTC"),
        "mixed",
        "boarding",
        "national_common_entrance",
    )


SCIENCE_TECHNICAL = [
    _fstc("FSTC-YABA", "Federal Science and Technical College, Yaba", "NG-LA", "Yaba"),
    _fstc("FSTC-UROMI", "Federal Science and Technical College, Uromi", "NG-ED", "Uromi"),
    _fstc("FSTC-OHANSO", "Federal Science and Technical College, Ohanso", "NG-AB", "Ohanso"),
    _fstc("FSTC-KAFANCHAN", "Federal Science and Technical College, Kafanchan", "NG-KD", "Kafanchan"),
    _fstc("FSTC-LASSA", "Federal Science and Technical College, Lassa", "NG-BO", "Lassa"),
    _fstc("FSTC-AHOADA", "Federal Science and Technical College, Ahoada", "NG-RI", "Ahoada"),
    _fstc("FSTC-USIEKITI", "Federal Science and Technical College, Usi-Ekiti", "NG-EK", "Usi-Ekiti"),
    _fstc("FSTC-AWKA", "Federal Science and Technical College, Awka", "NG-AN", "Awka"),
    _fstc("FSTC-OROZO", "Federal Science and Technical College, Orozo", "NG-FC", "Orozo"),
    _fstc("FSTC-TUNGBO", "Federal Science and Technical College, Tungbo", "NG-BY", "Tungbo"),
]


def _coe(code: str, name: str, state: str, town: str, t: str = "college_of_education") -> Inst:
    return Inst("FME", "COE", code, name, code, t, "college_of_education", state, town, ("NCE",), "mixed", None, "utme")


COLLEGES_OF_EDUCATION = [
    _coe("FCES-OYO", "Federal College of Education (Special), Oyo", "NG-OY", "Oyo", "college_of_education_special"),
    _coe(
        "FCET-AKOKA",
        "Federal College of Education (Technical), Akoka",
        "NG-LA",
        "Akoka",
        "college_of_education_technical",
    ),
    _coe(
        "FCET-GOMBE",
        "Federal College of Education (Technical), Gombe",
        "NG-GO",
        "Gombe",
        "college_of_education_technical",
    ),
    _coe(
        "FCET-OMOKU",
        "Federal College of Education (Technical), Omoku",
        "NG-RI",
        "Omoku",
        "college_of_education_technical",
    ),
    _coe(
        "FCET-UMUNZE",
        "Federal College of Education (Technical), Umunze",
        "NG-AN",
        "Umunze",
        "college_of_education_technical",
    ),
    _coe(
        "FCET-BICHI",
        "Federal College of Education (Technical), Bichi",
        "NG-KN",
        "Bichi",
        "college_of_education_technical",
    ),
    _coe(
        "FCET-GUSAU",
        "Federal College of Education (Technical), Gusau",
        "NG-ZA",
        "Gusau",
        "college_of_education_technical",
    ),
    _coe(
        "FCET-ASABA",
        "Federal College of Education (Technical), Asaba",
        "NG-DE",
        "Asaba",
        "college_of_education_technical",
    ),
    _coe(
        "FCET-POTISKUM",
        "Federal College of Education (Technical), Potiskum",
        "NG-YO",
        "Potiskum",
        "college_of_education_technical",
    ),
    _coe("FCE-ZARIA", "Federal College of Education, Zaria", "NG-KD", "Zaria"),
    _coe("FCE-KANO", "Federal College of Education, Kano", "NG-KN", "Kano"),
    _coe("FCE-ABEOKUTA", "Federal College of Education, Abeokuta", "NG-OG", "Abeokuta"),
    _coe("FCE-OKENE", "Federal College of Education, Okene", "NG-KO", "Okene"),
    _coe("FCE-KONTAGORA", "Federal College of Education, Kontagora", "NG-NI", "Kontagora"),
    _coe("FCE-PANKSHIN", "Federal College of Education, Pankshin", "NG-PL", "Pankshin"),
    _coe("FCE-YOLA", "Federal College of Education, Yola", "NG-AD", "Yola"),
    _coe("FCE-OBUDU", "Federal College of Education, Obudu", "NG-CR", "Obudu"),
    _coe("FCE-KATSINA", "Federal College of Education, Katsina", "NG-KT", "Katsina"),
    _coe("FCE-EHAAMUFU", "Federal College of Education, Eha-Amufu", "NG-EN", "Eha-Amufu"),
]


def _sp(
    body: str,
    unit: str,
    code: str,
    name: str,
    t: str,
    cat: str,
    state: str,
    town: str,
    levels: tuple[str, ...] = ("ND", "HND"),
) -> Inst:
    return Inst(body, unit, code, name, code, t, cat, state, town, levels, "mixed", None, "utme")


SPECIAL_TRAINING = [
    _sp(
        "NTI",
        "HQ",
        "NTI-KADUNA",
        "National Teachers' Institute, Kaduna",
        "teacher_training_institute",
        "college_of_education",
        "NG-KD",
        "Kaduna",
        ("NCE",),
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCA-AKURE",
        "Federal College of Agriculture, Akure",
        "college_of_agriculture",
        "monotechnic",
        "NG-ON",
        "Akure",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCA-IBADAN",
        "Federal College of Agriculture, Moor Plantation, Ibadan",
        "college_of_agriculture",
        "monotechnic",
        "NG-OY",
        "Ibadan",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCA-ISHIAGU",
        "Federal College of Agriculture, Ishiagu",
        "college_of_agriculture",
        "monotechnic",
        "NG-EB",
        "Ishiagu",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCAHPT-IBADAN",
        "Federal College of Animal Health and Production Technology, Ibadan",
        "college_of_animal_health",
        "monotechnic",
        "NG-OY",
        "Ibadan",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCAHPT-VOM",
        "Federal College of Animal Health and Production Technology, Vom",
        "college_of_animal_health",
        "monotechnic",
        "NG-PL",
        "Vom",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCVMLT-VOM",
        "Federal College of Veterinary and Medical Laboratory Technology, Vom",
        "college_of_veterinary_laboratory",
        "monotechnic",
        "NG-PL",
        "Vom",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCLRT-OWERRI",
        "Federal College of Land Resources Technology, Owerri",
        "college_of_land_resources",
        "monotechnic",
        "NG-IM",
        "Owerri",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCLRT-KURU",
        "Federal College of Land Resources Technology, Kuru",
        "college_of_land_resources",
        "monotechnic",
        "NG-PL",
        "Kuru",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCH-DADINKOWA",
        "Federal College of Horticulture, Dadin Kowa",
        "college_of_agriculture",
        "monotechnic",
        "NG-GO",
        "Dadin Kowa",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCFFT-NEWBUSSA",
        "Federal College of Freshwater Fisheries Technology, New Bussa",
        "college_of_fisheries",
        "monotechnic",
        "NG-NI",
        "New Bussa",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCFFT-BAGA",
        "Federal College of Freshwater Fisheries Technology, Baga",
        "college_of_fisheries",
        "monotechnic",
        "NG-BO",
        "Baga",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCFMT-LAGOS",
        "Federal College of Fisheries and Marine Technology, Lagos",
        "college_of_fisheries",
        "monotechnic",
        "NG-LA",
        "Victoria Island",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCOOP-IBADAN",
        "Federal Cooperative College, Ibadan",
        "cooperative_college",
        "monotechnic",
        "NG-OY",
        "Ibadan",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCOOP-KADUNA",
        "Federal Cooperative College, Kaduna",
        "cooperative_college",
        "monotechnic",
        "NG-KD",
        "Kaduna",
    ),
    _sp(
        "FMAFS",
        "COLL",
        "FCOOP-OJIRIVER",
        "Federal Cooperative College, Oji River",
        "cooperative_college",
        "monotechnic",
        "NG-EN",
        "Oji River",
    ),
    _sp(
        "FRIN",
        "COLL",
        "FCF-IBADAN",
        "Federal College of Forestry, Ibadan",
        "college_of_forestry",
        "monotechnic",
        "NG-OY",
        "Ibadan",
    ),
    _sp(
        "FRIN",
        "COLL",
        "FCF-JOS",
        "Federal College of Forestry, Jos",
        "college_of_forestry",
        "monotechnic",
        "NG-PL",
        "Jos",
    ),
    _sp(
        "FRIN",
        "COLL",
        "FCFM-AFAKA",
        "Federal College of Forestry Mechanization, Afaka",
        "college_of_forestry",
        "monotechnic",
        "NG-KD",
        "Afaka",
    ),
    _sp(
        "FRIN",
        "COLL",
        "FCWM-NEWBUSSA",
        "Federal College of Wildlife Management, New Bussa",
        "college_of_forestry",
        "monotechnic",
        "NG-NI",
        "New Bussa",
    ),
    _sp(
        "NBS",
        "TRG",
        "FSS-IBADAN",
        "Federal School of Statistics, Ibadan",
        "school_of_statistics",
        "monotechnic",
        "NG-OY",
        "Ibadan",
    ),
    _sp(
        "NBS",
        "TRG",
        "FSS-ENUGU",
        "Federal School of Statistics, Enugu",
        "school_of_statistics",
        "monotechnic",
        "NG-EN",
        "Enugu",
    ),
    _sp(
        "NBS",
        "TRG",
        "FSS-MANCHOK",
        "Federal School of Statistics, Manchok",
        "school_of_statistics",
        "monotechnic",
        "NG-KD",
        "Manchok",
    ),
    _sp(
        "OSGOF",
        "TRG",
        "FSSV-OYO",
        "Federal School of Surveying, Oyo",
        "school_of_surveying",
        "monotechnic",
        "NG-OY",
        "Oyo",
    ),
    _sp(
        "FMAV",
        "TRG",
        "NCAT-ZARIA",
        "Nigerian College of Aviation Technology, Zaria",
        "aviation_college",
        "monotechnic",
        "NG-KD",
        "Zaria",
    ),
    _sp(
        "FMMBE",
        "TRG",
        "MAN-ORON",
        "Maritime Academy of Nigeria, Oron",
        "maritime_academy",
        "monotechnic",
        "NG-AK",
        "Oron",
    ),
    _sp(
        "FMPR",
        "TRG",
        "PTI-EFFURUN",
        "Petroleum Training Institute, Effurun",
        "petroleum_training_institute",
        "polytechnic",
        "NG-DE",
        "Effurun",
    ),
]

# Sector regulators that license specific special institutions (added to the rule-derived profile)
SECTOR_REGULATORS = {
    "NCAT-ZARIA": ("NCAA", "licensing", "Approved aviation training organisation"),
    "MAN-ORON": ("NIMASA", "licensing", "Approved seafarer training (STCW)"),
    "FCVMLT-VOM": ("MLSCN", "professional_regulation", "Medical laboratory technician training"),
    "FSSV-OYO": ("SURCON", "professional_regulation", "Survey training"),
}

INSTITUTIONS = UNITY_COLLEGES + SCIENCE_TECHNICAL + COLLEGES_OF_EDUCATION + SPECIAL_TRAINING
