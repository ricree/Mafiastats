# Django settings for Mafiastats.project.
from deploy_settings import DATABASE_ENGINE,DATABASE_NAME,DATABASE_USER,DATABASE_PASSWORD,DATABASE_HOST,DATABASE_PORT,SECRET_KEY,SITE_ROOT,DEBUG,FONT_DIRECTORY,DOMAIN_NAME

TEMPLATE_DEBUG = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

import os

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = SITE_ROOT + '/static'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


INTERNAL_IPS=("127.0.0.1",)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.request",
'django_authopenid.context_processors.authopenid',
)

MIDDLEWARE_CLASSES = (
#	'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',)
#if DEBUG:
#	MIDDLEWARE_CLASSES +=('debug_toolbar.middleware.DebugToolbarMiddleware',)
MIDDLEWARE_CLASSES +=(
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django_authopenid.middleware.OpenIDMiddleware',
#	'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'Mafiastats.urls'

TEMPLATE_DIRS = (SITE_ROOT+'/templates/'
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

LOGIN_REDIRECT_URL='/account/profile'
LOGIN_URL='/account/signin/'

CACHE_MIDDLEWARE_PREFIX=''
CACHE_MIDDLEWARE_SECONDS=60

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
	'coffin',
    'registration',
    'django_authopenid',
    'django.contrib.comments',
    'debug_toolbar',
    'Mafiastats.mafiaStats',
	'celery'
)

JINJA2_FILTERS = ('Mafiastats.mafiaStats.extensions.bbcode',)

ACCOUNT_ACTIVATION_DAYS=7

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "mafiastats"
BROKER_PASSWORD = "rar000074"
BROKER_VHOST = "mafhost"
