from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMailSoftwareAccountsAppConfig(AppConfig):
    default = True
    name = 'speedy.mail.accounts'
    verbose_name = _("Speedy Mail Software Accounts")
    label = 'mail_accounts'


