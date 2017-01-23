from django.db import models
from django.forms import ModelForm, BaseModelFormSet
from mymensor.models import Asset

class AssetForm(ModelForm):
    class Meta:
        model = Asset
        fields = ['assetOwnerDescription', 'assetOwnerKey', 'assetRegistryCode', 'assetDciFrequencyUnit', 'assetDciFrequencyValue', 'assetDciTolerancePosition', 'assetDciToleranceRotation']

class BaseAssetFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BaseAssetFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        self.forms = []
        for i in xrange(self.total_form_count()):
            self.forms.append(self._construct_form(i, assetOwner=self.user))