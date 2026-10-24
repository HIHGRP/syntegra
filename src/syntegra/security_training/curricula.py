"""Curricula through each agency's own structure (CR-006, FR-STI-09 – FR-STI-12).

* ``AGENCY_MODULES`` — syllabus headings specific to each agency's mandate and establishing law, added to every
  course of that agency on top of the common service, leadership and law headings. Headings only: administration,
  law and mandate, never operational, tactical, weapons or intelligence content (CR-004).
* ``MORE_RANKS`` — rank structures of the agencies whose ranks CR-004 did not hold (to be confirmed by each agency).
  DSS and EFCC structures are not published in a form CEDA can hold; they are supplied by the agency.
* ``CAREER`` — the course (or course category) each rank requires for commissioning, confirmation, promotion,
  appointment or command, per agency.
* ``course_units`` — which units of the structure sponsor, approve, deliver and hold quotas on a course.

All entries are reference data marked illustrative or to_confirm until the agency confirms them.
"""

from __future__ import annotations

from typing import Any

I = "illustrative"  # noqa: E741
C = "to_confirm"

# code, title, area, assessment, categories (None = every course of the agency)
Module = tuple[str, str, str, str, tuple[str, ...] | None]
ENTRY = ("recruit_basic", "initial_officer", "cadet_degree")
CAREERS = ("promotion_career", "command_and_staff", "junior_leadership", "strategic_leadership")

