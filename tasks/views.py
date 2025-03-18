from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView
from django.http import HttpResponse
from tasks.models import TaskTemplate, TaskInstance
from tasks.forms import TaskTemplateWithInstanceForm
from django.db.models import Q
import json
from http import HTTPStatus
from django.utils import timezone
from core.util import get_day_time_range


class TaskView(LoginRequiredMixin, View):
    def get(self, request):
        """
        TODO:
        1. do a cancel bt to change the status
        2. how to deal with recursive tasks?
        """

        """
        go back to check your test
        """
        start_of_day, end_of_day = get_day_time_range(timezone.now().date())

        query = (
            TaskInstance.objects.filter(
                template__created_user=request.user,
            )
            .select_related("template")
            .order_by("created_at")
            .exclude(status=TaskInstance.Status.CANCELLED)
        )

        finished_tasks = query.filter(
            status=TaskInstance.Status.COMPLETED,
            finished_at__range=(start_of_day, end_of_day),
        ).order_by("-finished_at")

        unfinished_tasks = query.exclude(status=TaskInstance.Status.COMPLETED).order_by(
            "-template__priority"
        )

        context = {
            "form": TaskTemplateWithInstanceForm(),
            "finished_tasks": finished_tasks,
            "unfinished_tasks": unfinished_tasks,
        }
        return render(request, "tasks/index.html", context)

    def post(self, request):
        form = TaskTemplateWithInstanceForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
        return redirect("task_index")

    def patch(self, request, instance_id):
        """
        run through request.body and updating task instance
        1. add other part that might need to update
        """
        request = json.loads(request.body)

        task_instance = TaskInstance.objects.get(pk=instance_id)
        task_status = request.get("status", None)

        if not task_status or task_status not in TaskInstance.Status:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        task_instance.status = task_status
        task_instance.finished_at = timezone.now()
        task_instance.save()

        return HttpResponse(status=HTTPStatus.NO_CONTENT)

    # model = TaskInstance
    # context_object_name = "task_instance"
    # queryset = TaskInstance.objects.filter(
    #     created_at__lte=timezone.now(), created_at__gte=timezone.now()
    # )
    # paginate_by = 20
    # template_name = "tasks/index.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["form"] = TaskTemplateForm()
    #     return context


# class IndexView(ListView):
#     model = TaskInstance
#     context_object_name = "task_instance"
#     queryset = TaskInstance.objects.filter(
#         created_at__lte=timezone.now(), created_at__gte=timezone.now()
#     )
#     paginate_by = 20
#     template_name = "tasks/index.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["form"] = TaskTemplateForm()
#         return context
