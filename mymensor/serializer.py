from rest_framework import serializers
from .models import AmazonSNSNotification, AmazonS3Message

class AmazonSNSNotificationSerializer(serializers.ModelSerializer):
    s3_object_key = serializers.CharField(source='Message.Records.s3.object.key', read_only=True)

    class Meta:
        model = AmazonSNSNotification

class AmazonS3MessageSerializer(serializers.ModelSerializer):
    eventVersion = serializers.CharField(source='Records.eventVersion')
    eventSource = serializers.CharField(source='Records.eventSource')
    awsRegion = serializers.CharField(source='Records.awsRegion')
    eventTime = serializers.CharField(source='Records.eventTime')
    eventName = serializers.CharField(source='Records.eventName')
    userIdentity_principalId = serializers.CharField(source='Records.userIdentity.principalId')
    requestParameters_sourceIPAddress = serializers.CharField(source='Records.requestParameters.sourceIPAddress')
    responseElements_x_amz_request_id = serializers.CharField(source='Records.responseElements.x-amz-request-id')
    responseElements_x_amz_id_2 = serializers.CharField(source='Records.responseElements.x-amz-id-2')
    s3_s3SchemaVersion = serializers.CharField(source='Records.s3.s3SchemaVersion')
    s3_configurationId = serializers.CharField(source='Records.s3.configurationId')
    s3_bucket_name = serializers.CharField(source='Records.s3.bucket.name')
    s3_bucket_ownerIdentity_principalId = serializers.CharField(source='Records.s3.bucket.ownerIdentity.principalId')
    s3_bucket_arn = serializers.CharField(source='Records.s3.bucket.arn')
    s3_object_key = serializers.CharField(source='properties.Message.Records.s3.object.key')
    s3_object_size = serializers.CharField(source='Records.s3.object.size')
    s3_object_eTag = serializers.CharField(source='Records.s3.object.eTag')
    s3_object_versionId = serializers.CharField(source='Records.s3.object.versionId')
    s3_object_sequencer = serializers.CharField(source='Records.s3.object.sequencer')

    class Meta:
        model = AmazonS3Message