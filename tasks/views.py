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
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskInstanceSerializer


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


class TaskInstanceDetailViewSet(ModelViewSet):
    queryset = TaskInstance.objects.all()
    serializer_class = TaskInstanceSerializer
    permission_classes = [IsAuthenticated]

    # def get(self, request, instance_id):
    #     task_instance = get_object_or_404(
    #         TaskInstance, pk=instance_id, template__created_user=request.user
    #     )
    #     serializer = TaskInstanceSerializer(task_instance)
    #     return Response(serializer.data)

    # def patch(self, request, instance_id):
    #     """
    #     run through request.body and updating task instance
    #     1. add other part that might need to update

    #     NOTE:
    #     1. if cancell a non-repeated instance, delete template too
    #     2. if a should repeat template need to be cancelled, prompt user to check if they need to remove this 'template' permanently or just this 'task'(instance) once
    #     3. deal with the logic
    #     """

    #     # request_body = json.loads(request.body)
    #     # task_status = request_body.get("status", None)

    #     # """
    #     # NOTE 4/14:
    #     # 1. we should update object through different apis
    #     # 2. separate patch instance and template
    #     # 3. we might need to change view names too
    #     # 4. updating and creating are serializer's job
    #     # 5. check tests

    #     # """

    #     # if not task_status or task_status not in TaskInstance.Status:
    #     #     return HttpResponse(status=HTTPStatus.BAD_REQUEST)

    #     task_instance = get_object_or_404(
    #         TaskInstance, pk=instance_id, template__created_user=request.user
    #     )
    #     serializer = TaskInstanceSerializer(
    #         task_instance, data=request.data, partial=True
    #     )
    #     if serializer.is_valid():
    #         serializer.save()
    #         return HttpResponse(status=HTTPStatus.NO_CONTENT)
    #     return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    #     # task_instance.status = task_status
    #     # task_instance.finished_at = timezone.now()
    #     # task_instance.save()

    #     # return HttpResponse(status=HTTPStatus.NO_CONTENT)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        task_instance = self.get_object()
        is_recursive = task_instance.template.recursion_rule is not None

        if task_instance.template.created_user != request.user:
            return Response(status=HTTPStatus.FORBIDDEN)

        delete_future_tasks = request.data.get("delete_future_tasks", None)
        should_delete_template = False

        if is_recursive and delete_future_tasks:
            should_delete_template = True
        elif not is_recursive:
            should_delete_template = True

        task_instance.soft_delete(delete_template=should_delete_template)
        return Response(status=HTTPStatus.NO_CONTENT)


# class TaskDetailView(LoginRequiredMixin, View):
#     def get(self, request, instance_id):
#         task_instance = get_object_or_404(
#             TaskInstance, pk=instance_id, template__created_user=request.user
#         )
#         data = {
#             "name": task_instance.template.name,
#             "description": task_instance.template.description,
#             "priority": task_instance.template.priority,
#             "recursion_rule": getattr(
#                 task_instance.template.recursion_rule, "pk", None
#             ),
#             "due_date": task_instance.due_date,
#         }
#         return JsonResponse(data)

#     def patch(self, request, instance_id):
#         """
#         run through request.body and updating task instance
#         1. add other part that might need to update

#         NOTE:
#         1. if cancell a non-repeated instance, delete template too
#         2. if a should repeat template need to be cancelled, prompt user to check if they need to remove this 'template' permanently or just this 'task'(instance) once
#         3. deal with the logic
#         """

#         request_body = json.loads(request.body)
#         task_status = request_body.get("status", None)

#         """
#         what to update?
#         - task name
#         - description
#         - assignees
#         - priority
#         - recursion rule
#         - due date

#         """

#         if not task_status or task_status not in TaskInstance.Status:
#             return HttpResponse(status=HTTPStatus.BAD_REQUEST)

#         task_instance = get_object_or_404(
#             TaskInstance, pk=instance_id, template__created_user=request.user
#         )

#         task_instance.status = task_status
#         task_instance.finished_at = timezone.now()
#         task_instance.save()

#         return HttpResponse(status=HTTPStatus.NO_CONTENT)

#     @transaction.atomic
#     def delete(self, request, instance_id):
#         task_instance = get_object_or_404(
#             TaskInstance, id=instance_id, template__created_user=request.user
#         )
#         delete_future_tasks = json.loads(request.body)["body"].get(
#             "delete_future_tasks"
#         )

#         task_instance.deleted_at = timezone.now()
#         task_instance.status = TaskInstance.Status.CANCELLED
#         task_instance.save()

#         if task_instance.template.recursion_rule is None or (
#             delete_future_tasks and task_instance.template.recursion_rule is not None
#         ):
#             task_instance.template.deleted_at = timezone.now()
#             task_instance.template.save()

#         return HttpResponse(status=HTTPStatus.NO_CONTENT)
