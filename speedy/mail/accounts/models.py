from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from speedy.core.accounts.models import SiteProfileBase, User


class SiteProfile(SiteProfileBase):
    RELATED_NAME = 'speedy_mail_site_profile'

    user = models.OneToOneField(to=User, verbose_name=_('User'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    is_active = models.BooleanField(default=False)

    @cached_property
    def is_active_and_valid(self):
        return (self.is_active)

    class Meta:
        verbose_name = _('Speedy Mail Profile')
        verbose_name_plural = _('Speedy Mail Profiles')

    def __str__(self):
        return '{} @ Speedy Mail Software'.format(super().__str__())

    def activate(self):
        self.is_active = True
        self.user.save_user_and_profile()

    def deactivate(self):
        self.is_active = False
        self.user.save_user_and_profile()

    def get_name(self):
        return self.user.get_full_name()


