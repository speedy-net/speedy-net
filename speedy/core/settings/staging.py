from .base_site import *


def activate_staging(settings):
    admins = (
        ('Uri Even-Chen', 'webmaster@speedy.net'),
        ('Gleb Tocarenco', 'gleb.tocarenco@initech.co.il'),
    )
    settings.update({
        'DEFAULT_FROM_EMAIL': 'webmaster@speedy2000.net',
        'ADMINS': admins,
        'MANAGERS': admins,
        'DEBUG': True,
    })

activate_staging(settings=globals())

