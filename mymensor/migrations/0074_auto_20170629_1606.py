# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-29 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0073_braintreesubscription_braintreesubscriptionpaymthdresultobject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='braintreesubscription',
            name='braintreesubscriptionCClast4',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
