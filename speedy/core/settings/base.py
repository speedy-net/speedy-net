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

ADMINS = MANAGERS = (
    ('Uri Rodberg', 'webmaster@speedy.net'),
)

USE_SSL = False

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
]

FORMAT_MODULE_PATH = [
    'speedy.core.locale',
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

SESSION_COOKIE_AGE = int(60 * 60 * 24 * 365.25 * 30)  # ~ 30 years

AUTH_USER_MODEL = 'accounts.User'

SMALL_UDID_LENGTH = 15
REGULAR_UDID_LENGTH = 20

LANGUAGE_CODE = 'en'

# ~~~~ TODO: move the following constants to speedy/core/locale/en/formats.py and speedy/core/locale/he/formats.py
DATE_FORMAT = 'j F Y'
MONTH_DAY_FORMAT = 'j F'
YEAR_FORMAT = 'Y'

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

THUMBNAIL_DEBUG = True

THUMBNAIL_DUMMY = True

TEST_RUNNER = 'speedy.core.base.test.models.SiteDiscoverRunner'

FIXTURE_DIRS = [
    str(ROOT_DIR / 'speedy/core/fixtures')
]

# ~~~~ TODO: check if this is good for production!
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
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
    'handlers': {
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local7',
            'address': '/dev/log',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'root': {
            'handlers': ['syslog', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['syslog', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['syslog', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['syslog', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'speedy': {
            'handlers': ['syslog', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # 'speedy.net': {
        #     'handlers': ['syslog', 'mail_admins'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'speedy.match': {
        #     'handlers': ['syslog', 'mail_admins'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'speedy.composer': {
        #     'handlers': ['syslog', 'mail_admins'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'speedy.mail': {
        #     'handlers': ['syslog', 'mail_admins'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
    },
}


