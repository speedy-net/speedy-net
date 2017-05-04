from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.accounts.models import ACCESS_ANYONE, AccessField, ACCESS_ME
from speedy.core.accounts.models import SiteProfileBase
from speedy.core.base.models import TimeStampedModel


class SiteProfile(SiteProfileBase):
    class Meta:
        verbose_name = 'Speedy Net Profile'
        verbose_name_plural = 'Speedy Net Profiles'

    access_account = ACCESS_ANYONE
    access_dob_day_month = AccessField(verbose_name=_('who can view my birth month and day'), default=ACCESS_ME)
    access_dob_year = AccessField(verbose_name=_('who can view my birth year'), default=ACCESS_ME)
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'), default=True)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        self.save(update_fields={'is_active'})

    def get_name(self):
        return self.user.get_full_name()

