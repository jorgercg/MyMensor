from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from mymensor.models import BraintreeCustomer, Asset, BraintreeSubscription, BraintreePlan, BraintreeMerchant, \
    BraintreePrice
import braintree, json, pytz
from datetime import datetime, timedelta, date
from mymensorapp.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PRIVATE_KEY, BRAINTREE_PUBLIC_KEY, \
    BRAINTREE_PRODUCTION


@login_required
def updatepaymentmethod(request):
    if request.method == "GET":
        if BRAINTREE_PRODUCTION:
            braintree_env = braintree.Environment.Production
        else:
            braintree_env = braintree.Environment.Sandbox
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        btprice = BraintreePrice.objects.get(pk=btsubscription.braintreeprice.pk)
        btmerchant = BraintreeMerchant.objects.get(pk=btprice.braintreemerchant.pk)
        braintree.Configuration.configure(
            braintree_env,
            merchant_id=BRAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY,
        )
        try:
            client_token = braintree.ClientToken.generate({
                "customer_id": btcustomer.braintreecustomerCustomerId,
                "merchant_account_id": btmerchant.braintreemerchMerchId
            })
        except ValueError as e:
            return render(request, 'updatepaymentmethod.html', {"result_ok": False})
        return render(request, 'updatepaymentmethod.html',
                      {"token": client_token, "result_ok": True, "btsubscription": btsubscription})
    return HttpResponse(status=404)


@login_required
def getbraintreepaymentnonce(request):
    if request.method == 'POST':
        payment_nonce = request.POST.get('nonce')
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
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
def startsubscription(request):
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
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        btprice = BraintreePrice.objects.get(pk=btsubscription.braintreeprice.pk)
        btmerchant = BraintreeMerchant.objects.get(pk=btprice.braintreemerchant.pk)
        btplan = BraintreePlan.objects.get(pk=btprice.braintreeplan.pk)
        succesful = False
        # try:
        result = braintree.Subscription.create({
            "payment_method_nonce": btcustomer.braintreecustomerPaymentMethodNonce,
            "merchant_account_id": btmerchant.braintreemerchMerchId,
            "plan_id": btplan.braintreeplanPlanId
        })
        if result.is_success:
            btsubscription.braintreesubscriptionResultObject = result
            btsubscription.braintreesubscriptionSubscriptionId = result.subscription.id
            btsubscription.braintreesubscriptionSubscriptionStatus = result.subscription.status
            btcustomer.braintreecustomerPaymentMethodToken = result.subscription.payment_method_token
            payment_method_result = braintree.PaymentMethod.find(result.subscription.payment_method_token)
            btsubscription.braintreesubscriptionPayMthdResultObject = payment_method_result
            if (payment_method_result.__class__ == braintree.credit_card.CreditCard):
                btsubscription.braintreesubscriptionPaymentInstrumentType = "credit_card"
            if (payment_method_result.__class__ == braintree.paypal_account.PayPalAccount):
                btsubscription.braintreesubscriptionPaymentInstrumentType = "paypal_account"
                btsubscription.braintreesubscriptionPayPalBillingAgreementId = payment_method_result.billing_agreement_id
                btsubscription.braintreesubscriptionPayPalEmail = payment_method_result.email
            btsubscription.braintreesubscriptionPaymentImageURL = payment_method_result.image_url
            btsubscription.braintreesubscriptionLastDay = result.subscription.paid_through_date
            if btsubscription.braintreesubscriptionPaymentInstrumentType == "credit_card":
                btsubscription.braintreesubscriptionCClast4 = payment_method_result.masked_number
                btsubscription.braintreesubscriptionCCtype = payment_method_result.card_type
                btsubscription.braintreesubscriptionCCexpyear = payment_method_result.expiration_year
                btsubscription.braintreesubscriptionCCexpmonth = payment_method_result.expiration_month
            if btsubscription.braintreesubscriptionPaymentInstrumentType == "paypal_account":
                btsubscription.braintreesubscriptionPayPalBillingAgreementId = payment_method_result.billing_agreement_id
                btsubscription.braintreesubscriptionPayPalEmail = payment_method_result.email
            btsubscription.braintreesubscriptionPlanMymensorTypeLastChangeDate=datetime.now(pytz.utc)
            btcustomer.save()
            btsubscription.save()
            succesful = True
        else:
            btsubscription.braintreesubscriptionResultObject = result
            btsubscription.braintreesubscriptionSubscriptionStatus = "Unsuccessful"
            btsubscription.save()
            return render(request, 'startsubscription.html',
                          {"result": result,
                           "succesful": succesful})
            # except:
            # btsubscription.delete()
            # return render(request, 'startsubscription.html',
            # {"succesful": succesful})
        return render(request, 'startsubscription.html',
                      {"succesful": succesful,
                       "result": result
                       })
    return HttpResponse(status=404)


