from django.db import models
from django.forms import ModelForm
from mymensor.models import Asset, User, Vp, Tag
from django import forms

class AssetForm(ModelForm):

    FREQ_UNIT_CHOICES = (('millis','millis'),('hour','hour'), ('day','day'), ('week','week') , ('month','month'),)

    assetDescription = forms.CharField(max_length=1024)
    assetNumber = forms.IntegerField(widget=forms.HiddenInput)
    assetIsActive = forms.BooleanField(widget=forms.HiddenInput)
    assetOwner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)  ###### FK
    assetOwnerDescription = forms.CharField(max_length=1024)
    assetOwnerKey = forms.CharField(max_length=1024)
    assetRegistryCode = forms.CharField(max_length=255)
    assetDciFrequencyUnit = forms.CharField(widget=forms.Select(choices=FREQ_UNIT_CHOICES))
    assetDciFrequencyValue = forms.IntegerField()
    assetDciQtyVps = forms.IntegerField(widget=forms.HiddenInput)
    assetDciTolerancePosition = forms.IntegerField()
    assetDciToleranceRotation = forms.IntegerField()

    class Meta:
        model = Asset
        fields = '__all__'


class VpForm(ModelForm):

    FREQ_UNIT_CHOICES = (('millis', 'millis'), ('hour', 'hour'), ('day', 'day'), ('week', 'week'), ('month', 'month'),)

    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), widget=forms.HiddenInput)  ###### FK
    vpDescription = forms.CharField(max_length=1024)
    vpNumber = forms.IntegerField(widget=forms.HiddenInput)
    vpIsActive = forms.BooleanField(widget=forms.HiddenInput)
    vpListNumber = forms.IntegerField(widget=forms.HiddenInput)
    vpStdPhotoStorageURL = forms.CharField(max_length=255, widget=forms.HiddenInput)
    vpStdTagDescPhotoStorageURL = forms.CharField(max_length=255, widget=forms.HiddenInput)
    vpStdMarkerPhotoStorageURL = forms.CharField(max_length=255, widget=forms.HiddenInput)
    vpStdPhotoFileSize = forms.IntegerField(widget=forms.HiddenInput)
    vpStdMarkerPhotoFileSize = forms.IntegerField(widget=forms.HiddenInput)
    vpXDistance = forms.IntegerField(widget=forms.HiddenInput)
    vpYDistance = forms.IntegerField(widget=forms.HiddenInput)
    vpZDistance = forms.IntegerField(widget=forms.HiddenInput)
    vpXRotation = forms.IntegerField(widget=forms.HiddenInput)
    vpYRotation = forms.IntegerField(widget=forms.HiddenInput)
    vpZRotation = forms.IntegerField(widget=forms.HiddenInput)
    vpMarkerlessMarkerWidth = forms.IntegerField(widget=forms.HiddenInput)
    vpMarkerlessMarkerHeigth = forms.IntegerField(widget=forms.HiddenInput)
    vpArIsConfigured = forms.BooleanField(widget=forms.HiddenInput)
    vpIsVideo = forms.BooleanField(widget=forms.HiddenInput)
    vpIsAmbiguos = forms.BooleanField(widget=forms.HiddenInput)
    vpIsSuperSingle = forms.BooleanField(widget=forms.HiddenInput)
    vpFlashTorchIsOn = forms.BooleanField(widget=forms.HiddenInput)
    vpSuperMarkerId = forms.IntegerField(widget=forms.HiddenInput)
    vpFrequencyUnit = forms.CharField(widget=forms.Select(choices=FREQ_UNIT_CHOICES))
    vpFrequencyValue = forms.IntegerField()

    class Meta:
        model = Vp
        fields = '__all__'


class TagForm(ModelForm):

    vp = forms.ModelChoiceField(queryset=Vp.objects.all(), widget=forms.HiddenInput)  ###### FK
    tagDescription = forms.CharField(max_length=1024)
    tagNumber = forms.IntegerField()
    tagIsActive = forms.BooleanField(initial=True)
    tagListNumber = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagQuestion = forms.CharField(max_length=1024, required=False)
    tagLowRedValue = forms.FloatField(required=False)
    tagLowYellow = forms.FloatField(required=False)
    tagLowGreen = forms.FloatField(required=False)
    tagExpValue = forms.FloatField(required=False)
    tagHighGreen = forms.FloatField(required=False)
    tagHighYellow = forms.FloatField(required=False)
    tagHighRed = forms.FloatField(required=False)
    tagType = forms.CharField(max_length=50, widget=forms.HiddenInput, required=False)
    tagIsDependantOfMasterTagNumber = forms.IntegerField(initial=0, widget=forms.HiddenInput, required=False)
    tagMaxLagFromMasterTagInMillis = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagMaxLagFromSlaveTagsInMillis = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagIsSetForSpecialCheck = forms.BooleanField(initial=False, widget=forms.HiddenInput, required=False)
    tagSpecialCheckAcceptableDiscrepancy = forms.FloatField(initial=0, widget=forms.HiddenInput, required=False)

    class Meta:
        model = Tag
        fields = '__all__'

