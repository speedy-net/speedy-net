from django.conf import settings as django_settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from speedy.core.base.models import TimeStampedModel
from speedy.core.accounts.models import User


class UserLike(TimeStampedModel):
    from_user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('from user'), on_delete=models.CASCADE, related_name='+')
    to_user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('to user'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('user like')
        verbose_name_plural = _('user likes')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return '{} to {}'.format(self.from_user, self.to_user)


@receiver(models.signals.post_save, sender=UserLike)
def mail_user_on_new_message(sender, instance: UserLike, created, **kwargs):
    if (not (created)):
        return
    user = instance.to_user
    if (user.speedy_match_profile.notify_on_like == User.NOTIFICATIONS_ON):
        user.mail_user('likes/email/like', {
            'like': instance,
        })


