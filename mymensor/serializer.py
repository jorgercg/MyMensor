from rest_framework import serializers
from .models import AmazonSNSNotification

class AmazonSNSNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonSNSNotification