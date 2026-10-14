"""National directory of education watchdogs and examination bodies, and the rules that give every institution its
regulatory profile (CR-005). Public, high-level reference data; ``to_confirm`` marks entries to check with the body.
"""

from __future__ import annotations

from dataclasses import dataclass

I = "illustrative"  # noqa: E741
C = "to_confirm"

BASIC = ("ECCDE", "KG", "PRY1", "PRY2", "PRY3", "PRY4", "PRY5", "PRY6", "JSS1", "JSS2", "JSS3")
JUNIOR = ("JSS1", "JSS2", "JSS3")
SENIOR = ("SSS1", "SSS2", "SSS3")
SECONDARY = JUNIOR + SENIOR
UNIVERSITY = ("UG100", "UG200", "UG300", "UG400", "UG500", "UG600", "UG700", "PG")


@dataclass(frozen=True)
class Body:
    code: str
    name: str
    body_type: str
    jurisdiction: str
    statutory_basis: str | None
    functions: str
    levels: tuple[str, ...] = ()
    status: str = I


BODIES = [
    # ---------------- ministries
    Body(
        "FME",
        "Federal Ministry of Education",
        "ministry",
        "federal",
        "Constitution; National Policy on Education",
        "National education policy; owns and supervises the federal unity colleges and FME parastatals",
    ),
    Body(
        "FMOH",
        "Federal Ministry of Health",
        "ministry",
        "federal",
        None,
        "Supervises the health professional councils and federal health training institutions",
    ),
    Body(
        "FMOD",
        "Federal Ministry of Defence",
        "ministry",
        "federal",
        None,
        "Supervises the Armed Forces and their education and training institutions",
    ),
    Body(
        "FMPA",
        "Federal Ministry of Police Affairs",
        "ministry",
        "federal",
        None,
        "Supervises the Nigeria Police Force and its training institutions",
    ),
    Body(
        "FMI",
        "Federal Ministry of Interior",
        "ministry",
        "federal",
        None,
        "Supervises the Civil Defence, Correctional, Immigration and Fire services",
    ),
    Body("FMF", "Federal Ministry of Finance", "ministry", "federal", None, "Supervises the Nigeria Customs Service"),
    Body(
        "FMAFS",
        "Federal Ministry of Agriculture and Food Security",
        "ministry",
        "federal",
        None,
        "Owns federal colleges of agriculture, animal health, land resources and fisheries",
        status=C,
    ),
    Body(
        "FMENV",
        "Federal Ministry of Environment",
        "ministry",
        "federal",
        None,
        "Owns the federal colleges of forestry and wildlife (through its research institutes)",
        status=C,
    ),
    Body(
        "FMAV",
        "Federal Ministry of Aviation",
        "ministry",
        "federal",
        None,
        "Owns the Nigerian College of Aviation Technology",
        status=C,
    ),
    Body(
        "FMMBE",
        "Federal Ministry of Marine and Blue Economy",
        "ministry",
        "federal",
        None,
        "Owns the Maritime Academy of Nigeria",
        status=C,
    ),
    Body(
        "FMPR",
        "Federal Ministry of Petroleum Resources",
        "ministry",
        "federal",
        None,
        "Owns the Petroleum Training Institute",
        status=C,
    ),
    Body(
        "STATE_MOE",
        "State Ministry of Education (each state)",
        "ministry",
        "state",
        "State education laws",
        "Approves and supervises state and private schools in the state",
    ),
    # ---------------- regulators and accreditors
    Body(
        "NUC",
        "National Universities Commission",
        "regulator_accreditor",
        "federal",
        "Education (National Minimum Standards and Establishment of Institutions) Act",
        "Approves universities and accredits their programmes",
        UNIVERSITY,
    ),
    Body(
        "NBTE",
        "National Board for Technical Education",
        "regulator_accreditor",
        "federal",
        "Education (National Minimum Standards and Establishment of Institutions) Act",
        "Accredits polytechnics, monotechnics, technical colleges and their ND, HND and NTC programmes",
        ("NTC", "ND", "HND"),
    ),
    Body(
        "NCCE",
        "National Commission for Colleges of Education",
        "regulator_accreditor",
        "federal",
        "Education (National Minimum Standards and Establishment of Institutions) Act",
        "Accredits colleges of education and the NCE",
        ("NCE",),
    ),
    Body(
        "UBEC",
        "Universal Basic Education Commission",
        "regulator_accreditor",
        "federal",
        "Compulsory, Free Universal Basic Education Act 2004",
        "Regulates and funds universal basic education through the state SUBEBs",
        BASIC,
    ),
    Body(
        "SUBEB",
        "State Universal Basic Education Board (each state)",
        "regulator_accreditor",
        "state",
        "State UBE laws",
        "Manages public basic education in the state",
        BASIC,
    ),
    Body(
        "NMEC",
        "National Commission for Mass Literacy, Adult and Non-Formal Education",
        "regulator_accreditor",
        "federal",
        None,
        "Adult, non-formal and literacy education",
        status=C,
    ),
    Body(
        "NCNE",
        "National Commission for Nomadic Education",
        "regulator_accreditor",
        "federal",
        None,
        "Nomadic education",
        status=C,
    ),
    # ---------------- curriculum, teachers, funding
    Body(
        "NERDC",
        "Nigerian Educational Research and Development Council",
        "curriculum_authority",
        "federal",
        None,
        "National basic and senior secondary curricula",
        BASIC + SENIOR,
    ),
    Body(
        "TRCN",
        "Teachers Registration Council of Nigeria",
        "teacher_regulator",
        "federal",
        "Teachers Registration Council of Nigeria Act 1993",
        "Registers and licenses teachers",
    ),
    Body(
        "TETFUND",
        "Tertiary Education Trust Fund",
        "funding_agency",
        "federal",
        "Tertiary Education Trust Fund (Establishment) Act 2011",
        "Interventions in public tertiary institutions",
    ),
    Body(
        "NTI",
        "National Teachers' Institute",
        "training_institute",
        "federal",
        None,
        "Teacher training and professional development",
    ),
    # ---------------- examinations and admissions
    Body(
        "WAEC",
        "West African Examinations Council",
        "examination_body",
        "regional",
        "WAEC convention and Acts",
        "West African Senior School Certificate Examination (WASSCE)",
        ("SSS3",),
    ),
    Body(
        "NECO",
        "National Examinations Council",
        "examination_body",
        "federal",
        "National Examinations Council Act",
        "Senior School Certificate Examination; BECE for federal unity colleges; National Common Entrance "
        "Examination into the unity colleges",
        ("PRY6", "JSS3", "SSS3"),
    ),
    Body(
        "NABTEB",
        "National Business and Technical Examinations Board",
        "examination_body",
        "federal",
        None,
        "National Technical and Business Certificates (NTC/NBC) and SSCE",
        ("SSS3", "NTC"),
    ),
    Body(
        "NBAIS",
        "National Board for Arabic and Islamic Studies",
        "examination_body",
        "federal",
        None,
        "Senior Arabic and Islamic Secondary School Certificate",
        ("SSS3",),
        status=C,
    ),
    Body(
        "STATE_EXAM_BOARD",
        "State examinations board (each state)",
        "examination_body",
        "state",
        "State laws",
        "Basic Education Certificate Examination (BECE) and state examinations",
        ("PRY6", "JSS3"),
    ),
    Body(
        "JAMB",
        "Joint Admissions and Matriculation Board",
        "admissions_body",
        "federal",
        "Joint Admissions and Matriculation Board Act",
        "UTME and Direct Entry admissions into universities, polytechnics and colleges of education",
        ("UG100", "ND", "NCE"),
    ),
    # ---------------- professional councils and sector regulators
    Body(
        "NMCN",
        "Nursing and Midwifery Council of Nigeria",
        "professional_council",
        "federal",
        None,
        "Approves nursing and midwifery schools; registers nurses and midwives",
        ("NURSING",),
    ),
    Body(
        "MDCN",
        "Medical and Dental Council of Nigeria",
        "professional_council",
        "federal",
        None,
        "Accredits medical and dental training; registers practitioners",
    ),
    Body(
        "PCN",
        "Pharmacy Council of Nigeria",
        "professional_council",
        "federal",
        None,
        "Accredits pharmacy training; registers pharmacists",
    ),
    Body(
        "MLSCN",
        "Medical Laboratory Science Council of Nigeria",
        "professional_council",
        "federal",
        None,
        "Accredits medical laboratory training",
    ),
    Body(
        "CHPRBN",
        "Community Health Practitioners Registration Board of Nigeria",
        "professional_council",
        "federal",
        None,
        "Accredits community health training",
        ("HEALTH_TECH",),
    ),
    Body(
        "COREN",
        "Council for the Regulation of Engineering in Nigeria",
        "professional_council",
        "federal",
        None,
        "Accredits engineering programmes; registers engineers",
    ),
    Body(
        "VCN",
        "Veterinary Council of Nigeria",
        "professional_council",
        "federal",
        None,
        "Regulates veterinary training and practice",
        status=C,
    ),
    Body(
        "SURCON",
        "Surveyors Council of Nigeria",
        "professional_council",
        "federal",
        None,
        "Regulates surveying training and practice",
        status=C,
    ),
    Body(
        "NCAA",
        "Nigerian Civil Aviation Authority",
        "sector_regulator",
        "federal",
        "Civil Aviation Act",
        "Approves aviation training organisations",
    ),
    Body(
        "NIMASA",
        "Nigerian Maritime Administration and Safety Agency",
        "sector_regulator",
        "federal",
        None,
        "Approves seafarer training (STCW)",
        status=C,
    ),
]

