from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from mymensor.models import Media, AmazonS3Message
from mymensor.serializer import AmazonSNSNotificationSerializer
import json, boto3
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
            amzs3msg = AmazonS3Message()
            amzs3msg.eventVersion = body['Message']['Records']['eventVersion']
            amzs3msg.save()
            return HttpResponse(status=200)
    return HttpResponse(status=400)

# Portfolio View
@login_required
def portfolio(request):
    medias = Media.objects.all()
    return render(request, 'index.html', {'medias': medias,})

# Photo Feed View
@login_required
def photofeed(request):
    if request.user.is_authenticated:
        photos = Media.objects.all()
        return render(request, 'photofeed.html', {'photos': photos,})

@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def cognitoauth(request):
    if request.method == "GET":

        client = boto3.client(
            'cognito-identity',
            'eu-west-1',
            aws_access_key_id = 'AKIAI4HUWKFMXTSLG5JA',
            aws_secret_access_key = '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',
            )

        token = (Token.objects.get(user_id = request.user.id)).key

        email = request.user.email

        response = client.get_open_id_token_for_developer_identity(
            IdentityPoolId='eu-west-1:963bc158-d9dd-4ae2-8279-b5a8b1524f73',
            Logins={
                'cogdevserv.mymensor.com': email
            },
            TokenDuration=600
        )
        response.update({'identityPoolId':'eu-west-1:963bc158-d9dd-4ae2-8279-b5a8b1524f73'})
        response.update({'key': token})
        return JsonResponse(response)
    return HttpResponse(status=400)

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
