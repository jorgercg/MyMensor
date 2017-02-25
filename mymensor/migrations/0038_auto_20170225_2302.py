# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-25 23:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0037_auto_20170225_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='mediaStateEvaluated',
            field=models.CharField(choices=[('NP', 'NOT PROCESSED'), ('PR', 'PROCESSED'), ('LR', 'LOW RED'), ('LY', 'LOW YELLOW'), ('GR', 'GREEN'), ('HY', 'HIGH YELLOW'), ('HR', 'HIGH RED')], max_length=50, null=True),
        ),
    ]