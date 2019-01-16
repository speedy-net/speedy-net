from django.contrib import admin
from speedy.core.accounts.admin import SiteProfileBaseAdmin
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class SpeedyMatchSiteProfileAdmin(SiteProfileBaseAdmin):
    pass


admin.site.register(SpeedyMatchSiteProfile, SpeedyMatchSiteProfileAdmin)


