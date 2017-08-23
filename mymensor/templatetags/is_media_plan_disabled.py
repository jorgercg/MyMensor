from django.template import Library
from mymensor.models import Asset
register = Library()

@register.simple_tag
def is_media_plan_disabled(request):
    try:
        currentAsset = Asset.objects.get(assetOwner=request.user)
        currentuserplan = currentAsset.assetMyMensorPlan
    except:
        return
    if currentuserplan == "MyMensor Media":
        return "disabled"
    return