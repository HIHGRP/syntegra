from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.clearance.api import decision_from_headers
from syntegra.core.api import views as v
from syntegra.core.api.pagination import UUID7CursorPagination
from syntegra.families import services as families
from syntegra.families.domain.guardians import RELATIONSHIPS
from syntegra.learners import services


class GuardianSerializer(serializers.Serializer):  # type: ignore[type-arg]
    given = serializers.CharField(max_length=200)
    family = serializers.CharField(max_length=200)
    relationship = serializers.ChoiceField(list(RELATIONSHIPS))
    has_parental_responsibility = serializers.BooleanField(default=True)
    phone = serializers.CharField(max_length=24, required=False, allow_null=True, allow_blank=True)
    email = serializers.CharField(max_length=254, required=False, allow_null=True, allow_blank=True)
    nin = serializers.CharField(max_length=13, required=False, allow_null=True, allow_blank=True)
    title = serializers.CharField(max_length=30, required=False, allow_null=True, allow_blank=True)
    lives_with = serializers.BooleanField(default=True)
    is_authorised_collector = serializers.BooleanField(default=True)
    is_payer = serializers.BooleanField(default=False)
    preferred_language = serializers.CharField(max_length=35, required=False, allow_null=True)


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
    guardians = GuardianSerializer(many=True, required=False, default=list)
    programme_id = serializers.UUIDField(required=False, allow_null=True)
    cohort_label = serializers.CharField(max_length=60, required=False, allow_null=True, allow_blank=True)
    identifiers = serializers.DictField(child=serializers.CharField(max_length=40), required=False, default=dict)


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
            data = dict(s.validated_data)
            data["guardians"] = [families.GuardianInput(**g) for g in data.get("guardians", [])]
            r = services.register(
                services.RegisterLearner(**data),
                override_reason=m.override_reason,
                clearance=decision_from_headers(request),
            )
            body = {
                "outcome": r.outcome,
                "learner": learner_row(r.learner),
                "enrolment": v.row(r.enrolment) if r.enrolment else None,
                "match_review_id": str(r.review_id) if r.review_id else None,
                "match": r.match,
                "guardians": [
                    {"guardian_id": str(g.guardian.id), "created": g.created, "linked": g.linked} for g in r.guardians
                ],
            }
            return Response(
                body,
                status=201 if r.outcome == "created" else 200,
                headers={"Location": f"/api/v1/learners/{r.learner.id}"},
            )

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
        t = services.transfer(pk, **s.validated_data, clearance=decision_from_headers(request))
        return Response(v.row(t), status=201)


class LearnerNin(APIView):
    required_permission = "learner.nin:reveal"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        return Response({"nin": services.reveal_nin(pk)}, headers={"Cache-Control": "no-store"})


class LearnerGuardians(APIView):
    """Current guardians of a learner (FR-FAM-02); contact details are withheld where contact is restricted."""

    required_permission = "learner:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        services.get(pk)  # derived scope: only learners the caller may see
        return Response({"data": v.jsonable(families.guardians_of(pk))})
