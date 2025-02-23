from django.db import models
from core.models import Timestamp
from django.contrib.postgres.fields import ArrayField
from users.models import CustomUser
from django.utils import timezone


class RecursionRule(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    frequency = models.CharField(max_length=20, choices=Frequency.choices)
    interval = models.IntegerField(default=1)
    end_date = models.DateField(null=True, blank=True)
    days_of_week = ArrayField(models.IntegerField(), null=True, blank=True)

    class Meta:
        db_table = "tasks_recursion_rule"


class TaskTemplate(Timestamp):
    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"
        CRITICAL = 5, "Critical"

    request_body = models.JSONField()
    created_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assigned_users = ArrayField(models.IntegerField(), null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    recursion_rule = models.ForeignKey(
        RecursionRule, on_delete=models.SET_NULL, null=True, blank=True
    )
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        db_table = "tasks_task_template"


class TaskInstance(Timestamp):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        IN_PROGRESS = "in_progress", "In progress"
        CANCELLED = "cancelled", "Cancelled"

    due_date = models.DateTimeField(null=True, blank=True)
    finished_time = models.DateTimeField(null=True, blank=True)
    template = models.ForeignKey(
        TaskTemplate, on_delete=models.PROTECT, related_name="instances"
    )
    task_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        db_table = "tasks_task_instance"
        indexes = [
            models.Index(fields=["template", "created_at"]),
            models.Index(fields=["task_status", "created_at"]),
            models.Index(fields=["due_date"]),
        ]
