def activate_staging(settings):
    admins = (
        # ('Uri Rodberg', 'webmaster@speedy.net'),
        ('Uri Rodberg', 'webmaster+staging-server@speedy.net'),
        # ('Evgeniy Kirov', 'evgeniy.kirov@initech.co.il'),
    )
    settings.update({
        'DEFAULT_FROM_EMAIL': 'notifications@speedy.net.2.speedy-technologies.com',
        'SERVER_EMAIL': 'webmaster+staging-server@speedy.net.2.speedy-technologies.com',
        'ADMINS': admins,
        'MANAGERS': admins,
        'DEBUG': True,
    })


