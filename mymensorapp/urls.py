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
from django.views.generic import TemplateView
from django.contrib.auth.views import (password_reset, password_reset_done, password_reset_confirm, password_reset_complete)
from registration.backends.default.views import RegistrationView, ActivationView
from rest_framework.authtoken import views

from mymensor import mymviews

urlpatterns = [
    url(r'^/$', mymviews.portfolio, name='portfolio'),
    url(r'^portfolio/$', mymviews.portfolio, name='portfolio'),
    url(r'^mediafeed/$', mymviews.mediafeed, name='mediafeed'),
    url(r'^setup/$', mymviews.myMensorSetupFormView, name='setup'),
    url(r'^contact/$', TemplateView.as_view(template_name='contact.html'), name='contact'),
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

]

