from django.urls import path

from syntegra.assessment import api

urlpatterns = [
    path("exams/series", api.Series.as_view()),
    path("exams/series/<uuid:pk>/papers", api.Papers.as_view()),
    path("exams/series/<uuid:pk>/entries", api.Entries.as_view()),
    path("exams/series/<uuid:pk>/sittings", api.Sittings.as_view()),
    path("exams/papers/<uuid:pk>/sitting", api.PaperSitting.as_view()),
    path("exams/institutions/<uuid:institution_id>/halls", api.Halls.as_view()),
]
