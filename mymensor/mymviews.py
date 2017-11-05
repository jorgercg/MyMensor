from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model, login
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, render_to_response, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from instant.producers import publish
from mymensor.models import Asset, Vp, Tag, Media, Value, ProcessedTag, Tagbbox, AmazonS3Message, AmazonSNSNotification, \
    TagStatusTable, MobileSetupBackup, TwitterAccount, FacebookAccount, BraintreeCustomer, BraintreeSubscription, \
    MobileOnlyUser, MobileClientInstall, BraintreePrice, BraintreeMerchant, BraintreePlan
from mymensor.serializer import AmazonSNSNotificationSerializer, CreateUserSerializer
from mymensor.dcidatasync import loaddcicfg, writedcicfg
from mymensorapp.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, TWITTER_KEY, \
    TWITTER_SECRET, FB_APP_SECRET, FB_APP_ID, MYMMENSORMOBILE_MAX_INSTALLS, BRAINTREE_MERCHANT_ID, \
    BRAINTREE_PRIVATE_KEY, BRAINTREE_PUBLIC_KEY, \
    BRAINTREE_PRODUCTION
import json, boto3, urllib, pytz, urllib2, braintree
from botocore.exceptions import ClientError
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
from mymensor.forms import AssetForm, VpForm, TagForm
from mymensor.mymfunctions import isfloat, mobonlyprefix
from django.db.models import Q, Count
from .tables import TagStatusTableClass
import csv, os, requests
from twython import Twython
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _


def group_check(user):
    return user.groups.filter(name__in=['mymARwebapp']).exists()


def landingView(request):
    if request.method == "GET":
        mediaObjectS3Key = request.GET.get('key', 0)
        messagetype = request.GET.get('type', 0)
        requestsignature = request.GET.get('signature', 0)
        if mediaObjectS3Key != 0 and messagetype != 0 and requestsignature != 0:
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3Client = session.client('s3')
            mediaObjectS3KeyEncoded = urllib.quote(mediaObjectS3Key)
            mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                              Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                      'Key': mediaObjectS3KeyEncoded},
                                                              ExpiresIn=3600)
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3 = session.resource('s3')
            object = s3.Object(AWS_S3_BUCKET_NAME, mediaObjectS3KeyEncoded)
            object.load()
            obj_metadata = object.metadata
            mediaCheckURL = u''.join(['https://app.mymensor.com/landing/?type=']) + str(messagetype)
            mediaCheckURL = mediaCheckURL + '&key=' + mediaObjectS3KeyEncoded + '&signature=' + requestsignature
            if obj_metadata['sha-256'] == requestsignature:
                pdftitle = _('MyMensor Media Check')
                pdfcaptimecert = _('CAPTURE TIME CERTIFIED')
                pdfcaptimenotcert = _('CAPTURE TIME NOT CERTIFIED')
                pdfcaploccert = _('CAPTURE LOCATION CERTIFIED')
                pdfcaplocnotcert = _('CAPTURE LOCATION NOT CERTIFIED')
                pdftblcaptimecert = _('Capture time was certified:')
                pdftblcaptimenotcert = _('Capture time was not certified:')
                pdftblcaploccert = _('Capture location was certified:')
                pdftblcaplocnotcert = _('Capture location was not certified:')
                pdflatitude = _('Latitude')
                pdflongitude = _('Longitude')
                pdfaccuracy = _('Accuracy')
                pdfaron = _('Augmented Reality was used to capture this media.')
                pdfaroff = _('Augmented Reality was not used to capture this media.')
                pdflinktxt = _(
                    'Please use the code to the right or the below address to validate this document online.')
                pdfaccuracydefinition = _('*Please refer to the online page for the accuracy definition.')
                pdfinfotitle = _('MyMensor Media Check')
                pdfinfoauthor = obj_metadata['mymensoraccount']
                pdfinfosubject = _('Media from VP#') + obj_metadata['vp']
                pdfinfokeywords = object.content_type
                pdfinfocreator = _('MyMensor')
                pdfinfoproducer = _('MyMensor')
                pdffilename = 'mymensormediacheck ' + obj_metadata['datetime'] + '.pdf'
                return render(request, 'landing.html', {'mediaStorageURL': mediaStorageURL,
                                                        'mediaContentType': object.content_type,
                                                        'mediaArIsOn': obj_metadata['isarswitchon'],
                                                        'mediaTimeIsCertified': obj_metadata['timecertified'],
                                                        'mediaLocIsCertified': obj_metadata['loccertified'],
                                                        'mediaTimeStamp': obj_metadata['datetime'],
                                                        'loclatitude': obj_metadata['loclatitude'],
                                                        'loclongitude': obj_metadata['loclongitude'],
                                                        'locprecisioninm': obj_metadata['locprecisioninm'],
                                                        'mediasignature': obj_metadata['sha-256'],
                                                        'mediaCheckURL': mediaCheckURL,
                                                        'pdftitle': pdftitle,
                                                        'pdfcaptimecert': pdfcaptimecert,
                                                        'pdfcaptimenotcert': pdfcaptimenotcert,
                                                        'pdfcaploccert': pdfcaploccert,
                                                        'pdfcaplocnotcert': pdfcaplocnotcert,
                                                        'pdftblcaptimecert': pdftblcaptimecert,
                                                        'pdftblcaptimenotcert': pdftblcaptimenotcert,
                                                        'pdftblcaploccert': pdftblcaploccert,
                                                        'pdftblcaplocnotcert': pdftblcaplocnotcert,
                                                        'pdflatitude': pdflatitude,
                                                        'pdflongitude': pdflongitude,
                                                        'pdfaccuracy': pdfaccuracy,
                                                        'pdfaron': pdfaron,
                                                        'pdfaroff': pdfaroff,
                                                        'pdflinktxt': pdflinktxt,
                                                        'pdfaccuracydefinition': pdfaccuracydefinition,
                                                        'pdfinfotitle': pdfinfotitle,
                                                        'pdfinfoauthor': pdfinfoauthor,
                                                        'pdfinfosubject': pdfinfosubject,
                                                        'pdfinfokeywords': pdfinfokeywords,
                                                        'pdfinfocreator': pdfinfocreator,
                                                        'pdfinfoproducer': pdfinfoproducer,
                                                        'pdffilename': pdffilename
                                                        })
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)

    return HttpResponse(status=404)


def mediacheck(request, messagetype, messagemymuser, mediaObjectS3partialKey, requestsignature):
    if request.method == "GET":
        if mediaObjectS3partialKey != 0 and messagetype != 0 and requestsignature != 0 and messagemymuser != 0:
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3Client = session.client('s3')
            mediaObjectS3KeyEncoded = urllib.quote('cap/' + messagemymuser + '/' + mediaObjectS3partialKey)
            mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                              Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                      'Key': mediaObjectS3KeyEncoded},
                                                              ExpiresIn=3600)
            videoStorageURL = mediaStorageURL
            s3 = session.resource('s3')
            object = s3.Object(AWS_S3_BUCKET_NAME, mediaObjectS3KeyEncoded)
            object.load()
            obj_metadata = object.metadata
            mediaCheckURL = u''.join(['https://app.mymensor.com/mc/']) + str(messagetype)
            mediaCheckURLOG = u''.join(['https://app.mymensor.com/mcurl/']) + str(messagetype)
            mediaCheckURL = mediaCheckURL + '/' + mediaObjectS3KeyEncoded + '/' + requestsignature + '/'
            mediaCheckURLOG = mediaCheckURLOG + '/' + mediaObjectS3KeyEncoded + '/' + requestsignature + '/'
            if object.content_type == 'video/mp4':
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKey.replace('_v_', '_t_')
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKeyForThumbnail.replace('.mp4', '.jpg')
                mediaObjectS3KeyEncodedHeader = urllib.quote(
                    'cap/' + messagemymuser + '/' + mediaObjectS3partialKeyForThumbnail)
                mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                  Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                          'Key': mediaObjectS3KeyEncodedHeader},
                                                                  ExpiresIn=3600)

            if obj_metadata['sha-256'] == requestsignature:
                pdftitle = _('MyMensor Media Check')
                pdfcaptimecert = _('CAPTURE TIME CERTIFIED')
                pdfcaptimenotcert = _('CAPTURE TIME NOT CERTIFIED')
                pdfcaploccert = _('CAPTURE LOCATION CERTIFIED')
                pdfcaplocnotcert = _('CAPTURE LOCATION NOT CERTIFIED')
                pdftblcaptimecert = _('Capture time was certified:')
                pdftblcaptimenotcert = _('Capture time was not certified:')
                pdftblcaploccert = _('Capture location was certified:')
                pdftblcaplocnotcert = _('Capture location was not certified:')
                pdflatitude = _('Latitude')
                pdflongitude = _('Longitude')
                pdfaccuracy = _('Accuracy')
                pdfaron = _('Augmented Reality was used to capture this media.')
                pdfaroff = _('Augmented Reality was not used to capture this media.')
                pdflinktxt = _(
                    'Please use the code to the right or the below address to validate this document online.')
                pdfaccuracydefinition = _('*Please refer to the online page for the accuracy definition.')
                pdfinfotitle = _('MyMensor Media Check')
                pdfinfoauthor = obj_metadata['mymensoraccount']
                pdfinfosubject = _('Media from VP#')+obj_metadata['vp']
                pdfinfokeywords = object.content_type
                pdfinfocreator = _('MyMensor')
                pdfinfoproducer = _('MyMensor')
                pdffilename = 'mymensormediacheck '+obj_metadata['datetime']+'.pdf'
                return render(request, 'landing.html', {'mediaStorageURL': mediaStorageURL,
                                                        'videoStorageURL': videoStorageURL,
                                                        'mediaCheckURLOG': mediaCheckURLOG,
                                                        'mediaContentType': object.content_type,
                                                        'mediaArIsOn': obj_metadata['isarswitchon'],
                                                        'mediaTimeIsCertified': obj_metadata['timecertified'],
                                                        'mediaLocIsCertified': obj_metadata['loccertified'],
                                                        'mediaTimeStamp': obj_metadata['datetime'],
                                                        'loclatitude': obj_metadata['loclatitude'],
                                                        'loclongitude': obj_metadata['loclongitude'],
                                                        'locprecisioninm': obj_metadata['locprecisioninm'],
                                                        'mediasignature': obj_metadata['sha-256'],
                                                        'mediaCheckURL': mediaCheckURL,
                                                        'pdftitle': pdftitle,
                                                        'pdfcaptimecert': pdfcaptimecert,
                                                        'pdfcaptimenotcert': pdfcaptimenotcert,
                                                        'pdfcaploccert': pdfcaploccert,
                                                        'pdfcaplocnotcert': pdfcaplocnotcert,
                                                        'pdftblcaptimecert': pdftblcaptimecert,
                                                        'pdftblcaptimenotcert': pdftblcaptimenotcert,
                                                        'pdftblcaploccert': pdftblcaploccert,
                                                        'pdftblcaplocnotcert': pdftblcaplocnotcert,
                                                        'pdflatitude': pdflatitude,
                                                        'pdflongitude': pdflongitude,
                                                        'pdfaccuracy': pdfaccuracy,
                                                        'pdfaron': pdfaron,
                                                        'pdfaroff': pdfaroff,
                                                        'pdflinktxt': pdflinktxt,
                                                        'pdfaccuracydefinition': pdfaccuracydefinition,
                                                        'pdfinfotitle': pdfinfotitle,
                                                        'pdfinfoauthor': pdfinfoauthor,
                                                        'pdfinfosubject': pdfinfosubject,
                                                        'pdfinfokeywords': pdfinfokeywords,
                                                        'pdfinfocreator': pdfinfocreator,
                                                        'pdfinfoproducer': pdfinfoproducer,
                                                        'pdffilename': pdffilename
                                                        })
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)

    return HttpResponse(status=404)


