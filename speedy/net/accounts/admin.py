from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core import admin
    from speedy.core.accounts.admin import SiteProfileBaseAdmin
    from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


    class SpeedyNetSiteProfileAdmin(SiteProfileBaseAdmin):
        pass


    admin.site.register(SpeedyNetSiteProfile, SpeedyNetSiteProfileAdmin)


