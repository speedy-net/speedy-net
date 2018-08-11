# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20180322_1252'),
        ('blocks', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='block',
            old_name='blockee',
            new_name='blocked',
        ),
    ]
