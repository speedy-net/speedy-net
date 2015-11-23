# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_birth', models.DateTimeField(default=datetime.datetime(1909, 2, 13, 0, 0))),
                ('gender', models.SmallIntegerField(default=3, choices=[(1, b'Female'), (2, b'Male'), (3, b'Other')])),
                ('diet', models.SmallIntegerField(default=1, choices=[(1, b'Eat all'), (2, b'Vegeterian'), (3, b'Vegan')])),
                ('profile_picture', models.ImageField(upload_to=b'user_pictures/', blank=True)),
                ('field_privacy', models.TextField(default=b'{"first_name": 1, "last_name": 1, "gender": 1, "diet": 1, "date_of_birth": 1, "email": 1}', max_length=500)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
