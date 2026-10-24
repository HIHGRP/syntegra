"""Reference data for the Federal Security Education registry (CR-004) — public, high-level, to be confirmed.

Every record carries a ``data_status``: ``illustrative`` (from public sources, believed correct) or ``to_confirm``
(name, location or detail uncertain). Nothing here is ``verified``: each agency confirms its own entries before live
use (decision D32). Course modules are syllabus headings only; CEDA never holds operational, deployment, intelligence,
weapons or tactical content, and courses whose detail the agency withholds have ``content_held = False``.
Durations and contact hours are left empty unless publicly fixed; the agency supplies them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

I = "illustrative"  # noqa: E741 — short markers keep the tables readable
C = "to_confirm"


@dataclass(frozen=True)
class Agency:
    code: str
    name: str
    category: str
    ministry: str
    law: str
    status: str = I


@dataclass(frozen=True)
class Unit:
    code: str
    name: str
    unit_type: str
    parent: str | None
    state: str | None
    town: str | None
    status: str = I


@dataclass(frozen=True)
class Institution:
    code: str
    name: str
    short_name: str
    agency: str
    unit: str
    institution_type: str
    category: str  # institution_category code list
    state: str
    town: str
    head_title: str
    access_regime: str = "restricted"
    accreditation: tuple[str, ...] = ()
    established: int | None = None
    levels: tuple[str, ...] = ()
    status: str = I


@dataclass(frozen=True)
class Course:
    code: str
    title: str
    category: str
    award: str
    award_title: str
    accrediting_body: str | None = None
    duration_weeks: int | None = None
    target_ranks: tuple[str, ...] = ()
    entry: tuple[str, ...] = ()
    content_held: bool = True
    status: str = I
    modules: tuple[tuple[str, str, str, str], ...] = field(default_factory=tuple)  # code, title, area, assessment


# --------------------------------------------------------------------------- agencies (FR-STI-01)
AGENCIES = [
    Agency(
        "DHQ",
        "Defence Headquarters (Armed Forces of Nigeria — tri-service)",
        "armed_forces",
        "Federal Ministry of Defence",
        "Armed Forces Act, Cap A20 LFN 2004",
    ),
    Agency("NA", "Nigerian Army", "armed_forces", "Federal Ministry of Defence", "Armed Forces Act, Cap A20 LFN 2004"),
    Agency("NN", "Nigerian Navy", "armed_forces", "Federal Ministry of Defence", "Armed Forces Act, Cap A20 LFN 2004"),
    Agency(
        "NAF", "Nigerian Air Force", "armed_forces", "Federal Ministry of Defence", "Armed Forces Act, Cap A20 LFN 2004"
    ),
    Agency("NPF", "Nigeria Police Force", "police", "Federal Ministry of Police Affairs", "Police Act 2020"),
    Agency(
        "NSCDC",
        "Nigeria Security and Civil Defence Corps",
        "paramilitary",
        "Federal Ministry of Interior",
        "NSCDC Act 2003 (as amended 2007)",
    ),
    Agency(
        "NCOS",
        "Nigerian Correctional Service",
        "paramilitary",
        "Federal Ministry of Interior",
        "Nigerian Correctional Service Act 2019",
    ),
    Agency(
        "NIS", "Nigeria Immigration Service", "paramilitary", "Federal Ministry of Interior", "Immigration Act 2015"
    ),
    Agency(
        "FFS",
        "Federal Fire Service",
        "emergency_service",
        "Federal Ministry of Interior",
        "Fire Service Act, Cap F29 LFN 2004",
    ),
    Agency(
        "NCS",
        "Nigeria Customs Service",
        "paramilitary",
        "Federal Ministry of Finance",
        "Nigeria Customs Service Act 2023",
    ),
    Agency(
        "FRSC",
        "Federal Road Safety Corps",
        "law_enforcement",
        "Federal Government (to confirm)",
        "Federal Road Safety Commission (Establishment) Act 2007",
        C,
    ),
    Agency(
        "NDLEA",
        "National Drug Law Enforcement Agency",
        "law_enforcement",
        "To confirm",
        "NDLEA Act, Cap N30 LFN 2004",
        C,
    ),
    Agency(
        "EFCC",
        "Economic and Financial Crimes Commission",
        "law_enforcement",
        "To confirm",
        "EFCC (Establishment) Act 2004",
        C,
    ),
    Agency(
        "DSS",
        "Department of State Services",
        "intelligence_security",
        "Presidency (to confirm)",
        "National Security Agencies Act 1986",
        C,
    ),
]

# --------------------------------------------------------------------------- structures (FR-STI-02)
UNITS: dict[str, list[Unit]] = {
    "DHQ": [
        Unit("DHQ", "Defence Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("DHQ-EDU", "Tri-service education and training", "directorate", "DHQ", "NG-FC", "Abuja", C),
    ],
    "NA": [
        Unit("AHQ", "Army Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("TRADOC", "Training and Doctrine Command", "training_command", "AHQ", "NG-NI", "Minna"),
        Unit("DAE", "Directorate of Army Education", "directorate", "AHQ", "NG-FC", "Abuja", C),
        Unit("1DIV", "1 Division", "formation", "AHQ", "NG-KD", "Kaduna"),
        Unit("2DIV", "2 Division", "formation", "AHQ", "NG-OY", "Ibadan"),
        Unit("3DIV", "3 Division", "formation", "AHQ", "NG-PL", "Jos"),
        Unit("6DIV", "6 Division", "formation", "AHQ", "NG-RI", "Port Harcourt"),
        Unit("7DIV", "7 Division", "formation", "AHQ", "NG-BO", "Maiduguri"),
        Unit("8DIV", "8 Division", "formation", "AHQ", "NG-SO", "Sokoto"),
        Unit("81DIV", "81 Division", "formation", "AHQ", "NG-LA", "Lagos"),
        Unit("82DIV", "82 Division", "formation", "AHQ", "NG-EN", "Enugu"),
    ],
    "NN": [
        Unit("NHQ", "Naval Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("NAVTRAC", "Naval Training Command", "training_command", "NHQ", "NG-LA", "Lagos"),
        Unit("WNC", "Western Naval Command", "command", "NHQ", "NG-LA", "Lagos"),
        Unit("ENC", "Eastern Naval Command", "command", "NHQ", "NG-CR", "Calabar"),
        Unit("CNC", "Central Naval Command", "command", "NHQ", "NG-BY", "Yenagoa"),
        Unit("LOGCOM", "Logistics Command", "command", "NHQ", "NG-DE", "Oghara", C),
    ],
    "NAF": [
        Unit("HQNAF", "Headquarters Nigerian Air Force", "headquarters", None, "NG-FC", "Abuja"),
        Unit("ATC", "Air Training Command", "training_command", "HQNAF", "NG-KD", "Kaduna"),
        Unit("GTC", "Ground Training Command", "training_command", "HQNAF", "NG-EN", "Enugu"),
        Unit("TAC", "Tactical Air Command", "command", "HQNAF", "NG-BE", "Makurdi"),
        Unit("LC", "Logistics Command", "command", "HQNAF", "NG-LA", "Ikeja"),
        Unit("MC", "Mobility Command", "command", "HQNAF", "NG-BY", "Yenagoa"),
        Unit("SOC", "Special Operations Command", "command", "HQNAF", "NG-BA", "Bauchi", C),
    ],
    "NPF": [
        Unit("FHQ", "Force Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("DTD", "Department of Training and Development", "department", "FHQ", "NG-FC", "Abuja", C),
    ],
    "NSCDC": [
        Unit("NHQ", "National Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("TRG", "Training directorate", "directorate", "NHQ", "NG-FC", "Abuja", C),
    ],
    "NCOS": [
        Unit("NHQ", "National Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("TRG", "Training directorate", "directorate", "NHQ", "NG-FC", "Abuja", C),
    ],
    "NIS": [
        Unit("SHQ", "Service Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("TRG", "Training directorate", "directorate", "SHQ", "NG-FC", "Abuja", C),
    ],
    "FFS": [Unit("FHQ", "Federal Fire Service Headquarters", "headquarters", None, "NG-FC", "Abuja")],
    "NCS": [
        Unit("CHQ", "Customs Headquarters", "headquarters", None, "NG-FC", "Abuja"),
        Unit("TRG", "Training directorate", "directorate", "CHQ", "NG-FC", "Abuja", C),
    ],
    "FRSC": [Unit("NHQ", "National Headquarters", "headquarters", None, "NG-FC", "Abuja")],
    "NDLEA": [Unit("NHQ", "National Headquarters", "headquarters", None, "NG-FC", "Abuja")],
    "EFCC": [Unit("HQ", "Headquarters", "headquarters", None, "NG-FC", "Abuja")],
    "DSS": [Unit("NHQ", "National Headquarters", "headquarters", None, "NG-FC", "Abuja")],
}

# Agencies organised by state command in every state and the FCT (generated from the state list).
STATE_COMMANDS: dict[str, tuple[str, str, str]] = {
    # agency: (parent unit, unit type, name pattern)
    "NPF": ("FHQ", "state_command", "{state} Police Command"),
    "NSCDC": ("NHQ", "state_command", "{state} State Command"),
    "NCOS": ("NHQ", "state_command", "{state} State Command"),
    "NIS": ("SHQ", "state_command", "{state} State Command"),
    "NDLEA": ("NHQ", "state_command", "{state} State Command"),
    "FRSC": ("NHQ", "sector_command", "{state} Sector Command"),
}

# --------------------------------------------------------------------------- ranks (FR-STI-03), most junior first
RANKS: dict[str, list[tuple[str, str, str, str]]] = {
    "NA": [
        ("RCT", "Recruit", "RCT", "recruit"),
        ("PTE", "Private", "PTE", "other_rank"),
        ("LCPL", "Lance Corporal", "LCPL", "non_commissioned"),
        ("CPL", "Corporal", "CPL", "non_commissioned"),
        ("SGT", "Sergeant", "SGT", "non_commissioned"),
        ("SSGT", "Staff Sergeant", "SSGT", "non_commissioned"),
        ("WO", "Warrant Officer", "WO", "warrant_officer"),
        ("MWO", "Master Warrant Officer", "MWO", "warrant_officer"),
        ("AWO", "Army Warrant Officer", "AWO", "warrant_officer"),
        ("OCDT", "Officer Cadet", "OCDT", "cadet"),
        ("2LT", "Second Lieutenant", "2Lt", "commissioned_officer"),
        ("LT", "Lieutenant", "Lt", "commissioned_officer"),
        ("CAPT", "Captain", "Capt", "commissioned_officer"),
        ("MAJ", "Major", "Maj", "commissioned_officer"),
        ("LTCOL", "Lieutenant Colonel", "Lt Col", "commissioned_officer"),
        ("COL", "Colonel", "Col", "commissioned_officer"),
        ("BRIGGEN", "Brigadier General", "Brig Gen", "commissioned_officer"),
        ("MAJGEN", "Major General", "Maj Gen", "commissioned_officer"),
        ("LTGEN", "Lieutenant General", "Lt Gen", "commissioned_officer"),
        ("GEN", "General", "Gen", "commissioned_officer"),
    ],
    "NN": [
        ("OCDT", "Officer Cadet", "OCDT", "cadet"),
        ("MID", "Midshipman", "Mid", "cadet"),
        ("SLT", "Sub-Lieutenant", "SLt", "commissioned_officer"),
        ("LT", "Lieutenant", "Lt", "commissioned_officer"),
        ("LCDR", "Lieutenant Commander", "Lt Cdr", "commissioned_officer"),
        ("CDR", "Commander", "Cdr", "commissioned_officer"),
        ("CAPT", "Captain", "Capt", "commissioned_officer"),
        ("CDRE", "Commodore", "Cdre", "commissioned_officer"),
        ("RADM", "Rear Admiral", "RAdm", "commissioned_officer"),
        ("VADM", "Vice Admiral", "VAdm", "commissioned_officer"),
        ("ADM", "Admiral", "Adm", "commissioned_officer"),
    ],
    "NAF": [
        ("RCT", "Recruit", "RCT", "recruit"),
        ("AC", "Aircraftman / Aircraftwoman", "ACM", "other_rank"),
        ("LCPL", "Lance Corporal", "LCpl", "non_commissioned"),
        ("CPL", "Corporal", "Cpl", "non_commissioned"),
        ("SGT", "Sergeant", "Sgt", "non_commissioned"),
        ("FS", "Flight Sergeant", "FS", "non_commissioned"),
        ("WO", "Warrant Officer", "WO", "warrant_officer"),
        ("MWO", "Master Warrant Officer", "MWO", "warrant_officer"),
        ("AWO", "Air Warrant Officer", "AWO", "warrant_officer"),
        ("OCDT", "Officer Cadet", "OCDT", "cadet"),
        ("PLTOFF", "Pilot Officer", "Plt Offr", "commissioned_officer"),
        ("FGOFF", "Flying Officer", "Fg Offr", "commissioned_officer"),
        ("FLTLT", "Flight Lieutenant", "Flt Lt", "commissioned_officer"),
        ("SQNLDR", "Squadron Leader", "Sqn Ldr", "commissioned_officer"),
        ("WGCDR", "Wing Commander", "Wg Cdr", "commissioned_officer"),
        ("GPCAPT", "Group Captain", "Gp Capt", "commissioned_officer"),
        ("AIRCDRE", "Air Commodore", "Air Cdre", "commissioned_officer"),
        ("AVM", "Air Vice Marshal", "AVM", "commissioned_officer"),
        ("AM", "Air Marshal", "AM", "commissioned_officer"),
        ("ACM", "Air Chief Marshal", "ACM", "commissioned_officer"),
    ],
    "NPF": [
        ("RCT", "Recruit Constable", "Rct", "recruit"),
        ("PC", "Constable", "PC", "junior_staff"),
        ("CPL", "Corporal", "Cpl", "junior_staff"),
        ("SGT", "Sergeant", "Sgt", "junior_staff"),
        ("INSP", "Inspector", "Insp", "senior_staff"),
        ("CADET", "Cadet Assistant Superintendent", "Cdt ASP", "cadet"),
        ("ASP", "Assistant Superintendent of Police", "ASP", "commissioned_officer"),
        ("DSP", "Deputy Superintendent of Police", "DSP", "commissioned_officer"),
        ("SP", "Superintendent of Police", "SP", "commissioned_officer"),
        ("CSP", "Chief Superintendent of Police", "CSP", "commissioned_officer"),
        ("ACP", "Assistant Commissioner of Police", "ACP", "commissioned_officer"),
        ("DCP", "Deputy Commissioner of Police", "DCP", "commissioned_officer"),
        ("CP", "Commissioner of Police", "CP", "commissioned_officer"),
        ("AIG", "Assistant Inspector-General of Police", "AIG", "commissioned_officer"),
        ("DIG", "Deputy Inspector-General of Police", "DIG", "commissioned_officer"),
        ("IGP", "Inspector-General of Police", "IGP", "commissioned_officer"),
    ],
}
RANK_STATUS = {"NA": I, "NN": C, "NAF": I, "NPF": I}  # Navy ratings to be supplied; officer ranks illustrative

# --------------------------------------------------------------------------- module templates (syllabus headings)
_BASIC = (
    ("ORIENT", "Service orientation, history, values and conduct", "professional_core", "written"),
    ("DISC", "Drill, discipline and service routine", "professional_core", "practical"),
    ("PT", "Physical training and fitness", "physical_fitness", "practical"),
    ("LAW", "Law, human rights and the service code of conduct", "law_human_rights", "written"),
    ("FIRSTAID", "First aid, health and safety", "health_first_aid", "practical"),
    ("ICT", "Communication, records and basic ICT", "ict_cyber", "written"),
    ("COMM", "Community relations and public engagement", "community_relations", "continuous"),
    ("FIELD", "Field practicals (detail held by the agency)", "field_practical", "practical"),
)
_CADET_DEGREE = (
    (
        "DEGREE",
        "Degree programme courses (regulator-approved curriculum of the cadet's department)",
        "academic",
        "mixed",
    ),
    ("PROF", "Professional training of the service (detail held by the agency)", "professional_core", "mixed"),
    ("LEAD", "Leadership, character and ethics", "leadership_ethics", "continuous"),
    ("LAW", "Law, human rights and the law of armed conflict / policing law", "law_human_rights", "written"),
    ("PT", "Physical training, sports and endurance", "physical_fitness", "practical"),
    ("FIELD", "Field exercises (detail held by the agency)", "field_practical", "practical"),
    ("PROJECT", "Final-year research project", "research", "project"),
)
_INITIAL_OFFICER = (
    ("BRANCH", "Arm or branch professional training (detail held by the agency)", "professional_core", "mixed"),
    ("LEAD", "Junior leadership and command", "leadership_ethics", "continuous"),
    ("ADMIN", "Administration and staff duties", "management_administration", "written"),
    ("LAW", "Law and human rights in operations", "law_human_rights", "written"),
    ("PT", "Physical training", "physical_fitness", "practical"),
    ("FIELD", "Field practicals (detail held by the agency)", "field_practical", "practical"),
)
_CAREER = (
    ("STAFF", "Staff duties, writing and briefing", "management_administration", "written"),
    ("LEAD", "Command, leadership and ethics", "leadership_ethics", "continuous"),
    ("PROF", "Professional studies (detail held by the agency)", "professional_core", "mixed"),
    ("LAW", "Law, governance and human rights", "law_human_rights", "written"),
    ("ICT", "Information management", "ict_cyber", "written"),
    ("PAPER", "Research paper", "research", "project"),
)
_STRATEGIC = (
    ("SEC", "National security and strategy studies", "professional_core", "mixed"),
    ("POLICY", "Public policy, governance and international relations", "management_administration", "written"),
    ("LEAD", "Strategic leadership and ethics", "leadership_ethics", "continuous"),
    ("TOUR", "Study tours", "field_practical", "oral"),
    ("THESIS", "Research thesis", "research", "project"),
)
_SPECIALIST = (
    ("SPEC", "Specialist professional training (detail held by the agency)", "professional_core", "mixed"),
    ("LAW", "Law and human rights for the specialism", "law_human_rights", "written"),
    ("SAFETY", "Health and safety", "health_first_aid", "practical"),
    ("PRACT", "Supervised practicals (detail held by the agency)", "field_practical", "practical"),
)
_ACADEMIC = (
    ("PROG", "Programme courses (regulator-approved curriculum)", "academic", "mixed"),
    ("PROJECT", "Project or dissertation", "research", "project"),
)
_SECONDARY = (
    ("CURR", "Junior and senior secondary curriculum (NERDC)", "academic", "mixed"),
    ("CADET", "Cadet, character and leadership training", "leadership_ethics", "continuous"),
    ("PT", "Physical training and sports", "physical_fitness", "practical"),
    ("CIVIC", "Civic education and community service", "community_relations", "continuous"),
)
SECONDARY_LEVELS = ("JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3")

TEMPLATES = {
    "recruit_basic": _BASIC,
    "cadet_degree": _CADET_DEGREE,
    "initial_officer": _INITIAL_OFFICER,
    "promotion_career": _CAREER,
    "command_and_staff": _CAREER,
    "strategic_leadership": _STRATEGIC,
    "specialist": _SPECIALIST,
    "academic_programme": _ACADEMIC,
    "junior_leadership": _INITIAL_OFFICER,
    "continuing_professional": _SPECIALIST,
}


def _c(code: str, title: str, category: str, award: str, award_title: str, **kw: object) -> Course:
    return Course(code, title, category, award, award_title, **kw)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- institutions (FR-STI-04) and courses (FR-STI-05)
INSTITUTIONS: list[tuple[Institution, list[Course]]] = [
    # ---------------- tri-service (Defence Headquarters)
    (
        Institution(
            "NDA",
            "Nigerian Defence Academy",
            "NDA",
            "DHQ",
            "DHQ-EDU",
            "military_academy",
            "military_academy",
            "NG-KD",
            "Kaduna",
            "Commandant",
            accreditation=("NUC",),
            established=1964,
            levels=("UG100", "PG"),
        ),
        [
            _c(
                "RC",
                "Regular Course — officer cadet degree programme",
                "cadet_degree",
                "degree",
                "Bachelor's degree and commission",
                accrediting_body="NUC",
                target_ranks=("OCDT",),
                entry=(
                    "Senior school certificate with credits as advertised",
                    "UTME",
                    "Age, medical and fitness criteria",
                ),
            ),
            _c(
                "PG",
                "Postgraduate programmes",
                "academic_programme",
                "postgraduate",
                "M.Sc. / PhD",
                accrediting_body="NUC",
            ),
        ],
    ),
    (
        Institution(
            "AFCSC",
            "Armed Forces Command and Staff College",
            "AFCSC",
            "DHQ",
            "DHQ-EDU",
            "staff_college",
            "staff_college",
            "NG-KD",
            "Jaji",
            "Commandant",
            established=1976,
        ),
        [
            _c("JC", "Junior Course", "command_and_staff", "staff_qualification", "Junior staff course"),
            _c("SC", "Senior Course", "command_and_staff", "staff_qualification", "psc"),
        ],
    ),
    (
        Institution(
            "NDC",
            "National Defence College",
            "NDC",
            "DHQ",
            "DHQ-EDU",
            "defence_college",
            "defence_college",
            "NG-FC",
            "Abuja",
            "Commandant",
            established=1992,
        ),
        [_c("CSE", "Course of the National Defence College", "strategic_leadership", "staff_qualification", "fdc")],
    ),
    # ---------------- Nigerian Army
    (
        Institution(
            "DEPOTNA",
            "Depot Nigerian Army",
            "Depot NA",
            "NA",
            "TRADOC",
            "depot",
            "security_training_school",
            "NG-KD",
            "Zaria",
            "Commandant",
        ),
        [
            _c(
                "BMT",
                "Basic military training for recruits",
                "recruit_basic",
                "certificate",
                "Basic training",
                target_ranks=("RCT",),
            )
        ],
    ),
    (
        Institution(
            "NASI",
            "Nigerian Army School of Infantry",
            "NASI",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-KD",
            "Jaji",
            "Commandant",
        ),
        [
            _c(
                "YOC",
                "Young Officers Course (Infantry)",
                "initial_officer",
                "certificate",
                "YOC",
                target_ranks=("2LT", "LT"),
            ),
            _c(
                "CCC",
                "Company Commanders Course",
                "promotion_career",
                "certificate",
                "Course certificate",
                target_ranks=("CAPT", "MAJ"),
                status=C,
            ),
        ],
    ),
    (
        Institution(
            "NASA",
            "Nigerian Army School of Artillery",
            "NASA",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-NI",
            "Kontagora",
            "Commandant",
        ),
        [
            _c(
                "YOC",
                "Young Officers Course (Artillery)",
                "initial_officer",
                "certificate",
                "YOC",
                target_ranks=("2LT", "LT"),
            )
        ],
    ),
    (
        Institution(
            "NAACCS",
            "Nigerian Army Armoured Corps Centre and School",
            "NAACCS",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-BA",
            "Bauchi",
            "Commandant",
        ),
        [
            _c(
                "YOC",
                "Young Officers Course (Armour)",
                "initial_officer",
                "certificate",
                "YOC",
                target_ranks=("2LT", "LT"),
            )
        ],
    ),
    (
        Institution(
            "NASS",
            "Nigerian Army School of Signals",
            "NASS",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-LA",
            "Apapa",
            "Commandant",
            status=C,
        ),
        [
            _c(
                "YOC",
                "Young Officers Course (Signals)",
                "initial_officer",
                "certificate",
                "YOC",
                target_ranks=("2LT", "LT"),
            )
        ],
    ),
    (
        Institution(
            "NASME",
            "Nigerian Army School of Military Engineering",
            "NASME",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-BE",
            "Makurdi",
            "Commandant",
        ),
        [
            _c(
                "YOC",
                "Young Officers Course (Engineers)",
                "initial_officer",
                "certificate",
                "YOC",
                target_ranks=("2LT", "LT"),
            )
        ],
    ),
    (
        Institution(
            "NAUB",
            "Nigerian Army University Biu",
            "NAUB",
            "NA",
            "AHQ",
            "defence_university",
            "university",
            "NG-BO",
            "Biu",
            "Vice-Chancellor",
            access_regime="standard",
            accreditation=("NUC",),
            established=2018,
            levels=("UG100", "UG200", "UG300", "UG400"),
        ),
        [
            _c(
                "UG",
                "Undergraduate degree programmes",
                "academic_programme",
                "degree",
                "Bachelor's degree",
                accrediting_body="NUC",
            )
        ],
    ),
    (
        Institution(
            "NAITES",
            "Nigerian Army Institute of Technology and Environmental Studies",
            "NAITES",
            "NA",
            "AHQ",
            "technical_institute",
            "polytechnic",
            "NG-BE",
            "Makurdi",
            "Commandant",
            accreditation=("NBTE",),
            status=C,
        ),
        [
            _c(
                "ND",
                "National Diploma programmes",
                "academic_programme",
                "diploma",
                "ND",
                accrediting_body="NBTE",
                status=C,
            )
        ],
    ),
    # ---------------- Nigerian Navy
    (
        Institution(
            "NNBTS",
            "Nigerian Navy Basic Training School",
            "NNBTS",
            "NN",
            "NAVTRAC",
            "training_school",
            "security_training_school",
            "NG-RI",
            "Onne",
            "Commandant",
        ),
        [_c("BTC", "Basic training course for ratings", "recruit_basic", "certificate", "Basic training")],
    ),
    (
        Institution(
            "NNEC",
            "Nigerian Navy Engineering College",
            "NNEC",
            "NN",
            "NAVTRAC",
            "technical_institute",
            "security_training_school",
            "NG-DE",
            "Sapele",
            "Commandant",
            status=C,
        ),
        [
            _c(
                "TECH",
                "Marine engineering technical courses",
                "specialist",
                "certificate",
                "Course certificate",
                status=C,
            )
        ],
    ),
    (
        Institution(
            "NWCN",
            "Naval War College Nigeria",
            "NWC",
            "NN",
            "NHQ",
            "war_college",
            "staff_college",
            "NG-CR",
            "Calabar",
            "Commandant",
            status=C,
        ),
        [_c("NWC", "Naval war course", "command_and_staff", "staff_qualification", "Course qualification", status=C)],
    ),
    (
        Institution(
            "NNSHS",
            "Nigerian Navy School of Health Sciences",
            "NNSHS",
            "NN",
            "NAVTRAC",
            "health_sciences_school",
            "school_of_health_technology",
            "NG-KW",
            "Offa",
            "Commandant",
            status=C,
        ),
        [_c("HS", "Health sciences programmes", "academic_programme", "diploma", "Diploma", status=C)],
    ),
    # ---------------- Nigerian Air Force
    (
        Institution(
            "AFIT",
            "Air Force Institute of Technology",
            "AFIT",
            "NAF",
            "HQNAF",
            "technical_institute",
            "university",
            "NG-KD",
            "Kaduna",
            "Commandant",
            access_regime="standard",
            accreditation=("NUC", "NBTE"),
            levels=("ND", "HND", "UG100", "UG200", "UG300", "UG400"),
        ),
        [
            _c(
                "UG",
                "Undergraduate degree programmes",
                "academic_programme",
                "degree",
                "Bachelor's degree",
                accrediting_body="NUC",
            ),
            _c("ND", "National Diploma programmes", "academic_programme", "diploma", "ND", accrediting_body="NBTE"),
        ],
    ),
    (
        Institution(
            "NAFMTC",
            "NAF Military Training Centre",
            "MTC",
            "NAF",
            "ATC",
            "training_school",
            "security_training_school",
            "NG-KD",
            "Kaduna",
            "Commandant",
        ),
        [
            _c(
                "BMT",
                "Basic military training for airmen and airwomen",
                "recruit_basic",
                "certificate",
                "Basic training",
                target_ranks=("RCT",),
            )
        ],
    ),
    (
        Institution(
            "301FTS",
            "301 Flying Training School",
            "301 FTS",
            "NAF",
            "ATC",
            "specialist_school",
            "security_training_school",
            "NG-KD",
            "Kaduna",
            "Commandant",
            status=C,
        ),
        [
            _c(
                "FLY",
                "Ab initio flying training",
                "specialist",
                "certificate",
                "Course certificate",
                target_ranks=("PLTOFF", "FGOFF"),
                status=C,
            )
        ],
    ),
    # ---------------- Nigeria Police Force
    (
        Institution(
            "POLAC",
            "Nigeria Police Academy",
            "POLAC",
            "NPF",
            "DTD",
            "police_academy",
            "police_academy",
            "NG-KN",
            "Wudil",
            "Commandant",
            accreditation=("NUC",),
            levels=("UG100", "UG200", "UG300", "UG400"),
        ),
        [
            _c(
                "CADET",
                "Cadet degree programme (Cadet Assistant Superintendents)",
                "cadet_degree",
                "degree",
                "Bachelor's degree and appointment as ASP",
                accrediting_body="NUC",
                target_ranks=("CADET",),
            )
        ],
    ),
    (
        Institution(
            "PSC",
            "Police Staff College",
            "PSC Jos",
            "NPF",
            "DTD",
            "staff_college",
            "staff_college",
            "NG-PL",
            "Jos",
            "Commandant",
        ),
        [
            _c(
                "SCC",
                "Senior Command Course",
                "command_and_staff",
                "staff_qualification",
                "Course qualification",
                target_ranks=("SP", "CSP"),
                status=C,
            ),
            _c(
                "ICC",
                "Intermediate Command Course",
                "promotion_career",
                "certificate",
                "Course certificate",
                target_ranks=("ASP", "DSP"),
                status=C,
            ),
        ],
    ),
    (
        Institution(
            "PCI",
            "Police College Ikeja",
            "PC Ikeja",
            "NPF",
            "DTD",
            "training_college",
            "security_training_school",
            "NG-LA",
            "Ikeja",
            "Commandant",
        ),
        [
            _c(
                "RCC",
                "Recruit constables course",
                "recruit_basic",
                "certificate",
                "Basic training",
                target_ranks=("RCT",),
            )
        ],
    ),
    (
        Institution(
            "PMFTC",
            "Police Mobile Force Training College",
            "PMF TC",
            "NPF",
            "DTD",
            "specialist_school",
            "security_training_school",
            "NG-OS",
            "Ila-Orangun",
            "Commandant",
            status=C,
        ),
        [
            _c(
                "PMF",
                "Mobile force course",
                "specialist",
                "certificate",
                "Course certificate",
                content_held=False,
                status=C,
            )
        ],
    ),
    (
        Institution(
            "PDC",
            "Police Detective College",
            "PDC",
            "NPF",
            "DTD",
            "specialist_school",
            "security_training_school",
            "NG-EN",
            "Enugu",
            "Commandant",
            status=C,
        ),
        [_c("DET", "Detective and investigation course", "specialist", "certificate", "Course certificate", status=C)],
    ),
    # ---------------- paramilitary, law-enforcement, emergency and security services
    (
        Institution(
            "NSCDCA",
            "Civil Defence Academy",
            "NSCDC Academy",
            "NSCDC",
            "TRG",
            "service_academy",
            "paramilitary_academy",
            "NG-FC",
            "Sauka",
            "Commandant",
            status=C,
        ),
        [_c("BASIC", "Basic course for officers", "recruit_basic", "certificate", "Basic training", status=C)],
    ),
    (
        Institution(
            "NCOSSC",
            "Correctional Staff College",
            "CSC",
            "NCOS",
            "TRG",
            "staff_college",
            "staff_college",
            "NG-KD",
            "Kaduna",
            "Commandant",
            status=C,
        ),
        [_c("BASIC", "Basic correctional officers course", "recruit_basic", "certificate", "Basic training", status=C)],
    ),
    (
        Institution(
            "ITSKANO",
            "Immigration Training School, Kano",
            "ITS Kano",
            "NIS",
            "TRG",
            "training_school",
            "security_training_school",
            "NG-KN",
            "Kano",
            "Commandant",
            status=C,
        ),
        [_c("BASIC", "Basic immigration course", "recruit_basic", "certificate", "Basic training", status=C)],
    ),
    (
        Institution(
            "CCSC",
            "Customs Command and Staff College",
            "CCSC",
            "NCS",
            "TRG",
            "staff_college",
            "staff_college",
            "NG-FC",
            "Gwagwalada",
            "Commandant",
            status=C,
        ),
        [
            _c(
                "CSC",
                "Command and staff course",
                "command_and_staff",
                "staff_qualification",
                "Course qualification",
                status=C,
            )
        ],
    ),
    (
        Institution(
            "CTC",
            "Customs Training College, Ikeja",
            "CTC Ikeja",
            "NCS",
            "TRG",
            "training_college",
            "security_training_school",
            "NG-LA",
            "Ikeja",
            "Commandant",
            status=C,
        ),
        [_c("BASIC", "Basic customs course", "recruit_basic", "certificate", "Basic training", status=C)],
    ),
    (
        Institution(
            "FFSTS",
            "Federal Fire Service Training School",
            "FFS TS",
            "FFS",
            "FHQ",
            "training_school",
            "security_training_school",
            "NG-LA",
            "Lagos",
            "Commandant",
            status=C,
        ),
        [_c("BASIC", "Basic firefighting course", "recruit_basic", "certificate", "Basic training", status=C)],
    ),
    (
        Institution(
            "FRSCA",
            "FRSC Academy",
            "FRSC Academy",
            "FRSC",
            "NHQ",
            "service_academy",
            "paramilitary_academy",
            "NG-EN",
            "Udi",
            "Commandant",
        ),
        [_c("BASIC", "Basic marshal training", "recruit_basic", "certificate", "Basic training", status=C)],
    ),
    (
        Institution(
            "NDLEAA",
            "NDLEA Academy",
            "NDLEA Academy",
            "NDLEA",
            "NHQ",
            "service_academy",
            "paramilitary_academy",
            "NG-PL",
            "Jos",
            "Commandant",
        ),
        [_c("BASIC", "Basic narcotics officers course", "recruit_basic", "certificate", "Basic training", status=C)],
    ),
    (
        Institution(
            "EFCCA",
            "EFCC Academy",
            "EFCC Academy",
            "EFCC",
            "HQ",
            "service_academy",
            "paramilitary_academy",
            "NG-FC",
            "Karu",
            "Commandant",
            status=C,
        ),
        [_c("DIC", "Detective inspectors course", "initial_officer", "certificate", "Course certificate", status=C)],
    ),
    (
        Institution(
            "NISS",
            "National Institute for Security Studies",
            "NISS",
            "DSS",
            "NHQ",
            "strategic_institute",
            "defence_college",
            "NG-FC",
            "Abuja",
            "Commandant",
            access_regime="content_not_held",
            status=C,
        ),
        [
            _c(
                "EIMC",
                "Executive Intelligence Management Course",
                "strategic_leadership",
                "staff_qualification",
                "Course qualification",
                content_held=False,
                status=C,
            )
        ],
    ),
    # ---------------- agencies' secondary schools and further institutions (CR-005)
    (
        Institution(
            "NMS",
            "Nigerian Military School, Zaria",
            "NMS Zaria",
            "NA",
            "DAE",
            "secondary_school",
            "combined_secondary",
            "NG-KD",
            "Zaria",
            "Commandant",
            access_regime="standard",
            levels=SECONDARY_LEVELS,
        ),
        [
            _c(
                "SEC",
                "Secondary programme with military training",
                "academic_programme",
                "certificate",
                "BECE, SSCE and NABTEB certificates",
                modules=_SECONDARY,
            )
        ],
    ),
    *[
        (
            Institution(
                code,
                name,
                short,
                "NA",
                "DAE",
                "secondary_school",
                "combined_secondary",
                state,
                town,
                "Principal",
                access_regime="standard",
                levels=SECONDARY_LEVELS,
                status=C,
            ),
            [
                _c(
                    "SEC",
                    "Junior and senior secondary programme",
                    "academic_programme",
                    "certificate",
                    "BECE and SSCE",
                    modules=_SECONDARY,
                    status=C,
                )
            ],
        )
        for code, name, short, state, town in (
            ("CSSIPAJA", "Command Secondary School, Ipaja", "CSS Ipaja", "NG-LA", "Ipaja"),
            ("CSSKADUNA", "Command Secondary School, Kaduna", "CSS Kaduna", "NG-KD", "Kaduna"),
            ("CSSJOS", "Command Secondary School, Jos", "CSS Jos", "NG-PL", "Jos"),
            ("CSSIBADAN", "Command Secondary School, Ibadan", "CSS Ibadan", "NG-OY", "Ibadan"),
        )
    ],
    (
        Institution(
            "AFMS",
            "Air Force Military School, Jos",
            "AFMS Jos",
            "NAF",
            "HQNAF",
            "secondary_school",
            "combined_secondary",
            "NG-PL",
            "Jos",
            "Commandant",
            access_regime="standard",
            levels=SECONDARY_LEVELS,
        ),
        [
            _c(
                "SEC",
                "Secondary programme with military training",
                "academic_programme",
                "certificate",
                "BECE and SSCE",
                modules=_SECONDARY,
            )
        ],
    ),
    *[
        (
            Institution(
                code,
                name,
                short,
                "NN",
                "NHQ",
                "secondary_school",
                "combined_secondary",
                state,
                town,
                "Principal",
                access_regime="standard",
                levels=SECONDARY_LEVELS,
                status=C,
            ),
            [
                _c(
                    "SEC",
                    "Junior and senior secondary programme",
                    "academic_programme",
                    "certificate",
                    "BECE and SSCE",
                    modules=_SECONDARY,
                    status=C,
                )
            ],
        )
        for code, name, short, state, town in (
            ("NSSOJO", "Navy Secondary School, Ojo", "NSS Ojo", "NG-LA", "Ojo"),
            ("NSSABEOKUTA", "Navy Secondary School, Abeokuta", "NSS Abeokuta", "NG-OG", "Abeokuta"),
        )
    ],
    (
        Institution(
            "NACN",
            "Nigerian Army College of Nursing, Yaba",
            "NACN Yaba",
            "NA",
            "AHQ",
            "health_sciences_school",
            "school_of_nursing",
            "NG-LA",
            "Yaba",
            "Commandant",
            access_regime="standard",
            levels=("NURSING",),
            status=C,
        ),
        [
            _c(
                "RN",
                "General nursing programme",
                "academic_programme",
                "diploma",
                "Registered Nurse (NMCN)",
                accrediting_body="NMCN",
                status=C,
            )
        ],
    ),
    (
        Institution(
            "NASMP",
            "Nigerian Army School of Military Police",
            "NASMP",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-KD",
            "Basawa",
            "Commandant",
            status=C,
        ),
        [_c("SPEC", "Military police courses", "specialist", "certificate", "Course certificate", status=C)],
    ),
    (
        Institution(
            "NASFA",
            "Nigerian Army School of Finance and Administration",
            "NASFA",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-LA",
            "Apapa",
            "Commandant",
            status=C,
        ),
        [_c("SPEC", "Finance and administration courses", "specialist", "certificate", "Course certificate", status=C)],
    ),
    (
        Institution(
            "NASE",
            "Nigerian Army School of Education",
            "NASE",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-KW",
            "Ilorin",
            "Commandant",
            status=C,
        ),
        [_c("SPEC", "Army education courses", "specialist", "certificate", "Course certificate", status=C)],
    ),
    (
        Institution(
            "MLAILPKC",
            "Martin Luther Agwai International Leadership and Peacekeeping Centre",
            "MLAILPKC",
            "NA",
            "TRADOC",
            "specialist_school",
            "security_training_school",
            "NG-KD",
            "Jaji",
            "Commandant",
            status=C,
        ),
        [_c("PSO", "Peace support operations courses", "specialist", "certificate", "Course certificate", status=C)],
    ),
    *[
        (
            Institution(
                code,
                name,
                short,
                "NPF",
                "DTD",
                "training_college",
                "security_training_school",
                state,
                town,
                "Commandant",
                status=C,
            ),
            [
                _c(
                    "RCC",
                    "Recruit constables course",
                    "recruit_basic",
                    "certificate",
                    "Basic training",
                    target_ranks=("RCT",),
                    status=C,
                )
            ],
        )
        for code, name, short, state, town in (
            ("PCKADUNA", "Police College, Kaduna", "PC Kaduna", "NG-KD", "Kaduna"),
            ("PCMAIDUGURI", "Police College, Maiduguri", "PC Maiduguri", "NG-BO", "Maiduguri"),
            ("PCOJIRIVER", "Police College, Oji River", "PC Oji River", "NG-EN", "Oji River"),
        )
    ],
    (
        Institution(
            "DIC",
            "Defence Intelligence College",
            "DIC",
            "DHQ",
            "DHQ-EDU",
            "strategic_institute",
            "defence_college",
            "NG-FC",
            "Karu",
            "Commandant",
            access_regime="content_not_held",
            status=C,
        ),
        [
            _c(
                "CSE",
                "Defence intelligence courses",
                "specialist",
                "certificate",
                "Course certificate",
                content_held=False,
                status=C,
            )
        ],
    ),
]
