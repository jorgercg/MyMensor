from rest_framework import serializers
from .models import AmazonSNSNotification, AmazonS3Message
from django.core import exceptions
from django.contrib.auth.models import User
import django.contrib.auth.password_validation as validators


class AmazonSNSNotificationSerializer(serializers.ModelSerializer):
    #Message = serializers.CharField(source='Message.Records.eventVersion')

    class Meta:
        model = AmazonSNSNotification
        fields = '__all__'

    #def create(self, validated_data):
    #    data = validated_data
    #    data['Message'] = validated_data.get('Message.Records.eventVersion', data['Message']['Records']['eventVersion'])
    #    return AmazonSNSNotification.objects.create(**data)


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


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, data):
        user = User(**data)
        password = data.get('password')
        errors = dict()
        try:
            validators.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(CreateUserSerializer, self).validate(data)