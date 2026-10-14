from django.urls import path

from syntegra.academic import api

urlpatterns = [
    path("classes", api.ClassList.as_view()),
    path("classes/<uuid:pk>/members", api.ClassMembers.as_view()),
]
