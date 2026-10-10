"""
Django settings for Speedy Net project.
"""

import re

from django.utils.translation import gettext_lazy as _

from .utils import env, APP_DIR, ROOT_DIR

# Site IDs (django.contrib.sites) of the sites served by this project, read from the environment.
SPEEDY_NET_SITE_ID = int(env('SPEEDY_NET_SITE_ID'))
SPEEDY_MATCH_SITE_ID = int(env('SPEEDY_MATCH_SITE_ID'))
SPEEDY_COMPOSER_SITE_ID = int(env('SPEEDY_COMPOSER_SITE_ID'))
SPEEDY_MAIL_SOFTWARE_SITE_ID = int(env('SPEEDY_MAIL_SOFTWARE_SITE_ID'))

# IDs of the sites which have user accounts and login (Speedy Net and Speedy Match).
SITES_WITH_LOGIN = [
    SPEEDY_NET_SITE_ID,
    SPEEDY_MATCH_SITE_ID,
]

# Sites which use cross-domain authentication (xd_auth) and the sites whose templates are used as top-level templates; both are the sites with login.
XD_AUTH_SITES = SITES_WITH_LOGIN
TEMPLATES_TOP_SITES = SITES_WITH_LOGIN

# Secret keys: Django's SECRET_KEY and the access key of the ipapi geolocation API (values are read from the environment).
SECRET_KEY = env('SECRET_KEY')
IPAPI_API_ACCESS_KEY = env('IPAPI_API_ACCESS_KEY')

# Default environment flags, overridden for the tests, development and under-construction sites: TESTS is True only when running tests.
TESTS = False
DEBUG = False
THIS_SITE_IS_UNDER_CONSTRUCTION = False

# Hosts the site may serve (any host is allowed).
ALLOWED_HOSTS = ['*']

# Robots which don't respect robots.txt:
DISALLOWED_USER_AGENTS = [
    re.compile(pattern=r'Edg/114.0.1823.43'),
    re.compile(pattern=r'Amzn-SearchBot'),
    re.compile(pattern=r'OAI-SearchBot'),
]

# Email addresses used as the sender of notifications and of server error emails.
DEFAULT_FROM_EMAIL = 'notifications@speedy.net'
SERVER_EMAIL = 'webmaster+server@speedy.net'

# People who receive error reports and broken-link notifications by email (ADMINS and MANAGERS are the same).
ADMINS = MANAGERS = (
    ('Uri Rodberg', 'webmaster@speedy.net'),
)

# Whether the site is served over HTTPS (turned off in the development environment).
USE_HTTPS = True

# Installed Django apps: Django contrib apps, third-party apps and Speedy apps.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'django_admin_inline_paginator_plus',
    'crispy_forms',
    'crispy_bootstrap4',
    'friendship',
    'rules.apps.AutodiscoverRulesConfig',
    'sorl.thumbnail',

    'speedy.core.base',
    'speedy.core.accounts',
    'speedy.core.blocks',
    'speedy.core.uploads',
    'speedy.core.messages',
    'speedy.core.profiles',
    'speedy.core.friends',
    'speedy.core.about',
    'speedy.core.privacy',
    'speedy.core.terms',
    'speedy.net.accounts',
    'speedy.match.accounts',
    'speedy.match.likes',
    'speedy.composer.accounts',  # For admin - for deleting users.
    'speedy.mail.accounts',  # For admin - for deleting users.
]

# Directories (as Python modules) with custom locale formats.
FORMAT_MODULE_PATH = [
    'speedy.core.formats',
]

