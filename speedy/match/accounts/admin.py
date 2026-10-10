"""
Admin configuration for the Speedy Match accounts app (the site profile admin).
"""
from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core import admin
    from speedy.core.accounts.admin import SiteProfileBaseAdmin
    from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


    class SpeedyMatchSiteProfileAdmin(SiteProfileBaseAdmin):
        """
        Admin configuration for the Speedy Match SiteProfile model. Inherits all behavior from SiteProfileBaseAdmin without any additions.
        """
        pass


    admin.site.register(SpeedyMatchSiteProfile, SpeedyMatchSiteProfileAdmin)


