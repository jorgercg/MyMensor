from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from mymensor.models import Photo, AmazonSNSNotification, OpenIdOuath2RedirectCode
from mymensor.serializer import AmazonSNSNotificationSerializer, OpenIdOuath2RedirectCodeSerializer
import json, requests
#from mymensor.forms import AssetOwnerConfigurationFormSet, AssetConfigurationFormSet, DciConfigurationFormSet

# Amazon SNS Notification Processor View
@csrf_exempt
def amazon_sns_processor(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = AmazonSNSNotificationSerializer(data=body)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse(status=200)
    return HttpResponse(status=400)

#URL Redirect for OPENID Connect purposes
@csrf_exempt
def oauth2redirect(request):
    if request.method == "GET":
        code = request.GET.get('code',"")
        state = request.GET.get('state',"")
    if request.method == "POST":
        code = request.POST.get('code',"")
        state = request.POST.get('state',"")
    serializer = OpenIdOuath2RedirectCodeSerializer(data = {'code': code, 'state': state})
    if serializer.is_valid():
        serializer.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

#Returning the last code value received from the specific state
@csrf_exempt
def oauth2redirectreturn(request):
    if request.method == "POST":
        returnstate = request.POST.get('state',"")
        returncode = OpenIdOuath2RedirectCode.objects.get(state=returnstate).order_by('id')[0].values('code')
        return JsonResponse({'code': returncode, 'state':returnstate})
    return HttpResponse(status=400)

# Portfolio View
@login_required
def portfolio(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', {'photos': photos,})


# Photo Feed View
@login_required
def photofeed(request):
    photos = Photo.objects.all()
    return render(request, 'photofeed.html', {'photos': photos,})


def zerossl(request):
    if request.method == "GET":
        return TemplateResponse(request, "zerossl.html")

def android_assetlinks(request):
    if request.method == "GET":
        return TemplateResponse(request, "android_assetlinks.html", content_type="application/json")

# Setup Side View
@login_required
def myMensorSetupFormView(request):
    pass
    #if request.method == 'POST':
        #assetOwnerFormSet = AssetOwnerConfigurationFormSet(request.POST, request.FILES, prefix='assetOwnerFormSet')
        #assetFormSet = AssetConfigurationFormSet(request.POST, request.FILES, prefix='assetFormSet')
        #dciFormSet = DciConfigurationFormSet(request.POST, request.FILES, prefix='dciFormSet')
        #if assetOwnerFormSet.is_valid() and assetFormSet.is_valid() and dciFormSet.is_valid():
        #    assetOwnerFormSet.save()
        # process the data in form.cleaned_data as required
        # ...
        # redirect to a new URL:
    #else:
        #assetOwnerFormSet = AssetOwnerConfigurationFormSet(prefix='assetOwnerFormSet')
        #dciFormSet = DciConfigurationFormSet()
        #assetFormSet = AssetConfigurationFormSet()
    #return render(request, 'setup.html', {'formSetAssetOwner': assetOwnerFormSet, 'formSetAsset': assetFormSet, 'formSetDci':dciFormSet})
