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
from mymensorapp.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_DEFAULT_REGION
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
            message_json = json.loads(body['Message'])
            amzs3msg = AmazonS3Message()
            message_items = message_json['Records'][0]
            amzs3msg.eventVersion = message_items['eventVersion']
            amzs3msg.eventSource = message_items['eventSource']
            amzs3msg.awsRegion = message_items['awsRegion']
            amzs3msg.eventTime = message_items['eventTime']
            amzs3msg.eventName = message_items['eventName']
            amzs3msg.userIdentity_principalId = message_items['userIdentity']['principalId']
            amzs3msg.requestParameters_sourceIPAddress = message_items['requestParameters']['sourceIPAddress']
            amzs3msg.responseElements_x_amz_request_id = message_items['responseElements']['x-amz-request-id']
            amzs3msg.responseElements_x_amz_id_2 = message_items['responseElements']['x-amz-id-2']
            amzs3msg.s3_s3SchemaVersion = message_items['s3']['s3SchemaVersion']
            amzs3msg.s3_configurationId = message_items['s3']['configurationId']
            amzs3msg.s3_bucket_name = message_items['s3']['bucket']['name']
            amzs3msg.s3_bucket_arn = message_items['s3']['bucket']['arn']
            amzs3msg.s3_bucket_ownerIdentity_principalId = message_items['s3']['bucket']['ownerIdentity']['principalId']
            amzs3msg.s3_object_key = message_items['s3']['object']['key']
            amzs3msg.s3_object_size = message_items['s3']['object']['size']
            amzs3msg.s3_object_eTag = message_items['s3']['object']['eTag']
            amzs3msg.s3_object_versionId = message_items['s3']['object']['versionId']
            amzs3msg.s3_object_sequencer = message_items['s3']['object']['sequencer']
            amzs3msg.save()

            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            s3 = session.resource('s3')

            object = s3.Object(amzs3msg.s3_bucket_name,amzs3msg.s3_object_key)

            object.load()

            obj_metadata = object.metadata

            media_received = Media()

            media_received.mediaSha256 = obj_metadata

            media_received.save()


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
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
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