AGENCY_MODULES: dict[str, tuple[Module, ...]] = {
    "DHQ": (
        (
            "JOINT",
            "Joint (tri-service) organisation and doctrine of the Armed Forces of Nigeria",
            "professional_core",
            "written",
            None,
        ),
        (
            "AFA",
            "Armed Forces Act, military justice and the law of armed conflict",
            "law_human_rights",
            "written",
            None,
        ),
        (
            "CIVMIL",
            "Civil–military relations and support to civil authority",
            "community_relations",
            "continuous",
            CAREERS,
        ),
    ),
    "NA": (
        (
            "NAORG",
            "Nigerian Army organisation, history, traditions and customs of the service",
            "professional_core",
            "written",
            None,
        ),
        (
            "NALAW",
            "Armed Forces Act, Nigerian Army Act provisions and the Army code of conduct",
            "law_human_rights",
            "written",
            None,
        ),
        (
            "NAADM",
            "Army administration, records and personnel management",
            "management_administration",
            "written",
            CAREERS,
        ),
    ),
    "NN": (
        (
            "NNORG",
            "Nigerian Navy organisation, history, traditions and customs of the service",
            "professional_core",
            "written",
            None,
        ),
        (
            "SEALAW",
            "Law of the sea, maritime law and international maritime conventions",
            "law_human_rights",
            "written",
            None,
        ),
        (
            "SHIPADM",
            "Shipboard administration, seamanship theory and maritime safety",
            "management_administration",
            "mixed",
            None,
        ),
    ),
    "NAF": (
        (
            "NAFORG",
            "Nigerian Air Force organisation, history, traditions and customs of the service",
            "professional_core",
            "written",
            None,
        ),
        (
            "AIRSAFE",
            "Aviation safety culture, airworthiness and flight-safety administration",
            "health_first_aid",
            "written",
            None,
        ),
        ("AIRLAW", "Air law, the Armed Forces Act and civil aviation regulations", "law_human_rights", "written", None),
    ),
    "NPF": (
        ("POLACT", "Police Act 2020, Police Regulations and Force orders", "law_human_rights", "written", None),
        (
            "CRIMLAW",
            "Criminal law and procedure — ACJA 2015, Criminal Code and Penal Code",
            "law_human_rights",
            "written",
            None,
        ),
        (
            "RIGHTS",
            "Constitutional rights, use-of-force principles and police accountability",
            "law_human_rights",
            "written",
            None,
        ),
        ("COMPOL", "Community policing and public relations", "community_relations", "continuous", None),
        (
            "STATION",
            "Station administration, crime records and statistics",
            "management_administration",
            "written",
            None,
        ),
    ),
    "NSCDC": (
        ("NSCDCACT", "NSCDC Act 2003 (as amended) and the Corps' mandate", "law_human_rights", "written", None),
        (
            "CNAI",
            "Critical national assets and infrastructure — administration and inter-agency liaison",
            "professional_core",
            "written",
            None,
        ),
        ("PGC", "Regulation and licensing of private guard companies", "management_administration", "written", None),
        ("DISASTER", "Disaster management and civil defence", "professional_core", "mixed", None),
    ),
    "NCOS": (
        ("NCOSACT", "Nigerian Correctional Service Act 2019", "law_human_rights", "written", None),
        (
            "CUSTODY",
            "Custodial administration, inmates' rights and welfare (UN Nelson Mandela Rules)",
            "law_human_rights",
            "written",
            None,
        ),
        (
            "NONCUST",
            "Non-custodial measures, probation, parole and reintegration",
            "professional_core",
            "written",
            None,
        ),
        ("CASEMGT", "Correctional records and case management", "management_administration", "written", None),
    ),
    "NIS": (
        ("IMMACT", "Immigration Act 2015 and Immigration Regulations", "law_human_rights", "written", None),
        (
            "PASSPORT",
            "Passport, visa and residence permit administration",
            "management_administration",
            "written",
            None,
        ),
        ("BORDER", "Border management and migration data administration", "professional_core", "written", None),
        (
            "ECOWAS",
            "ECOWAS free-movement protocols and international migration law",
            "law_human_rights",
            "written",
            None,
        ),
    ),
    "FFS": (
        ("FIREACT", "Fire Service Act and fire safety regulations", "law_human_rights", "written", None),
        (
            "PREVENT",
            "Fire prevention, building inspection and fire safety education",
            "professional_core",
            "mixed",
            None,
        ),
        (
            "FIRESCI",
            "Fire science, fire service equipment and appliances (theory)",
            "professional_core",
            "written",
            None,
        ),
        ("RESCUE", "Rescue and emergency medical response principles", "health_first_aid", "practical", None),
    ),
    "NCS": (
        ("CUSTACT", "Nigeria Customs Service Act 2023 and customs procedures", "law_human_rights", "written", None),
        (
            "TARIFF",
            "Tariff classification, valuation and rules of origin (HS, WTO Valuation Agreement)",
            "professional_core",
            "written",
            None,
        ),
        ("TRADE", "Trade facilitation, AfCFTA and ECOWAS trade protocols", "professional_core", "written", None),
        ("REVENUE", "Revenue accounting and customs administration", "management_administration", "written", None),
    ),
    "FRSC": (
        (
            "FRSCACT",
            "FRSC (Establishment) Act 2007 and the National Road Traffic Regulations",
            "law_human_rights",
            "written",
            None,
        ),
        ("RSEDU", "Road safety education and public enlightenment", "community_relations", "continuous", None),
        (
            "LICENCE",
            "Driver licensing and vehicle registration administration",
            "management_administration",
            "written",
            None,
        ),
        ("CRASH", "Crash data, reporting and rescue coordination", "health_first_aid", "mixed", None),
    ),
    "NDLEA": (
        ("NDLEAACT", "NDLEA Act and drug control law", "law_human_rights", "written", None),
        ("DEMAND", "Drug demand reduction, prevention and counselling", "community_relations", "continuous", None),
        (
            "UNCONV",
            "International drug control conventions (UN 1961, 1971 and 1988)",
            "law_human_rights",
            "written",
            None,
        ),
        (
            "EXHIBIT",
            "Evidence handling, exhibits and records administration",
            "management_administration",
            "written",
            None,
        ),
    ),
    "EFCC": (
        (
            "EFCCACT",
            "EFCC (Establishment) Act 2004 and the Money Laundering (Prevention and Prohibition) Act 2022",
            "law_human_rights",
            "written",
            None,
        ),
        ("FORENSIC", "Forensic accounting and financial records analysis", "professional_core", "mixed", None),
        ("ASSETS", "Asset recovery and proceeds-of-crime administration", "management_administration", "written", None),
        (
            "CASEFILE",
            "Prosecution liaison, evidence and case-file management",
            "management_administration",
            "written",
            None,
        ),
    ),
    "DSS": (),  # the Service does not release module detail (CR-004 access regime)
}


