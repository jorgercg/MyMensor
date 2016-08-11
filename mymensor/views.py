from django.shortcuts import render
from mymensor.models import Photo

# Create your views here.
def index(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', { 'photos': photos,})