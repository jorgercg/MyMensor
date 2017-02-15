from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Asset(models.Model):
    assetDescription = models.CharField(max_length=1024, null=True)
    assetNumber = models.IntegerField()
    assetIsActive = models.BooleanField(default=True)
    assetOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  ###### FK
    assetOwnerDescription = models.CharField(max_length=1024, null=True)
    assetOwnerKey = models.CharField(max_length=1024, null=True)
    assetRegistryCode = models.CharField(max_length=255, null=True)
    assetDciFrequencyUnit = models.CharField(max_length=50, default="millis")
    assetDciFrequencyValue = models.IntegerField(default=20000)
    assetDciQtyVps = models.IntegerField(default=31)
    assetDciTolerancePosition = models.IntegerField(default=50)
    assetDciToleranceRotation = models.IntegerField(default=10)

class MobileSetupBackup(models.Model):
    backupOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  ###### FK
    backupDescription = models.CharField(max_length=1024, null=True)
    backupName = models.CharField(max_length=255, null=True)
    backupDBTimeStamp = models.DateTimeField(auto_now_add=True)

class Vp(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)  ###### FK
    vpDescription = models.CharField(max_length=1024)
    vpNumber = models.IntegerField()
    vpIsActive = models.BooleanField(default=True)
    vpListNumber = models.IntegerField(null=True)
    vpStdPhotoStorageURL = models.CharField(max_length=255, null=True)
    vpStdTagDescPhotoStorageURL = models.CharField(max_length=255, null=True)
    vpStdMarkerPhotoStorageURL = models.CharField(max_length=255, null=True)
    vpStdPhotoFileSize = models.BigIntegerField(null=True)
    vpStdMarkerPhotoFileSize = models.BigIntegerField(null=True)
    vpXDistance = models.IntegerField(default=0)
    vpYDistance = models.IntegerField(default=0)
    vpZDistance = models.IntegerField(default=0)
    vpXRotation = models.IntegerField(default=0)
    vpYRotation = models.IntegerField(default=0)
    vpZRotation = models.IntegerField(default=0)
    vpMarkerlessMarkerWidth = models.IntegerField(default=400)
    vpMarkerlessMarkerHeigth = models.IntegerField(default=400)
    vpArIsConfigured = models.BooleanField(default=False)
    vpIsVideo = models.BooleanField(default=False)
    vpIsAmbiguos = models.BooleanField(default=False)
    vpIsSuperSingle = models.BooleanField(default=False)
    vpFlashTorchIsOn = models.BooleanField(default=False)
    vpSuperMarkerId = models.IntegerField(default=0)
    vpFrequencyUnit = models.CharField(max_length=50, null=True)
    vpFrequencyValue = models.IntegerField(null=True)


class Tag(models.Model):
    vp = models.ForeignKey(Vp, on_delete=models.CASCADE)  ###### FK
    tagDescription = models.CharField(max_length=1024)
    tagNumber = models.IntegerField()
    tagIsActive = models.BooleanField(default=True)
    tagListNumber = models.IntegerField(null=True)
    tagQuestion = models.CharField(max_length=1024)
    tagUnit = models.CharField(max_length=50, null=True)
    tagLowRed = models.FloatField(null=True)
    tagLowYellow = models.FloatField(null=True)
    tagExpValue = models.FloatField(null=True)
    tagHighYellow = models.FloatField(null=True)
    tagHighRed = models.FloatField(null=True)
    tagType = models.CharField(max_length=50, null=True)
    tagIsDependantOfMasterTagNumber = models.IntegerField(null=True)
    tagMaxLagFromMasterTagInMillis = models.BigIntegerField(null=True)
    tagMaxLagFromSlaveTagsInMillis = models.BigIntegerField(null=True)
    tagIsSetForSpecialCheck = models.BooleanField(default=False)
    tagSpecialCheckAcceptableDiscrepancy = models.FloatField(null=True)


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