# (from, to, type, note, status)
DEPENDENCIES = [
    *[
        (b, "FME", "supervised_by", "Parastatal of the Federal Ministry of Education", I)
        for b in (
            "NUC",
            "NBTE",
            "NCCE",
            "UBEC",
            "NERDC",
            "TRCN",
            "TETFUND",
            "NTI",
            "NECO",
            "NABTEB",
            "JAMB",
            "NMEC",
            "NCNE",
            "NBAIS",
        )
    ],
    ("SUBEB", "STATE_MOE", "supervised_by", "State board under the state ministry", I),
    ("STATE_EXAM_BOARD", "STATE_MOE", "supervised_by", "State examinations board", I),
    ("SUBEB", "UBEC", "funded_by", "UBE matching grants to the states", I),
    *[
        (b, "FMOH", "supervised_by", "Health professional council", I)
        for b in ("NMCN", "MDCN", "PCN", "MLSCN", "CHPRBN")
    ],
    ("NCAA", "FMAV", "supervised_by", "Aviation regulator", C),
    ("NIMASA", "FMMBE", "supervised_by", "Maritime regulator", C),
    *[
        ("JAMB", b, "recognises_results_of", "O-level results required for UTME admission", I)
        for b in ("WAEC", "NECO", "NABTEB")
    ],
    ("JAMB", "NBAIS", "recognises_results_of", "For programmes that accept the NBAIS certificate", C),
    *[
        ("NUC", b, "accredits_with", "Joint accreditation of professional programmes", I)
        for b in ("MDCN", "PCN", "NMCN", "MLSCN", "COREN")
    ],
    ("NBTE", "COREN", "accredits_with", "Engineering technology programmes", C),
    ("NERDC", "UBEC", "member_of", "Basic education curriculum used by UBE schools", C),
]


