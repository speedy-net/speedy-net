from django.contrib.auth.apps import AuthConfig


class SpeedyMailSoftwareAccountsConfig(AuthConfig):
    name = 'speedy.mail.accounts'
    label = 'mail_accounts'


