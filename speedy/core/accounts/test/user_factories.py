from django.conf import settings as django_settings


if (django_settings.LOGIN_ENABLED):
    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
        from speedy.net.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, ActiveUserFactory
    if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
        from speedy.match.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, ActiveUserFactory


