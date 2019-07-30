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

IGNORE_LAST_VISIT = [
    '/set-session/',
]

LOCALE_PATHS += [
    str(ROOT_DIR / 'speedy/net/locale'),
    str(ROOT_DIR / 'speedy/match/locale'),
]

