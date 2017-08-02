import xml.etree.ElementTree as ET
import boto3, urllib
from django.contrib.staticfiles import finders
from mymensorapp.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, ASSETFILES_FOLDER
from mymensor.models import Asset
from mymensor.models import Vp as modelVp


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def bool2str(v):
    return str(v).lower()


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def loaddcicfg(request):
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    usernameEncoded = urllib.quote(request.user.username)
    s3_object_key = "usrcfg/" + usernameEncoded + "/cfg/1/vps/vps.xml"
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
        VpFrequencyUnit.append('millis')
        VpFrequencyValue.append('0')
        counter += 1

    loadasset = Asset.objects.get(assetOwner=request.user)
    loadasset.assetNumber = int(AssetId)
    loadasset.assetDciFrequencyUnit = FrequencyUnit
    loadasset.assetDciFrequencyValue = int(FrequencyValue)
    loadasset.assetDciQtyVps = int(QtyVps)
    loadasset.assetDciTolerancePosition = int(float(TolerancePosition))
    loadasset.assetDciToleranceRotation = int(float(ToleranceRotation))
    loadasset.save()

    i = 0
    while i < counter:
        loadvp = modelVp.objects.filter(asset__assetOwner=request.user).filter(vpNumber=i).get()
        loadvp.asset = Asset.objects.get(assetOwner=request.user)
        loadvp.vpDescription = VpLocDescription[i]
        loadvp.vpNumber = int(VpNumber[i])
        loadvp.vpIsActive = True
        loadvp.vpListNumber = int(VpNumber[i])
        loadvp.vpStdPhotoStorageURL = "usrcfg/" + usernameEncoded + "/cfg/1/vps/dsc/descvp" + str(VpNumber[i]) + ".png"
        loadvp.vpStdTagDescPhotoStorageURL = "usrcfg/" + usernameEncoded + "/cfg/1/vps/dsc/tagdescvp" + str(
            VpNumber[i]) + ".png"
        loadvp.vpStdMarkerPhotoStorageURL = "usrcfg/" + usernameEncoded + "/cfg/1/vps/dsc/markervp" + str(
            VpNumber[i]) + ".png"
        loadvp.vpStdPhotoFileSize = int(VpDescFileSize[i])
        loadvp.vpStdMarkerPhotoFileSize = int(VpMarkerFileSize[i])
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
        loadvp.vpFrequencyUnit = VpFrequencyUnit[i]
        loadvp.vpFrequencyValue = str(VpFrequencyValue[i])
        loadvp.save()
        i += 1


