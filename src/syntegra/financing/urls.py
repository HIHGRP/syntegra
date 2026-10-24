from django.urls import path

from syntegra.financing import api

urlpatterns = [
    path("institutions/<uuid:institution_id>/census", api.TakeCensus.as_view()),
    path("census/<uuid:pk>/freeze", api.FreezeCensus.as_view()),
    path("census/<uuid:pk>/demand", api.IssueDemand.as_view()),
]
