"""mymensorapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.views import (password_reset, password_reset_done, password_reset_confirm, password_reset_complete)
from django.contrib.auth.decorators import login_required
from registration.backends.default.views import RegistrationView, ActivationView
from rest_framework.authtoken import views
from instant.views import instant_auth
from mymensor import mymviews

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/portfolio/')),
    url(r'^portfolio/$', mymviews.portfolio, name='portfolio'),
    url(r'^mediafeed/$', mymviews.mediafeed, name='mediafeed'),
    url(r'^vpdetail/$', mymviews.vpDetailView, name='vpdetail'),
    url(r'^tagstatus/$', mymviews.TagStatusView, name='tagstatus'),
    url(r'^taganalysis/$', mymviews.tagAnalysisView, name='taganalysis'),
    url(r'^tagprocessing/$', mymviews.tagProcessingFormView, name='tagprocessing'),
    url(r'^proctagedit/$', mymviews.procTagEditView, name='proctagedit'),
    url(r'^support/$', TemplateView.as_view(template_name='support.html'), name='support'),
    url(r'^assetsetup/$', mymviews.assetSetupFormView, name='assetsetup'),
    url(r'^vpsetup/$', mymviews.vpSetupFormView, name='vpsetup'),
    url(r'^tagsetup/$', mymviews.tagSetupFormView, name='tagsetup'),

    url(r'^mobilebackup/$', mymviews.mobileBackupFormView, name='mobilebackup'),

    url(r'^landing/$', mymviews.landingView, name='landing'),

    url(r'^chaining/', include('smart_selects.urls')),

    url(r'^accounts/', include('registration.backends.default.urls')),

    # password reset urls
    url(r'^accounts/password/reset/$', password_reset, {'template_name': 'registration/password_reset_form.html'}, name="password_reset"),
    url(r'^accounts/password/reset/done/$', password_reset_done, {'template_name': 'registration/password_reset_done.html'}, name="password_reset_done"),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm,{'template_name': 'registration/password_reset_confirm.html'},
        name="password_reset_confirm"),
    url(r'^accounts/password/done/$', password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}, name="password_reset_complete"),
    url(r'^accounts/register/$', RegistrationView.as_view(), name='registration_register'),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^sns-notifications/', mymviews.amazon_sns_processor),

    url(r'^cognito-auth/', mymviews.cognitoauth),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^.well-known/acme-challenge/6tkddfaSb9H4On2KEHI9q8sKzO3eIW225xNkH-4PMnU/$', mymviews.zerossl),

    url(r'^api-token-auth/', views.obtain_auth_token),

    url(r'^instant/', include('instant.urls')),

    url(r'^centrifuge/auth/$', instant_auth, name='instant-auth'),

    url(r'^tz_detect/', include('tz_detect.urls')),

    url(r'^tagprocessing/save_value/', mymviews.saveValue, name='save_value'),

    url(r'^proctagedit/save_value/', mymviews.saveValue, name='save_value'),

    url(r'^tagsetup/save_tagbboxvalues/', mymviews.save_tagboundingbox, name='save_tagbboxvalues'),

    url(r'^mobilebackup/create_backup/', mymviews.createdcicfgbackup, name='create_backup'),

    url(r'^mobilebackup/restore_backup/', mymviews.restoredcicfgbackup, name='restore_backup'),

    url(r'^portfolio/pf_mediaid_sendvalue/', mymviews.tagsprocessedinthismedia, name='pf_mediaid_sendvalue'),

    url(r'^mediafeed/mf_mediaid_sendvalue/', mymviews.tagsprocessedinthismedia, name='mf_mediaid_sendvalue'),

    url(r'^portfolio/pf_mediaid_sendvalue_loc/', mymviews.locofthismedia, name='pf_mediaid_sendvalue_loc'),

    url(r'^mediafeed/mf_mediaid_sendvalue_loc/', mymviews.locofthismedia, name='mf_mediaid_sendvalue_loc'),

    url(r'^vpdetail/delete_media/', mymviews.deletemedia, name='delete_media'),

    url(r'^vpdetail/move_media/', mymviews.movemedia, name='move_media'),

    url(r'^export_tagstatus_csv/', mymviews.export_tagstatus_csv, name='export_tagstatus_csv'),
]