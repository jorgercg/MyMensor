import xml.etree.ElementTree as ET
import boto3, ast
from mymensorapp.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_DEFAULT_REGION
from mymensor.models import Asset
from mymensor.models import Vp as modelVp

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

    counter = 1
    for Vp in root.findall('Vp'):
        VpNumber[counter] = Vp.find('VpNumber').text
        VpDescFileSize[counter] = Vp.find('VpDescFileSize').text
        VpMarkerFileSize[counter] = Vp.find('VpMarkerFileSize').text
        VpArIsConfigured[counter] = Vp.find('VpArIsConfigured').text
        VpIsVideo[counter] = Vp.find('VpIsVideo').text
        VpXCameraDistance[counter] = Vp.find('VpXCameraDistance').text
        VpYCameraDistance[counter] = Vp.find('VpYCameraDistance').text
        VpZCameraDistance[counter] = Vp.find('VpZCameraDistance').text
        VpXCameraRotation[counter] = Vp.find('VpXCameraRotation').text
        VpYCameraRotation[counter] = Vp.find('VpYCameraRotation').text
        VpZCameraRotation[counter] = Vp.find('VpZCameraRotation').text
        VpLocDescription[counter] = Vp.find('VpLocDescription').text
        VpMarkerlessMarkerWidth[counter] = Vp.find('VpMarkerlessMarkerWidth').text
        VpMarkerlessMarkerHeigth[counter] = Vp.find('VpMarkerlessMarkerHeigth').text
        VpIsAmbiguous[counter] = Vp.find('VpIsAmbiguous').text
        VpFlashTorchIsOn[counter] = Vp.find('VpFlashTorchIsOn').text
        VpIsSuperSingle[counter] = Vp.find('VpIsSuperSingle').text
        VpSuperMarkerId[counter] = Vp.find('VpSuperMarkerId').text
        VpFrequencyUnit[counter] = Vp.find('VpFrequencyUnit').text
        VpFrequencyValue[counter] = Vp.find('VpFrequencyValue').text
        counter += 1

    loadasset = Asset.objects.get(assetOwner=request.user)
    loadasset.assetNumber=int(AssetId)
    loadasset.assetDciFrequencyUnit=FrequencyUnit
    loadasset.assetDciFrequencyValue=int(FrequencyValue)
    loadasset.assetDciQtyVps=int(QtyVps)
    loadasset.assetDciTolerancePosition=int(TolerancePosition)
    loadasset.assetDciToleranceRotation=int(ToleranceRotation)
    loadasset.save()

    i = 1
    while i < counter:
        loadvp = modelVp.objects.filter(asset__assetOwner=request.user).filter(vpNumber=(i-1))
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
        loadvp.vpArIsConfigured = ast.literal_eval(VpArIsConfigured[i])
        loadvp.vpIsVideo = ast.literal_eval(VpIsVideo[i])
        loadvp.vpIsAmbiguos = ast.literal_eval(VpIsAmbiguous[i])
        loadvp.vpIsSuperSingle = ast.literal_eval(VpIsSuperSingle[i])
        loadvp.vpFlashTorchIsOn = ast.literal_eval(VpFlashTorchIsOn[i])
        loadvp.vpSuperMarkerId = int(VpSuperMarkerId[i])
        loadvp.vpFrequencyUnit = VpFrequencyUnit[i]
        loadvp.vpFrequencyValue = int(VpFrequencyValue[i])
        i += 1
    loadvp.save()
