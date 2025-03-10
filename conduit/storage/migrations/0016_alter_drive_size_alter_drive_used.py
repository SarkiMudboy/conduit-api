# Generated by Django 5.0.7 on 2025-02-18 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0015_alter_object_path"),
    ]

    operations = [
        migrations.AlterField(
            model_name="drive",
            name="size",
            field=models.FloatField(
                blank=True,
                default=5368709120.0,
                null=True,
                verbose_name="Drive size (kb)",
            ),
        ),
        migrations.AlterField(
            model_name="drive",
            name="used",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="Space used (kb)"
            ),
        ),
    ]
