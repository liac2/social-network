# Generated by Django 5.1.3 on 2025-01-15 08:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("network", "0002_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="time",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2025, 1, 15, 8, 43, 3, 298199, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
    ]
