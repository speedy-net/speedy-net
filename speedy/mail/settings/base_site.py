from django.utils.translation import ugettext_lazy as _
from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = int(env('SPEEDY_MAIL_SOFTWARE_SITE_ID'))

ROOT_URLCONF = 'speedy.mail.urls'

INSTALLED_APPS += [
    'speedy.mail.accounts',
]

AUTH_SITE_PROFILE_MODEL = 'mail_accounts.SiteProfile'
