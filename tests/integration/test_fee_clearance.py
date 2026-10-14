"""CR-001 fee-clearance due diligence across the ecosystem (private creditor → public admitting school)."""

import datetime as dt
import uuid

import pytest

from syntegra.core.errors import Forbidden, HardValidation

pytestmark = pytest.mark.django_db(databases="__all__")
NAIRA = 100


@pytest.fixture
def private_school(world, as_user):  # type: ignore[no-untyped-def]
    from syntegra.core.tenancy import SEED_STATE_TENANT
    from syntegra.institutions import services as inst

    with as_user("STA", world.state_scope):
        return inst.register(
            inst.RegisterInstitution(
                name="Royal Crest Private Academy",
                category="secondary",
                ownership="private",
                lga_scope_id=world.lga_scope,
                address={"town": "Aba"},
                levels=["jss_1", "sss_3"],
                location=(7.40, 5.12),
                operating_tenant_id=SEED_STATE_TENANT,
            )
        )


def enrol_at(world, as_user, school, given, level="sss_1"):  # type: ignore[no-untyped-def]
    from syntegra.learners import services as learners

    with as_user("HEAD", school.scope_node_id):
        return learners.register(
            learners.RegisterLearner(
                given=given,
                family="Okonkwo",
                date_of_birth=dt.date(2010, 2, 3),
                sex="male",
                institution_id=school.id,
                education_level=level,
                start_on=dt.date(2025, 9, 8),
            )
        ).learner


def owe(world, as_user, school, learner, amount_naira, kind="tuition_fees"):  # type: ignore[no-untyped-def]
    from syntegra.clearance import services as fcl

    with as_user("FINO", school.scope_node_id):
        return fcl.publish(
            learner_id=learner.id,
            creditor_institution_id=school.id,
            kind=kind,
            amount_minor=amount_naira * NAIRA,
            oldest_due_on=dt.date(2026, 5, 1),
            evidence=[{"invoice": f"INV-{uuid.uuid4().hex[:6]}"}],
            periods=["2025/26-T3"],
        )


def test_transfer_with_debt_needs_a_human_decision_never_a_refusal(world, as_user, private_school) -> None:  # type: ignore[no-untyped-def]
    from syntegra.clearance.models import ClearanceCheck, ClearanceDecision
    from syntegra.clearance.services import AdmissionDeferred, ClearanceDecisionRequired, DecisionInput
    from syntegra.learners import services as learners
    from syntegra.learners.models import Enrolment

    lrn = enrol_at(world, as_user, private_school, "Chukwudi")
    owe(world, as_user, private_school, lrn, 450_000)
    with as_user("HEAD", world.institution.scope_node_id):
        with pytest.raises(ClearanceDecisionRequired) as e:
            learners.transfer(lrn.id, world.institution.id, education_level="sss_1")
        body = e.value.problem()
        assert body["status"] == 409 and body["total_outstanding_minor"] == 450_000 * NAIRA
        assert body["obligations"][0]["creditor"] == "Royal Crest Private Academy"
        assert "refuse" not in body["allowed_decisions"]
        # nothing moved: the learner still attends the old school (P9)
        assert Enrolment.objects.get(learner_id=lrn.id, status="active").institution_id == private_school.id
        check_id = uuid.UUID(body["clearance_check_id"])
        with pytest.raises(AdmissionDeferred):
            learners.transfer(
                lrn.id,
                world.institution.id,
                education_level="sss_1",
                clearance=DecisionInput(
                    decision="defer_pending_settlement",
                    reason="Family to settle with the bursar first",
                    check_id=check_id,
                ),
            )
        with pytest.raises(HardValidation, match="Decision incomplete"):
            learners.transfer(
                lrn.id,
                world.institution.id,
                education_level="sss_1",
                clearance=DecisionInput(
                    decision="admit_with_payment_plan", reason="Instalments agreed with Royal Crest"
                ),
            )
        t = learners.transfer(
            lrn.id,
            world.institution.id,
            education_level="sss_1",
            clearance=DecisionInput(
                decision="admit_with_payment_plan",
                reason="Instalments agreed with Royal Crest",
                payment_plan_ref="RC-PP-0042",
            ),
        )
        assert t.status == "completed"
    checks = list(ClearanceCheck.unscoped.filter(learner_id=lrn.id).order_by("checked_at"))
    assert [c.result for c in checks] == ["outstanding"] * 3
    decisions = {d.check_id: d.decision for d in ClearanceDecision.unscoped.filter(check_id__in=[c.id for c in checks])}
    assert sorted(decisions.values()) == ["admit_with_payment_plan", "defer_pending_settlement"]


