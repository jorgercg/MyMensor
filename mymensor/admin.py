from django.contrib import admin

from mymensor.models import Photo

class PhotoAdmin(admin.ModelAdmin):
    model = Photo
    list_display = ('photoMillisSinceEpoch', 'photoVpNumber', 'photoAssetOwnerNumber', 'photoAssetNumber', 'photoStorageURL', 'photoImageLatitude', 'photoImageLongitude', 'photoDBTimeStamp', 'photoTimeStamp', 'photoProcessed',)

class VpAdmin(admin.ModelAdmin):
    model = Vp
    list_display = ('vpNumber', 'vpIsActive', 'vpDescription', 'dci', 'vpStdPhotoStorageURL',)

class DciAdmin(admin.ModelAdmin):
    model = Dci
    list_display = ('asset', 'dciNumber', 'dciIsActive', 'dciFrequencyUnit', 'dciFrequencyValue', 'dciTolerancePosition', 'dciToleranceRotation')

class AssetAdmin(admin.ModelAdmin):
    model = Asset
    list_display = ('assetOwner', 'assetNumber', 'assetIsActive',)

class AssetOwnerAdmin(admin.ModelAdmin):
    model = AssetOwner
    list_display = ('assetOwnerNumber', 'assetOwnerIsActive',)
    
# Register your models here.
admin.site.register(Photo, PhotoAdmin, Vp, VpAdmin, Dci, DciAdmin, Asset, AssetAdmin, AssetOwner, AssetOwnerAdmin,)