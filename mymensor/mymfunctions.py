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
        vpdescription = "VP#" + str(i)
        if i < 2:
            vpisactive = True
            vpstdphotostorageurl = "usrcfg/" + instance.username + "/cfg/" + str(
                asset.assetNumber) + "/vps/dsc/descvp" + str(i) + ".png"
            vpstdtagdescphotostorageurl = "usrcfg/" + instance.username + "/cfg/" + str(
                asset.assetNumber) + "/vps/dsc/tagdescvp" + str(i) + ".png"
            vpstdmarkerphotostorageurl = "usrcfg/" + instance.username + "/cfg/" + str(
                asset.assetNumber) + "/vps/mrk/markervp" + str(i) + ".png"
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
                          vpStdPhotoStorageURL=vpstdphotostorageurl,
                          vpStdTagDescPhotoStorageURL=vpstdtagdescphotostorageurl,
                          vpStdMarkerPhotoStorageURL=vpstdmarkerphotostorageurl, vpStdPhotoFileSize=vpstdphotofilesize,
                          vpStdMarkerPhotoFileSize=vpstdmarkerphotofilesize)


def create_braintree_customer(instance):
    import braintree
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
                                              braintreecustomerMerchantAccId="mymensorUSD",
                                              braintreecustomerSubscriptionStatus="onTrialBeforeSubscription",
                                              braintreecustomerCustomerCreated=True)
        else:
            btnewcustomer = BraintreeCustomer(braintreecustomerOwner=instance,
                                              braintreecustomerCustomerCreated=False)
    except ValueError as e:
        btnewcustomer = BraintreeCustomer(braintreecustomerOwner=instance,
                                          braintreecustomerCustomerCreated=False)
    btnewcustomer.save()
