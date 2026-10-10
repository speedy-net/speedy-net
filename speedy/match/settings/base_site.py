from django.utils.translation import gettext_lazy as _
from speedy.core.settings.base_with_login import *
from speedy.core.settings.utils import update_site_paths
from speedy.net.settings.global_settings import *
from speedy.match.settings.global_settings import *
from .utils import APP_DIR

update_site_paths(settings=globals())

# The Django site ID of Speedy Match (the same value as SPEEDY_MATCH_SITE_ID).
SITE_ID = SPEEDY_MATCH_SITE_ID

# The title of the Speedy Match site, shown in pages and emails (translatable).
SITE_TITLE = _('Speedy Match [alpha]')

# The root URL configuration module of Speedy Match.
ROOT_URLCONF = 'speedy.match.urls'

# Sender address for notification emails, and sender address for server error emails sent to the webmaster (Speedy Match).
DEFAULT_FROM_EMAIL = 'notifications@speedymatch.com'
SERVER_EMAIL = 'webmaster+server@speedymatch.com'

INSTALLED_APPS += [
    'speedy.match.profiles',
    'speedy.match.matches',
]

# The SiteProfile model of Speedy Match, used by the accounts app for per-site user profiles.
AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'

# Whether a user's Speedy Match profile is activated automatically after registration (not automatic, the user has to complete the activation steps).
ACTIVATE_PROFILE_AFTER_REGISTRATION = False

# The form used to activate a user's Speedy Match profile.
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


