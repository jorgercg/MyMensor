from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import braintree
from mymensorapp.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PRIVATE_KEY, BRAINTREE_PUBLIC_KEY, BRAINTREE_PRODUCTION

@login_required
def updatepaymentmethod(request):
    if request.method == "GET":
        return render(request, 'updatepaymentmethod.html')
    return HttpResponse(status=404)

@login_required
def get_braintree_client_token(request):
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
        try:
            client_token = braintree.ClientToken.generate()
        except ValueError as e:
            return JsonResponse({"error": e.message}, status=500)
        return JsonResponse({"token": client_token})
    return HttpResponse(status=404)
