from django.urls import path
from tasks.views import TaskView, TaskRecursionCheckView

urlpatterns = [
    path("", TaskView.as_view(), name="task_index"),
    path("add/", TaskView.as_view(), name="add_task"),
    path(
        "update/<int:instance_id>",
        TaskView.as_view(),
        name="patch_task",
    ),
    path("delete/<int:instance_id>", TaskView.as_view(), name="delete_task"),
    path(
        "check_recursion/<int:instance_id>",
        TaskRecursionCheckView.as_view(),
        name="check_recursion",
    ),
]


"""
make the url look like 'api/tasks/.... to avoid rewriting crud
"""
