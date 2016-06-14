from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.net.accounts.models import BaseSiteProfile, UserEmailAddress, ACCESS_FRIENDS


class SiteProfile(BaseSiteProfile):
    class Meta:
        verbose_name = 'Speedy Net Profile'
        verbose_name_plural = 'Speedy Net Profiles'

    access_account = ACCESS_FRIENDS
    public_email = models.ForeignKey(UserEmailAddress, verbose_name=_('public email'), blank=True, null=True,
                                     limit_choices_to={'is_confirmed': True}, on_delete=models.SET_NULL,
                                     related_name='+')
