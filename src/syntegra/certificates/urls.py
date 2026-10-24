from django.urls import path

from syntegra.certificates import api

urlpatterns = [
    path("certificates", api.CertificateList.as_view()),
    path("certificates/<uuid:pk>", api.CertificateDetail.as_view()),
    path("certificates/<uuid:pk>/reissue", api.RequestReissue.as_view()),
    path("reissue-cases/<uuid:pk>/decision", api.DecideReissue.as_view()),
    path("public/verify", api.PublicVerify.as_view()),
    path("public/jwks.json", api.Jwks.as_view()),
]
