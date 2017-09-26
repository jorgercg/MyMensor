## subscrip_state.py
from django.template import Library
from datetime import datetime
import pytz, braintree
from mymensor.models import Asset, BraintreeCustomer, BraintreeSubscription
from mymensorapp.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PRIVATE_KEY, BRAINTREE_PUBLIC_KEY, \
    BRAINTREE_PRODUCTION
register = Library()

@register.simple_tag
def subscrip_state(request):
    if BRAINTREE_PRODUCTION:
        braintree_env = braintree.Environment.Production
    else:
        braintree_env = braintree.Environment.Sandbox
    braintree.Configuration.configure(
        braintree_env,
        merchant_id=BRAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY,
    )
    #try:
    #    btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
    #    btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
    #except:
    #    return "NoMyMSubscriptionFound"
    try:
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        currentbtsubscription = braintree.Subscription.find(btsubscription.braintreesubscriptionSubscriptionId)
    except:
        currentAsset = Asset.objects.get(assetOwner=request.user)
        dateofendoftrialbeforesubscription = currentAsset.assetDateOfEndEfTrialBeforeSubscription
        if dateofendoftrialbeforesubscription is not None:
            if datetime.now(pytz.utc) < dateofendoftrialbeforesubscription:
                return "Trial"
            else:
                return "TrialExpired"
        return "TrialPeriodNotSet"
    btsubscription.braintreesubscriptionResultObject = currentbtsubscription
    btsubscription.braintreesubscriptionLastDay = currentbtsubscription.paid_through_date
    btsubscription.braintreesubscriptionSubscriptionStatus = currentbtsubscription.status
    btsubscription.save()
    return btsubscription.braintreesubscriptionSubscriptionStatus

