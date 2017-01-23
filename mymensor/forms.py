from django.db import models
from django.forms import ModelForm
from mymensor.models import Asset, User
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
