from __future__ import annotations

import base64
import uuid

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from syntegra.certificates import services
from syntegra.certificates.models import Certificate
from syntegra.core.api import views as v
from syntegra.core.api.permissions import Public
from syntegra.core.errors import NotFound


class IssueSerializer(serializers.Serializer):  # type: ignore[type-arg]
    learner_id = serializers.UUIDField()
    institution_id = serializers.UUIDField()
    template_id = serializers.UUIDField()
    signatory_id = serializers.UUIDField()
    award_date = serializers.DateField()
    award_title = serializers.CharField(max_length=200)
    award_class = serializers.CharField(max_length=40, required=False, allow_null=True)
    qualification_id = serializers.UUIDField(required=False, allow_null=True)


class ReissueSerializer(serializers.Serializer):  # type: ignore[type-arg]
    reason = serializers.ChoiceField(["lost_or_stolen", "damaged", "change_of_name", "issuer_error", "certified_copy"])
    applicant_name = serializers.CharField(max_length=200)
    applicant_phone = serializers.CharField(max_length=16)


def cert_row(c: Certificate) -> dict[str, object]:
    out = v.row(c, [f for f in c.ceda_fields if f not in ("signature", "payload_hash", "vc_document")])
    out["signature_b64"] = base64.b64encode(bytes(c.signature)).decode()
    return out


class CertificateList(APIView):
    required_permission = {"GET": "certificate:view", "POST": "certificate:issue"}

    def get(self, request: Request) -> Response:
        qs = Certificate.objects.in_scope()
        if lid := request.query_params.get("learner_id"):
            qs = qs.filter(learner_id=lid)
        return Response({"data": [cert_row(c) for c in qs.order_by("-award_date")[:200]]})

    def post(self, request: Request) -> Response:
        s = IssueSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return v.idempotent(request, lambda: Response(cert_row(services.issue(services.IssueRequest(**s.validated_data))),
                                                      status=201))


class CertificateDetail(APIView):
    required_permission = "certificate:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        c = Certificate.objects.in_scope().filter(pk=pk).first()
        if c is None:
            raise NotFound("certificate", pk)
        return v.with_etag(Response(cert_row(c)), c)


class RequestReissue(APIView):
    required_permission = "certificate:reissue"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        s = ReissueSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(v.row(services.request_reissue(pk, **s.validated_data)), status=201)


class DecideReissue(APIView):
    required_permission = "certificate:approve"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        approve = bool(request.data.get("approve"))
        return Response(v.row(services.decide_reissue(pk, approve, note=request.data.get("note"))))


class PublicVerify(APIView):
    """PUB-01: anyone may verify a certificate by number or code (rate-limited, logged)."""

    authentication_classes: list[object] = []
    permission_classes = [Public]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_verify"

    def get(self, request: Request) -> Response:
        q = request.query_params.get("number") or request.query_params.get("code") or ""
        channel = "qr" if request.query_params.get("via") == "qr" else "web_number"
        return Response(v.jsonable(services.verify(q, channel=channel)), headers={"Cache-Control": "no-store"})


class Jwks(APIView):
    authentication_classes: list[object] = []
    permission_classes = [Public]

    def get(self, request: Request) -> Response:
        return Response(services.jwks(), headers={"Cache-Control": "public, max-age=3600"})
