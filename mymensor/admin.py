from django.contrib import admin

from mymensor.models import Asset, Vp, Media, Tag, ProcessedTag, Value, BraintreePlan, BraintreeMerchant, BraintreePrice


class AssetAdmin(admin.ModelAdmin):
    model = Asset
    list_display = ('assetDescription', 'assetOwnerDescription', 'assetNumber', 'assetIsActive', 'assetDateOfEndEfTrialBeforeSubscription')


class VpAdmin(admin.ModelAdmin):
    model = Vp
    list_display = ('asset', 'vpNumber', 'vpIsActive', 'vpDescription', 'vpStdPhotoStorageURL',)


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('vp', 'tagNumber', 'tagIsActive', 'tagListNumber', 'tagDescription')


class MediaAdmin(admin.ModelAdmin):
    model = Media
    list_display = (
        'vp', 'mediaMillisSinceEpoch', 'mediaVpNumber', 'mediaAssetNumber', 'mediaStorageURL', 'mediaLatitude',
        'mediaLongitude', 'mediaDBTimeStamp', 'mediaTimeStamp', 'mediaProcessed')


class ProcesedTagAdmin(admin.ModelAdmin):
    model = ProcessedTag
    list_display = ('media', 'tag', 'valValueEvaluated', 'valValueEvaluatedEntryDBTimeStamp', 'tagStateEvaluated')


class ValueAdmin(admin.ModelAdmin):
    model = Value
    list_display = ('processedTag', 'processorUserId', 'valValue', 'valValueEntryDBTimeStamp', 'valEvalStatus',
                    'tagStateResultingFromValValueStatus')


class BraintreePlanAdmin(admin.ModelAdmin):
    model = BraintreePlan
    list_display = (
        'braintreeplanPlanName', 'braintreeplanPlanId', 'braintreeplanBillingCycleQty', 'braintreeplanBillingCycleUnit',
        'braintreeplanBillingExpirationExists',
        'braintreeplanBillingExpirationInCycleQty', 'braintreeplanDiscountExists', 'braintreeplanDiscountPercentage')


class BraintreeMerchantAdmin(admin.ModelAdmin):
    model = BraintreeMerchant
    list_display = (
        'braintreemerchMerchId', 'braintreemerchCurrency')


class BraintreePriceAdmin(admin.ModelAdmin):
    model = BraintreePrice
    list_display = (
        'braintrepricePrice', 'braintreeplan', 'braintreemerchant')


# Register your models here.
admin.site.register(Asset, AssetAdmin)
admin.site.register(Vp, VpAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(ProcessedTag, ProcesedTagAdmin)
admin.site.register(Value, ValueAdmin)
admin.site.register(BraintreePlan, BraintreePlanAdmin)
admin.site.register(BraintreeMerchant, BraintreeMerchantAdmin)
admin.site.register(BraintreePrice, BraintreePriceAdmin)