@login_required
def changesubscriptionplan(request):
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
        currentAsset = Asset.objects.get(assetOwner=request.user)
        currentuserplan = currentAsset.assetMyMensorPlan
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        btprice = BraintreePrice.objects.get(pk=btsubscription.braintreeprice.pk)
        btmerchant = BraintreeMerchant.objects.get(pk=btprice.braintreemerchant.pk)
        btplan = BraintreePlan.objects.get(pk=btprice.braintreeplan.pk)
        if currentuserplan == "MyMensor Media and Data":
            btplan = BraintreePlan.objects.get(braintreeplanPlanMymensorType="MEDIA", braintreeplanCurrency=btmerchant.braintreemerchCurrency)
            btprice = BraintreePrice.objects.get(braintreemerchant_id=btmerchant.id, braintreeplan_id=btplan.id)
            btsubscription.braintreeprice_id = btprice.id
            currentAsset.assetMyMensorPlan = "MyMensor Media"
        elif currentuserplan == "MyMensor Media":
            btplan = BraintreePlan.objects.get(braintreeplanPlanMymensorType="MEDIAANDDATA", braintreeplanCurrency=btmerchant.braintreemerchCurrency)
            btprice = BraintreePrice.objects.get(braintreemerchant_id=btmerchant.id, braintreeplan_id=btplan.id)
            btsubscription.braintreeprice_id = btprice.id
            currentAsset.assetMyMensorPlan = "MyMensor Media and Data"
        succesful = False
        # try:
        result = braintree.Subscription.update(btsubscription.braintreesubscriptionSubscriptionId, {
            "price": str(btprice.braintrepricePrice),
            "merchant_account_id": btmerchant.braintreemerchMerchId,
            "plan_id": btplan.braintreeplanPlanId
        })
        if result.is_success:
            currentAsset.save()
            btsubscription.braintreesubscriptionResultObject = result
            btsubscription.braintreesubscriptionSubscriptionId = result.subscription.id
            btsubscription.braintreesubscriptionSubscriptionStatus = result.subscription.status
            btcustomer.braintreecustomerPaymentMethodToken = result.subscription.payment_method_token
            payment_method_result = braintree.PaymentMethod.find(result.subscription.payment_method_token)
            btsubscription.braintreesubscriptionPayMthdResultObject = payment_method_result
            if (payment_method_result.__class__ == braintree.credit_card.CreditCard):
                btsubscription.braintreesubscriptionPaymentInstrumentType = "credit_card"
            if (payment_method_result.__class__ == braintree.paypal_account.PayPalAccount):
                btsubscription.braintreesubscriptionPaymentInstrumentType = "paypal_account"
                btsubscription.braintreesubscriptionPayPalBillingAgreementId = payment_method_result.billing_agreement_id
                btsubscription.braintreesubscriptionPayPalEmail = payment_method_result.email
            btsubscription.braintreesubscriptionPaymentImageURL = payment_method_result.image_url
            btsubscription.braintreesubscriptionLastDay = result.subscription.paid_through_date
            if btsubscription.braintreesubscriptionPaymentInstrumentType == "credit_card":
                btsubscription.braintreesubscriptionCClast4 = payment_method_result.masked_number
                btsubscription.braintreesubscriptionCCtype = payment_method_result.card_type
                btsubscription.braintreesubscriptionCCexpyear = payment_method_result.expiration_year
                btsubscription.braintreesubscriptionCCexpmonth = payment_method_result.expiration_month
            if btsubscription.braintreesubscriptionPaymentInstrumentType == "paypal_account":
                btsubscription.braintreesubscriptionPayPalBillingAgreementId = payment_method_result.billing_agreement_id
                btsubscription.braintreesubscriptionPayPalEmail = payment_method_result.email
            btsubscription.braintreesubscriptionPlanMymensorTypeLastChangeDate = datetime.now(pytz.utc)
            btcustomer.save()
            btsubscription.save()
            succesful = True
        else:
            btsubscription.braintreesubscriptionResultObject = result
            btsubscription.braintreesubscriptionSubscriptionStatus = "ChangeUnsuccessful"
            btsubscription.save()
            return render(request, 'changesubscriptionplan.html',
                          {"result": result,
                           "succesful": succesful})
            # except:
            # btsubscription.delete()
            # return render(request, 'startsubscription.html',
            # {"succesful": succesful})
        return render(request, 'changesubscriptionplan.html',
                      {"succesful": succesful,
                       "result": result
                       })
    return HttpResponse(status=404)


