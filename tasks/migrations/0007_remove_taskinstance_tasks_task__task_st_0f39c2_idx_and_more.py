# Generated by Django 5.1.5 on 2025-02-27 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_remove_tasktemplate_request_body'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='taskinstance',
            name='tasks_task__task_st_0f39c2_idx',
        ),
        migrations.RenameField(
            model_name='taskinstance',
            old_name='task_status',
            new_name='status',
        ),
        migrations.AddIndex(
            model_name='taskinstance',
            index=models.Index(fields=['status', 'created_at'], name='tasks_task__status_25aba1_idx'),
        ),
    ]
