from django.urls import path

from syntegra.security_training import api

urlpatterns = [
    path("security-training/agencies", api.Agencies.as_view()),
    path("security-training/agencies/<uuid:pk>", api.Agency.as_view()),
    path("security-training/institutions/<uuid:pk>", api.TrainingInstitution.as_view()),
    path("security-training/courses/<uuid:pk>", api.Course.as_view()),
    path("security-training/courses/<uuid:pk>/intakes", api.CourseIntakes.as_view()),
    path("security-training/intakes/<uuid:pk>", api.Intake.as_view()),
    path("security-training/intakes/<uuid:pk>/trainees", api.IntakeTrainees.as_view()),
    path("security-training/trainees/<uuid:pk>/outcome", api.TraineeOutcome.as_view()),
]
