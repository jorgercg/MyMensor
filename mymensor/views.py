from django.shortcuts import render
from mymensor.models import Photo, AssetOwner, Asset, Dci, Vp, Tag, MyMensorConfiguration, MyMensorConfigurationForm, AssetOwnerConfigurationForm


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
        sideForm = MyMensorConfigurationForm(request.POST, prefix='sideForm')
        assetOwnerForm = AssetOwnerConfigurationForm(request.POST, prefix='assetOwnerForm')
        if sideForm.is_valid() and assetOwnerForm.is_valid():
            assetOwner = assetOwnerForm.save(commit=False)
            assetOwner.save()
        # process the data in form.cleaned_data as required
        # ...
        # redirect to a new URL:
    else:
        sideForm = MyMensorConfigurationForm(prefix='sideForm')
        assetOwnerForm = AssetOwnerConfigurationForm(prefix='assetOwnerForm')
    return render(request, 'setup.html', {'formSide': sideForm, 'formAssetOwner': assetOwnerForm,})
