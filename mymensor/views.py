from django.shortcuts import render
from mymensor.models import Photo, AssetOwner, Asset
from mymensor.forms import AssetOwnerConfigurationFormSet, AssetConfigurationFormSet, DciConfigurationFormSet

# Portfolio View
def portfolio(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', {'photos': photos,})


# Photo Feed View
def photofeed(request):
    photos = Photo.objects.all()
    return render(request, 'photofeed.html', {'photos': photos,})


# Setup Side View
def myMensorSetupFormView(request):
    if request.method == 'POST':
        assetOwnerFormSet = AssetOwnerConfigurationFormSet(request.POST, request.FILES, prefix='assetOwnerFormSet')
        assetFormSet = AssetConfigurationFormSet(request.POST, request.FILES, prefix='assetFormSet')
        dciFormSet = DciConfigurationFormSet(request.POST, request.FILES, prefix='dciFormSet')
        if assetOwnerFormSet.is_valid() and assetFormSet.is_valid() and dciFormSet.is_valid():
            assetOwnerFormSet.save()
        # process the data in form.cleaned_data as required
        # ...
        # redirect to a new URL:
    else:
        assetOwnerFormSet = AssetOwnerConfigurationFormSet(prefix='assetOwnerFormSet')
        dciFormSet = DciConfigurationFormSet()
        assetFormSet = AssetConfigurationFormSet()
    return render(request, 'setup.html', {'formSetAssetOwner': assetOwnerFormSet, 'formSetAsset': assetFormSet, 'formSetDci':dciFormSet})
