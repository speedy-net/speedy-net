from speedy.core import admin
from speedy.core.accounts.admin import SiteProfileBaseAdmin
from speedy.mail.accounts.models import SiteProfile as SpeedyMailSiteProfile


class SpeedyMailSiteProfileAdmin(SiteProfileBaseAdmin):
    pass


admin.site.register(SpeedyMailSiteProfile, SpeedyMailSiteProfileAdmin)


