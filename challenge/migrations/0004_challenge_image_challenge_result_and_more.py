# Generated by Django 5.0.2 on 2024-02-17 15:01

import challenge.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("challenge", "0003_refactor_challenge"),
    ]

    operations = [
        migrations.AddField(
            model_name="challenge",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to=challenge.models.upload_to_func
            ),
        ),
        migrations.AddField(
            model_name="challenge",
            name="result",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="challenge",
            name="similarity",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
