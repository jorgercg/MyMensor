from django.shortcuts import render
from mymensor.models import Photo, AssetOwner, Asset, Dci, Vp, Tag, MyMensorConfiguration, MyMensorConfigurationForm

# Portfolio View
def portfolio(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', { 'photos': photos,})

# Photo Feed View
def photofeed(request):
    photos = Photo.objects.all()
    return render(request, 'photofeed.html', { 'photos': photos,})

# Setup View
def myMensorSetupSideFormView(request):
    if request.method == 'POST':
        form = MyMensorConfigurationForm(request.POST)
        #if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
    else:
        form = MyMensorConfigurationForm()
    return render(request, 'setup.html', { 'form': form,})