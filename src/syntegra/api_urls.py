"""API v1 routes — one include per module (Book 3 §26)."""

from django.urls import include, path

urlpatterns = [
    path("", include("syntegra.iam.urls")),
]
