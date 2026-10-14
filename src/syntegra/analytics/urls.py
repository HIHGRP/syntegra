from django.urls import path

from syntegra.analytics import api

urlpatterns = [path("metrics/<str:metric_id>", api.MetricView.as_view())]
