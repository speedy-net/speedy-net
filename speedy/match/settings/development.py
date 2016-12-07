from .base_site import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

INSTALLED_APPS += [
    'debug_toolbar',
]

ALLOWED_HOSTS = [".localhost"]
