# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-23 18:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0087_asset_assetmymensorplan'),
    ]

    operations = [
        migrations.AddField(
            model_name='braintreeplan',
            name='braintreeplanCurrency',
            field=models.CharField(choices=[('USD', 'USD'), ('EUR', 'EUR'), ('BRL', 'BRL')], default='USD', max_length=50),
        ),
        migrations.AddField(
            model_name='braintreeplan',
            name='braintreeplanPlanMymensorType',
            field=models.CharField(default='MEDIAANDDATA', max_length=1024),
        ),
    ]
