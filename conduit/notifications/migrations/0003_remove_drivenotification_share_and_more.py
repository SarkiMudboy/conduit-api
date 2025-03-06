# Generated by Django 5.0.7 on 2025-03-06 09:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0002_remove_drivenotification_read_and_more"),
        ("storage", "0016_alter_drive_size_alter_drive_used"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="drivenotification",
            name="share",
        ),
        migrations.AddField(
            model_name="drivenotification",
            name="read_by",
            field=models.ManyToManyField(
                related_name="read_notification", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="drivenotification",
            name="drive",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to="storage.drive",
            ),
        ),
        migrations.AlterField(
            model_name="drivenotification",
            name="publisher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="published_notifications",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