def mediacheckurl(request, messagetype, messagemymuser, mediaObjectS3partialKey, requestsignature):
    if request.method == "GET":
        if mediaObjectS3partialKey != 0 and messagetype != 0 and requestsignature != 0 and messagemymuser != 0:
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3Client = session.client('s3')
            mediaObjectS3KeyEncoded = urllib.quote('cap/' + messagemymuser + '/' + mediaObjectS3partialKey)
            mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                              Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                      'Key': mediaObjectS3KeyEncoded},
                                                              ExpiresIn=3600)
            mediaStorageURLHeader = mediaStorageURL
            s3 = session.resource('s3')
            object = s3.Object(AWS_S3_BUCKET_NAME, mediaObjectS3KeyEncoded)
            object.load()
            obj_metadata = object.metadata
            if object.content_type == 'video/mp4':
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKey.replace('_v_', '_t_')
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKeyForThumbnail.replace('.mp4', '.jpg')
                mediaObjectS3KeyEncodedHeader = urllib.quote(
                    'cap/' + messagemymuser + '/' + mediaObjectS3partialKeyForThumbnail)
                mediaStorageURLHeader = s3Client.generate_presigned_url('get_object',
                                                                        Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                                'Key': mediaObjectS3KeyEncodedHeader},
                                                                        ExpiresIn=3600)
            if obj_metadata['sha-256'] == requestsignature:
                url = mediaStorageURLHeader
                opener = urllib2.urlopen(url)
                content_type = "application/octet-stream"
                response = HttpResponse(opener.read(), content_type=content_type)
                response["Content-Disposition"] = "attachment; filename=media.jpg"
                return response
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)
    return HttpResponse(status=404)


def mediacheckpdf(request, messagetype, messagemymuser, mediaObjectS3partialKey, requestsignature):
    if request.method == "GET":
        if mediaObjectS3partialKey != 0 and messagetype != 0 and requestsignature != 0 and messagemymuser != 0:
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3Client = session.client('s3')
            mediaObjectS3KeyEncoded = urllib.quote('cap/' + messagemymuser + '/' + mediaObjectS3partialKey)
            mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                              Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                      'Key': mediaObjectS3KeyEncoded},
                                                              ExpiresIn=3600)
            videoStorageURL = mediaStorageURL
            s3 = session.resource('s3')
            object = s3.Object(AWS_S3_BUCKET_NAME, mediaObjectS3KeyEncoded)
            object.load()
            obj_metadata = object.metadata
            mediaCheckURL = u''.join(['https://app.mymensor.com/mc/']) + str(messagetype)
            mediaCheckURLOG = u''.join(['https://app.mymensor.com/mcurl/']) + str(messagetype)
            mediaCheckURL = mediaCheckURL + '/' + mediaObjectS3KeyEncoded + '/' + requestsignature + '/'
            mediaCheckURLOG = mediaCheckURLOG + '/' + mediaObjectS3KeyEncoded + '/' + requestsignature + '/'
            if object.content_type == 'video/mp4':
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKey.replace('_v_', '_t_')
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKeyForThumbnail.replace('.mp4', '.jpg')
                mediaObjectS3KeyEncodedHeader = urllib.quote(
                    'cap/' + messagemymuser + '/' + mediaObjectS3partialKeyForThumbnail)
                mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                  Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                          'Key': mediaObjectS3KeyEncodedHeader},
                                                                  ExpiresIn=3600)

            if obj_metadata['sha-256'] == requestsignature:
                pdftitle = _('MyMensor Media Check')
                pdfcaptimecert = _('CAPTURE TIME CERTIFIED')
                pdfcaptimenotcert = _('CAPTURE TIME NOT CERTIFIED')
                pdfcaploccert = _('CAPTURE LOCATION CERTIFIED')
                pdfcaplocnotcert = _('CAPTURE LOCATION NOT CERTIFIED')
                pdftblcaptimecert = _('Capture time was certified:')
                pdftblcaptimenotcert = _('Capture time was not certified:')
                pdftblcaploccert = _('Capture location was certified:')
                pdftblcaplocnotcert = _('Capture location was not certified:')
                pdflatitude = _('Latitude')
                pdflongitude = _('Longitude')
                pdfaccuracy = _('Accuracy')
                pdfaron = _('Augmented Reality was used to capture this media.')
                pdfaroff = _('Augmented Reality was not used to capture this media.')
                pdflinktxt = _(
                    'Please use the code to the right or the below address to validate this document online.')
                pdfaccuracydefinition = _('*Please refer to the online page for the accuracy definition.')
                pdfinfotitle = _('MyMensor Media Check')
                pdfinfoauthor = obj_metadata['mymensoraccount']
                pdfinfosubject = _('Media from VP#')+obj_metadata['vp']
                pdfinfokeywords = object.content_type
                pdfinfocreator = _('MyMensor')
                pdfinfoproducer = _('MyMensor')
                pdffilename = 'mymensormediacheck '+obj_metadata['datetime']+'.pdf'
                return render(request, 'landingpdf.html', {'mediaStorageURL': mediaStorageURL,
                                                        'videoStorageURL': videoStorageURL,
                                                        'mediaCheckURLOG': mediaCheckURLOG,
                                                        'mediaContentType': object.content_type,
                                                        'mediaArIsOn': obj_metadata['isarswitchon'],
                                                        'mediaTimeIsCertified': obj_metadata['timecertified'],
                                                        'mediaLocIsCertified': obj_metadata['loccertified'],
                                                        'mediaTimeStamp': obj_metadata['datetime'],
                                                        'loclatitude': obj_metadata['loclatitude'],
                                                        'loclongitude': obj_metadata['loclongitude'],
                                                        'locprecisioninm': obj_metadata['locprecisioninm'],
                                                        'mediasignature': obj_metadata['sha-256'],
                                                        'mediaCheckURL': mediaCheckURL,
                                                        'pdftitle': pdftitle,
                                                        'pdfcaptimecert': pdfcaptimecert,
                                                        'pdfcaptimenotcert': pdfcaptimenotcert,
                                                        'pdfcaploccert': pdfcaploccert,
                                                        'pdfcaplocnotcert': pdfcaplocnotcert,
                                                        'pdftblcaptimecert': pdftblcaptimecert,
                                                        'pdftblcaptimenotcert': pdftblcaptimenotcert,
                                                        'pdftblcaploccert': pdftblcaploccert,
                                                        'pdftblcaplocnotcert': pdftblcaplocnotcert,
                                                        'pdflatitude': pdflatitude,
                                                        'pdflongitude': pdflongitude,
                                                        'pdfaccuracy': pdfaccuracy,
                                                        'pdfaron': pdfaron,
                                                        'pdfaroff': pdfaroff,
                                                        'pdflinktxt': pdflinktxt,
                                                        'pdfaccuracydefinition': pdfaccuracydefinition,
                                                        'pdfinfotitle': pdfinfotitle,
                                                        'pdfinfoauthor': pdfinfoauthor,
                                                        'pdfinfosubject': pdfinfosubject,
                                                        'pdfinfokeywords': pdfinfokeywords,
                                                        'pdfinfocreator': pdfinfocreator,
                                                        'pdfinfoproducer': pdfinfoproducer,
                                                        'pdffilename': pdffilename
                                                        })
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)

    return HttpResponse(status=404)


# Amazon SNS Notification Processor View
@csrf_exempt
def amazon_sns_processor(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = AmazonSNSNotificationSerializer(data=body)
        if serializer.is_valid():
            amzSns = AmazonSNSNotification(**serializer.validated_data)
            amzSns.save()
            message_json = json.loads(body['Message'])
            amzs3msg = AmazonS3Message()
            amzs3msg.amazonSNSNotification = amzSns
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
            amzs3msg.s3_object_key = urllib.unquote(message_items['s3']['object']['key'])
            amzs3msg.s3_object_size = message_items['s3']['object']['size']
            amzs3msg.s3_object_eTag = message_items['s3']['object']['eTag']
            amzs3msg.s3_object_versionId = message_items['s3']['object']['versionId']
            amzs3msg.s3_object_sequencer = message_items['s3']['object']['sequencer']
            amzs3msg.save()

            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3 = session.resource('s3')
            object = s3.Object(amzs3msg.s3_bucket_name, amzs3msg.s3_object_key)
            object.load()
            obj_metadata = object.metadata
            media_received = Media()
            media_received.amazonS3Message = amzs3msg
            media_received.mediaMillisSinceEpoch = obj_metadata['phototakenmillis']
            media_received.mediaVpNumber = obj_metadata['vp']
            media_received.mediaMymensorAccount = urllib.unquote(obj_metadata['mymensoraccount'])
            media_received.mediaOriginalMymensorAccount = urllib.unquote(obj_metadata['origmymacc'])
            media_received.mediaDeviceId = obj_metadata['deviceid']
            media_received.mediaClientType = obj_metadata['clitype']

            # Fetching the info necessary to fill the vp_id i.e. pk information
            media_user_id = User.objects.get(username=media_received.mediaMymensorAccount).pk
            media_asset_id = Asset.objects.get(assetOwner=media_user_id).pk
            media_received.vp = Vp.objects.get(asset=media_asset_id, vpNumber=media_received.mediaVpNumber)
            media_received.mediaAssetNumber = Asset.objects.get(pk=media_asset_id).assetNumber
            media_received.mediaObjectS3Key = amzs3msg.s3_object_key
            media_received.mediaContentType = object.content_type
            media_received.mediaSha256 = obj_metadata['sha-256']
            media_received.mediaLatitude = obj_metadata['loclatitude']
            media_received.mediaLongitude = obj_metadata['loclongitude']
            media_received.mediaAltitude = obj_metadata['localtitude']
            media_received.mediaLocPrecisionInMeters = obj_metadata['locprecisioninm']
            media_received.mediaLocMethod = obj_metadata['locmethod']
            media_received.mediaLocMillis = obj_metadata['locmillis']
            media_received.mediaLocIsCertified = obj_metadata['loccertified']
            media_received.mediaTimeIsCertified = obj_metadata['timecertified']
            media_received.mediaArIsOn = obj_metadata['isarswitchon']
            media_received.mediaTimeStamp = obj_metadata['datetime']
            try:
                media_received.mediaRemark = urllib.unquote(obj_metadata['remark']).decode('utf-8')
            except:
                media_received.mediaRemark = None
            # Presently the Mobile App DOES NOT PROCESS the VPs
            media_received.mediaProcessed = False

            listofmediaindb = Media.objects.filter(vp=media_received.vp).values_list('mediaSha256', flat=True)

            vp_received = media_received.vp
            vp_received.vpIsUsed = True

            if media_received.mediaSha256 in listofmediaindb:
                return HttpResponse(status=200)
            else:
                media_received.save()
                vp_received.save()

            publish(message='New media arrived on server', event_class="NewMedia", channel="my_mensor_public",
                    data={"username": media_received.mediaMymensorAccount})
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3Client = session.client('s3')
            url = s3Client.generate_presigned_url('get_object',
                                                  Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                          'Key': media_received.mediaObjectS3Key},
                                                  ExpiresIn=3600)
            landingurl = 'https://app.mymensor.com/landing/?type=1&key=' + media_received.mediaObjectS3Key + '&signature=' + media_received.mediaSha256
            mcurl = 'https://app.mymensor.com/mc/1/' + media_received.mediaObjectS3Key + '/' + media_received.mediaSha256
            if (vp_received.vpShareEmail is not None) and (len(vp_received.vpShareEmail) > 0):
                emailsender = User.objects.get(username=media_received.mediaMymensorAccount)
                if media_received.mediaContentType == "image/jpeg":
                    if media_received.mediaRemark is None:
                        mediaRemarkToBeShared = unicode(_('Image Shared by MyMensor Bot \n\n')) + mcurl + unicode(
                            _(
                                '\n\n(Sent by MyMensor Bot - folow the link above to check the image on mymensor.com) \n'))
                    else:
                        mediaRemarkToBeShared = media_received.mediaRemark + '\n\n' + mcurl + unicode(
                            _(
                                '\n\n(Sent by MyMensor Bot - folow the link above to check the image on mymensor.com) \n'))
                    filename = 'temp.jpg'
                    requesturl = requests.get(url, stream=True)
                    if requesturl.status_code == 200:
                        with open(filename, 'wb') as image:
                            for chunk in requesturl:
                                image.write(chunk)
                        image = open(filename, 'rb')
                        subject = _("MyMensor Bot sent you this PHOTO by request of ") + emailsender.username
                        message = mediaRemarkToBeShared
                        from_email = emailsender.email
                        recipient_list = [vp_received.vpShareEmail]
                        reply_to = [from_email]
                        email = EmailMessage(subject=subject, body=message, from_email=from_email, to=recipient_list,
                                             reply_to=reply_to)
                        email.attach(image.name, image.read(), 'image/jpeg')
                        email.send(fail_silently=False)
                        os.remove(filename)
                    else:
                        print("Unable to download media")
                if media_received.mediaContentType == "video/mp4":
                    if media_received.mediaRemark is None:
                        mediaRemarkToBeShared = unicode(_('Video Shared by MyMensor Bot \n\n')) + mcurl + unicode(
                            _(
                                '\n\n(Sent by MyMensor Bot - folow the link above to check the video on mymensor.com) \n'))
                    else:
                        mediaRemarkToBeShared = media_received.mediaRemark + '\n\n' + mcurl + unicode(
                            _(
                                '\n\n(Sent by MyMensor Bot - folow the link above to check the video on mymensor.com) \n'))
                    filename = 'temp.mp4'
                    requesturl = requests.get(url, stream=True)
                    if requesturl.status_code == 200:
                        with open(filename, 'wb') as video:
                            for chunk in requesturl:
                                video.write(chunk)
                        video = open(filename, 'rb')
                        subject = _("MyMensor Bot sent you this VIDEO by request of ") + emailsender.username
                        message = mediaRemarkToBeShared
                        from_email = emailsender.email
                        recipient_list = [vp_received.vpShareEmail]
                        reply_to = [from_email]
                        email = EmailMessage(subject=subject, body=message, from_email=from_email, to=recipient_list,
                                             reply_to=reply_to)
                        email.attach(video.name, video.read(), 'video/mp4')
                        email.send(fail_silently=False)
                        os.remove(filename)
                    else:
                        print("Unable to download media")
            twitterAccount = None
            if vp_received.vpIsSharedToTwitter:
                try:
                    twitterAccount = TwitterAccount.objects.get(twtOwner_id=media_user_id)
                except:
                    twitterAccount = None
                if twitterAccount is not None:
                    twitter_api = Twython(TWITTER_KEY, TWITTER_SECRET, twitterAccount.twtAccessTokenKey,
                                          twitterAccount.twtAccessTokenSecret)
                    if media_received.mediaRemark is None:
                        mediaRemarkToBeSharedToTwitter = mcurl
                    else:
                        mediaRemarkToBeSharedToTwitter = media_received.mediaRemark + '\n\n' + mcurl
                    twitter_api.update_status(status=mediaRemarkToBeSharedToTwitter)
            facebookAccount = None
            if vp_received.vpIsSharedToFacebook:
                try:
                    facebookAccount = FacebookAccount.objects.get(fbOwner_id=media_user_id)
                except:
                    facebookAccount = None
                if facebookAccount is not None:
                    if media_received.mediaRemark is None:
                        mediaRemarkToBeSharedToFB = ""
                    else:
                        mediaRemarkToBeSharedToFB = media_received.mediaRemark
                    data = {'message': mediaRemarkToBeSharedToFB, 'link': mcurl,
                            'access_token': facebookAccount.fbLongTermAccesToken}
                    feedpostresponse = requests.post('https://graph.facebook.com/v2.10/me/feed', data=data)
            return HttpResponse(status=200)
    return HttpResponse(status=400)