def _paramilitary(prefix: str, of: str, top: str) -> list[tuple[str, str, str, str]]:
    """The common rank structure of the services under the Civil Defence, Correctional, Fire and Immigration
    Services Board (and the Customs Service), most junior first: code, title, abbreviation, category."""
    return [
        ("ASST", f"{of} Assistant", "ASST", "junior_staff"),
        ("AI", f"Assistant Inspector of {prefix}", "AI", "junior_staff"),
        ("INSP", f"Inspector of {prefix}", "INSP", "junior_staff"),
        ("CI", f"Chief Inspector of {prefix}", "CI", "junior_staff"),
        ("ASII", f"Assistant Superintendent of {prefix} II", "AS II", "senior_staff"),
        ("ASI", f"Assistant Superintendent of {prefix} I", "AS I", "senior_staff"),
        ("DS", f"Deputy Superintendent of {prefix}", "DS", "senior_staff"),
        ("SUPT", f"Superintendent of {prefix}", "SUPT", "senior_staff"),
        ("CS", f"Chief Superintendent of {prefix}", "CS", "senior_staff"),
        ("AC", f"Assistant {top}", "AC", "senior_staff"),
        ("DC", f"Deputy {top}", "DC", "senior_staff"),
        ("CC", top, "CC", "senior_staff"),
        ("ACG", f"Assistant {top}-General", "ACG", "senior_staff"),
        ("DCG", f"Deputy {top}-General", "DCG", "senior_staff"),
        ("CG", f"{top}-General", "CG", "senior_staff"),
    ]


MORE_RANKS: dict[str, list[tuple[str, str, str, str]]] = {
    "NSCDC": _paramilitary("Corps", "Corps", "Commandant"),
    "NCOS": _paramilitary("Corrections", "Correctional", "Controller"),
    "NIS": _paramilitary("Immigration", "Immigration", "Comptroller"),
    "FFS": _paramilitary("Fire", "Fire", "Controller"),
    "NCS": _paramilitary("Customs", "Customs", "Comptroller"),
    "FRSC": [
        ("RMA", "Road Marshal Assistant", "RMA", "junior_staff"),
        ("MI", "Marshal Inspector", "MI", "junior_staff"),
        ("ARC", "Assistant Route Commander", "ARC", "senior_staff"),
        ("DRC", "Deputy Route Commander", "DRC", "senior_staff"),
        ("RC", "Route Commander", "RC", "senior_staff"),
        ("SRC", "Superintendent Route Commander", "SRC", "senior_staff"),
        ("CRC", "Chief Route Commander", "CRC", "senior_staff"),
        ("ACC", "Assistant Corps Commander", "ACC", "senior_staff"),
        ("DCC", "Deputy Corps Commander", "DCC", "senior_staff"),
        ("CC", "Corps Commander", "CC", "senior_staff"),
        ("ACM", "Assistant Corps Marshal", "ACM", "senior_staff"),
        ("DCM", "Deputy Corps Marshal", "DCM", "senior_staff"),
        ("CM", "Corps Marshal", "CM", "senior_staff"),
    ],
    "NDLEA": [
        ("NA", "Narcotics Agent", "NA", "junior_staff"),
        ("ASNII", "Assistant Superintendent of Narcotics II", "ASN II", "senior_staff"),
        ("ASNI", "Assistant Superintendent of Narcotics I", "ASN I", "senior_staff"),
        ("DSN", "Deputy Superintendent of Narcotics", "DSN", "senior_staff"),
        ("SN", "Superintendent of Narcotics", "SN", "senior_staff"),
        ("CSN", "Chief Superintendent of Narcotics", "CSN", "senior_staff"),
        ("ACN", "Assistant Commander of Narcotics", "ACN", "senior_staff"),
        ("DCN", "Deputy Commander of Narcotics", "DCN", "senior_staff"),
        ("CN", "Commander of Narcotics", "CN", "senior_staff"),
        ("ACGN", "Assistant Commander-General of Narcotics", "ACGN", "senior_staff"),
    ],
}

