from speedy.core import admin
from speedy.core.accounts.admin import SiteProfileBaseAdmin
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


class SpeedyNetSiteProfileAdmin(SiteProfileBaseAdmin):
    pass


admin.site.register(SpeedyNetSiteProfile, SpeedyNetSiteProfileAdmin)


