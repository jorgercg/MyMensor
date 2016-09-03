from django.forms import modelformset_factory, inlineformset_factory
from mymensor.models import Asset


#AssetConfigurationFormSet = inlineformset_factory(AssetOwner, Asset, fields='__all__', can_delete=True)

