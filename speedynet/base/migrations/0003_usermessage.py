# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0002_auto_20151109_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('opened', models.DateTimeField(blank=True)),
                ('hidden', models.BooleanField(default=False)),
                ('sent_from', models.ForeignKey(related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
                ('sent_to', models.ForeignKey(related_name='received_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
