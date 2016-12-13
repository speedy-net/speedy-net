from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = int(env('SPEEDY_COMPOSER_SITE_ID'))

ROOT_URLCONF = 'speedy.composer.urls'

INSTALLED_APPS += [
    'speedy.composer.accounts',
    'speedy.composer.compose',
]

AUTH_SITE_PROFILE_MODEL = 'composer_accounts.SiteProfile'
