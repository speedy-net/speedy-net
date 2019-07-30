from django.conf import settings as django_settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core.base.models import TimeStampedModel
from speedy.core.accounts.models import User
from .managers import UserLikeManager


class UserLike(TimeStampedModel):
    from_user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('from user'), on_delete=models.CASCADE, related_name='likes_from_user')
    to_user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('to user'), on_delete=models.CASCADE, related_name='likes_to_user')
    date_viewed = models.DateTimeField(blank=True, null=True, db_index=True) # May be used later.

    objects = UserLikeManager()

    class Meta:
        verbose_name = _('user like')
        verbose_name_plural = _('user likes')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return "User {} likes {}".format(self.from_user, self.to_user)

    def save(self, *args, **kwargs):
        # Ensure users can't like themselves.
        if (self.from_user == self.to_user):
            raise ValidationError(_("Users cannot like themselves."))
        super().save(*args, **kwargs)


@receiver(models.signals.post_save, sender=UserLike)
def mail_user_on_new_message(sender, instance: UserLike, created, **kwargs):
    if (not (created)):
        return
    user = instance.to_user
    if (user.speedy_match_profile.notify_on_like == User.NOTIFICATIONS_ON):
        user.mail_user('likes/email/like', {
            'like': instance,
        })


