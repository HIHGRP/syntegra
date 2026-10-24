from django.urls import path

from syntegra.funding import api

urlpatterns = [
    path("funding/programmes", api.Programmes.as_view()),
    path("funding/overview", api.Overview.as_view()),
    path("funding/applications", api.Applications.as_view()),
    path("funding/applications/<uuid:pk>/recommendation", api.Recommendation.as_view()),
    path("funding/applications/<uuid:pk>/decision", api.Decision.as_view()),
    path("funding/applications/<uuid:pk>/agreement", api.Agreements.as_view()),
    path("funding/agreements/<uuid:pk>", api.Agreement.as_view()),
    path("funding/agreements/<uuid:pk>/disbursements", api.Disbursements.as_view()),
    path("funding/agreements/<uuid:pk>/repayments", api.Repayments.as_view()),
    path("funding/mine", api.Mine.as_view()),
]
