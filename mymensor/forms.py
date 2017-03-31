from django.db import models
from django.forms import ModelForm
from mymensor.models import Asset, User, Vp, Tag, Value
from django import forms

class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['assetDescription', 'assetOwnerDescription', 'assetOwnerKey', 'assetRegistryCode', 'assetDciFrequencyUnit', 'assetDciFrequencyValue']


class VpForm(ModelForm):

    class Meta:
        model = Vp
        fields = [ 'vpDescription', 'vpFrequencyUnit', 'vpFrequencyValue', 'vpIsSharedToTwitter']


class TagForm(ModelForm):

    class Meta:
        model = Tag
        fields = ['tagDescription', 'tagIsActive', 'tagQuestion', 'tagUnit', 'tagLowRed', 'tagLowYellow', 'tagExpValue', 'tagHighYellow', 'tagHighRed']
