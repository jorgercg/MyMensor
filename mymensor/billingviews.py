from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from mymensor.models import BraintreeCustomer, Asset, BraintreeSubscription, BraintreePlan, BraintreeMerchant, \
    BraintreePrice
import braintree, json
from mymensorapp.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PRIVATE_KEY, BRAINTREE_PUBLIC_KEY, \
    BRAINTREE_PRODUCTION


@login_required
def updatepaymentmethod(request):
    if request.method == "GET":
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
        btcustomer = BraintreeCustomer(braintreecustomerOwner=request.user)
        try:
            client_token = braintree.ClientToken.generate({
                "customer_id": btcustomer.braintreecustomerCustomerId,
                "merchant_account_id": btcustomer.braintreecustomerMerchantAccId
            })
        except ValueError as e:
            return render(request, 'updatepaymentmethod.html', {"result_ok": False})
        return render(request, 'updatepaymentmethod.html', {"token": client_token, "result_ok": True})
    return HttpResponse(status=404)


@login_required
def get_braintree_payment_nonce(request):
    if request.method == 'POST':
        payment_nonce = int(request.POST.get('nonce'))
        btcustomer = BraintreeCustomer(braintreecustomerOwner=request.user)
        btcustomer.braintreecustomerPaymentMethodNonce = payment_nonce
        try:
            btcustomer.save()
        except:
            return HttpResponse(
                json.dumps({"error": "not saved"}),
                content_type="application/json",
                status=400
            )

        return HttpResponse(
            json.dumps({"success": "success"}),
            content_type="application/json",
            status=200
        )
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json",
            status=400
        )


@login_required
def createsubscription(request):
    if request.method == "GET":
        availablebtmerchants = BraintreeMerchant.objects.all()
        availablebtplans = BraintreePlan.objects.all()
        availablebtprices = BraintreePrice.objects.all()
        currentbtcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        currentbtsubscription=BraintreeSubscription()
        try:
            currentbtsubscription = BraintreeSubscription.objects.get(braintreecustomer=currentbtcustomer)
            currentbtprice = currentbtsubscription.braintreeprice
            currentbtmerchant = currentbtprice.braintreemerchant
            currentbtplan = currentbtprice.braintreeplan
        except currentbtsubscription.DoesNotExist:
            currentbtmerchant = availablebtmerchants.first()
            currentbtplan = availablebtplans.first()
            currentbtprice = availablebtprices.filter(braintreeplan=currentbtplan,braintreemerchant=currentbtmerchant)
            currentbtsubscription = BraintreeSubscription(braintreecustomer=currentbtcustomer,braintreeprice=currentbtprice.pk)

        return render(request, 'createsubscription.html',
                      { "currentbtcustomer": currentbtcustomer,
                        "currentsubscription": currentbtsubscription,
                        "currentbtprice":currentbtprice,
                        "currentmerchant":currentbtmerchant,
                        "currentplan":currentbtplan,
                        "availablebtmerchants":availablebtmerchants,
                        "availablebtplans":availablebtplans,
                        "availablebtprices":availablebtprices
                       })
    return HttpResponse(status=404)


@login_required
def setmerchid(request):
    if request.method == "POST":
        merchid = request.POST.get('merchantID')
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btcustomer.braintreecustomerMerchantAccId = merchid
        try:
            btcustomer.save()
        except:
            return HttpResponse(
                json.dumps({"error": "not saved"}),
                content_type="application/json",
                status=400
            )

        return HttpResponse(
            json.dumps({"success": "success"}),
            content_type="application/json",
            status=200
        )
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json",
            status=400
        )
