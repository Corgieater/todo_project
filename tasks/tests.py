from django.test import TestCase
from tasks.models import CustomUser, TaskTemplate, TaskInstance
from datetime import date, timedelta
from tasks.forms import TaskTemplateWithInstanceForm
from django.urls import reverse
from django.utils import timezone
from http import HTTPStatus
import json


class TaskTemplateWithInstanceFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            name="test",
            password="abcd4321",
        )

    def test_valid_form_creates_task_and_instance_ok(self):
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
            email="user@example.com", name="test", password="abcd4321"
        )
        self.client.login(email="user@example.com", password="abcd4321")

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