# Portfolio View
@login_required
@user_passes_test(group_check)
def portfolio(request):
    if request.user.is_authenticated:
        try:
            loaddcicfg(request)
        except ClientError as e:
            error_code = e
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
            (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
            (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        new_enddate = enddate + timedelta(days=1)
        maxcolumnstxt = request.device.matched
        maxcolumns = 10
        if 'onecolumn' in maxcolumnstxt:
            maxcolumns = 1
        elif 'twocolumn' in maxcolumnstxt:
            maxcolumns = 2
        elif 'threecolumn' in maxcolumnstxt:
            maxcolumns = 3
        elif 'fourcolumn' in maxcolumnstxt:
            maxcolumns = 4
        elif 'fivecolumn' in maxcolumnstxt:
            maxcolumns = 5
        elif 'sixcolumn' in maxcolumnstxt:
            maxcolumns = 6
        elif 'sevencolumn' in maxcolumnstxt:
            maxcolumns = 7
        elif 'eightcolumn' in maxcolumnstxt:
            maxcolumns = 8
        elif 'ninecolumn' in maxcolumnstxt:
            maxcolumns = 9
        elif 'tencolumn' in maxcolumnstxt:
            maxcolumns = 10
        qtypervp = int(request.GET.get('qtypervp', request.session.get('qtypervp', maxcolumns)))
        vpsselected = request.GET.getlist('vpsselected', default=None)
        orgmymaccselected = request.GET.getlist('orgmymaccselected', default=None)
        showonlyloccert = int(request.GET.get('showonlyloccert', request.session.get('showonlyloccert', 0)))
        showonlytimecert = int(request.GET.get('showonlytimecert', request.session.get('showonlytimecert', 0)))
        showlastmedia = int(request.GET.get('showlastmedia', request.session.get('showlastmedia', 1)))
        vps = Vp.objects.filter(asset__assetOwner=request.user).filter(asset__vp__media__isnull=False).filter(
            media__mediaTimeStamp__range=[startdate, new_enddate]).filter(vpIsActive=True).order_by(
            'vpNumber').distinct()
        vpslist = vps
        vpsselectedfromlist = vps.values_list('vpNumber', flat=True)
        if not vpsselected:
            vpsselected = vpsselectedfromlist
        else:
            vps = vps.filter(vpNumber__in=vpsselected).order_by('vpNumber')
            vpsselected = vps.values_list('vpNumber', flat=True)
        if showonlyloccert == 1 and showonlytimecert == 1:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    mediaLocIsCertified=True).filter(
                    mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).order_by(
                    '-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - new_enddate).total_seconds() > 0:
                        new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(mediaLocIsCertified=True).filter(
                mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, new_enddate]).order_by('-mediaMillisSinceEpoch')
        elif showonlyloccert == 1 and showonlytimecert == 0:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    mediaLocIsCertified=True).filter(
                    vp__vpNumber__in=vpsselected).order_by('-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - new_enddate).total_seconds() > 0:
                        new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(mediaLocIsCertified=True).filter(
                vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, new_enddate]).order_by('-mediaMillisSinceEpoch')
        elif showonlyloccert == 0 and showonlytimecert == 1:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).order_by(
                    '-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - new_enddate).total_seconds() > 0:
                        new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, new_enddate]).order_by('-mediaMillisSinceEpoch')
        else:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    vp__vpNumber__in=vpsselected).order_by('-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - new_enddate).total_seconds() > 0:
                        new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, new_enddate]).order_by('-mediaMillisSinceEpoch')
        startdateformatted = urllib.quote(startdate.strftime('%Y-%m-%d %H:%M:%S %z'))
        enddateformatted = urllib.quote(enddate.strftime('%Y-%m-%d %H:%M:%S %z'))
        orgmymacc = medias.order_by('mediaOriginalMymensorAccount').distinct('mediaOriginalMymensorAccount')
        orgmymacclist = orgmymacc.values_list('mediaOriginalMymensorAccount', flat=True)
        if not orgmymaccselected:
            orgmymaccselected = orgmymacclist
        media_vpnumbers = []
        for media in medias:
            media.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                    Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                            'Key': media.mediaObjectS3Key},
                                                                    ExpiresIn=3600)
            media_vpnumbers.append(media.mediaVpNumber)
            if media.mediaContentType == 'video/mp4':
                mediaObjectS3KeyForThumbnail = media.mediaObjectS3Key.replace('_v_', '_t_')
                mediaObjectS3KeyForThumbnail = mediaObjectS3KeyForThumbnail.replace('.mp4', '.jpg')
                media.mediaThumbnailStorageURL = s3Client.generate_presigned_url('get_object',
                                                                                 Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                                         'Key': mediaObjectS3KeyForThumbnail},
                                                                                 ExpiresIn=3600)
        request.session['showonlyloccert'] = showonlyloccert
        request.session['showonlytimecert'] = showonlytimecert
        request.session['startdate'] = startdateformatted
        request.session['enddate'] = enddateformatted
        request.session['qtypervp'] = qtypervp
        request.session['showlastmedia'] = showlastmedia
        return render(request, 'index.html',
                      {'medias': medias, 'vps': vps, 'start': startdateformatted, 'end': enddateformatted,
                       'qtypervp': qtypervp, 'vpsselected': vpsselected, 'vpslist': vpslist,
                       'showonlyloccert': showonlyloccert, 'showlastmedia': showlastmedia,
                       'showonlytimecert': showonlytimecert, 'orgmymaccselected': orgmymaccselected,
                       'orgmymacclist': orgmymacclist, 'media_vpnumbers': media_vpnumbers})


# Location View
@login_required
@user_passes_test(group_check)
def location(request):
    if request.user.is_authenticated:
        try:
            loaddcicfg(request)
        except ClientError as e:
            error_code = e
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
            (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
            (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        # new_enddate = enddate #+ timedelta(days=1)
        vpsselected = request.GET.getlist('vpsselected', default=None)
        orgmymaccselected = request.GET.getlist('orgmymaccselected', default=None)
        showlocationprecision = int(
            request.GET.get('showlocationprecision', request.session.get('showlocationprecision', 0)))
        showonlyloccert = int(request.GET.get('showonlyloccert', request.session.get('showonlyloccert', 0)))
        showonlytimecert = int(request.GET.get('showonlytimecert', request.session.get('showonlytimecert', 0)))
        showlastmedia = int(request.GET.get('showlastmedia', request.session.get('showlastmedia', 1)))
        showuserpath = int(request.GET.get('showuserpath', request.session.get('showuserpath', 0)))
        centerlat = float(request.GET.get('centerlat', 0))
        centerlng = float(request.GET.get('centerlng', 0))
        mapzoom = int(request.GET.get('mapzoom', 0))
        vps = Vp.objects.filter(asset__assetOwner=request.user).filter(asset__vp__media__isnull=False).filter(
            media__mediaTimeStamp__range=[startdate, enddate]).filter(vpIsActive=True).order_by(
            'vpNumber').distinct()
        vpslist = vps
        vpsselectedfromlist = vps.values_list('vpNumber', flat=True)
        if not vpsselected:
            vpsselected = vpsselectedfromlist
        else:
            vps = vps.filter(vpNumber__in=vpsselected).order_by('vpNumber')
            vpsselected = vps.values_list('vpNumber', flat=True)
        if showonlyloccert == 1 and showonlytimecert == 1:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    mediaLocIsCertified=True).filter(
                    mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).order_by(
                    '-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - enddate).total_seconds() > 0:
                        # new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(mediaLocIsCertified=True).filter(
                mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, enddate]).order_by('-mediaMillisSinceEpoch')
        elif showonlyloccert == 1 and showonlytimecert == 0:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    mediaLocIsCertified=True).filter(
                    vp__vpNumber__in=vpsselected).order_by('-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - enddate).total_seconds() > 0:
                        # new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(mediaLocIsCertified=True).filter(
                vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, enddate]).order_by('-mediaMillisSinceEpoch')
        elif showonlyloccert == 0 and showonlytimecert == 1:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).order_by(
                    '-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - enddate).total_seconds() > 0:
                        # new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                mediaTimeIsCertified=True).filter(vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, enddate]).order_by('-mediaMillisSinceEpoch')
        else:
            if showlastmedia == 1:
                lastmedia = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                    vp__vpNumber__in=vpsselected).order_by('-mediaMillisSinceEpoch').first()
                if lastmedia:
                    if (lastmedia.mediaTimeStamp - enddate).total_seconds() > 0:
                        # new_enddate = lastmedia.mediaTimeStamp
                        enddate = lastmedia.mediaTimeStamp
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                vp__vpNumber__in=vpsselected).filter(
                mediaTimeStamp__range=[startdate, enddate]).order_by('-mediaMillisSinceEpoch')
        startdateformatted = urllib.quote(startdate.strftime('%Y-%m-%d %H:%M:%S %z'))
        enddateformatted = urllib.quote(enddate.strftime('%Y-%m-%d %H:%M:%S %z'))
        orgmymacc = medias.order_by('mediaOriginalMymensorAccount').distinct('mediaOriginalMymensorAccount')
        orgmymacclist = orgmymacc.values_list('mediaOriginalMymensorAccount', flat=True)
        if not orgmymaccselected:
            orgmymaccselected = orgmymacclist
        media_vpnumbers = []
        for media in medias:
            media.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                    Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                            'Key': media.mediaObjectS3Key},
                                                                    ExpiresIn=3600)
            media_vpnumbers.append(media.mediaVpNumber)
            if media.mediaContentType == 'video/mp4':
                mediaObjectS3KeyForThumbnail = media.mediaObjectS3Key.replace('_v_', '_t_')
                mediaObjectS3KeyForThumbnail = mediaObjectS3KeyForThumbnail.replace('.mp4', '.jpg')
                media.mediaThumbnailStorageURL = s3Client.generate_presigned_url('get_object',
                                                                                 Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                                         'Key': mediaObjectS3KeyForThumbnail},
                                                                                 ExpiresIn=3600)
        request.session['showonlyloccert'] = showonlyloccert
        request.session['showonlytimecert'] = showonlytimecert
        request.session['showuserpath'] = showuserpath
        request.session['showlocationprecision'] = showlocationprecision
        request.session['startdate'] = startdateformatted
        request.session['enddate'] = enddateformatted
        request.session['showlastmedia'] = showlastmedia
        return render(request, 'location.html',
                      {'medias': medias, 'vps': vps, 'start': startdateformatted, 'end': enddateformatted,
                       'vpsselected': vpsselected, 'vpslist': vpslist, 'showlocationprecision': showlocationprecision,
                       'showuserpath': showuserpath, 'showonlyloccert': showonlyloccert, 'showlastmedia': showlastmedia,
                       'showonlytimecert': showonlytimecert, 'centerlat': centerlat, 'centerlng': centerlng,
                       'mapzoom': mapzoom, 'orgmymaccselected': orgmymaccselected, 'orgmymacclist': orgmymacclist,
                       'media_vpnumbers': media_vpnumbers})


