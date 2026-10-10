"""
Utilities for the Speedy Core staging environment settings: the function which updates a settings dict for staging.
"""


def activate_staging(settings):
    """
    Update the given settings dict in place for the staging environment (from/server email addresses, admins/managers, DEBUG enabled).

    :param settings: The settings dict to update.
    :type settings: dict
    """
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


