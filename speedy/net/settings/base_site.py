from .base import *

SITE_ID = env('SPEEDY_NET_SITE_ID')

ROOT_URLCONF = 'speedy.net.urls'

STATIC_ROOT = str(APP_DIR / 'static_serve')

AUTH_SITE_PROFILE_MODEL = 'accounts.SiteProfile'
