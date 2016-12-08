from django.utils.translation import ugettext_lazy as _
from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths

update_site_paths(settings=globals())

SITE_ID = int(env('SPEEDY_NET_SITE_ID'))

SITE_TITLE = _('Speedy Net [alpha]')

ROOT_URLCONF = 'speedy.net.urls'

AUTH_SITE_PROFILE_MODEL = 'accounts.SiteProfile'
