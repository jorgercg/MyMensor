# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-25 19:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0068_braintreesubscription_braintreesubscriptionresultobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='braintreesubscription',
            name='braintreesubscriptionCCexpmonth',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='braintreesubscription',
            name='braintreesubscriptionCCexpyear',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='braintreesubscription',
            name='braintreesubscriptionCClast4',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='braintreesubscription',
            name='braintreesubscriptionCCtype',
            field=models.CharField(max_length=10, null=True),
        ),
    ]