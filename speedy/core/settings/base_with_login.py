from .base import *


LOGIN_ENABLED = True

INSTALLED_APPS += [
    'speedy.core.contact_by_form',
    'speedy.composer.accounts',  # For admin - for deleting users.
    'speedy.mail.accounts',  # For admin - for deleting users.
]

MIDDLEWARE += [
    'speedy.core.accounts.middleware.SiteProfileMiddleware',
]

USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
]

ADMIN_USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
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

