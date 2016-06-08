from .base import *

SITE_NAME = 'Speedy Net'

SITE_URL = env('SPEEDY_NET_URL')

STATIC_ROOT = str(APP_DIR / 'static_serve')
