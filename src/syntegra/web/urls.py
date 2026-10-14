from django.urls import path

from syntegra.web import views

urlpatterns = [
    path("", views.home, name="home"),
]
