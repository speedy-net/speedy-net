from .base_site import *
from speedy.net.settings.development_base import *

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

INSTALLED_APPS += [
    'debug_toolbar',
]

