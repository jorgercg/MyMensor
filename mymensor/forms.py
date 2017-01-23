from django.db import models
from django.forms import ModelForm, BaseModelFormSet
from mymensor.models import Asset

class AssetForm(ModelForm):
    class Meta:
        model = Asset
        fields = ['assetOwnerDescription', 'assetOwnerKey', 'assetRegistryCode', 'assetDciFrequencyUnit', 'assetDciFrequencyValue', 'assetDciTolerancePosition', 'assetDciToleranceRotation']

class BaseAssetFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseAssetFormSet, self).__init__(*args, **kwargs)