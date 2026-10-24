"""Funding and loans API (CR-006, FR-FND-01 – FR-FND-08).

Programmes, applications for an institution, a member of staff or a learner, review and human decision by different
people, agreements with repayment schedules, disbursements and repayments. Amounts are in kobo (``*_minor``).
"""

from __future__ import annotations

import uuid
from typing import Any

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core import catalog
from syntegra.core.api import views as v
from syntegra.funding import services


def _enum(name: str, **kw: object) -> serializers.ChoiceField:
    return serializers.ChoiceField(catalog.enum_values(name), **kw)  # type: ignore[arg-type]


class ApplicationSerializer(serializers.Serializer):  # type: ignore[type-arg]
    programme_id = serializers.UUIDField()
    applicant_kind = _enum("funding_beneficiary")
    applicant_id = serializers.UUIDField()
    institution_id = serializers.UUIDField()
    amount_minor = serializers.IntegerField(min_value=1)
    purpose_detail = serializers.CharField(min_length=10, max_length=2000)
    capital_plan_item_id = serializers.UUIDField(required=False, allow_null=True)


class RecommendSerializer(serializers.Serializer):  # type: ignore[type-arg]
    recommendation = serializers.CharField(min_length=10, max_length=2000)


class DecideSerializer(serializers.Serializer):  # type: ignore[type-arg]
    approve = serializers.BooleanField()
    reason = serializers.CharField(min_length=10, max_length=2000)
    amount_approved_minor = serializers.IntegerField(min_value=1, required=False, allow_null=True)


class AgreementSerializer(serializers.Serializer):  # type: ignore[type-arg]
    signed_on = serializers.DateField(required=False, allow_null=True)
    first_repayment_on = serializers.DateField(required=False, allow_null=True)
    interest_rate = serializers.DecimalField(
        max_digits=6, decimal_places=3, min_value=0, required=False, allow_null=True
    )
    tenor_months = serializers.IntegerField(min_value=1, max_value=360, required=False, allow_null=True)
    gross_pay_minor = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    other_deductions_minor = serializers.IntegerField(min_value=0, default=0)


class DisbursementSerializer(serializers.Serializer):  # type: ignore[type-arg]
    amount_minor = serializers.IntegerField(min_value=1)
    payee_kind = _enum("disbursement_payee")
    purpose = serializers.CharField(max_length=300)
    reference = serializers.CharField(max_length=80)
    payee_reference = serializers.CharField(max_length=120, required=False, allow_null=True, allow_blank=True)
    budget_line_id = serializers.UUIDField(required=False, allow_null=True)
    disbursed_on = serializers.DateField(required=False, allow_null=True)


class RepaymentSerializer(serializers.Serializer):  # type: ignore[type-arg]
    amount_minor = serializers.IntegerField(min_value=1)
    method = _enum("repayment_method")
    reference = serializers.CharField(max_length=80)
    received_on = serializers.DateField(required=False, allow_null=True)


def _clean(d: dict[str, Any]) -> dict[str, Any]:
    return {k: x for k, x in d.items() if x not in (None, "")}


class Programmes(APIView):
    required_permission = "funding:view"

    def get(self, request: Request) -> Response:
        kind = request.query_params.get("beneficiary_kind")
        if kind and kind not in catalog.enum_values("funding_beneficiary"):
            raise serializers.ValidationError({"beneficiary_kind": "institution, staff or learner"})
        return Response({"data": v.jsonable(services.programmes(kind or None))})


class Overview(APIView):
    required_permission = "funding:view"

    def get(self, request: Request) -> Response:
        """FND-01: programmes, applications by status and agreements with balances and arrears."""
        return Response(v.jsonable(services.overview()))


class Applications(APIView):
    required_permission = None  # funding:apply, or funding:apply_own for a member of staff's own — in the service
    level_permissions = ("funding:apply", "funding:apply_own")

    def post(self, request: Request) -> Response:
        s = ApplicationSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        app = services.apply(d.pop("programme_id"), **_clean(d))
        return Response(v.row(app), status=201)


class Recommendation(APIView):
    required_permission = "funding:review"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = RecommendSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.recommend(pk, s.validated_data["recommendation"])))


class Decision(APIView):
    required_permission = "funding:decide"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = DecideSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        app = services.decide(pk, d["approve"], d["reason"], amount_approved_minor=d.get("amount_approved_minor"))
        return Response(v.row(app))


class Agreements(APIView):
    required_permission = "funding:decide"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        """Sign the agreement for approved application ``pk``; the repayment schedule is generated."""
        s = AgreementSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.sign_agreement(pk, **_clean(dict(s.validated_data)))), status=201)


class Agreement(APIView):
    required_permission = None  # funding:view, or the beneficiary's own — in the service

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.jsonable(services.agreement(pk)))


class Disbursements(APIView):
    required_permission = "funding:disburse"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = DisbursementSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = _clean(dict(s.validated_data))
        return Response(v.row(services.disburse(pk, d.pop("amount_minor"), **d)), status=201)


class Repayments(APIView):
    required_permission = "funding:collect"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = RepaymentSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = _clean(dict(s.validated_data))
        return Response(v.row(services.record_repayment(pk, d.pop("amount_minor"), **d)), status=201)


class Mine(APIView):
    required_permission = None  # any signed-in member of staff sees their own agreements

    def get(self, request: Request) -> Response:
        return Response({"data": v.jsonable(services.my_agreements())})
