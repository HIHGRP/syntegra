from django.urls import path

from syntegra.iam import api

urlpatterns = [
    path("auth/sign-in", api.SignInView.as_view()),
    path("auth/mfa", api.MfaView.as_view()),
    path("auth/role", api.SelectRoleView.as_view()),
    path("auth/sign-out", api.SignOutView.as_view()),
    path("me", api.MeView.as_view()),
]
