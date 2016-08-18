from django import forms

from selectable.forms import AutoCompleteWidget

from mymensor.lookups import AssetOwnerLookup

class AssetOwnerForm(forms.Form):
    autocomplete = forms.CharField(
        label='AssetOwnerDescription (AutoCompleteWidget)',
        widget=AutoCompleteWidget(AssetOwnerLookup),
        required=False,
    )