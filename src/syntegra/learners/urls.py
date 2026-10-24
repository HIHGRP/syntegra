from django.urls import path

from syntegra.learners import api

urlpatterns = [
    path("learners", api.LearnerList.as_view()),
    path("learners/<uuid:pk>", api.LearnerDetail.as_view()),
    path("learners/<uuid:pk>/transfer", api.LearnerTransfer.as_view()),
    path("learners/<uuid:pk>/nin", api.LearnerNin.as_view()),
    path("learners/<uuid:pk>/guardians", api.LearnerGuardians.as_view()),
]
