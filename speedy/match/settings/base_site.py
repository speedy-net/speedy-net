from django.utils.translation import ugettext_lazy as _
from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = int(env('SPEEDY_MATCH_SITE_ID'))

SITE_TITLE = _('Speedy Match [alpha]')

ROOT_URLCONF = 'speedy.match.urls'

INSTALLED_APPS += [
    'speedy.match.accounts',
    'speedy.match.likes',
]

AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'

ACTIVATE_PROFILE_AFTER_REGISTRATION = False