# --------------------------------------------------------------------------- rules: an institution's regulatory profile
def normalise_level(level: str) -> str:
    """``jss_1`` / ``primary_4`` / ``sss 3`` → the national codes ``JSS1`` / ``PRY4`` / ``SSS3``."""
    v = level.upper().replace("_", "").replace(" ", "").replace("-", "")
    return v.replace("PRIMARY", "PRY").replace("NURSERY", "KG")


@dataclass(frozen=True)
class Link:
    body: str
    relationship: str
    covers: str
    levels: tuple[str, ...] = ()
    mandatory: bool = True


TERTIARY_ACCREDITOR = {
    "university": "NUC",
    "defence_university": "NUC",
    "military_academy": "NUC",
    "police_academy": "NUC",
    "polytechnic": "NBTE",
    "monotechnic": "NBTE",
    "technical_college": "NBTE",
    "college_of_education": "NCCE",
    "school_of_nursing": "NMCN",
    "school_of_health_technology": "CHPRBN",
}
SECONDARY_CATEGORIES = ("junior_secondary", "senior_secondary", "combined_secondary", "international_school")
PRIMARY_CATEGORIES = ("eccde_centre", "nursery_primary", "primary", "special_school")
PUBLIC = ("federal", "state", "lga")


def profile(
    *,
    category: str,
    ownership: str,
    levels: tuple[str, ...] | list[str],
    owner_ministry: str | None = None,
    accreditation: tuple[str, ...] | list[str] = (),
    unity_college: bool = False,
    technical: bool = False,
) -> list[Link]:
    """The links an institution needs, from its category, ownership and levels (FR-REG-03)."""
    lv = {normalise_level(x) for x in levels}
    out: list[Link] = []
    federal = ownership == "federal"
    # supervision: the owning ministry for federal bodies, the state ministry for state and private schools
    if federal and owner_ministry:
        out.append(Link(owner_ministry, "supervision", "Owning or supervising ministry"))
    elif not federal:
        out.append(
            Link(
                "STATE_MOE",
                "supervision" if ownership in PUBLIC else "licensing",
                "Supervision" if ownership in PUBLIC else "Approval and licensing of the school",
            )
        )
    has_basic = bool(lv & set(BASIC)) or category in PRIMARY_CATEGORIES
    has_jss = bool(lv & set(JUNIOR)) or category in ("junior_secondary", "combined_secondary")
    has_sss = bool(lv & set(SENIOR)) or category in ("senior_secondary", "combined_secondary")
    if has_basic or has_sss or category in SECONDARY_CATEGORIES:
        out.append(Link("NERDC", "curriculum", "National curriculum", tuple(sorted(lv & set(BASIC + SENIOR)))))
        out.append(Link("TRCN", "teacher_registration", "Teachers registered and licensed"))
    if has_basic and ownership in ("state", "lga"):
        out.append(Link("SUBEB", "supervision", "Public basic education in the state", BASIC))
        out.append(Link("UBEC", "funding", "UBE intervention funds through the SUBEB", BASIC))
    if has_jss:
        out.append(
            Link(
                "NECO" if federal else "STATE_EXAM_BOARD",
                "examination",
                "Basic Education Certificate Examination (BECE)",
                ("JSS3",),
            )
        )
    if has_sss:
        out.append(Link("WAEC", "examination", "WASSCE", ("SSS3",)))
        out.append(Link("NECO", "examination", "SSCE", ("SSS3",)))
    if technical:
        out.append(Link("NABTEB", "examination", "NTC / NBC", ("SSS3", "NTC")))
        out.append(Link("NBTE", "accreditation", "Technical college programmes", ("NTC",)))
    if unity_college:
        out.append(Link("NECO", "admission", "National Common Entrance Examination into the unity colleges", ("JSS1",)))
    accreditors = list(
        dict.fromkeys(
            [
                *accreditation,
                *([TERTIARY_ACCREDITOR[category]] if category in TERTIARY_ACCREDITOR and not technical else []),
            ]
        )
    )
    for a in accreditors:
        rel = "professional_regulation" if a in ("NMCN", "CHPRBN", "MDCN", "PCN", "MLSCN") else "accreditation"
        out.append(
            Link(
                a,
                rel,
                {"NUC": "Degree programmes", "NBTE": "ND / HND / NTC programmes", "NCCE": "NCE programmes"}.get(
                    a, "Programmes and practice"
                ),
            )
        )
    if any(a in ("NUC", "NBTE", "NCCE") for a in accreditors) and not technical:
        out.append(Link("JAMB", "admission", "UTME and Direct Entry admissions"))
        if ownership in PUBLIC:
            out.append(Link("TETFUND", "funding", "Tertiary education interventions", mandatory=False))
    seen: set[tuple[str, str, str]] = set()
    unique = []
    for link in out:
        key = (link.body, link.relationship, link.covers)
        if key not in seen:
            seen.add(key)
            unique.append(link)
    return unique


def gaps(links: list[tuple[str, str]], *, category: str, levels: tuple[str, ...] | list[str]) -> list[str]:
    """What an institution's profile is missing (FR-REG-04). ``links`` are (body, relationship) pairs."""
    rels = {r for _b, r in links}
    lv = {normalise_level(x) for x in levels}
    out = []
    if not rels & {"supervision", "licensing"}:
        out.append("no supervising or licensing body")
    if category in TERTIARY_ACCREDITOR and not rels & {"accreditation", "professional_regulation"}:
        out.append("no accrediting body")
    if lv & ({"JSS3"} | set(SENIOR)) and "examination" not in rels:
        out.append("no examination body for examined levels")
    if (lv & set(BASIC + SENIOR) or category in SECONDARY_CATEGORIES + PRIMARY_CATEGORIES) and "curriculum" not in rels:
        out.append("no curriculum authority")
    return out
