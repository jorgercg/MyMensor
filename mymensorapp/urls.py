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
from django.conf.urls import url, patterns, include
from django.contrib import admin
from django.views.generic import TemplateView
from mymensor import views

urlpatterns = [
    url(r'^$', views.portfolio, name='portfolio'),
    url(r'^photofeed/$', views.photofeed,name='photofeed'),
    url(r'^setup/$',views.myMensorSetupSideFormView,name='setup'),
    url(r'^get_assets/\w/$',views.get_assets,name='get_assets'),
    url(r'^get_dcis/$',views.get_dcis,name='get_dcis'),
    url(r'^get_vps/$',views.get_vps,name='get_vps'),
    url(r'^get_tags/$',views.get_tags,name='get_tags'),
    url(r'^contact/$',TemplateView.as_view(template_name='contact.html'),name='contact'),
    url(r'^admin/', admin.site.urls),
    url(r'^chaining/', include('smart_selects.urls')),
]
