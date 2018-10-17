# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-17 16:56
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations
import speedy.core.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20180811_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='id',
            field=speedy.core.base.models.SmallUDIDField(db_index=True, max_length=15, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='id contains illegal characters.', regex='^[1-9][0-9]{14}$')], verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='useremailaddress',
            name='id',
            field=speedy.core.base.models.RegularUDIDField(db_index=True, max_length=20, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='id contains illegal characters.', regex='^[1-9][0-9]{19}$')], verbose_name='ID'),
        ),
    ]
