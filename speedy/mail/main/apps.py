"""
Django app configuration for the Speedy Mail Software main app.
"""
from django.apps import AppConfig


class SpeedyMailSoftwareMainAppConfig(AppConfig):
    """
    App configuration for the Speedy Mail Software main app.
    """
    default = True
    name = 'speedy.mail.main'
    verbose_name = "Speedy Mail Software Main"
    label = 'mail_main'


