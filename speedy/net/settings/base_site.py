"""
Base Django settings of the Speedy Net site, shared by all the Speedy Net environments.
"""
from django.utils.translation import gettext_lazy as _
from speedy.core.settings.base_with_login import *
from speedy.core.settings.utils import update_site_paths
from speedy.match.settings.global_settings import *
from speedy.net.settings.global_settings import *
from .utils import APP_DIR

update_site_paths(settings=globals())

# The Django site ID of Speedy Net (the same value as SPEEDY_NET_SITE_ID).
SITE_ID = SPEEDY_NET_SITE_ID

# The title of the Speedy Net site, shown in pages and emails (translatable).
SITE_TITLE = _('Speedy Net [alpha]')

# The root URL configuration module of Speedy Net.
ROOT_URLCONF = 'speedy.net.urls'

# Sender address for notification emails, and sender address for server error emails sent to the webmaster (Speedy Net).
DEFAULT_FROM_EMAIL = 'notifications@speedy.net'
SERVER_EMAIL = 'webmaster+server@speedy.net'

INSTALLED_APPS += [
    # 'speedy.net.pages',
    # 'speedy.net.groups',
    # 'speedy.net.causes',
]

# The SiteProfile model of Speedy Net, used by the accounts app for per-site user profiles.
AUTH_SITE_PROFILE_MODEL = 'net_accounts.SiteProfile'

# Whether a user's Speedy Net profile is activated automatically after registration.
ACTIVATE_PROFILE_AFTER_REGISTRATION = True  # ~~~~ TODO: maybe user has to confirm email before activation?

# The form used to activate a user's Speedy Net profile.
SITE_PROFILE_ACTIVATION_FORM = 'speedy.core.accounts.forms.SiteProfileActivationForm'

USER_PROFILE_WIDGETS += [
    'speedy.core.friends.widgets.UserFriendsWidget',
    'speedy.match.profiles.widgets.UserOnSpeedyMatchWidget',
]

ADMIN_USER_PROFILE_WIDGETS += [
    'speedy.core.friends.widgets.UserFriendsWidget',
    'speedy.core.friends.admin.widgets.AdminUserFriendsWidget',
    'speedy.match.profiles.widgets.UserOnSpeedyMatchWidget',
]


