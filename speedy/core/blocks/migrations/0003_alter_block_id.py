# Generated by Django 3.2.8 on 2021-10-06 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0002_auto_20200507_0446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
