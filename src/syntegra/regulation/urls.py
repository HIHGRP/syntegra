from django.urls import path

from syntegra.regulation import api

urlpatterns = [
    path("regulators", api.Regulators.as_view()),
    path("institutions/<uuid:pk>/regulation", api.InstitutionRegulation.as_view()),
    path("regulation-links/<uuid:pk>", api.RegulationLink.as_view()),
]
