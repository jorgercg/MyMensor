from django.db import models
from django.forms import ModelForm
from mymensor.models import Asset, User, Vp, Tag, Value
from django import forms

class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['assetDescription', 'assetOwnerDescription', 'assetOwnerKey', 'assetRegistryCode', 'assetDciFrequencyUnit', 'assetDciFrequencyValue']


class VpForm(ModelForm):

    FREQ_UNIT_CHOICES = (('millis', 'millis'), ('hour', 'hour'), ('day', 'day'), ('week', 'week'), ('month', 'month'),)

    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), widget=forms.HiddenInput)  ###### FK
    vpDescription = forms.CharField(max_length=1024)
    vpNumber = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpIsActive = forms.BooleanField(widget=forms.HiddenInput, required=False)
    vpListNumber = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpStdPhotoStorageURL = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)
    vpStdTagDescPhotoStorageURL = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)
    vpStdMarkerPhotoStorageURL = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)
    vpStdPhotoFileSize = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpStdMarkerPhotoFileSize = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpXDistance = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpYDistance = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpZDistance = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpXRotation = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpYRotation = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpZRotation = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpMarkerlessMarkerWidth = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpMarkerlessMarkerHeigth = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpArIsConfigured = forms.BooleanField(widget=forms.HiddenInput, required=False)
    vpIsVideo = forms.BooleanField(widget=forms.HiddenInput, required=False)
    vpIsAmbiguos = forms.BooleanField(widget=forms.HiddenInput, required=False)
    vpIsSuperSingle = forms.BooleanField(widget=forms.HiddenInput, required=False)
    vpFlashTorchIsOn = forms.BooleanField(widget=forms.HiddenInput, required=False)
    vpSuperMarkerId = forms.IntegerField(widget=forms.HiddenInput, required=False)
    vpFrequencyUnit = forms.CharField(widget=forms.Select(choices=FREQ_UNIT_CHOICES))
    vpFrequencyValue = forms.IntegerField()

    class Meta:
        model = Vp
        fields = '__all__'


class TagForm(ModelForm):

    vp = forms.ModelChoiceField(queryset=Vp.objects.all(), widget=forms.HiddenInput)  ###### FK
    tagDescription = forms.CharField(max_length=1024)
    tagNumber = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagIsActive = forms.BooleanField(initial=True)
    tagListNumber = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagQuestion = forms.CharField(max_length=1024, required=False)
    tagUnit = forms.CharField(max_length=50, required=False)
    tagLowRed = forms.FloatField(required=False)
    tagLowYellow = forms.FloatField(required=False)
    tagExpValue = forms.FloatField(required=False)
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

class ValueForm(ModelForm):
    processedTag = forms.ModelChoiceField(queryset=Tag.objects.all(), widget=forms.HiddenInput)  ###### FK
    processorUserId = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)  ###### FK
    valValue = forms.FloatField()
    valValueEntryDBTimeStamp = forms.DateTimeField(widget=forms.HiddenInput)
    valEvalStatus = forms.CharField(widget=forms.HiddenInput, required=False)
    tagStateResultingFromValValueStatus = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Value
        fields = '__all__'