from django.urls import path

from syntegra.iam import api

urlpatterns = [
    path("auth/sign-in", api.SignInView.as_view()),
    path("auth/mfa", api.MfaView.as_view()),
    path("auth/role", api.SelectRoleView.as_view()),
    path("auth/sign-out", api.SignOutView.as_view()),
    path("me", api.MeView.as_view()),
    path("auth/sessions", api.SessionsView.as_view()),
    path("auth/sessions/<uuid:pk>/end", api.SessionEndView.as_view()),
    path("access/levels", api.AccessLevelsView.as_view()),
    path("access/grants/<uuid:pk>/level", api.GrantLevelView.as_view()),
    path("access/grants/<uuid:pk>/office", api.GrantOfficeView.as_view()),
    path("access/offices", api.OfficesView.as_view()),
    path("access/offices/<uuid:pk>/address", api.OfficeAddressView.as_view()),
]
