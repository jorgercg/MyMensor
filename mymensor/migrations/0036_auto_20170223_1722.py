# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-23 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0035_auto_20170223_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processedtag',
            name='tagStateEvaluated',
            field=models.CharField(choices=[('NP', 'NOT PROCESSED'), ('PR', 'PROCESSED'), ('LR', 'LOW RED'), ('LY', 'LOW YELLOW'), ('GR', 'GREEN'), ('HY', 'HIGH YELLOW'), ('HR', 'HIGH RED')], max_length=50, verbose_name='Status'),
        ),
    ]
