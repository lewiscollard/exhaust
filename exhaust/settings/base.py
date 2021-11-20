import os
import subprocess

from django.urls import reverse_lazy

# Root directory of the 'exhaust' project.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
# Root directory of the repository.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

SITE_DOMAIN = 'exhaust.lewiscollard.com'
SITE_NAME = 'Exhaust'
SITE_DESCRIPTION = 'things Lewis Collard likes, by Lewis Collard'

SECRET_KEY_FILE = os.path.join(ROOT_DIR, '.secret_key')

with open(SECRET_KEY_FILE) as fd:
    SECRET_KEY = fd.read().strip()


DEBUG = False

ALLOWED_HOSTS = [SITE_DOMAIN, f'www.{SITE_DOMAIN}', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    # Standard Django stuff.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',

    # Third-party
    'markdownx',
    'sorl.thumbnail',
    'reversion',
    'cachalot',

    # Project-local things.
    'exhaust.common',
    'exhaust.deployment',
    'exhaust.posts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'exhaust.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'exhaust.common.context_processors.settings',
                # Uncomment for query count debugging
                # 'exhaust.common.context_processors.query_count',
            ],
        },
    },
]

CACHE_MIDDLEWARE_KEY_PREFIX = 'exhaust'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        # None = cache forever (until a code update does a memcached restart).
        # If there's no clear plan for cache invalidation, it should not be
        # cached.
        'TIMEOUT': None,
    }
}

#
# DB settings
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'exhaust',
        'USER': os.environ.get('DB_USER'),
    },
}

WSGI_APPLICATION = 'exhaust.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = '/var/www/exhaust_static'
MEDIA_ROOT = '/var/www/exhaust_media'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(ROOT_DIR, 'static')]

# Security headers. Some of these are actually handled in my nginx config;
# this is just to make `manage.py check --deploy` happy. There are others in
# the production settings to avoid breaking local dev.
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

SILENCED_SYSTEM_CHECKS = [
    # The "no HSTS header" thing can be silenced, since my whole domain is on
    # the HSTS Preload list and my web server adds an HSTS header.
    'security.W004',
    # This is coming from django-reversion not defining a primary key type.
    # Remove this some day.
    'models.W042',
]

# Current git HEAD hash, useful for cache invalidation. -C ROOT_DIR ensures
# Git is running in the same directory that 'manage.py' lives in; when we're
# using management commands we cannot assume this is the case.
GIT_COMMIT_HASH = subprocess.check_output(['/usr/bin/git', '-C', ROOT_DIR, 'rev-parse', '--short', 'HEAD']).decode('utf8').strip()

# MarkdownX things
MARKDOWNX_IMAGE_MAX_SIZE = {
    'size': (1920, 1920),
    'quality': 90
}

MARKDOWNX_UPLOAD_URLS_PATH = reverse_lazy('posts:image_upload')

# Group writable is intentional.
FILE_UPLOAD_PERMISSIONS = 0o664

# Default is 95, which is unnecessary at these sizes.
THUMBNAIL_QUALITY = 80

# HTML sanitising options.
BLEACH_CONFIG = {
    'tags': [
        'p', 'div', 'a', 'hr',
        # Headings
        'h2', 'h3', 'h4', 'h5', 'h6',
        # Image & videos
        'img', 'video', 'picture', 'figure', 'figcaption', 'source',
        # Simple emphasis
        'i', 'em', 'strong', 'b',
        # obvs
        'br',
        # Lists
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        # Quotes
        'q', 'blockquote',
        # Custom thing swapped out with a Vue component.
        'youtube-video',
        # Code formats
        'code', 'pre',
        # super/subscripts
        'sup', 'sub',
        # a thing I needed once
        'abbr',
        # Obsolete tags that I use anyway!
        'center', 's',
    ],
    'attributes': {
        'img': ['src', 'alt', 'title', 'loading', 'class'],
        'a': ['href', 'rel', 'target'],
        'youtube-video': ['id', 'title'],
        # These feel a bit too blanket, but should be safe.
        'div': ['class', 'style'],
        'figure': ['class', 'style'],
        'figcaption': ['class'],
        'p': ['class'],
        'source': ['srcset', 'src', 'type'],
        'picture': ['aria-hidden'],
        'video': ['autoplay', 'muted', 'controls', 'loop', 'width', 'height', 'title'],
        'abbr': ['title'],
    },
    'styles': [
        # Used by our multiformat image for aspect ratio preservation (must be
        # inline, unfortunately).
        'padding-bottom', 'max-width'
    ]
}

# Settings for deployment & management scripts.
DEPLOYMENT = {
    'HOST': '178.128.170.126',
    'USER': 'exhaust',
    'DATABASE_NAME': 'exhaust',
    'LOCAL_DATABASE_NAME': 'exhaust',
    'SUDO_USER': 'deploy',
    'ROOT_DIR': '/var/www/exhaust',
    'MEDIA_DIR': MEDIA_ROOT + '/',
    'DJANGO_SETTINGS_MODULE': 'exhaust.settings.production',
}
