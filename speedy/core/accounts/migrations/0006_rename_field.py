# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_entity_special_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='marital_status',
            new_name='relationship_status',
        ),
    ]
