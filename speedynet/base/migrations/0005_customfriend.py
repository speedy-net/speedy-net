# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0001_initial'),
        ('base', '0004_auto_20151109_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFriend',
            fields=[
                ('friend_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='friendship.Friend')),
            ],
            bases=('friendship.friend',),
        ),
    ]