def writedcicfg(request):
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    usernameEncoded = urllib.quote(request.user.username)
    s3_object_key = "usrcfg/" + usernameEncoded + "/cfg/1/vps/vps.xml"

    vpsdata = ET.Element("VpsData")
    parameters = ET.SubElement(vpsdata, "Parameters")

    writeasset = Asset.objects.get(assetOwner=request.user)

    ET.SubElement(parameters, "AssetId").text = str(writeasset.assetNumber)
    ET.SubElement(parameters, "FrequencyUnit").text = writeasset.assetDciFrequencyUnit
    ET.SubElement(parameters, "FrequencyValue").text = str(writeasset.assetDciFrequencyValue)
    ET.SubElement(parameters, "QtyVps").text = str(writeasset.assetDciQtyVps)
    ET.SubElement(parameters, "TolerancePosition").text = str(writeasset.assetDciTolerancePosition)
    ET.SubElement(parameters, "ToleranceRotation").text = str(writeasset.assetDciToleranceRotation)

    i = 0
    while i < writeasset.assetDciQtyVps:
        writevp = modelVp.objects.filter(asset__assetOwner=request.user).filter(vpNumber=i).get()

        vp = ET.SubElement(vpsdata, "Vp")
        ET.SubElement(vp, "VpNumber").text = str(writevp.vpNumber)
        ET.SubElement(vp, "VpDescFileSize").text = str(writevp.vpStdPhotoFileSize)
        ET.SubElement(vp, "VpMarkerFileSize").text = str(writevp.vpStdMarkerPhotoFileSize)
        ET.SubElement(vp, "VpArIsConfigured").text = bool2str(writevp.vpArIsConfigured)
        ET.SubElement(vp, "VpIsVideo").text = bool2str(writevp.vpIsVideo)
        ET.SubElement(vp, "VpXCameraDistance").text = str(writevp.vpXDistance)
        ET.SubElement(vp, "VpYCameraDistance").text = str(writevp.vpYDistance)
        ET.SubElement(vp, "VpZCameraDistance").text = str(writevp.vpZDistance)
        ET.SubElement(vp, "VpXCameraRotation").text = str(writevp.vpXRotation)
        ET.SubElement(vp, "VpYCameraRotation").text = str(writevp.vpYRotation)
        ET.SubElement(vp, "VpZCameraRotation").text = str(writevp.vpZRotation)
        ET.SubElement(vp, "VpLocDescription").text = writevp.vpDescription
        ET.SubElement(vp, "VpMarkerlessMarkerWidth").text = str(writevp.vpMarkerlessMarkerWidth)
        ET.SubElement(vp, "VpMarkerlessMarkerHeigth").text = str(writevp.vpMarkerlessMarkerHeigth)
        ET.SubElement(vp, "VpIsAmbiguous").text = bool2str(writevp.vpIsAmbiguos)
        ET.SubElement(vp, "VpFlashTorchIsOn").text = bool2str(writevp.vpFlashTorchIsOn)
        ET.SubElement(vp, "VpIsSuperSingle").text = bool2str(writevp.vpIsSuperSingle)
        ET.SubElement(vp, "VpSuperMarkerId").text = str(writevp.vpSuperMarkerId)
        ET.SubElement(vp, "VpFrequencyUnit").text = writevp.vpFrequencyUnit
        ET.SubElement(vp, "VpFrequencyValue").text = str(writevp.vpFrequencyValue)

        i += 1

    tempfile = open("tempfile.xml", "w")
    indent(vpsdata)
    tree = ET.ElementTree(vpsdata)
    tree.write(tempfile, encoding="UTF-8")
    tempfile.close()

    s3.Object(AWS_S3_BUCKET_NAME, s3_object_key).upload_file("tempfile.xml")


