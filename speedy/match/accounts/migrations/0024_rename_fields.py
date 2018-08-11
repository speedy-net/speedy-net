# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_accounts', '0023_auto_20180810_1554'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteprofile',
            old_name='smoking',
            new_name='smoking_status',
        ),
        migrations.RenameField(
            model_name='siteprofile',
            old_name='smoking_match',
            new_name='smoking_status_match',
        ),
    ]
