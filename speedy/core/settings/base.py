"""
Django settings for Speedy Net project.
"""

from django.utils.translation import gettext_lazy as _

from .utils import env, APP_DIR, ROOT_DIR


SPEEDY_NET_SITE_ID = int(env('SPEEDY_NET_SITE_ID'))
SPEEDY_MATCH_SITE_ID = int(env('SPEEDY_MATCH_SITE_ID'))
SPEEDY_COMPOSER_SITE_ID = int(env('SPEEDY_COMPOSER_SITE_ID'))
SPEEDY_MAIL_SOFTWARE_SITE_ID = int(env('SPEEDY_MAIL_SOFTWARE_SITE_ID'))

SITES_WITH_LOGIN = [
    SPEEDY_NET_SITE_ID,
    SPEEDY_MATCH_SITE_ID,
]

XD_AUTH_SITES = SITES_WITH_LOGIN

SECRET_KEY = env('SECRET_KEY')

TESTS = False
DEBUG = False

ALLOWED_HOSTS = ['*']

DEFAULT_FROM_EMAIL = 'webmaster@speedy.net'
SERVER_EMAIL = 'webmaster+server@speedy.net'

ADMINS = MANAGERS = (
    ('Uri Rodberg', 'webmaster@speedy.net'),
)

USE_HTTPS = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',
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

FORMAT_MODULE_PATH = [
    'speedy.core.formats',
]

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
    'speedy.core.base.middleware.EnsureCachesMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

CRISPY_FAIL_SILENTLY = False

DATABASES = {
    'default': env.db()
}

CACHES = {
    'default': env.cache()
}

DEFAULT_AUTHENTICATION_BACKEND = 'django.contrib.auth.backends.AllowAllUsersModelBackend'

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    DEFAULT_AUTHENTICATION_BACKEND,
)

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_AGE = int(60 * 60 * 24 * 365.25 * 30)  # ~ 30 years

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'

AUTH_USER_MODEL = 'accounts.User'

SMALL_UDID_LENGTH = 15
REGULAR_UDID_LENGTH = 20

LANGUAGE_CODE = 'en'

DATE_FORMAT = 'j F Y'
MONTH_DAY_FORMAT = 'j F'
YEAR_FORMAT = 'Y'

FORMAT_SETTINGS = (
    'YEAR_FORMAT',
)

LANGUAGES = [
    ('en', _('English')),
    ('he', _('Hebrew')),
]

LOCALE_PATHS = [
    str(APP_DIR / 'locale'),
    str(ROOT_DIR / 'speedy/core/locale'),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    str(APP_DIR / 'static'),
    str(ROOT_DIR / 'speedy/core/static')
]

MEDIA_URL = '/media/'

MEDIA_ROOT = str(ROOT_DIR / 'media')

FILE_UPLOAD_MAX_MEMORY_SIZE = int(7.5 * 1024 * 1024)  # 7.5 MB

MAX_PHOTO_SIZE = int(15 * 1024 * 1024)  # 15 MB

IMAGE_FILE_EXTENSIONS = (
    'jpeg',
    'jpg',
    'png',
)

THUMBNAIL_DEBUG = True

THUMBNAIL_DUMMY = True

THUMBNAIL_FORMAT = 'PNG'

THUMBNAIL_CACHE_TIMEOUT = int(60 * 60 * 24 * 90)  # 90 days

TEST_RUNNER = 'speedy.core.base.test.models.SiteDiscoverRunner'

FIXTURE_DIRS = [
    str(ROOT_DIR / 'speedy/core/fixtures')
]

DATE_FIELD_FORMATS = [
    '%Y-%m-%d',  # '2006-10-25'
]

DEFAULT_DATE_FIELD_FORMAT = '%Y-%m-%d'

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
        #         'verbose': {
        # #            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        #             'format': '%(asctime)s %(name)s %(levelname)s: %(message)s',
        #             'datefmt': '%Y-%m-%d %H:%M:%S',
        #         },
        #         'simple': {
        #             'format': '%(levelname)s %(message)s'
        #         },
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
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'include_html': True,
        },
    },
    'loggers': {
        'root': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['console', 'file', 'mail_admins'],
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
            'propagate': True,
        },
    },
}

DEFAULT_HASHING_ALGORITHM = 'sha1'  # ~~~~ TODO: temporary setting; remove this line after Django 3.1 works properly.