@login_required
@user_passes_test(group_check)
def mediafeed(request):
    if request.user.is_authenticated:
        try:
            loaddcicfg(request)
        except ClientError as e:
            error_code = e
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        medias = Media.objects.filter(vp__asset__assetOwner=request.user).order_by('-mediaMillisSinceEpoch')[:50]
        vps = Vp.objects.filter(asset__assetOwner=request.user).order_by('vpNumber')
        for media in medias:
            media.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                    Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                            'Key': media.mediaObjectS3Key},
                                                                    ExpiresIn=3600)
        return render(request, 'mediafeed.html', {'medias': medias, 'vps': vps})


def subscription_state(assetinstance):
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
    #    btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=assetinstance.assetOwner)
    #    btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
    #except:
    #    return "NoMyMSubscriptionFound"
    try:
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=assetinstance.assetOwner)
        btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        currentbtsubscription = braintree.Subscription.find(btsubscription.braintreesubscriptionSubscriptionId)
    except:
        dateofendoftrialbeforesubscription = assetinstance.assetDateOfEndEfTrialBeforeSubscription
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

@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def create_new_user(request):
    serialized = CreateUserSerializer(data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response(serialized.data, status=201)
    else:
        return Response(serialized._errors, status=400)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
@user_passes_test(group_check)
def mobiletowebapp(request):
    if request.method == "GET":
        user = request.user
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse('portfolio'))
        else:
            HttpResponse(status=400)
    return HttpResponse(status=400)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def cognitoauth(request):
    if request.method == "GET":
        client = boto3.client(
            'cognito-identity',
            'eu-west-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        try:
            mymensormobileclienttype = request.META['HTTP_FROM']
        except KeyError:
            mymensormobileclienttype = "UNKNOWN"
        # No mobile client type set
        if mymensormobileclienttype == "UNKNOWN":
            return HttpResponse(status=400)
        try:
            mymclientguid = request.META['HTTP_WARNING']
        except KeyError:
            mymclientguid = "NOTSET"
        # No mobile GUID set
        if mymclientguid == "NOTSET":
            return HttpResponse(status=400)
        assetinstance = Asset.objects.get(assetOwner=request.user)
        thirtydaysago = datetime.now(pytz.utc) - timedelta(days=30)
        qtyofinstallactiveduringlastmonth = MobileClientInstall.objects.filter(asset=assetinstance).filter(
            mobileClientInstallLastAccessTimeStamp__gte=thirtydaysago).distinct('mobileClientInstallGUID').count()
        qtyofinstallevermade = MobileClientInstall.objects.filter(asset=assetinstance).distinct(
            'mobileClientInstallGUID').count()
        mobclientinstallinstace = MobileClientInstall()
        try:
            mobclientinstallinstace = MobileClientInstall.objects.get(asset=assetinstance,
                                                                      mobileClientInstallGUID=mymclientguid)
            mobclientinstallinstace.mobileClientInstallLastAccessTimeStamp = datetime.now(pytz.utc)
            mobclientinstallinstace.save(force_update=True)
        except mobclientinstallinstace.DoesNotExist:
            timenow = datetime.now(pytz.utc)
            mobclientinstallinstace = MobileClientInstall(asset=assetinstance, mobileClientInstallGUID=mymclientguid,
                                                          mobileClientInstallOrderNumber=qtyofinstallevermade + 1,
                                                          mobileClientInstallCreationTimeStamp=timenow,
                                                          mobileClientInstallLastAccessTimeStamp=timenow)
            mobclientinstallinstace.save(force_insert=True)
            qtyofinstallactiveduringlastmonth = qtyofinstallactiveduringlastmonth + 1
        # More than MYMMENSORMOBILE_MAX_INSTALLS per username including service users
        if qtyofinstallactiveduringlastmonth > MYMMENSORMOBILE_MAX_INSTALLS:
            return HttpResponse(status=433)

        usergroup = 'mymARwebapp'
        token = (Token.objects.get(user_id=request.user.id)).key
        username = request.user.username
        if request.user.groups.filter(name__in=['mymARmobileapp']).exists():
            # TODO: Bring the prefix from Asset (Firstly put it there, obviusly....)
            usernameprefix = username[:7]
            username = username.replace(usernameprefix, '')
            usergroup = 'mymARmobileapp'
            masteruser = User.objects.get(username=username)
            assetinstance = Asset.objects.get(assetOwner=masteruser)

        subscriptionState = subscription_state(assetinstance)

        if subscriptionState == "NoMyMSubscriptionFound":
            return HttpResponse(status=432)

        if subscriptionState == "TrialPeriodNotSet":
            return HttpResponse(status=432)

        if subscriptionState == "TrialExpired":
            return HttpResponse(status=432)

        if subscriptionState == "PastDue":
            return HttpResponse(status=434)

        if subscriptionState == "Canceled":
            btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=assetinstance.assetOwner)
            btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
            if datetime.now(pytz.utc) > btsubscription.braintreesubscriptionLastDay:
                return HttpResponse(status=434)

        response = client.get_open_id_token_for_developer_identity(
            IdentityPoolId='eu-west-1:963bc158-d9dd-4ae2-8279-b5a8b1524f73',
            Logins={
                'cogdevserv.mymensor.com': username
            },
            TokenDuration=600
        )
        response.update({'identityPoolId': 'eu-west-1:963bc158-d9dd-4ae2-8279-b5a8b1524f73'})
        response.update({'key': token})
        response.update({'usergroup': usergroup})

        assetinstance.assetOwnerIdentityId = response['IdentityId']
        assetinstance.assetDciClientSoftwareType = mymensormobileclienttype
        assetinstance.save()
        return JsonResponse(response)
    return HttpResponse(status=400)


def zerossl(request):
    if request.method == "GET":
        return TemplateResponse(request, "zerossl.html")


def android_assetlinks(request):
    if request.method == "GET":
        return TemplateResponse(request, "android_assetlinks.html", content_type="application/json")


@login_required
@user_passes_test(group_check)
def assetSetupFormView(request):
    try:
        loaddcicfg(request)
    except ClientError as e:
        error_code = e
    asset = Asset.objects.get(assetOwner=request.user)
    form = AssetForm(request.POST, instance=asset)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            writedcicfg(request)
    else:
        form = AssetForm(instance=asset)
    return render(request, 'assetsetup.html', {'form': form})


@login_required
@user_passes_test(group_check)
def vpSetupFormView(request):
    try:
        loaddcicfg(request)
    except ClientError as e:
        error_code = e
    currentvp = 1
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3Client = session.client('s3')
    if request.method == 'POST':
        currentvp = int(request.POST.get('currentvp', 1))
    if request.method == 'GET':
        currentvp = int(request.GET.get('currentvp', 1))
    vp = Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).filter(vpNumber=currentvp).get()

    form = VpForm(request.POST, instance=vp)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            writedcicfg(request)
    else:
        form = VpForm(instance=vp)
    vps = Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).order_by('vpNumber')
    try:
        descvpStorageURL = s3Client.generate_presigned_url('get_object',
                                                           Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                   'Key': vp.vpStdPhotoStorageURL},
                                                           ExpiresIn=3600)
    except:
        descvpStorageURL = " "
    try:
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3 = session.resource('s3')
        object = s3.Object(AWS_S3_BUCKET_NAME, vp.vpStdPhotoStorageURL)
        object.load()
        obj_metadata = object.metadata
        descvpTimeStampTemp = obj_metadata['datetime']
        descvpTimeStampTemp = descvpTimeStampTemp.replace(" ","T")
        descvpTimeStamp = parse(descvpTimeStampTemp, yearfirst=True)
    except:
        descvpTimeStamp = " "
    tags = Tag.objects.filter(vp__vpIsActive=True).filter(vp__asset__assetOwner=request.user).filter(
        vp__vpNumber=currentvp)
    tagbboxes = Tagbbox.objects.filter(tag__in=tags)

    swaltitle = _('Explicit Consent Needed!')
    swaltext = _(
        'Please type your MyMensor username below and click on the Confirm button below to hereby attest that you are giving your explicit consent to MyMensor to automatically share ALL INCOMING MEDIA to this VP Folder directly to the Twitter account configured in your MyMensor Account. You also explicit confirm that you know and agree that you will not be able to revise the content of the posting before it is actually posted.')
    swalinputPlaceholder = _("Type your MyMensor username here.")
    swalconfirmButtonText = _('Confirm')
    swalcancelButtonText = _('Cancel')
    swalreject = _('You need to enter your username.')
    swalsuccesstitle = _("Thank you for your confirmation!")
    swalsuccesstext = _("Please submit this VP configuration in order to start tweeting automatically from MyMensor!")

    return render(request, 'vpsetup.html',
                  {'form': form, 'vps': vps, 'currentvp': currentvp, 'descvpStorageURL': descvpStorageURL,
                   'descvpTimeStamp': descvpTimeStamp, 'tagbboxes': tagbboxes, 'tags': tags, 'swaltitle': swaltitle,
                   'swaltext': swaltext, 'swalinputPlaceholder': swalinputPlaceholder,
                   'swalconfirmButtonText': swalconfirmButtonText,
                   'swalcancelButtonText': swalcancelButtonText, 'swalreject': swalreject,
                   'swalsuccesstitle': swalsuccesstitle, 'swalsuccesstext': swalsuccesstext})


