from django.contrib.auth.apps import AuthConfig


class SpeedyNetAccountsConfig(AuthConfig):
    name = 'speedy.net.accounts'
    label = 'net_accounts'
