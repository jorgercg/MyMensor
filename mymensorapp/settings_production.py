from mymensorapp.settings import *
import subprocess
import sys

import dj_database_url


DATABASES['default'] = dj_database_url.config()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# UPDATE BEFORE LAUNCH !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ALLOWED_HOSTS = ['app.mymensor.com', 'mymensor.herokuapp.com']

DEBUG = True

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Ensure virtualenv path is part of PATH env var
os.environ['PATH'] += os.pathsep + os.path.dirname(sys.executable)

WKHTMLTOPDF_CMD = subprocess.Popen(
    ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')], # Note we default to 'wkhtmltopdf' as the binary name
    stdout=subprocess.PIPE).communicate()[0].strip()