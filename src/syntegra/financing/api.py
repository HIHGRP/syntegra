from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.financing import services


class CensusSerializer(serializers.Serializer):  # type: ignore[type-arg]
    billing_period_id = serializers.UUIDField()


class TakeCensus(APIView):
    required_permission = "census:take"

    def post(self, request: Request, institution_id: uuid.UUID) -> Response:
        s = CensusSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        snap = services.take_census(institution_id, s.validated_data["billing_period_id"])
        return Response(v.row(snap), status=201)


class FreezeCensus(APIView):
    required_permission = "census:confirm"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.row(services.confirm_and_freeze(pk)))


class IssueDemand(APIView):
    required_permission = "financing:demand"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response({"data": [v.row(d) for d in services.issue_demand(pk)]}, status=201)