@login_required
@user_passes_test(group_check)
def tagSetupFormView(request):
    try:
        loaddcicfg(request)
    except ClientError as e:
        error_code = e
    currentvp = 1
    qtyvps = Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).count()
    listoftagsindatabase = Tag.objects.filter(vp__asset__assetOwner=request.user)
    qtytagsindatabase = listoftagsindatabase.count()

    if request.method == 'POST':
        currentvp = int(request.POST.get('currentvp', 1))
        currenttag = int(request.POST.get('currenttag', 1))
        qtytagsinclient = int(request.GET.get('qtytags', qtytagsindatabase))
        try:
            tag = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(
                vp__vpNumber=currentvp).filter(tagNumber=currenttag).get()
            lasttag = Tag.objects.filter(vp__asset__assetOwner=request.user).order_by('tagNumber').last()
            vpoflasttag = lasttag.vp
            listoftagsindatabase = Tag.objects.filter(vp__asset__assetOwner=request.user)
            qtytagsindatabase = listoftagsindatabase.count()
            form = TagForm(request.POST, instance=tag)
        except tag.DoesNotExist:
            tag = Tag(vp=Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).filter(
                vpNumber=currentvp).get())
            lasttag = Tag.objects.filter(vp__asset__assetOwner=request.user).order_by('tagNumber').last()
            vpoflasttag = lasttag.vp
            listoftagsindatabase = Tag.objects.filter(vp__asset__assetOwner=request.user)
            qtytagsindatabase = listoftagsindatabase.count()
            form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
    if request.method == 'GET':
        form = None
        currentvp = int(request.GET.get('currentvp', 1))
        currenttag_temp = int(request.GET.get('currenttag', 0))
        tagdeleted = int(request.GET.get('tagdeleted', 0))
        if tagdeleted > 0:
            taginstance = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpNumber=currentvp).filter(
                tagNumber=tagdeleted).get()
            taginstance.delete()
        qtytagsinclient = int(request.GET.get('qtytags', qtytagsindatabase))
        if qtytagsindatabase > 0:
            listoftagsincurrentvp = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(
                vp__vpNumber=currentvp).values_list('tagNumber', flat=True).order_by('tagNumber')
            qtytagsincurrentvp = listoftagsincurrentvp.count()
            if qtytagsincurrentvp > 0:
                if currenttag_temp in listoftagsincurrentvp:
                    currenttag = currenttag_temp
                elif qtytagsinclient > qtytagsindatabase:
                    currenttag = qtytagsinclient
                else:
                    currenttag = listoftagsincurrentvp.first()
                tag = Tag()
                try:
                    tag = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpNumber=currentvp).filter(
                        tagNumber=currenttag).get()
                    lasttag = Tag.objects.filter(vp__asset__assetOwner=request.user).order_by('tagNumber').last()
                    vpoflasttag = lasttag.vp
                    listoftagsindatabase = Tag.objects.filter(vp__asset__assetOwner=request.user)
                    qtytagsindatabase = listoftagsindatabase.count()
                    form = TagForm(instance=tag)
                except tag.DoesNotExist:
                    tag = Tag.objects.create(
                        vp=Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).filter(
                            vpNumber=currentvp).get(), tagDescription=_('TAG#') + str(currenttag), tagNumber=currenttag,
                        tagQuestion=_('Tag question for TAG#') + str(currenttag))
                    lasttag = Tag.objects.filter(vp__asset__assetOwner=request.user).order_by('tagNumber').last()
                    vpoflasttag = lasttag.vp
                    listoftagsindatabase = Tag.objects.filter(vp__asset__assetOwner=request.user)
                    qtytagsindatabase = listoftagsindatabase.count()
                    form = TagForm(instance=tag)
            if qtytagsincurrentvp == 0 and qtytagsinclient <= qtytagsindatabase:
                currenttag = 0
                form = None
            if qtytagsincurrentvp == 0 and qtytagsinclient > qtytagsindatabase:
                currenttag = qtytagsinclient
                tag = Tag.objects.create(
                    vp=Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).filter(
                        vpNumber=currentvp).get(), tagDescription=_('TAG#') + str(currenttag), tagNumber=currenttag,
                    tagQuestion=_('Tag question for TAG#') + str(currenttag))
                lasttag = Tag.objects.filter(vp__asset__assetOwner=request.user).order_by('tagNumber').last()
                vpoflasttag = lasttag.vp
                listoftagsindatabase = Tag.objects.filter(vp__asset__assetOwner=request.user)
                qtytagsindatabase = listoftagsindatabase.count()
                form = TagForm(instance=tag)
        if qtytagsindatabase == 0:
            if qtytagsinclient > qtytagsindatabase:
                currenttag = qtytagsinclient
                tag = Tag.objects.create(
                    vp=Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).filter(
                        vpNumber=currentvp).get(), tagDescription=_('TAG#') + str(currenttag), tagNumber=currenttag,
                    tagQuestion=_('Tag question for TAG#') + str(currenttag))
                lasttag = Tag.objects.filter(vp__asset__assetOwner=request.user).order_by('tagNumber').last()
                vpoflasttag = lasttag.vp
                listoftagsindatabase = Tag.objects.filter(vp__asset__assetOwner=request.user)
                qtytagsindatabase = listoftagsindatabase.count()
                form = TagForm(instance=tag)
            else:
                currenttag = 0
                form = None
    if form is not None:
        tags = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpNumber=currentvp).order_by(
            'tagNumber')
    else:
        tags = None
        lasttag = Tag.objects.filter(vp__asset__assetOwner=request.user).order_by('tagNumber').last()
        if lasttag == None:
            vpoflasttag = None
        else:
            vpoflasttag = lasttag.vp

    vps = Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).exclude(vpNumber=0).order_by(
        'vpNumber')
    vp = Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).filter(vpNumber=currentvp).get()
    try:
        tagbbox = Tagbbox.objects.get(tag=tag)
    except:
        tagbbox = None
    try:
        firstsession = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = firstsession.client('s3')
        descvpStorageURL = s3Client.generate_presigned_url('get_object',
                                                           Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                   'Key': vp.vpStdPhotoStorageURL},
                                                           ExpiresIn=3600)
    except:
        descvpStorageURL = " "
    try:
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3 = session.resource('s3')
        object = s3.Object(AWS_S3_BUCKET_NAME, vp.vpStdPhotoStorageURL)
        object.load()
        obj_metadata = object.metadata
        descvpTimeStampTemp = obj_metadata['datetime']
        descvpTimeStampTemp = descvpTimeStampTemp.replace(" ", "T")
        descvpTimeStamp = parse(descvpTimeStampTemp, yearfirst=True)
    except:
        descvpTimeStamp = " "
    return render(request, 'tagsetup.html',
                  {'form': form, 'qtyvps': qtyvps, 'currentvp': currentvp, 'qtytagsinclient': qtytagsinclient,
                   'currenttag': currenttag, 'tags': tags, 'vps': vps, 'descvpStorageURL': descvpStorageURL,
                   'descvpTimeStamp': descvpTimeStamp, 'tagbbox': tagbbox, 'lasttag': lasttag,
                   'vpoflasttag': vpoflasttag,
                   'qtytagsindatabase': qtytagsindatabase})


@login_required
@user_passes_test(group_check)
def save_tagboundingbox(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        posx = float(received_json_data[0]['x'])
        posy = float(received_json_data[0]['y'])
        width = float(received_json_data[0]['width'])
        height = float(received_json_data[0]['height'])
        tagnumber = int(received_json_data[0]['tagnumber'])
        taginstance = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(tagNumber=tagnumber).get()
        try:
            tagbboxinstancepk = Tagbbox.objects.get(tag_id=taginstance.pk).pk
        except Tagbbox.DoesNotExist:
            tagbboxinstancetmp = Tagbbox(tag_id=taginstance.pk)
            tagbboxinstancetmp.save()
            tagbboxinstancepk = tagbboxinstancetmp.pk
        tagbboxinstance = Tagbbox(pk=tagbboxinstancepk)
        tagbboxinstance.tag_id = taginstance.pk
        tagbboxinstance.tagbboxX = posx
        tagbboxinstance.tagbboxY = posy
        tagbboxinstance.tagbboxWidth = width
        tagbboxinstance.tagbboxHeight = height
        tagbboxinstance.save()
        return HttpResponse(
            json.dumps({"result": "success"}),
            content_type="application/json",
            status=200)
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json",
            status=400
        )


@login_required
@user_passes_test(group_check)
def procTagEditView(request):
    if request.user.is_authenticated:
        try:
            loaddcicfg(request)
        except ClientError as e:
            error_code = e
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
            (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
            (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        new_enddate = enddate + timedelta(days=1)
        qtypervp = int(request.GET.get('qtypervp', request.session.get('qtypervp', 5)))

        medias = Media.objects.filter(vp__vpIsActive=True).filter(mediaProcessed=True).filter(
            vp__asset__assetOwner=request.user).filter(mediaTimeStamp__range=[startdate, new_enddate]).order_by(
            'mediaMillisSinceEpoch')
        startdateformatted = urllib.quote(startdate.strftime('%Y-%m-%d %H:%M:%S %z'))
        enddateformatted = urllib.quote(enddate.strftime('%Y-%m-%d %H:%M:%S %z'))
        for media in medias:
            media.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                    Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                            'Key': media.mediaObjectS3Key},
                                                                    ExpiresIn=3600)
        vpsofthemediasprocessedlist = medias.values_list('vp__id', flat=True)
        vps = Vp.objects.annotate(qtyoftags=Count('tag')).filter(asset__assetOwner=request.user).filter(
            vpIsActive=True).filter(id__in=vpsofthemediasprocessedlist).order_by('vpNumber').distinct()
        tags = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(tagIsActive=True).distinct()
        for vp in vps:
            vp.vpStdPhotoStorageURL = s3Client.generate_presigned_url('get_object',
                                                                      Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                              'Key': vp.vpStdPhotoStorageURL},
                                                                      ExpiresIn=3600)
        values = ProcessedTag.objects.filter(media__vp__asset__assetOwner=request.user).filter(
            tag__tagIsActive=True).filter(
            media__mediaProcessed=True).distinct()  # .values_list('media','tag','valValueEvaluated')
        mediasofthevaluelist = values.values_list('media__id', flat=True)
        tagsofthevaluelist = values.values_list('tag__id', flat=True)
        request.session['qtypervp'] = qtypervp
        tagbboxes = Tagbbox.objects.filter(tag__in=tags)
        return render(request, 'proctagedit.html', {'medias': medias, 'vps': vps, 'tags': tags, 'values': values,
                                                    'mediasofthevaluelist': mediasofthevaluelist,
                                                    'tagsofthevaluelist': tagsofthevaluelist,
                                                    'start': startdateformatted, 'end': enddateformatted,
                                                    'qtypervp': qtypervp, 'tagbboxes':tagbboxes})


@login_required
@user_passes_test(group_check)
def tagProcessingFormView(request):
    if request.user.is_authenticated:
        try:
            loaddcicfg(request)
        except ClientError as e:
            error_code = e
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
            (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
            (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        new_enddate = enddate + timedelta(days=1)
        qtypervp = int(request.GET.get('qtypervp', request.session.get('qtypervp', 5)))
        medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpIsActive=True).filter(
            mediaProcessed=False).filter(vp__tag__isnull=False).filter(
            mediaTimeStamp__range=[startdate, new_enddate]).order_by('mediaMillisSinceEpoch').distinct()
        startdateformatted = urllib.quote(startdate.strftime('%Y-%m-%d %H:%M:%S %z'))
        enddateformatted = urllib.quote(enddate.strftime('%Y-%m-%d %H:%M:%S %z'))
        for media in medias:
            media.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                    Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                            'Key': media.mediaObjectS3Key},
                                                                    ExpiresIn=3600)
        vpsofthemediasnotprocessedlist = medias.values_list('vp__id', flat=True)
        vps = Vp.objects.annotate(qtyoftags=Count('tag')).filter(asset__assetOwner=request.user).filter(
            vpIsActive=True).filter(id__in=vpsofthemediasnotprocessedlist).exclude(vpNumber=0).order_by(
            'vpNumber').distinct()
        tags = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(tagIsActive=True).distinct()
        for vp in vps:
            vp.vpStdPhotoStorageURL = s3Client.generate_presigned_url('get_object',
                                                                      Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                              'Key': vp.vpStdPhotoStorageURL},
                                                                      ExpiresIn=3600)
        values = ProcessedTag.objects.filter(media__vp__asset__assetOwner=request.user).filter(
            tag__tagIsActive=True).filter(
            media__mediaProcessed=False).distinct()  # .values_list('media','tag','valValueEvaluated')
        mediasofthevaluelist = values.values_list('media__id', flat=True)
        tagsofthevaluelist = values.values_list('tag__id', flat=True)
        request.session['qtypervp'] = qtypervp
        tagbboxes = Tagbbox.objects.filter(tag__in=tags)
        return render(request, 'tagprocessing.html', {'medias': medias, 'vps': vps, 'tags': tags, 'values': values,
                                                      'mediasofthevaluelist': mediasofthevaluelist,
                                                      'tagsofthevaluelist': tagsofthevaluelist,
                                                      'start': startdateformatted, 'end': enddateformatted,
                                                      'qtypervp': qtypervp, 'tagbboxes':tagbboxes})


