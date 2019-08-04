from speedy.core.admin import admin_site
from speedy.mail.accounts.models import SiteProfile as SpeedyMailSiteProfile

admin_site.register(SpeedyMailSiteProfile)


