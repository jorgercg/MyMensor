from django.shortcuts import render
from mymensor.models import Photo

# Portfolio View
def portfolio(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', { 'photos': photos,})

# Photo Feed View
def photofeed(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', { 'photos': photos,})

