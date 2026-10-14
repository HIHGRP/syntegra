"""Fee-clearance API (CR-001). The check informs a human decision; there is no refusal endpoint by design."""

from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.clearance import services
from syntegra.clearance.models import LearnerObligation
from syntegra.core.api import views as v


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


class Disputes(APIView):
    required_permission = "clearance:dispute"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = DisputeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.raise_dispute(pk, **s.validated_data)), status=201)


class DisputeResolution(APIView):
    required_permission = "clearance:resolve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        d = request.data
        amt = d.get("resolved_amount_minor")
        return Response(
            v.row(
                services.resolve_dispute(
                    pk,
                    str(d["resolution"]),
                    reason=str(d.get("reason", "")),
                    resolved_amount_minor=int(amt) if amt else None,
                )
            )
        )


class LearnerChecks(APIView):
    required_permission = "learner:view"

    def get(self, request: Request, learner_id: uuid.UUID) -> Response:
        return Response({"data": v.jsonable(services.checks_about(learner_id))})
