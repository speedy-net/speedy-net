from speedy.net.settings.base import *

from .utils import APP_DIR

SITE_ID = env('SPEEDY_MATCH_SITE_ID')

ROOT_URLCONF = 'speedy.match.urls'

STATIC_ROOT = str(APP_DIR / 'static_serve')

TEMPLATES[0]['DIRS'].insert(0, str(APP_DIR / 'templates'))

LOCALE_PATHS.append(str(APP_DIR / 'locale'))

STATICFILES_DIRS.insert(0, str(APP_DIR / 'static'))

INSTALLED_APPS += [
    'speedy.match.accounts',
]

AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'
