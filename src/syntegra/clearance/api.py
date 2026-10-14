"""Fee-clearance API (CR-001). The check informs a human decision; there is no refusal endpoint by design."""

from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from syntegra.clearance import federation, services
from syntegra.clearance.models import LearnerObligation
from syntegra.core.api import views as v
from syntegra.core.api.permissions import Public
from syntegra.platform.models import ExchangePeer


class CheckSerializer(serializers.Serializer):  # type: ignore[type-arg]
    learner_id = serializers.UUIDField()
    institution_id = serializers.UUIDField()
    purpose = serializers.ChoiceField(["admission", "transfer", "re_enrolment", "enquiry_with_consent"])
    education_level = serializers.CharField(max_length=32)
    basis = serializers.ChoiceField(["admission_due_diligence", "guardian_consent"], default="admission_due_diligence")


class DecisionSerializer(serializers.Serializer):  # type: ignore[type-arg]
    decision = serializers.ChoiceField(
        ["admit", "admit_with_payment_plan", "defer_pending_settlement", "admit_protected"]
    )
    reason = serializers.CharField(min_length=10)
    protected_reason = serializers.CharField(required=False, allow_null=True)
    payment_plan_ref = serializers.CharField(required=False, allow_null=True)


class DisputeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    party = serializers.ChoiceField(["guardian", "learner", "admitting_institution", "creditor"])
    grounds = serializers.ChoiceField(
        ["already_paid", "amount_wrong", "not_liable", "waiver_granted", "statute_barred", "protected_learner", "other"]
    )
    statement = serializers.CharField(min_length=10)


class ResolutionSerializer(serializers.Serializer):  # type: ignore[type-arg]
    resolution = serializers.ChoiceField(["upheld", "partly_upheld", "rejected", "withdrawn"])
    reason = serializers.CharField(min_length=10)
    resolved_amount_minor = serializers.IntegerField(min_value=1, required=False, allow_null=True)


class ObligationSerializer(serializers.Serializer):  # type: ignore[type-arg]
    learner_id = serializers.UUIDField()
    creditor_institution_id = serializers.UUIDField()
    kind = serializers.ChoiceField(
        [
            "tuition_fees",
            "boarding",
            "examination_fees",
            "transport",
            "meals",
            "books_and_materials",
            "uniform",
            "development_levy",
            "damaged_property",
            "library",
            "other_dues",
        ]
    )
    amount_minor = serializers.IntegerField(min_value=0)
    oldest_due_on = serializers.DateField()
    evidence = serializers.ListField(child=serializers.DictField(), min_length=1)
    periods = serializers.ListField(child=serializers.CharField(max_length=20), required=False)
    payer_kind = serializers.ChoiceField(
        ["learner", "family", "guardian", "sponsor", "funder", "government", "employer", "institution"],
        default="guardian",
    )
    source = serializers.ChoiceField(["ledger", "manual_with_evidence"], default="manual_with_evidence")  # type: ignore[assignment]  # DRF field named "source"


def decision_from_headers(request: Request) -> services.DecisionInput | None:
    """``X-Syntegra-Clearance-Decision`` (+ ``-Reason``, ``-Check``, ``-Protected``, ``-Plan``) on admission calls."""
    h = request.headers
    if not h.get("X-Syntegra-Clearance-Decision"):
        return None
    check = h.get("X-Syntegra-Clearance-Check")
    return services.DecisionInput(
        decision=h["X-Syntegra-Clearance-Decision"],
        reason=h.get("X-Syntegra-Clearance-Reason", ""),
        check_id=uuid.UUID(check) if check else None,
        protected_reason=h.get("X-Syntegra-Clearance-Protected"),
        payment_plan_ref=h.get("X-Syntegra-Clearance-Plan"),
    )


class Checks(APIView):
    required_permission = "clearance:check"

    def post(self, request: Request) -> Response:
        s = CheckSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        chk = services.check(
            d["learner_id"],
            d["institution_id"],
            purpose=d["purpose"],
            education_level=d["education_level"],
            basis=d["basis"],
        )
        return Response(v.row(chk), status=201)


class CheckDecision(APIView):
    required_permission = "admission:decide"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = DecisionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.decide(pk, services.DecisionInput(**s.validated_data))), status=201)


class Obligations(APIView):
    required_permission = "clearance:publish"

    def get(self, request: Request) -> Response:
        qs = LearnerObligation.objects.in_scope().order_by("-published_at")
        if st := request.query_params.get("status"):
            qs = qs.filter(status=st)
        return Response({"data": [v.row(o) for o in qs[:500]]})

    def post(self, request: Request) -> Response:
        """Publish (or settle, with amount 0) an obligation — manual claims need an evidence document."""
        s = ObligationSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        ob = services.publish(**s.validated_data)
        return Response(v.row(ob) if ob else {"settled": True}, status=201)


class Disputes(APIView):
    required_permission = "clearance:dispute"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = DisputeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.raise_dispute(pk, **s.validated_data)), status=201)


class DisputeResolution(APIView):
    required_permission = "clearance:resolve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = ResolutionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        return Response(
            v.row(
                services.resolve_dispute(
                    pk, d["resolution"], reason=d["reason"], resolved_amount_minor=d.get("resolved_amount_minor")
                )
            )
        )


class LearnerChecks(APIView):
    required_permission = "learner:view"

    def get(self, request: Request, learner_id: uuid.UUID) -> Response:
        return Response({"data": v.jsonable(services.checks_about(learner_id))})


class ExchangeClearance(APIView):
    """National clearance network (CR-002): a signed query from another state's registry, answered and signed.

    Not user-authenticated: the message itself is authenticated (ES256 against the national directory), expiring
    and single-use. Refusals are signed answers too, so the caller can always tell why.
    """

    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes = [Public]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "exchange"

    def post(self, request: Request) -> Response:
        token = request.data.get("jws") if isinstance(request.data, dict) else None
        if not isinstance(token, str) or token.count(".") != 2 or len(token) > 16384:
            raise federation.ExchangeRefused('body must be {"jws": <compact JWS>}')
        return Response({"jws": federation.answer(token)}, headers={"Cache-Control": "no-store"})


class ExchangeKeys(APIView):
    """Verification keys of the state registries answered by this platform (for remote peers' directories)."""

    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes = [Public]

    def get(self, request: Request) -> Response:
        keys = []
        for p in ExchangePeer.objects.using("platform").filter(hosting="co_hosted", status="active"):
            if p.public_jwk:
                keys.append({**p.public_jwk, "kid": p.kid, "use": "sig", "state_code": p.state_code})
        return Response({"keys": keys}, headers={"Cache-Control": "public, max-age=3600"})
