from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.accounts.models import UserAccessField, User
from speedy.core.accounts.models import SiteProfileBase
from speedy.core.base.models import TimeStampedModel


class SiteProfile(SiteProfileBase):
    RELATED_NAME = 'speedy_net_site_profile'
    user = models.OneToOneField(User, primary_key=True, related_name=RELATED_NAME)

    class Meta:
        verbose_name = 'Speedy Net Profile'
        verbose_name_plural = 'Speedy Net Profiles'

    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'), default=True)

    def __str__(self):
        return '{} @ Speedy Net'.format(self.user)

    def activate(self):
        self.is_active = True
        self.user.is_active = True
        self.user.save(update_fields={'is_active'})
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        if not self.user.is_superuser:
            self.user.is_active = False
            self.user.save(update_fields={'is_active'})
        self.save(update_fields={'is_active'})

    def get_name(self):
        return self.user.get_full_name()

