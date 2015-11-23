# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_usermessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermessage',
            name='opened',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(default=b'default_profile_pic.png', upload_to=b'user_pictures/', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='security_answer',
            field=models.CharField(default=b'', max_length=128, blank=True),
        ),
    ]
