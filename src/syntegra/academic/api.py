from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.academic import services
from syntegra.academic.models import ClassGroup
from syntegra.core.api import views as v


class ClassSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    period_id = serializers.UUIDField()
    name = serializers.CharField(max_length=300)
    education_level = serializers.CharField(max_length=32)
    capacity = serializers.IntegerField(min_value=1, required=False)


class ClassList(APIView):
    required_permission = {"GET": "class:view", "POST": "class:manage"}

    def get(self, request: Request) -> Response:
        qs = ClassGroup.objects.in_scope().filter(status="active")
        if inst := v.uuid_param(request, "institution_id"):
            qs = qs.filter(institution_id=inst)
        return Response({"data": [v.row(c) for c in qs.order_by("name")[:500]]})

    def post(self, request: Request) -> Response:
        s = ClassSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.create_class(**s.validated_data)), status=201)


class MemberSerializer(serializers.Serializer):  # type: ignore[type-arg]
    learner_id = serializers.UUIDField()


class ClassMembers(APIView):
    required_permission = {"GET": "class:view", "POST": "class:manage"}

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        if not ClassGroup.objects.in_scope().filter(pk=pk).exists():
            return Response(status=404)
        return Response({"data": [v.row(m) for m in services.members(pk)]})

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = MemberSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.add_member(pk, s.validated_data["learner_id"])), status=201)
