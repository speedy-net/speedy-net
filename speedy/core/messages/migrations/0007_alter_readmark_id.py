# Generated by Django 3.2.8 on 2021-10-06 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_messages', '0006_auto_20201205_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readmark',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]