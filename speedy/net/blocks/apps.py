"""
Django app configuration for the Speedy Net blocks app.
"""
from django.apps import AppConfig


class SpeedyNetBlocksAppConfig(AppConfig):
    """
    App configuration for the Speedy Net blocks app.
    """
    default = True
    name = 'speedy.net.blocks'
    verbose_name = "Speedy Net Blocks"
    label = 'net_blocks'


