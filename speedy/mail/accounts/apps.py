from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMailSoftwareAccountsAppConfig(AppConfig):
    """
    App configuration for the Speedy Mail Software accounts app.
    """
    default = True
    name = 'speedy.mail.accounts'
    verbose_name = _("Speedy Mail Software Accounts")
    label = 'mail_accounts'


