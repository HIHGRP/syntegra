from __future__ import annotations

import datetime as dt
import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.attendance import services
from syntegra.core.api import views as v


class MarkSerializer(serializers.Serializer):  # type: ignore[type-arg]
    learner_id = serializers.UUIDField()
    code = serializers.CharField(max_length=4)
    minutes_late = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    client_op_id = serializers.UUIDField(required=False, allow_null=True)
    reason_source = serializers.ChoiceField(["teacher", "parent", "office", "system"], required=False, allow_null=True)


class SubmitSerializer(serializers.Serializer):  # type: ignore[type-arg]
    marks = MarkSerializer(many=True)
    device_captured_at = serializers.DateTimeField(required=False, allow_null=True)


class OpenRegisterSerializer(serializers.Serializer):  # type: ignore[type-arg]
    session_date = serializers.DateField(required=False, allow_null=True)
    kind = serializers.ChoiceField(["am", "pm", "daily", "lesson", "activity", "trip"], default="daily")


class OpenRegister(APIView):
    required_permission = "attendance:mark"

    def post(self, request: Request, class_id: uuid.UUID) -> Response:
        s = OpenRegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        reg = services.open_register(class_id, d.get("session_date") or dt.date.today(), d["kind"])
        return v.with_etag(Response(v.row(reg), status=201), reg)


class RegisterDetail(APIView):
    required_permission = {"GET": "attendance:view", "PUT": "attendance:mark"}

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        view = services.register_view(pk)
        reg = view["register"]
        marks = view["marks"]
        body = v.row(reg)
        body["roster"] = [
            {"learner_id": str(m.learner_id), "mark": v.row(marks[m.learner_id]) if m.learner_id in marks else None}
            for m in view["roster"]
        ]
        return v.with_etag(Response(body), reg)

    def put(self, request: Request, pk: uuid.UUID) -> Response:
        s = SubmitSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        m = v.meta(request)
        marks = [services.Mark(**x) for x in s.validated_data["marks"]]

        def run() -> Response:
            r = services.submit(
                pk, marks, device_captured_at=s.validated_data.get("device_captured_at"), if_match=m.if_match
            )
            resp = Response(v.jsonable(r))
            resp["ETag"] = f'W/"{r["row_version"]}"'
            return resp

        return v.idempotent(request, run)


class LearnerAttendance(APIView):
    required_permission = "attendance:view"

    def get(self, request: Request, learner_id: uuid.UUID) -> Response:
        end = dt.date.fromisoformat(request.query_params.get("to", dt.date.today().isoformat()))
        start = dt.date.fromisoformat(request.query_params.get("from", (end - dt.timedelta(days=90)).isoformat()))
        from syntegra.learners import services as learners

        learners.get(learner_id)  # visibility (derived scope)
        return Response(v.jsonable(services.learner_summary(learner_id, start, end)))
