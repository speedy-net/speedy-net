from django.utils.translation import gettext_lazy as _
from speedy.core.settings.base_with_login import *
from speedy.core.settings.utils import update_site_paths
from speedy.match.settings.global_settings import *
from speedy.net.settings.global_settings import *
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = SPEEDY_NET_SITE_ID

SITE_TITLE = _('Speedy Net [alpha]')

ROOT_URLCONF = 'speedy.net.urls'

DEFAULT_FROM_EMAIL = 'webmaster@speedy.net'
SERVER_EMAIL = 'webmaster+server@speedy.net'

INSTALLED_APPS += [
    # 'speedy.net.pages',
    # 'speedy.net.groups',
    # 'speedy.net.causes',
]

AUTH_SITE_PROFILE_MODEL = 'net_accounts.SiteProfile'

ACTIVATE_PROFILE_AFTER_REGISTRATION = True  # ~~~~ TODO: maybe user has to confirm email before activation?

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


