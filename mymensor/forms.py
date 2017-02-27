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
        fields = [ 'vpDescription', 'vpFrequencyUnit', 'vpFrequencyValue']


class TagForm(ModelForm):

    vp = forms.ModelChoiceField(queryset=Vp.objects.all(), widget=forms.HiddenInput)  ###### FK
    tagDescription = forms.CharField(max_length=1024)
    tagNumber = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagIsActive = forms.BooleanField(initial=True)
    tagListNumber = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagQuestion = forms.CharField(max_length=1024, required=False)
    tagUnit = forms.CharField(max_length=50, required=False)
    tagLowRed = forms.FloatField(required=False)
    tagLowYellow = forms.FloatField(required=False)
    tagExpValue = forms.FloatField(required=False)
    tagHighYellow = forms.FloatField(required=False)
    tagHighRed = forms.FloatField(required=False)
    tagType = forms.CharField(max_length=50, widget=forms.HiddenInput, required=False)
    tagIsDependantOfMasterTagNumber = forms.IntegerField(initial=0, widget=forms.HiddenInput, required=False)
    tagMaxLagFromMasterTagInMillis = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagMaxLagFromSlaveTagsInMillis = forms.IntegerField(widget=forms.HiddenInput, required=False)
    tagIsSetForSpecialCheck = forms.BooleanField(initial=False, widget=forms.HiddenInput, required=False)
    tagSpecialCheckAcceptableDiscrepancy = forms.FloatField(initial=0, widget=forms.HiddenInput, required=False)

    class Meta:
        model = Tag
        fields = '__all__'

class ValueForm(ModelForm):
    processedTag = forms.ModelChoiceField(queryset=Tag.objects.all(), widget=forms.HiddenInput)  ###### FK
    processorUserId = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)  ###### FK
    valValue = forms.FloatField()
    valValueEntryDBTimeStamp = forms.DateTimeField(widget=forms.HiddenInput)
    valEvalStatus = forms.CharField(widget=forms.HiddenInput, required=False)
    tagStateResultingFromValValueStatus = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Value
        fields = '__all__'