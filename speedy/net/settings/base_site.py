from .base import *

SITE_NAME = 'Speedy Net'

SITE_URL = env('SPEEDY_NET_URL')

ROOT_URLCONF = 'speedy.net.urls'

STATIC_ROOT = str(APP_DIR / 'static_serve')

AUTH_PROFILE_MODEL = 'accounts.SiteProfile'
