from speedy.net.settings.base import *

from .utils import APP_DIR

SITE_ID = int(env('SPEEDY_MATCH_SITE_ID'))

SESSION_COOKIE_NAME = SESSION_COOKIE_NAME_TEMPLATE.format(site_id=SITE_ID)

ROOT_URLCONF = 'speedy.match.urls'

STATIC_ROOT = str(APP_DIR / 'static_serve')

TEMPLATES[0]['DIRS'].insert(0, str(APP_DIR / 'templates'))

LOCALE_PATHS.append(str(APP_DIR / 'locale'))

STATICFILES_DIRS.insert(0, str(APP_DIR / 'static'))

INSTALLED_APPS += [
    'speedy.match.accounts',
    'speedy.match.likes',
]

AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'
