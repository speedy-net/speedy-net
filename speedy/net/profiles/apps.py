"""
Django app configuration for the Speedy Net profiles app.
"""
from django.apps import AppConfig


class SpeedyNetProfilesAppConfig(AppConfig):
    """
    App configuration for the Speedy Net profiles app.
    """
    default = True
    name = 'speedy.net.profiles'
    verbose_name = "Speedy Net Profiles"
    label = 'net_profiles'


