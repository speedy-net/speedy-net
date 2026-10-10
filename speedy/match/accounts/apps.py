from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMatchAccountsAppConfig(AppConfig):
    """
    Django app configuration for the Speedy Match accounts app.
    """
    default = True
    name = 'speedy.match.accounts'
    verbose_name = _("Speedy Match Accounts")
    label = 'match_accounts'


