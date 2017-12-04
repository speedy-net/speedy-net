from django.utils.translation import ugettext_lazy as _
from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = int(env('SPEEDY_MATCH_SITE_ID'))

SITE_TITLE = _('Speedy Match [alpha]')

ROOT_URLCONF = 'speedy.match.urls'

DEFAULT_FROM_EMAIL = 'webmaster@speedymatch.com'

INSTALLED_APPS += [
    'speedy.match.accounts',
    'speedy.match.profiles',
    'speedy.match.likes',
    'speedy.match.matches',
]

AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'

ACTIVATE_PROFILE_AFTER_REGISTRATION = False

SITE_PROFILE_ACTIVATION_FORM = 'speedy.match.accounts.forms.SpeedyMatchProfileActivationForm'

USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
    'speedy.net.profiles.widgets.UserOnSpeedyNetWidget',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
#            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            'format': '%(asctime)s %(name)s %(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/speedy_debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'root': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'speedy.match': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
