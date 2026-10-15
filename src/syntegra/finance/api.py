"""Budgets, commitments, virements and imprest API (CR-006, FR-ACC-01 – FR-ACC-06).

Amounts are in kobo (``*_minor``). Services enforce permissions, scope and the four-eyes rules (the preparer of a
budget, the requester of a virement and the requester of an imprest cannot approve their own).
"""

from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core import catalog
from syntegra.core.api import views as v
from syntegra.finance import budgets


def _enum(name: str, **kw: object) -> serializers.ChoiceField:
    return serializers.ChoiceField(catalog.enum_values(name), **kw)  # type: ignore[arg-type]


class CostCentreSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    code = serializers.RegexField(r"^[A-Za-z0-9][A-Za-z0-9-]{0,19}$")
    name = serializers.CharField(max_length=200)
    kind = _enum("cost_centre_kind")
    holder_staff_id = serializers.UUIDField(required=False, allow_null=True)
    parent_id = serializers.UUIDField(required=False, allow_null=True)


class LineSerializer(serializers.Serializer):  # type: ignore[type-arg]
    cost_centre_id = serializers.UUIDField()
    economic_code = serializers.RegexField(r"^\d{4,12}$")
    amount_minor = serializers.IntegerField(min_value=1)
    funding_source_kind = _enum("budget_funding_kind", default="subvention")
    description = serializers.CharField(max_length=300, required=False, allow_null=True, allow_blank=True)
    account_name = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)


class BudgetSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    fiscal_year = serializers.IntegerField(min_value=2000, max_value=2100)
    lines = LineSerializer(many=True, allow_empty=False)
    assumptions = serializers.DictField(required=False)


class CommitmentSerializer(serializers.Serializer):  # type: ignore[type-arg]
    budget_line_id = serializers.UUIDField()
    amount_minor = serializers.IntegerField(min_value=1)
    source_kind = _enum("commitment_source", default="manual")
    source_id = serializers.UUIDField(required=False, allow_null=True)
    description = serializers.CharField(max_length=300)


class SpendSerializer(serializers.Serializer):  # type: ignore[type-arg]
    amount_minor = serializers.IntegerField(min_value=0)
    final = serializers.BooleanField(default=False)


class VirementSerializer(serializers.Serializer):  # type: ignore[type-arg]
    from_line_id = serializers.UUIDField()
    to_line_id = serializers.UUIDField()
    amount_minor = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(min_length=10, max_length=1000)


class DecisionSerializer(serializers.Serializer):  # type: ignore[type-arg]
    approve = serializers.BooleanField()


class ImprestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    holder_staff_id = serializers.UUIDField()
    budget_line_id = serializers.UUIDField()
    purpose = serializers.CharField(min_length=5, max_length=500)
    amount_minor = serializers.IntegerField(min_value=1)
    retire_by = serializers.DateField()


class ReceiptSerializer(serializers.Serializer):  # type: ignore[type-arg]
    reference = serializers.CharField(max_length=80)
    amount_minor = serializers.IntegerField(min_value=0)
    payee = serializers.CharField(max_length=200, required=False, allow_blank=True)
    date = serializers.DateField(required=False, allow_null=True)


class RetireSerializer(serializers.Serializer):  # type: ignore[type-arg]
    receipts = ReceiptSerializer(many=True, allow_empty=False)
    amount_minor = serializers.IntegerField(min_value=0)
    refund_minor = serializers.IntegerField(min_value=0, default=0)


class CostCentres(APIView):
    required_permission = "budget:prepare"

    def post(self, request: Request) -> Response:
        s = CostCentreSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        cc = budgets.create_cost_centre(d.pop("institution_id"), d.pop("code"), d.pop("name"), d.pop("kind"), **d)
        return Response(v.row(cc), status=201)


class Budgets(APIView):
    required_permission = {"GET": "budget:view", "POST": "budget:prepare"}

    def get(self, request: Request) -> Response:
        """FIN-02 budget execution (``?institution_id=`` and ``?fiscal_year=`` optional)."""
        year = request.query_params.get("fiscal_year")
        data = budgets.execution(
            institution_id=v.uuid_param(request, "institution_id"),
            fiscal_year=int(year) if year and year.isdigit() else None,
        )
        return Response(v.jsonable(data))

    def post(self, request: Request) -> Response:
        s = BudgetSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        lines = [budgets.LineInput(**{k: x for k, x in ln.items() if x not in (None, "")}) for ln in d["lines"]]
        b = budgets.prepare_budget(d["institution_id"], d["fiscal_year"], lines, assumptions=d.get("assumptions"))
        return Response(v.row(b), status=201)


class BudgetApproval(APIView):
    required_permission = "budget:approve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.row(budgets.approve_budget(pk)))


class Commitments(APIView):
    required_permission = "budget:commit"

    def post(self, request: Request) -> Response:
        s = CommitmentSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        c = budgets.commit(
            d["budget_line_id"],
            d["amount_minor"],
            source_kind=d["source_kind"],
            source_id=d.get("source_id") or uuid.uuid4(),
            description=d["description"],
        )
        return Response(v.row(c), status=201)


class CommitmentSpend(APIView):
    required_permission = "budget:commit"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = SpendSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(budgets.spend(pk, s.validated_data["amount_minor"], final=s.validated_data["final"])))


class CommitmentRelease(APIView):
    required_permission = "budget:commit"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.row(budgets.release(pk)))


class Virements(APIView):
    required_permission = "budget:virement"

    def post(self, request: Request) -> Response:
        s = VirementSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(budgets.request_virement(**s.validated_data)), status=201)


class VirementDecision(APIView):
    required_permission = "budget:approve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = DecisionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(budgets.decide_virement(pk, s.validated_data["approve"])))


class ImprestList(APIView):
    required_permission = {"GET": "budget:view", "POST": "imprest:request"}

    def get(self, request: Request) -> Response:
        """ACC-01 imprest register (``?status=`` optional)."""
        status = request.query_params.get("status")
        if status and status not in catalog.enum_values("imprest_status"):
            raise serializers.ValidationError({"status": "unknown imprest status"})
        return Response({"data": v.jsonable(budgets.imprest_register(status=status or None))})

    def post(self, request: Request) -> Response:
        s = ImprestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        imp = budgets.request_imprest(
            d["holder_staff_id"], d["budget_line_id"], d["purpose"], d["amount_minor"], d["retire_by"]
        )
        return Response(v.row(imp), status=201)


class ImprestApproval(APIView):
    required_permission = "imprest:approve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = DecisionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(budgets.approve_imprest(pk, s.validated_data["approve"])))


class ImprestRetirement(APIView):
    required_permission = "imprest:retire"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = RetireSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        receipts = [v.jsonable(dict(r)) for r in d["receipts"]]
        return Response(v.row(budgets.retire_imprest(pk, receipts, d["amount_minor"], d["refund_minor"])))
