"""
Django settings for sites with login (Speedy Net and Speedy Match), extending the Speedy Core base settings with login URLs, profile widgets, redirect rules and the available languages.
"""
from django.utils.translation import gettext_lazy as _

from .base import *

# Login is enabled on sites which use these settings (Speedy Net and Speedy Match).
LOGIN_ENABLED = True

INSTALLED_APPS += [
    'speedy.core.contact_by_form',
]

MIDDLEWARE += [
    'speedy.core.accounts.middleware.SiteProfileMiddleware',
]

# Widgets displayed on a user's profile page.
USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
]

# Widgets displayed on a user's profile page when viewed by an admin.
ADMIN_USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.admin.widgets.AdminUserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
    'speedy.core.profiles.admin.widgets.AdminUserInfoWidget',
]

# URL of the login page.
LOGIN_URL = '/login/'

# URL to which users are redirected after login.
LOGIN_REDIRECT_URL = '/me/'

# URL prefixes which inactive users can access without being redirected to complete registration.
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

# URL prefixes which admins can access without being redirected.
DONT_REDIRECT_ADMIN = [
    '/admin/',
    '/logout/',
    '/media/',
    '/static/',
    '/set-session/',
]

# URL prefixes which don't update the user's last visit time.
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
    ('az', _('Azerbaijani')),
    ('zh-yue', _('Cantonese')),
    ('lt', _('Lithuanian')),
    ('sl', _('Slovenian')),
    ('eu', _('Basque')),
    ('hy', _('Armenian')),
    ('uz', _('Uzbek')),
    ('ta', _('Tamil')),
    ('lv', _('Latvian')),
]

# Available languages: the base languages combined with additional languages, ordered with English first and Hebrew after the first group.
LANGUAGES = _LANGUAGES[:1] + _LANGUAGES_TO_ADD_1 + _LANGUAGES[1:] + _LANGUAGES_TO_ADD_2

# Languages shown in the HTML language selector: English, the first six additional languages and Hebrew.
LANGUAGES_IN_HTML = _LANGUAGES[:1] + _LANGUAGES_TO_ADD_1[:6] + _LANGUAGES[1:]

# LANGUAGES_WITH_ADS = {'en'}
# LANGUAGES_WITH_ADS = set()
# LANGUAGES_WITH_ADS = {'en', 'fr', 'de', 'es', 'pt'}
LANGUAGES_WITH_ADS = set()


