from django.utils.translation import ugettext_lazy as _

from .base import *

SITE_ID = int(env('SPEEDY_NET_SITE_ID'))

SITE_TITLE = _('Speedy Net [alpha]')

ROOT_URLCONF = 'speedy.net.urls'

STATIC_ROOT = str(APP_DIR / 'static_serve')

AUTH_SITE_PROFILE_MODEL = 'accounts.SiteProfile'
