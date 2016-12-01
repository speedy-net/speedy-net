from django.contrib.auth.apps import AuthConfig


class SpeedyComposerAccountsConfig(AuthConfig):
    name = 'speedy.composer.accounts'
    label = 'composer_accounts'
