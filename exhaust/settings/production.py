
from .base import *  # pylint:disable=unused-wildcard-import,wildcard-import

DEBUG = False
TEMPLATE_DEBUG = DEBUG
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
