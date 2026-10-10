from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core import admin
    from speedy.core.accounts.admin import SiteProfileBaseAdmin
    from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


    class SpeedyNetSiteProfileAdmin(SiteProfileBaseAdmin):
        """
        Admin configuration for the Speedy Net site profile model. Uses the default admin configuration defined by the base site profile admin class.
        """
        pass


    admin.site.register(SpeedyNetSiteProfile, SpeedyNetSiteProfileAdmin)


