# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-29 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0074_auto_20170629_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='braintreesubscription',
            name='braintreesubscriptionCancelResultObject',
            field=models.CharField(max_length=65535, null=True),
        ),
        migrations.AlterField(
            model_name='braintreesubscription',
            name='braintreesubscriptionResultObject',
            field=models.CharField(max_length=65535, null=True),
        ),
    ]