# Middleware classes, in the order they are applied to requests.
MIDDLEWARE = [
    'speedy.core.base.middleware.SessionCookieDomainMiddleware',
    'speedy.core.base.middleware.RemoveExtraSlashesMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    'speedy.core.base.middleware.LocaleDomainMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Template engine configuration: template directories and context processors.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APP_DIR / 'templates'),
            str(ROOT_DIR / 'speedy/core/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',

                'speedy.core.base.context_processors.active_url_name',
                'speedy.core.base.context_processors.settings',
                'speedy.core.base.context_processors.sites',
                'speedy.core.base.context_processors.speedy_net_domain',
                'speedy.core.base.context_processors.speedy_match_domain',
                'speedy.core.base.context_processors.add_admin_user_prefix',
                'speedy.core.base.context_processors.display_ads_today_1',
                'speedy.core.base.context_processors.display_ads_today_2',
            ],
        },
    },
]

# Allowed crispy-forms template packs.
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'

# Template pack used by crispy-forms to render forms.
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Whether crispy-forms hides errors raised while rendering (False means errors are raised).
CRISPY_FAIL_SILENTLY = False

# Database configuration, read from the environment.
DATABASES = {
    'default': env.db(),
}

# Cache configuration, read from the environment.
CACHES = {
    'default': env.cache(),
}

# Speedy Net and Speedy Match timeouts:
CACHE_SET_BLOCKED_ENTITIES_IDS_TIMEOUT = 6 * 60  # 6 minutes
CACHE_GET_BLOCKED_ENTITIES_IDS_SLIDING_TIMEOUT = 0
CACHE_SET_BLOCKING_ENTITIES_IDS_TIMEOUT = 6 * 60  # 6 minutes
CACHE_GET_BLOCKING_ENTITIES_IDS_SLIDING_TIMEOUT = 0
CACHE_SET_RECEIVED_FRIENDSHIP_REQUESTS_COUNT_TIMEOUT = 5 * 60  # 5 minutes
CACHE_GET_RECEIVED_FRIENDSHIP_REQUESTS_COUNT_SLIDING_TIMEOUT = 0
CACHE_SET_UNREAD_CHATS_COUNT_TIMEOUT = 5 * 60  # 5 minutes
CACHE_GET_UNREAD_CHATS_COUNT_SLIDING_TIMEOUT = 0

# Speedy Match timeouts:
CACHE_SET_MATCHES_TIMEOUT = 6 * 60  # 6 minutes
CACHE_GET_MATCHES_SLIDING_TIMEOUT = 0

# Whether all cached values of a user are invalidated (busted) when the user's data changes.
BUST_ALL_CACHES_FOR_A_USER = True

# Default authentication backend (allows login of inactive users too, which are handled by the site).
DEFAULT_AUTHENTICATION_BACKEND = 'django.contrib.auth.backends.AllowAllUsersModelBackend'

# Authentication backends: django-rules object permissions and the default backend.
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    DEFAULT_AUTHENTICATION_BACKEND,
)

# Session cookie settings: sent only over HTTPS, cross-site allowed (needed for cross-domain login), and a lifetime of about 30 years.
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_AGE = int(60 * 60 * 24 * 365.25 * 30)  # ~ 30 years

# CSRF cookie settings: sent only over HTTPS and with SameSite=Lax.
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'

# The user model used by the project.
AUTH_USER_MODEL = 'accounts.User'

# Lengths of the UDIDs (unique identifiers) of the small and the regular kinds.
SMALL_UDID_LENGTH = 15
REGULAR_UDID_LENGTH = 20

# Default language code of the site.
LANGUAGE_CODE = 'en'

# Default date formats (in Django date format syntax): full date, month and day, and year.
DATE_FORMAT = "j F Y"
MONTH_DAY_FORMAT = "j F"
YEAR_FORMAT = "Y"

# Number of digits in each group when thousand separators are used.
NUMBER_GROUPING = 3

# Additional format settings loaded from the format modules (see FORMAT_MODULE_PATH).
FORMAT_SETTINGS = (
    "YEAR_FORMAT",
)

# Available languages (English and Hebrew by default; extended on sites with login).
LANGUAGES = [
    ('en', _('English')),
    ('he', _('Hebrew')),
]