def test_public_basic_education_always_admits(world, as_user, private_school) -> None:  # type: ignore[no-untyped-def]
    from syntegra.clearance.models import ClearanceCheck, ClearanceDecision, LearnerObligation
    from syntegra.learners import services as learners

    lrn = enrol_at(world, as_user, private_school, "Adaeze", level="jss_2")
    ob = owe(world, as_user, private_school, lrn, 120_000)
    with as_user("HEAD", world.institution.scope_node_id):
        t = learners.transfer(lrn.id, world.institution.id, education_level="jss_2")  # no decision needed
    assert t.status == "completed"
    chk = ClearanceCheck.unscoped.get(learner_id=lrn.id)
    dec = ClearanceDecision.unscoped.get(check_id=chk.id)
    assert chk.result == "protected" and dec.decision == "admit_protected"
    assert dec.protected_reason == "public_basic_education"
    assert LearnerObligation.unscoped.get(pk=ob.id).status == "outstanding"  # the creditor keeps its claim


def test_disputes_are_shown_and_resolved_by_the_lga(world, as_user, private_school) -> None:  # type: ignore[no-untyped-def]
    from syntegra.clearance import services as fcl
    from syntegra.clearance.models import LearnerObligation
    from syntegra.learners import services as learners

    lrn = enrol_at(world, as_user, private_school, "Ifeanyi")
    ob = owe(world, as_user, private_school, lrn, 300_000)
    with as_user("HEAD", world.institution2.scope_node_id), pytest.raises(Forbidden):  # never checked this learner
        fcl.raise_dispute(ob.id, party="admitting_institution", grounds="other", statement="Fishing for information")
    with as_user("HEAD", world.institution.scope_node_id):
        fcl.check(lrn.id, world.institution.id, purpose="transfer", education_level="sss_1")
        d = fcl.raise_dispute(
            ob.id,
            party="admitting_institution",
            grounds="already_paid",
            statement="Family holds bank receipts for term 3 fees",
        )
        t = learners.transfer(lrn.id, world.institution.id, education_level="sss_1")  # disputed only → no decision
    assert t.status == "completed"
    with as_user("LGA", world.lga2_scope), pytest.raises(Forbidden):
        fcl.resolve_dispute(d.id, "rejected", reason="Wrong LGA trying to resolve")
    with as_user("LGA", world.lga_scope):
        fcl.resolve_dispute(
            d.id,
            "partly_upheld",
            resolved_amount_minor=100_000 * NAIRA,
            reason="Receipts cover two thirds of the claim",
        )
    ob = LearnerObligation.unscoped.get(pk=ob.id)
    assert ob.status == "outstanding" and ob.amount_outstanding_minor == 100_000 * NAIRA


def test_debt_hopping_is_flagged_and_family_sees_every_check(world, as_user, private_school) -> None:  # type: ignore[no-untyped-def]
    from syntegra.clearance import services as fcl
    from syntegra.core.tenancy import SEED_STATE_TENANT
    from syntegra.institutions import services as inst
    from syntegra.learners.models import Enrolment

    with as_user("STA", world.state_scope):
        other = inst.register(
            inst.RegisterInstitution(
                name="Bright Future College",
                category="secondary",
                ownership="private",
                lga_scope_id=world.lga2_scope,
                address={"town": "Umuahia"},
                levels=["sss_1"],
                operating_tenant_id=SEED_STATE_TENANT,
            )
        )
    lrn = enrol_at(world, as_user, private_school, "Obinna")
    owe(world, as_user, private_school, lrn, 200_000)
    owe(world, as_user, other, lrn, 150_000, kind="boarding")
    Enrolment.unscoped.filter(learner_id=lrn.id).update(status="withdrawn", end_on=dt.date(2026, 7, 20))
    with as_user("HEAD", world.institution.scope_node_id):
        chk = fcl.check(lrn.id, world.institution.id, purpose="admission", education_level="sss_1")
    assert chk.result == "outstanding" and chk.total_outstanding_minor == 350_000 * NAIRA
    assert chk.pattern_flags[0]["flag"] == "repeat_unsettled_transfers"
    with as_user("STA", world.state_scope):
        seen = fcl.checks_about(lrn.id)
    assert seen[0]["by_institution"] == world.institution.name and seen[0]["purpose"] == "admission"


def test_readmission_of_known_learner_runs_the_check(world, as_user, private_school) -> None:  # type: ignore[no-untyped-def]
    from syntegra.clearance.services import ClearanceDecisionRequired
    from syntegra.learners import services as learners
    from syntegra.learners.models import Enrolment

    lrn = enrol_at(world, as_user, private_school, "Emeka")
    owe(world, as_user, private_school, lrn, 90_000)
    Enrolment.unscoped.filter(learner_id=lrn.id).update(status="withdrawn", end_on=dt.date(2026, 7, 20))
    data = learners.RegisterLearner(
        given="Emeka",
        family="Okonkwo",
        date_of_birth=dt.date(2010, 2, 3),
        sex="male",
        institution_id=world.institution.id,
        education_level="sss_1",
    )
    with as_user("HEAD", world.institution.scope_node_id):
        with pytest.raises(ClearanceDecisionRequired):
            learners.register(data)
        r = learners.register(
            data, clearance=learners.DecisionInput(decision="admit", reason="Head's discretion: scholarship pending")
        )
    assert r.outcome == "linked" and r.learner.id == lrn.id


