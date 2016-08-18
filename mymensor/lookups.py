from __future__ import unicode_literals

from selectable.base import ModelLookup
from selectable.registry import registry

from mymensor.models import AssetOwner

class AssetOwnerLookup(ModelLookup):
    model = AssetOwner
    search_fields = ('assetOwnerDescription__icontains', )
    
registry.register(AssetOwnerLookup)