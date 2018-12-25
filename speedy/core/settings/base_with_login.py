from .base import *


LOGIN_ENABLED = True


INSTALLED_APPS += [
    'speedy.core.accounts',
    'speedy.core.im',
    'speedy.core.profiles',
    'speedy.core.friends',
    'speedy.core.blocks',
    'speedy.core.uploads',
    'speedy.core.feedback',
]

MIDDLEWARE += [
    'speedy.core.accounts.middleware.SiteProfileMiddleware',
]

USER_PROFILE_WIDGETS = [
    'speedy.core.profiles.widgets.UserPhotoWidget',
    'speedy.core.profiles.widgets.UserInfoWidget',
]

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 120

PASSWORD_VALIDATORS = [
    {
        'NAME': 'speedy.core.accounts.validators.PasswordMinLengthValidator',
    },
    {
        'NAME': 'speedy.core.accounts.validators.PasswordMaxLengthValidator',
    },
]

AUTH_PASSWORD_VALIDATORS = PASSWORD_VALIDATORS

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/me/'

UNAVAILABLE_USERNAMES = [
    'about',
    'admin',
    'contact',
    'css',
    'domain',
    'editprofile',
    'feedback',
    'friends',
    'i18n',
    'icons',
    'images',
    'javascript',
    'js',
    'locale',
    'login',
    'logout',
    'mail',
    'me',
    'messages',
    'postmaster',
    'python',
    'register',
    'report',
    'resetpassword',
    'root',
    'setsession',
    'speedy',
    'speedycomposer',
    'speedymail',
    'speedymailsoftware',
    'speedymatch',
    'speedynet',
    'static',
    'uri',
    'webmaster',
    'welcome',
]

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

SITE_PROFILE_ACTIVATION_FORM = 'speedy.core.accounts.forms.SiteProfileActivationForm'

