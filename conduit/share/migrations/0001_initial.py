# Generated by Django 5.0.7 on 2025-03-01 21:25

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("storage", "0016_alter_drive_size_alter_drive_used"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Share",
            fields=[
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "note",
                    models.CharField(
                        blank=True,
                        max_length=3000,
                        null=True,
                        verbose_name="Upload Message",
                    ),
                ),
                ("assets", models.ManyToManyField(to="storage.object")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="uploads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "drive",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="shares",
                        to="storage.drive",
                    ),
                ),
                (
                    "mentioned_members",
                    models.ManyToManyField(to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
    ]
