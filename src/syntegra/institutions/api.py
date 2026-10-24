from __future__ import annotations

import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.core.api.pagination import UUID7CursorPagination
from syntegra.institutions import services
from syntegra.institutions.models import Institution


class RegisterSerializer(serializers.Serializer):  # type: ignore[type-arg]
    name = serializers.CharField(max_length=300)
    category = serializers.CharField(max_length=32)
    ownership = serializers.ChoiceField(["federal", "state", "lga", "private", "faith", "community", "ngo"])
    lga_scope_id = serializers.UUIDField()
    address = serializers.DictField()
    levels = serializers.ListField(child=serializers.CharField(max_length=32), min_length=1)
    gov_reg_no = serializers.CharField(max_length=40, required=False, allow_null=True)
    location = serializers.ListField(child=serializers.FloatField(), min_length=2, max_length=2, required=False)
    capacity = serializers.IntegerField(min_value=1, required=False)
    short_name = serializers.CharField(max_length=80, required=False)
    day_boarding = serializers.ChoiceField(["day", "boarding", "mixed"], required=False)
    gender_intake = serializers.ChoiceField(["mixed", "boys", "girls"], required=False)
    operating_tenant_id = serializers.UUIDField(required=False)


class InstitutionList(APIView):
    required_permission = {"GET": "institution:view", "POST": "institution:register"}

    def get(self, request: Request) -> Response:
        qs = Institution.objects.in_scope()
        if lga := v.uuid_param(request, "lga_scope_id"):
            qs = qs.filter(lga_scope_id=lga)
        if q := request.query_params.get("q"):
            qs = qs.filter(name__icontains=q)
        pager = UUID7CursorPagination()
        return pager.get_paginated_response([v.row(i) for i in pager.paginate_queryset(qs, request, self)])

    def post(self, request: Request) -> Response:
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        if d.get("location"):
            d["location"] = tuple(d["location"])
        m = v.meta(request)

        def run() -> Response:
            inst = services.register(services.RegisterInstitution(**d), override_reason=m.override_reason)
            return v.with_etag(
                Response(v.row(inst), status=201, headers={"Location": f"/api/v1/institutions/{inst.id}"}), inst
            )

        return v.idempotent(request, run)


class InstitutionDetail(APIView):
    required_permission = "institution:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        inst = services.get(pk)
        return v.with_etag(Response(v.row(inst)), inst)
