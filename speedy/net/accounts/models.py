import logging

from django.db import models
from django.conf import settings as django_settings
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.models import Site

from translated_fields import TranslatedField

from speedy.core.accounts.models import SiteProfileBase, User

logger = logging.getLogger(__name__)


class SiteProfile(SiteProfileBase):
    RELATED_NAME = 'speedy_net_site_profile'

    user = models.OneToOneField(to=User, verbose_name=_('User'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    is_active = models.BooleanField(default=True)
    number_of_friends = TranslatedField(
        field=models.PositiveSmallIntegerField(verbose_name=_("Number of friends on last user's visit"), default=None, blank=True, null=True),
    )

    @property
    def is_active_and_valid(self):
        return (self.is_active)

    class Meta:
        verbose_name = _('Speedy Net Profile')
        verbose_name_plural = _('Speedy Net Profiles')

    def __str__(self):
        return '{} @ Speedy Net'.format(super().__str__())

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

    def call_after_verify_email_address(self):
        pass

    def update_last_visit(self):
        if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
            site = Site.objects.get_current()
            self.number_of_friends = self.user.friends_count
            logger.info('SpeedyNetSiteProfile::update_last_visit::User {user} has {number_of_friends} friends on {site_name}.'.format(site_name=_(site.name), user=self.user, number_of_friends=self.number_of_friends))
            if (self.number_of_friends > User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 20):
                logger.warning('SpeedyNetSiteProfile::update_last_visit::User {user} has more than {number_of_friends} friends on {site_name}.'.format(site_name=_(site.name), user=self.user, number_of_friends=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 20))
            if (self.number_of_friends > User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
                logger.error('SpeedyNetSiteProfile::update_last_visit::User {user} has more than {MAX_NUMBER_OF_FRIENDS_ALLOWED} friends on {site_name}.'.format(site_name=_(site.name), user=self.user, MAX_NUMBER_OF_FRIENDS_ALLOWED=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED))
        return super().update_last_visit()