# agency → (rank code, requirement kind, course code or None, course category or None, mandatory)
Req = tuple[str, str, str | None, str | None, bool]
_ARMED = (
    ("PTE", "confirmation", "BMT", None, True),
    ("2LT", "commissioning", "RC", None, True),
    ("LT", "promotion", "YOC", None, True),
    ("MAJ", "promotion", "CCC", None, True),
    ("LTCOL", "promotion", "SC", None, True),
    ("BRIGGEN", "promotion", "CSE", None, True),
    ("COL", "command", None, "command_and_staff", True),
)
CAREER: dict[str, tuple[Req, ...]] = {
    "NA": _ARMED,
    "NN": (
        ("SLT", "commissioning", "RC", None, True),
        ("LCDR", "promotion", "JC", None, True),
        ("CDR", "promotion", "SC", None, True),
        ("CAPT", "command", "NWC", None, False),
        ("CDRE", "promotion", "CSE", None, True),
    ),
    "NAF": (
        ("AC", "confirmation", "BMT", None, True),
        ("PLTOFF", "commissioning", "RC", None, True),
        ("FGOFF", "appointment", "FLY", None, False),
        ("SQNLDR", "promotion", "JC", None, True),
        ("WGCDR", "promotion", "SC", None, True),
        ("AIRCDRE", "promotion", "CSE", None, True),
    ),
    "NPF": (
        ("PC", "confirmation", "RCC", None, True),
        ("ASP", "commissioning", "CADET", None, False),
        ("DSP", "promotion", "ICC", None, True),
        ("CSP", "promotion", "SCC", None, True),
        ("ACP", "command", None, "strategic_leadership", False),
    ),
    "NSCDC": (("ASII", "confirmation", "BASIC", None, True), ("ASST", "confirmation", "BASIC", None, True)),
    "NCOS": (("ASII", "confirmation", "BASIC", None, True), ("ASST", "confirmation", "BASIC", None, True)),
    "NIS": (("ASII", "confirmation", "BASIC", None, True), ("ASST", "confirmation", "BASIC", None, True)),
    "FFS": (("ASII", "confirmation", "BASIC", None, True), ("ASST", "confirmation", "BASIC", None, True)),
    "NCS": (
        ("ASII", "confirmation", "BASIC", None, True),
        ("ASST", "confirmation", "BASIC", None, True),
        ("DC", "promotion", "CSC", None, True),
    ),
    "FRSC": (("ARC", "confirmation", "BASIC", None, True), ("RMA", "confirmation", "BASIC", None, True)),
    "NDLEA": (("ASNII", "confirmation", "BASIC", None, True), ("NA", "confirmation", "BASIC", None, True)),
}

# Units whose role for every course of the agency is fixed by the structure: (agency, unit code) → role
APPROVING = {
    "DHQ": "DHQ",
    "NA": "AHQ",
    "NN": "NHQ",
    "NAF": "HQNAF",
    "NPF": "FHQ",
    "NSCDC": "NHQ",
    "NCOS": "NHQ",
    "NIS": "SHQ",
    "FFS": "FHQ",
    "NCS": "CHQ",
    "FRSC": "NHQ",
    "NDLEA": "NHQ",
    "EFCC": "HQ",
    "DSS": "NHQ",
}
SPONSOR = {
    "DHQ": "DHQ-EDU",
    "NA": "TRADOC",
    "NN": "NAVTRAC",
    "NAF": "ATC",
    "NPF": "DTD",
    "NSCDC": "TRG",
    "NCOS": "TRG",
    "NIS": "TRG",
    "NCS": "TRG",
}
# Tri-service courses: the service headquarters hold the places
QUOTAS = {"DHQ": (("NA", "AHQ"), ("NN", "NHQ"), ("NAF", "HQNAF"))}


def modules_for(agency: str, category: str) -> list[Module]:
    return [m for m in AGENCY_MODULES.get(agency, ()) if m[4] is None or category in m[4]]


def course_units(agency: str, delivering_unit: str, category: str) -> list[tuple[str, str, str]]:
    """(agency, unit code, role) for a course: approving authority, sponsor, delivering unit, quota holders."""
    out = [(agency, delivering_unit, "delivering_unit")]
    if agency in APPROVING:
        out.append((agency, APPROVING[agency], "approving_authority"))
    if agency in SPONSOR:
        out.append((agency, SPONSOR[agency], "sponsor"))
    if category in CAREERS or category in ("specialist", "academic_programme", "cadet_degree"):
        out.extend((a, u, "quota_holder") for a, u in QUOTAS.get(agency, ()))
    seen: set[tuple[str, str, str]] = set()
    return [x for x in out if not (x in seen or seen.add(x))]  # type: ignore[func-returns-value]


def summary() -> dict[str, Any]:
    return {
        "agencies_with_specific_modules": sum(1 for v in AGENCY_MODULES.values() if v),
        "agencies_with_ranks_added": len(MORE_RANKS),
        "career_requirements": sum(len(v) for v in CAREER.values()),
    }
