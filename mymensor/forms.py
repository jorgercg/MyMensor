from django.forms import ModelForm, widgets, TextInput
from mymensor.models import Asset, Vp, Tag, BraintreeCustomer
from registration.forms import RegistrationForm

class MyMensorRegistrationForm(RegistrationForm):

    class Meta:
        widgets = {
            'username': TextInput(attrs={'autocapitalize':'off'}),
        }

class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['assetDescription', 'assetOwnerDescription', 'assetDciFrequencyUnit', 'assetDciFrequencyValue']


class VpForm(ModelForm):

    class Meta:
        model = Vp
        fields = ['vpDescription', 'vpFrequencyUnit', 'vpFrequencyValue', 'vpIsSharedToTwitter', 'vpShareEmail']


class TagForm(ModelForm):

    class Meta:
        model = Tag
        fields = ['tagDescription', 'tagIsActive', 'tagQuestion', 'tagUnit', 'tagLowRed', 'tagLowYellow', 'tagExpValue', 'tagHighYellow', 'tagHighRed']