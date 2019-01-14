from django.conf import settings as django_settings
from django.contrib.sites.models import Site


if (django_settings.LOGIN_ENABLED):
    site = Site.objects.get_current()
    if (site.id == django_settings.SPEEDY_NET_SITE_ID):
        from speedy.net.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, ActiveUserFactory
    if (site.id == django_settings.SPEEDY_MATCH_SITE_ID):
        from speedy.match.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, ActiveUserFactory


