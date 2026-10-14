from django.urls import path

from syntegra.estate import api

urlpatterns = [
    path("estate/sites", api.Sites.as_view()),
    path("estate/buildings", api.Buildings.as_view()),
    path("estate/rooms", api.Rooms.as_view()),
    path("estate/assets", api.Assets.as_view()),
    path("estate/assessments", api.Assessments.as_view()),
    path("estate/schedules", api.Schedules.as_view()),
    path("estate/schedules/<uuid:pk>/done", api.ScheduleDone.as_view()),
    path("estate/actions", api.Actions.as_view()),
    path("estate/actions/<uuid:pk>", api.ActionUpdate.as_view()),
    path("estate/actions/<uuid:pk>/work-order", api.WorkOrder.as_view()),
    path("estate/institutions/<uuid:institution_id>/workspace", api.Workspace.as_view()),
    path("estate/infrastructure", api.Infrastructure.as_view()),
]
