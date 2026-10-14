from __future__ import annotations

import datetime as dt

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from syntegra.analytics import metrics
from syntegra.core.api import views as v


class MetricView(APIView):
    required_permission = "metric:view"

    def get(self, request: Request, metric_id: str) -> Response:
        p = request.query_params
        start = dt.date.fromisoformat(p["from"]) if p.get("from") else None
        end = dt.date.fromisoformat(p["to"]) if p.get("to") else None
        return Response(v.jsonable(metrics.compute(metric_id.upper(), start=start, end=end)))