@login_required
def createsubscription(request):
    if request.method == "GET":
        currentAsset = Asset.objects.get(assetOwner=request.user)
        currentuserplan = currentAsset.assetMyMensorPlan
        availablebtplans = BraintreePlan.objects.all()
        if currentuserplan == "MyMensor Media and Data":
            availablebtplans = BraintreePlan.objects.filter(braintreeplanPlanMymensorType="MEDIAANDDATA")
        elif currentuserplan == "MyMensor Media":
            availablebtplans = BraintreePlan.objects.filter(braintreeplanPlanMymensorType="MEDIA")
        availablebtmerchants = BraintreeMerchant.objects.all()
        availablebtprices = BraintreePrice.objects.all()
        currentbtcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        currentbtsubscription = BraintreeSubscription()
        try:
            currentbtsubscription = BraintreeSubscription.objects.get(braintreecustomer=currentbtcustomer)
            currentbtprice = currentbtsubscription.braintreeprice
            currentbtmerchant = currentbtprice.braintreemerchant
            currentbtplan = currentbtprice.braintreeplan
        except currentbtsubscription.DoesNotExist:
            currentbtmerchant = availablebtmerchants.first()
            currentbtplan = availablebtplans.first()
            currentbtprice = BraintreePrice.objects.get(braintreeplan=currentbtplan,
                                                        braintreemerchant=currentbtmerchant)
            currentbtsubscription = BraintreeSubscription.objects.create(braintreecustomer=currentbtcustomer,
                                                                         braintreeprice=currentbtprice)
            currentbtsubscription.braintreesubscriptionSubscriptionStatus = "Empty"
            currentbtsubscription.save()
        return render(request, 'createsubscription.html',
                      {"currentbtcustomer": currentbtcustomer,
                       "currentsubscription": currentbtsubscription,
                       "currentbtprice": currentbtprice,
                       "currentmerchant": currentbtmerchant,
                       "currentplan": currentbtplan,
                       "availablebtmerchants": availablebtmerchants,
                       "availablebtplans": availablebtplans,
                       "availablebtprices": availablebtprices
                       })
    return HttpResponse(status=404)


@login_required
def setplanmerchid(request):
    if request.method == "POST":
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        priceid = request.POST.get('priceID')
        btprice = BraintreePrice.objects.get(pk=priceid)
        try:
            btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
            btsubscription.braintreeprice = btprice
            btsubscription.braintreesubscriptionSubscriptionStatus = "Empty"
            btsubscription.save(update_fields=['braintreeprice', 'braintreesubscriptionSubscriptionStatus'])
        except btsubscription.DoesNotExist:
            BraintreeSubscription.objects.create(braintreeprice=btprice, braintreecustomer=btcustomer,
                                                 braintreesubscriptionSubscriptionStatus="Empty")
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
def deletesubscription(request):
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
        currentbtcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        succesful = False
        try:
            currentbtsubscription = BraintreeSubscription.objects.get(braintreecustomer=currentbtcustomer)
        except currentbtsubscription.DoesNotExist:
            currentbtsubscription = None
            return render(request, 'deletesubscription.html',
                          {"succesful": succesful
                           })
        try:
            result = braintree.Subscription.cancel(currentbtsubscription.braintreesubscriptionSubscriptionId)
            currentbtsubscription.braintreesubscriptionCancelResultObject = result
        except:
            return render(request, 'deletesubscription.html',
                          {"succesful": succesful
                           })
        if result.is_success:
            succesful = True
            currentbtsubscription.braintreesubscriptionSubscriptionStatus = result.subscription.status
            currentbtsubscription.save()
            return render(request, 'deletesubscription.html',
                          {"succesful": succesful,
                           "currentbtcustomer": currentbtcustomer,
                           "currentsubscription": currentbtsubscription
                           })
        else:
            currentbtsubscription.save()
        return render(request, 'deletesubscription.html',
                      {"succesful": succesful
                       })
    return HttpResponse(status=404)


