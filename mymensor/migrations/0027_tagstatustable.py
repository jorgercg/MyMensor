# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-02 15:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0026_tagstatusdjango'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagStatusTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusTagNumber', models.IntegerField()),
                ('statusTagDescription', models.CharField(max_length=1024)),
                ('statusVpNumber', models.IntegerField()),
                ('statusVpDescription', models.CharField(max_length=1024)),
                ('statusValValueEvaluated', models.FloatField()),
                ('statusTagUnit', models.CharField(max_length=50, null=True)),
                ('statusMediaTimeStamp', models.DateTimeField(null=True)),
                ('statusTagStateEvaluated', models.IntegerField()),
                ('processedTag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mymensor.ProcessedTag')),
            ],
        ),
    ]
