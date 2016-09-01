from django.forms import ModelForm
from mymensor.models import AssetOwner, Asset

class AssetConfigurationForm(ModelForm):
    class Meta:
        model = Asset
        fields = '__all__'





