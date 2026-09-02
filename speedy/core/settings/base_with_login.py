from django.utils.translation import gettext_lazy as _

from .base import *

LOGIN_ENABLED = True

INSTALLED_APPS += [
    'speedy.core.contact_by_form',
]

MIDDLEWARE += [
    'speedy.core.accounts.middleware.SiteProfileMiddleware',
]

USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
]

ADMIN_USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.admin.widgets.AdminUserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
    'speedy.core.profiles.admin.widgets.AdminUserInfoWidget',
]

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/me/'

DONT_REDIRECT_INACTIVE_USER = [
    '/logout/',
    '/welcome/',
    '/registration-step-',
    '/about/',
    '/privacy/',
    '/terms/',
    '/contact/',
    '/edit-profile/',
    '/admin/',
    '/media/',
    '/static/',
    '/set-session/',
]

DONT_REDIRECT_ADMIN = [
    '/admin/',
    '/logout/',
    '/media/',
    '/static/',
    '/set-session/',
]

IGNORE_LAST_VISIT = [
    '/set-session/',
]

LOCALE_PATHS += [
    str(ROOT_DIR / 'speedy/net/locale'),
    str(ROOT_DIR / 'speedy/match/locale'),
]

_LANGUAGES = LANGUAGES

_LANGUAGES_TO_ADD_1 = [
    ('fr', _('French')),
    ('de', _('German')),
    ('es', _('Spanish')),
    ('pt', _('Portuguese')),
    ('it', _('Italian')),
    ('nl', _('Dutch')),
    ('ja', _('Japanese')),
    ('ru', _('Russian')),
    ('zh', _('Chinese')),
    ('pl', _('Polish')),
    ('fa', _('Persian')),
]

_LANGUAGES_TO_ADD_2 = [
    ('ko', _('Korean')),
    ('ar', _('Arabic')),
    ('id', _('Indonesian')),
    ('uk', _('Ukrainian')),
    ('tr', _('Turkish')),
    ('vi', _('Vietnamese')),
    ('cs', _('Czech')),
    ('sv', _('Swedish')),
    ('fi', _('Finnish')),
    ('hu', _('Hungarian')),
    ('th', _('Thai')),
    ('el', _('Greek')),
    ('ms', _('Malay')),
    ('sr', _('Serbian')),
    ('ro', _('Romanian')),
    ('bn', _('Bengali')),
    ('ca', _('Catalan')),
    ('no', _('Norwegian (Bokmål)')),
    ('bg', _('Bulgarian')),
    ('da', _('Danish')),
    ('sk', _('Slovak')),
    ('hi', _('Hindi')),
    ('et', _('Estonian')),
    ('hr', _('Croatian')),
]

LANGUAGES = _LANGUAGES[:1] + _LANGUAGES_TO_ADD_1 + _LANGUAGES[1:] + _LANGUAGES_TO_ADD_2

LANGUAGES_IN_HTML = _LANGUAGES[:1] + _LANGUAGES_TO_ADD_1[:6] + _LANGUAGES[1:]

# LANGUAGES_WITH_ADS = {'en'}
# LANGUAGES_WITH_ADS = set()
# LANGUAGES_WITH_ADS = {'en', 'fr', 'de', 'es', 'pt'}
LANGUAGES_WITH_ADS = set()

