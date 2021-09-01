from speedy.core import admin
from speedy.core.accounts.admin import SiteProfileBaseAdmin
from speedy.composer.accounts.models import SiteProfile as SpeedyComposerSiteProfile


class SpeedyComposerSiteProfileAdmin(SiteProfileBaseAdmin):
    pass


admin.site.register(SpeedyComposerSiteProfile, SpeedyComposerSiteProfileAdmin)


