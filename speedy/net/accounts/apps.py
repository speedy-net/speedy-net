from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyNetAccountsAppConfig(AppConfig):
    name = 'speedy.net.accounts'
    verbose_name = _("Speedy Net Accounts")
    label = 'net_accounts'


