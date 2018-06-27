from django.utils.translation import ugettext_lazy as _
from speedy.core.settings.base import *
from speedy.core.settings.base_site import update_site_paths
from .utils import APP_DIR

update_site_paths(settings=globals())

SITE_ID = int(env('SPEEDY_NET_SITE_ID'))

SITE_TITLE = _('Speedy Net [alpha]')

ROOT_URLCONF = 'speedy.net.urls'

INSTALLED_APPS += [
    'speedy.net.accounts',
    'speedy.net.pages',
    'speedy.net.groups',
    'speedy.net.causes',
    # Required by "A Speedy Net profile should have a link to the relevant Speedy Match profile"
    # https://trello.com/c/2D1njNa4
    'speedy.match.accounts',
    'speedy.match.likes',
]

AUTH_SITE_PROFILE_MODEL = 'net_accounts.SiteProfile'

USER_PROFILE_WIDGETS += [
    'speedy.core.friends.widgets.UserFriendsWidget',
    'speedy.match.profiles.widgets.UserOnSpeedyMatchWidget',
]
