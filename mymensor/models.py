from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@python_2_unicode_compatible
class Asset(models.Model):
    assetDescription = models.CharField(max_length=1024, null=True)
    assetNumber = models.IntegerField()
    assetIsActive = models.BooleanField(default=True)
    assetOwnerUserId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  ###### FK
    assetOwnerDescription = models.CharField(max_length=1024, null=True)
    assetOwnerKey = models.CharField(max_length=1024, null=True)
    assetRegistryCode = models.CharField(max_length=255, null=True)
    assetDciFrequencyUnit = models.CharField(max_length=50, default="millis")
    assetDciFrequencyValue = models.IntegerField(default=20000)
    assetDciQtyVps = models.IntegerField(default=2)
    assetDciTolerancePosition = models.IntegerField(default=50)
    assetDciToleranceRotation = models.IntegerField(default=10)

    def __str__(self):
        return self.assetDescription


@python_2_unicode_compatible
class Vp(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)  ###### FK
    vpDescription = models.CharField(max_length=1024)
    vpNumber = models.IntegerField()
    vpIsActive = models.BooleanField(default=True)
    vpListNumber = models.IntegerField(null=True)
    vpStdPhotoStorageURL = models.CharField(max_length=255)
    vpStdTagDescPhotoStorageURL = models.CharField(max_length=255, null=True)
    vpStdMarkerPhotoStorageURL = models.CharField(max_length=255, null=True)
    vpStdPhotoFileSize = models.BigIntegerField(null=True)
    vpStdMarkerPhotoFileSize = models.BigIntegerField(null=True)
    vpMarkerId = models.IntegerField(null=True)
    vpStdIdMarkerPhotoStorageURL = models.CharField(max_length=255, null=True)
    vpConfiguredMillis = models.BigIntegerField(null=True)
    vpXDistance = models.IntegerField(null=True)
    vpYDistance = models.IntegerField(null=True)
    vpZDistance = models.IntegerField(null=True)
    vpXRotation = models.IntegerField(null=True)
    vpYRotation = models.IntegerField(null=True)
    vpZRotation = models.IntegerField(null=True)
    vpMarkerlessMarkerWidth = models.IntegerField(null=True)
    vpMarkerlessMarkerHeigth = models.IntegerField(null=True)
    vpArIsConfigured = models.BooleanField(default=False)
    vpIsVideo = models.BooleanField(default=False)
    vpIsAmbiguos = models.BooleanField(default=False)
    vpIsSuperSingle = models.BooleanField(default=False)
    vpFlashTorchIsOn = models.BooleanField(default=False)
    vpSuperMarkerId = models.IntegerField(null=True)
    vpFrequencyUnit = models.CharField(max_length=50, null=True)
    vpFrequencyValue = models.IntegerField(null=True)

    def __str__(self):
        return self.vpDescription


@python_2_unicode_compatible
class Tag(models.Model):
    vp = models.ForeignKey(Vp, on_delete=models.CASCADE)  ###### FK
    tagDescription = models.CharField(max_length=1024)
    tagNumber = models.IntegerField()
    tagIsActive = models.BooleanField(default=True)
    tagListNumber = models.IntegerField(null=True)
    tagQuestion = models.CharField(max_length=1024)
    tagLowRedValue = models.FloatField(null=True)
    tagLowYellow = models.FloatField(null=True)
    tagLowGreen = models.FloatField(null=True)
    tagExpValue = models.FloatField(null=True)
    tagHighGreen = models.FloatField(null=True)
    tagHighYellow = models.FloatField(null=True)
    tagHighRed = models.FloatField(null=True)
    tagType = models.CharField(max_length=50, null=True)
    tagIsDependantOfMasterTagNumber = models.IntegerField(null=True)
    tagMaxLagFromMasterTagInMillis = models.BigIntegerField(null=True)
    tagMaxLagFromSlaveTagsInMillis = models.BigIntegerField(null=True)
    tagIsSetForSpecialCheck = models.BooleanField(default=False)
    tagSpecialCheckAcceptableDiscrepancy = models.FloatField(null=True)

    def __str__(self):
        return self.tagDescription


class Media(models.Model):
    vp = models.ForeignKey(Vp, on_delete=models.CASCADE, null=True)  ###### FK
    mediaMillisSinceEpoch = models.BigIntegerField()
    mediaVpNumber = models.IntegerField()
    mediaAssetNumber = models.IntegerField()
    mediaStorageURL = models.CharField(max_length=255)
    mediaContentType = models.CharField(max_length=255)
    mediaLatitude = models.FloatField()
    mediaLongitude = models.FloatField()
    mediaAltitude = models.FloatField()
    mediaLocPrecisionInMeters = models.FloatField()
    mediaLocMethod = models.CharField(max_length=255)
    mediaLocMillis = models.BigIntegerField()
    mediaSha256 = models.CharField(max_length=1024, null=True)
    mediaLocIsCertified = models.NullBooleanField()
    mediaTimeIsCertified = models.NullBooleanField()
    mediaArIsOn = models.NullBooleanField()
    mediaDBTimeStamp = models.DateTimeField(auto_now_add=True)
    mediaTimeStamp = models.DateTimeField(auto_now=False)
    mediaMymensorAccount = models.CharField(max_length=255)
    mediaProcessed = models.NullBooleanField()


class ProcessedTag(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)  ###### FK
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)  ###### FK
    valValueEvaluated = models.FloatField()
    valValueEvaluatedEntryDBTimeStamp = models.DateTimeField(auto_now_add=True)
    tagStateEvaluated = models.IntegerField()


class Value(models.Model):
    processedTag = models.ForeignKey(ProcessedTag, on_delete=models.CASCADE)  ###### FK
    processorUserId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  ###### FK
    valValue = models.FloatField()
    valValueEntryDBTimeStamp = models.DateTimeField(auto_now_add=True)
    valEvalStatus = models.CharField(max_length=50, null=True)
    tagStateResultingFromValValueStatus = models.IntegerField()

class AmazonSNSNotification(models.Model):
    Message = models.CharField(max_length=4096, null=True)
    MessageId = models.CharField(max_length=1024, null=True)
    Signature = models.CharField(max_length=1024, null=True)
    Subject = models.CharField(max_length=1024, null=True)
    Timestamp =  models.CharField(max_length=1024, null=True)
    TopicArn = models.CharField(max_length=1244, null=True)
    Type = models.CharField(max_length=1024, null=True)
    UnsubscribeURL = models.CharField(max_length=1024, null=True)
    SignatureVersion = models.CharField(max_length=1024, null=True)
    SubscribeURL = models.CharField(max_length=1024, null=True)
    Token = models.CharField(max_length=1024, null=True)