def test_ledger_publication_settlement_expiry_and_sdaf_exclusion(world, as_user, private_school) -> None:  # type: ignore[no-untyped-def]
    from syntegra.clearance import services as fcl
    from syntegra.clearance.models import LearnerObligation
    from syntegra.core import context
    from syntegra.finance import obligations
    from syntegra.finance.models import Account, ChargeType, Invoice, InvoiceLine
    from tests.conftest import system_ctx

    lrn = enrol_at(world, as_user, private_school, "Kelechi")
    node = private_school.scope_node_id
    with context.use(system_ctx()):
        acc = Account(
            scope_node_id=node,
            account_kind="learner",
            code=f"L-{uuid.uuid4().hex[:6]}",
            name="Kelechi",
            holder_kind="learner",
            holder_id=lrn.id,
            currency="NGN",
            status="active",
        )
        acc.save(using="ops")
        types = {}
        for code in ("TUITION", "SDAF_LEVY", "BUS"):
            ct = ChargeType(
                scope_node_id=node,
                code=f"{code}_{uuid.uuid4().hex[:4]}",
                name=code,
                income_account_id=acc.id,
                status="active",
            )
            ct.save(using="ops")
            types[code] = ct
        inv = Invoice(
            scope_node_id=node,
            invoice_number=f"INV-{uuid.uuid4().hex[:8]}",
            account_id=acc.id,
            learner_id=lrn.id,
            payer_kind="guardian",
            payer_id=uuid.uuid4(),
            period_label="2025/26-T3",
            issued_on=dt.date(2026, 4, 1),
            due_on=dt.date(2026, 5, 1),
            total_minor=500_000 * NAIRA,
            balance_minor=500_000 * NAIRA,
            currency="NGN",
            content_hash=b"\x01" * 32,
            status="overdue",
        )
        inv.save(using="ops")
        for i, (code, net) in enumerate([("TUITION", 400_000), ("SDAF_LEVY", 50_000), ("BUS", 50_000)], start=1):
            InvoiceLine(
                invoice_id=inv.id,
                line_no=i,
                charge_type_id=types[code].id,
                description=code,
                gross_minor=net * NAIRA,
                discount_minor=0,
                funded_minor=0,
                net_minor=net * NAIRA,
                currency="NGN",
            ).save(using="ops")
    with as_user("FINO", node):
        r = obligations.publish_from_ledger(private_school.id, as_of=dt.date(2026, 10, 14))
    obs = {o.obligation_kind: o for o in LearnerObligation.unscoped.filter(learner_id=lrn.id, status="outstanding")}
    assert r["published"] == 2 and set(obs) == {"tuition_fees", "transport"}  # never SDAF
    assert obs["tuition_fees"].amount_outstanding_minor == 400_000 * NAIRA
    assert obs["tuition_fees"].evidence[0]["invoice"] == inv.invoice_number
    Invoice.unscoped.filter(pk=inv.id).update(balance_minor=0, status="paid")
    with as_user("FINO", node):
        r = obligations.publish_from_ledger(private_school.id, as_of=dt.date(2026, 10, 14))
    assert r["settled"] == 2
    assert not LearnerObligation.unscoped.filter(learner_id=lrn.id, status="outstanding").exists()
    stale = owe(world, as_user, private_school, lrn, 10_000, kind="library")
    LearnerObligation.unscoped.filter(pk=stale.id).update(reconfirm_by=dt.date(2026, 1, 1))
    with as_user("STA", world.state_scope):
        assert fcl.expire_stale() >= 1
    assert LearnerObligation.unscoped.get(pk=stale.id).status == "expired"


def test_clearance_over_the_api(world, as_user, private_school, api) -> None:  # type: ignore[no-untyped-def]
    lrn = enrol_at(world, as_user, private_school, "Nnamdi")
    owe(world, as_user, private_school, lrn, 60_000)
    head = api("HEAD", world.institution.scope_node_id)
    r = head(
        "post",
        f"/api/v1/learners/{lrn.id}/transfer",
        {"to_institution_id": str(world.institution.id), "education_level": "sss_1"},
    )
    assert r.status_code == 409 and r.json()["code"] == "FCL-DECISION-REQUIRED"
    check_id = r.json()["clearance_check_id"]
    r = head(
        "post",
        f"/api/v1/learners/{lrn.id}/transfer",
        {"to_institution_id": str(world.institution.id), "education_level": "sss_1"},
        **{
            "X-Syntegra-Clearance-Decision": "admit",
            "X-Syntegra-Clearance-Reason": "Debt to be recovered by creditor",
            "X-Syntegra-Clearance-Check": check_id,
        },
    )
    assert r.status_code == 201, r.content
    assert head("get", f"/api/v1/learners/{lrn.id}/clearance-checks").json()["data"][0]["decision"] == "admit"
