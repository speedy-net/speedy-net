from django.db import models
from django.utils.translation import gettext_lazy as _

from speedy.core.accounts.models import SiteProfileBase, User


class SiteProfile(SiteProfileBase):
    RELATED_NAME = 'speedy_net_site_profile'

    user = models.OneToOneField(to=User, verbose_name=_('user'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'), default=True)

    class Meta:
        verbose_name = 'Speedy Net Profile'
        verbose_name_plural = 'Speedy Net Profiles'

    def __str__(self):
        return '{} @ Speedy Net'.format(self.user)

    def activate(self):
        self.is_active = True
        self.user.is_active = True
        self.user.save_user_and_profile()

    def deactivate(self):
        self.is_active = False
        if (not (self.user.is_superuser)):
            self.user.is_active = False
        self.user.save_user_and_profile()

    def get_name(self):
        return self.user.get_full_name()


