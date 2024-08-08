# Generated by Django 5.0.7 on 2024-08-08 13:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0004_drive_used"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="drive",
            name="unique_personal_drive_per_user",
        ),
        migrations.AddConstraint(
            model_name="drive",
            constraint=models.UniqueConstraint(
                condition=models.Q(("type", "personal")),
                fields=("owner",),
                name="unique_personal_drive_per_user",
            ),
        ),
    ]
