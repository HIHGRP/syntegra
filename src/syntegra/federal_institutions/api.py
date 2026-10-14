"""Federal institutions API (CR-005)."""

from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.core.api import views as v
from syntegra.federal_institutions import services


class FederalInstitutions(APIView):
    required_permission = "federal_institutions:view"

    def get(self, request: Request) -> Response:
        q = request.query_params
        return Response(
            v.jsonable(services.directory(body=q.get("body"), zone=q.get("zone"), institution_type=q.get("type")))
        )


class FederalImport(APIView):
    """Official list as CSV text (``text/csv`` body or ``{"csv": ...}``); ``?dry_run=1`` validates only."""

    required_permission = "federal_institutions:import"

    def post(self, request: Request) -> Response:
        text = request.data.get("csv") if isinstance(request.data, dict) else None
        r = services.import_csv(str(text or ""), dry_run=request.query_params.get("dry_run") == "1")
        return Response(v.jsonable(r), status=201 if r["applied"] else 200)
