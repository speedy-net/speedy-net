from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.accounts.models import SiteProfileBase, User


class SiteProfile(SiteProfileBase):
    RELATED_NAME = 'speedy_mail_site_profile'
    user = models.OneToOneField(to=User, verbose_name=_('user'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)

    class Meta:
        verbose_name = 'Speedy Composer Profile'
        verbose_name_plural = 'Speedy Composer Profiles'

    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'), default=False)

    def __str__(self):
        return '{} @ Speedy Mail Software'.format(self.user)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        self.save(update_fields={'is_active'})

    def get_name(self):
        return self.user.get_full_name()

