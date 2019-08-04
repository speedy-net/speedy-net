from speedy.match.admin import admin_site
from speedy.core.accounts.admin import SiteProfileBaseAdmin
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class SpeedyMatchSiteProfileAdmin(SiteProfileBaseAdmin):
    pass


admin_site.register(SpeedyMatchSiteProfile, SpeedyMatchSiteProfileAdmin)


