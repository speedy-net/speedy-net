from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyComposerAccountsAppConfig(AppConfig):
    name = 'speedy.composer.accounts'
    verbose_name = _("Speedy Composer Accounts")
    label = 'composer_accounts'


