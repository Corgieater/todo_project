from django.db import models
from core.models import Timestamp
from django.contrib.postgres.fields import ArrayField


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


# 　this should be changed see claud
class Task(models.Model, Timestamp):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        IN_PROGRESS = "in_progress", "In progress"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"
        CRITICAL = 5, "Critical"

    # how due_date works for weekly or monthly task?
    due_date = models.DateTimeField(null=False, blank=True)
    request_body = models.JSONField()
    assigned_users = ArrayField(models.IntegerField(), null=True, blank=True)
    location = models.CharField(max_length=256, null=True, blank=True)
    recursion_rule = models.ForeignKey(
        RecursionRule, on_delete=models.SET_NULL, null=True, blank=True
    )
    task_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
