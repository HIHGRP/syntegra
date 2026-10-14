from django.urls import path

from syntegra.web import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sign-in", views.sign_in, name="sign_in"),
    path("sign-out", views.sign_out, name="sign_out"),
    path("pages", views.catalogue, name="catalogue"),
    path("verify", views.verify, name="verify"),
    path("registers/class/<uuid:class_id>", views.register, name="register"),
    path("learners/<uuid:learner_id>", views.learner, name="learner"),
    path("coverage", views.coverage, name="coverage"),
]
