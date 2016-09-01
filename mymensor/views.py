from django.shortcuts import render
from django.forms import modelformset_factory
from mymensor.models import Photo, AssetOwner, Asset
from mymensor.forms import AssetConfigurationForm

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
    AssetOwnerConfigurationFormSet = modelformset_factory(AssetOwner, fields='__all__', can_delete=True)
    if request.method == 'POST':
        assetOwnerFormSet = AssetOwnerConfigurationFormSet(request.POST, request.FILES, prefix='assetOwnerFormSet')
        if assetOwnerFormSet.is_valid():
            assetOwnerFormSet.save()
        # process the data in form.cleaned_data as required
        # ...
        # redirect to a new URL:
    else:
        assetOwnerFormSet = AssetOwnerConfigurationFormSet(prefix='assetOwnerFormSet')
    return render(request, 'setup.html', {'formSetAssetOwner': assetOwnerFormSet,})
