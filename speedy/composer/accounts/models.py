from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.net.accounts.models import NamedEntity, SiteProfileBase


class SpeedyComposerNamedEntity(NamedEntity):
    MIN_USERNAME_LENGTH = 1
    MAX_USERNAME_LENGTH = 200
    MIN_SLUG_LENGTH = 1
    MAX_SLUG_LENGTH = 200
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 200

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.name)


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
