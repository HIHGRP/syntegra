from django.urls import path

from syntegra.records import api

urlpatterns = [
    path("documents", api.Documents.as_view()),
    path("documents/categories", api.Categories.as_view()),
    path("documents/<uuid:pk>", api.DocumentDetail.as_view()),
    path("documents/<uuid:pk>/content", api.DocumentContent.as_view()),
    path("documents/<uuid:pk>/word", api.DocumentWord.as_view()),
    path("documents/<uuid:pk>/certified", api.DocumentCertified.as_view()),
    path("records/releases", api.Releases.as_view()),
    path("records/releases/<str:code>", api.ReleaseCheck.as_view()),
    path("institutions/<uuid:institution_id>/documents", api.SchoolRegister.as_view()),
]
