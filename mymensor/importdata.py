from django.contrib.auth.models import User
import xml.etree.ElementTree as ET
import boto3, ast
from mymensorapp.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_DEFAULT_REGION
from mymensor.models import Asset
from mymensor.models import Vp as modelVp

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def loaddcicfg(request):
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    s3_object_key = request.user.username + "/cfg/1/vps/vps.xml"
    object = s3.Object(AWS_S3_BUCKET_NAME, s3_object_key)
    vpsfilecontents = object.get()['Body'].read()

    root = ET.fromstring(vpsfilecontents)

    for Parameters in root.findall('Parameters'):
        AssetId = Parameters.find('AssetId').text
        FrequencyUnit = Parameters.find('FrequencyUnit').text
        FrequencyValue = Parameters.find('FrequencyValue').text
        QtyVps = Parameters.find('QtyVps').text
        TolerancePosition = Parameters.find('TolerancePosition').text
        ToleranceRotation = Parameters.find('ToleranceRotation').text


    VpNumber = []
    VpDescFileSize = []
    VpMarkerFileSize = []
    VpArIsConfigured = []
    VpIsVideo = []
    VpXCameraDistance = []
    VpYCameraDistance = []
    VpZCameraDistance = []
    VpXCameraRotation = []
    VpYCameraRotation = []
    VpZCameraRotation = []
    VpLocDescription = []
    VpMarkerlessMarkerWidth = []
    VpMarkerlessMarkerHeigth = []
    VpIsAmbiguous = []
    VpFlashTorchIsOn = []
    VpIsSuperSingle = []
    VpSuperMarkerId = []
    VpFrequencyUnit = []
    VpFrequencyValue = []

    counter = 0
    for Vp in root.findall('Vp'):
        VpNumber.append(Vp.find('VpNumber').text)
        VpDescFileSize.append(Vp.find('VpDescFileSize').text)
        VpMarkerFileSize.append(Vp.find('VpMarkerFileSize').text)
        VpArIsConfigured.append(Vp.find('VpArIsConfigured').text)
        VpIsVideo.append(Vp.find('VpIsVideo').text)
        VpXCameraDistance.append(Vp.find('VpXCameraDistance').text)
        VpYCameraDistance.append(Vp.find('VpYCameraDistance').text)
        VpZCameraDistance.append(Vp.find('VpZCameraDistance').text)
        VpXCameraRotation.append(Vp.find('VpXCameraRotation').text)
        VpYCameraRotation.append(Vp.find('VpYCameraRotation').text)
        VpZCameraRotation.append(Vp.find('VpZCameraRotation').text)
        VpLocDescription.append(Vp.find('VpLocDescription').text)
        VpMarkerlessMarkerWidth.append(Vp.find('VpMarkerlessMarkerWidth').text)
        VpMarkerlessMarkerHeigth.append(Vp.find('VpMarkerlessMarkerHeigth').text)
        VpIsAmbiguous.append(Vp.find('VpIsAmbiguous').text)
        VpFlashTorchIsOn.append(Vp.find('VpFlashTorchIsOn').text)
        VpIsSuperSingle.append(Vp.find('VpIsSuperSingle').text)
        VpSuperMarkerId.append(Vp.find('VpSuperMarkerId').text)
        #VpFrequencyUnit.append(Vp.find('VpFrequencyUnit').text)
        #VpFrequencyValue.append(Vp.find('VpFrequencyValue').text)
        counter += 1

    loadasset = Asset.objects.get(assetOwner=request.user)
    loadasset.assetNumber=int(AssetId)
    loadasset.assetDciFrequencyUnit=FrequencyUnit
    loadasset.assetDciFrequencyValue=int(FrequencyValue)
    loadasset.assetDciQtyVps=int(QtyVps)
    loadasset.assetDciTolerancePosition=int(float(TolerancePosition))
    loadasset.assetDciToleranceRotation=int(float(ToleranceRotation))
    loadasset.save()

    i = 0
    while i < counter:
        loadvp = modelVp.objects.filter(asset__assetOwner=request.user).filter(vpNumber=i).get()
        loadvp.asset = Asset.objects.get(assetOwner=request.user)
        loadvp.vpDescription = VpLocDescription[i]
        loadvp.vpNumber = int(VpNumber[i])
        loadvp.vpIsActive = True
        loadvp.vpListNumber = int(VpNumber[i])
        loadvp.vpStdPhotoStorageURL = request.user.username + "/cfg/1/vps/dsc/descvp"+str(VpNumber[i])+".png"
        loadvp.vpStdTagDescPhotoStorageURL = request.user.username + "/cfg/1/vps/dsc/tagdescvp"+str(VpNumber[i])+".png"
        loadvp.vpStdMarkerPhotoStorageURL = request.user.username + "/cfg/1/vps/dsc/markervp"+str(VpNumber[i])+".png"
        loadvp.vpXDistance = int(VpXCameraDistance[i])
        loadvp.vpYDistance = int(VpYCameraDistance[i])
        loadvp.vpZDistance = int(VpZCameraDistance[i])
        loadvp.vpXRotation = int(VpXCameraRotation[i])
        loadvp.vpYRotation = int(VpYCameraRotation[i])
        loadvp.vpZRotation = int(VpZCameraRotation[i])
        loadvp.vpMarkerlessMarkerWidth = int(VpMarkerlessMarkerWidth[i])
        loadvp.vpMarkerlessMarkerHeigth = int(VpMarkerlessMarkerHeigth[i])
        loadvp.vpArIsConfigured = str2bool(VpArIsConfigured[i])
        loadvp.vpIsVideo = str2bool(VpIsVideo[i])
        loadvp.vpIsAmbiguos = str2bool(VpIsAmbiguous[i])
        loadvp.vpIsSuperSingle = str2bool(VpIsSuperSingle[i])
        loadvp.vpFlashTorchIsOn = str2bool(VpFlashTorchIsOn[i])
        loadvp.vpSuperMarkerId = int(VpSuperMarkerId[i])
        loadvp.vpFrequencyUnit = 0 #VpFrequencyUnit[i]
        loadvp.vpFrequencyValue = 0 #int(VpFrequencyValue[i])
        loadvp.save()
        i += 1