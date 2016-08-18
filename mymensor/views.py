import pprint

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext

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
    if request.method == 'POST':
        form = AssetOwnerForm(request.POST)
    else:
        if request.GET:
            form = AssetOwnerForm(initial=request.GET)
        else:
            form = AssetOwnerForm()

    raw_post = ''
    cleaned_data = ''
    if request.POST:
        raw_post = pprint.pformat(dict(request.POST))
        if form.is_valid():
            cleaned_data = pprint.pformat(getattr(form, 'cleaned_data', ''))

    context = {
        'cleaned_data': cleaned_data,
        'form': form,
        'raw_post': raw_post
    }
    return render_to_response('setup.html', context, context_instance=RequestContext(request))