# Languages shown in the HTML language selector (the same as LANGUAGES by default).
LANGUAGES_IN_HTML = LANGUAGES

# Languages in which ads are displayed (none by default).
LANGUAGES_WITH_ADS = set()

# Directories which contain translation files (locale).
LOCALE_PATHS = [
    str(APP_DIR / 'locale'),
    str(ROOT_DIR / 'speedy/core/locale'),
]

# Time zone of the site (UTC).
TIME_ZONE = 'UTC'

# Whether datetimes are timezone-aware.
USE_TZ = True

# Whether Django's translation system is enabled.
USE_I18N = True

# Whether numbers are displayed with a thousand separator.
USE_THOUSAND_SEPARATOR = True

# URL prefix of static files.
STATIC_URL = '/static/'

# Additional directories with static files.
STATICFILES_DIRS = [
    str(APP_DIR / 'static'),
    str(ROOT_DIR / 'speedy/core/static')
]

# URL prefix of uploaded media files.
MEDIA_URL = '/media/'

# Directory where uploaded media files are stored.
MEDIA_ROOT = str(ROOT_DIR / 'media')

# Maximum size of an uploaded file (in bytes) which is kept in memory before being written to a temporary file.
FILE_UPLOAD_MAX_MEMORY_SIZE = int(7.5 * 1024 * 1024)  # 7.5 MB

# Maximum size of an uploaded photo (in bytes).
MAX_PHOTO_SIZE = int(30 * 1024 * 1024)  # 30 MB

# Allowed file extensions of uploaded images.
IMAGE_FILE_EXTENSIONS = (
    'jpeg',
    'jpg',
    'png',
)

# sorl-thumbnail: whether to raise thumbnail errors (debug mode).
THUMBNAIL_DEBUG = True

# sorl-thumbnail: whether to generate dummy thumbnail images (True) instead of real ones.
THUMBNAIL_DUMMY = True

# sorl-thumbnail: output format of generated thumbnails.
THUMBNAIL_FORMAT = 'PNG'

# sorl-thumbnail: cache timeout of thumbnails, in seconds.
THUMBNAIL_CACHE_TIMEOUT = int(60 * 60 * 24 * 2)  # 48 hours

# sorl-thumbnail: the timeout, in seconds, after which old thumbnails are deleted by the cleanup command.
THUMBNAIL_CLEANUP_DELETE_TIMEOUT = int(60 * 60 * 24 * 92)  # 92 days

# Whether to get information about the user's location from the ipapi service, and whether to use it to calculate the distance between users.
GET_IP_ADDRESS_IPAPI_INFO = True
USE_DISTANCE_BETWEEN_USERS_FROM_IPAPI_RESULTS = True

# Test runner class used to run the tests.
TEST_RUNNER = 'speedy.core.base.test.models.SiteDiscoverRunner'

# Directories with fixtures.
FIXTURE_DIRS = [
    str(ROOT_DIR / 'speedy/core/fixtures')
]

# Accepted input formats of date fields.
DATE_FIELD_FORMATS = [
    '%Y-%m-%d',  # '2006-10-25'
]

# Default format of date fields.
DEFAULT_DATE_FIELD_FORMAT = '%Y-%m-%d'

# Default type of automatically created primary keys.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration: console logging for development, and file and admin-email logging for staging and production.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {  # for development
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'django.server': {  # for development
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'file': {  # for staging and production
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/django/speedy.log',
            'formatter': 'verbose',
        },
        'mail_admins': {  # for staging and production
            'level': 'INFO',
            'class': 'speedy.core.base.log.AdminEmailHandler',
            'formatter': 'verbose',
            'include_html': True,
        },
    },
    'root': {
        'handlers': ['console', 'file', 'mail_admins'],
        'level': 'INFO',
        'propagate': True,
    },
    'loggers': {
        'django': {
            'handlers': [],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': [],
            'level': 'INFO',
            'propagate': True,
        },
        'django.template': {
            'handlers': [],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'speedy': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


