# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-31 21:55
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workoutcal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='workout',
            name='cardio',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]