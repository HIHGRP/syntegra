"""API v1 routes — one include per module (Book 3 §26)."""

from django.urls import include, path

from syntegra.core.api import ceda

urlpatterns = [
    path("", include("syntegra.iam.urls")),
    path("", include("syntegra.institutions.urls")),
    path("", include("syntegra.learners.urls")),
    path("", include("syntegra.academic.urls")),
    path("", include("syntegra.attendance.urls")),
    path("", include("syntegra.curriculum.urls")),
    path("", include("syntegra.certificates.urls")),
    path("", include("syntegra.financing.urls")),
    path("", include("syntegra.analytics.urls")),
    path("", include("syntegra.hr.urls")),
    path("", include("syntegra.clearance.urls")),
    path("", include("syntegra.security_training.urls")),
    path("", include("syntegra.federal_institutions.urls")),
    path("", include("syntegra.regulation.urls")),
    path("", include("syntegra.finance.urls")),
    path("", include("syntegra.funding.urls")),
    path("", include("syntegra.estate.urls")),
    path("ceda", ceda.Catalogue.as_view()),
    path("ceda/<str:entity>", ceda.EntityList.as_view()),
    path("ceda/<str:entity>/<uuid:pk>", ceda.EntityDetail.as_view()),
]
