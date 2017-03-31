from mymensorapp.settings import TWT_API_KEY, TWT_API_SECRET
import tweepy

def isfloat(value):
  try:
    float(value)
    return True
  except:
    return False


def setup_new_user(instance, **kwargs):
    from mymensor.models import Asset, Vp
    asset = Asset(assetDescription="Asset1", assetNumber=1, assetOwner=instance, assetOwnerDescription=instance.email)
    asset.save()
    maxqtyvps = 31  ###### Maximum quantity of vps in a DCI + 1 !!!!!!!
    for i in range(0, maxqtyvps):
        vpdescription = "VP#"+str(i)
        if i<2:
            vpisactive = True
            vpstdphotostorageurl = instance.username+"/cfg/"+str(asset.assetNumber)+"/vps/dsc/descvp"+str(i)+".png"
            vpstdtagdescphotostorageurl = instance.username+"/cfg/"+str(asset.assetNumber)+"/vps/dsc/tagdescvp"+str(i)+".png"
            vpstdmarkerphotostorageurl = instance.username+"/cfg/"+str(asset.assetNumber)+"/vps/mrk/markervp"+str(i)+".png"
            vpstdphotofilesize = 36156
            vpstdmarkerphotofilesize = 32209
        else:
            vpisactive = False
            vpstdphotostorageurl = None
            vpstdtagdescphotostorageurl = None
            vpstdmarkerphotostorageurl = None
            vpstdphotofilesize = None
            vpstdmarkerphotofilesize = None
        Vp.objects.create(asset=asset, vpDescription=vpdescription, vpNumber=i, vpIsActive=vpisactive, vpListNumber=i,
                          vpStdPhotoStorageURL=vpstdphotostorageurl, vpStdTagDescPhotoStorageURL=vpstdtagdescphotostorageurl,
                          vpStdMarkerPhotoStorageURL= vpstdmarkerphotostorageurl, vpStdPhotoFileSize=vpstdphotofilesize,
                          vpStdMarkerPhotoFileSize=vpstdmarkerphotofilesize)
