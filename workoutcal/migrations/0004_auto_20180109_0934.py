# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-09 09:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workoutcal', '0003_auto_20171231_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardioactivity',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='liftactivity',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]