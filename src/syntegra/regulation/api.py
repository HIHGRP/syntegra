"""Education watchdogs API (CR-005)."""

from __future__ import annotations

import uuid
from typing import Any

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.core.api.permissions import Public
from syntegra.regulation import services


class LinkSerializer(serializers.Serializer):  # type: ignore[type-arg]
    body_code = serializers.CharField(max_length=16)
    relationship = serializers.ChoiceField(
        [
            "supervision",
            "accreditation",
            "licensing",
            "curriculum",
            "examination",
            "admission",
            "teacher_registration",
            "professional_regulation",
            "funding",
            "affiliation",
        ]
    )
    covers = serializers.CharField(max_length=200)
    levels = serializers.ListField(child=serializers.CharField(max_length=16), required=False)
    reason = serializers.CharField(min_length=10)


class Regulators(APIView):
    """REG-01: the national directory is public."""

    authentication_classes: list[Any] = []
    permission_classes = [Public]

    def get(self, request: Request) -> Response:
        return Response(v.jsonable(services.directory()), headers={"Cache-Control": "public, max-age=3600"})


class InstitutionRegulation(APIView):
    required_permission = {"GET": "institution:view", "POST": "regulation:manage"}

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.jsonable(services.profile(pk)))

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = LinkSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        row = services.set_link(
            pk, d["body_code"], d["relationship"], covers=d["covers"], levels=d.get("levels"), reason=d["reason"]
        )
        return Response(v.row(row), status=201)


class RegulationLink(APIView):
    required_permission = "regulation:manage"

    def delete(self, request: Request, pk: uuid.UUID) -> Response:
        services.end_link(pk, reason=str(request.data.get("reason", "")) or "ended")
        return Response(status=204)
