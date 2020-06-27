from .base import *

import os

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'exhaust',
        'USER': os.environ.get('DB_USER'),
    },
}


MEDIA_ROOT = os.path.expanduser(os.path.join('~/Sites', SITE_DOMAIN, 'media'))
STATIC_ROOT = os.path.expanduser(os.path.join('~/Sites', SITE_DOMAIN, 'static'))
