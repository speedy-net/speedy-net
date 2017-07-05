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
    'speedy.match.likes',
    'speedy.match.matches'
]

AUTH_SITE_PROFILE_MODEL = 'match_accounts.SiteProfile'

ACTIVATE_PROFILE_AFTER_REGISTRATION = False

SITE_PROFILE_ACTIVATION_FORM = 'speedy.match.accounts.forms.SpeedyMatchProfileActivationForm'

SITE_PROFILE_FORM_FIELDS = [
    ['photo'],
    ['profile_description', 'city', 'height'],
    ['children', 'more_children'],
    ['diet', 'smoking'],
    ['marital_status'],
    ['gender_to_match', 'match_description', 'min_age_match', 'max_age_match'],
    ['diet_match', 'smoking_match'],
    ['marital_status_match']
]

USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
]
