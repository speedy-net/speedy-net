"""
Django app configuration for the Speedy Match matches app.
"""
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMatchMatchesAppConfig(AppConfig):
    """
    Django app configuration for the Speedy Match matches app.
    """
    default = True
    name = 'speedy.match.matches'
    verbose_name = _("Speedy Match Matches")
    label = 'matches'


