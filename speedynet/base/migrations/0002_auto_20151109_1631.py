# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='security_answer',
            field=models.CharField(max_length=128, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='security_question',
            field=models.SmallIntegerField(default=1, choices=[(1, b'School name'), (2, b'Maiden name'), (3, b'Dog name')]),
        ),
    ]
