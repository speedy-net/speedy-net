from .base_site import *


def activate_development(settings):
    settings.update({
        'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
        'MIDDLEWARE': ['debug_toolbar.middleware.DebugToolbarMiddleware'] + settings['MIDDLEWARE'],
        'INSTALLED_APPS': settings['INSTALLED_APPS'] + ['debug_toolbar'],
        'DEBUG': True,
    })

activate_development(settings=globals())
