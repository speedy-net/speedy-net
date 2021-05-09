def activate_production(settings):
    settings.update({
        'DEFAULT_FROM_EMAIL': 'notifications@speedy.net',
        'SERVER_EMAIL': 'webmaster+production-server@speedy.net',
        'DEBUG': False,
    })


