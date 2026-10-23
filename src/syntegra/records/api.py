"""Document management API (CR-007, FR-DOC-202–206): search, upload, metadata, the scan, the Word copy, a school's
register. The services decide scope, access level, purpose and audit; these views only validate input."""

from __future__ import annotations

import uuid

from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core import context
from syntegra.core.api import views as v
from syntegra.core.context import CLASS_ORDER
from syntegra.records import services


def _purpose(request: Request) -> str | None:
    return request.META.get("HTTP_X_SYNTEGRA_PURPOSE") or request.query_params.get("purpose") or None


class SearchSerializer(serializers.Serializer):  # type: ignore[type-arg]
    q = serializers.CharField(max_length=300, required=False, allow_blank=True, default="")
    institution_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    category = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    year = serializers.IntegerField(min_value=1800, max_value=2200, required=False, allow_null=True, default=None)
    limit = serializers.IntegerField(min_value=1, max_value=500, required=False, default=100)


class UploadSerializer(serializers.Serializer):  # type: ignore[type-arg]
    institution_id = serializers.UUIDField()
    category = serializers.CharField(max_length=40)
    title = serializers.CharField(min_length=3, max_length=300)
    date_from = serializers.DateField(required=False, allow_null=True, default=None)
    date_to = serializers.DateField(required=False, allow_null=True, default=None)
    session_label = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    level_or_class = serializers.CharField(max_length=80, required=False, allow_blank=True, default="")
    subject_label = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    source_reference = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    description = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    transcription = serializers.CharField(max_length=200000, required=False, allow_blank=True, default="")
    classification = serializers.ChoiceField(choices=CLASS_ORDER, required=False, allow_null=True, default=None)


class Documents(APIView):
    """GET search documents; POST (multipart, one or more ``files``) upload digitised paper documents."""

    required_permission = {"GET": "document:view", "POST": "document:upload"}
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request: Request) -> Response:
        s = SearchSerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        result = services.search(
            context.require(),
            q=d["q"],
            institution_id=d["institution_id"],
            category_code=d["category"],
            year=d["year"],
            limit=d["limit"],
            purpose=_purpose(request),
        )
        for r in result["rows"]:
            r["access_level"] = r.pop("level").number
        return Response(v.jsonable(result))

    def post(self, request: Request) -> Response:
        s = UploadSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        files = [services.Upload(f.name or "file", f.read()) for f in request.FILES.getlist("files")]
        docs = services.upload(
            context.require(),
            institution_id=d["institution_id"],
            category_code=d["category"],
            title=d["title"],
            files=files,
            date_from=d["date_from"],
            date_to=d["date_to"],
            session_label=d["session_label"],
            level_or_class=d["level_or_class"],
            subject_label=d["subject_label"],
            source_reference=d["source_reference"],
            description=d["description"],
            transcription=d["transcription"],
            classification=d["classification"],
        )
        return Response(
            {"documents": [{"id": str(x.id), "reference_no": x.reference_no, "title": x.title} for x in docs]},
            status=201,
        )


class DocumentDetail(APIView):
    """GET a document's metadata (restricted documents need X-Syntegra-Purpose)."""

    required_permission = "document:view"

    def get(self, request: Request, pk: uuid.UUID) -> Response:
        d = services.detail(context.require(), pk, _purpose(request))
        d["access_level"] = d.pop("level").number
        return Response(v.jsonable(d))


class DocumentContent(APIView):
    """GET the scan itself, hash-verified."""

    required_permission = "document:view"

    def get(self, request: Request, pk: uuid.UUID) -> HttpResponse:
        data, mime, name = services.content(context.require(), pk, _purpose(request))
        resp = HttpResponse(data, content_type=mime)
        resp["Content-Disposition"] = f'attachment; filename="{name}"'
        resp["Cache-Control"] = "no-store"
        return resp


class DocumentWord(APIView):
    """GET an editable Word (.docx) copy of the document's text, made on demand."""

    required_permission = "document:view"

    def get(self, request: Request, pk: uuid.UUID) -> HttpResponse:
        data, name = services.word_copy(context.require(), pk, _purpose(request))
        resp = HttpResponse(
            data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        resp["Content-Disposition"] = f'attachment; filename="{name}"'
        resp["Cache-Control"] = "no-store"
        return resp


class SchoolRegister(APIView):
    """GET one school's complete document register, grouped by category."""

    required_permission = "document:view"

    def get(self, request: Request, institution_id: uuid.UUID) -> Response:
        q = str(request.query_params.get("q", ""))[:300]
        reg = services.register(context.require(), institution_id, q=q, purpose=_purpose(request))
        return Response(
            v.jsonable(
                {
                    "institution": reg["institution"],
                    "total": reg["total"],
                    "size_bytes": reg["size"],
                    "hidden_above_level": reg["hidden_above_level"],
                    "restricted_hidden": reg["restricted_hidden"],
                    "restricted_left_out": reg["restricted_left_out"],
                    "groups": [
                        {"category": title, "documents": [{**r, "level": r["level"].number} for r in rows]}
                        for title, rows in reg["groups"]
                    ],
                }
            )
        )


class Categories(APIView):
    required_permission = "document:view"

    def get(self, request: Request) -> Response:
        return Response(
            {
                "data": [
                    {"code": c.code, "title": c.title, "classification": c.classification}
                    for c in services.categories()
                ]
            }
        )
