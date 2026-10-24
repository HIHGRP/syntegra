from django.urls import path

from syntegra.hr import api

urlpatterns = [
    path("hr/positions", api.Positions.as_view()),
    path("hr/institutions/<uuid:institution_id>/establishment", api.Establishment.as_view()),
    path("hr/appointments", api.Appointments.as_view()),
    path("hr/postings", api.Postings.as_view()),
    path("hr/postings/<uuid:pk>/decision", api.PostingDecision.as_view()),
    path("hr/separations", api.Separations.as_view()),
    path("hr/leave", api.LeaveRequests.as_view()),
    path("hr/leave/<uuid:pk>/decision", api.LeaveDecision.as_view()),
    path("hr/promotions", api.Promotions.as_view()),
    path("hr/promotions/<uuid:pk>/decision", api.PromotionDecision.as_view()),
    path("hr/relations", api.RelationsCases.as_view()),
    path("hr/integrity/scan", api.IntegrityScan.as_view()),
    path("hr/integrity/<uuid:pk>/hold", api.IntegrityHold.as_view()),
    path("hr/payroll-runs", api.PayrollRuns.as_view()),
    path("hr/payroll-runs/<uuid:pk>/approve", api.PayrollApproval.as_view()),
]
