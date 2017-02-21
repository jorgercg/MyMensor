from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from mymensor.models import Token, Media, Asset, Vp, ProcessedTag
from mymensor.mymfunctions import setup_new_user


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        setup_new_user(instance)

