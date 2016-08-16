from django.shortcuts import render
from mymensor.models import Photo, AssetOwner
from mymensor.forms import AssetOwnerForm

# Portfolio View
def portfolio(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', { 'photos': photos,})

# Photo Feed View
def photofeed(request):
    photos = Photo.objects.all()
    return render(request, 'photofeed.html', { 'photos': photos,})

# Setup View
def setup(request):
    assetOwner = AssetOwner.objects.get(pk=1)
    form_class = AssetOwnerForm
    
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=assetOwner)
        if form.is_valid():
            form.save()
            return redirect('portfolio')
    else:
        form = form_class(instace=assetOwner)
    return render(request, 'setup.html', { 'assetOwner': assetOwner,
                                            'form':form,
                                        })
