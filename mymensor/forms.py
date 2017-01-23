from django.db import models
from django.forms import ModelForm
from mymensor.models import Asset

class AssetForm(ModelForm):
    class Meta:
        model = Asset
        fields = ['assetOwnerDescription', 'assetOwnerKey', 'assetRegistryCode', 'assetDciFrequencyUnit', 'assetDciFrequencyValue', 'assetDciTolerancePosition', 'assetDciToleranceRotation']
