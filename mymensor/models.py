from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Photo(models.Model):
    photoMillisSinceEpoch = models.BigIntegerField()
    photoVpNumber = models.IntegerField()
    photoAssetOwnerNumber = models.IntegerField()
    photoAssetNumber = models.IntegerField()
    photoStorageURL = models.CharField(max_length=255)
    photoImageLatitude = models.FloatField()
    photoImageLongitude = models.FloatField()
    photoDBTimeStamp = models.DateTimeField(auto_now=True)
    photoTimeStamp = models.DateTimeField(auto_now=False)
    photoProcessed = models.NullBooleanField()


