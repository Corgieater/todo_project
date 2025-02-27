from django import forms
from tasks.models import TaskTemplate, TaskInstance
from datetime import date


class TaskTemplateWithInstanceForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "min": date.today().isoformat(),
                "placeholder": "Select a date",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        task_template = super().save(commit=False)
        task_template.created_user = self.user

        if commit:
            task_template.save()
            task_instance = TaskInstance(
                template=task_template, due_date=self.cleaned_data["due_date"]
            )
            task_instance.save()

        return task_template, task_instance

    class Meta:
        model = TaskTemplate
        fields = [
            "name",
            "description",
            "assigned_users",
            "location",
            "priority",
            "recursion_rule",
        ]
        labels = {
            "name": "Task Name",
            "description": "Task Description",
            "assigned_users": "Assignees",
        }


# class TaskTemplateForm(ModelForm):
#     def clean(self):
#         cleaned_data = super().clean()
#         json_fields = {
#             "name": cleaned_data.get("name"),
#             "description": cleaned_data.get("description"),
#             "assigned_users": cleaned_data.get("assigned_users"),
#             "location": cleaned_data.get("location"),
#             "priority": cleaned_data.get("priority"),
#             "recursion_rule": cleaned_data.get("recursion_rule"),
#         }

#     class Meta:
#         model = TaskTemplate
#         fields = [
#             "name",
#             "description",
#             "assigned_users",
#             "location",
#             "priority",
#             "recursion_rule",
#         ]
#         labels = {
#             "name": "Task Name",
#             "description": "Task Description",
#             "assigned_users": "Assignees",
#         }
