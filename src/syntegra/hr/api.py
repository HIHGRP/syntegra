"""HRMS API (CR-001). Services enforce permissions, scope, four-eyes and human-only decisions."""

from __future__ import annotations

import datetime as dt
import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.hr import establishment, leave, payroll, postings, relations


class PositionSerializer(serializers.Serializer):  # type: ignore[type-arg]
    title = serializers.CharField(max_length=300)
    cadre_code = serializers.CharField(max_length=20)
    employer_scope_id = serializers.UUIDField()
    grade_level_min = serializers.IntegerField(min_value=1, max_value=17)
    grade_level_max = serializers.IntegerField(min_value=1, max_value=17)
    institution_id = serializers.UUIDField(required=False, allow_null=True)
    subject_id = serializers.UUIDField(required=False, allow_null=True)
    education_levels = serializers.ListField(child=serializers.CharField(), required=False)
    funding = serializers.ChoiceField(["funded", "unfunded", "donor_funded", "privately_funded"], default="funded")


class AppointSerializer(serializers.Serializer):  # type: ignore[type-arg]
    staff_id = serializers.UUIDField()
    position_id = serializers.UUIDField()
    appointment_type = serializers.CharField(max_length=32)
    first_appointment_on = serializers.DateField()
    grade_level = serializers.IntegerField(min_value=1, max_value=17)
    step = serializers.IntegerField(min_value=1, max_value=15, default=1)
    confirmed_on = serializers.DateField(required=False, allow_null=True)


class PostingSerializer(serializers.Serializer):  # type: ignore[type-arg]
    staff_id = serializers.UUIDField()
    to_position_id = serializers.UUIDField()
    posting_kind = serializers.CharField(max_length=32)
    reason = serializers.CharField()
    effective_on = serializers.DateField()


class LeaveSerializer(serializers.Serializer):  # type: ignore[type-arg]
    staff_id = serializers.UUIDField()
    leave_type = serializers.CharField(max_length=32)
    starts_on = serializers.DateField()
    ends_on = serializers.DateField()
    note = serializers.CharField(max_length=500, required=False, allow_null=True)


class Positions(APIView):
    required_permission = "hr:establishment"

    def post(self, request: Request) -> Response:
        s = PositionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(establishment.create_position(establishment.NewPosition(**s.validated_data))), status=201)


class Establishment(APIView):
    required_permission = "hr:view"

    def get(self, request: Request, institution_id: uuid.UUID) -> Response:
        return Response(v.jsonable(establishment.establishment(institution_id)))


class Appointments(APIView):
    required_permission = "hr:appoint"

    def post(self, request: Request) -> Response:
        s = AppointSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(establishment.appoint(establishment.Appointment(**s.validated_data))), status=201)


class Postings(APIView):
    required_permission = "hr:posting_request"

    def post(self, request: Request) -> Response:
        s = PostingSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(postings.request_posting(**s.validated_data)), status=201)


class PostingDecision(APIView):
    required_permission = "hr:posting_approve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        action = str(request.data.get("action", "approve"))
        if action == "effective":
            return Response(v.row(postings.make_effective(pk)))
        return Response(v.row(postings.approve_posting(pk, approve=action == "approve", note=request.data.get("note"))))


class Separations(APIView):
    required_permission = "hr:separate"

    def post(self, request: Request) -> Response:
        d = request.data
        sep = postings.record_separation(
            uuid.UUID(str(d["staff_post_id"])),
            str(d["separation_kind"]),
            effective_on=dt.date.fromisoformat(str(d["effective_on"])),
        )
        return Response(v.row(sep), status=201)


class LeaveRequests(APIView):
    required_permission = None  # own leave (hr:leave_request) or on behalf (hr:leave_manage) — checked in service

    def post(self, request: Request) -> Response:
        s = LeaveSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(leave.request_leave(**s.validated_data)), status=201)


class LeaveDecision(APIView):
    required_permission = "hr:leave_approve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.row(leave.decide_leave(pk, bool(request.data.get("approve")))))


class Promotions(APIView):
    required_permission = "hr:promote"

    def post(self, request: Request) -> Response:
        d = request.data
        return Response(
            v.row(establishment.open_promotion(uuid.UUID(str(d["staff_id"])), str(d["exercise_label"]))), status=201
        )


class PromotionDecision(APIView):
    required_permission = "hr:promote"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(
            v.row(establishment.decide_promotion(pk, str(request.data["decision"]), reason=request.data.get("reason")))
        )


class RelationsCases(APIView):
    required_permission = "hr:relations"

    def post(self, request: Request) -> Response:
        d = request.data
        return Response(
            v.row(relations.open_case(uuid.UUID(str(d["staff_id"])), str(d["case_kind"]), str(d["summary"]))),
            status=201,
        )


class IntegrityScan(APIView):
    required_permission = "hr:integrity"

    def post(self, request: Request) -> Response:
        return Response({"raised": payroll.scan_integrity()})


class IntegrityHold(APIView):
    required_permission = "hr:integrity"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(
            v.row(payroll.decide_hold(pk, bool(request.data.get("hold")), str(request.data.get("reason", ""))))
        )


class PayrollRuns(APIView):
    required_permission = "hr:payroll_prepare"

    def post(self, request: Request) -> Response:
        d = request.data
        run = payroll.compute_payroll(
            uuid.UUID(str(d["employer_scope_id"])), str(d["period_label"]), dt.date.fromisoformat(str(d["pay_date"]))
        )
        return Response(v.row(run), status=201)


class PayrollApproval(APIView):
    required_permission = "hr:payroll_approve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.row(payroll.approve_payroll(pk)))
