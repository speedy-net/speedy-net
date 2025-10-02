from django.conf import settings as django_settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core.base.models import TimeStampedModel
from speedy.core.accounts.models import User
from .managers import UserLikeManager


class UserLike(TimeStampedModel):
    """
    Represents a 'like' from one user to another.

    Attributes:
        from_user (ForeignKey): The user who likes.
        to_user (ForeignKey): The user who is liked.
        date_viewed (DateTimeField): The date when the like was viewed.
    """
    from_user: User = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('from user'), on_delete=models.CASCADE, related_name='likes_from_user')
    to_user: User = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('to user'), on_delete=models.CASCADE, related_name='likes_to_user')
    date_viewed = models.DateTimeField(blank=True, null=True, db_index=True)  # May be used later.

    objects = UserLikeManager()

    class Meta:
        verbose_name = _('user like')
        verbose_name_plural = _('user likes')
        unique_together = ('from_user', 'to_user')
        ordering = ('-date_created',)

    def __str__(self):
        return "User {} likes {}".format(self.from_user, self.to_user)

    def save(self, *args, **kwargs):
        """
        Saves the UserLike instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ValidationError: If a user tries to like themselves.
        """
        if (self.from_user == self.to_user):
            raise ValidationError(_("Users cannot like themselves."))
        return super().save(*args, **kwargs)


@receiver(signal=models.signals.post_save, sender=UserLike)
def mail_user_on_new_like(sender, instance: UserLike, created, **kwargs):
    """
    Sends an email notification to the user when they receive a new like.

    Args:
        sender (type): The model class that sent the signal.
        instance (UserLike): The instance of the UserLike model.
        created (bool): Whether this is a new instance.
        **kwargs: Additional keyword arguments.
    """
    if (created):
        user = instance.to_user
        if ((user.is_active) and (user.speedy_match_profile.notify_on_like == User.NOTIFICATIONS_ON)):
            user.mail_user(template_name_prefix='email/likes/like', context={
                'like': instance,
            })


@receiver(signal=models.signals.post_save, sender=UserLike)
def update_likes_to_user_count_on_new_like(sender, instance: UserLike, created, **kwargs):
    """
    Updates the count of likes received by the user when a new like is created.

    Args:
        sender (type): The model class that sent the signal.
        instance (UserLike): The instance of the UserLike model.
        created (bool): Whether this is a new instance.
        **kwargs: Additional keyword arguments.
    """
    if (created):
        user = instance.to_user
        user.speedy_match_profile._update_likes_to_user_count()
        user.speedy_match_profile.save()


@receiver(signal=models.signals.post_delete, sender=UserLike)
def update_likes_to_user_count_on_unlike(sender, instance: UserLike, **kwargs):
    """
    Updates the count of likes received by the user when a like is deleted.

    Args:
        sender (type): The model class that sent the signal.
        instance (UserLike): The instance of the UserLike model.
        **kwargs: Additional keyword arguments.
    """
    user = instance.to_user
    # Check origin because for cascade delete User -> UserLike, accessing user.speedy_match_profile will re-create deleted SpeedyMatchSiteProfile.
    if (not (user == kwargs.get('origin'))):
        user.speedy_match_profile._update_likes_to_user_count()
        user.speedy_match_profile.save()


