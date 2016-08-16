from django.forms import ModelForm
from mymensor.models import AssetOwner

class AssetOwnerForm(ModelForm):
    class Meta:
        model = AssetOwner
        fields = ('assetOwnerNumber','assetOwnerIsActive','assetOwnerDescription','assetOwnerLogoURL',)