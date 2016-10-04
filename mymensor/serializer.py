from rest_framework import serializers
from .models import AmazonSNSNotification #, OpenIdOuath2RedirectCode

class AmazonSNSNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonSNSNotification

#class OpenIdOuath2RedirectCodeSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = OpenIdOuath2RedirectCode