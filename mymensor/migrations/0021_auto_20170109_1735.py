# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-09 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mymensor', '0020_auto_20170109_1223'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='assetOwnerUserId',
            new_name='assetOwner',
        ),
        migrations.RemoveField(
            model_name='vp',
            name='vpConfiguredMillis',
        ),
        migrations.RemoveField(
            model_name='vp',
            name='vpMarkerId',
        ),
        migrations.RemoveField(
            model_name='vp',
            name='vpStdIdMarkerPhotoStorageURL',
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpMarkerlessMarkerHeigth',
            field=models.IntegerField(default=400),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpMarkerlessMarkerWidth',
            field=models.IntegerField(default=400),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpStdPhotoStorageURL',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpSuperMarkerId',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpXDistance',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpXRotation',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpYDistance',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpYRotation',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpZDistance',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vp',
            name='vpZRotation',
            field=models.IntegerField(default=0),
        ),
    ]
