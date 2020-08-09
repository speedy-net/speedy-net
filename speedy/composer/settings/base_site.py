from django.utils.translation import gettext_lazy as _
from speedy.core.settings.base_without_login import *
from speedy.core.settings.utils import update_site_paths
from speedy.match.settings.global_settings import *  # ~~~~ TODO: Maybe we don't need this here? (added because the migrations fail).
from speedy.net.settings.global_settings import *  # ~~~~ TODO: Maybe we don't need this here? (added because the migrations fail).
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = SPEEDY_COMPOSER_SITE_ID

ROOT_URLCONF = 'speedy.composer.urls'

# if (LOGIN_ENABLED):
if (True or LOGIN_ENABLED):  # ~~~~ TODO: remove this line!
    INSTALLED_APPS += [
        # 'speedy.composer.accounts',
        # 'speedy.composer.compose',
    ]

    AUTH_SITE_PROFILE_MODEL = 'composer_accounts.SiteProfile'


