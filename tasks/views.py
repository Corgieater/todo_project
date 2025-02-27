from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView
from django.http import HttpResponse
from tasks.models import TaskTemplate, TaskInstance
from django.utils import timezone
from tasks.forms import TaskTemplateWithInstanceForm
from datetime import datetime, time
from django.db.models import Q
import json
from http import HTTPStatus


class TaskView(LoginRequiredMixin, View):
    def get(self, request):
        """
        how to deal with recursive tasks?
        """
        today = timezone.now().date()
        start_of_day = timezone.make_aware(datetime.combine(today, time.min))
        end_of_day = timezone.make_aware(datetime.combine(today, time.max))
        # filter task today or not finished
        tasks = (
            TaskInstance.objects.filter(template__created_user=request.user)
            .filter(
                Q(created_at__gte=start_of_day, created_at__lte=end_of_day)
                | Q(finished_time__isnull=True)
            )
            .select_related("template")
            .order_by("created_at")
        )
        context = {"form": TaskTemplateWithInstanceForm(), "task": tasks}
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
        status = request.get("status", None)

        if status and status in TaskInstance.Status:
            task_instance.status = status
            task_instance.finished_time = timezone.now()
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
