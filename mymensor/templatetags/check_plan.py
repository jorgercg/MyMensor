## trial_end_date.py
from django.template import Library
from mymensor.models import Asset
register = Library()

@register.simple_tag
def check_plan(request):
    currentAsset = Asset.objects.get(assetOwner=request.user)
    return currentAsset.assetMyMensorPlan
