from django.contrib import admin

from mymensor.models import AssetOwner, Asset, Dci, Vp, Photo

class AssetOwnerAdmin(admin.ModelAdmin):
    model = AssetOwner
    list_display = ('assetOwnerNumber', 'assetOwnerIsActive',)

class AssetAdmin(admin.ModelAdmin):
    model = Asset
    list_display = ('assetNumber', 'assetIsActive',)

class DciAdmin(admin.ModelAdmin):
    model = Dci
    list_display = ('dciNumber', 'dciIsActive', 'dciFrequencyUnit', 'dciFrequencyValue', 'dciTolerancePosition', 'dciToleranceRotation')

class VpAdmin(admin.ModelAdmin):
    model = Vp
    list_display = ('vpNumber', 'vpIsActive', 'vpDescription', 'vpStdPhotoStorageURL',)

class PhotoAdmin(admin.ModelAdmin):
    model = Photo
    list_display = ('photoMillisSinceEpoch', 'photoVpNumber', 'photoAssetOwnerNumber', 'photoAssetNumber', 'photoStorageURL', 'photoImageLatitude', 'photoImageLongitude', 'photoDBTimeStamp', 'photoTimeStamp', 'photoProcessed',)
    
# Register your models here.
admin.site.register(AssetOwner, AssetOwnerAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Dci, DciAdmin)
admin.site.register(Vp, VpAdmin)
admin.site.register(Photo, PhotoAdmin)