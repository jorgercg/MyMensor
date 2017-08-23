from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token

class BraintreePlan(models.Model):
    CURRENCY_CHOICES = (('USD', 'USD'), ('EUR', 'EUR'), ('BRL', 'BRL'))

    braintreeplanPlanName = models.CharField(max_length=1024)
    braintreeplanPlanId = models.CharField(max_length=1024)
    braintreeplanPlanMymensorType = models.CharField(max_length=1024, default="MEDIAANDDATA")
    braintreeplanCurrency = models.CharField(max_length=50, choices=CURRENCY_CHOICES, default='USD')
    braintreeplanBillingCycleQty = models.IntegerField()
    braintreeplanBillingCycleUnit = models.CharField(max_length=255)
    braintreeplanBillingExpirationExists = models.BooleanField(default=False)
    braintreeplanBillingExpirationInCycleQty = models.IntegerField(null=True, blank=True)
    braintreeplanDiscountExists = models.BooleanField(default=False)
    braintreeplanDiscountPercentage = models.FloatField(null=True, blank=True)

class BraintreeMerchant(models.Model):
    CURRENCY_CHOICES = (('USD', 'USD'), ('EUR', 'EUR'), ('BRL', 'BRL'))

    braintreemerchMerchId = models.CharField(max_length=1024, null=True)
    braintreemerchCurrency = models.CharField(max_length=50, choices=CURRENCY_CHOICES)

class BraintreePrice(models.Model):
    braintrepricePrice = models.FloatField()
    braintreeplan = models.ForeignKey(BraintreePlan,on_delete=None)
    braintreemerchant = models.ForeignKey(BraintreeMerchant, on_delete=None)

class BraintreeCustomer(models.Model):
    braintreecustomerOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  ###### FK
    braintreecustomerCustomerId = models.CharField(max_length=1024, null=True)
    braintreecustomerPaymentMethodNonce = models.CharField(max_length=1024, null=True)
    braintreecustomerPaymentMethodToken = models.CharField(max_length=1024, null=True)
    braintreecustomerCustomerCreated = models.NullBooleanField(null=True)
    braintreecustomerCustomerCreatedDate = models.DateTimeField(auto_now=False, null=True)

class BraintreeSubscription(models.Model):
    braintreesubscriptionSubscriptionId = models.CharField(max_length=1024, null=True)
    braintreesubscriptionSubscriptionStatus = models.CharField(max_length=50, null=True)
    braintreesubscriptionPaymentInstrumentType = models.CharField(max_length=50, null=True)
    braintreesubscriptionPaymentImageURL = models.CharField(max_length=1024, null=True)
    braintreesubscriptionPayMthdResultObject = models.TextField(null=True)
    braintreesubscriptionResultObject = models.TextField(null=True)
    braintreesubscriptionCancelResultObject = models.TextField(null=True)
    braintreesubscriptionCClast4 = models.CharField(max_length=50, null=True)
    braintreesubscriptionCCtype = models.CharField(max_length=10, null=True)
    braintreesubscriptionCCexpyear = models.CharField(max_length=10, null=True)
    braintreesubscriptionCCexpmonth = models.CharField(max_length=10, null=True)
    braintreesubscriptionPayPalBillingAgreementId = models.CharField(max_length=1024, null=True)
    braintreesubscriptionPayPalEmail = models.CharField(max_length=1024, null=True)
    braintreesubscriptionLastDay = models.DateTimeField(auto_now=False, null=True)
    braintreesubscriptionDBTimeStamp = models.DateTimeField(auto_now=True, null=True)
    braintreecustomer = models.ForeignKey(BraintreeCustomer, on_delete=models.CASCADE)
    braintreeprice = models.ForeignKey(BraintreePrice, on_delete=None)


