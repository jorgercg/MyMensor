## subscrip_state.py
from django.template import Library
from datetime import datetime
from mymensor.models import Asset, BraintreeCustomer, BraintreeSubscription
register = Library()

@register.simple_tag
def subscrip_state(request):
    btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
    try:
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        return btsubscription.braintreesubscriptionSubscriptionStatus
    except:
        btsubscription = None
    currentAsset = Asset.objects.get(assetOwner=request.user)
    dateofendoftrialbeforesubscription = currentAsset.assetDateOfEndEfTrialBeforeSubscription
    if dateofendoftrialbeforesubscription < datetime.utcnow():
        return "Trial"
    else:
        return "TrialExpired"