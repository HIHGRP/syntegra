"""CR-005: federal unity colleges and special training institutions; every institution's regulatory profile."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from syntegra.core.errors import Forbidden
from tests.conftest import FED_HOST

pytestmark = pytest.mark.django_db(databases="__all__")


def fed_ctx(role: str, scope_code: str) -> Any:
    from syntegra.core import authz, context
    from syntegra.core.context import Context
    from syntegra.federal_institutions import registry
    from syntegra.governance.models import ScopeNode
    from syntegra.iam import services as iam

    sysctx = registry.system_context()
    with context.use(sysctx):
        u = iam.create_user(
            sysctx,
            username=f"{role.lower()}-{uuid.uuid4().hex[:8]}@fed.test",
            display_name=role,
            password="correct-horse-battery",
        )
        g = iam.grant_role(sysctx, user=u, role_code=role, scope_id=ScopeNode.objects.get(code=scope_code).id)
    tid = sysctx.state_tenant_id
    base = Context(tenant_id=tid, state_tenant_id=tid, actor_kind="user", actor_id=u.id)
    with context.use(base):
        return authz.grant_context(base, g.id), u


def test_national_directory_of_watchdogs_and_their_dependencies(fed: Any) -> None:
    from syntegra.regulation import services as reg

    d = reg.directory()
    codes = {b["code"] for b in d["bodies"]}
    assert {
        "FME",
        "NUC",
        "NBTE",
        "NCCE",
        "UBEC",
        "NERDC",
        "TRCN",
        "WAEC",
        "NECO",
        "NABTEB",
        "NBAIS",
        "JAMB",
        "TETFUND",
        "NMCN",
        "MDCN",
        "NCAA",
    } <= codes
    jamb = next(b for b in d["bodies"] if b["code"] == "JAMB")
    assert {x["code"] for x in jamb["depends_on"] if x["type"] == "recognises_results_of"} >= {"WAEC", "NECO", "NABTEB"}
    assert {"type": "supervised_by", "code": "FME", "note": "Parastatal of the Federal Ministry of Education"} in next(
        b for b in d["bodies"] if b["code"] == "NUC"
    )["depends_on"]


def test_every_registered_state_institution_gets_its_profile(world: Any, as_user: Any) -> None:
    from syntegra.regulation import services as reg

    with as_user("STA", world.state_scope):
        p = reg.profile(world.institution.id)  # a state secondary school registered by the fixture
    got = {(link["body_code"], link["relationship"]) for link in p["links"]}
    assert got >= {
        ("ABMOE", "supervision"),  # Abia's own ministry and board replace the generic state bodies (CR-007)
        ("ASUBEB", "supervision"),
        ("NERDC", "curriculum"),
        ("TRCN", "teacher_registration"),
        ("STATE_EXAM_BOARD", "examination"),
    }
    assert p["gaps"] == []


def test_federal_registry_unity_colleges_and_special_institutions(fed: Any) -> None:
    from syntegra.core import context
    from syntegra.federal_institutions import services as fsvc
    from syntegra.regulation import services as reg

    root, _ = fed_ctx("FADM", "NG-FED")
    with context.use(root):
        d = fsvc.directory()
        assert len(d["institutions"]) >= 130 and d["by_type"]["science_technical_college"] == 10
        kc = next(r for r in d["institutions"] if r["name"] == "King's College, Lagos")
        assert (
            kc["zone"] == "south_west"
            and kc["gender_intake"] == "boys"
            and kc["admission_basis"] == "national_common_entrance"
        )
        p = reg.profile(kc["institution_id"])
        rels = {(x["body_code"], x["relationship"]) for x in p["links"]}
        assert (
            rels
            >= {
                ("FME", "supervision"),
                ("NECO", "admission"),
                ("NECO", "examination"),
                ("WAEC", "examination"),
                ("NERDC", "curriculum"),
                ("TRCN", "teacher_registration"),
            }
            and p["gaps"] == []
        )
        ncat = next(r for r in d["institutions"] if r["name"].startswith("Nigerian College of Aviation"))
        assert {"NCAA (licensing)", "NBTE (accreditation)", "JAMB (admission)"} <= set(ncat["depends_on"])
        coe = next(r for r in d["institutions"] if r["name"] == "Federal College of Education (Special), Oyo")
        assert "NCCE (accreditation)" in coe["depends_on"]
    zone, _ = fed_ctx("FADM", "FED.FME.FUC-SW")
    with context.use(zone):
        names = {r["name"] for r in fsvc.directory()["institutions"]}
    assert "King's College, Lagos" in names and "Federal Government College, Kano" not in names
    assert all("Federal College of Education" not in n for n in names)  # zone grant: unity colleges of the zone only


def test_official_list_import_adds_corrects_and_refuses_bad_files(fed: Any) -> None:
    from syntegra.core import context
    from syntegra.federal_institutions import services as fsvc
    from syntegra.regulation import services as reg

    header = ",".join(fsvc.COLUMNS)
    good = "\n".join(
        [
            header,
            'FME,FUC-NW,FGC-KAZAURE,"Federal Government College, Kazaure",FGC Kazaure,unity_college,combined_secondary,'
            "NG-JI,Kazaure,JSS1 JSS2 JSS3 SSS1 SSS2 SSS3,mixed,boarding,national_common_entrance,verified",
            'FME,FUC-SW,KC,"King\'s College, Lagos (Lagos Island)",KC,unity_college_boys,combined_secondary,'
            "NG-LA,Lagos,"
            "JSS1 JSS2 JSS3 SSS1 SSS2 SSS3,boys,boarding,national_common_entrance,verified",
        ]
    )
    bad = header + "\nXYZ,FUC-NW,BAD,Bad row,BAD,unity_college,combined_secondary,LAGOS,Town,JSS1,,,,"
    root, _ = fed_ctx("FADM", "NG-FED")
    with context.use(root):
        r = fsvc.import_csv(bad)
        assert r["applied"] is False and set(r["errors"][0]["problems"]) >= {
            "unknown body",
            "state must be an ISO code such as NG-LA",
        }
        r = fsvc.import_csv(good)
        assert r["applied"] and r["added"] == 1 and r["updated"] == 1 and r["regulatory_links"] >= 6
    root, _ = fed_ctx("FADM", "NG-FED")  # a new request: its scope includes the imported college
    with context.use(root):
        names = {x["name"]: x for x in fsvc.directory()["institutions"]}
        assert (
            "King's College, Lagos (Lagos Island)" in names
            and names["Federal Government College, Kazaure"]["zone"] == "north_west"
        )
        assert reg.profile(names["Federal Government College, Kazaure"]["institution_id"])["gaps"] == []
    officer, _ = fed_ctx("STA", "NG-FED")  # a role without the import permission
    with context.use(officer), pytest.raises(Forbidden):
        fsvc.import_csv(good)


def test_security_institutions_have_profiles_too(fse: Any) -> None:
    from syntegra.core import context
    from syntegra.institutions.models import Institution
    from syntegra.regulation import services as reg
    from syntegra.security_training import registry

    with context.use(registry.system_context()):

        def rels(short: str) -> set[tuple[str, str]]:
            i = Institution.objects.get(short_name=short)
            return {(x["body_code"], x["relationship"]) for x in reg.profile(i.id)["links"]}

        assert rels("NDA") >= {("NUC", "accreditation"), ("JAMB", "admission"), ("FMOD", "supervision")}
        assert ("NMCN", "professional_regulation") in rels("NACN Yaba")
        assert rels("NMS Zaria") >= {("NECO", "examination"), ("WAEC", "examination"), ("NERDC", "curriculum")}
        assert ("FMPA", "supervision") in rels("POLAC")


def test_watchdog_and_federal_pages(fed: Any, client: Any, settings: Any) -> None:
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, FED_HOST]
    page = client.get("/regulators", HTTP_HOST=FED_HOST)
    assert page.status_code == 200 and b"Joint Admissions and Matriculation Board" in page.content  # public
    assert client.get("/api/v1/regulators", HTTP_HOST=FED_HOST).status_code == 200
    _, u = fed_ctx("FADM", "NG-FED")
    client.handler.enforce_csrf_checks = False
    client.post("/sign-in", {"username": u.username, "password": "correct-horse-battery"}, HTTP_HOST=FED_HOST)
    page = client.get("/federal-institutions?zone=south_west", HTTP_HOST=FED_HOST).content
    assert b"Queen&#39;s College, Lagos" in page or b"Queen's College, Lagos" in page
    assert b"Federal Government College, Kano" not in page
    import re

    iid = re.search(rb'href="/institutions/([0-9a-f-]{36})/regulation">Queen', page).group(1).decode()
    page = client.get(f"/institutions/{iid}/regulation", HTTP_HOST=FED_HOST).content
    assert b"Complete profile" in page and b"National Examinations Council" in page
