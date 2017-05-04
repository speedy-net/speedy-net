from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.accounts.models import SiteProfileBase


class SiteProfile(SiteProfileBase):
    class Meta:
        verbose_name = 'Speedy Composer Profile'
        verbose_name_plural = 'Speedy Composer Profiles'

    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'), default=False)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        self.save(update_fields={'is_active'})

    def get_name(self):
        return self.user.get_full_name()

