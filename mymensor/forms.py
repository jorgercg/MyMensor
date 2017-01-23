from django.db import models
from django.forms import ModelForm
from mymensor.models import Asset, User, Vp
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