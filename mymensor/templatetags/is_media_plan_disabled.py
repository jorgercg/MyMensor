from django.template import Library
from mymensor.models import Asset
register = Library()

@register.simple_tag
def is_media_plan_disabled(request):
    if Asset.objects.get(assetOwner=request.user).assetMyMensorPlan == "MyMensor Media":
        return "disabled"
    return