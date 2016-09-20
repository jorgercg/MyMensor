from mymensorapp.settings import *

import dj_database_url 
DATABASES['default'] = dj_database_url.config()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True

# UPDATE BEFORE LAUNCH !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ALLOWED_HOSTS = ['app.mymensor.com']

DEBUG = True

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'