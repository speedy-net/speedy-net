from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.net.accounts.models import SiteProfileBase, UserEmailAddress, ACCESS_FRIENDS


class SiteProfile(SiteProfileBase):
    access_account = ACCESS_FRIENDS
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    notify_on_like = models.PositiveIntegerField(verbose_name=_('on new likes'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)

    class Meta:
        verbose_name = 'Speedy Match Profile'
        verbose_name_plural = 'Speedy Match Profiles'