class AmazonS3Message(models.Model):
    amazonSNSNotification = models.ForeignKey(AmazonSNSNotification, on_delete=None, null=True)  ###### FK
    eventVersion = models.CharField(max_length=1024, null=True)
    eventSource = models.CharField(max_length=1024, null=True)
    awsRegion = models.CharField(max_length=1024, null=True)
    eventTime = models.CharField(max_length=1024, null=True)
    eventName = models.CharField(max_length=1024, null=True)
    userIdentity_principalId = models.CharField(max_length=1024, null=True)
    requestParameters_sourceIPAddress = models.CharField(max_length=1024, null=True)
    responseElements_x_amz_request_id = models.CharField(max_length=1024, null=True)
    responseElements_x_amz_id_2 = models.CharField(max_length=1024, null=True)
    s3_s3SchemaVersion = models.CharField(max_length=1024, null=True)
    s3_configurationId = models.CharField(max_length=1024, null=True)
    s3_bucket_name = models.CharField(max_length=1024, null=True)
    s3_bucket_ownerIdentity_principalId = models.CharField(max_length=1024, null=True)
    s3_bucket_arn = models.CharField(max_length=1024, null=True)
    s3_object_key = models.CharField(max_length=1024, null=True)
    s3_object_size = models.CharField(max_length=1024, null=True)
    s3_object_eTag = models.CharField(max_length=1024, null=True)
    s3_object_versionId = models.CharField(max_length=1024, null=True)
    s3_object_sequencer = models.CharField(max_length=1024, null=True)


class Media(models.Model):
    vp = models.ForeignKey(Vp, on_delete=models.CASCADE, null=True)  ###### FK
    amazonS3Message = models.ForeignKey(AmazonS3Message, on_delete=None, null=True)  ###### FK
    mediaMillisSinceEpoch = models.BigIntegerField(null=True)
    mediaVpNumber = models.IntegerField(null=True)
    mediaAssetNumber = models.IntegerField(null=True)
    mediaObjectS3Key = models.CharField(max_length=255, null=True)
    mediaStorageURL = models.CharField(max_length=1024, null=True)
    mediaContentType = models.CharField(max_length=255, null=True)
    mediaLatitude = models.FloatField(null=True)
    mediaLongitude = models.FloatField(null=True)
    mediaAltitude = models.FloatField(null=True)
    mediaLocPrecisionInMeters = models.FloatField(null=True)
    mediaLocMethod = models.CharField(max_length=255, null=True)
    mediaLocMillis = models.BigIntegerField(null=True)
    mediaSha256 = models.CharField(max_length=1024, null=True)
    mediaLocIsCertified = models.NullBooleanField(null=True)
    mediaTimeIsCertified = models.NullBooleanField(null=True)
    mediaArIsOn = models.NullBooleanField(null=True)
    mediaDBTimeStamp = models.DateTimeField(auto_now_add=True)
    mediaTimeStamp = models.DateTimeField(auto_now=False, null=True)
    mediaMymensorAccount = models.CharField(max_length=255, null=True)
    mediaProcessed = models.NullBooleanField(null=True)
    mediaStateEvaluated = models.IntegerField(null=True)


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


class TagStatusTable(models.Model):
    processedTag = models.ForeignKey(ProcessedTag, on_delete=models.CASCADE)  ###### FK
    statusTagNumber = models.IntegerField()
    statusTagDescription = models.CharField(max_length=1024)
    statusVpNumber = models.IntegerField()
    statusVpDescription = models.CharField(max_length=1024)
    statusValValueEvaluated = models.FloatField()
    statusTagUnit = models.CharField(max_length=50, null=True)
    statusMediaTimeStamp = models.DateTimeField(auto_now=False, null=True)
    statusMediaMillisSinceEpoch = models.BigIntegerField(null=True)
    statusDBTimeStamp = models.DateTimeField(auto_now_add=True)
    statusTagStateEvaluated = models.IntegerField()
