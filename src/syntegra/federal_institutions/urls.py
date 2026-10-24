from django.urls import path

from syntegra.federal_institutions import api

urlpatterns = [
    path("federal-institutions", api.FederalInstitutions.as_view()),
    path("federal-institutions/import", api.FederalImport.as_view()),
]