class Asset(models.Model):
    FREQ_UNIT_CHOICES = (('millis', 'millis'), ('hour', 'hour'), ('day', 'day'), ('week', 'week'), ('month', 'month'),)
    MYM_PLAN_CHOICES = (('MyMensor Media', 'MyMensor Media'), ('MyMensor Media and Data', 'MyMensor Media and Data'),)

    assetDescription = models.CharField(max_length=1024, null=True, verbose_name=_('Asset Description'))
    assetNumber = models.IntegerField(verbose_name="Asset Number")
    assetIsActive = models.BooleanField(default=True, verbose_name="Asset is active")
    assetOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1,
                                   verbose_name="Asset Owner")  ###### FK
    assetOwnerDescription = models.CharField(max_length=1024, null=True, verbose_name=_('Asset Owner Description'))
    assetOwnerKey = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Asset Owner Key")
    assetOwnerIdentityId = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Asset Owner Identity Id")
    assetRegistryCode = models.CharField(max_length=255, null=True, blank=True, verbose_name="Asset Registry code")
    assetDateOfEndEfTrialBeforeSubscription = models.DateTimeField(auto_now=False, null=True, verbose_name="End of Trial Befor Subscription")
    assetMyMensorPlan = models.CharField(max_length=50, choices=MYM_PLAN_CHOICES, default="MyMensor Media and Data", verbose_name=_('MyMensor Plan'))
    assetDciFrequencyUnit = models.CharField(max_length=50, choices=FREQ_UNIT_CHOICES, default="millis", verbose_name=_('Capture frequency unit'))
    assetDciFrequencyValue = models.IntegerField(default=20000, verbose_name=_('Minimum capture frequency value'))
    assetDciQtyVps = models.IntegerField(default=31, verbose_name="Quantity of Vps in Asset")
    assetDciTolerancePosition = models.IntegerField(default=50, verbose_name="Position tolerance for capture")
    assetDciToleranceRotation = models.IntegerField(default=10, verbose_name="Rotation tolerance for capture")
    assetDciClientSoftwareType = models.CharField(max_length=255, null=True, blank=True, verbose_name="Client Software Type")


class MobileClientInstall(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)  ###### FK
    mobileClientInstallGUID = models.CharField(max_length=1024, null=True, blank=True)
    mobileClientInstallCreationTimeStamp = models.DateTimeField(auto_now=False, null=True)
    mobileClientInstallOrderNumber = models.IntegerField(null=True)
    mobileClientInstallLastAccessTimeStamp = models.DateTimeField(auto_now=False, null=True)


class MobileOnlyUser(models.Model):
    mobileOnlyUserOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name="Mobile Only User")
    mobileOnlyUserPrefix = models.CharField(max_length=50, null=True, verbose_name=_('Mobile Only User Prefix'))
    mobileOnlyUserAuthUserId = models.IntegerField(null=True)


class MobileSetupBackup(models.Model):
    backupOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  ###### FK
    backupDescription = models.CharField(max_length=1024, null=True)
    backupName = models.CharField(max_length=255, null=True)
    backupDBTimeStamp = models.DateTimeField(auto_now=True)


class TwitterAccount(models.Model):
    twtOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1,
                                 verbose_name="Twitter Owner")  ###### FK
    twtAccessTokenKey = models.CharField(max_length=1024, null=True, verbose_name="Twitter Auth Access Token Key")
    twtAccessTokenSecret = models.CharField(max_length=1024, null=True, verbose_name="Twitter Auth Access Token Secret")


class FacebookAccount(models.Model):
    fbOwner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1,
                                verbose_name="Facebook Owner")  ###### FK
    fbUserId = models.CharField(max_length=1024, null=True, verbose_name="Facebook User ID")
    fbUserName = models.CharField(max_length=1024, null=True, verbose_name="Facebook User Name")
    fbShortTermAccesToken = models.CharField(max_length=2048, null=True,
                                             verbose_name="Facebook Short Term Access Token")
    fbShortTermAccesTokenSignedRequest = models.CharField(max_length=2048, null=True,
                                                          verbose_name="Facebook Short Term Access Token Signed Request")
    fbLongTermAccesToken = models.CharField(max_length=2048, null=True, verbose_name="Facebook Short Term Access Token")
    fbLongTermAccesTokenIssuedAt = models.DateTimeField(auto_now=False, null=True,
                                                        verbose_name="Facebook Short Term Access Token Issue Time")
    fbLongTermAccesTokenExpiresIn = models.CharField(max_length=255, null=True,
                                                     verbose_name="Facebook Long Term Access Token Expires In Seconds")


