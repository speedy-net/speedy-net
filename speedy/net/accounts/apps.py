"""
Django app configuration for the Speedy Net accounts app.
"""
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyNetAccountsAppConfig(AppConfig):
    """
    App configuration for the Speedy Net accounts app.
    """
    default = True
    name = 'speedy.net.accounts'
    verbose_name = _("Speedy Net Accounts")
    label = 'net_accounts'


