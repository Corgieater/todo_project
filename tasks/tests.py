from django.test import TestCase
from tasks.models import CustomUser, TaskTemplate, TaskInstance, RecursionRule
from datetime import date, timedelta
from tasks.forms import TaskTemplateWithInstanceForm
from django.urls import reverse
from django.utils import timezone
from http import HTTPStatus
import json


class TaskTemplateWithInstanceFormTest(TestCase):
    """
    NOTE:
    Add invalidate tests?
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test1@test.com",
            name="test1",
            password="abcd4321",
        )

    def test_valid_form_creates_task_and_instance_200_ok(self):
        form_data = {
            "name": "Test Task",
            "description": "Test Description",
            "assigned_users": [],
            "location": "Office",
            "priority": 3,
            "recursion_rule": None,
            "due_date": timezone.now().date().isoformat(),
        }
        form = TaskTemplateWithInstanceForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

        task_template, task_instance = form.save()
        self.assertIsNotNone(task_template)
        self.assertIsNotNone(task_instance)
        self.assertEqual(task_template.created_user, self.user)
        self.assertEqual(task_instance.template, task_template)


class TaskViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test1@test.com", name="test1", password="abcd4321"
        )
        self.client.login(email="test1@test.com", password="abcd4321")

        # Set an unfinished task
        self.unfinished_task_template = TaskTemplate.objects.create(
            created_user=self.user, name="unfinished task", description="test"
        )
        self.unfinished_task_instance = TaskInstance.objects.create(
            template=self.unfinished_task_template,
        )

        # Set a yesterday unfinished task
        self.unfinished_yesterday_task_template = TaskTemplate.objects.create(
            created_user=self.user,
            name="unfinished yesterday task",
            description="unfinished yesterday task",
        )
        self.unfinished_yesterday_task_instance = TaskInstance.objects.create(
            template=self.unfinished_task_template,
        )
        self.unfinished_yesterday_task_instance.created_at = timezone.now() - timedelta(
            days=1
        )
        self.unfinished_yesterday_task_instance.save()

        # Set a finished task
        self.finished_task_template = TaskTemplate.objects.create(
            created_user=self.user, name="finished task", description="finished task"
        )
        self.finished_task_instance = TaskInstance.objects.create(
            template=self.finished_task_template,
            finished_at=timezone.now(),
            status=TaskInstance.Status.COMPLETED,
        )

        # Set another user and it's related task
        self.another_user = CustomUser.objects.create_user(
            email="test2@test.com", name="test2", password="abcd4321"
        )
        self.another_template = TaskTemplate.objects.create(
            created_user=self.another_user, name="another user task"
        )
        self.another_task = TaskInstance.objects.create(template=self.another_template)

    def test_get_task_instance_200_ok(self):
        url = reverse("task_index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "tasks/index.html")
        self.assertContains(response, self.unfinished_task_template.name)
        self.assertContains(response, self.unfinished_task_template.description)
        self.assertContains(response, self.finished_task_template.name)
        self.assertContains(response, self.finished_task_template.description)
        unfinished_tasks_in_context = response.context["unfinished_tasks"]
        finished_tasks_in_context = response.context["finished_tasks"]
        self.assertEqual(unfinished_tasks_in_context.count(), 2)
        self.assertIn(self.unfinished_task_instance, unfinished_tasks_in_context)
        self.assertIn(self.finished_task_instance, finished_tasks_in_context)

    def test_get_task_instance_with_no_task_200_ok(self):
        TaskInstance.objects.all().delete()

        url = reverse("task_index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "tasks/index.html")
        self.assertEqual(response.context["unfinished_tasks"].count(), 0)
        self.assertEqual(response.context["finished_tasks"].count(), 0)

    def test_patch_update_task_instance_status_200_ok(self):
        url = reverse("patch_task", args=[self.unfinished_task_instance.id])
        data = {"status": TaskInstance.Status.COMPLETED}

        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.unfinished_task_instance.refresh_from_db()

        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(
            self.unfinished_task_instance.status, TaskInstance.Status.COMPLETED
        )
        self.assertIsNotNone(self.unfinished_task_instance.finished_at)

    def test_patch_update_task_instance_status_400_bad_request(self):
        url = reverse("patch_task", args=[self.unfinished_task_instance.id])
        data = {"status": "Invalid Status"}
        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.unfinished_task_instance.refresh_from_db()

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_patch_update_task_instance_status_404_not_found(self):
        url = reverse("patch_task", args=[9999999999])
        data = {"status": TaskInstance.Status.COMPLETED}
        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.unfinished_task_instance.refresh_from_db()

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TaskCancellTest(TestCase):
    """
    check if the user are nor the creater to do delete to, it should fail
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test1@test.com", name="test1", password="abcd4321"
        )
        self.client.login(email="test1@test.com", password="abcd4321")

        # set non-repreated task
        self.non_repeat_task_template = TaskTemplate.objects.create(
            created_user=self.user, name="no repeat"
        )
        self.non_repeat_task = TaskInstance.objects.create(
            template=self.non_repeat_task_template
        )

        # set repeated task
        self.repeat_task_template = TaskTemplate.objects.create(
            created_user=self.user,
            name="repeat",
            recursion_rule=RecursionRule.objects.get(id=1),
        )
        self.repeat_task = TaskInstance.objects.create(
            template=self.repeat_task_template
        )

    def test_soft_delete_non_repeat_task_status_204_no_content(self):
        url = reverse("delete_task", args=[self.non_repeat_task.id])
        data = {"body": {"delete_future_tasks": False}}
        response = self.client.delete(
            url, data=json.dumps(data), content="application/json"
        )
        non_repeat_task_template = TaskTemplate.objects.get(
            id=self.non_repeat_task.template.id
        )
        non_repeat_task_instance = TaskInstance.objects.get(id=self.non_repeat_task.id)
        self.assertIsNotNone(non_repeat_task_instance.deleted_at)
        self.assertEqual(TaskInstance.Status.CANCELLED, non_repeat_task_instance.status)
        self.assertIsNotNone(non_repeat_task_template.deleted_at)
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

    def test_soft_delete_repeat_task_and_future_tasks_status_204_no_content(self):
        url = reverse("delete_task", args=[self.repeat_task.id])
        data = {"body": {"delete_future_tasks": True}}
        response = self.client.delete(
            url, data=json.dumps(data), content="application/json"
        )
        repeat_task_template = TaskTemplate.objects.get(id=self.repeat_task.template.id)
        repeat_task_instance = TaskInstance.objects.get(id=self.repeat_task.id)
        self.assertIsNotNone(repeat_task_instance.deleted_at)
        self.assertEqual(TaskInstance.Status.CANCELLED, repeat_task_instance.status)
        self.assertIsNotNone(repeat_task_template.deleted_at)
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

    def test_soft_delete_repeat_task_only_this_time_status_204_no_content(self):
        url = reverse("delete_task", args=[self.repeat_task.id])
        data = {"body": {"delete_future_tasks": False}}
        response = self.client.delete(
            url, data=json.dumps(data), content="application/json"
        )
        repeat_task_template = TaskTemplate.objects.get(id=self.repeat_task.template.id)
        repeat_task_instance = TaskInstance.objects.get(id=self.repeat_task.id)
        self.assertIsNotNone(repeat_task_instance.deleted_at)
        self.assertEqual(TaskInstance.Status.CANCELLED, repeat_task_instance.status)
        self.assertIsNone(repeat_task_template.deleted_at)
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

    def test_soft_delete_non_repeat_task_status_404_not_found(self):
        url = reverse("delete_task", args=[999999999])
        data = {"body": {"delete_future_tasks": False}}
        response = self.client.delete(
            url, data=json.dumps(data), content="application/json"
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
