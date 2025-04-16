from rest_framework import serializers
from .models import TaskInstance, TaskTemplate, RecursionRule
from django.utils import timezone


class RecursionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursionRule
        fields = ["id", "interval", "days_of_week"]


class TaskTemplateSerializer(serializers.ModelSerializer):
    recursion_rule = RecursionRuleSerializer(read_only=True)

    class Meta:
        model = TaskTemplate
        fields = "__all__"
        # fields = ["name", "description", "priority", "recursion_rule"]


class TaskInstanceSerializer(serializers.ModelSerializer):
    template = TaskTemplateSerializer(read_only=True)

    class Meta:
        model = TaskInstance
        fields = "__all__"
        # fields = ["id", "due_date", "status", "template"]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        if instance.status == TaskInstance.Status.COMPLETED:
            instance.finished_at = timezone.now()
        else:
            instance.finished_at = None

        instance.save()
        return instance


# class TaskInstanceSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source="template.name")
#     description = serializers.CharField(source="template.description")
#     priority = serializers.IntegerField(source="template.priority")
#     recursion_rule = serializers.PrimaryKeyRelatedField(
#         source="template.recursion_rule"
#     )
