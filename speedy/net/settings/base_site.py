from .base import *

SITE_ID = int(env('SPEEDY_NET_SITE_ID'))

SESSION_COOKIE_NAME = SESSION_COOKIE_NAME_TEMPLATE.format(site_id=SITE_ID)

ROOT_URLCONF = 'speedy.net.urls'

STATIC_ROOT = str(APP_DIR / 'static_serve')

AUTH_SITE_PROFILE_MODEL = 'accounts.SiteProfile'
