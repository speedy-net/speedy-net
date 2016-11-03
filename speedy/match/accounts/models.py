from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.net.accounts.models import SiteProfileBase, UserEmailAddress, ACCESS_FRIENDS


class SiteProfile(SiteProfileBase):
    access_account = ACCESS_FRIENDS
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    notify_on_like = models.PositiveIntegerField(verbose_name=_('on new likes'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    active_languages = models.TextField(verbose_name=_('active languages'), blank=True)

    class Meta:
        verbose_name = 'Speedy Match Profile'
        verbose_name_plural = 'Speedy Match Profiles'

    def get_active_languages(self):
        return list(filter(None, (l.strip() for l in self.active_languages.split(','))))

    def set_active_languages(self, languages):
        self.active_languages = ','.join(set(languages))

    def activate(self, language_code):
        languages = self.get_active_languages()
        languages.append(language_code)
        self.set_active_languages(languages)
        self.save(update_fields={'active_languages'})

    def is_active_for_language(self, language_code):
        return language_code in self.get_active_languages()
