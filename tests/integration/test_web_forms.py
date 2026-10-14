"""Web forms for every write action, the workspace chooser, and pages that used to fail with HTTP 500 on bad input."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

import pytest
from markupsafe import escape

from tests.conftest import FED_HOST, make_user, user_ctx
from tests.integration.test_hrms import hr  # noqa: F401 — fixture

pytestmark = pytest.mark.django_db(databases="__all__")
PASSWORD = "correct-horse-battery"


def errs(r: Any) -> str:
    """The page's error messages, for assertion messages."""
    return " | ".join(re.findall(r'class="(?:err|alert alert-error)"[^>]*>([^<]*)<', r.content.decode()))


def sign_in(client: Any, user: Any, **kw: Any) -> Any:
    client.handler.enforce_csrf_checks = False
    return client.post("/sign-in", {"username": user.username, "password": PASSWORD}, **kw)


def test_every_form_renders_only_for_roles_that_may_use_it(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.web import forms

    u, _ = make_user(world, "PLAT", world.state_scope)
    assert sign_in(client, u).status_code == 302
    hub = client.get("/forms").content.decode()
    for f in forms.FORMS:  # every form: no server error, whatever data exists
        r = client.get(f"/forms/{f.key}")
        assert r.status_code == 200, (f.key, r.content[-2000:])
        assert str(escape(f.title)) in r.content.decode() and f'href="/forms/{f.key}"' in hub
    assert len(forms.FORMS) == len(forms.REGISTRY) >= 33
    for f in forms.FORMS:  # an empty submission is a validation problem, never a server error
        if any(x.required for x in f.fields):
            r = client.post(f"/forms/{f.key}", {})
            assert r.status_code == 422 and (errs(r) or b"nothing waiting" in r.content), f.key
    assert client.get("/forms/no-such-form").status_code == 404

    client.post("/sign-out")
    t, tg = make_user(world, "TCH", world.institution.scope_node_id)
    sign_in(client, t)
    with context.use(user_ctx(t.id, tg)):
        allowed = {f.key for f in forms.FORMS if f.allowed(context.current())}
    assert allowed == {"hr-leave", "funding-apply"}  # a teacher may only request their own leave or loan
    hub = client.get("/forms").content.decode()
    assert "/forms/hr-leave" in hub and "/forms/institution-register" not in hub
    assert client.get("/forms/institution-register").status_code == 403


def test_institution_register_form_validates_like_the_api_and_saves(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.institutions.models import Institution

    u, g = make_user(world, "STA", world.state_scope)
    sign_in(client, u)
    page = client.get("/forms/institution-register").content.decode()
    assert "Local government area" in page and str(world.lga_scope) in page
    r = client.post("/forms/institution-register", {"name": "", "ownership": "state", "levels": ["JSS1"]})
    assert r.status_code == 422
    body = r.content.decode()
    assert "Please correct the fields" in body and body.count("Required.") >= 3
    assert 'value="state" selected' in body  # values are kept
    r = client.post(
        "/forms/institution-register",
        {"name": "Community School Ohafia", "category": "nonsense", "ownership": "community"},
    )
    assert r.status_code == 422 and b"Choose from the options shown" in r.content
    good = {
        "name": "Community Secondary School Ohafia",
        "category": "combined_secondary",
        "ownership": "community",
        "lga_scope_id": str(world.lga2_scope),
        "town": "Ohafia",
        "levels": ["JSS1", "JSS2"],
        "latitude": "5.61",
    }
    r = client.post("/forms/institution-register", good)
    assert r.status_code == 422 and b"Give both latitude and longitude" in r.content, errs(r)
    good["longitude"] = "7.83"
    r = client.post("/forms/institution-register", good)
    assert r.status_code == 200 and b"registered as" in r.content, errs(r)
    with context.use(user_ctx(u.id, g)):
        inst = Institution.objects.get(name="Community Secondary School Ohafia")
    assert inst.address == {"town": "Ohafia"} and inst.levels == ["JSS1", "JSS2"]
    assert f"/institutions/{inst.id}/regulation".encode() in r.content


def test_class_forms_and_learner_lookup_by_glid(world: Any, as_user: Any, client: Any) -> None:
    from syntegra.academic.models import ClassGroup, ClassMembership
    from syntegra.core import context
    from tests.integration.test_fee_clearance import enrol_at

    lrn = enrol_at(world, as_user, world.institution, "Obinna", level="jss_1")
    h, g = make_user(world, "HEAD", world.institution.scope_node_id)
    sign_in(client, h)
    r = client.post(
        "/forms/class-create",
        {
            "institution_id": str(world.institution.id),
            "period_id": str(world.period.id),
            "name": "JSS 1 Blue",
            "education_level": "JSS1",
            "capacity": "0",
        },
    )
    assert r.status_code == 422 and b"greater than or equal to 1" in r.content, errs(
        r
    )  # the API serializer's own message
    data = {
        "institution_id": str(world.institution.id),
        "period_id": str(world.period.id),
        "name": "JSS 1 Blue",
        "education_level": "JSS1",
    }
    assert client.post("/forms/class-create", data).status_code == 200
    with context.use(user_ctx(h.id, g)):
        cls = ClassGroup.objects.get(name="JSS 1 Blue")
    page = client.get(f"/forms/class-member?target={cls.id}").content.decode()
    assert f'value="{cls.id}" selected' in page
    r = client.post("/forms/class-member", {"target": str(cls.id), "learner_id": "LRN-0000-0000-00"})
    assert r.status_code == 422 and b"No learner with that Global Learner ID" in r.content
    r = client.post("/forms/class-member", {"target": str(cls.id), "learner_id": lrn.global_learner_id.lower()})
    assert r.status_code == 200 and b"Learner added to the class" in r.content
    with context.use(user_ctx(h.id, g)):
        assert ClassMembership.objects.filter(class_group_id=cls.id, learner_id=lrn.id).exists()
    r = client.post("/forms/class-member", {"target": str(uuid.uuid4()), "learner_id": lrn.global_learner_id})
    assert r.status_code == 422 and b"Choose from the options shown" in r.content  # out-of-scope ids are refused


def test_fee_clearance_forms_publish_dispute_and_resolve(world: Any, as_user: Any, client: Any) -> None:
    from syntegra.clearance.models import LearnerObligation, ObligationDispute
    from syntegra.core import context
    from tests.integration.test_fee_clearance import enrol_at

    lrn = enrol_at(world, as_user, world.institution, "Kelechi", level="jss_2")
    h, g = make_user(world, "HEAD", world.institution.scope_node_id)
    sign_in(client, h)
    base = {
        "learner_id": lrn.global_learner_id,
        "creditor_institution_id": str(world.institution.id),
        "kind": "boarding",
        "amount_minor": "12,500.505",
        "oldest_due_on": "2026-05-01",
        "invoices": "INV-1\nINV-2",
        "document_id": "DOC-77",
        "payer_kind": "guardian",
    }
    r = client.post("/forms/obligation-publish", base)
    assert r.status_code == 422 and b"at most two decimal places" in r.content
    r = client.post("/forms/obligation-publish", {**base, "amount_minor": "12,500.50"})
    assert r.status_code == 200 and "₦12,500.50 outstanding".encode() in r.content, errs(r)
    with context.use(user_ctx(h.id, g)):
        ob = LearnerObligation.objects.get(learner_id=lrn.id)
        assert ob.amount_outstanding_minor == 1_250_050 and ob.source == "manual_with_evidence"
        assert ob.evidence == [{"invoice": "INV-1"}, {"invoice": "INV-2"}, {"document_id": "DOC-77"}]
    r = client.post(
        "/forms/obligation-dispute",
        {
            "target": str(ob.id),
            "party": "guardian",
            "grounds": "already_paid",
            "statement": "Paid in cash, receipt 4471",
        },
    )
    assert r.status_code == 200 and b"Dispute recorded" in r.content
    client.post("/sign-out")
    s, sg = make_user(world, "STA", world.state_scope)
    sign_in(client, s)
    with context.use(user_ctx(s.id, sg)):
        d = ObligationDispute.objects.get(obligation_id=ob.id)
    r = client.post(
        "/forms/obligation-dispute-resolve", {"target": str(d.id), "resolution": "upheld", "reason": "short"}
    )
    assert r.status_code == 422 and b"at least 10 characters" in r.content
    r = client.post(
        "/forms/obligation-dispute-resolve",
        {"target": str(d.id), "resolution": "upheld", "reason": "Receipt 4471 verified with the bursar"},
    )
    assert r.status_code == 200 and b"Dispute resolved" in r.content
    with context.use(user_ctx(s.id, sg)):
        assert LearnerObligation.objects.get(pk=ob.id).status == "withdrawn"
    page = client.get("/forms/obligation-dispute-resolve").content
    assert b"There is nothing waiting for this action" in page


def test_hr_forms_create_a_position_and_report_service_errors(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.hr.models import Position

    u, g = make_user(world, "STA", world.state_scope)
    sign_in(client, u)
    page = client.get("/forms/hr-position").content.decode()
    assert 'value="TEACHER"' in page  # cadres seeded with the state (hr.defaults)
    data = {
        "title": "Mathematics teacher",
        "cadre_code": "TEACHER",
        "employer_scope_id": str(world.state_scope),
        "institution_id": str(world.institution.id),
        "grade_level_min": "8",
        "grade_level_max": "18",
        "funding": "funded",
    }
    r = client.post("/forms/hr-position", data)
    assert r.status_code == 422 and b"less than or equal to 17" in r.content
    r = client.post("/forms/hr-position", {**data, "grade_level_max": "12"})
    assert r.status_code == 200 and b"Position" in r.content and b"created" in r.content, errs(r)
    with context.use(user_ctx(u.id, g)):
        assert Position.objects.filter(title="Mathematics teacher", institution_id=world.institution.id).exists()
    r = client.post(
        "/forms/hr-payroll-run",
        {"employer_scope_id": str(world.state_scope), "period_label": "2026-10", "pay_date": "31/10/2026"},
    )
    assert r.status_code == 422 and b"Date has wrong format" in r.content
    r = client.post("/forms/hr-integrity-scan", {})
    assert r.status_code == 200 and b"Scan complete" in r.content


def test_workspace_chooser_after_sign_in_with_several_roles(world: Any, client: Any) -> None:
    from syntegra.core import context
    from syntegra.iam import services as iam
    from tests.conftest import system_ctx

    u, g1 = make_user(world, "HEAD", world.institution.scope_node_id)
    with context.use(system_ctx()):
        g2 = iam.grant_role(system_ctx(), user=u, role_code="LGA", scope_id=world.lga_scope).id
    r = sign_in(client, u, QUERY_STRING="next=/forms")
    assert r.status_code == 302 and r["Location"] == "/auth/context?next=%2Fforms"
    page = client.get("/auth/context?next=/forms")
    assert page.status_code == 200
    body = page.content.decode()
    assert "Head of institution" in body and "LGA education officer" in body and str(g2) in body
    assert client.post("/auth/context", {"grant_id": str(uuid.uuid4())}).status_code == 422
    r = client.post("/auth/context?next=/forms", {"grant_id": str(g2)})
    assert r.status_code == 302 and r["Location"] == "/forms"
    hub = client.get("/forms").content.decode()
    assert "<strong>LGA</strong>" in hub and "/forms/coverage-gap-accept" in hub and "/forms/class-create" not in hub
    r = client.post("/auth/context?next=//evil.example", {"grant_id": str(g1)})
    assert r["Location"] == "/"  # no open redirect
    assert "<strong>HEAD</strong>" in client.get("/forms").content.decode()


def test_regulation_and_federal_import_forms(fed: Any, client: Any, settings: Any) -> None:
    from syntegra.core import authz, context
    from syntegra.core.context import Context
    from syntegra.federal_institutions import registry
    from syntegra.governance.models import ScopeNode
    from syntegra.iam import services as iam
    from syntegra.institutions.models import Institution
    from syntegra.regulation.models import InstitutionRegulation

    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, FED_HOST]
    sysctx = registry.system_context()
    with context.use(sysctx):
        u = iam.create_user(
            sysctx, username=f"fadm-{uuid.uuid4().hex[:8]}@fed.test", display_name="FADM", password=PASSWORD
        )
        g = iam.grant_role(sysctx, user=u, role_code="FADM", scope_id=ScopeNode.objects.get(code="NG-FED").id)
        inst = Institution.objects.filter(name__icontains="Federal Government College").order_by("name").first()
    assert sign_in(client, u, HTTP_HOST=FED_HOST).status_code == 302
    r = client.post(
        "/forms/regulation-link",
        {
            "institution_id": str(inst.id),
            "body_code": "NABTEB",
            "relationship": "examination",
            "covers": "NBC/NTC for technical subjects",
            "levels": "SSS3",
            "reason": "Offers technical subjects to SSS3 candidates",
        },
        HTTP_HOST=FED_HOST,
    )
    assert r.status_code == 200 and b"NABTEB linked" in r.content, errs(r)
    tid = registry.system_context().tenant_id
    base = Context(tenant_id=tid, state_tenant_id=tid, actor_kind="user", actor_id=u.id)
    with context.use(base):
        ctx = authz.grant_context(base, g.id)
    with context.use(ctx):
        link = InstitutionRegulation.objects.get(institution_id=inst.id, body_code="NABTEB", valid_to__isnull=True)
    page = client.get(f"/institutions/{inst.id}/regulation", HTTP_HOST=FED_HOST).content.decode()
    assert f"/forms/regulation-end?institution_id={inst.id}&amp;target={link.id}" in page
    assert f"/forms/regulation-link?institution_id={inst.id}" in page
    end = client.get(f"/forms/regulation-end?institution_id={inst.id}&target={link.id}", HTTP_HOST=FED_HOST)
    assert f'value="{link.id}" selected'.encode() in end.content
    r = client.post(
        f"/forms/regulation-end?institution_id={inst.id}",
        {"institution_id": str(inst.id), "target": str(link.id), "reason": "Entered against the wrong college"},
        HTTP_HOST=FED_HOST,
    )
    assert r.status_code == 200 and b"NABTEB link ended" in r.content
    with context.use(ctx):
        assert InstitutionRegulation.objects.get(pk=link.id).valid_to is not None

    template = Path(__file__).resolve().parents[2] / "ceda" / "templates" / "federal_institutions.csv"
    with template.open("rb") as fh:
        r = client.post("/forms/federal-import", {"csv": fh, "dry_run": "on"}, HTTP_HOST=FED_HOST)
    assert r.status_code == 200 and b"rows are valid" in r.content, errs(r)
    r = client.post("/forms/federal-import", {"dry_run": "on"}, HTTP_HOST=FED_HOST)
    assert r.status_code == 422 and b"Choose a file" in r.content


def test_pages_return_problems_not_server_errors_for_bad_input(world: Any, as_user: Any, client: Any) -> None:
    from tests.integration.test_operations_flows import enrol_class

    cls, _ = enrol_class(world, as_user, n=1)
    h, _ = make_user(world, "HEAD", world.institution.scope_node_id)
    sign_in(client, h)
    assert client.get(f"/registers/class/{cls.id}?date=yesterday").status_code == 422
    assert client.get("/hr/establishment?institution_id=not-a-uuid").status_code == 422
    r = client.post("/admissions/clearance", {"check_id": "nope"})
    assert r.status_code == 422
    r = client.post("/admissions/clearance", {"check_id": str(uuid.uuid4())})
    assert r.status_code == 404


def test_security_training_forms_intake_trainee_and_outcome(fse: Any, client: Any, settings: Any) -> None:
    import datetime as dt

    from syntegra.core import context
    from syntegra.learners import services as learners
    from syntegra.security_training import services as sti
    from tests.integration.test_security_training import HOST, as_fse

    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, HOST]
    root, admin = as_fse("SADM", "NG-FSE")
    with context.use(root):
        nda = next(
            i for a in sti.directory() if a["code"] == "DHQ" for i in a["institutions"] if i["short_name"] == "NDA"
        )
        rc = next(c for c in sti.institution(nda["institution_id"])["courses"] if c["code"] == "RC")
    assert sign_in(client, admin, HTTP_HOST=HOST).status_code == 302
    page = client.get(f"/security-training/courses/{rc['id']}", HTTP_HOST=HOST).content.decode()
    assert f"/forms/security-intake?target={rc['id']}" in page
    code = f"F{uuid.uuid4().hex[:5]}".upper()
    form = {"target": str(rc["id"]), "intake_code": code, "name": "Form-made Regular Course", "starts_on": "2026-09-07"}
    r = client.post("/forms/security-intake", {**form, "ends_on": "2026-01-01", "capacity": "-3"}, HTTP_HOST=HOST)
    assert r.status_code == 422 and b"greater than or equal to 1" in r.content, errs(r)
    r = client.post("/forms/security-intake", form, HTTP_HOST=HOST)
    assert r.status_code == 200 and f"Intake {code} created".encode() in r.content, errs(r)
    intake = re.search(rb'href="/security-training/intakes/([0-9a-f-]{36})"', r.content).group(1).decode()
    client.post("/sign-out", HTTP_HOST=HOST)

    officer, sto = as_fse("STO", "DHQ.NDA")
    with context.use(officer):
        cadet = learners.register(
            learners.RegisterLearner(
                given="Ibrahim",
                family="Garba",
                date_of_birth=dt.date(2006, 5, 6),
                sex="male",
                institution_id=nda["institution_id"],
                education_level="UG100",
            )
        ).learner
    sign_in(client, sto, HTTP_HOST=HOST)
    roll = client.get(f"/security-training/intakes/{intake}", HTTP_HOST=HOST).content.decode()
    assert f"/forms/security-trainee?target={intake}" in roll
    r = client.post(
        "/forms/security-trainee",
        {"target": intake, "learner_id": cadet.global_learner_id, "rank_code": "IGP"},
        HTTP_HOST=HOST,
    )
    assert r.status_code == 422 and b"Unknown rank" in r.content, errs(r)  # the service's own check, shown on the form
    r = client.post(
        "/forms/security-trainee",
        {"target": intake, "learner_id": cadet.global_learner_id, "rank_code": "OCDT"},
        HTTP_HOST=HOST,
    )
    assert r.status_code == 200 and b"Trainee added" in r.content, errs(r)
    roll = client.get(f"/security-training/intakes/{intake}", HTTP_HOST=HOST).content.decode()
    record = re.search(r"/forms/security-outcome\?target=([0-9a-f-]{36})", roll).group(1)
    r = client.post("/forms/security-outcome", {"target": record, "outcome": "relegated"}, HTTP_HOST=HOST)
    assert r.status_code == 422 and b"reason" in r.content.lower(), errs(r)
    r = client.post(
        "/forms/security-outcome",
        {"target": record, "outcome": "commissioned", "result": "Second Class Upper"},
        HTTP_HOST=HOST,
    )
    assert r.status_code == 200 and b"Outcome recorded: commissioned" in r.content, errs(r)
    with context.use(officer):
        assert sti.learner_courses(cadet.id)[0]["outcome"] == "commissioned"


def test_hr_workflow_forms_posting_leave_and_relations(world: Any, hr: Any, client: Any) -> None:  # noqa: F811
    from syntegra.core import context
    from syntegra.hr.models import EmployeeRelationsCase, LeaveRequest, StaffPosting
    from tests.integration.test_hrms import next_monday

    officer, og = make_user(world, "HR", world.state_scope)
    sign_in(client, officer)
    r = client.post(
        "/forms/hr-posting",
        {
            "staff_id": str(hr.staff.id),
            "to_position_id": str(hr.p2.id),
            "posting_kind": "transfer",
            "effective_on": next_monday().isoformat(),
            "reason": "Staffing need in Umuahia",
        },
    )
    assert r.status_code == 200 and b"submitted for approval" in r.content, errs(r)
    with context.use(user_ctx(officer.id, og)):
        posting = StaffPosting.objects.get(staff_id=hr.staff.id, status="submitted")
    client.post("/sign-out")
    second, _ = make_user(world, "HR", world.state_scope)
    sign_in(client, second)  # a different officer approves
    r = client.post("/forms/hr-posting-decision", {"target": str(posting.id), "action": "approve"})
    assert r.status_code == 200 and f"Posting {posting.order_number} is now approved".encode() in r.content, errs(r)
    r = client.post(
        "/forms/hr-relations",
        {"staff_id": str(hr.staff.id), "case_kind": "query", "summary": "Absent without leave on 3 May"},
    )
    assert r.status_code == 200 and b"Case opened" in r.content, errs(r)
    with context.use(user_ctx(officer.id, og)):
        assert EmployeeRelationsCase.objects.filter(staff_id=hr.staff.id).exists()
    client.post("/sign-out")

    sign_in(client, hr.user)  # the teacher: own leave only
    page = client.get("/forms/hr-leave").content.decode()
    leave_type = re.search(
        r'<select name="leave_type"[^>]*>\s*<option value="">[^<]*</option>\s*<option value="([^"]+)"', page
    )
    assert leave_type, page[-2000:]
    start = next_monday() + dt_days(14)
    r = client.post(
        "/forms/hr-leave",
        {
            "staff_id": str(hr.staff.id),
            "leave_type": leave_type.group(1),
            "starts_on": start.isoformat(),
            "ends_on": (start - dt_days(3)).isoformat(),
        },
    )
    assert r.status_code == 422 and b"Leave ends before it starts" in r.content, errs(r)
    r = client.post(
        "/forms/hr-leave",
        {
            "staff_id": str(hr.staff.id),
            "leave_type": leave_type.group(1),
            "starts_on": start.isoformat(),
            "ends_on": (start + dt_days(4)).isoformat(),
        },
    )
    assert r.status_code == 200 and b"Leave requested" in r.content, errs(r)
    client.post("/sign-out")
    head, hg = make_user(world, "HEAD", world.institution.scope_node_id)
    sign_in(client, head)
    with context.use(user_ctx(head.id, hg)):
        lr = LeaveRequest.objects.get(staff_id=hr.staff.id, status="requested")
    assert f'value="{lr.id}"' in client.get("/forms/hr-leave-decision").content.decode()
    r = client.post("/forms/hr-leave-decision", {"target": str(lr.id), "approve": "true"})
    assert r.status_code == 200 and b"Leave approved" in r.content, errs(r)


def dt_days(n: int) -> Any:
    import datetime as dt

    return dt.timedelta(days=n)
