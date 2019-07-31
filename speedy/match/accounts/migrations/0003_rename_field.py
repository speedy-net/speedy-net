# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('match_accounts', '0002_auto_20190730_1956'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteprofile',
            old_name='marital_status_match',
            new_name='relationship_status_match',
        ),
    ]
