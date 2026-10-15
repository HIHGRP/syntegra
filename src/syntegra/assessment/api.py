"""Examinations API: series, papers, candidate entries and sitting arrangements (FR-EXM-01 – FR-EXM-03)."""

from __future__ import annotations

import datetime as dt
import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.assessment import exams, seating
from syntegra.core import catalog
from syntegra.core.api import views as v


class SeriesSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    name = serializers.CharField(max_length=300)
    exam_body = serializers.ChoiceField(catalog.code_list("exam_body"), default="INSTITUTION")
    entry_closes_on = serializers.DateField(required=False, allow_null=True)


class PaperSerializer(serializers.Serializer):  # type: ignore[type-arg]
    paper_code = serializers.RegexField(r"^[A-Za-z0-9][A-Za-z0-9-]{0,19}$")
    title = serializers.CharField(max_length=300)
    duration_minutes = serializers.IntegerField(min_value=10, max_value=480)
    subject_id = serializers.UUIDField(required=False, allow_null=True)


class EntriesSerializer(serializers.Serializer):  # type: ignore[type-arg]
    class_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False, max_length=50)
    paper_codes = serializers.ListField(
        child=serializers.RegexField(r"^[A-Za-z0-9][A-Za-z0-9-]{0,19}$"), allow_empty=False, max_length=40
    )


class SittingSerializer(serializers.Serializer):  # type: ignore[type-arg]
    room_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False, max_length=60)
    starts_on = serializers.DateField()
    starts_time = serializers.TimeField()
    spacing = serializers.ChoiceField(seating.SPACING, default="alternate")
    invigilator_staff_ids = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=200)


def starts_at(d: dict[str, object]) -> dt.datetime:
    return dt.datetime.combine(d["starts_on"], d["starts_time"], tzinfo=dt.UTC)  # type: ignore[arg-type]


class Series(APIView):
    required_permission = {"GET": "exam:view", "POST": "exam:manage"}

    def get(self, request: Request) -> Response:
        return Response({"data": v.jsonable(exams.series_list())})

    def post(self, request: Request) -> Response:
        s = SeriesSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        return Response(v.row(exams.create_series(d.pop("institution_id"), d.pop("name"), **d)), status=201)


class Papers(APIView):
    required_permission = "exam:manage"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = PaperSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        paper = exams.add_paper(pk, d["paper_code"], d["title"], d["duration_minutes"], subject_id=d.get("subject_id"))
        return Response(v.row(paper), status=201)


class Entries(APIView):
    required_permission = "exam:manage"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = EntriesSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(exams.enter_classes(pk, s.validated_data["class_ids"], s.validated_data["paper_codes"]))


class Sittings(APIView):
    required_permission = {"GET": "exam:view", "POST": "exam:manage"}

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        """EXM-03 for a series (``pk`` is the series)."""
        return Response(v.jsonable(exams.arrangements(pk)))


class PaperSitting(APIView):
    required_permission = "exam:manage"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        """Plan (or re-plan) the sitting of paper ``pk``."""
        s = SittingSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        rows = exams.plan_sitting(
            pk,
            d["room_ids"],
            starts_at(d),
            spacing=d["spacing"],
            invigilator_staff_ids=d.get("invigilator_staff_ids") or [],
        )
        return Response({"data": [v.row(x) for x in rows]}, status=201)


class Halls(APIView):
    required_permission = "exam:view"

    def get(self, request: Request, institution_id: uuid.UUID) -> Response:
        return Response({"data": v.jsonable(exams.halls(institution_id))})
