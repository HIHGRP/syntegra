from django.urls import path

from syntegra.clearance import api

urlpatterns = [
    path("clearance/checks", api.Checks.as_view()),
    path("clearance/checks/<uuid:pk>/decision", api.CheckDecision.as_view()),
    path("clearance/obligations", api.Obligations.as_view()),
    path("clearance/obligations/<uuid:pk>/disputes", api.Disputes.as_view()),
    path("clearance/disputes/<uuid:pk>/resolution", api.DisputeResolution.as_view()),
    path("learners/<uuid:learner_id>/clearance-checks", api.LearnerChecks.as_view()),
]
