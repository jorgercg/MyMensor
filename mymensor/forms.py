from django.forms import modelformset_factory, inlineformset_factory
from mymensor.models import AssetOwner, Asset, Dci

AssetOwnerConfigurationFormSet = modelformset_factory(AssetOwner, fields='__all__', can_delete=True)

AssetConfigurationFormSet = inlineformset_factory(AssetOwner, Asset, fields='__all__', can_delete=True)

DciConfigurationFormSet = inlineformset_factory(Asset, Dci, fields='__all__', can_delete=True)
