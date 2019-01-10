def activate_staging(settings):
    admins = (
        ('Uri Rodberg', 'webmaster@speedy.net'),
        # ('Evgeniy Kirov', 'evgeniy.kirov@initech.co.il'),
    )
    settings.update({
        'DEFAULT_FROM_EMAIL': 'webmaster@speedy2000.net',
        'ADMINS': admins,
        'MANAGERS': admins,
        'DEBUG': True,
    })


