from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView
from django.http import HttpResponse, JsonResponse
from tasks.models import TaskTemplate, TaskInstance
from tasks.forms import TaskTemplateWithInstanceForm
from django.db.models import Q
from django.db import transaction
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
        print("get method")
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

        NOTE:
        1. if cancell a non-repeated instance, delete template too
        2. if a should repeat template need to be cancelled, prompt user to check if they need to remove this 'template' permanently or just this 'task'(instance) once
        3. deal with the logic
        """

        request_body = json.loads(request.body)
        task_status = request_body.get("status", None)

        if not task_status or task_status not in TaskInstance.Status:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        task_instance = get_object_or_404(
            TaskInstance, pk=instance_id, template__created_user=request.user
        )

        task_instance.status = task_status
        task_instance.finished_at = timezone.now()
        task_instance.save()

        return HttpResponse(status=HTTPStatus.NO_CONTENT)

    @transaction.atomic
    def delete(self, request, instance_id):
        task_instance = get_object_or_404(
            TaskInstance, id=instance_id, template__created_user=request.user
        )
        delete_future_tasks = json.loads(request.body)["body"].get(
            "delete_future_tasks"
        )

        task_instance.deleted_at = timezone.now()
        task_instance.status = TaskInstance.Status.CANCELLED
        task_instance.save()

        if task_instance.template.recursion_rule is None or (
            delete_future_tasks and task_instance.template.recursion_rule is not None
        ):
            task_instance.template.deleted_at = timezone.now()
            task_instance.template.save()

        return HttpResponse(status=HTTPStatus.NO_CONTENT)


class TaskRecursionCheckView(LoginRequiredMixin, View):
    """
    do tests!
    """

    def get(self, request, instance_id):
        task_instance = get_object_or_404(
            TaskInstance, pk=instance_id, template__created_user=request.user
        )
        is_recursive = task_instance.template.recursion_rule is not None
        return JsonResponse({"is_recursive": is_recursive})

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
