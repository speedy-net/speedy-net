from django.utils.translation import ugettext_lazy as _
from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths
from speedy.net.settings.global_settings import *
from speedy.match.settings.global_settings import *
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = SPEEDY_MATCH_SITE_ID

SITE_TITLE = _('Speedy Match [alpha]')

ROOT_URLCONF = 'speedy.match.urls'

DEFAULT_FROM_EMAIL = 'webmaster@speedymatch.com'

INSTALLED_APPS += [
    'speedy.match.accounts',
    'speedy.match.profiles',
    'speedy.match.likes',
    'speedy.match.matches',
]

AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'

ACTIVATE_PROFILE_AFTER_REGISTRATION = False

SITE_PROFILE_ACTIVATION_FORM = 'speedy.match.accounts.forms.SpeedyMatchProfileActivationForm'

USER_PROFILE_WIDGETS += [
    'speedy.match.profiles.widgets.UserRankWidget',
    'speedy.match.profiles.widgets.UserExtraDetailsWidget',
    'speedy.net.profiles.widgets.UserOnSpeedyNetWidget',
]


