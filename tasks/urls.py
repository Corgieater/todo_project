from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import TaskView, TaskInstanceDetailViewSet

router = DefaultRouter()
router.register(r"instance", TaskInstanceDetailViewSet, basename="task-instance")

urlpatterns = [
    path("", TaskView.as_view(), name="task_index"),
    path("", TaskView.as_view(), name="task_create"),
    path("", include(router.urls)),
    # path(
    #     "<int:instance_id>",
    #     TaskInstanceDetailViewSet.as_view(),
    #     name="task_detail_api",
    # ),
    # path(
    #     "<int:instance_id>",
    #     TaskInstanceDetailView.as_view(),
    #     name="task_update",
    # ),
    # path("<int:instance_id>", TaskInstanceDetailViewSet.as_view(), name="task_delete"),
]
