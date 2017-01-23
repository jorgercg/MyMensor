from django.db import models
from django.forms import ModelForm
from mymensor.models import Asset
from django import forms

class AssetForm(ModelForm):

    FREQ_UNIT_CHOICES = ( 'millis', 'hour', 'day', 'week', 'month')

    assetDescription = forms.CharField(max_length=1024)
    assetNumber = forms.IntegerField(widget=forms.HiddenInput)
    assetIsActive = forms.BooleanField(default=True)
    assetOwner = forms.IntegerField(widget=forms.HiddenInput)  ###### FK
    assetOwnerDescription = forms.CharField(max_length=1024)
    assetOwnerKey = forms.CharField(max_length=1024)
    assetRegistryCode = forms.CharField(max_length=255)
    assetDciFrequencyUnit = forms.CharField(widget=forms.Select(choices=FREQ_UNIT_CHOICES), default="millis")
    assetDciFrequencyValue = forms.IntegerField(default=20000)
    assetDciQtyVps = forms.IntegerField(widget=forms.HiddenInput)
    assetDciTolerancePosition = forms.IntegerField(default=50)
    assetDciToleranceRotation = forms.IntegerField(default=10)

    class Meta:
        model = Asset

