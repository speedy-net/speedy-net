from speedy.net.settings.base import *

from .utils import APP_DIR

SITE_ID = int(env('SPEEDY_COMPOSER_SITE_ID'))

SESSION_COOKIE_NAME = SESSION_COOKIE_NAME_TEMPLATE.format(site_id=SITE_ID)

ROOT_URLCONF = 'speedy.composer.urls'

STATIC_ROOT = str(APP_DIR / 'static_serve')

TEMPLATES[0]['DIRS'].insert(0, str(APP_DIR / 'templates'))

LOCALE_PATHS.append(str(APP_DIR / 'locale'))

STATICFILES_DIRS.insert(0, str(APP_DIR / 'static'))

AUTH_SITE_PROFILE_MODEL = 'composer_accounts.SiteProfile'
