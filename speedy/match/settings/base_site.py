from django.utils.translation import ugettext_lazy as _
from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = int(env('SPEEDY_MATCH_SITE_ID'))

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

MIN_HEIGHT_ALLOWED = 1 # In cm.
MAX_HEIGHT_ALLOWED = 450 # In cm.

SITE_PROFILE_FORM_FIELDS = [
    [],  # There's no step 0
    [],  # Step 1 = registration form
    ['photo'],
    ['profile_description', 'city', 'height'],
    ['children', 'more_children'],
    ['diet', 'smoking_status'],
    ['marital_status'],
    ['gender_to_match', 'match_description', 'min_age_match', 'max_age_match'],
    ['diet_match', 'smoking_status_match'],
    ['marital_status_match']
]

USER_PROFILE_WIDGETS += [
    'speedy.match.profiles.widgets.UserRankWidget',
    'speedy.match.profiles.widgets.UserExtraDetailsWidget',
    'speedy.net.profiles.widgets.UserOnSpeedyNetWidget',
]
