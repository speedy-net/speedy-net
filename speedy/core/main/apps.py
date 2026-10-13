"""
Django app configuration for the Speedy Core main app.
"""
from django.apps import AppConfig


class SpeedyCoreMainAppConfig(AppConfig):
    """
    App configuration for the Speedy Core main app.
    """
    default = True
    name = 'speedy.core.main'
    verbose_name = "Speedy Core Main"
    label = 'core_main'


