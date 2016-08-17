from __future__ import unicode_literals

from django.db import models
from django.conf import settings

class AssetOwner(models.Model):
    assetOwnerNumber = models.IntegerField()
    assetOwnerIsActive = models.BooleanField(default=True)
    assetOwnerDescription = models.CharField(max_length=1024, null=True)    
    assetOwnerLogoURL = models.CharField(max_length=255, null=True)

class Asset(models.Model):
    #assetOwner = models.ForeignKey(AssetOwner, on_delete=models.CASCADE)  ###### FK
    assetNumber = models.IntegerField()
    assetIsActive = models.BooleanField(default=True)
    assetDescription = models.CharField(max_length=1024, null=True)
    assetRegistryCode = models.CharField(max_length=255, null=True)
    assetProviderAcc = models.CharField(max_length=255, null=True)
    assetProviderAccPassword = models.CharField(max_length=255, null=True)
    assetStoragePassword = models.CharField(max_length=255, null=True)

class Dci(models.Model):
    #asset = models.ForeignKey(Asset, on_delete=models.CASCADE)  ###### FK
    dciNumber = models.IntegerField()
    dciIsActive = models.BooleanField(default=True)
    dciUserPassword = models.CharField(max_length=50, null=True)
    dciConfigPassword = models.CharField(max_length=50, null=True)
    dciFrequencyUnit = models.CharField(max_length=50)
    dciFrequencyValue = models.IntegerField()
    dciQtyVps = models.IntegerField(null=True)
    dciTolerancePosition = models.IntegerField(default=50)
    dciToleranceRotation = models.IntegerField(default=10)
    dciIMEI = models.CharField(max_length=50, null=True)
    dciModel = models.CharField(max_length=50, null=True)
    dciWifiMAC = models.CharField(max_length=50, null=True)
    dciRemotePassword = models.CharField(max_length=50, null=True)
    dciDciBoxWifiModel = models.CharField(max_length=50, null=True)
    dciDciBoxWifiSSID = models.CharField(max_length=50, null=True)
    dciDciBoxWifiPassword = models.CharField(max_length=50, null=True)
    dciDciBoxWifiAdministrator = models.CharField(max_length=50, null=True)
    
class Vp(models.Model):
    vpNumber = models.IntegerField()
    vpIsActive = models.BooleanField(default=True)
    vpListNumber = models.IntegerField(null=True)
    vpDescription = models.CharField(max_length=1024)
    #dci = models.ForeignKey(Dci, on_delete=models.CASCADE)  ###### FK
    vpStdPhotoStorageURL = models.CharField(max_length=255)
    vpStdTagDescPhotoStorageURL = models.CharField(max_length=255, null=True)
    vpStdMarkerPhotoStorageURL = models.CharField(max_length=255, null=True)
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
    vpIsAmbiguos = models.BooleanField(default=False)
    vpIsSuperSingle = models.BooleanField(default=False)
    vpIsSuperMultiple = models.BooleanField(default=False)
    vpFlashTorchIsOn = models.BooleanField(default=False)
    vpSuperIdIsSmall = models.BooleanField(default=False)
    vpSuperIdIsMedium = models.BooleanField(default=False)
    vpSuperIdIsLarge = models.BooleanField(default=False)
    vpSuperMarkerId = models.IntegerField(null=True)
    vpFrequencyUnit = models.CharField(max_length=50, null=True)
    vpFrequencyValue = models.IntegerField(null=True)
    
class Tag(models.Model):
    #vp = models.ForeignKey(Vp, on_delete=models.CASCADE)   ###### FK
    tagNumber = models.IntegerField()
    tagIsActive = models.BooleanField(default=True)
    tagDescription = models.CharField(max_length=1024)
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

class Photo(models.Model):
    photoMillisSinceEpoch = models.BigIntegerField()
    photoVpNumber = models.IntegerField()
    #vp = models.ForeignKey(Vp, on_delete=models.CASCADE)   ###### FK
    photoAssetOwnerNumber = models.IntegerField()
    photoAssetNumber = models.IntegerField()
    photoStorageURL = models.CharField(max_length=255)
    photoImageLatitude = models.FloatField()
    photoImageLongitude = models.FloatField()
    photoDBTimeStamp = models.DateTimeField(auto_now_add=True)
    photoTimeStamp = models.DateTimeField(auto_now=False)
    photoProcessed = models.NullBooleanField()    
    
class ProcessedTag(models.Model):
    #photo = models.ForeignKey(Photo, on_delete=models.CASCADE)   ###### FK
    #tag = models.ForeignKey(Tag, on_delete=models.CASCADE)   ###### FK
    valValueEvaluated = models.FloatField()
    valValueEvaluatedEntryDBTimeStamp = models.DateTimeField(auto_now_add=True)
    tagStateEvaluated = models.IntegerField()
    
class Value(models.Model):
    #processedTag = models.ForeignKey(ProcessedTag, on_delete=models.CASCADE)   ###### FK
    #processorUserId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)      ###### FK
    valValue = models.FloatField()
    valValueEntryDBTimeStamp = models.DateTimeField(auto_now_add=True)
    valEvalStatus = models.CharField(max_length=50, null=True)
    tagStateResultingFromValValueStatus = models.IntegerField()