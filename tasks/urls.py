from django.urls import path
from tasks.views import TaskView, TaskRecursionCheckView

urlpatterns = [
    path("", TaskView.as_view(), name="task_index"),
    path("", TaskView.as_view(), name="task_create"),
    path(
        "<int:instance_id>",
        TaskView.as_view(),
        name="task_update",
    ),
    path("<int:instance_id>", TaskView.as_view(), name="task_delete"),
    path(
        "<int:instance_id>/task_check_recursion",
        TaskRecursionCheckView.as_view(),
        name="task_check_recursion",
    ),
]


"""
make the url look like 'api/tasks/.... to avoid rewriting crud
"""
