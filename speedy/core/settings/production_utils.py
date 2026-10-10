def activate_production(settings):
    """
    Update the given settings dict in place for the production environment (from/server email addresses, DEBUG disabled).

    :param settings: The settings dict to update.
    :type settings: dict
    """
    settings.update({
        'DEFAULT_FROM_EMAIL': 'notifications@speedy.net',
        'SERVER_EMAIL': 'webmaster+production-server@speedy.net',
        'DEBUG': False,
    })


