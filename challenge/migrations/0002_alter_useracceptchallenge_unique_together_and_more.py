# Generated by Django 5.0.2 on 2024-02-14 15:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenge', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='useracceptchallenge',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='useracceptchallenge',
            constraint=models.UniqueConstraint(fields=('user', 'challenge'), name='challenge_useracceptchallenge_unique_user_challenge'),
        ),
    ]
