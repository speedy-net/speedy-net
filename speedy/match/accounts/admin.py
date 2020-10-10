from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core import admin
    from speedy.core.accounts.admin import SiteProfileBaseAdmin
    from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


    class SpeedyMatchSiteProfileAdmin(SiteProfileBaseAdmin):
        pass


    admin.site.register(SpeedyMatchSiteProfile, SpeedyMatchSiteProfileAdmin)


