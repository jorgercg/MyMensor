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
        AssetId = Parameters.get('AssetId')
        FrequencyUnit = Parameters.get('FrequencyUnit')
        FrequencyValue = Parameters.get('FrequencyValue')
        QtyVps = Parameters.get('QtyVps')
        TolerancePosition = Parameters.get('TolerancePosition')
        ToleranceRotation = Parameters.get('ToleranceRotation')

    counter = -1
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

    for Vp in root.findall('Vp'):
        counter += 1
        VpNumber[counter] = Vp.get('VpNumber')
        VpDescFileSize[counter] = Vp.get('VpDescFileSize')
        VpMarkerFileSize[counter] = Vp.get('VpMarkerFileSize')
        VpArIsConfigured[counter] = Vp.get('VpArIsConfigured')
        VpIsVideo[counter] = Vp.get('VpIsVideo')
        VpXCameraDistance[counter] = Vp.get('VpXCameraDistance')
        VpYCameraDistance[counter] = Vp.get('VpYCameraDistance')
        VpZCameraDistance[counter] = Vp.get('VpZCameraDistance')
        VpXCameraRotation[counter] = Vp.get('VpXCameraRotation')
        VpYCameraRotation[counter] = Vp.get('VpYCameraRotation')
        VpZCameraRotation[counter] = Vp.get('VpZCameraRotation')
        VpLocDescription[counter] = Vp.get('VpLocDescription')
        VpMarkerlessMarkerWidth[counter] = Vp.get('VpMarkerlessMarkerWidth')
        VpMarkerlessMarkerHeigth[counter] = Vp.get('VpMarkerlessMarkerHeigth')
        VpIsAmbiguous[counter] = Vp.get('VpIsAmbiguous')
        VpFlashTorchIsOn[counter] = Vp.get('VpFlashTorchIsOn')
        VpIsSuperSingle[counter] = Vp.get('VpIsSuperSingle')
        VpSuperMarkerId[counter] = Vp.get('VpSuperMarkerId')
        VpFrequencyUnit[counter] = Vp.get('VpFrequencyUnit')
        VpFrequencyValue[counter] = Vp.get('VpFrequencyValue')

    loadasset = Asset.objects.get(assetOwner=request.user)
    loadasset.assetNumber=int(AssetId)
    loadasset.assetDciFrequencyUnit=FrequencyUnit
    loadasset.assetDciFrequencyValue=int(FrequencyValue)
    loadasset.assetDciQtyVps=int(QtyVps)
    loadasset.assetDciTolerancePosition=int(TolerancePosition)
    loadasset.assetDciToleranceRotation=int(ToleranceRotation)
    loadasset.save()
    i = 0
    while i <= counter:
        loadvp = modelVp.objects.filter(asset__assetOwner=request.user).filter(vpNumber=i)
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
