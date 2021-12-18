from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMatchAccountsAppConfig(AppConfig):
    default = True
    name = 'speedy.match.accounts'
    verbose_name = _("Speedy Match Accounts")
    label = 'match_accounts'


