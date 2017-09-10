from mymensorapp.settings import *

import dj_database_url


DATABASES['default'] = dj_database_url.config()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# UPDATE BEFORE LAUNCH !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#ALLOWED_HOSTS = ['app.mymensor.com', 'mymensor.herokuapp.com']

DEBUG = False

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'