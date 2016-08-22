from django.shortcuts import render
from mymensor.models import Photo, AssetOwner, Asset, Dci, Vp, Tag, MyMensorConfiguration, MyMensorConfigurationForm

# Portfolio View
def portfolio(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', { 'photos': photos,})

# Photo Feed View
def photofeed(request):
    photos = Photo.objects.all()
    return render(request, 'photofeed.html', { 'photos': photos,})

# Setup View
def myMensorSetupSideFormView(request):
    if request.method == 'POST':
        form = MyMensorConfigurationForm(request.POST)
        #if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
    else:
        form = MyMensorConfigurationForm()
    return render(request, 'setup.html', { 'form': form,})

def get_assets(request, id_assetOwner):
    assetowner = AssetOwner.objects.get(pk=id_assetOwner)
    assets = Asset.objects.filter(asseOwner=assetowner)
    asset_dict = {}
    for asset in assets:
        asset_dict[asset.id] = asset.assetDescription
    return HttpResponse(json.dumps(asset_dict), mimetype="application/json")

def get_dcis(request, id_asset):
    assets = models.Asset.objects.get(pk=id_asset)
    dcis = models.Dci.objects.filter(assets=assets)
    dci_dict = {}
    for dci in dcis:
        dci_dict[dci.id] = dci.dciDescription
    return HttpResponse(json.dumps(dci_dict), mimetype="application/json")
    
def get_vps(request, id_dci):
    dcis = models.Dci.objects.get(pk=id_dci)
    vps = models.Vp.objects.filter(dcis=dcis)
    vp_dict = {}
    for vp in vps:
        vp_dict[vp.id] = vp.vpDescription
    return HttpResponse(json.dumps(vp_dict), mimetype="application/json")

def get_tags(request, id_vp):
    vps = models.Vp.objects.get(pk=id_vp)
    tags = models.Tag.objects.filter(vps=vps)
    tag_dict = {}
    for tag in tags:
        tag_dict[tag.id] = tag.tagDescription
    return HttpResponse(json.dumps(tag_dict), mimetype="application/json")