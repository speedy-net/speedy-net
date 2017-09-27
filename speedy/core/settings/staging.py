from .base_site import *


def activate_staging(settings):
    admins = (
        ('Uri Even-Chen', 'webmaster@speedy.net'),
        ('Asaf Gery', 'asaf.gery@gmail.com'),
    )
    settings.update({
        'DEFAULT_FROM_EMAIL': 'webmaster@speedy2000.net',
        'ADMINS': admins,
        'MANAGERS': admins,
        'DEBUG': True,
    })

activate_staging(settings=globals())

