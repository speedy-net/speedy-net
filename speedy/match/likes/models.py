from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from speedy.core.models import TimeStampedModel
from speedy.net.accounts.models import Entity, SiteProfileBase


class EntityLike(TimeStampedModel):
    from_user = models.ForeignKey(verbose_name=_('from user'), to=settings.AUTH_USER_MODEL, related_name='+')
    # to_entity = models.ForeignKey(verbose_name=_('to entity'), to=Entity, related_name='+', null=True) #obsolete field, should be removed after migrating to to_user field
    to_user = models.ForeignKey(verbose_name=('to user'), to=settings.AUTH_USER_MODEL)
    class Meta:
        verbose_name = _('like')
        verbose_name_plural = _('entity likes')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return '{} to {}'.format(self.from_user, self.to_user)


@receiver(models.signals.post_save, sender=EntityLike)
def mail_user_on_new_message(sender, instance: EntityLike, created, **kwargs):
    if not created:
        return
    user = instance.to_user
    if user.profile.notify_on_like == SiteProfileBase.NOTIFICATIONS_ON:
        user.mail_user('likes/email/like', {
            'like': instance,
        })
