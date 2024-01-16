from django.utils.translation import gettext_lazy as _
from speedy.core.settings.base_with_login import *
from speedy.core.settings.utils import update_site_paths
from speedy.net.settings.global_settings import *
from speedy.match.settings.global_settings import *
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = SPEEDY_MATCH_SITE_ID

SITE_TITLE = _('Speedy Match [alpha]')

ROOT_URLCONF = 'speedy.match.urls'

DEFAULT_FROM_EMAIL = 'notifications@speedymatch.com'
SERVER_EMAIL = 'webmaster+server@speedymatch.com'

INSTALLED_APPS += [
    'speedy.match.profiles',
    'speedy.match.matches',
]

CACHE_SET_MATCHES_TIMEOUT = 6 * 60  # 6 minutes
CACHE_GET_MATCHES_SLIDING_TIMEOUT = 0

AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'

ACTIVATE_PROFILE_AFTER_REGISTRATION = False

SITE_PROFILE_ACTIVATION_FORM = 'speedy.match.accounts.forms.SpeedyMatchProfileActivationForm'

USER_PROFILE_WIDGETS += [
    'speedy.match.profiles.widgets.UserRankWidget',
    'speedy.match.profiles.widgets.UserExtraDetailsWidget',
    'speedy.net.profiles.widgets.UserOnSpeedyNetWidget',
]

ADMIN_USER_PROFILE_WIDGETS += [
    'speedy.match.profiles.widgets.UserExtraDetailsWidget',
    'speedy.net.profiles.widgets.UserOnSpeedyNetWidget',
]


