from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.core.api.pagination import UUID7CursorPagination
from syntegra.learners import services


class RegisterSerializer(serializers.Serializer):  # type: ignore[type-arg]
    given = serializers.CharField(max_length=200)
    family = serializers.CharField(max_length=200)
    middle = serializers.CharField(max_length=200, required=False, allow_null=True)
    preferred_name = serializers.CharField(max_length=200, required=False, allow_null=True)
    date_of_birth = serializers.DateField()
    dob_precision = serializers.ChoiceField(["day", "month", "year"], default="day")
    sex = serializers.CharField(max_length=32)
    institution_id = serializers.UUIDField()
    education_level = serializers.CharField(max_length=32)
    nin = serializers.CharField(max_length=11, required=False, allow_null=True)
    state_of_origin = serializers.CharField(max_length=6, required=False, allow_null=True)
    start_on = serializers.DateField(required=False)
    is_minimal_documentation = serializers.BooleanField(default=False)


class TransferSerializer(serializers.Serializer):  # type: ignore[type-arg]
    to_institution_id = serializers.UUIDField()
    effective_on = serializers.DateField(required=False)
    education_level = serializers.CharField(max_length=32, required=False)


def learner_row(lrn: object) -> dict[str, object]:
    return v.row(lrn)


class LearnerList(APIView):
    required_permission = {"GET": "learner:view", "POST": "learner:register"}

    def get(self, request: Request) -> Response:
        qs = services.visible()
        if g := request.query_params.get("glid"):
            qs = qs.filter(global_learner_id=g.upper())
        if q := request.query_params.get("q"):
            qs = qs.filter(legal_family_name__istartswith=q)
        pager = UUID7CursorPagination()
        return pager.get_paginated_response([learner_row(x) for x in pager.paginate_queryset(qs, request, self)])

    def post(self, request: Request) -> Response:
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        m = v.meta(request)

        def run() -> Response:
            r = services.register(services.RegisterLearner(**s.validated_data), override_reason=m.override_reason)
            body = {"outcome": r.outcome, "learner": learner_row(r.learner),
                    "enrolment": v.row(r.enrolment) if r.enrolment else None,
                    "match_review_id": str(r.review_id) if r.review_id else None, "match": r.match}
            return Response(body, status=201 if r.outcome == "created" else 200,
                            headers={"Location": f"/api/v1/learners/{r.learner.id}"})

        return v.idempotent(request, run)


class LearnerDetail(APIView):
    required_permission = "learner:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        lrn = services.get(pk)
        body = learner_row(lrn)
        body["enrolments"] = [v.row(e) for e in services.enrolments(pk)]
        return v.with_etag(Response(body), lrn)


class LearnerTransfer(APIView):
    required_permission = "enrolment:transfer"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = TransferSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        t = services.transfer(pk, **s.validated_data)
        return Response(v.row(t), status=201)


class LearnerNin(APIView):
    required_permission = "learner.nin:reveal"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response({"nin": services.reveal_nin(pk)}, headers={"Cache-Control": "no-store"})
