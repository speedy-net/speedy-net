from speedy.core.admin import admin_site
from speedy.core.accounts.admin import SiteProfileBaseAdmin
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


class SpeedyNetSiteProfileAdmin(SiteProfileBaseAdmin):
    pass


admin_site.register(SpeedyNetSiteProfile, SpeedyNetSiteProfileAdmin)


