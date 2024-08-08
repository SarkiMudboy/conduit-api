# Generated by Django 5.0.7 on 2024-08-08 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0003_alter_drive_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="drive",
            name="used",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Space used (kb)"
            ),
        ),
    ]
