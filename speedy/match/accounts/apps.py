from django.contrib.auth.apps import AuthConfig


class SpeedyMatchAccountsConfig(AuthConfig):
    name = 'speedy.match.accounts'
    label = 'match_accounts'
