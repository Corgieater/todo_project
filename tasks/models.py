from django.db import models
from core.models import Timestamp
from django.contrib.postgres.fields import ArrayField
from users.models import CustomUser
from django.utils import timezone


class RecursionRule(models.Model):
    # this is not working as I think
    # I think things should work like in book
    # need to change
    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    frequency = models.CharField(max_length=20, choices=Frequency.choices)
    interval = models.IntegerField(default=1)
    end_date = models.DateField(null=True, blank=True)
    days_of_week = ArrayField(models.IntegerField(), null=True, blank=True)

    def __str__(self):
        WEEK_DAYS_MAPPING = (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
        if self.days_of_week:
            days = "".join([WEEK_DAYS_MAPPING[day] for day in self.days_of_week])
            return f"Every {days}"
        return f"{self.frequency.capitalize()}"

    class Meta:
        db_table = "tasks_recursion_rule"


class TaskTemplate(Timestamp):
    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"
        CRITICAL = 5, "Critical"

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assigned_users = ArrayField(models.IntegerField(), null=True, blank=True)
    name = models.CharField(max_length=255, default="task")
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    recursion_rule = models.ForeignKey(
        RecursionRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    due_date = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    template = models.ForeignKey(
        TaskTemplate, on_delete=models.PROTECT, related_name="instances"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        db_table = "tasks_task_instance"
        indexes = [
            models.Index(fields=["template", "created_at"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["due_date"]),
        ]

    def soft_delete(self, delete_template):
        self.deleted_at = timezone.now()
        self.status = TaskInstance.Status.CANCELLED
        self.save()

        if delete_template:
            self.template.soft_delete()
