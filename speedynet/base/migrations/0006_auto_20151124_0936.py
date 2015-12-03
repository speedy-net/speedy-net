# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_customfriend'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customfriend',
            name='friend_ptr',
        ),
        migrations.DeleteModel(
            name='CustomFriend',
        ),
    ]
