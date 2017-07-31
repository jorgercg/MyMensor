from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from instant.producers import publish
from mymensor.models import Asset, Vp, Tag, Media, Value, ProcessedTag, Tagbbox, AmazonS3Message, AmazonSNSNotification, \
    TagStatusTable, MobileSetupBackup, TwitterAccount, FacebookAccount, BraintreeCustomer, BraintreeSubscription, \
    MobileOnlyUser, MobileClientInstall
from mymensor.serializer import AmazonSNSNotificationSerializer
from mymensor.dcidatasync import loaddcicfg, writedcicfg
from mymensorapp.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, TWITTER_KEY, \
    TWITTER_SECRET, FB_APP_SECRET, FB_APP_ID
import json, boto3, urllib
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, date
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
            mediaObjectS3KeyEncoded = urllib.quote('cap/'+messagemymuser+'/'+mediaObjectS3partialKey)
            mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                              Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                      'Key': mediaObjectS3KeyEncoded},
                                                              ExpiresIn=3600)
            mediaStorageURLHeader = mediaStorageURL
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3 = session.resource('s3')
            object = s3.Object(AWS_S3_BUCKET_NAME, mediaObjectS3KeyEncoded)
            object.load()
            obj_metadata = object.metadata
            mediaCheckURL = u''.join(['https://app.mymensor.com/mc/']) + str(messagetype)
            mediaCheckURL = mediaCheckURL + '/' + mediaObjectS3KeyEncoded + '/' + requestsignature + '/'
            if object.content_type == 'video/mp4':
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKey.replace('_v_','_t_')
                mediaObjectS3partialKeyForThumbnail = mediaObjectS3partialKeyForThumbnail.replace('.mp4','.jpg')
                mediaObjectS3KeyEncodedHeader = urllib.quote('cap/' + messagemymuser + '/' + mediaObjectS3partialKeyForThumbnail)
                mediaStorageURLHeader = s3Client.generate_presigned_url('get_object',
                                                              Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                      'Key': mediaObjectS3KeyEncodedHeader},
                                                              ExpiresIn=3600)
            if obj_metadata['sha-256'] == requestsignature:
                return render(request, 'landing.html', {'mediaStorageURL': mediaStorageURL,
                                                        'mediaStorageURLHeader': mediaStorageURLHeader,
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

            if media_received.mediaSha256 in listofmediaindb:
                return HttpResponse(status=200)
            else:
                media_received.save()
            publish(message='New media arrived on server', event_class="NewMedia", channel="my_mensor_public",
                    data={"username": media_received.mediaMymensorAccount})
            vp_received = media_received.vp
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3Client = session.client('s3')
            url = s3Client.generate_presigned_url('get_object',
                                                  Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                          'Key': media_received.mediaObjectS3Key},
                                                  ExpiresIn=3600)
            landingurl = 'https://app.mymensor.com/landing/?type=1&key='+media_received.mediaObjectS3Key+'&signature='+media_received.mediaSha256
            mcurl= 'https://app.mymensor.com/mc/1/'+media_received.mediaObjectS3Key+'/'+media_received.mediaSha256
            if (vp_received.vpShareEmail is not None) and (len(vp_received.vpShareEmail)>0):
                emailsender = User.objects.get(username=media_received.mediaMymensorAccount)
                if media_received.mediaContentType == "image/jpeg":
                    if media_received.mediaRemark is None:
                        mediaRemarkToBeShared = unicode(_('Image Shared by MyMensor Bot \n\n')) + mcurl + unicode(
                            _('\n\n(Sent by MyMensor Bot - folow the link above to check the image on mymensor.com) \n'))
                    else:
                        mediaRemarkToBeShared = media_received.mediaRemark + '\n\n' + mcurl + unicode(
                            _('\n\n(Sent by MyMensor Bot - folow the link above to check the image on mymensor.com) \n'))
                    filename = 'temp.jpg'
                    requesturl = requests.get(url, stream=True)
                    if requesturl.status_code == 200:
                        with open(filename, 'wb') as image:
                            for chunk in requesturl:
                                image.write(chunk)
                        image = open(filename, 'rb')
                        subject = _("MyMensor Bot sent you this PHOTO by request of ")+emailsender.username
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
                            _('\n\n(Sent by MyMensor Bot - folow the link above to check the video on mymensor.com) \n'))
                    else:
                        mediaRemarkToBeShared = media_received.mediaRemark + '\n\n' + mcurl + unicode(
                            _('\n\n(Sent by MyMensor Bot - folow the link above to check the video on mymensor.com) \n'))
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
                    if media_received.mediaContentType == "image/jpeg":
                        if media_received.mediaRemark is None:
                            mediaRemarkToBeSharedToTwitter = unicode(_('Image Shared by MyMensor Bot \n\n Use the link to check the media: \n\n')) + mcurl
                        else:
                            mediaRemarkToBeSharedToTwitter = media_received.mediaRemark + '\n\n Use the link to check the media: \n\n' + mcurl
                        filename = 'temp.jpg'
                        requesturl = requests.get(url, stream=True)
                        if requesturl.status_code == 200:
                            with open(filename, 'wb') as image:
                                for chunk in requesturl:
                                    image.write(chunk)
                            image = open(filename, 'rb')
                            response = twitter_api.upload_media(media=image)
                            twitter_api.update_status(status=mediaRemarkToBeSharedToTwitter, media_ids=[response['media_id']])
                            os.remove(filename)
                        else:
                            print("Unable to download media")
                    if media_received.mediaContentType == "video/mp4":
                        if media_received.mediaRemark is None:
                            mediaRemarkToBeSharedToTwitter = unicode(_('Video Shared by MyMensor Bot \n\n Use the link to check the media: \n\n')) + mcurl
                        else:
                            mediaRemarkToBeSharedToTwitter = media_received.mediaRemark + '\n\n Use the link to check the media: \n\n' + mcurl
                        filename = 'temp.mp4'
                        requesturl = requests.get(url, stream=True)
                        if requesturl.status_code == 200:
                            with open(filename, 'wb') as video:
                                for chunk in requesturl:
                                    video.write(chunk)
                            video = open(filename, 'rb')
                            response = twitter_api.upload_video(media=video, media_type='video/mp4')
                            twitter_api.update_status(status=mediaRemarkToBeSharedToTwitter,
                                                      media_ids=[response['media_id']])
                            os.remove(filename)
                        else:
                            print("Unable to download media")
            facebookAccount = None
            if vp_received.vpIsSharedToFacebook:
                try:
                    facebookAccount = FacebookAccount.objects.get(fbOwner_id=media_user_id)
                except:
                    facebookAccount = None
                if facebookAccount is not None:
                    if media_received.mediaContentType == "image/jpeg":
                        if media_received.mediaRemark is None:
                            mediaRemarkToBeSharedToFB = unicode(_('Image Shared by MyMensor Bot \n\n Use the link to check the media: \n\n')) + mcurl
                        else:
                            mediaRemarkToBeSharedToFB = media_received.mediaRemark+ '\n\n Use the link to check the media: \n\n' + mcurl
                        data = {'url': url, 'caption': mediaRemarkToBeSharedToFB,
                                'access_token': facebookAccount.fbLongTermAccesToken}
                        feedpostresponse = requests.post('https://graph.facebook.com/v2.10/me/photos', data=data)
                    if media_received.mediaContentType == "video/mp4":
                        if media_received.mediaRemark is None:
                            mediaRemarkToBeSharedToFB = unicode(_('Video Shared by MyMensor Bot \n\n Use the link to check the media: \n\n')) + mcurl
                        else:
                            mediaRemarkToBeSharedToFB = media_received.mediaRemark+ '\n\n Use the link to check the media: \n\n' + mcurl
                        data = {'file_url': url, 'description': mediaRemarkToBeSharedToFB,
                                'access_token': facebookAccount.fbLongTermAccesToken}
                        feedpostresponse = requests.post('https://graph.facebook.com/v2.10/me/videos', data=data)
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
        startdate = datetime.strptime(
            request.GET.get('startdate', (datetime.today() - timedelta(days=29)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        enddate = datetime.strptime(request.GET.get('enddate', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
        new_enddate = enddate + timedelta(days=1)
        qtypervp = int(request.GET.get('qtypervp', 5))
        vpsselected = request.GET.getlist('vpsselected', default=None)
        vps = Vp.objects.filter(asset__assetOwner=request.user).filter(vpIsActive=True).order_by('vpNumber')
        vpslist = vps
        vpsselectedfromlist = vps.values_list('vpNumber', flat=True)
        if not vpsselected:
            vpsselected = vpsselectedfromlist
        else:
            vps = vps.filter(vpNumber__in=vpsselected).order_by('vpNumber')
            vpsselected = vps.values_list('vpNumber', flat=True)

        medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpNumber__in=vpsselected).filter(
            mediaTimeStamp__range=[startdate, new_enddate]).order_by('-mediaMillisSinceEpoch')
        startdateformatted = startdate.strftime('%Y-%m-%d')
        enddateformatted = enddate.strftime('%Y-%m-%d')
        media_vpnumbers = []
        for media in medias:
            media.mediaStorageURL = s3Client.generate_presigned_url('get_object',
                                                                    Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                            'Key': media.mediaObjectS3Key},
                                                                    ExpiresIn=3600)
            media_vpnumbers.append(media.mediaVpNumber)
            if media.mediaContentType == 'video/mp4':
                mediaObjectS3KeyForThumbnail = media.mediaObjectS3Key.replace('_v_','_t_')
                mediaObjectS3KeyForThumbnail = mediaObjectS3KeyForThumbnail.replace('.mp4','.jpg')
                media.mediaThumbnailStorageURL = s3Client.generate_presigned_url('get_object',
                                                              Params={'Bucket': AWS_S3_BUCKET_NAME,
                                                                      'Key': mediaObjectS3KeyForThumbnail},
                                                              ExpiresIn=3600)
        return render(request, 'index.html',
                      {'medias': medias, 'vps': vps, 'start': startdateformatted, 'end': enddateformatted,
                       'qtypervp': qtypervp, 'vpsselected': vpsselected, 'vpslist': vpslist,
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

        mymensormobileclienttype = request.META['HTTP_FROM']
        try:
            mymclientguid = request.META['HTTP_WARNING']
        except KeyError:
            mymclientguid = "NOTSET"

        if mymclientguid == "NOTSET":
            return HttpResponse(status=401)

        assetinstance = Asset.objects.get(assetOwner=request.user)

        thirtydaysago = datetime.today() - timedelta(days=30)

        qtyofinstallactiveduringlastmonth = MobileClientInstall.objects.filter(asset=assetinstance).filter(mobileClientInstallLastAccessTimeStamp__gte=thirtydaysago).distinct('mobileClientInstallGUID').count()

        qtyofinstallevermade = MobileClientInstall.objects.filter(asset=assetinstance).distinct('mobileClientInstallGUID').count()

        mobclientinstallinstace = MobileClientInstall()
        try:
            mobclientinstallinstace = MobileClientInstall.objects.get(asset=assetinstance, mobileClientInstallGUID=mymclientguid)
            mobclientinstallinstace.mobileClientInstallLastAccessTimeStamp = datetime.utcnow()
            mobclientinstallinstace.save(force_update=True)
        except mobclientinstallinstace.DoesNotExist:
            timenow = datetime.utcnow()
            mobclientinstallinstace = MobileClientInstall(asset=assetinstance, mobileClientInstallGUID=mymclientguid, mobileClientInstallOrderNumber=qtyofinstallevermade+1, mobileClientInstallCreationTimeStamp=timenow, mobileClientInstallLastAccessTimeStamp=timenow)
            mobclientinstallinstace.save(force_insert=True)

        usergroup = 'mymARwebapp'

        token = (Token.objects.get(user_id=request.user.id)).key

        username = request.user.username

        if request.user.groups.filter(name__in=['mymARmobileapp']).exists():
            # TODO: Bring the prefix from Asset (Firstly put it there, obviusly....)
            usernameprefix = username[:7]
            username = username.replace(usernameprefix, '')
            usergroup = 'mymARmobileapp'

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
        descvpTimeStamp = obj_metadata['datetime']
    except:
        descvpTimeStamp = " "
    tags = Tag.objects.filter(vp__vpIsActive=True).filter(vp__asset__assetOwner=request.user).filter(
        vp__vpNumber=currentvp)
    tagbboxes = Tagbbox.objects.filter(tag__in=tags)
    return render(request, 'vpsetup.html',
                  {'form': form, 'vps': vps, 'currentvp': currentvp, 'descvpStorageURL': descvpStorageURL,
                   'descvpTimeStamp': descvpTimeStamp, 'tagbboxes': tagbboxes, 'tags': tags})


@login_required
@user_passes_test(group_check)
def tagSetupFormView(request):
    try:
        loaddcicfg(request)
    except ClientError as e:
        error_code = e
    currentvp = 1
    qtyvps = Vp.objects.filter(vpIsActive=True).filter(asset__assetOwner=request.user).count()
    listoftagsindatabase = Tag.objects.filter(tagIsActive=True).filter(vp__asset__assetOwner=request.user)
    qtytagsindatabase = listoftagsindatabase.count()

    if request.method == 'POST':
        currentvp = int(request.POST.get('currentvp', 1))
        currenttag = int(request.POST.get('currenttag', 1))
        qtytagsinclient = int(request.GET.get('qtytags', qtytagsindatabase))
        tag = Tag()
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
                    currenttag = listoftagsincurrentvp[0]
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
                            vpNumber=currentvp).get(), tagDescription='TAG#' + str(currenttag), tagNumber=currenttag,
                        tagQuestion='Tag question for TAG#' + str(currenttag))
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
                        vpNumber=currentvp).get(), tagDescription='TAG#' + str(currenttag), tagNumber=currenttag,
                    tagQuestion='Tag question for TAG#' + str(currenttag))
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
                        vpNumber=currentvp).get(), tagDescription='TAG#' + str(currenttag), tagNumber=currenttag,
                    tagQuestion='Tag question for TAG#' + str(currenttag))
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
        descvpTimeStamp = obj_metadata['datetime']
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
            tagbboxinstancepk = Tagbbox.objects.get(tag=taginstance).pk
        except Tagbbox.DoesNotExist:
            tagbboxinstancetmp = Tagbbox(tag=taginstance)
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
        startdate = datetime.strptime(
            request.GET.get('startdate', (datetime.today() - timedelta(days=29)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        enddate = datetime.strptime(request.GET.get('enddate', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
        new_enddate = enddate + timedelta(days=1)
        qtypervp = int(request.GET.get('qtypervp', 5))

        medias = Media.objects.filter(vp__vpIsActive=True).filter(mediaProcessed=True).filter(
            vp__asset__assetOwner=request.user).filter(mediaTimeStamp__range=[startdate, new_enddate]).order_by(
            'mediaMillisSinceEpoch')
        startdateformatted = startdate.strftime('%Y-%m-%d')
        enddateformatted = enddate.strftime('%Y-%m-%d')
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
        return render(request, 'proctagedit.html', {'medias': medias, 'vps': vps, 'tags': tags, 'values': values,
                                                    'mediasofthevaluelist': mediasofthevaluelist,
                                                    'tagsofthevaluelist': tagsofthevaluelist,
                                                    'start': startdateformatted, 'end': enddateformatted,
                                                    'qtypervp': qtypervp})


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
        startdate = datetime.strptime(
            request.GET.get('startdate', (datetime.today() - timedelta(days=29)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        enddate = datetime.strptime(request.GET.get('enddate', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
        new_enddate = enddate + timedelta(days=1)
        qtypervp = int(request.GET.get('qtypervp', 5))
        medias = Media.objects.filter(vp__asset__assetOwner=request.user).filter(vp__vpIsActive=True).filter(
            mediaProcessed=False).filter(vp__tag__isnull=False).filter(
            mediaTimeStamp__range=[startdate, new_enddate]).order_by('mediaMillisSinceEpoch').distinct()
        startdateformatted = startdate.strftime('%Y-%m-%d')
        enddateformatted = enddate.strftime('%Y-%m-%d')
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
        return render(request, 'tagprocessing.html', {'medias': medias, 'vps': vps, 'tags': tags, 'values': values,
                                                      'mediasofthevaluelist': mediasofthevaluelist,
                                                      'tagsofthevaluelist': tagsofthevaluelist,
                                                      'start': startdateformatted, 'end': enddateformatted,
                                                      'qtypervp': qtypervp})


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
        startdate = datetime.strptime(
            request.GET.get('startdate', (datetime.today() - timedelta(days=29)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        enddate = datetime.strptime(request.GET.get('enddate', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
        new_enddate = enddate + timedelta(days=1)
        startdateformatted = startdate.strftime('%Y-%m-%d')
        enddateformatted = enddate.strftime('%Y-%m-%d')
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
        startdate = datetime.strptime(
            request.GET.get('startdate', (datetime.today() - timedelta(days=29)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        enddate = datetime.strptime(request.GET.get('enddate', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
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
        startdate = datetime.strptime(
            request.GET.get('startdate', (datetime.today() - timedelta(days=29)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        enddate = datetime.strptime(request.GET.get('enddate', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
        new_enddate = enddate + timedelta(days=1)
        startdateformatted = startdate.strftime('%Y-%m-%d')
        enddateformatted = enddate.strftime('%Y-%m-%d')
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
            startdate = datetime.strptime(
                request.GET.get('startdate', (datetime.today() - timedelta(days=29)).strftime('%Y-%m-%d')), '%Y-%m-%d')
            enddate = datetime.strptime(request.GET.get('enddate', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d')
            new_enddate = enddate + timedelta(days=1)
            startdateformatted = startdate.strftime('%Y-%m-%d')
            enddateformatted = enddate.strftime('%Y-%m-%d')
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
            timenow = datetime.utcnow()
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
        btcustomer = BraintreeCustomer.objects.get(braintreecustomerOwner=request.user)
        try:
            btsubscription = BraintreeSubscription.objects.get(braintreecustomer=btcustomer)
        except:
            btsubscription = None
        currentAsset = Asset.objects.get(assetOwner=request.user)
        dateofendoftrialbeforesubscription = currentAsset.assetDateOfEndEfTrialBeforeSubscription
        return render(request, 'subscription.html', {'userloggedin': request.user, 'btcustomer': btcustomer,
                                                     'btsubscription': btsubscription,
                                                     'dateofendoftrialbeforesubscription': dateofendoftrialbeforesubscription})
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
        try:
            mobonlyuser = MobileOnlyUser.objects.get(mobileOnlyUser=request.user)
            succesful = True
        except:
            return render(request, 'createmobileonlyuserresult.html',
                          {'succesful': succesful})
        return render(request, 'createmobileonlyuserresult.html',
                      {'succesful': succesful, 'mobonlyuser': mobonlyuser})
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
                    mobonlyuser = MobileOnlyUser.objects.get(mobileOnlyUser=request.user)
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
                        MobileOnlyUser.objects.update_or_create(mobileOnlyUser=request.user,
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
        mobonlyuser = MobileOnlyUser.objects.get(mobileOnlyUser=request.user)
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
