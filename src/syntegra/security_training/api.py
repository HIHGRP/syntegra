"""Security agencies' education and training API (CR-004)."""

from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.security_training import services


class IntakeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    intake_code = serializers.CharField(max_length=40)
    name = serializers.CharField(max_length=300)
    starts_on = serializers.DateField()
    ends_on = serializers.DateField(required=False, allow_null=True)
    capacity = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class TraineeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    learner_id = serializers.UUIDField()
    rank_code = serializers.CharField(max_length=24, required=False, allow_null=True)


class OutcomeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    outcome = serializers.ChoiceField(list(services.FINAL_OUTCOMES))
    result = serializers.CharField(max_length=120, required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_null=True)
    on = serializers.DateField(required=False, allow_null=True)


class Agencies(APIView):
    required_permission = "security_training:view"

    def get(self, request: Request) -> Response:
        return Response({"data": v.jsonable(services.directory())})


class Agency(APIView):
    required_permission = "security_training:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.jsonable(services.agency(pk)))


class TrainingInstitution(APIView):
    required_permission = "security_training:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.jsonable(services.institution(pk)))


class Course(APIView):
    required_permission = "security_training:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.jsonable(services.course(pk)))


class CourseIntakes(APIView):
    required_permission = "security_training:intake"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = IntakeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.create_intake(pk, **s.validated_data)), status=201)


class Intake(APIView):
    required_permission = "security_training:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.jsonable(services.intake(pk)))


class IntakeTrainees(APIView):
    required_permission = "security_training:record"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = TraineeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        return Response(v.row(services.add_trainee(pk, d["learner_id"], rank_code=d.get("rank_code"))), status=201)


class TraineeOutcome(APIView):
    required_permission = "security_training:record"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = OutcomeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        r = services.record_outcome(pk, d["outcome"], result=d.get("result"), reason=d.get("reason"), on=d.get("on"))
        return Response(v.row(r))
