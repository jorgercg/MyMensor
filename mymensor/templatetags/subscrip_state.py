## subscrip_state.py
from django.template import Library
from datetime import datetime
import pytz
from mymensor.models import Asset, BraintreeCustomer, BraintreeSubscription
register = Library()

@register.simple_tag
def subscrip_state(request):
    try:
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        return btsubscription.braintreesubscriptionSubscriptionStatus
    except:
        btsubscription = None
    currentAsset = Asset.objects.get(assetOwner=request.user)
    dateofendoftrialbeforesubscription = currentAsset.assetDateOfEndEfTrialBeforeSubscription
    if dateofendoftrialbeforesubscription:
        if (datetime.now(pytz.utc) < dateofendoftrialbeforesubscription):
            return "Trial"
        else:
            return "TrialExpired"
    return "Trial Period Not Set"