def writedciinitialcfg(instance):
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    usernameEncoded = urllib.quote(instance.username)
    s3_object_key = "usrcfg/" + usernameEncoded + "/cfg/1/vps/vps.xml"

    vpsdata = ET.Element("VpsData")
    parameters = ET.SubElement(vpsdata, "Parameters")

    writeasset = Asset.objects.get(assetOwner=instance)

    ET.SubElement(parameters, "AssetId").text = str(writeasset.assetNumber)
    ET.SubElement(parameters, "FrequencyUnit").text = writeasset.assetDciFrequencyUnit
    ET.SubElement(parameters, "FrequencyValue").text = str(writeasset.assetDciFrequencyValue)
    ET.SubElement(parameters, "QtyVps").text = str(writeasset.assetDciQtyVps)
    ET.SubElement(parameters, "TolerancePosition").text = str(writeasset.assetDciTolerancePosition)
    ET.SubElement(parameters, "ToleranceRotation").text = str(writeasset.assetDciToleranceRotation)

    i = 0
    while i < writeasset.assetDciQtyVps:
        writevp = modelVp.objects.filter(asset__assetOwner=instance).filter(vpNumber=i).get()

        vp = ET.SubElement(vpsdata, "Vp")
        ET.SubElement(vp, "VpNumber").text = str(writevp.vpNumber)
        ET.SubElement(vp, "VpDescFileSize").text = str(writevp.vpStdPhotoFileSize)
        ET.SubElement(vp, "VpMarkerFileSize").text = str(writevp.vpStdMarkerPhotoFileSize)
        ET.SubElement(vp, "VpArIsConfigured").text = bool2str(writevp.vpArIsConfigured)
        ET.SubElement(vp, "VpIsVideo").text = bool2str(writevp.vpIsVideo)
        ET.SubElement(vp, "VpXCameraDistance").text = str(writevp.vpXDistance)
        ET.SubElement(vp, "VpYCameraDistance").text = str(writevp.vpYDistance)
        ET.SubElement(vp, "VpZCameraDistance").text = str(writevp.vpZDistance)
        ET.SubElement(vp, "VpXCameraRotation").text = str(writevp.vpXRotation)
        ET.SubElement(vp, "VpYCameraRotation").text = str(writevp.vpYRotation)
        ET.SubElement(vp, "VpZCameraRotation").text = str(writevp.vpZRotation)
        ET.SubElement(vp, "VpLocDescription").text = writevp.vpDescription
        ET.SubElement(vp, "VpMarkerlessMarkerWidth").text = str(writevp.vpMarkerlessMarkerWidth)
        ET.SubElement(vp, "VpMarkerlessMarkerHeigth").text = str(writevp.vpMarkerlessMarkerHeigth)
        ET.SubElement(vp, "VpIsAmbiguous").text = bool2str(writevp.vpIsAmbiguos)
        ET.SubElement(vp, "VpFlashTorchIsOn").text = bool2str(writevp.vpFlashTorchIsOn)
        ET.SubElement(vp, "VpIsSuperSingle").text = bool2str(writevp.vpIsSuperSingle)
        ET.SubElement(vp, "VpSuperMarkerId").text = str(writevp.vpSuperMarkerId)
        ET.SubElement(vp, "VpFrequencyUnit").text = writevp.vpFrequencyUnit
        ET.SubElement(vp, "VpFrequencyValue").text = str(writevp.vpFrequencyValue)

        i += 1

    tempfile = open("tempfile.xml", "w")
    indent(vpsdata)
    tree = ET.ElementTree(vpsdata)
    tree.write(tempfile, encoding="UTF-8")
    tempfile.close()

    s3.Object(AWS_S3_BUCKET_NAME, s3_object_key).upload_file("tempfile.xml")

    copy_source_dsc = {
        'Bucket': AWS_S3_BUCKET_NAME,
        'Key': 'admin/cfgbase/mymensordescvp.png'
    }

    copy_source_mrk = {
        'Bucket': AWS_S3_BUCKET_NAME,
        'Key': 'admin/cfgbase/mymensormarkervpbw.png'
    }

    j = 0
    while j < writeasset.assetDciQtyVps:
        dest_dsc = "usrcfg/" + usernameEncoded + "/cfg/1/vps/dsc/descvp" + str(j) + ".png"
        source_dsc = ASSETFILES_FOLDER+'mymensordescvp.png'
        s3.Object(AWS_S3_BUCKET_NAME, dest_dsc).upload_file(source_dsc)
        dest_mrk = "usrcfg/" + usernameEncoded + "/cfg/1/vps/mrk/markervp" + str(j) + ".png"
        source_mrk = ASSETFILES_FOLDER+'mymensormarkervpbw.png'
        s3.Object(AWS_S3_BUCKET_NAME, dest_mrk).upload_file(source_mrk)
    j += 1


def writedciinitialvpschk(instance):
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    usernameEncoded = urllib.quote(instance.username)
    s3_object_key = "usrcfg/" + usernameEncoded + "/chk/1/vpschecked.xml"

    vpsdata = ET.Element("VpsChecked")

    writeasset = Asset.objects.get(assetOwner=instance)

    i = 0
    while i < writeasset.assetDciQtyVps:
        writevp = modelVp.objects.filter(asset__assetOwner=instance).filter(vpNumber=i).get()

        vp = ET.SubElement(vpsdata, "Vp")
        ET.SubElement(vp, "VpNumber").text = str(writevp.vpNumber)
        ET.SubElement(vp, "Checked").text = "false"
        ET.SubElement(vp, "PhotoTakenTimeMillis").text = "0"

        i += 1

    tempfile = open("tempfile.xml", "w")
    indent(vpsdata)
    tree = ET.ElementTree(vpsdata)
    tree.write(tempfile, encoding="UTF-8")
    tempfile.close()

    s3.Object(AWS_S3_BUCKET_NAME, s3_object_key).upload_file("tempfile.xml")
