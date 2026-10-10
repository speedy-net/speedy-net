"""
Django app configuration for the Speedy Match profiles app.
"""
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMatchProfilesAppConfig(AppConfig):
    """
    Django app configuration for the Speedy Match profiles app.
    """
    default = True
    name = 'speedy.match.profiles'
    verbose_name = _("Speedy Match Profiles")
    label = 'match_profiles'


