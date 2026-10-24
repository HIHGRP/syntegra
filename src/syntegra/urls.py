"""URL configuration: versioned REST API under /api/v1, public endpoints and server-rendered pages."""

from django.http import HttpRequest, JsonResponse
from django.urls import include, path


def healthz(request: HttpRequest) -> JsonResponse:
    from syntegra.core.catalog import ceda_version

    return JsonResponse({"status": "ok", "ceda": ceda_version()})


urlpatterns = [
    path("healthz", healthz),
    path("api/v1/", include("syntegra.api_urls")),
    path("", include("syntegra.web.urls")),
]
