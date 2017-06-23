from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from mymensor.models import Token, Media, Asset, Vp, ProcessedTag
from mymensor.mymfunctions import setup_new_user, create_braintree_customer
from mymensorapp.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME
import boto3


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        setup_new_user(instance)
        create_braintree_customer(instance)

@receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
def delete_cognito_related_id(sender, instance=None, **kwargs):
    client = boto3.client(
        'cognito-identity',
        'eu-west-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    assetinstance = Asset.objects.get(assetOwner=instance)

    usercogidtodelete = assetinstance.assetOwnerIdentityId

    try:
        response = client.delete_identities(
            IdentityIdsToDelete=[
                usercogidtodelete,
            ]
        )
    except:
        pass
