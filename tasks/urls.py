from django.urls import path
from tasks.views import TaskView

urlpatterns = [
    path("", TaskView.as_view(), name="task_index"),
    path("add/", TaskView.as_view(), name="add_task"),
    path(
        "update/<int:instance_id>",
        TaskView.as_view(),
        name="update_instance_status",
    ),
]


"""
make the url look like 'api/tasks/.... to avoid rewriting crud
"""