@login_required
@user_passes_test(group_check)
def saveValue(request):
    if request.method == 'POST':
        mediaid = int(request.POST.get('mediaid'))
        vpid = int(request.POST.get('vpid'))
        tagid = int(request.POST.get('tagid'))
        valuetxt = request.POST.get('value')
        if isfloat(valuetxt):
            valuefloat = float(valuetxt)
        else:
            return HttpResponse(status=400)
        mediainstance = Media.objects.get(id=mediaid)
        taginstance = Tag.objects.get(id=tagid)
        vpinstance = Vp.objects.get(id=vpid)
        proctagstate = "NP"
        if taginstance.tagLowRed == None or taginstance.tagLowYellow == None or taginstance.tagHighYellow == None or taginstance.tagHighRed == None:
            proctagstate = "PR"
        else:
            if valuefloat < taginstance.tagLowRed:
                proctagstate = "LR"
            if valuefloat >= taginstance.tagLowRed and valuefloat < taginstance.tagLowYellow:
                proctagstate = "LY"
            if valuefloat >= taginstance.tagLowYellow and valuefloat <= taginstance.tagHighYellow:
                proctagstate = "GR"
            if valuefloat > taginstance.tagHighYellow and valuefloat <= taginstance.tagHighRed:
                proctagstate = "HY"
            if valuefloat > taginstance.tagHighRed:
                proctagstate = "HR"
        try:
            processedtag = ProcessedTag.objects.get(media=mediainstance, tag=taginstance)
            processedtag.valValueEvaluated = valuefloat
            processedtag.tagStateEvaluated = proctagstate
            processedtag.save()
        except ProcessedTag.DoesNotExist:
            ProcessedTag.objects.create(media=mediainstance, tag=taginstance, valValueEvaluated=valuefloat,
                                        tagStateEvaluated=proctagstate)
        processedtag = ProcessedTag.objects.get(media=mediainstance, tag=taginstance, valValueEvaluated=valuefloat,
                                                tagStateEvaluated=proctagstate)
        value = Value(processedTag=processedtag, processorUserId=request.user, valValue=valuefloat,
                      tagStateResultingFromValValueStatus=proctagstate)
        value.save()
        try:
            tagstatusinstance = TagStatusTable.objects.get(processedTag=processedtag,
                                                           statusTagNumber=taginstance.tagNumber,
                                                           statusVpNumber=vpinstance.vpNumber,
                                                           statusMediaTimeStamp=mediainstance.mediaTimeStamp,
                                                           statusMediaMillisSinceEpoch=mediainstance.mediaMillisSinceEpoch)
            tagstatusinstance.statusValValueEvaluated = processedtag.valValueEvaluated
            tagstatusinstance.statusTagStateEvaluated = processedtag.tagStateEvaluated
            tagstatusinstance.save()
        except TagStatusTable.DoesNotExist:
            TagStatusTable.objects.create(processedTag=processedtag, statusTagNumber=taginstance.tagNumber,
                                          statusTagDescription=taginstance.tagDescription,
                                          statusVpNumber=vpinstance.vpNumber,
                                          statusVpDescription=vpinstance.vpDescription,
                                          statusValValueEvaluated=processedtag.valValueEvaluated,
                                          statusTagUnit=taginstance.tagUnit,
                                          statusMediaTimeStamp=mediainstance.mediaTimeStamp,
                                          statusTagStateEvaluated=processedtag.tagStateEvaluated,
                                          statusMediaMillisSinceEpoch=mediainstance.mediaMillisSinceEpoch)
        qtyoftagsinavp = Tag.objects.filter(vp__asset__assetOwner=request.user).filter(tagIsActive=True).filter(
            vp=vpinstance).count()
        qtyofprocessedtagsinamedia = ProcessedTag.objects.filter(media=mediainstance).count()
        alltagsinmediaprocessed = 0
        if qtyoftagsinavp == qtyofprocessedtagsinamedia:
            mediaprocessed = Media.objects.get(id=mediainstance.pk)
            mediaprocessed.mediaProcessed = True
            mediaprocessed.mediaStateEvaluated = processedtag.tagStateEvaluated
            mediaprocessed.save()
            alltagsinmediaprocessed = 1
        else:
            mediaprocessed = Media.objects.get(id=mediainstance.pk)
            mediaprocessed.mediaProcessed = False
            mediaprocessed.mediaStateEvaluated = processedtag.tagStateEvaluated
            mediaprocessed.save()

        return HttpResponse(
            json.dumps({"result": alltagsinmediaprocessed}),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json"
        )


@login_required
@user_passes_test(group_check)
def TagStatusView(request):
    if request.user.is_authenticated:
        try:
            loaddcicfg(request)
        except ClientError as e:
            error_code = e
        startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
            (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
            (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        new_enddate = enddate + timedelta(days=1)
        startdateformatted = urllib.quote(startdate.strftime('%Y-%m-%d %H:%M:%S %z'))
        enddateformatted = urllib.quote(enddate.strftime('%Y-%m-%d %H:%M:%S %z'))
        processedtags = TagStatusTable.objects.filter(processedTag__media__vp__asset__assetOwner=request.user).filter(
            statusMediaTimeStamp__range=[startdate, new_enddate]).order_by('statusMediaMillisSinceEpoch')
        listofprocessedtagsnumbers = processedtags.order_by('statusTagNumber', 'statusMediaMillisSinceEpoch').distinct(
            'statusTagNumber')
        tagsselectedfromlist = listofprocessedtagsnumbers.order_by('statusTagNumber').values_list('statusTagNumber',
                                                                                                  flat=True)
        tagsselected = request.GET.getlist('tagsselected', default=None)
        tags = Tag.objects.filter(vp__asset__assetOwner=request.user)
        if not tagsselected:
            tagsselected = tagsselectedfromlist
        else:
            tagsselected = listofprocessedtagsnumbers.filter(statusTagNumber__in=tagsselected).order_by(
                'statusTagNumber').values_list('statusTagNumber', flat=True)
        qtyoftagsselected = tagsselected.count()

        sort = request.GET.get('sort', '-statusMediaTimeStamp')
        linesperpage = request.GET.get('linesperpage', 15)
        tagstatustable = TagStatusTableClass(
            TagStatusTable.objects.filter(processedTag__media__vp__asset__assetOwner=request.user).filter(
                statusMediaTimeStamp__range=[startdate, new_enddate]).filter(statusTagNumber__in=tagsselected).order_by(
                sort))
        tagstatustable.paginate(page=request.GET.get('page', 1), per_page=linesperpage)
        request.session['startdate'] = startdateformatted
        request.session['enddate'] = enddateformatted
        return render(request, 'tagstatus.html', {'tagstatustable': tagstatustable,
                                                  'start': startdateformatted,
                                                  'end': enddateformatted,
                                                  'tags': tags,
                                                  'tagsselected': tagsselected,
                                                  'qtyoftagsselected': qtyoftagsselected,
                                                  'linesperpage': linesperpage,
                                                  'processedtags': processedtags,
                                                  'listofprocessedtagsnumbers': listofprocessedtagsnumbers,
                                                  'tablesort': sort,
                                                  })
    else:
        return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def export_tagstatus_csv(request):
    if request.method == 'GET':
        startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
            (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
            (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        new_enddate = enddate + timedelta(days=1)
        tagsselected = request.GET.getlist('tagsselected', default=None)
        sort = request.GET.get('sort', '-statusMediaTimeStamp')
        tagsstatustablequeryset = TagStatusTable.objects.filter(
            processedTag__media__vp__asset__assetOwner=request.user).filter(
            statusMediaTimeStamp__range=[startdate, new_enddate]).filter(statusTagNumber__in=tagsselected).order_by(
            sort)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="MyMensorTagStatusTable.csv"'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
        writer.writerow([
            smart_str(u"TAG"),
            smart_str(u"TAG Description"),
            smart_str(u"VP"),
            smart_str(u"VP Description"),
            smart_str(u"Value"),
            smart_str(u"Unit"),
            smart_str(u"Media Time"),
            smart_str(u"Processing Time"),
            smart_str(u"Status"),
        ])
        for obj in tagsstatustablequeryset:
            writer.writerow([
                smart_str(obj.statusTagNumber),
                smart_str(obj.statusTagDescription),
                smart_str(obj.statusVpNumber),
                smart_str(obj.statusVpDescription),
                smart_str(obj.statusValValueEvaluated),
                smart_str(obj.statusTagUnit),
                smart_str(obj.statusMediaTimeStamp),
                smart_str(obj.statusDBTimeStamp),
                smart_str(obj.statusTagStateEvaluated),
            ])
        return response
    else:
        return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def tagAnalysisView(request):
    if request.user.is_authenticated:
        try:
            loaddcicfg(request)
        except ClientError as e:
            error_code = e
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
            (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
            (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
        new_enddate = enddate + timedelta(days=1)
        startdateformatted = urllib.quote(startdate.strftime('%Y-%m-%d %H:%M:%S %z'))
        enddateformatted = urllib.quote(enddate.strftime('%Y-%m-%d %H:%M:%S %z'))
        medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpIsActive=True).filter(
            mediaProcessed=True).filter(mediaTimeStamp__range=[startdate, new_enddate])
        for media in medias:
            media.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                    Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                            'Key': media.mediaObjectS3Key},
                                                                    ExpiresIn=3600)

        processedtags = TagStatusTable.objects.filter(processedTag__media__vp__asset__assetOwner=request.user).filter(
            statusMediaTimeStamp__range=[startdate, new_enddate]).order_by('statusMediaMillisSinceEpoch')
        listofprocessedtagsnumbers = processedtags.order_by('statusTagNumber', 'statusMediaMillisSinceEpoch').distinct(
            'statusTagNumber')
        tagsselectedfromlist = listofprocessedtagsnumbers.order_by('statusTagNumber').values_list('statusTagNumber',
                                                                                                  flat=True)
        tagsselected = request.GET.getlist('tagsselected', default=None)
        tags = Tag.objects.filter(vp__asset__assetOwner=request.user)
        if not tagsselected:
            tagsselected = tagsselectedfromlist
        else:
            tagsselected = listofprocessedtagsnumbers.filter(statusTagNumber__in=tagsselected).order_by(
                'statusTagNumber').values_list('statusTagNumber', flat=True)
        qtyoftagsselected = tagsselected.count()
        request.session['startdate'] = startdateformatted
        request.session['enddate'] = enddateformatted
        return render(request, 'taganalysis.html',
                      {'processedtags': processedtags, 'listofprocessedtagsnumbers': listofprocessedtagsnumbers,
                       'tagsselected': tagsselected, 'start': startdateformatted, 'end': enddateformatted,
                       'medias': medias, 'tags': tags, 'qtyoftagsselected': qtyoftagsselected})
    else:
        return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def mobileBackupFormView(request):
    try:
        loaddcicfg(request)
    except ClientError as e:
        error_code = e

    backupinstance = MobileSetupBackup.objects.filter(backupOwner=request.user).filter(
        backupName=request.user.username + "_backup").order_by('backupDBTimeStamp').last()

    return render(request, 'mobilebackup.html', {'backupinstance': backupinstance})


@login_required
@user_passes_test(group_check)
def createdcicfgbackup(request):
    if request.method == 'POST':
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        usernameEncoded = "usrcfg/" + urllib.quote(request.user.username)
        keys_to_backup = s3Client.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=usernameEncoded)
        s3 = session.resource('s3')
        bucket = s3.Bucket(AWS_S3_BUCKET_NAME)
        try:
            for key_to_backup in keys_to_backup['Contents']:
                if "_backup" not in key_to_backup['Key']:
                    if key_to_backup['Key'] == usernameEncoded:
                        replace = usernameEncoded
                        withstring = usernameEncoded + "_backup"
                        newprefix, found, endpart = key_to_backup['Key'].partition(replace)
                        newprefix += withstring + endpart
                        obj = bucket.Object(newprefix)
                        obj.copy_from(CopySource=AWS_S3_BUCKET_NAME + '/' + key_to_backup['Key'])
                        backupinstance = MobileSetupBackup(backupOwner=request.user)
                        backupinstance.backupDescription = "Manual user-requested backup"
                        backupinstance.backupName = request.user.username + "_backup"
                        backupinstance.save()
                        return HttpResponse(
                            json.dumps({"result": "backup_saved"}),
                            content_type="application/json",
                            status=200
                        )
            return HttpResponse(
                json.dumps(keys_to_backup['Contents']),
                content_type="application/json",
                status=400
            )
        except ClientError as e:
            error_code = e
            return HttpResponse(
                json.dumps({"error_code": error_code}),
                content_type="application/json",
                status=400
            )
    else:
        return HttpResponse(
            json.dumps({"nothing": "nothing happened"}),
            content_type="application/json",
            status=400
        )


@login_required
@user_passes_test(group_check)
def restoredcicfgbackup(request):
    if request.method == 'POST':
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        usernameEncoded = "usrcfg/" + urllib.quote(request.user.username)
        keys_to_backup = s3Client.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=usernameEncoded + "_backup")
        s3 = session.resource('s3')
        bucket = s3.Bucket(AWS_S3_BUCKET_NAME)
        try:
            for key_to_backup in keys_to_backup['Contents']:
                replace = usernameEncoded + "_backup"
                withstring = usernameEncoded
                newprefix, found, endpart = key_to_backup['Key'].partition(replace)
                newprefix += withstring + endpart
                obj = bucket.Object(newprefix)
                obj.copy_from(CopySource=AWS_S3_BUCKET_NAME + '/' + key_to_backup['Key'])
            return HttpResponse(
                json.dumps({"result": "backup_restored"}),
                content_type="application/json",
                status=200
            )
        except ClientError as e:
            error_code = e
            return HttpResponse(
                json.dumps({"error_code": error_code}),
                content_type="application/json",
                status=400
            )
    else:
        return HttpResponse(
            json.dumps({"nothing": "nothing happened"}),
            content_type="application/json",
            status=400
        )


@login_required
@user_passes_test(group_check)
def tagsprocessedinthismedia(request):
    if request.method == 'POST':
        mediaid = int(request.POST.get('mediaid'))
        mediainstance = Media.objects.get(pk=mediaid)
        listofprocessedtags = ProcessedTag.objects.filter(media=mediainstance).values('id')
        listoftagsnumbers = TagStatusTable.objects.filter(processedTag__in=listofprocessedtags).values(
            'statusTagNumber')
        return JsonResponse({'result': list(listoftagsnumbers)})
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json",
            status=400
        )


