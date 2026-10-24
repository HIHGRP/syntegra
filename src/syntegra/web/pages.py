"""Page registry (MFS Part B page catalogue, 260 pages) — which pages exist, who may open them, which are built.

Each catalogue page carries its route, classification and roles. ``IMPLEMENTED`` maps the page ids that are
served by this release to their Django URL names; the rest are listed as planned by phase.
"""

from __future__ import annotations

from typing import Any

from syntegra.core import catalog

IMPLEMENTED: dict[str, str] = {
    "PUB-01": "verify",
    "ATT-01": "register",
    "LRN-02": "learner_new",
    "LRN-04": "learner",
    "CUR-101": "coverage",
    "FCL-01": "clearance",
    "FCL-04": "clearance_network",
    "HRM-01": "establishment",
    "STI-01": "security_training",
    "FED-01": "federal_institutions",
    "REG-01": "regulators",
    "REG-02": "institution_regulation",
    "STI-02": "security_institution",
    "STI-03": "security_course",
    "STI-04": "security_intake",
    "AUT-02": "mfa_challenge",
    "AUT-03": "workspace",
    "HOM-04": "profile",
    "ADM-103": "sign_in_providers",
    "CMD-101": "control_room",
    "CMD-102": "league",
    "FIN-02": "budget_execution",
    "ACC-01": "imprest",
    "FND-01": "funding",
    "FND-02": "funding_agreement",
    "EST-01": "property_register",
    "EST-02": "facility_actions",
    "EST-03": "infrastructure",
    "OPS-01": "facilities",
    "STI-05": "security_careers",
    "EXM-01": "exam_series",
    "EXM-03": "exam_seating",
    "BEH-102": "seating",
    "ACA-101": "class_plan",
    "CUR-09": "lesson_plans",
    "ASM-01": "markbook",
    "ASM-04": "report_cards",
    "ADM-101": "access_levels",
    "ADM-102": "sessions_admin",
    "DOC-104": "documents",
    "DOC-105": "document_view",
    "DOC-107": "document_upload",
    "DOC-108": "school_documents",
    "DOC-109": "releases_page",
}
# Pages served for any signed-in user, independent of role lists
UNIVERSAL = {"home", "catalogue", "forms_hub", "form_page"}

# Access level needed to open a page (CR-007, FR-ADM-201). By default a page's catalogue classification. Pages whose
# content is trimmed for each viewer — tabs, fields or records above the viewer's level are withheld by the services —
# are entered at a lower level; the data-level checks still apply inside them.
ENTRY_LEVEL: dict[str, str] = {
    "AUT-02": "public",  # the second factor comes before any access level applies
    "AUT-03": "public",  # choosing the role comes before any access level applies
    "LRN-04": "confidential",  # Learner 360: safeguarding (special) and restricted tabs are withheld per viewer
    "LRN-02": "confidential",  # registration captures data; identity numbers are revealed only to cleared roles
    "FCL-01": "confidential",  # fee-clearance check: obligation detail stays purpose-bound in the service
    "FND-02": "confidential",  # funding agreement: borrowers see their own; others need the restricted level
    "DOC-104": "confidential",  # documents hold personal records; each document's own level is checked as well
    "DOC-105": "confidential",
    "ASM-04": "confidential",  # report cards carry each learner's results, attendance and comments
}


def entry_level(page_id: str) -> str:
    if page_id in ENTRY_LEVEL:
        return ENTRY_LEVEL[page_id]
    return str(page(page_id).get("classification") or "internal").lower()


def all_pages() -> list[dict[str, Any]]:
    return list(catalog.catalog().get("pages", []))


def page(page_id: str) -> dict[str, Any]:
    for p in all_pages():
        if p["id"] == page_id:
            return p
    raise KeyError(page_id)


def for_role(role: str | None) -> list[dict[str, Any]]:
    if not role:
        return []
    return [p for p in all_pages() if role in p["roles"] or "All" in p["roles"]]


def status(page_id: str) -> str:
    return "live" if page_id in IMPLEMENTED else "planned"
