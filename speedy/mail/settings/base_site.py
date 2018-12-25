from django.utils.translation import gettext_lazy as _
from speedy.core.settings.base_without_login import *
from speedy.core.settings.utils import update_site_paths
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = SPEEDY_MAIL_SOFTWARE_SITE_ID

ROOT_URLCONF = 'speedy.mail.urls'

# if (LOGIN_ENABLED):
if (True or LOGIN_ENABLED): # ~~~~ TODO: remove this line!
    INSTALLED_APPS += [
        'speedy.mail.accounts',
    ]

    AUTH_SITE_PROFILE_MODEL = 'mail_accounts.SiteProfile'