@login_required
@user_passes_test(group_check)
def locofthismedia(request):
    if request.method == 'POST':
        mediaid = int(request.POST.get('mediaid'))
        mediainstance = Media.objects.get(pk=mediaid)
        return HttpResponse(
            json.dumps({'mediaLatitude': mediainstance.mediaLatitude, 'mediaLongitude': mediainstance.mediaLongitude,
                        'mediaLocPrecisionInMeters': mediainstance.mediaLocPrecisionInMeters}),
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
@user_passes_test(group_check)
def vpDetailView(request):
    if request.user.is_authenticated:
        mediascount = Media.objects.filter(vp__asset__assetOwner=request.user).count()
        if mediascount > 0:
            try:
                loaddcicfg(request)
            except ClientError as e:
                error_code = e
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3Client = session.client('s3')
            startdate = parse(urllib.unquote(request.GET.get('startdate', request.session.get('startdate', urllib.quote(
                (datetime.now(pytz.utc) - timedelta(days=29)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
            enddate = parse(urllib.unquote(request.GET.get('enddate', request.session.get('enddate', urllib.quote(
                (datetime.now(pytz.utc)).strftime('%Y-%m-%d %H:%M:%S %z'))))), yearfirst=True)
            new_enddate = enddate + timedelta(days=1)
            startdateformatted = startdate.strftime('%Y-%m-%d %H:%M:%S %z')
            enddateformatted = enddate.strftime('%Y-%m-%d %H:%M:%S %z')
            vpselected = int(request.GET.get('vpselected', 0))
            mediaselected = int(request.GET.get('mediaselected', 0))
            medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpNumber=vpselected).filter(
                mediaTimeStamp__range=[startdate, new_enddate]).order_by('mediaMillisSinceEpoch')
            if not medias:
                medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpIsActive=True).filter(
                    vp__vpNumber=vpselected).order_by(
                    'mediaMillisSinceEpoch')
                if not medias:
                    medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                        vp__vpIsActive=True).order_by('mediaMillisSinceEpoch')
                    lastmediainstance = medias.last()
                    vpoflastmediainstance = lastmediainstance.vp
                    vpselected = vpoflastmediainstance.vpNumber
                    medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(
                        vp__vpIsActive=True).filter(vp__vpNumber=vpselected).order_by(
                        'mediaMillisSinceEpoch')
                recalcend = medias.last().mediaTimeStamp
                recalcstart = recalcend - timedelta(days=29)
                startdateformatted = recalcstart.strftime('%Y-%m-%d')
                enddateformatted = recalcend.strftime('%Y-%m-%d')
                vps = Vp.objects.filter(asset__vp__media__isnull=False).filter(asset__assetOwner=request.user).filter(
                    media__mediaTimeStamp__range=[startdate, new_enddate]).filter(vpIsActive=True).order_by(
                    'vpNumber').distinct()
                mediaspks = medias.values_list('id', flat=True)
                if mediaselected == 0:
                    mediaselected = medias.first().pk
                if mediaselected not in mediaspks:
                    mediaselected = medias.first().pk
            else:
                mediaspks = medias.values_list('id', flat=True)
                vps = Vp.objects.filter(asset__vp__media__isnull=False).filter(asset__assetOwner=request.user).filter(
                    media__mediaTimeStamp__range=[startdate, new_enddate]).filter(vpIsActive=True).order_by(
                    'vpNumber').distinct()
                if mediaselected == 0:
                    mediaselected = medias.first().pk
                if mediaselected not in mediaspks:
                    mediaselected = medias.first().pk
            mediainstance = Media.objects.get(pk=mediaselected)
            mediainstance.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                            Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                                    'Key': mediainstance.mediaObjectS3Key},
                                                                            ExpiresIn=3600)
            assetvps = Vp.objects.filter(asset__assetOwner=request.user).filter(vpIsActive=True).order_by('vpNumber')
            request.session['startdate'] = startdateformatted
            request.session['enddate'] = enddateformatted
            return render(request, 'vpdetail.html', {'vpselected': vpselected,
                                                     'vps': vps,
                                                     'assetvps': assetvps,
                                                     'mediaselected': mediaselected,
                                                     'start': startdateformatted,
                                                     'end': enddateformatted,
                                                     'medias': medias,
                                                     'mediaObjectS3Key': mediainstance.mediaObjectS3Key,
                                                     'mediaStorageURL': mediainstance.mediaStorageURL,
                                                     'mediaContentType': mediainstance.mediaContentType,
                                                     'mediaArIsOn': mediainstance.mediaArIsOn,
                                                     'mediaTimeIsCertified': mediainstance.mediaTimeIsCertified,
                                                     'mediaLocIsCertified': mediainstance.mediaLocIsCertified,
                                                     'mediaTimeStamp': mediainstance.mediaTimeStamp,
                                                     'mediaSha256': mediainstance.mediaSha256,
                                                     'mediaProcessed': mediainstance.mediaProcessed,
                                                     'loclatitude': mediainstance.mediaLatitude,
                                                     'loclongitude': mediainstance.mediaLongitude,
                                                     'locprecisioninm': mediainstance.mediaLocPrecisionInMeters,
                                                     'mediaRemark': mediainstance.mediaRemark,
                                                     })
        else:
            return render(request, 'index.html')
    else:
        return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def deletemedia(request):
    if request.method == 'POST':
        mediaid = int(request.POST.get('mediaid'))
        mediainstance = Media.objects.get(pk=mediaid)
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        try:
            responseS3 = s3Client.delete_object(Bucket=AWS_S3_BUCKET_NAME,
                                                Key=mediainstance.mediaObjectS3Key)
            responseDJ = mediainstance.delete()
        except ClientError as e:
            error_code = e
            return HttpResponse(
                json.dumps({"error": error_code, "responseS3": responseS3, "responseDJ": responseDJ}),
                content_type="application/json",
                status=400
            )
        return HttpResponse(
            json.dumps({"responseS3": responseS3, "responseDJ": responseDJ}),
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
@user_passes_test(group_check)
def movemedia(request):
    if request.method == 'POST':
        mediaid = int(request.POST.get('mediaid'))
        movetovpnumber = int(request.POST.get('movetovpnumber'))
        mediainstance = Media.objects.get(pk=mediaid)
        vpinstance = Vp.objects.filter(asset__assetOwner=request.user).filter(vpNumber=movetovpnumber).get()
        mediainstance.vp = vpinstance
        mediainstance.mediaVpNumber = vpinstance.vpNumber
        try:
            mediainstance.save()
        except:
            return HttpResponse(
                json.dumps({"error": "not saved"}),
                content_type="application/json",
                status=400
            )

        return HttpResponse(
            json.dumps({"success": "seccess"}),
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
@user_passes_test(group_check)
def twtmain(request):
    """
    main view of app, either login page or info page
    """
    # if we haven't authorised yet, direct to login page
    if twtcheck_key(request):
        twitterAccount = TwitterAccount.objects.get(twtOwner=request.user)
        twitter_api = Twython(TWITTER_KEY, TWITTER_SECRET, twitterAccount.twtAccessTokenKey,
                              twitterAccount.twtAccessTokenSecret)
        user = twitter_api.verify_credentials()
        return render(request, 'twtinfo.html', {'twtuser': user})
    else:
        return render(request, 'twtmain.html')


@login_required
@user_passes_test(group_check)
def twtunauth(request):
    """
    logout and remove all session data
    """
    if twtcheck_key(request):
        try:
            request.session.delete('access_key_tw')
            request.session.delete('access_secret_tw')
        except KeyError:
            pass
        twtAcc = TwitterAccount.objects.get(twtOwner=request.user)
        twtAcc.delete()
    return HttpResponseRedirect(reverse('twtmain'))


@login_required
@user_passes_test(group_check)
def twtinfo(request):
    """
    display some user info to show we have authenticated successfully
    """
    if twtcheck_key(request):
        twitterAccount = TwitterAccount.objects.get(twtOwner=request.user)
        twitter_api = Twython(TWITTER_KEY, TWITTER_SECRET, twitterAccount.twtAccessTokenKey,
                              twitterAccount.twtAccessTokenSecret)
        user = twitter_api.verify_credentials()
        return render(request, 'twtinfo.html', {'twtuser': user})
    else:
        return HttpResponseRedirect(reverse('twtmain'))


@login_required
@user_passes_test(group_check)
def twtauth(request):
    twitter_api = Twython(TWITTER_KEY, TWITTER_SECRET)
    auth = twitter_api.get_authentication_tokens(callback_url='https://app.mymensor.com/twtoauthcallback')
    response = HttpResponseRedirect(auth['auth_url'])
    request.session['oauth_token'] = auth['oauth_token']
    request.session['oauth_token_secret'] = auth['oauth_token_secret']
    return response


@login_required
@user_passes_test(group_check)
def twtcallback(request):
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.session['oauth_token']
    oauth_token_secret = request.session['oauth_token_secret']
    twitter_api = Twython(TWITTER_KEY, TWITTER_SECRET, oauth_token, oauth_token_secret)
    final_step = twitter_api.get_authorized_tokens(oauth_verifier)
    request.session['access_key_tw'] = final_step['oauth_token']
    request.session['access_secret_tw'] = final_step['oauth_token_secret']
    twitteraccount, created = TwitterAccount.objects.get_or_create(twtOwner=request.user)
    twitteraccount.twtAccessTokenKey = final_step['oauth_token']
    twitteraccount.twtAccessTokenSecret = final_step['oauth_token_secret']
    twitteraccount.save()
    return HttpResponseRedirect(reverse('twtmain'))


@login_required
@user_passes_test(group_check)
def twtcheck_key(request):
    """
    Check to see if we already have an access_key stored, if we do then we have already gone through
    OAuth. If not then we haven't and we probably need to.
    """
    try:
        access_key = request.session.get('access_key_tw', None)
    except KeyError:
        access_key = None
    try:
        twtAcc = TwitterAccount.objects.get(twtOwner=request.user)
        access_key = twtAcc.twtAccessTokenKey
    except:
        access_key = None
    if not access_key:
        return False
    return True


@login_required
@user_passes_test(group_check)
def twtget_api(request):
    try:
        access_key = request.session['access_key_tw']
        access_secret = request.session['access_secret_tw']
    except KeyError:
        twtAcc = TwitterAccount.objects.get(twtOwner=request.user)
        access_key = twtAcc.twtAccessTokenKey
        access_secret = twtAcc.twtAccessTokenSecret
    twitter_api = Twython(TWITTER_KEY, TWITTER_SECRET, access_key, access_secret)
    return twitter_api


@login_required
@user_passes_test(group_check)
def fbmain(request):
    mymensoruserID = request.user.id
    return render(request, 'fbmain.html', {'mymensoruserID': mymensoruserID})


@login_required
@user_passes_test(group_check)
def fbsecstageauth(request):
    if request.method == 'POST':
        fbUserID = request.POST.get('fbUserID')
        fbUserName = request.POST.get('fbUserName')
        shrtAccessToken = request.POST.get('fbAccessToken')
        shrtAccessTokenSignRqst = request.POST.get('fbAccTknSignedRequest')
        mymensorUserID = request.POST.get('mymensorUserID')
        params = {'grant_type': 'fb_exchange_token', 'client_id': FB_APP_ID, 'client_secret': FB_APP_SECRET,
                  'fb_exchange_token': shrtAccessToken}
        longlivetokenresponse = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        if longlivetokenresponse.status_code == 200:
            timenow = datetime.now(pytz.utc)
            data = longlivetokenresponse.json()
            facebookaccount, created = FacebookAccount.objects.get_or_create(fbOwner_id=mymensorUserID,
                                                                             fbUserId=fbUserID,
                                                                             fbUserName=fbUserName)
            facebookaccount.fbShortTermAccesToken = shrtAccessToken
            facebookaccount.fbShortTermAccesTokenSignedRequest = shrtAccessTokenSignRqst
            facebookaccount.fbLongTermAccesToken = data['access_token']
            facebookaccount.fbLongTermAccesTokenIssuedAt = timenow
            facebookaccount.fbLongTermAccesTokenExpiresIn = data['expires_in']
            facebookaccount.save()
            return HttpResponse(
                longlivetokenresponse,
                content_type="application/json",
                status=200
            )
        else:
            return HttpResponse(
                json.dumps({"Error": "error when retrieving long lived token"}),
                content_type="application/json",
                status=longlivetokenresponse.status_code
            )
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json",
            status=400
        )


@login_required
@user_passes_test(group_check)
def fbsecstagelogout(request):
    if request.method == 'POST':
        fbUserID = request.POST.get('fbUserID')
        fbUserName = request.POST.get('fbUserName')
        mymensorUserID = request.POST.get('mymensorUserID')
        facebookaccount = FacebookAccount.objects.get(fbOwner_id=mymensorUserID, fbUserId=fbUserID,
                                                      fbUserName=fbUserName)
        facebookaccount.delete()
        return HttpResponse(
            json.dumps({"Sucess": "facebook account deleted"}),
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
@user_passes_test(group_check)
def subscription(request):
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
        try:
            btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
            btprice = BraintreePrice.objects.get(pk=btsubscription.braintreeprice_id)
            btmercht = BraintreeMerchant.objects.get(pk=btprice.braintreemerchant_id)
            currentbtsubstatus = braintree.Subscription.find(btsubscription.braintreesubscriptionSubscriptionId)
        except:
            btsubscription = None
            btprice = None
            btmercht = None
            currentbtsubstatus = None
        currentAsset = Asset.objects.get(assetOwner=request.user)
        dateofendoftrialbeforesubscription = currentAsset.assetDateOfEndEfTrialBeforeSubscription
        currentuserplan = currentAsset.assetMyMensorPlan
        # put here the control to show or not the change plan button
        mediaqty = Media.objects.filter(vp__asset__assetOwner=request.user).count()
        tagqty = Tag.objects.filter(vp__asset__assetOwner=request.user).count()
        processedtagqty = ProcessedTag.objects.filter(tag__vp__asset__assetOwner=request.user).count()
        swalchgbtntitle = _('Really Change Plan?')
        swalchgbtntext = _(
            'You will change plan immediately and in the next monthly payment you will be charged the new subscription rate, in the same currency as you pay now. There will be no prorating for downgrades in between billing cycles.')
        swalchgbtnconfirmButtonText = _('Confirm')
        swalchgbtncancelButtonText = _('Cancel')
        swalchgbtnsuccesstitle = _("Done!")
        swalchgbtncanceltitle = _("No change!")
        return render(request, 'subscription.html',
                      {'userloggedin': request.user, 'btcustomer': btcustomer, 'btprice': btprice, 'btmercht': btmercht,
                       'btsubscription': btsubscription, 'currentuserplan': currentuserplan,
                       'currentbtsubstatus': currentbtsubstatus,
                       'dateofendoftrialbeforesubscription': dateofendoftrialbeforesubscription,
                       'swalchgbtntitle': swalchgbtntitle, 'swalchgbtntext': swalchgbtntext,
                       'swalchgbtnconfirmButtonText': swalchgbtnconfirmButtonText,
                       'swalchgbtncancelButtonText': swalchgbtncancelButtonText,
                       'swalchgbtnsuccesstitle': swalchgbtnsuccesstitle, 'swalchgbtncanceltitle': swalchgbtncanceltitle,
                       'mediaqty': mediaqty, 'tagqty': tagqty, 'processedtagqty': processedtagqty})
    return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def completereg(request):
    if request.method=="POST":
        try:
            currentUser = User.objects.get(id=request.user.id)
            currentUser.first_name = request.POST.get('first_name')
            currentUser.last_name = request.POST.get('last_name')
            currentUser.save()
        except:
            return HttpResponse(status=404)
        try:
            currentAsset = Asset.objects.get(assetOwner=request.user)
            currentAsset.assetGeoIpResponse = request.POST.get('assetGeoIpResponse')
            currentAsset.assetCountryGeoIp = request.POST.get('assetCountryGeoIp')
            currentAsset.assetIpGeoIp = request.POST.get('assetIpGeoIp')
            currentAsset.save()
        except:
            return HttpResponse(status=404)
        return HttpResponse(status=200)
    return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def changeplan(request):
    if request.method == "GET":
        currentAsset = Asset.objects.get(assetOwner=request.user)
        currentuserplan = currentAsset.assetMyMensorPlan
        if currentuserplan == "MyMensor Media and Data":
            currentAsset.assetMyMensorPlan = "MyMensor Media"
            currentAsset.save()
        elif currentuserplan == "MyMensor Media":
            currentAsset.assetMyMensorPlan = "MyMensor Media and Data"
            currentAsset.save()
        return subscription(request)
    return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def markerdownload(request):
    if request.method == "GET":
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3Client = session.client('s3')
        stdmrkurl1 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                           'Key': 'markers/standard/MyMensor StandardMarkers 20mm 10 to 33.png'},
                                                     ExpiresIn=3600)
        stdmrkurl2 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                           'Key': 'markers/standard/MyMensor StandardMarkers 20mm 34 to 39.png'},
                                                     ExpiresIn=3600)
        supermrkurl1 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 10-11-12.png'},
                                                       ExpiresIn=3600)
        supermrkurl2 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 13-14-15.png'},
                                                       ExpiresIn=3600)
        supermrkurl3 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 16-17-18.png'},
                                                       ExpiresIn=3600)
        supermrkurl4 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 19-20-21.png'},
                                                       ExpiresIn=3600)
        supermrkurl5 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 22-23-24.png'},
                                                       ExpiresIn=3600)
        supermrkurl6 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 25-26-27.png'},
                                                       ExpiresIn=3600)
        supermrkurl7 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 28-29-30.png'},
                                                       ExpiresIn=3600)
        supermrkurl8 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 31-32-33.png'},
                                                       ExpiresIn=3600)
        supermrkurl9 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                             'Key': 'markers/super/MyMensor SuperMarkers 60mm 34-35-36.png'},
                                                       ExpiresIn=3600)
        supermrkurl10 = s3Client.generate_presigned_url('get_object', Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                              'Key': 'markers/super/MyMensor SuperMarkers 60mm 37-38-39.png'},
                                                        ExpiresIn=3600)
        return render(request, 'downloadmarker.html',
                      {'stdmrkurl1': stdmrkurl1, 'stdmrkurl2': stdmrkurl2, 'supermrkurl1': supermrkurl1,
                       'supermrkurl2': supermrkurl2, 'supermrkurl3': supermrkurl3,
                       'supermrkurl4': supermrkurl4, 'supermrkurl5': supermrkurl5, 'supermrkurl6': supermrkurl6,
                       'supermrkurl7': supermrkurl7, 'supermrkurl8': supermrkurl8,
                       'supermrkurl9': supermrkurl9, 'supermrkurl10': supermrkurl10})
    return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def createmobileonlyuser(request):
    if request.method == "GET":
        succesful = False
        mobonlyuser = None
        try:
            mobonlyuser = MobileOnlyUser.objects.get(mobileOnlyUserOwner=request.user)
            succesful = True
        except:
            return render(request, 'createmobileonlyuserresult.html',
                          {'succesful': succesful})
        if mobonlyuser:
            return render(request, 'createmobileonlyuserresult.html',
                          {'succesful': succesful, 'mobonlyuser': mobonlyuser})
        else:
            return render(request, 'createmobileonlyuserresult.html',
                          {'succesful': succesful})
    return HttpResponse(status=404)


