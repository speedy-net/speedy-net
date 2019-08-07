from django.conf import settings as django_settings


if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
    from speedy.net.admin import site
elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
    from speedy.match.admin import site
else:
    from .sites import admin_site as site


