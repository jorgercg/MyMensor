from mymensorapp.settings import *

import dj_database_url


DATABASES['default'] = dj_database_url.config()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True

# required settings
CENTRIFUGO_SECRET_KEY = "7da2d4f3f367734c07b7267368d4b37ce641c3aba2c15cca01396c145aae6d9d" # the_key_that_is_in_config.json

SITE_SLUG = "my_mensor" # used internaly to prefix the channels
SITE_NAME = "MyMensor"

# optionnal settings
CENTRIFUGO_HOST = 'https://centrifugo-mym.herokuapp.com' #default: localhost
#CENTRIFUGO_PORT = 8012 # default: 8001
INSTANT_PUBLIC_CHANNEL = "public" #default: SITE_SLUG+'_public'
INSTANT_ENABLE_USERS_CHANNEL = "$mediafeed"

INSTANT_DEBUG = True

# UPDATE BEFORE LAUNCH !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ALLOWED_HOSTS = ['app.mymensor.com', 'mymensor.herokuapp.com']

DEBUG = True

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'