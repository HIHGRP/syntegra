from __future__ import annotations

import uuid

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.core.errors import HardValidation
from syntegra.curriculum import services


class EvaluateCoverage(APIView):
    required_permission = "coverage:evaluate"

    def post(self, request: Request, institution_id: uuid.UUID) -> Response:
        return Response(v.jsonable(services.evaluate_institution(institution_id)))


class GapList(APIView):
    required_permission = "coverage:view"

    def get(self, request: Request) -> Response:
        gaps = services.open_gaps(v.uuid_param(request, "institution_id"))
        return Response({"data": [v.row(g) for g in gaps]})


class AcceptGap(APIView):
    required_permission = "coverage:manage"

    def post(self, request: Request, pk: uuid.UUID) -> Response:
        reason = str(request.data.get("reason", "")).strip()
        if len(reason) < 10:
            raise HardValidation("GAP-REASON", "Reason required", "Explain why the gap is accepted (10+ characters).")
        return Response(v.row(services.accept(pk, reason)))
