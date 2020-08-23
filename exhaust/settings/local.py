import os

from .base import *  # pylint: disable=unused-wildcard-import,wildcard-import

DEBUG = True

MEDIA_ROOT = os.path.expanduser(os.path.join('~/Sites', SITE_DOMAIN, 'media'))
STATIC_ROOT = os.path.expanduser(os.path.join('~/Sites', SITE_DOMAIN, 'static'))
