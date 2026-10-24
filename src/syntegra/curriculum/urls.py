from django.urls import path

from syntegra.curriculum import api

urlpatterns = [
    path("institutions/<uuid:institution_id>/coverage/evaluate", api.EvaluateCoverage.as_view()),
    path("coverage/gaps", api.GapList.as_view()),
    path("coverage/gaps/<uuid:pk>/accept", api.AcceptGap.as_view()),
]
