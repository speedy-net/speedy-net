"""
Admin configuration for the Speedy Mail Software accounts app (the site profile admin).
"""
from speedy.core import admin
from speedy.core.accounts.admin import SiteProfileBaseAdmin
from speedy.mail.accounts.models import SiteProfile as SpeedyMailSiteProfile


class SpeedyMailSiteProfileAdmin(SiteProfileBaseAdmin):
    """
    Admin configuration for the Speedy Mail Software site profile.
    """
    pass


admin.site.register(SpeedyMailSiteProfile, SpeedyMailSiteProfileAdmin)


