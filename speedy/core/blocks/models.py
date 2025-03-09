from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.dispatch import receiver
from friendship.models import Friend, FriendshipRequest

from speedy.core.base.models import TimeStampedModel
from speedy.core.accounts.models import Entity, User
from speedy.match.likes.models import UserLike
from .managers import BlockManager


class Block(TimeStampedModel):
    """
    Represents a block relationship between two entities.

    Attributes:
        blocker (Entity): The entity that is blocking.
        blocked (Entity): The entity that is being blocked.
    """
    blocker = models.ForeignKey(to=Entity, verbose_name=_('user'), on_delete=models.CASCADE, related_name='blocked_entities+')
    blocked = models.ForeignKey(to=Entity, verbose_name=_('blocked user'), on_delete=models.CASCADE, related_name='blocking_entities+')

    objects = BlockManager()

    class Meta:
        verbose_name = _('block')
        verbose_name_plural = _('user blocks')
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return "User {} blocked {}".format(self.blocker, self.blocked)

    def save(self, *args, **kwargs):
        """
        Save the Block instance to the database.

        Raises:
            ValidationError: If the blocker is the same as the blocked entity.
        """
        if (self.blocker == self.blocked):
            raise ValidationError(_("Users cannot block themselves."))
        return super().save(*args, **kwargs)


@receiver(signal=models.signals.post_save, sender=Block)
def cancel_friendship_requests_on_block(sender, instance: Block, **kwargs):
    """
    Signal receiver that cancels friendship requests between users when a block is created.

    Args:
        sender (type): The model class that sent the signal.
        instance (Block): The instance of the Block model.
        **kwargs: Additional keyword arguments.
    """
    # Remove friendship requests between users.
    if ((isinstance(instance.blocker, User))) and (isinstance(instance.blocked, User)):
        q1 = Q(from_user=instance.blocker, to_user=instance.blocked)
        q2 = Q(from_user=instance.blocked, to_user=instance.blocker)
        active_requests = FriendshipRequest.objects.filter(q1 | q2)
        for request in active_requests:
            request.cancel()


@receiver(signal=models.signals.post_save, sender=Block)
def remove_friends_on_block(sender, instance: Block, **kwargs):
    """
    Signal receiver that removes friendship between users when a block is created.

    Args:
        sender (type): The model class that sent the signal.
        instance (Block): The instance of the Block model.
        **kwargs: Additional keyword arguments.
    """
    # Remove friendship between users.
    if ((isinstance(instance.blocker, User))) and (isinstance(instance.blocked, User)):
        Friend.objects.remove_friend(from_user=instance.blocker, to_user=instance.blocked)


@receiver(signal=models.signals.post_save, sender=Block)
def remove_like_on_block(sender, instance: Block, **kwargs):
    """
    Signal receiver that removes likes from blocker to blocked when a block is created.

    Args:
        sender (type): The model class that sent the signal.
        instance (Block): The instance of the Block model.
        **kwargs: Additional keyword arguments.
    """
    # Remove like from blocker to blocked, but not from blocked to blocker (if the blocker unblocks the blocked, the like persists).
    if ((isinstance(instance.blocker, User))) and (isinstance(instance.blocked, User)):
        UserLike.objects.remove_like(from_user=instance.blocker, to_user=instance.blocked)


