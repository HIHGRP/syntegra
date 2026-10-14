from django.urls import path

from syntegra.institutions import api

urlpatterns = [
    path("institutions", api.InstitutionList.as_view()),
    path("institutions/<uuid:pk>", api.InstitutionDetail.as_view()),
]
