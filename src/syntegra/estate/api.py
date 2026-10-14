"""Government property, facility condition and proactive maintenance API (CR-006, FR-EST-01 – FR-EST-06).

Sites, buildings, rooms and equipment; dated condition and usability assessments; preventive maintenance plans;
the proactive actions the rules raise (acknowledge, start, complete, dismiss, turn into a work order); and the
read models for the head (workspace), the LGA and ministry (actions, property register) and the Commissioner
(infrastructure overview from the warehouse). Amounts are in kobo.
"""

from __future__ import annotations

import uuid
from typing import Any

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core import catalog
from syntegra.core.api import views as v
from syntegra.estate import services

SUBJECT_KINDS = tuple(services.SUBJECTS)


def _enum(name: str, **kw: object) -> serializers.ChoiceField:
    return serializers.ChoiceField(catalog.enum_values(name), **kw)  # type: ignore[arg-type]


def _cl(name: str, **kw: object) -> serializers.ChoiceField:
    return serializers.ChoiceField(catalog.code_list(name), **kw)  # type: ignore[arg-type]


def _clean(d: dict[str, Any]) -> dict[str, Any]:
    return {k: x for k, x in d.items() if x not in (None, "")}


class SiteSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    site_code = serializers.RegexField(r"^[A-Za-z0-9][A-Za-z0-9-]{0,19}$")
    name = serializers.CharField(max_length=200)
    owner = _enum("property_owner")
    title_document = _enum("land_title")
    title_reference = serializers.CharField(max_length=120, required=False, allow_null=True, allow_blank=True)
    area_sqm = serializers.FloatField(min_value=1, required=False, allow_null=True)
    latitude = serializers.FloatField(min_value=-90, max_value=90, required=False, allow_null=True)
    longitude = serializers.FloatField(min_value=-180, max_value=180, required=False, allow_null=True)
    fenced = _enum("fence_status", default="unknown")
    encroachment = _enum("encroachment_status", default="unknown")
    acquired_on = serializers.DateField(required=False, allow_null=True)
    valuation_minor = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    valued_on = serializers.DateField(required=False, allow_null=True)


class BuildingSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    built_year = serializers.IntegerField(min_value=1850, max_value=2100, required=False, allow_null=True)


class RoomSerializer(serializers.Serializer):  # type: ignore[type-arg]
    building_id = serializers.UUIDField()
    code = serializers.RegexField(r"^[A-Za-z0-9][A-Za-z0-9-]{0,19}$")
    room_type = _cl("room_type")
    capacity = serializers.IntegerField(min_value=0, max_value=5000)
    name = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)


class AssetSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    asset_tag = serializers.RegexField(r"^[A-Za-z0-9][A-Za-z0-9/-]{0,39}$")
    name = serializers.CharField(max_length=200)
    category = _cl("asset_category")
    room_id = serializers.UUIDField(required=False, allow_null=True)
    acquired_on = serializers.DateField(required=False, allow_null=True)
    value_minor = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    next_service_on = serializers.DateField(required=False, allow_null=True)
    safety_check_due_on = serializers.DateField(required=False, allow_null=True)


class DefectSerializer(serializers.Serializer):  # type: ignore[type-arg]
    element = serializers.CharField(max_length=60)
    severity = _enum("severity")
    note = serializers.CharField(max_length=300, required=False, allow_blank=True)


class AssessmentSerializer(serializers.Serializer):  # type: ignore[type-arg]
    subject_kind = serializers.ChoiceField(SUBJECT_KINDS)
    subject_id = serializers.UUIDField()
    condition_grade = _cl("condition_grade")
    usability = _enum("usability_status")
    structural_risk = _enum("severity")
    in_use = serializers.BooleanField()
    assessor_kind = _enum("facility_assessor", default="head_of_institution")
    defects = DefectSerializer(many=True, required=False)
    utilities = serializers.DictField(required=False)
    learners_affected = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    repair_estimate_minor = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    next_due_on = serializers.DateField(required=False, allow_null=True)
    assessed_on = serializers.DateField(required=False, allow_null=True)
    client_op_id = serializers.UUIDField(required=False, allow_null=True)


class ScheduleSerializer(serializers.Serializer):  # type: ignore[type-arg]
    subject_kind = serializers.ChoiceField(SUBJECT_KINDS)
    subject_id = serializers.UUIDField()
    task = serializers.CharField(max_length=200)
    task_kind = _enum("maintenance_task_kind")
    frequency_days = serializers.IntegerField(min_value=1, max_value=3650)
    next_due_on = serializers.DateField()
    responsible_staff_id = serializers.UUIDField(required=False, allow_null=True)
    estimated_cost_minor = serializers.IntegerField(min_value=0, required=False, allow_null=True)


