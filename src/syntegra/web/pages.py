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
    "AUT-03": "workspace",
}
# Pages served for any signed-in user, independent of role lists
UNIVERSAL = {"home", "catalogue", "forms_hub", "form_page"}


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
