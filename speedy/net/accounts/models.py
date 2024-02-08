import logging

from django.db import models
from django.conf import settings as django_settings
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _
from django.contrib.sites.models import Site

from translated_fields import TranslatedField

from speedy.core.accounts.models import SiteProfileBase, User

logger = logging.getLogger(__name__)


class SiteProfile(SiteProfileBase):
    RELATED_NAME = 'speedy_net_site_profile'

    DELETED_NAME = _('Speedy Net User')

    user = models.OneToOneField(to=User, verbose_name=_('User'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    is_active = models.BooleanField(default=True)
    number_of_friends = TranslatedField(
        field=models.PositiveSmallIntegerField(verbose_name=_("Number of friends on last user's visit"), default=None, blank=True, null=True),
    )
    friends_count = models.PositiveSmallIntegerField(default=0)

    @cached_property
    def is_active_and_valid(self):
        return (self.is_active)

    class Meta:
        verbose_name = _('Speedy Net Profile')
        verbose_name_plural = _('Speedy Net Profiles')
        ordering = ('-last_visit', 'user_id')

    def __str__(self):
        return '{} @ Speedy Net'.format(super().__str__())

    def _get_deleted_name(self):
        return self.__class__.DELETED_NAME

    def _update_number_of_friends(self):
        previous_number_of_friends = self.number_of_friends
        self.number_of_friends = self.user.speedy_net_friends_count
        if (not (self.number_of_friends == previous_number_of_friends)):
            speedy_net_site = Site.objects.get(pk=django_settings.SPEEDY_NET_SITE_ID)
            language_code = get_language()
            logger.debug('SpeedyNetSiteProfile::_update_number_of_friends::User {user} has {number_of_friends} friends on {site_name} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                site_name=_(speedy_net_site.name),
                user=self.user,
                number_of_friends=self.number_of_friends,
                registered_days_ago=(now() - self.user.date_created).days,
                language_code=language_code,
            ))
            if (self.number_of_friends > User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 20):
                logger.warning('SpeedyNetSiteProfile::_update_number_of_friends::User {user} has more than {number_of_friends} friends on {site_name} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                    site_name=_(speedy_net_site.name),
                    user=self.user,
                    number_of_friends=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED - 20,
                    registered_days_ago=(now() - self.user.date_created).days,
                    language_code=language_code,
                ))
            if (self.number_of_friends > User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
                logger.error('SpeedyNetSiteProfile::_update_number_of_friends::User {user} has more than {MAX_NUMBER_OF_FRIENDS_ALLOWED} friends on {site_name} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                    site_name=_(speedy_net_site.name),
                    user=self.user,
                    MAX_NUMBER_OF_FRIENDS_ALLOWED=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED,
                    registered_days_ago=(now() - self.user.date_created).days,
                    language_code=language_code,
                ))

    def save(self, *args, **kwargs):
        self._update_number_of_friends()
        return super().save(*args, **kwargs)

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
        if (self.user.is_deleted):
            return self._get_deleted_name()
        return self.user.get_full_name()

    def call_after_verify_email_address(self):
        pass


