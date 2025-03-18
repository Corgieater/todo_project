# Generated by Django 5.1.2 on 2025-03-18 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_rename_finished_time_taskinstance_finished_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskinstance',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='tasktemplate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
