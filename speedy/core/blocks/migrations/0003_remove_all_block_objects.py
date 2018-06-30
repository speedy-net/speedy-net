# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    Block = apps.get_model('blocks', 'Block')
    Block.objects.all().delete()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20180322_1252'),
        ('blocks', '0002_auto_20180630_2254'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
