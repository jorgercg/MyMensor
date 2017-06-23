from django.forms import ModelForm
from mymensor.models import Asset, Vp, Tag, BraintreeCustomer

class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['assetDescription', 'assetOwnerDescription', 'assetDciFrequencyUnit', 'assetDciFrequencyValue']


class VpForm(ModelForm):

    class Meta:
        model = Vp
        fields = ['vpDescription', 'vpFrequencyUnit', 'vpFrequencyValue', 'vpIsSharedToTwitter', 'vpIsSharedToFacebook', 'vpShareEmail']


class TagForm(ModelForm):

    class Meta:
        model = Tag
        fields = ['tagDescription', 'tagIsActive', 'tagQuestion', 'tagUnit', 'tagLowRed', 'tagLowYellow', 'tagExpValue', 'tagHighYellow', 'tagHighRed']


class PaymentCurrencyForm(ModelForm):

    class Meta:
        model = BraintreeCustomer
        fields = ['braintreecustomerMerchantAccId']
