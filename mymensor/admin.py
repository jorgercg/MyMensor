from django.contrib import admin

from mymensor.models import Photo

class PhotoAdmin(admin.ModelAdmin):
    model = Photo
    list_display = ('photoMillisSinceEpoch', 'photoVpNumber', 'photoAssetOwnerNumber', 'photoAssetNumber', 'photoStorageURL', 'photoImageLatitude', 'photoImageLongitude', 'photoDBTimeStamp', 'photoTimeStamp', 'photoProcessed',)


# Register your models here.

admin.site.register(Photo, PhotoAdmin)