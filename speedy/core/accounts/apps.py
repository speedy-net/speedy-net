from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyCoreAccountsAppConfig(AppConfig):
    default = True
    name = 'speedy.core.accounts'
    verbose_name = _("Speedy Core Accounts")
    label = 'accounts'