class CompleteSerializer(serializers.Serializer):  # type: ignore[type-arg]
    done_on = serializers.DateField(required=False, allow_null=True)
    cost_minor = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    note = serializers.CharField(max_length=500, required=False, allow_null=True, allow_blank=True)


class ActSerializer(serializers.Serializer):  # type: ignore[type-arg]
    status = serializers.ChoiceField(["acknowledged", "in_progress", "done", "dismissed"])
    note = serializers.CharField(max_length=1000, required=False, allow_null=True, allow_blank=True)


class Sites(APIView):
    required_permission = None  # reading needs estate:view, registering estate:manage — checked in the service

    def get(self, request: Request) -> Response:
        """EST-01: the government property register in scope."""
        return Response({"data": v.jsonable(services.property_register())})

    def post(self, request: Request) -> Response:
        s = SiteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = _clean(dict(s.validated_data))
        lat, lon = d.pop("latitude", None), d.pop("longitude", None)
        if lat is not None and lon is not None:
            d["location"] = (lat, lon)
        return Response(v.row(services.register_site(d.pop("institution_id"), **d)), status=201)


class Buildings(APIView):
    required_permission = "estate:manage"

    def post(self, request: Request) -> Response:
        s = BuildingSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        b = services.add_building(d["institution_id"], d["name"], built_year=d.get("built_year"))
        return Response(v.row(b), status=201)


class Rooms(APIView):
    required_permission = "estate:manage"

    def post(self, request: Request) -> Response:
        s = RoomSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        r = services.add_room(d["building_id"], d["code"], d["room_type"], d["capacity"], name=d.get("name") or None)
        return Response(v.row(r), status=201)


class Assets(APIView):
    required_permission = "estate:manage"

    def post(self, request: Request) -> Response:
        s = AssetSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = _clean(dict(s.validated_data))
        a = services.add_asset(d.pop("institution_id"), d.pop("asset_tag"), d.pop("name"), d.pop("category"), **d)
        return Response(v.row(a), status=201)


class Assessments(APIView):
    required_permission = "estate:assess"

    def post(self, request: Request) -> Response:
        s = AssessmentSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = _clean(dict(s.validated_data))
        if "defects" in d:
            d["defects"] = [dict(x) for x in d["defects"]]
        a = services.assess(d.pop("subject_kind"), d.pop("subject_id"), **d)
        return Response(v.row(a), status=201)


class Schedules(APIView):
    required_permission = "estate:manage"

    def post(self, request: Request) -> Response:
        s = ScheduleSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = _clean(dict(s.validated_data))
        return Response(
            v.row(services.schedule_maintenance(d.pop("subject_kind"), d.pop("subject_id"), **d)), status=201
        )


class ScheduleDone(APIView):
    required_permission = "estate:act"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = CompleteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.complete_maintenance(pk, **_clean(dict(s.validated_data)))))


class Actions(APIView):
    required_permission = "estate:view"

    def get(self, request: Request) -> Response:
        """EST-02: open proactive actions in scope, escalated first (``?status=done`` etc. for closed ones)."""
        status = request.query_params.get("status", "open")
        if status not in ("open", "done", "dismissed"):
            raise serializers.ValidationError({"status": "open, done or dismissed"})
        return Response({"data": v.jsonable(services.actions_in_scope(status=status))})


class ActionUpdate(APIView):
    required_permission = "estate:act"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = ActSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.act(pk, s.validated_data["status"], s.validated_data.get("note") or None)))


class WorkOrder(APIView):
    required_permission = "estate:act"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        return Response(v.row(services.raise_work_order(pk)), status=201)


class Workspace(APIView):
    required_permission = "estate:view"

    def get(self, request: Request, institution_id: uuid.UUID) -> Response:
        """The head's facilities workspace (FR-EST-05)."""
        return Response(v.jsonable(services.workspace(institution_id)))


class Infrastructure(APIView):
    required_permission = "warehouse:view"

    def get(self, request: Request) -> Response:
        """EST-03: the Commissioner's holistic view of school infrastructure (``?scope_id=`` to drill down)."""
        from syntegra.analytics import warehouse

        return Response(v.jsonable(warehouse.state_overview(v.uuid_param(request, "scope_id"))))
