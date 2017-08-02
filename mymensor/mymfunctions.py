def isfloat(value):
    try:
        float(value)
        return True
    except:
        return False


def mobonlyprefix():
    import random, string
    code = ''.join(random.choice(string.uppercase) for i in range(3))
    return 'mym' + code + '+'


def setup_new_user(instance, **kwargs):
    from mymensor.models import Asset, Vp
    from datetime import datetime, timedelta
    from mymensor.dcidatasync import writedciinitialcfg, writedciinitialvpschk
    asset = Asset(assetDescription="Asset1", assetNumber=1, assetOwner=instance, assetOwnerDescription=instance.email,
                  assetDateOfEndEfTrialBeforeSubscription=datetime.utcnow() + timedelta(days=30))
    asset.save()
    maxqtyvps = 31  ###### Maximum quantity of vps in a DCI + 1 !!!!!!!
    for i in range(0, maxqtyvps):
        vpdescription = "VP#" + str(i)
        vpisactive = True
        vpisused = False
        vpstdphotostorageurl = "usrcfg/" + instance.username + "/cfg/" + str(
            asset.assetNumber) + "/vps/dsc/descvp" + str(i) + ".png"
        vpstdtagdescphotostorageurl = "usrcfg/" + instance.username + "/cfg/" + str(
            asset.assetNumber) + "/vps/dsc/tagdescvp" + str(i) + ".png"
        vpstdmarkerphotostorageurl = "usrcfg/" + instance.username + "/cfg/" + str(
            asset.assetNumber) + "/vps/mrk/markervp" + str(i) + ".png"
        vpstdphotofilesize = 36156
        vpstdmarkerphotofilesize = 32209
        Vp.objects.create(asset=asset, vpDescription=vpdescription, vpNumber=i, vpIsActive=vpisactive, vpListNumber=i,
                          vpIsUsed=vpisused, vpStdPhotoStorageURL=vpstdphotostorageurl,
                          vpStdTagDescPhotoStorageURL=vpstdtagdescphotostorageurl,
                          vpStdMarkerPhotoStorageURL=vpstdmarkerphotostorageurl, vpStdPhotoFileSize=vpstdphotofilesize,
                          vpStdMarkerPhotoFileSize=vpstdmarkerphotofilesize)
    writedciinitialcfg(instance)
    writedciinitialvpschk(instance)


def create_braintree_customer(instance):
    import braintree
    from datetime import datetime
    from mymensorapp.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PRIVATE_KEY, BRAINTREE_PUBLIC_KEY, \
        BRAINTREE_PRODUCTION
    from mymensor.models import BraintreeCustomer
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
    try:
        result = braintree.Customer.create({
            "first_name": instance.username,
            "email": instance.email
        })
        if result.is_success:
            btnewcustomer = BraintreeCustomer(braintreecustomerOwner=instance,
                                              braintreecustomerCustomerId=result.customer.id,
                                              braintreecustomerCustomerCreated=True,
                                              braintreecustomerCustomerCreatedDate=datetime.utcnow())
        else:
            btnewcustomer = BraintreeCustomer(braintreecustomerOwner=instance,
                                              braintreecustomerCustomerCreated=False)
    except ValueError as e:
        btnewcustomer = BraintreeCustomer(braintreecustomerOwner=instance,
                                          braintreecustomerCustomerCreated=False)
    btnewcustomer.save()