class Vp(models.Model):
    FREQ_UNIT_CHOICES = (('millis', 'millis'), ('hour', 'hour'), ('day', 'day'), ('week', 'week'), ('month', 'month'),)

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)  ###### FK
    vpDescription = models.CharField(max_length=1024, verbose_name=_('vp description'))
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
    vpFrequencyUnit = models.CharField(max_length=50, choices=FREQ_UNIT_CHOICES, null=True,
                                       verbose_name=_('unit for the vp capture frequency'))
    vpFrequencyValue = models.IntegerField(null=True, verbose_name=_('minimum vp capture frequency'))
    vpIsUsed = models.BooleanField(default=False)
    vpIsSharedToTwitter = models.BooleanField(default=False, verbose_name=_(
        'share all of this vp captures to the Twitter Account configured.'))
    vpIsSharedToFacebook = models.BooleanField(default=False, verbose_name=_(
        'share all of this vp captures to the Facebook Account configured.'))
    vpShareEmail = models.EmailField(null=True, blank=True,
                                     verbose_name=_('send all of this vp captures to the following email.'))


class Tag(models.Model):
    vp = models.ForeignKey(Vp, on_delete=models.CASCADE)  ###### FK
    tagDescription = models.CharField(max_length=1024, verbose_name=_('tag description'))
    tagNumber = models.IntegerField()
    tagIsActive = models.BooleanField(default=True, verbose_name=_('tag is active'))
    tagListNumber = models.IntegerField(null=True)
    tagQuestion = models.CharField(max_length=1024,
                                   verbose_name=_('question that shall be answered when processing this tag'))
    tagUnit = models.CharField(max_length=50, null=True, verbose_name=_('unit to be used when processing this tag'))
    tagLowRed = models.FloatField(null=True, blank=True, verbose_name=_(
        'minimum value from which the tag will be flagged as in LOW RED state'))
    tagLowYellow = models.FloatField(null=True, blank=True, verbose_name=_(
        'minimum value from which the tag will be flagged as in LOW YELLOW state'))
    tagExpValue = models.FloatField(null=True, blank=True, verbose_name=_('expected value for the tag'))
    tagHighYellow = models.FloatField(null=True, blank=True, verbose_name=_(
        'maximum value from which the tag will be flagged as in HIGH YELLOW state'))
    tagHighRed = models.FloatField(null=True, blank=True, verbose_name=_(
        'maximum value from which the tag will be flagged as in HIGH RED state'))
    tagType = models.CharField(max_length=50, null=True)
    tagIsDependantOfMasterTagNumber = models.IntegerField(null=True)
    tagMaxLagFromMasterTagInMillis = models.BigIntegerField(null=True)
    tagMaxLagFromSlaveTagsInMillis = models.BigIntegerField(null=True)
    tagIsSetForSpecialCheck = models.BooleanField(default=False)
    tagSpecialCheckAcceptableDiscrepancy = models.FloatField(null=True)


class Tagbbox(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)  ###### FK
    tagbboxType = models.CharField(max_length=50, default="rect")
    tagbboxX = models.FloatField(null=True)
    tagbboxY = models.FloatField(null=True)
    tagbboxWidth = models.FloatField(null=True)
    tagbboxHeight = models.FloatField(null=True)
    tagbboxStroke = models.CharField(max_length=50, default="#000")
    tagbboxStrokeWidth = models.IntegerField(default=2)
    tagbboxFill = models.CharField(max_length=50, default="none")


