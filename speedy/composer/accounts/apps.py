"""
Django app configuration for the Speedy Composer accounts app.
"""
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyComposerAccountsAppConfig(AppConfig):
    """
    App configuration for the Speedy Composer accounts app.
    """
    default = True
    name = 'speedy.composer.accounts'
    verbose_name = _("Speedy Composer Accounts")
    label = 'composer_accounts'


