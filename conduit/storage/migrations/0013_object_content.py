# Generated by Django 5.0.7 on 2024-08-15 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0012_remove_object_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="object",
            name="content",
            field=models.ManyToManyField(blank=True, to="storage.object"),
        ),
    ]