class AmazonSNSNotification(models.Model):
    Message = models.CharField(max_length=4096, null=True)
    MessageId = models.CharField(max_length=1024, null=True)
    Signature = models.CharField(max_length=1024, null=True)
    Subject = models.CharField(max_length=1024, null=True)
    Timestamp = models.CharField(max_length=1024, null=True)
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
    TAG_STATUS_CHOICES = (
        ('NP', 'NOT PROCESSED'), ('PR', 'PROCESSED'), ('LR', 'LOW RED'), ('LY', 'LOW YELLOW'), ('GR', 'GREEN'),
        ('HY', 'HIGH YELLOW'), ('HR', 'HIGH RED'),)

    vp = models.ForeignKey(Vp, on_delete=models.CASCADE, null=True)  ###### FK
    amazonS3Message = models.ForeignKey(AmazonS3Message, on_delete=None, null=True)  ###### FK
    mediaMillisSinceEpoch = models.BigIntegerField(null=True)
    mediaVpNumber = models.IntegerField(null=True)
    mediaAssetNumber = models.IntegerField(null=True)
    mediaObjectS3Key = models.CharField(max_length=255, null=True)
    mediaStorageURL = models.CharField(max_length=1024, null=True)
    mediaThumbnailStorageURL = models.CharField(max_length=1024, null=True)
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
    mediaDBTimeStamp = models.DateTimeField(auto_now=True)
    mediaTimeStamp = models.DateTimeField(auto_now=False, null=True)
    mediaMymensorAccount = models.CharField(max_length=255, null=True)
    mediaRemark = models.CharField(max_length=1000, null=True)
    mediaProcessed = models.NullBooleanField(null=True)
    mediaStateEvaluated = models.CharField(max_length=50, choices=TAG_STATUS_CHOICES, null=True)
    mediaOriginalMymensorAccount = models.CharField(max_length=255, null=True)
    mediaDeviceId = models.CharField(max_length=255, null=True)
    mediaClientType = models.CharField(max_length=255, null=True)


class ProcessedTag(models.Model):
    TAG_STATUS_CHOICES = (
        ('NP', 'NOT PROCESSED'), ('PR', 'PROCESSED'), ('LR', 'LOW RED'), ('LY', 'LOW YELLOW'), ('GR', 'GREEN'),
        ('HY', 'HIGH YELLOW'), ('HR', 'HIGH RED'),)

    media = models.ForeignKey(Media, on_delete=models.CASCADE)  ###### FK
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)  ###### FK
    valValueEvaluated = models.FloatField()
    valValueEvaluatedEntryDBTimeStamp = models.DateTimeField(auto_now=True)
    tagStateEvaluated = models.CharField(max_length=50, choices=TAG_STATUS_CHOICES)


class Value(models.Model):
    TAG_STATUS_CHOICES = (
        ('NP', 'NOT PROCESSED'), ('PR', 'PROCESSED'), ('LR', 'LOW RED'), ('LY', 'LOW YELLOW'), ('GR', 'GREEN'),
        ('HY', 'HIGH YELLOW'), ('HR', 'HIGH RED'),)

    processedTag = models.ForeignKey(ProcessedTag, on_delete=models.CASCADE)  ###### FK
    processorUserId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  ###### FK
    valValue = models.FloatField()
    valValueEntryDBTimeStamp = models.DateTimeField(auto_now=True)
    valEvalStatus = models.CharField(max_length=50, null=True)
    tagStateResultingFromValValueStatus = models.CharField(max_length=50, choices=TAG_STATUS_CHOICES)


class TagStatusTable(models.Model):
    TAG_STATUS_CHOICES = (
        ('NP', _('NOT PROCESSED')), ('PR', _('PROCESSED')), ('LR', _('LOW RED')), ('LY', _('LOW YELLOW')),
        ('GR', _('GREEN')),
        ('HY', _('HIGH YELLOW')), ('HR', _('HIGH RED')),)

    processedTag = models.ForeignKey(ProcessedTag, on_delete=models.CASCADE)  ###### FK
    statusTagNumber = models.IntegerField(verbose_name=_('Tag#'))
    statusTagDescription = models.CharField(max_length=1024, verbose_name=_('Tag Description'))
    statusVpNumber = models.IntegerField(verbose_name=_('VP#'))
    statusVpDescription = models.CharField(max_length=1024, verbose_name=_('VP Description'))
    statusValValueEvaluated = models.FloatField(verbose_name=_('Value'))
    statusTagUnit = models.CharField(max_length=50, null=True, verbose_name=_('Unit'))
    statusMediaTimeStamp = models.DateTimeField(auto_now=False, null=True, verbose_name=_('Media Time'))
    statusMediaMillisSinceEpoch = models.BigIntegerField(null=True)
    statusDBTimeStamp = models.DateTimeField(auto_now=True, verbose_name=_('Processing Time'))
    statusTagStateEvaluated = models.CharField(max_length=50, choices=TAG_STATUS_CHOICES, verbose_name=_('Status'))