@login_required
def modifypaymentmethod(request):
    if request.method == "GET":
        if BRAINTREE_PRODUCTION:
            braintree_env = braintree.Environment.Production
        else:
            braintree_env = braintree.Environment.Sandbox
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        btprice = BraintreePrice.objects.get(pk=btsubscription.braintreeprice.pk)
        btmerchant = BraintreeMerchant.objects.get(pk=btprice.braintreemerchant.pk)
        braintree.Configuration.configure(
            braintree_env,
            merchant_id=BRAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY,
        )
        try:
            client_token = braintree.ClientToken.generate({
                "customer_id": btcustomer.braintreecustomerCustomerId,
                "merchant_account_id": btmerchant.braintreemerchMerchId
            })
        except ValueError as e:
            return render(request, 'modifypaymentmethod.html', {"result_ok": False})
        return render(request, 'modifypaymentmethod.html',
                      {"token": client_token, "result_ok": True, "btsubscription": btsubscription})
    return HttpResponse(status=404)


@login_required
def modifypaymentmethodinsubscription(request):
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
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        currentAsset = Asset.objects.get(assetOwner=request.user)
        dateofendoftrialbeforesubscription = currentAsset.assetDateOfEndEfTrialBeforeSubscription
        succesful = False
        # try:
        result = braintree.Subscription.update(btsubscription.braintreesubscriptionSubscriptionId, {
            "payment_method_nonce": btcustomer.braintreecustomerPaymentMethodNonce
        })
        if result.is_success:
            btsubscription.braintreesubscriptionResultObject = result
            btsubscription.braintreesubscriptionSubscriptionId = result.subscription.id
            btsubscription.braintreesubscriptionSubscriptionStatus = result.subscription.status
            btcustomer.braintreecustomerPaymentMethodToken = result.subscription.payment_method_token
            payment_method_result = braintree.PaymentMethod.find(result.subscription.payment_method_token)
            btsubscription.braintreesubscriptionPayMthdResultObject = payment_method_result
            btsubscription.braintreesubscriptionLastDay = result.subscription.paid_through_date
            btsubscription.braintreesubscriptionPaymentImageURL = payment_method_result.image_url
            if (payment_method_result.__class__ == braintree.credit_card.CreditCard):
                btsubscription.braintreesubscriptionPaymentInstrumentType = "credit_card"
                btsubscription.braintreesubscriptionCClast4 = payment_method_result.masked_number
                btsubscription.braintreesubscriptionCCtype = payment_method_result.card_type
                btsubscription.braintreesubscriptionCCexpyear = payment_method_result.expiration_year
                btsubscription.braintreesubscriptionCCexpmonth = payment_method_result.expiration_month
            if (payment_method_result.__class__ == braintree.paypal_account.PayPalAccount):
                btsubscription.braintreesubscriptionPaymentInstrumentType = "paypal_account"
                btsubscription.braintreesubscriptionPayPalBillingAgreementId = payment_method_result.billing_agreement_id
                btsubscription.braintreesubscriptionPayPalEmail = payment_method_result.email
            btcustomer.save()
            btsubscription.save()
            btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
            btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
            currentAsset = Asset.objects.get(assetOwner=request.user)
            dateofendoftrialbeforesubscription = currentAsset.assetDateOfEndEfTrialBeforeSubscription
            succesful = True
        else:
            return render(request, 'subscription.html', {'userloggedin': request.user, 'btcustomer': btcustomer,
                                                         'btsubscription': btsubscription,
                                                         'dateofendoftrialbeforesubscription': dateofendoftrialbeforesubscription,
                                                         'result':result,
                                                         'succesful': succesful})
            # except:
            # return render(request, 'subscription.html', {'userloggedin': request.user, 'btcustomer': btcustomer,
            #                                             'btsubscription': btsubscription,
            #                                             'dateofendoftrialbeforesubscription': dateofendoftrialbeforesubscription,
            #                                             'succesful': succesful})
        return render(request, 'subscription.html', {'userloggedin': request.user, 'btcustomer': btcustomer,
                                                     'btsubscription': btsubscription,
                                                     'dateofendoftrialbeforesubscription': dateofendoftrialbeforesubscription,
                                                     'result': result,
                                                     'succesful': succesful})
    return HttpResponse(status=404)
