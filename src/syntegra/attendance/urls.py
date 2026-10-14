from django.urls import path

from syntegra.attendance import api

urlpatterns = [
    path("classes/<uuid:class_id>/registers", api.OpenRegister.as_view()),
    path("registers/<uuid:pk>", api.RegisterDetail.as_view()),
    path("learners/<uuid:learner_id>/attendance", api.LearnerAttendance.as_view()),
]
