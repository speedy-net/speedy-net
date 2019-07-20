def activate_staging(settings):
    admins = (
        ('Uri Rodberg', 'webmaster@speedy.net'),
        # ('Evgeniy Kirov', 'evgeniy.kirov@initech.co.il'),
    )
    settings.update({
        'DEFAULT_FROM_EMAIL': 'webmaster@speedy.net.2.speedy-technologies.com',
        'ADMINS': admins,
        'MANAGERS': admins,
        'DEBUG': True,
    })


