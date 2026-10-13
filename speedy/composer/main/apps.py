"""
Django app configuration for the Speedy Composer main app.
"""
from django.apps import AppConfig


class SpeedyComposerMainAppConfig(AppConfig):
    """
    App configuration for the Speedy Composer main app.
    """
    default = True
    name = 'speedy.composer.main'
    verbose_name = "Speedy Composer Main"
    label = 'composer_main'


