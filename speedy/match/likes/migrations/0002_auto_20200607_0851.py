# Generated by Django 3.0.6 on 2020-06-07 05:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('likes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userlike',
            options={'ordering': ('-date_created',), 'verbose_name': 'user like', 'verbose_name_plural': 'user likes'},
        ),
    ]
