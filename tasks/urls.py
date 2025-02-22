from django.urls import path
from tasks.views import IndexView

urlpatterns = [path("", IndexView.as_view(), name="task_index")]