@login_required
@user_passes_test(group_check)
def savemobileonlyuser(request):
    if request.method == 'POST':
        succesful = False
        currentusername = request.user.username
        currentuseremail = request.user.email
        mobusernamecurrentprefix = mobonlyprefix()
        mobusername = mobusernamecurrentprefix + currentusername
        mobuserplainpassword = request.POST.get('mobuserplainpassword', None)
        mobuseralreadyexists = int(request.POST.get('mobuseralreadyexists', 0))
        if all(c.isdigit() or c.islower() or c.isupper() for c in mobuserplainpassword) is not True:
            mobuserplainpassword = None
        if mobuserplainpassword is not None:
            if all(c.isdigit() for c in mobuserplainpassword):
                mobuserplainpassword = None
        if mobuserplainpassword is not None:
            if len(mobuserplainpassword) < 8:
                mobuserplainpassword = None
        if mobuserplainpassword is not None:
            if mobuseralreadyexists == 1:
                try:
                    mobonlyuser = MobileOnlyUser.objects.get(mobileOnlyUserOwner=request.user)
                    mobuser = User.objects.get(id=mobonlyuser.mobileOnlyUserAuthUserId)
                    mobuserusername = mobuser.username
                    mobuser.set_password(mobuserplainpassword)
                    mobuser.save()
                    succesful = True
                except:
                    return HttpResponse(
                        json.dumps({"succesful": succesful, "error": "exception"}),
                        content_type="application/json",
                        status=400
                    )
                return HttpResponse(
                    json.dumps({"succesful": succesful, "mobuserUsername": mobuserusername}),
                    content_type="application/json",
                    status=200
                )
            else:
                while User.objects.filter(username=mobusername).exists():
                    mobusernamecurrentprefix = mobonlyprefix()
                    mobusername = mobusernamecurrentprefix + currentusername
                try:
                    if mobusername and currentuseremail and mobuserplainpassword:
                        mobuser = User.objects.create_user(mobusername, currentuseremail, mobuserplainpassword)
                        g = Group.objects.get(name='mymARwebapp')
                        g.user_set.remove(mobuser)
                        g = Group.objects.get(name='mymARmobileapp')
                        g.user_set.add(mobuser)
                        MobileOnlyUser.objects.update_or_create(mobileOnlyUserOwner=request.user,
                                                                mobileOnlyUserPrefix=mobusernamecurrentprefix,
                                                                mobileOnlyUserAuthUserId=mobuser.id)
                        succesful = True
                    else:
                        return HttpResponse(
                            json.dumps({"succesful": succesful, "error": "password"}),
                            content_type="application/json",
                            status=400
                        )
                except:
                    return HttpResponse(
                        json.dumps({"succesful": succesful, "error": "exception"}),
                        content_type="application/json",
                        status=400
                    )
                return HttpResponse(
                    json.dumps({"succesful": succesful}),
                    content_type="application/json",
                    status=200
                )
        else:
            return HttpResponse(
                json.dumps({"succesful": succesful, "error": "password"}),
                content_type="application/json",
                status=400
            )
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json",
            status=400
        )


@login_required
@user_passes_test(group_check)
def deletemobileonlyuser(request):
    if request.method == 'POST':
        succesful = False
        mobonlyuser = MobileOnlyUser.objects.get(mobileOnlyUserOwner=request.user)
        mobuser = User.objects.get(id=mobonlyuser.mobileOnlyUserAuthUserId)
        try:
            mobuser.delete()
            mobonlyuser.delete()
        except:
            return HttpResponse(
                json.dumps({"succesful": succesful, "error": "exception"}),
                content_type="application/json",
                status=400
            )
        return HttpResponse(
            json.dumps({"succesful": succesful}),
            content_type="application/json",
            status=200
        )
    else:
        return HttpResponse(
            json.dumps({"nothing": "not happening"}),
            content_type="application/json",
            status=400
        )
