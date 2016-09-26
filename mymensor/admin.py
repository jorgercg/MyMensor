from django.contrib import admin

from mymensor.models import Asset, Vp, Photo, Tag, ProcessedTag, Value



class AssetAdmin(admin.ModelAdmin):
    model = Asset
    list_display = ('assetDescription', 'assetOwnerDescription', 'assetNumber', 'assetIsActive',)

class VpAdmin(admin.ModelAdmin):
    model = Vp
    list_display = ('asset', 'vpNumber', 'vpIsActive', 'vpDescription', 'vpStdPhotoStorageURL',)

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('vp', 'tagNumber', 'tagIsActive', 'tagListNumber', 'tagDescription' )    

class PhotoAdmin(admin.ModelAdmin):
    model = Photo
    list_display = ('vp', 'photoMillisSinceEpoch', 'photoVpNumber', 'photoAssetNumber', 'photoStorageURL', 'photoImageLatitude', 'photoImageLongitude', 'photoDBTimeStamp', 'photoTimeStamp', 'photoProcessed' )

class ProcesedTagAdmin(admin.ModelAdmin):
    model = ProcessedTag
    list_display = ( 'photo', 'tag', 'valValueEvaluated', 'valValueEvaluatedEntryDBTimeStamp', 'tagStateEvaluated' )

class ValueAdmin(admin.ModelAdmin):
    model = Value
    list_display = ('processedTag', 'processorUserId', 'valValue', 'valValueEntryDBTimeStamp', 'valEvalStatus', 'tagStateResultingFromValValueStatus')


# Register your models here.
admin.site.register(Asset, AssetAdmin)
admin.site.register(Vp, VpAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(ProcessedTag, ProcesedTagAdmin)
admin.site.register(Value, ValueAdmin)